"""Six-month backtest of the takeover portfolio rules: decide on May 15, 2026 using only 13F filings filed by then,
buy at the May 18 close, hold to the Nov 13, 2026 close, $5,000 each. Writes out_backtest_6m.json and out_backtest_6m.csv.

Strategies (equal weight, 10 bps slippage each side, deal targets held at the deal value):
  pool     every drug company held by 3+ of the 30 specialist funds, $0.5B to $25B value  (the benchmark basket)
  five     the same pool, only names with 5+ specialist holders                             (the tested rule)
  lite     top quarter of the pool ranked by the model's point-in-time factors: holders (1.0 at 5+, else 0.4)
           x size (May 15 value) x stage (revenue and furthest trial phase as known today: mild look-ahead)
  XBI      the biotech index
Known limits: companies that delisted for reasons other than an acquisition between May and November are missing
(survivorship that flatters the pool); deal targets whose price history vanished after closing are valued from the
day-before-announcement price implied by the deal file, assuming no drift between May 18 and that day.
"""
import os, glob, json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/paper")
import engine
from funds import SPECIALISTS
import screens as X

DECIDE, START, END = "2026-05-15", "2026-05-18", "2026-11-13"
SLIP = 0.001
CAP = 5000.0

# 1. point-in-time holders: each fund's latest 13F filed on or before May 15
files = {}
for f in glob.glob("data/h13f/*.parquet"):
    cik, d = os.path.basename(f)[:-8].split("_")
    if d <= DECIDE and int(cik) in {int(c) for c in SPECIALISTS} and (cik not in files or d > files[cik][0]):
        files[cik] = (d, f)
hold = pd.concat([pd.read_parquet(f).assign(cik=c) for c, (d, f) in files.items()])
hold = hold[hold.SharesPrnAmount > 0].dropna(subset=["Ticker"])
nspec = hold.groupby("Ticker").cik.nunique()
print("funds with a filing by May 15:", len(files), "of", len(SPECIALISTS))

# 2. universe and May 15 value
u = pd.read_parquet("data/universe.parquet")
deals0 = pd.read_csv("data/deals_2024_2026.csv")
DEALT = {"NUVL", "APGE", "CRNX", "ATAI", "FBRX", "SLN", "TBPH", "PCRX"}
nosic = [t for t in u.index if pd.isna(u.loc[t, "sic"]) and nspec.get(t, 0) >= 3]
print("held by 3+ but no SEC industry code today (delisted?):", nosic)
u = u[(u.sic.isin(X.BIO_SIC) | u.index.isin(DEALT)) & ~u.index.isin(X.RESTRICTED)]
u = u[~((u.index.str.len() == 5) & u.index.str.endswith("W"))]
cand = [t for t in u.index if nspec.get(t, 0) >= 3]
px, src = engine.prices(cand + ["XBI"], "1y")
deals = pd.read_csv("data/deals_2024_2026.csv")
TICK = {"Nuvalent": "NUVL", "Apogee Therapeutics": "APGE", "Crinetics Pharmaceuticals": "CRNX", "AtaiBeckley": "ATAI",
        "Forte Biosciences": "FBRX", "Silence Therapeutics": "SLN", "Theravance Biopharma": "TBPH", "Pacira BioSciences": "PCRX"}
deals["ticker"] = deals.target.map(lambda s: next((v for k, v in TICK.items() if s.startswith(k)), None))
win = deals[(deals.announce_date > DECIDE) & (deals.announce_date <= END) & deals.ticker.notna()].set_index("ticker")

rows = []
for t in cand:
    p = px.get(t) or {}
    ds = sorted(d for d in p if d <= DECIDE)
    gone = t in win.index and len(p) <= 2  # history vanished after the deal closed
    if gone:
        r = win.loc[t]
        pre = float(r.implied_pre_deal_mktcap_usd_m) * 1e6 if str(r.implied_pre_deal_mktcap_usd_m) not in ("unknown", "nan") else np.nan
        mcap = pre
    elif ds:
        mcap = p[ds[-1]] * (u.loc[t, "shares_out"] or np.nan)
    else:
        continue
    rows.append(dict(ticker=t, n=int(nspec[t]), mcap=mcap, gone=gone))
pool = pd.DataFrame(rows).set_index("ticker")
pool = pool[(pool.mcap >= 0.5e9) & (pool.mcap <= 25e9)]

# 3. lite score: holders x size x stage (stage from today's targets/universe data where available)
tp = pd.read_parquet("data/targets.parquet")
SB = {"Commercial": 1.5, "Filed": 1.2, "Ph3": 1.2, "Ph2": 1.0, "Ph1": 0.6}
def stage_m(t):
    if t in win.index and pool.loc[t, "gone"]:
        return SB.get(win.loc[t].stage_bin, 1.0)   # stage at announcement from the deal file (known in May)
    if t in tp.index:
        r = tp.loc[t]
        if (r.revenue_ttm or 0) >= 50e6 and (r.max_phase or 0) >= 3: return 1.5
        mp = r.max_phase or 0
        return 1.2 if mp >= 3 else 1.0 if mp >= 2 else 0.6 if mp >= 1 else 0.35
    return 1.5 if (u.loc[t, "revenue_ttm"] or 0) >= 50e6 else 1.0   # not in today's pool: no trial data, neutral
pool["lite"] = [(1.0 if r.n >= 5 else 0.4) * engine_size for engine_size, r in
                zip([1.0 if m < 1e9 else 1.3 if m < 5e9 else 0.9 if m < 10e9 else 0.55 for m in pool.mcap], pool.itertuples())]
pool["lite"] *= [stage_m(t) for t in pool.index]
q = int(round(len(pool) / 4))
lite = list(pool.sort_values(["lite", "n"], ascending=False).index[:q])
five = list(pool[pool.n >= 5].index)
print("pool", len(pool), "five", len(five), "lite", len(lite), "deal targets in pool:", [t for t in pool.index if t in win.index])

# 4. daily values
xbi = px["XBI"]
days = sorted(d for d in xbi if START <= d <= END)

def series(names):
    per = CAP / len(names)
    val = {d: 0.0 for d in days}
    notes = []
    for t in names:
        p = px.get(t) or {}
        if pool.loc[t, "gone"]:
            r = win.loc[t]
            prem = float(str(r.premium_1day).strip("%")) / 100 if str(r.premium_1day) not in ("unknown", "nan") else 0.0
            ann = r.announce_date
            dv = per * (1 - SLIP) / (1 + SLIP) * (1 + prem)        # entry at the unaffected price, exit at the deal price
            for d in days:
                val[d] += per if d < ann else dv
            notes.append(f"{t}: est. {prem:+.0%} at the {ann} announcement (price history removed after closing)")
            continue
        if START not in p:
            ds = sorted(x for x in p if x >= START)
            if not ds: continue
        e = p.get(START) or p[min(x for x in p if x >= START)]
        sh = per / (e * (1 + SLIP))
        last = e
        for d in days:
            last = p.get(d, last)
            val[d] += sh * last
        if t in win.index:
            notes.append(f"{t}: announced {win.loc[t].announce_date}, held at market price (still trading)")
    for d in days:
        val[d] = val[d] - (CAP / len(names)) * 0  # equal weight already applied
    final = {d: v * (1 - SLIP) if d == days[-1] else v for d, v in val.items()}
    return pd.Series(final), notes

out, notes = {}, {}
for k, names in (("lite", lite), ("five", five), ("pool", list(pool.index))):
    out[k], notes[k] = series(names)
xs = CAP / (xbi[START] * (1 + SLIP))
out["XBI"] = pd.Series({d: xs * xbi[d] * (1 - SLIP if d == days[-1] else 1) for d in days})
df = pd.DataFrame(out)
df.to_csv("out_backtest_6m.csv")

# 5. monthly and total
def month_table(s):
    m = s.groupby(s.index.str[:7]).last()
    prev = pd.concat([pd.Series({"start": CAP}), m]).shift(1).dropna()
    return (m / prev.values - 1)

res = {"decide": DECIDE, "start": START, "end": END, "names": {"lite": lite, "five": five, "pool_n": len(pool)},
       "monthly": {k: {mm: round(v, 4) for mm, v in month_table(df[k]).items()} for k in df},
       "final_value": {k: round(df[k].iloc[-1], 2) for k in df},
       "total_return": {k: round(df[k].iloc[-1] / CAP - 1, 4) for k in df},
       "max_drawdown": {k: round(float((df[k] / df[k].cummax() - 1).min()), 4) for k in df},
       "notes": notes, "deal_targets_in_window": list(win.index)}
# per-name contribution for the lite portfolio
contrib = {}
for t in lite:
    p = px.get(t) or {}
    if pool.loc[t, "gone"]:
        continue
    e = p.get(START) or p[min(x for x in p if x >= START)]
    l = p[max(x for x in p if x <= END)]
    contrib[t] = round(l / e - 1, 4)
res["lite_name_returns"] = dict(sorted(contrib.items(), key=lambda x: -x[1]))
json.dump(res, open("out_backtest_6m.json", "w"), indent=1)
print(json.dumps({k: res[k] for k in ("monthly", "final_value", "total_return", "max_drawdown")}, indent=1))
print(notes)
print(res["lite_name_returns"])
