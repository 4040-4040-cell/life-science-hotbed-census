"""Two-year backtest on daily prices, so results can be cut by month and year.
Same selections as backtest_2y.py (read from its per-quarter files), same 0.2% round-trip cost per quarter.
Each quarter: equal weight at the decision-day close, buy and hold to the next decision day, then rebalance.
Deal targets whose history vanished: held at cost until announcement, then at the one-day deal premium.
Benchmarks XBI, IBB, SPY (S&P 500): price return, 0.1% cost once. Strategies are also price return.
"""
import sys, json, glob
import numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/paper"); import engine
DECIDE = ["2024-11-15","2025-02-15","2025-05-15","2025-08-15","2025-11-15","2026-02-15","2026-05-15","2026-08-15"]
FINAL = "2026-11-13"; COST = 0.002
deals = pd.read_csv("data/deals_2024_2026.csv")
from backtest_2y_helpers import DEALT
deals["ticker"] = deals.target.map(lambda s: next((v for k, v in DEALT.items() if s.startswith(k)), None))
deals = deals.dropna(subset=["ticker"]).drop_duplicates("ticker").set_index("ticker")
P = {d: pd.read_csv(f"/tmp/bt2y_{d}.csv").set_index("t") for d in DECIDE}
names = sorted(set().union(*[set(p.index) for p in P.values()]))
px, _ = engine.prices(names + ["XBI", "IBB", "SPY"], "5y")
cal = sorted(d for d in px["XBI"] if DECIDE[0] <= d <= FINAL)
start = max(d for d in px["XBI"] if d <= DECIDE[0]); cal = [start] + [d for d in cal if d > start]

def path(t, d0, d1, days, deal):
    """Daily value of $1 in t from close d0 to close d1."""
    p = px.get(t) or {}
    if deal and len(p) <= 2:
        ann = deals.loc[t].announce_date; pr = str(deals.loc[t].premium_1day)
        prem = float(pr.strip("%")) / 100 if pr not in ("unknown", "nan") else 0.4
        return np.array([1.0 if d < ann else 1 + prem for d in days])
    b = p[max(x for x in p if x <= d0)]; last = b; out = []
    for d in days:
        last = p.get(d, last) if d <= max(p) else last
        out.append(last / b)
    return np.array(out)

def pick(Pq, key):
    q = max(1, round(len(Pq) / 4))
    if key == "pool": return list(Pq.index)
    if key == "five": return list(Pq[Pq.n >= 5].index)
    if key == "top10": return list(Pq.sort_values(["stage", "n"], ascending=False).head(10).index)
    return list(Pq.sort_values([key, "n"], ascending=False).head(q).index)

series = {k: [] for k in ("stage", "top10", "flat", "pool", "five")}
nav = {k: 1.0 for k in series}; daily_days = []
for i, d0 in enumerate(DECIDE):
    d1 = DECIDE[i + 1] if i + 1 < len(DECIDE) else FINAL
    s0 = max(d for d in px["XBI"] if d <= d0); s1 = max(d for d in px["XBI"] if d <= d1)
    days = [d for d in cal if s0 < d <= s1]
    for k in series:
        Pq = P[d0]; T = pick(Pq, k)
        v = np.mean([path(t, s0, s1, days, bool(Pq.loc[t, "deal"])) for t in T], axis=0)
        base = nav[k] * (1 - COST)
        series[k] += list(base * v); nav[k] = base * v[-1]
    daily_days += days
df = pd.DataFrame(series, index=daily_days)
for b in ("XBI", "IBB", "SPY"):
    p = px[b]; df[b] = [p[max(x for x in p if x <= d)] / p[start] * (1 - 0.001) for d in daily_days]
df.loc[start] = 1.0; df = df.sort_index()
df["tilt"] = (1 + (df.XBI.pct_change() + df.five.pct_change() - df.pool.pct_change()).fillna(0)).cumprod()
df.to_csv("out_backtest_2y_daily.csv")
me = df.groupby(df.index.str[:7]).last(); me = pd.concat([df.iloc[[0]].rename(index={start: "start"}), me])
monthly = (me / me.shift(1) - 1).iloc[1:]
def win(a, b):
    x = df[(df.index >= a) & (df.index <= b)]; return x.iloc[-1] / df[df.index <= a].iloc[-1] - 1
years = pd.DataFrame({"Nov 15-Dec 31, 2024": win(start, "2024-12-31"), "2025": win("2024-12-31", "2025-12-31"),
                      "2026 to Nov 13": win("2025-12-31", FINAL), "Year 1 (Nov 24-Nov 25)": win(start, "2025-11-14"),
                      "Year 2 (Nov 25-Nov 26)": win("2025-11-14", FINAL), "Two years": df.iloc[-1] - 1}).T
dd = (df / df.cummax() - 1).min()
monthly.to_csv("out_2y_monthly.csv"); years.to_csv("out_2y_years.csv")
pd.set_option("display.width", 200)
print((monthly * 100).round(1).to_string()); print((years * 100).round(1).to_string()); print((dd * 100).round(1).to_string())
mx = monthly.sub(monthly.XBI, axis=0)
print("months beating XBI:", (mx > 0).sum().to_dict())
