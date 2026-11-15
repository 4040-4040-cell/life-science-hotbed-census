"""Loss-control lab. Rules and pass marks are pre-registered in loss_control_prereg.md (commit 830f672).
Tuning window Nov 15, 2024 to Nov 13, 2026; holdout Aug 15, 2023 to Nov 15, 2024. Daily simulation, signals
read at a close and acted on at the next close. Writes out_loss_lab.json, out_loss_lab_daily.csv.
"""
import os, glob, json, sys, pickle
import numpy as np, pandas as pd
os.chdir("/home/claude/lsbook"); sys.path.insert(0, "/home/claude/lsbook"); sys.path.insert(0, "/home/claude/paper")
import engine
import screens as X
from backtest_2y_helpers import DEALT

DEALT = dict(DEALT, **{"Ambrx": "AMAM", "Harpoon": "HARP", "MorphoSys": "MOR", "CymaBay": "CBAY", "Fusion": "FUSN",
                       "Alpine": "ALPN", "Deciphera": "DCPH", "Calliditas": "CALT", "Morphic": "MORF", "Revance": "RVNC",
                       "Longboard": "LBPH"})
HOLD = ["2023-08-15", "2023-11-15", "2024-02-15", "2024-05-15", "2024-08-15"]
TUNE = ["2024-11-15", "2025-02-15", "2025-05-15", "2025-08-15", "2025-11-15", "2026-02-15", "2026-05-15", "2026-08-15"]
DECIDE = HOLD + TUNE
FINAL = "2026-11-13"
QCOST, SWITCH, CASH = 0.002, 0.005, 0.04 / 252

deals = pd.read_csv("data/deals_2024_2026.csv")
deals = deals[deals.scope.str.startswith("core") | deals.scope.str.startswith("upfront")]
deals["ticker"] = deals.target.map(lambda s: next((v for k, v in DEALT.items() if s.startswith(k)), None))
deals = deals.dropna(subset=["ticker"]).drop_duplicates("ticker").set_index("ticker")
prem = deals.premium_1day.map(lambda p: float(str(p).strip("%")) / 100 if str(p) not in ("unknown", "nan") else 0.4)
SB = {"Commercial": 1.5, "Filed": 1.2, "Ph3": 1.2, "Ph2": 1.0, "Ph1": 0.6}

files = {}
for f in glob.glob("data/h13f/*.parquet"):
    cik, d = os.path.basename(f)[:-8].split("_")
    files.setdefault(cik, []).append((d, f))
for c in files:
    files[c].sort()
_cache = {}
def holdings_at(day, back=0):
    out = []
    for c, lst in files.items():
        ok = [x for x in lst if x[0] <= day]
        if len(ok) > back:
            f = ok[-1 - back][1]
            if f not in _cache:
                h = pd.read_parquet(f); _cache[f] = h[h.SharesPrnAmount > 0].dropna(subset=["Ticker"])
            out.append(_cache[f].assign(cik=c))
    return pd.concat(out)

u = pd.read_parquet("data/universe.parquet")
tp = pd.read_parquet("data/targets.parquet")
names = set(u.index[(u.sic.isin(X.BIO_SIC))]) | set(deals.index)
names = {t for t in names if t not in X.RESTRICTED and not (len(t) == 5 and t.endswith("W"))}
PK = "px_cache_5y.pkl"
if os.path.exists(PK):
    px = pickle.load(open(PK, "rb"))
else:
    px, _ = engine.prices(sorted(names) + ["XBI", "IBB", "SPY", "^VIX"], "5y"); pickle.dump(px, open(PK, "wb"))
print("priced", len(px))

cal = sorted(d for d in px["XBI"] if d <= FINAL)
C = pd.DataFrame({t: pd.Series(v) for t, v in px.items() if v}).reindex(cal)
C = C.apply(lambda s: s.ffill().where(s.ffill().notna()))
def last_on(d): return max(x for x in cal if x <= d)

def stage_m(t):
    if t in deals.index and len(px.get(t) or {}) <= 2:
        return SB.get(deals.loc[t].stage_bin, 1.0)
    if t in tp.index:
        r = tp.loc[t]
        if (r.revenue_ttm or 0) >= 50e6 and (r.max_phase or 0) >= 3: return 1.5
        mp = r.max_phase or 0
        return 1.2 if mp >= 3 else 1.0 if mp >= 2 else 0.6 if mp >= 1 else 0.35
    return 1.5 if t in u.index and (u.loc[t, "revenue_ttm"] or 0) >= 50e6 else 1.0
size_m = lambda m: 1.0 if m < 1e9 else 1.3 if m < 5e9 else 0.9 if m < 10e9 else 0.55

# ---- quarterly candidate pools and relative price panels -------------------------------------------------
Q = []
for i, d0 in enumerate(DECIDE):
    d1 = DECIDE[i + 1] if i + 1 < len(DECIDE) else FINAL
    s0, s1 = last_on(d0), last_on(d1)
    days = [d for d in cal if s0 <= d <= s1]
    h = holdings_at(d0)
    try:
        hp = holdings_at(d0, back=1)
    except ValueError:  # first quarter: no earlier filing, cuts unknown (treated as zero)
        hp = h.iloc[0:0]
    n = h.groupby("Ticker").cik.nunique()
    now = h.groupby(["Ticker", "cik"]).SharesPrnAmount.sum(); prev = hp.groupby(["Ticker", "cik"]).SharesPrnAmount.sum()
    cutpairs = [(t, c) for (t, c), sp in prev.items() if now.get((t, c), 0) < 0.8 * sp and c in set(h.cik)]
    ncut = pd.Series([t for t, c in cutpairs]).value_counts() if cutpairs else pd.Series(dtype=int)
    recs, panel = [], {}
    for t in names:
        if n.get(t, 0) < 3: continue
        if t in deals.index and deals.loc[t].announce_date <= d0: continue
        gone = t in deals.index and len(px.get(t) or {}) <= 2
        in_deal = t in deals.index and d0 < deals.loc[t].announce_date <= d1
        if gone and not in_deal: continue
        if gone:
            v = deals.loc[t].implied_pre_deal_mktcap_usd_m
            if str(v) in ("unknown", "nan"): continue
            mcap, vol = float(v) * 1e6, np.nan
            ann = deals.loc[t].announce_date
            panel[t] = pd.Series([1.0 if d < ann else 1 + prem[t] for d in days], index=days)
        else:
            if t not in C or pd.isna(C.at[s0, t]) or min(px[t]) > d0: continue
            sh = u.loc[t, "shares_out"] if t in u.index else np.nan
            if pd.isna(sh): continue
            mcap = C.at[s0, t] * sh
            hist = C[t].loc[:s0].dropna().iloc[-64:]
            vol = float(np.log(hist).diff().std() * np.sqrt(252)) if len(hist) > 40 else np.nan
            panel[t] = C[t].loc[s0:s1] / C.at[s0, t]
        if not (0.5e9 <= mcap <= 25e9): panel.pop(t, None); continue
        recs.append(dict(t=t, n=int(n[t]), cut=int(ncut.get(t, 0)), mcap=mcap, st=stage_m(t), deal=in_deal, vol=vol))
    P = pd.DataFrame(recs).set_index("t")
    P["vol"] = P.vol.fillna(P.vol.median())
    P["score"] = np.where(P.n >= 5, 1.0, 0.4) * P.mcap.map(size_m) * P.st
    pairs_now = int(h[h.Ticker.isin(P.index)].groupby(["Ticker", "cik"]).ngroups)
    pairs_prev = int(hp[hp.Ticker.isin(P.index)].groupby(["Ticker", "cik"]).ngroups)
    Q.append(dict(d0=d0, s0=s0, s1=s1, days=days, P=P, R=pd.DataFrame(panel)[P.index], pairs_now=pairs_now, pairs_prev=pairs_prev))
    print(d0, "pool", len(P), "deals", int(P.deal.sum()))

# pool basket index (equal weight, quarterly) for the relative-strength signal
pool_idx = pd.Series(index=cal, dtype=float); v = 1.0
for q in Q:
    path = q["R"].mean(axis=1) * v
    pool_idx.loc[path.index] = path.values; v = path.iloc[-1]
xbi = C["XBI"]; vix = C["^VIX"]
ma = {k: xbi.rolling(k).mean() for k in (100, 200)}
rs21 = (pool_idx / pool_idx.shift(21)) - (xbi / xbi.shift(21))

# ---- simulation ------------------------------------------------------------------------------------------
cal_idx = {d: i for i, d in enumerate(cal)}
prevday = lambda d: cal[cal_idx[d] - 1]

def select(P, p, rel=None):
    P = P.copy()
    if rel is not None:  # monthly re-score with current value
        P["mcap"] = P.mcap * rel.reindex(P.index).fillna(1.0)
        P["score"] = np.where(P.n >= 5, 1.0, 0.4) * P.mcap.map(size_m) * P.st
    if p.get("volscreen"): P = P[P.vol <= P.vol.quantile(1 - p["volscreen"])]
    if p.get("cutscreen"): P = P[P.cut < p["cutscreen"]]
    k = p.get("top")
    k = max(1, round(len(P) / 4)) if k is None else k
    T = P.assign(_t=P.index).sort_values(["score", "n", "_t"], ascending=[False, False, True]).head(k)  # ticker breaks ties: reproducible
    return (1 / T.vol) / (1 / T.vol).sum() if p.get("invvol") else pd.Series(1 / len(T), index=T.index)

def overlay_series(p):
    """Market-signal target exposure decided at each close (independent of the portfolio)."""
    core = p.get("core", 1.0); tg = {}; rs_on = vx_on = False
    for d in cal:
        c = [(core, "xbi" if core < 1 else "cash")]
        if p.get("rs"):
            g = rs21.get(d, np.nan)
            if not np.isnan(g):
                rs_on = True if g <= -p["rs"] else False if g > 0 else rs_on
            if rs_on: c.append((0.0, "xbi"))
        if p.get("trend"):
            m = ma[p["trend"]].get(d, np.nan)
            if not np.isnan(m) and xbi.at[d] < m: c.append((0.5 * core, "cash"))
        if p.get("vix"):
            hi, lo = p["vix"]; vv = vix.get(d, np.nan)
            if not np.isnan(vv):
                vx_on = True if vv > hi else False if vv < lo else vx_on
            if vx_on: c.append((0.5 * core, "cash"))
        tg[d] = min(c, key=lambda z: z[0])
    return tg

def run(qs, p):
    core = p.get("core", 1.0); tg = overlay_series(p)
    nav = peak = 1.0; first = True; braked = False
    hold = pd.Series(dtype=float); pocket = altv = 0.0; e, alt = core, ("xbi" if core < 1 else "cash")
    out, expo, stops_pending = [], [], []
    for q in qs:
        days, R, P = q["days"], q["R"], q["P"]
        mreb = {d for i, d in enumerate(days) if i > 0 and d[:7] != days[i - 1][:7]} if p.get("monthly") else set()
        for i, d in enumerate(days):
            if i > 0:
                hold = hold * (R.loc[d] / R.loc[days[i - 1]]).reindex(hold.index).fillna(1.0)
                rx = xbi.at[d] / xbi.at[days[i - 1]]
                pocket *= rx
                altv *= rx if alt == "xbi" else 1 + CASH
            if i == 0:  # quarterly rebalance at the decision-day close
                total = 1.0 if first else hold.sum() + pocket + altv
                total *= 1 - QCOST; braked = False
                e, alt = (core, alt) if first else tg[prevday(d)]
                w = select(P, p)
                hold = w * total * e; pocket = 0.0; altv = total * (1 - e)
                base, xentry = R.loc[d].copy(), xbi.at[d]; stops_pending = []; first = False
            else:
                if d in mreb:
                    sleeve = hold.sum() + pocket
                    w = select(P, p, rel=R.loc[d])
                    old = hold / hold.sum() if hold.sum() > 0 else pd.Series(dtype=float)
                    cost = QCOST * 0.5 * w.subtract(old, fill_value=0).abs().sum()
                    hold = w * sleeve * (1 - cost); pocket = 0.0
                    base, xentry = R.loc[d].copy(), xbi.at[d]; stops_pending = []
                for t in stops_pending:  # decided at the previous close
                    if hold.get(t, 0) > 0:
                        pocket += hold[t] * (1 - SWITCH); hold[t] = 0.0
                stops_pending = []
                c = [tg[prevday(d)]] + ([(0.5 * core, "cash")] if braked else [])
                want, walt = min(c, key=lambda z: z[0])
                if abs(want - e) > 1e-9 or (walt != alt and altv > 0):
                    if walt != alt and altv > 0: altv *= 1 - SWITCH
                    alt = walt
                    sleeve = hold.sum() + pocket; total = sleeve + altv
                    move = total * want - sleeve
                    if move < -1e-12:
                        f = -move / sleeve
                        hold = hold * (1 - f); pocket *= 1 - f; altv += -move * (1 - SWITCH)
                    elif move > 1e-12:
                        move = min(move, altv); altv -= move; add = move * (1 - SWITCH)
                        if hold.sum() > 0: hold = hold + add * hold / hold.sum()
                        else: pocket += add
                    e = want
            nav = hold.sum() + pocket + altv
            peak = max(peak, nav)
            out.append((d, nav)); expo.append((d, (hold.sum() + pocket) / nav))
            # decisions at this close, executed at the next
            if p.get("brake") and nav / peak - 1 <= -p["brake"]: braked = True
            if p.get("stop") or p.get("relstop"):
                rel_now = R.loc[d] / base; xr = xbi.at[d] / xentry - 1
                for t in hold.index:
                    if hold[t] <= 0: continue
                    rr = rel_now.get(t, 1.0) - 1
                    if (p.get("stop") and rr <= -p["stop"]) or (p.get("relstop") and rr - xr <= -p["relstop"]):
                        stops_pending.append(t)
    s = pd.Series(dict(out)); x = pd.Series(dict(expo))
    return s, x

VARIANTS = {
    "Base system": {},
    "R1 stop 20%": {"stop": 0.20}, "R1 stop 30%": {"stop": 0.30},
    "R2 rel stop 20": {"relstop": 0.20}, "R2 rel stop 30": {"relstop": 0.30},
    "R3 brake 15%": {"brake": 0.15}, "R3 brake 20%": {"brake": 0.20},
    "R4 RS switch 5": {"rs": 0.05}, "R4 RS switch 8": {"rs": 0.08},
    "R5 trend 100d": {"trend": 100}, "R5 trend 200d": {"trend": 200},
    "R6 vol screen 25%": {"volscreen": 0.25}, "R6 vol screen 33%": {"volscreen": 1 / 3},
    "R7 inverse vol": {"invvol": True},
    "R8 cut screen 2": {"cutscreen": 2}, "R8 cut screen 3": {"cutscreen": 3},
    "R9 VIX 25/20": {"vix": (25, 20)}, "R9 VIX 30/25": {"vix": (30, 25)},
    "R10 core 50/50": {"core": 0.5}, "R10 core 70/30": {"core": 0.3},
    "R11 monthly": {"monthly": True},
    "R12 top 20": {"top": 20}, "R12 top 10": {"top": 10},
}

def bench(t, days):
    s = C[t].loc[days[0]:days[-1]]; return s / s.iloc[0] * (1 - 0.001)

def metrics(s, xb):
    tot = s.iloc[-1] / s.iloc[0] - 1
    dd = float((s / s.cummax() - 1).min())
    me = s.groupby(s.index.str[:7]).last(); me = pd.concat([s.iloc[:1], me])
    mx = xb.groupby(xb.index.str[:7]).last(); mx = pd.concat([xb.iloc[:1], mx])
    mr, mxr = me.pct_change().dropna(), mx.pct_change().dropna()
    return dict(total=round(tot, 4), maxdd=round(dd, 4), ret_per_dd=round(tot / abs(dd), 3) if dd else None,
                worst_month=round(float(mr.min()), 4), months_beat_xbi=int((mr.values > mxr.values).sum()), months=len(mr))

res, series = {}, {}
for win, qs in (("tune", [q for q in Q if q["d0"] in TUNE]), ("hold", [q for q in Q if q["d0"] in HOLD])):
    days = [d for q in qs for d in q["days"]]; days = sorted(set(days))
    xb = bench("XBI", days)
    res[win] = {"XBI": metrics(xb, xb), "IBB": metrics(bench("IBB", days), xb), "S&P 500": metrics(bench("SPY", days), xb)}
    for name, p in VARIANTS.items():
        s, x = run(qs, p)
        m = metrics(s, xb); m["avg_exposure"] = round(float(x.mean()), 3)
        if win == "tune":
            m["y2025"] = round(float(s[s.index <= "2025-12-31"].iloc[-1] / s[s.index <= "2024-12-31"].iloc[-1] - 1), 4)
            m["sep_oct_2026"] = round(float(s[s.index <= "2026-10-31"].iloc[-1] / s[s.index <= "2026-08-31"].iloc[-1] - 1), 4)
        res[win][name] = m; series[(win, name)] = s
    print(win, "done")

json.dump(res, open("out_loss_lab.json", "w"), indent=1)
pickle.dump({"series": series, "Q": [{k: v for k, v in q.items() if k != "R"} for q in Q]}, open("loss_lab_series.pkl", "wb"))
for win in res:
    print("\n==", win)
    print(pd.DataFrame(res[win]).T.to_string())
