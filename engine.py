"""Takeover paper portfolio engine, v1.3 (2026-11-28): the loss-control package rules now run the live book (decide).

State lives next to this script: ledger.json (positions, orders, trades, benchmarks) and nav_history.csv
(one row per market close). Commands:
  python3 engine.py flags     today's prices; holdings that moved 25% or more; deal filings at the SEC (last 4 days)
  python3 engine.py order sell TICKER "reason"    queue a sale; it fills at the next market close
  python3 engine.py run       fill queued orders at the latest close, mark to market, write the report files
  python3 engine.py decide    after run: read the signals, set the day's call, queue rebalance or risk orders, put the call atop the report
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


NAV_COLS = ["date", "nav", "cash", "invested", "xbi_nav", "basket_nav", "five_nav", "top10_nav", "tilt_nav", "pkg_nav", "frozen_nav", "ret", "xbi_ret", "basket_ret", "five_ret", "top10_ret", "tilt_ret", "pkg_ret", "frozen_ret", "pkg_expo", "positions"]


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
            w.writerow({k: r.get(k, "") for k in NAV_COLS})


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
    b = float(prev[-1].get(key) or prev[-1]["nav"]) if prev else cap   # frozen_nav is blank before Nov 28; it equals nav there
    return float(rows[-1][key]) / b - 1


# ---- shadow package (loss-control rules R4 + R5 + R11, pre-registered in loss_control_prereg.md) --------------
P_SWITCH, P_QCOST, P_CASH = 0.005, 0.002, 0.04 / 252


def _size_m(m):
    return 1.0 if m < 1e9 else 1.3 if m < 5e9 else 0.9 if m < 10e9 else 0.55


def pkg_select(cands, px, d):
    """Top quarter of candidates by holders x size x stage at the d close; ties broken by holders, then ticker."""
    rows = []
    for t, c in cands.items():
        p = mark(px.get(t), d)[0]
        if p is None or t in RESTRICTED:
            continue
        m = p * c["sh"]
        if 0.5e9 <= m <= 25e9:
            rows.append((-(1.0 if c["n"] >= 5 else 0.4) * _size_m(m) * c["st"], -c["n"], t))
    rows.sort()
    return [r[2] for r in rows[:max(1, round(len(rows) / 4))]]


def pkg_signal(P, px, xh, d):
    """Target exposure decided at the d close: (fraction in stocks, where the rest waits)."""
    cl = sorted(x for x in xh if x <= d)
    st = P["state"]
    if len(cl) < 22:
        return [1.0, "cash"]
    d21 = cl[-22]
    rets = [b / a - 1 for a, b in ((mark(px.get(t), d21)[0], mark(px.get(t), d)[0]) for t in P["cands"]) if a and b]
    gap = (sum(rets) / len(rets) if rets else 0.0) - (xh[d] / xh[d21] - 1)
    if gap <= -0.08:
        st["rs_on"] = True
    elif gap > 0:
        st["rs_on"] = False
    ma = sum(xh[x] for x in cl[-200:]) / 200 if len(cl) >= 200 else None
    c = [(1.0, "cash")]
    if st.get("rs_on"):
        c.append((0.0, "xbi"))
    if ma and xh[d] < ma:
        c.append((0.5, "cash"))
    st["signal"] = {"date": d, "pool_minus_xbi_21d": round(gap, 4), "xbi_vs_200d": round(xh[d] / ma - 1, 4) if ma else None}
    return list(min(c, key=lambda z: z[0]))


def pkg_values(st, px, xp, d):
    hv = sum(sh * (mark(px.get(t), d)[0] or 0) for t, sh in st["hold"].items())
    return hv, st["pocket_sh"] * xp, st["alt_xbi_sh"] * xp + st["cash"]


def pkg_buy(st, names, px, d, dollars):
    st["hold"] = {t: (dollars / len(names)) / px[t][d] for t in names if (px.get(t) or {}).get(d)} if names else {}


def pkg_step(s, px, xh, d, new_inception):
    """Advance the shadow package to the d close. Returns (nav, exposure)."""
    P = s.get("package")
    if not P:
        return None, None
    xp = xh[d]
    cl = sorted(x for x in xh if x <= d)
    if new_inception or P.get("state") is None:
        P["state"] = st = {"hold": {}, "pocket_sh": 0.0, "alt_xbi_sh": 0.0, "cash": 0.0, "rs_on": False, "last": d, "month": d[:7], "pending": None}
        e, alt = pkg_signal(P, px, xh, cl[-2]) if len(cl) > 1 else [1.0, "cash"]
        total = s["start_capital"] * (1 - P_QCOST)
        pkg_buy(st, pkg_select(P["cands"], px, d), px, d, total * e)
        if alt == "xbi":
            st["alt_xbi_sh"] = total * (1 - e) / xp
        else:
            st["cash"] = total * (1 - e)
        st["e"], st["alt"] = e, alt
    else:
        st = P["state"]
        if d <= st["last"]:
            hv, pv, av = pkg_values(st, px, xp, d); return hv + pv + av, (hv + pv) / (hv + pv + av)
        st["cash"] *= (1 + P_CASH) ** len([x for x in cl if x > st["last"]])
        # monthly rescore or post-13F rebuild
        if d[:7] != st["month"] or P.get("rebalance_due"):
            hv, pv, av = pkg_values(st, px, xp, d)
            sleeve = hv + pv
            new = pkg_select(P["cands"], px, d)
            old = {t: sh * (mark(px.get(t), d)[0] or 0) / hv for t, sh in st["hold"].items()} if hv > 0 else {}
            w = {t: 1 / len(new) for t in new}
            turn = sum(abs(w.get(t, 0) - old.get(t, 0)) for t in set(w) | set(old))
            cost = P_QCOST if P.get("rebalance_due") else P_QCOST * 0.5 * turn
            pkg_buy(st, new, px, d, sleeve * (1 - cost)); st["pocket_sh"] = 0.0
            st["month"] = d[:7]; P["rebalance_due"] = False
        # execute the target decided at the previous close
        if st.get("pending"):
            want, walt = st["pending"]
            hv, pv, av = pkg_values(st, px, xp, d)
            if abs(want - st["e"]) > 1e-9 or (walt != st["alt"] and av > 0):
                if walt != st["alt"] and av > 0:
                    av *= 1 - P_SWITCH
                    st["alt_xbi_sh"], st["cash"] = (av / xp, 0.0) if walt == "xbi" else (0.0, av)
                st["alt"] = walt
                sleeve = hv + pv; move = (sleeve + av) * want - sleeve
                if move < -1e-9:
                    f = -move / sleeve
                    st["hold"] = {t: sh * (1 - f) for t, sh in st["hold"].items()}; st["pocket_sh"] *= 1 - f
                    got = -move * (1 - P_SWITCH)
                    if walt == "xbi": st["alt_xbi_sh"] += got / xp
                    else: st["cash"] += got
                elif move > 1e-9:
                    move = min(move, av); add = move * (1 - P_SWITCH)
                    if walt == "xbi": st["alt_xbi_sh"] -= move / xp
                    else: st["cash"] -= move
                    if hv > 0:
                        st["hold"] = {t: sh * (1 + add / hv) for t, sh in st["hold"].items()}
                    else:
                        st["pocket_sh"] += add / xp   # waits in XBI until the next monthly rescore, as tested
                st["e"] = want
            st["pending"] = None
        st["last"] = d
    tgt = pkg_signal(P, px, xh, d)
    if abs(tgt[0] - st["e"]) > 1e-9 or tgt[1] != st["alt"]:
        st["pending"] = tgt
    hv, pv, av = pkg_values(st, px, xp, d)
    nav = hv + pv + av
    return nav, (hv + pv) / nav


def cmd_run():
    s = load()
    basket = s["basket"]["tickers"]
    five = s["five"]["tickers"]
    top10 = s["top10"]["tickers"]
    pc = list(s.get("package", {}).get("cands", {}))
    px, src = prices(list(s["positions"]) + [o["ticker"] for o in s["pending_orders"]] + basket + five + top10 + pc + ["XBI"])
    xh = prices(["XBI"], "1y")[0].get("XBI") or px.get("XBI")
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
            if o["ticker"] not in s["positions"]:
                warnings.append(f"Sell {o['ticker']} skipped: not held"); continue
            pos = s["positions"][o["ticker"]]
            q = min(o.get("shares") or pos["shares"], pos["shares"])
            if q >= pos["shares"] * 0.9999:
                q = pos["shares"]; s["positions"].pop(o["ticker"]); basis = pos["cost"]
            else:
                basis = pos["cost"] * q / pos["shares"]; pos["shares"] -= q; pos["cost"] -= basis
            fill = c * (1 - slip); val = q * fill
            s["cash"] += val
            tr = {"date": d, "side": "sell", "ticker": o["ticker"], "shares": round(q, 6), "price": round(fill, 4), "value": round(val, 2), "reason": o["reason"], "pnl": round(val - basis, 2)}
            s["trades"].append(tr); trades_today.append(tr)
        buys = [o for o in fillable if o["side"] == "buy"]
        if buys:
            per = s["cash"] / len(buys)
            want = sum(o.get("dollars") or per for o in buys)
            scale = min(1.0, s["cash"] / want) if want > 0 else 1.0   # never spend more cash than the account holds
            for o in buys:
                c = (px.get(o["ticker"]) or {}).get(d)
                if c is None:
                    remaining.append(o); warnings.append(f"Buy {o['ticker']} not filled: no close on {d}"); continue
                dollars = (o.get("dollars") or per) * scale
                fill = c * (1 + slip); sh = dollars / fill
                s["cash"] -= dollars
                if o["ticker"] in s["positions"]:
                    pos = s["positions"][o["ticker"]]; pos["shares"] += sh; pos["cost"] += dollars
                else:
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
        pnav, pexp = pkg_step(s, px, xh, d, new_inception=not rows)
        fz = s.get("frozen")
        znav = (fz["cash"] + sum(sh * (mark(px.get(t), d)[0] or 0) for t, sh in fz["shares"].items())) if fz else None
        zprev = float(prev["frozen_nav"]) if prev and prev.get("frozen_nav") else (prev and float(prev["nav"]))
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
                     "pkg_nav": round(pnav, 2) if pnav else "", "pkg_ret": round(pnav / (float(prev["pkg_nav"]) if prev and prev.get("pkg_nav") else cap) - 1, 6) if pnav else "",
                     "pkg_expo": round(pexp, 3) if pexp is not None else "",
                     "frozen_nav": round(znav, 2) if znav else "", "frozen_ret": round(znav / zprev - 1, 6) if znav and zprev else "",
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
        pk = float(last.get("pkg_nav") or cap)
        zk = float(last.get("frozen_nav") or nav)
        ltd, xltd, bltd, fltd, tltd, gltd, pltd, zltd = (v / cap - 1 for v in (nav, xnav, bnav, fnav, tnav, gnav, pk, zk))
        head = f"{pct(float(last['ret']))} today" if new_day else "market closed"
        subject = f"Takeover paper portfolio, {day_label}: {head}, {pct(ltd)} since start (XBI {pct(xltd)})"
        K = ("nav", "frozen_nav", "xbi_nav", "basket_nav", "five_nav", "top10_nav", "tilt_nav", "pkg_nav")
        T = [("", "Portfolio", "Frozen rules", "XBI", "Pool basket", "5+ holders", "Top 10", "XBI + tilt", "Package since Nov 16")]
        T.append(("Value", money(nav), money(zk), money(xnav), money(bnav), money(fnav), money(tnav), money(gnav), money(pk)))
        if new_day:
            T.append((f"Day ({d})", *[pct(float(last.get(k) or 0)) for k in ("ret", "frozen_ret", "xbi_ret", "basket_ret", "five_ret", "top10_ret", "tilt_ret", "pkg_ret")]))
        if wd == 5:
            mon = (today - dt.timedelta(days=5)).isoformat()
            T.append(("Week", *[pct(ret_between(rows, mon, cap, k if rows[-1].get(k) else "nav")) for k in K]))
            ms = today.replace(day=1).isoformat()
            T.append(("Month to date", *[pct(ret_between(rows, ms, cap, k if rows[-1].get(k) else "nav")) for k in K]))
        if today.day == 1:
            pe = today - dt.timedelta(days=1)
            sub = [r for r in rows if r["date"] <= pe.isoformat()]
            if sub:
                T.append((pe.strftime("%B %Y"), *[pct(ret_between(sub, pe.replace(day=1).isoformat(), cap, k if sub[-1].get(k) else "nav")) for k in K]))
        T.append((f"Since start ({s['inception']})", pct(ltd), pct(zltd), pct(xltd), pct(bltd), pct(fltd), pct(tltd), pct(gltd), pct(pltd)))
        T.append(("Portfolio ahead by", "", pct(ltd - zltd), pct(ltd - xltd), pct(ltd - bltd), pct(ltd - fltd), pct(ltd - tltd), pct(ltd - gltd), pct(ltd - pltd)))
        if not new_day:
            lines.append(f"No trading today ({'weekend' if wd >= 5 else 'market holiday'}). Figures are as of the {last['date']} close.")
            hp.append(f"<p>{html.escape(lines[-1])}</p>")
        for r in T:
            lines.append(" | ".join(r))
        hp.append("<table style='border-collapse:collapse;font-family:Arial,sans-serif;font-size:14px'>" + "".join(
            "<tr>" + "".join(f"<td style='padding:5px 18px 5px 0;{'text-align:right;' if i else ''}{'font-weight:bold;' if i == 1 else ''}{'color:#5F6368;' if j == 0 else ''}'>{html.escape(c)}</td>" for i, c in enumerate(r)) + "</tr>"
            for j, r in enumerate(T)) + "</table>")
        pst = (s.get("package") or {}).get("state") or {}
        if pst:
            sg = pst.get("signal", {})
            pl = (f"Loss-control package (shadow): {float(last.get('pkg_expo') or 1)*100:.0f}% in stocks, rest in {pst.get('alt', 'cash').upper() if pst.get('alt') == 'xbi' else 'cash'}; "
                  f"candidate basket minus XBI over 21 days {pct(sg.get('pool_minus_xbi_21d'))} (switch to XBI at -8.00%), XBI vs its 200-day average {pct(sg.get('xbi_vs_200d'))}"
                  + (f"; change queued for the next close: {pst['pending'][0]*100:.0f}% in stocks" if pst.get("pending") else ""))
            lines.append(pl); hp.append(f"<p>{html.escape(pl)}</p>")
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
    foot = ("Pretend money only; no real orders. Live rules since Nov 28, 2026: monthly rescore to the top quarter of specialist-held names "
            "at current value, equal weight; rotate into XBI when those names trail XBI by 8 points over 21 trading days; half cash when XBI is "
            "below its 200-day average; deal targets sold once an agreement is confirmed. Orders fill at the first close after they are queued, "
            "plus 10 bps slippage. Frozen rules = the Nov 15 book (34 top-quarter names of the Nov 8 scores, buy and hold) tracked from Nov 27. Pool basket = all 128 scored names; 5+ holders = the pool names with five or more specialist holders; Top 10 = the ten highest scores; all equal weight. XBI + tilt = XBI plus the daily return of 5+ holders minus the pool basket. Loss-control package = top quarter rescored monthly, switches to XBI when specialist-held names trail XBI by 8 points over a month, half cash when XBI is below its 200-day average, run from Nov 16 (shadow, not traded). Prices: Yahoo Finance closes, "
            "Nasdaq fallback; unofficial.")
    lines += ["", foot]
    hp.append(f"<p style='color:#5F6368;font-size:12px'>{html.escape(foot)}</p>")
    open(os.path.join(HERE, "report_subject.txt"), "w").write(subject)
    open(os.path.join(HERE, "report.txt"), "w").write("\n".join(lines))
    open(os.path.join(HERE, "report.html"), "w").write("<div style='font-family:Arial,sans-serif;font-size:14px;color:#1A1A1A'>" + "".join(hp) + "</div>")
    print(subject); print("\n".join(lines))


# ---- live decision layer (from Nov 28, 2026): the package rules now run the live book --------------------------
LIVE_RULES = ("Live from Nov 28, 2026 (owner's instruction): the loss-control package rules run the live book. Each market day, "
              "after the close: (1) monthly rescore at the first close of each month: top quarter of the specialist-held "
              "candidates by holders x size x stage at current value, equal weight; (2) rotate the stock sleeve into XBI when the "
              "candidate basket trails XBI by 8+ points over 21 trading days, back when the gap turns positive; (3) half in cash "
              "when XBI closes below its 200-day average; (4) confirmed deal targets sold, cash redeployed at the next rescore. "
              "Orders fill at the next close with 10 bps slippage. The Nov 15 frozen rules continue as a comparison line.")
MIN_TRADE = 0.001   # skip trades under 0.1% of the book (about $5)


def cmd_decide():
    s = load()
    P = s["package"]; cands = P["cands"]
    L = s.setdefault("live", {"since": None, "month": None, "rs_on": False, "last_decided": None, "decisions": []})
    held = [t for t in s["positions"] if t != "XBI"]
    px, _ = prices(sorted(set(cands) | set(s["positions"]) | {"XBI"}))
    xh = prices(["XBI"], "1y")[0].get("XBI") or px["XBI"]
    d = max(px["XBI"])
    out = []
    if L.get("last_decided") == d:
        last = (L.get("decisions") or [{}])[-1]
        out.append(f"Call: no new close since {d}. Standing call from that close: {last.get('call', 'HOLD')}.")
        return _decision_out(out, [])
    if L.get("since") is None:
        L["since"] = d; L["month"] = d[:7]
    vals = {t: pos["shares"] * (mark(px.get(t), d)[0] or pos["cost"] / pos["shares"]) for t, pos in s["positions"].items()}
    nav = s["cash"] + sum(vals.values())
    stock = sum(v for t, v in vals.items() if t != "XBI")
    e_now = stock / nav if nav else 0
    e, alt = pkg_signal({"cands": cands, "state": L}, px, xh, d)
    sg = L["signal"]
    pend_sell = {o["ticker"] for o in s["pending_orders"] if o["side"] == "sell"}
    rescore = d[:7] != L["month"] or L.get("rebalance_due") or (e > 0 and stock < 0.01 * nav)   # coming back from XBI or cash buys the current top quarter
    if rescore:
        names = pkg_select(cands, px, d)
        target = {t: nav * e / len(names) for t in names}
        L["month"] = d[:7]; L["rebalance_due"] = False
    elif abs(e - e_now) > 0.05:
        k = (nav * e) / stock if stock else 0
        target = {t: vals[t] * k for t in held if t not in pend_sell}
    else:
        target = None
    orders = []
    if target is not None:
        alt_val = nav - sum(target.values())
        target["XBI"] = alt_val if alt == "xbi" else 0.0
        for t in sorted(set(target) | set(vals)):
            if t in pend_sell:
                continue
            diff = target.get(t, 0.0) - vals.get(t, 0.0)
            if abs(diff) < MIN_TRADE * nav and target.get(t, 0.0) > 0:
                continue
            c = mark(px.get(t), d)[0]
            if diff < 0 and c:
                full = target.get(t, 0.0) <= 0
                orders.append({"side": "sell", "ticker": t, "shares": None if full else -diff / c, "dollars_est": round(-diff, 2)})
            elif diff > 0 and t not in RESTRICTED:
                orders.append({"side": "buy", "ticker": t, "dollars": round(diff, 2)})
    why = "monthly rescore" if rescore else ("regime change" if target is not None else "")
    for o in orders:
        o.update({"reason": f"{why}, decided at the {d} close", "created": max(now_pt().date().isoformat(), d)})
        s["pending_orders"].append({k: v for k, v in o.items() if k != "dollars_est" and v is not None})
    sig = (f"Specialist-held candidates are {pct(sg.get('pool_minus_xbi_21d'))} against XBI over 21 trading days (rotate to XBI at -8.00%). "
           f"XBI is {pct(sg.get('xbi_vs_200d'))} against its 200-day average (half to cash below it).")
    if not orders:
        call = "HOLD"
        nxt = "Next monthly rescore at the first close of " + (dt.date.fromisoformat(d[:7] + "-01") + dt.timedelta(days=32)).strftime("%B") + "."
        out.append(f"Call: HOLD. {sig} Book is {e_now*100:.0f}% in stocks, target {e*100:.0f}%. {nxt}")
    else:
        call = "REBALANCE" if rescore else ("DE-RISK" if e < e_now else "RE-RISK")
        sells = [o["ticker"] for o in orders if o["side"] == "sell" and o["shares"] is None]
        trims = [o["ticker"] for o in orders if o["side"] == "sell" and o["shares"] is not None]
        buys = [o["ticker"] for o in orders if o["side"] == "buy" and o["ticker"] not in vals]
        adds = [o["ticker"] for o in orders if o["side"] == "buy" and o["ticker"] in vals]
        parts = [f"exit {', '.join(sells)}" if sells else "", f"new {', '.join(buys)}" if buys else "",
                 f"trim {len(trims)}" if trims else "", f"add to {len(adds)}" if adds else ""]
        out.append(f"Call: {call} ({why}). {sig} Target {e*100:.0f}% in stocks{', rest in XBI' if alt == 'xbi' and e < 1 else ', rest in cash' if e < 1 else ''}. "
                   f"Orders queued to fill at the next close: {'; '.join(x for x in parts if x)}. Turnover {sum(abs(o.get('dollars') or o.get('dollars_est') or 0) for o in orders)/nav*100:.0f}% of the book.")
    rk = []
    for t in held:
        p = px.get(t) or {}; ds = sorted(x for x in p if x <= d)
        if len(ds) > 21:
            rk.append((p[ds[-1]] / p[ds[-22]] - 1, t))
    rk.sort()
    if rk:
        out.append("Book over 21 trading days: best " + ", ".join(f"{t} {pct(r)}" for r, t in rk[::-1][:3]) +
                   "; worst " + ", ".join(f"{t} {pct(r)}" for r, t in rk[:3]) + ".")
    out.append(f"Scores use the 13F holdings in the ledger ({P.get('cands_asof', 'unknown')}); the Q3 rebuild is still outstanding.")
    L["last_decided"] = d
    L.setdefault("decisions", []).append({"date": d, "call": call, "target_stocks": e, "alt": alt, "signal": sg,
                                          "orders": [{k: v for k, v in o.items() if k in ("side", "ticker", "dollars", "dollars_est")} for o in orders]})
    L["decisions"] = L["decisions"][-120:]
    save(s)
    _decision_out(out, orders)


def _decision_out(lines, orders):
    """Put the call at the top of the report written by `run`."""
    rt, rh = os.path.join(HERE, "report.txt"), os.path.join(HERE, "report.html")
    txt = "\n".join(lines)
    blk = "<div style='font-family:Arial,sans-serif;font-size:14px;color:#1A1A1A;margin-bottom:12px'>" + "".join(
        f"<p style='margin:0 0 6px 0'>{'<b>' if i == 0 else ''}{html.escape(l)}{'</b>' if i == 0 else ''}</p>" for i, l in enumerate(lines)) + "</div>"
    if os.path.exists(rt):
        body = open(rt).read()
        if not body.startswith("Call:"):
            open(rt, "w").write(txt + "\n\n" + body)
            open(rh, "w").write(blk + open(rh).read())
    print(txt)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    {"flags": lambda: cmd_flags(), "run": lambda: cmd_run(), "decide": lambda: cmd_decide(),
     "order": lambda: cmd_order(a[1], a[2], a[3] if len(a) > 3 else "manual")}.get(a[0], lambda: sys.exit(__doc__))()
