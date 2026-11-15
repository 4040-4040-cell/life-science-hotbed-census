"""Takeover paper portfolio engine, v1.1 (2026-11-15).

State lives next to this script: ledger.json (positions, orders, trades, benchmarks) and nav_history.csv
(one row per market close). Commands:
  python3 engine.py flags     today's prices; holdings that moved 25% or more; deal filings at the SEC (last 4 days)
  python3 engine.py order sell TICKER "reason"    queue a sale; it fills at the next market close
  python3 engine.py run       fill queued orders at the latest close, mark to market, write the report files
Rules (frozen 2026-11-15, see "rules" in ledger.json): equal-weight the 34 top-quarter names of the Nov 8, 2026
takeover scores with $5,000 of pretend money; fractional shares; every order fills at the first market close after it
is queued, plus 10 bps slippage; no commissions; deal targets sold once an agreement is confirmed; cash held until the
quarterly rebalance; restricted names never bought. Two benchmarks bought at the same close: XBI, and an equal-weight
basket of all 128 names in the scored pool, and an equal-weight basket of the pool names with 5+ specialist holders
(the tests of whether the score beats owning every specialist-held name, and beats the one tested rule on its own).
"""
import json, os, sys, time, csv, datetime as dt, urllib.request, html
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "ledger.json")
NAV = os.path.join(HERE, "nav_history.csv")
PT = ZoneInfo("America/Los_Angeles")
UA = {"User-Agent": "Mozilla/5.0"}
SEC_UA = {"User-Agent": "CatalystBook research admin@example.com"}
RESTRICTED = {"ERAS", "NBIX", "BOLD"}
DEAL_FORMS = {"SC 13D", "SC 13D/A", "SC TO-T", "SC TO-C", "SC 14D9", "SC14D9C", "DEFM14A", "PREM14A", "425", "8-K"}


def now_pt():
    o = os.environ.get("ENGINE_NOW")  # testing only, e.g. 2026-11-17T15:47
    return dt.datetime.fromisoformat(o).replace(tzinfo=PT) if o else dt.datetime.now(PT)


def _get(url, headers=UA, timeout=25):
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout).read().decode()


def _day(ts):
    return (dt.datetime.fromtimestamp(ts, dt.timezone.utc) - dt.timedelta(hours=5)).date().isoformat()


def _spark(batch, rng):
    for host in ("query2", "query1", "query2"):
        try:
            raw = json.loads(_get(f"https://{host}.finance.yahoo.com/v8/finance/spark?symbols={','.join(batch)}&range={rng}&interval=1d"))
            out = {}
            for t, v in raw.items():
                if v and v.get("timestamp") and v.get("close"):
                    out[t] = {_day(ts): float(c) for ts, c in zip(v["timestamp"], v["close"]) if c is not None}
            return out
        except Exception:
            time.sleep(2)
    return {}


def _chart(t, rng):
    for host in ("query1", "query2"):
        try:
            r = json.loads(_get(f"https://{host}.finance.yahoo.com/v8/finance/chart/{t}?range={rng}&interval=1d"))["chart"]["result"][0]
            out = {_day(ts): float(c) for ts, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c is not None}
            if out:
                return out
        except Exception:
            time.sleep(1.5)
    return None


def _nasdaq(t):
    try:
        frm = (now_pt().date() - dt.timedelta(days=90)).isoformat()
        cls = "etf" if t == "XBI" else "stocks"
        raw = json.loads(_get(f"https://api.nasdaq.com/api/quote/{t}/historical?assetclass={cls}&fromdate={frm}&limit=90&todate={now_pt().date().isoformat()}"))
        out = {}
        for row in raw["data"]["tradesTable"]["rows"]:
            m, d, y = row["date"].split("/")
            out[f"{y}-{m}-{d}"] = float(row["close"].replace("$", "").replace(",", ""))
        return out or None
    except Exception:
        return None


def prices(tickers, rng="3mo"):
    tickers = sorted(set(tickers))
    px, src = {}, {}
    for i in range(0, len(tickers), 20):
        for t, v in _spark(tickers[i:i + 20], rng).items():
            if v:
                px[t], src[t] = v, "yahoo"
        time.sleep(0.5)
    for t in tickers:
        if t not in px:
            v = _chart(t, rng)
            if v:
                px[t], src[t] = v, "yahoo"
            else:
                v = _nasdaq(t)
                if v:
                    px[t], src[t] = v, "nasdaq"
    n = now_pt()
    cap = n.date().isoformat()  # never use a bar dated after "now"; today's bar only after 1:30pm PT
    for t in px:
        px[t] = {d: c for d, c in px[t].items() if d < cap or (d == cap and (n.hour, n.minute) >= (13, 30))}
    return px, src


def mark(p, d):
    """Close on d, else the last close before d (a delisted deal target keeps its last price)."""
    if not p:
        return None, None
    ds = [x for x in p if x <= d]
    return (p[max(ds)], max(ds)) if ds else (None, None)


def load():
    return json.load(open(LEDGER))


def save(s):
    json.dump(s, open(LEDGER, "w"), indent=1)


NAV_COLS = ["date", "nav", "cash", "invested", "xbi_nav", "basket_nav", "five_nav", "top10_nav", "tilt_nav", "ret", "xbi_ret", "basket_ret", "five_ret", "top10_ret", "tilt_ret", "positions"]


def nav_rows():
    if not os.path.exists(NAV):
        return []
    with open(NAV) as f:
        return list(csv.DictReader(f))


def write_nav(rows):
    with open(NAV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=NAV_COLS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in NAV_COLS})


def cmd_flags():
    s = load()
    px, _ = prices(list(s["positions"]) + ["XBI"])
    d = max(px["XBI"])
    moves, missing = [], []
    for t in s["positions"]:
        p = px.get(t) or {}
        ds = sorted(x for x in p if x <= d)
        if len(ds) >= 2 and ds[-1] == d:
            r = p[ds[-1]] / p[ds[-2]] - 1
            if abs(r) >= 0.25:
                moves.append({"ticker": t, "move": round(r, 4)})
        else:
            missing.append(t)
    since = (now_pt().date() - dt.timedelta(days=4)).isoformat()
    filings = []
    for t, pos in s["positions"].items():
        cik = pos.get("cik") or s.get("ciks", {}).get(t)
        if not cik:
            continue
        try:
            r = json.loads(_get(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json", SEC_UA))["filings"]["recent"]
            for f, fd, acc, items in zip(r["form"], r["filingDate"], r["accessionNumber"], r.get("items", [""] * len(r["form"]))):
                if fd >= since and f in DEAL_FORMS and (f != "8-K" or any(i in (items or "") for i in ("1.01", "2.01", "5.02"))):
                    filings.append({"ticker": t, "form": f, "filed": fd, "items": items, "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/"})
        except Exception as e:
            filings.append({"ticker": t, "error": str(e)[:80]})
        time.sleep(0.15)
    print(json.dumps({"market_date": d, "big_moves": moves, "no_price_today": missing, "deal_type_filings_last_4_days": filings}, indent=1))


def cmd_order(side, ticker, reason):
    s = load()
    ticker = ticker.upper()
    if side == "sell" and ticker not in s["positions"]:
        sys.exit(f"{ticker} is not held")
    if side == "buy" and ticker in RESTRICTED:
        sys.exit(f"{ticker} is restricted")
    s["pending_orders"].append({"side": side, "ticker": ticker, "reason": reason, "created": now_pt().date().isoformat()})
    save(s)
    print("queued", side, ticker, "to fill at the next market close")


def pct(x):
    return "n/a" if x is None else f"{x*100:+.2f}%"


def money(x):
    return f"${x:,.2f}"


def ret_between(rows, start_date, cap, key):
    prev = [r for r in rows if r["date"] < start_date]
    b = float(prev[-1][key]) if prev else cap
    return float(rows[-1][key]) / b - 1


def cmd_run():
    s = load()
    basket = s["basket"]["tickers"]
    five = s["five"]["tickers"]
    top10 = s["top10"]["tickers"]
    px, src = prices(list(s["positions"]) + [o["ticker"] for o in s["pending_orders"]] + basket + five + top10 + ["XBI"])
    if not px.get("XBI"):
        sys.exit("FATAL: no benchmark prices from Yahoo or Nasdaq")
    d = max(px["XBI"])
    rows = nav_rows()
    today = now_pt().date()
    fillable = [o for o in s["pending_orders"] if o["created"] < d]
    new_day = (not rows or d > rows[-1]["date"]) and (s["inception"] is not None or bool(fillable))
    slip = s["slippage_bps"] / 1e4
    trades_today, warnings = [], []
    if new_day:
        remaining = [o for o in s["pending_orders"] if o not in fillable]
        for o in [o for o in fillable if o["side"] == "sell"]:
            c = (px.get(o["ticker"]) or {}).get(d)
            if c is None:
                remaining.append(o); warnings.append(f"Sell {o['ticker']} not filled: no close on {d}"); continue
            pos = s["positions"].pop(o["ticker"])
            fill = c * (1 - slip); val = pos["shares"] * fill
            s["cash"] += val
            tr = {"date": d, "side": "sell", "ticker": o["ticker"], "shares": round(pos["shares"], 6), "price": round(fill, 4), "value": round(val, 2), "reason": o["reason"], "pnl": round(val - pos["cost"], 2)}
            s["trades"].append(tr); trades_today.append(tr)
        buys = [o for o in fillable if o["side"] == "buy"]
        if buys:
            per = s["cash"] / len(buys)
            for o in buys:
                c = (px.get(o["ticker"]) or {}).get(d)
                if c is None:
                    remaining.append(o); warnings.append(f"Buy {o['ticker']} not filled: no close on {d}"); continue
                dollars = o.get("dollars") or per
                fill = c * (1 + slip); sh = dollars / fill
                s["cash"] -= dollars
                s["positions"][o["ticker"]] = {"shares": sh, "cost": dollars, "entry_date": d, "entry_px": round(fill, 4), "cik": s.get("ciks", {}).get(o["ticker"])}
                tr = {"date": d, "side": "buy", "ticker": o["ticker"], "shares": round(sh, 6), "price": round(fill, 4), "value": round(dollars, 2), "reason": o["reason"]}
                s["trades"].append(tr); trades_today.append(tr)
        s["pending_orders"] = remaining
        if s["inception"] is None and s["positions"]:
            s["inception"] = d
            s["xbi"] = {"shares": s["start_capital"] / (px["XBI"][d] * (1 + slip))}
            have = [t for t in basket if (px.get(t) or {}).get(d)]
            per = s["start_capital"] / len(have)
            s["basket"]["shares"] = {t: per / (px[t][d] * (1 + slip)) for t in have}
            s["basket"]["missing_at_start"] = sorted(set(basket) - set(have))
            have5 = [t for t in five if (px.get(t) or {}).get(d)]
            s["five"]["shares"] = {t: (s["start_capital"] / len(have5)) / (px[t][d] * (1 + slip)) for t in have5}
            have10 = [t for t in top10 if (px.get(t) or {}).get(d)]
            s["top10"]["shares"] = {t: (s["start_capital"] / len(have10)) / (px[t][d] * (1 + slip)) for t in have10}
        invested, marks = 0.0, {}
        for t, pos in s["positions"].items():
            c, used = mark(px.get(t), d)
            if c is None:
                c = pos["cost"] / pos["shares"]; warnings.append(f"{t}: no price, carried at cost")
            elif used != d:
                warnings.append(f"{t}: no close on {d}, used {used}")
            marks[t] = c; invested += pos["shares"] * c
        nav = s["cash"] + invested
        xnav = s["xbi"]["shares"] * px["XBI"][d]
        bnav = sum(sh * (mark(px.get(t), d)[0] or 0) for t, sh in s["basket"]["shares"].items())
        fnav = sum(sh * (mark(px.get(t), d)[0] or 0) for t, sh in s["five"]["shares"].items())
        tnav = sum(sh * (mark(px.get(t), d)[0] or 0) for t, sh in s["top10"]["shares"].items())
        prev = rows[-1] if rows else None
        cap = s["start_capital"]
        rows.append({"date": d, "nav": round(nav, 2), "cash": round(s["cash"], 2), "invested": round(invested, 2),
                     "xbi_nav": round(xnav, 2), "basket_nav": round(bnav, 2), "five_nav": round(fnav, 2), "top10_nav": round(tnav, 2),
                     "tilt_nav": round((float(prev["tilt_nav"]) if prev else cap) * (1 + (xnav / (float(prev["xbi_nav"]) if prev else cap) - 1) + (fnav / (float(prev["five_nav"]) if prev else cap) - 1) - (bnav / (float(prev["basket_nav"]) if prev else cap) - 1)), 2),
                     "ret": round(nav / (float(prev["nav"]) if prev else cap) - 1, 6),
                     "xbi_ret": round(xnav / (float(prev["xbi_nav"]) if prev else cap) - 1, 6),
                     "basket_ret": round(bnav / (float(prev["basket_nav"]) if prev else cap) - 1, 6),
                     "five_ret": round(fnav / (float(prev["five_nav"]) if prev else cap) - 1, 6),
                     "top10_ret": round(tnav / (float(prev["top10_nav"]) if prev else cap) - 1, 6),
                     "tilt_ret": round((xnav / (float(prev["xbi_nav"]) if prev else cap) - 1) + (fnav / (float(prev["five_nav"]) if prev else cap) - 1) - (bnav / (float(prev["basket_nav"]) if prev else cap) - 1), 6),
                     "positions": len(s["positions"])})
        write_nav(rows)
        s["last_marks"] = {t: round(v, 4) for t, v in marks.items()}
        mv = []
        for t in s["positions"]:
            p = px.get(t) or {}
            ds = sorted(x for x in p if x <= d)
            if len(ds) >= 2 and ds[-1] == d:
                mv.append((t, p[ds[-1]] / p[ds[-2]] - 1))
        mv.sort(key=lambda x: x[1])
        s["last_movers"] = {"down": mv[:3], "up": mv[::-1][:3]}
    save(s)
    report(s, rows, d, new_day, trades_today, warnings, today, src)


def report(s, rows, d, new_day, trades_today, warnings, today, src):
    wd = today.weekday()
    lines, hp = [], []
    cap = s["start_capital"]
    day_label = today.strftime("%a %b %-d, %Y")
    if s["inception"] is None:
        n = len(s["pending_orders"])
        subject = f"Takeover paper portfolio, {day_label}: {n} orders queued, first fills at the next close"
        p1 = (f"The paper portfolio starts with {money(cap)} of pretend money. {n} buy orders are queued at about {money(cap/n)} each "
              f"and fill at the next market close. Benchmarks bought at the same close: {money(cap)} in XBI, and {money(cap)} spread "
              f"equally across all {len(s['basket']['tickers'])} names in the scored pool, and {money(cap)} across the {len(s['five']['tickers'])} pool names with 5 or more specialist holders.")
        q = ", ".join(o["ticker"] for o in s["pending_orders"])
        lines += [p1, "", "Queued: " + q]
        hp.append(f"<p>{html.escape(p1)}</p><p><b>Queued:</b> {html.escape(q)}</p>")
    else:
        last = rows[-1]
        nav, xnav, bnav, fnav, tnav, gnav = (float(last[k]) for k in ("nav", "xbi_nav", "basket_nav", "five_nav", "top10_nav", "tilt_nav"))
        ltd, xltd, bltd, fltd, tltd, gltd = (v / cap - 1 for v in (nav, xnav, bnav, fnav, tnav, gnav))
        head = f"{pct(float(last['ret']))} today" if new_day else "market closed"
        subject = f"Takeover paper portfolio, {day_label}: {head}, {pct(ltd)} since start (XBI {pct(xltd)})"
        K = ("nav", "xbi_nav", "basket_nav", "five_nav", "top10_nav", "tilt_nav")
        T = [("", "Portfolio", "XBI", "Pool basket", "5+ holders", "Top 10", "XBI + tilt")]
        T.append(("Value", money(nav), money(xnav), money(bnav), money(fnav), money(tnav), money(gnav)))
        if new_day:
            T.append((f"Day ({d})", *[pct(float(last[k])) for k in ("ret", "xbi_ret", "basket_ret", "five_ret", "top10_ret", "tilt_ret")]))
        if wd == 5:
            mon = (today - dt.timedelta(days=5)).isoformat()
            T.append(("Week", *[pct(ret_between(rows, mon, cap, k)) for k in K]))
            ms = today.replace(day=1).isoformat()
            T.append(("Month to date", *[pct(ret_between(rows, ms, cap, k)) for k in K]))
        if today.day == 1:
            pe = today - dt.timedelta(days=1)
            sub = [r for r in rows if r["date"] <= pe.isoformat()]
            if sub:
                T.append((pe.strftime("%B %Y"), *[pct(ret_between(sub, pe.replace(day=1).isoformat(), cap, k)) for k in K]))
        T.append((f"Since start ({s['inception']})", pct(ltd), pct(xltd), pct(bltd), pct(fltd), pct(tltd), pct(gltd)))
        T.append(("Portfolio ahead by", "", pct(ltd - xltd), pct(ltd - bltd), pct(ltd - fltd), pct(ltd - tltd), pct(ltd - gltd)))
        if not new_day:
            lines.append(f"No trading today ({'weekend' if wd >= 5 else 'market holiday'}). Figures are as of the {last['date']} close.")
            hp.append(f"<p>{html.escape(lines[-1])}</p>")
        for r in T:
            lines.append(" | ".join(r))
        hp.append("<table style='border-collapse:collapse;font-family:Arial,sans-serif;font-size:14px'>" + "".join(
            "<tr>" + "".join(f"<td style='padding:5px 18px 5px 0;{'text-align:right;' if i else ''}{'font-weight:bold;' if i == 1 else ''}{'color:#5F6368;' if j == 0 else ''}'>{html.escape(c)}</td>" for i, c in enumerate(r)) + "</tr>"
            for j, r in enumerate(T)) + "</table>")
        lines.append(f"Holdings: {last['positions']}; cash {money(float(last['cash']))}")
        hp.append(f"<p>Holdings: {last['positions']}; cash {html.escape(money(float(last['cash'])))}</p>")
        if trades_today:
            lines.append("Trades:")
            hp.append("<p><b>Trades</b></p><ul>")
            for t in trades_today:
                extra = f", P&L {money(t['pnl'])}" if "pnl" in t else ""
                ln = f"{t['side'].upper()} {t['ticker']} {t['shares']:.4f} sh at {money(t['price'])} = {money(t['value'])}{extra} ({t['reason']})"
                lines.append("  " + ln); hp.append(f"<li>{html.escape(ln)}</li>")
            hp.append("</ul>")
        elif new_day:
            lines.append("Trades: none."); hp.append("<p><b>Trades:</b> none.</p>")
        if new_day and s.get("last_movers"):
            up = ", ".join(f"{t} {pct(r)}" for t, r in s["last_movers"]["up"])
            dn = ", ".join(f"{t} {pct(r)}" for t, r in s["last_movers"]["down"])
            lines += [f"Biggest gains: {up}", f"Biggest losses: {dn}"]
            hp.append(f"<p>Biggest gains: {html.escape(up)}<br>Biggest losses: {html.escape(dn)}</p>")
    fb = sorted(t for t, v in src.items() if v == "nasdaq")
    if fb:
        warnings.append("Nasdaq fallback prices for " + ", ".join(fb))
    if warnings:
        lines += ["", "Data notes: " + "; ".join(warnings)]
        hp.append(f"<p style='color:#5F6368'>Data notes: {html.escape('; '.join(warnings))}</p>")
    foot = ("Pretend money only; no real orders. Rules: equal weight across the 34 top-quarter names of the Nov 8, 2026 takeover scores; "
            "every order fills at the first close after it is queued, plus 10 bps slippage; deal targets sold once an agreement is confirmed, "
            "cash held until the quarterly rebalance. Pool basket = all 128 scored names; 5+ holders = the pool names with five or more specialist holders; Top 10 = the ten highest scores; all equal weight. XBI + tilt = XBI plus the daily return of 5+ holders minus the pool basket (shadow challengers, not traded). Prices: Yahoo Finance closes, "
            "Nasdaq fallback; unofficial.")
    lines += ["", foot]
    hp.append(f"<p style='color:#5F6368;font-size:12px'>{html.escape(foot)}</p>")
    open(os.path.join(HERE, "report_subject.txt"), "w").write(subject)
    open(os.path.join(HERE, "report.txt"), "w").write("\n".join(lines))
    open(os.path.join(HERE, "report.html"), "w").write("<div style='font-family:Arial,sans-serif;font-size:14px;color:#1A1A1A'>" + "".join(hp) + "</div>")
    print(subject); print("\n".join(lines))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    {"flags": lambda: cmd_flags(), "run": lambda: cmd_run(),
     "order": lambda: cmd_order(a[1], a[2], a[3] if len(a) > 3 else "manual")}.get(a[0], lambda: sys.exit(__doc__))()
