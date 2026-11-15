"""Two-year quarterly backtest, Nov 15, 2024 to Nov 13, 2026: eight holding periods, rebalanced the day after each
13F deadline using only filings filed by then. Answers: does the system lose to XBI every quarter or only lately,
and do the pre-registered challengers (C1 hedge against the pool, C2 flat size, C4 holder change) fix it?

Known limits (all flatter or penalize the baskets alike unless noted):
- Share counts are today's, so older market values are slightly overstated for companies that issued stock.
- Stage uses today's trial and revenue data (look-ahead) in the "stage" variants; "clean" uses holders and size only.
- Deal targets whose price history vanished after closing are valued at their one-day deal premium, assuming no drift
  between the period start and the announcement. Other delisted companies are missing (flatters the baskets).
- The stage and size multipliers were set from 2024 to 2026 deal data, so this is not a clean out-of-sample test.
"""
import os, glob, json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/paper")
import engine
from funds import SPECIALISTS
import screens as X

DECIDE = ["2024-11-15", "2025-02-15", "2025-05-15", "2025-08-15", "2025-11-15", "2026-02-15", "2026-05-15", "2026-08-15"]
FINAL = "2026-11-13"
COST = 0.002  # round trip per period, every name, every strategy

DEALT = {"Poseida": "PSTX", "Intra-Cellular": "ITCI", "Chimerix": "CMRX", "SpringWorks": "SWTX", "Regulus": "RGLS", "Vigil": "VIGL",
         "Blueprint": "BPMC", "CureVac": "CVAC", "Sage": "SAGE", "Verve": "VERV", "Verona": "VRNA", "Tourmaline": "TRML", "89bio": "ETNB",
         "Metsera": "MTSR", "Merus": "MRUS", "Akero": "AKRO", "Astria": "ATXS", "Avadel": "AVDL", "Avidity": "RNA", "Cidara": "CDTX",
         "Amicus": "FOLD", "Dynavax": "DVAX", "Ventyx": "VTYX", "RAPT": "RAPT", "Arcellx": "ACLX", "Day One": "DAWN", "Terns": "TERN",
         "Apellis": "APLS", "Centessa": "CNTA", "Soleno": "SLNO", "KalVista": "KALV", "Esperion": "ESPR", "Catalyst": "CPRX",
         "Nuvalent": "NUVL", "Apogee": "APGE", "Theravance": "TBPH", "Crinetics": "CRNX", "AtaiBeckley": "ATAI", "Forte": "FBRX",
         "Pacira": "PCRX", "Silence": "SLN"}
deals = pd.read_csv("data/deals_2024_2026.csv")
deals = deals[deals.scope.str.startswith("core") | deals.scope.str.startswith("upfront")]
deals["ticker"] = deals.target.map(lambda s: next((v for k, v in DEALT.items() if s.startswith(k)), None))
deals = deals.dropna(subset=["ticker"]).drop_duplicates("ticker").set_index("ticker")
prem = deals.premium_1day.map(lambda p: float(str(p).strip("%")) / 100 if str(p) not in ("unknown", "nan") else 0.4)
SB = {"Commercial": 1.5, "Filed": 1.2, "Ph3": 1.2, "Ph2": 1.0, "Ph1": 0.6}

# 13F files per fund, by filing date
files = {}
for f in glob.glob("data/h13f/*.parquet"):
    cik, d = os.path.basename(f)[:-8].split("_")
    files.setdefault(cik, []).append((d, f))
for c in files:
    files[c].sort()
_cache = {}
def holdings_at(day, back=0):
    """Each fund's filing `back` filings before its latest one filed on or before `day`."""
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
px, _ = engine.prices(sorted(names) + ["XBI"], "5y")
print("priced", len(px), "of", len(names) + 1)

def close_on_or_before(t, d):
    p = px.get(t) or {}
    ds = [x for x in p if x <= d]
    return p[max(ds)] if ds else None

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
size_flat = lambda m: 1.0 if m < 1e9 else 1.3

rows, periods = [], []
for i, d0 in enumerate(DECIDE):
    d1 = DECIDE[i + 1] if i + 1 < len(DECIDE) else FINAL
    h = holdings_at(d0); n = h.groupby("Ticker").cik.nunique()
    hp = holdings_at(d0, back=1); prevset = set(zip(hp.Ticker, hp.cik))
    added = h[[ (t, c) not in prevset for t, c in zip(h.Ticker, h.cik)]].groupby("Ticker").cik.nunique()
    recs = []
    for t in names:
        if n.get(t, 0) < 3: continue
        if t in deals.index and deals.loc[t].announce_date <= d0: continue           # deal already public
        gone = t in deals.index and len(px.get(t) or {}) <= 2
        in_period_deal = t in deals.index and d0 < deals.loc[t].announce_date <= d1
        if gone and not in_period_deal: continue                                    # cannot price it
        if gone:
            v = deals.loc[t].implied_pre_deal_mktcap_usd_m
            if str(v) in ("unknown", "nan"): continue
            mcap, r = float(v) * 1e6, prem[t]
        else:
            p0 = close_on_or_before(t, d0)
            p1 = close_on_or_before(t, d1)
            sh = u.loc[t, "shares_out"] if t in u.index else np.nan
            if p0 is None or p1 is None or pd.isna(sh): continue
            if min(x for x in px[t]) > d0: continue                                 # not trading yet
            mcap, r = p0 * sh, p1 / p0 - 1
        if not (0.5e9 <= mcap <= 25e9): continue
        recs.append(dict(t=t, n=int(n[t]), added=int(added.get(t, 0)), mcap=mcap, r=r - COST, st=stage_m(t), deal=in_period_deal))
    P = pd.DataFrame(recs).set_index("t")
    hm = np.where(P.n >= 5, 1.0, 0.4)
    P["clean"] = hm * P.mcap.map(size_m)
    P["stage"] = P.clean * P.st
    P["flat"] = hm * P.mcap.map(size_flat) * P.st                                    # C2
    P["chg"] = np.where(P.added >= 2, 1.0, 0.4) * P.mcap.map(size_m) * P.st          # C4
    q = max(1, round(len(P) / 4))
    top = lambda col: P.sort_values([col, "n"], ascending=False).head(q)
    x0, x1 = close_on_or_before("XBI", d0), close_on_or_before("XBI", d1)
    res = {"start": d0, "end": d1, "pool_n": len(P), "deals_in_pool": int(P.deal.sum()),
           "XBI": x1 / x0 - 1 - 0.001, "pool": P.r.mean(), "five": P[P.n >= 5].r.mean()}
    for col in ("clean", "stage", "flat", "chg"):
        T = top(col); res[col] = T.r.mean(); res[col + "_deals"] = int(T.deal.sum())
    res["top10_stage"] = P.sort_values(["stage","n"], ascending=False).head(10).r.mean()
    res["h3_4"] = P[P.n <= 4].r.mean(); res["h8p"] = P[P.n >= 8].r.mean()
    P.assign(start=d0).to_csv(f"/tmp/bt2y_{d0}.csv")
    periods.append(res)
    print(d0, "->", d1, "pool", len(P), "deals", int(P.deal.sum()), {k: round(v, 3) for k, v in res.items() if isinstance(v, float)})

R = pd.DataFrame(periods).set_index("start")
R["hedge_stage"] = R["stage"] - R["pool"]                       # C1: long system, short pool basket
R["overlay"] = R["XBI"] + R["hedge_stage"]                      # XBI plus the market-neutral takeover spread
R["overlay_five"] = R["XBI"] + (R["five"] - R["pool"])
R["core70"] = 0.7 * R["XBI"] + 0.3 * R["stage"]
keys = ["XBI", "pool", "five", "clean", "stage", "flat", "chg", "hedge_stage", "overlay", "overlay_five", "core70", "top10_stage", "h3_4", "h8p"]
summ = {}
for k in keys:
    s = R[k]
    summ[k] = {"total": round(float((1 + s).prod() - 1), 4), "per_q_mean": round(float(s.mean()), 4),
               "beats_xbi_quarters": int((s > R.XBI).sum()) if k != "XBI" else None,
               "t_vs_xbi": round(float((s - R.XBI).mean() / ((s - R.XBI).std(ddof=1) / np.sqrt(len(s)))), 2) if k != "XBI" else None,
               "worst_q": round(float(s.min()), 4)}
R.to_csv("out_backtest_2y.csv")
json.dump({"periods": periods, "summary": summ}, open("out_backtest_2y.json", "w"), indent=1, default=float)
print(pd.DataFrame(summ).T.to_string())
