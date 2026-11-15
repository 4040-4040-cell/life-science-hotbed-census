"""Judge the rules against the pre-registered pass marks, run the package, and answer the diagnostic questions."""
import json
src = open("/home/claude/lsbook/loss_lab.py").read()
exec(src[:src.index("VARIANTS = {")])
exec(src[src.index("def bench("):src.index("res, series = {}, {}")])
lab = json.load(open("out_loss_lab.json"))

# 1. pass marks, exactly as committed in 830f672
pairs = {"R1": ["R1 stop 20%", "R1 stop 30%"], "R2": ["R2 rel stop 20", "R2 rel stop 30"], "R3": ["R3 brake 15%", "R3 brake 20%"],
         "R4": ["R4 RS switch 5", "R4 RS switch 8"], "R5": ["R5 trend 100d", "R5 trend 200d"], "R6": ["R6 vol screen 25%", "R6 vol screen 33%"],
         "R7": ["R7 inverse vol"], "R8": ["R8 cut screen 2", "R8 cut screen 3"], "R9": ["R9 VIX 25/20", "R9 VIX 30/25"],
         "R10": ["R10 core 50/50", "R10 core 70/30"], "R11": ["R11 monthly"], "R12": ["R12 top 20", "R12 top 10"]}
bt, bh = lab["tune"]["Base system"], lab["hold"]["Base system"]
def tune_pass(m):
    a = (m["maxdd"] - bt["maxdd"] >= 0.03 - 1e-9) and (m["total"] >= bt["total"] - 0.03)
    b = m["ret_per_dd"] >= 1.2 * bt["ret_per_dd"]
    return a or b
verdict = {}
for r, vs in pairs.items():
    ok = [v for v in vs if tune_pass(lab["tune"][v])]
    if not ok:
        verdict[r] = {"setting": None, "tune": "fail", "hold": None}; continue
    best = max(ok, key=lambda v: lab["tune"][v]["ret_per_dd"])
    h = lab["hold"][best]
    conf = h["maxdd"] >= bh["maxdd"] - 1e-9 and h["ret_per_dd"] >= bh["ret_per_dd"] - 1e-9
    verdict[r] = {"setting": best, "tune": "pass", "hold": "confirmed" if conf else "rejected",
                  "fired_in_holdout": h["avg_exposure"] < 0.999 or h["total"] != bh["total"]}
print(json.dumps(verdict, indent=1))

# 2. package and full-span runs
PARAMS = {"Base system": {}, "Package": {"rs": 0.08, "trend": 200, "monthly": True}, "R4 + R5 only": {"rs": 0.08, "trend": 200}}
win_q = {"tune": [q for q in Q if q["d0"] in TUNE], "hold": [q for q in Q if q["d0"] in HOLD], "full": Q}
out = {}; full = {}
for w, qs in win_q.items():
    days = sorted({d for q in qs for d in q["days"]}); xb = bench("XBI", days)
    out[w] = {"XBI": metrics(xb, xb), "IBB": metrics(bench("IBB", days), xb), "S&P 500": metrics(bench("SPY", days), xb)}
    for k, p in PARAMS.items():
        s, x = run(qs, p); m = metrics(s, xb); m["avg_exposure"] = round(float(x.mean()), 3); out[w][k] = m
        if w == "full": full[k] = s; full[k + " exposure"] = x
    if w == "full":
        for b in ("XBI", "IBB", "SPY"): full[b] = bench(b, days)
# slippage sensitivity for the package (Q43)
SWITCH = 0.01
s, _ = run(win_q["tune"], PARAMS["Package"]); out["tune"]["Package, 1% switch cost"] = metrics(s, bench("XBI", sorted({d for q in win_q["tune"] for d in q["days"]})))
SWITCH = 0.005
F = pd.DataFrame(full); F.to_csv("out_loss_lab_full_daily.csv")
for w in ("tune", "hold", "full"):
    print("\n==", w); print(pd.DataFrame(out[w]).T.to_string())

# 3. calendar years and months, full span
cols = ["Base system", "Package", "XBI", "IBB", "SPY"]
def span(a, b):
    x = F[cols]; return x[x.index <= b].iloc[-1] / x[x.index <= a].iloc[-1] - 1
yrs = pd.DataFrame({"Aug 15 to Dec 31, 2023": span(F.index[0], "2023-12-31"), "2024": span("2023-12-31", "2024-12-31"),
                    "2025": span("2024-12-31", "2025-12-31"), "2026 to Nov 13": span("2025-12-31", FINAL),
                    "Holdout (Aug 2023 to Nov 2024)": span(F.index[0], "2024-11-15"),
                    "Two years (Nov 2024 to Nov 2026)": span("2024-11-15", FINAL), "Full span": F[cols].iloc[-1] / F[cols].iloc[0] - 1}).T
me = F[cols].groupby(F.index.str[:7]).last(); me = pd.concat([F[cols].iloc[:1], me]); mon = me.pct_change().iloc[1:]
mon["Package exposure"] = F["Package exposure"].groupby(F.index.str[:7]).mean()
yrs.to_csv("out_loss_years.csv"); mon.to_csv("out_loss_monthly.csv")
print((yrs * 100).round(1).to_string()); print((mon * 100).round(1).to_string())

# 4. diagnostics
D = {}
b = F["Base system"]; x = F["XBI"]
rb, rx = b.pct_change().dropna(), x.pct_change().dropna()
beta = float(np.cov(rb, rx)[0, 1] / rx.var()); r2 = float(np.corrcoef(rb, rx)[0, 1] ** 2)
D["Q4 beta, share of daily variance explained by XBI"] = [round(beta, 2), round(r2, 2)]
sep = {y: [round(float(span(f"{y}-08-31", f"{y}-09-30")[c]), 4) for c in ("Base system", "XBI")] for y in (2023, 2024, 2025, 2026)}
D["Q38 September base vs XBI"] = sep
rows = []
for q in Q:
    P, R = q["P"], q["R"]; w = select(P, {})
    xr = xbi.at[q["s1"]] / xbi.at[q["s0"]] - 1
    P = P.assign(r=R.iloc[-1] - 1, ex=R.iloc[-1] - 1 - xr, pick=P.index.isin(w.index), q=q["d0"],
                 vrank=P.vol.rank(pct=True), minpath=R.min())
    rows.append(P)
A = pd.concat(rows)
D["Q3 picks: mean quarterly excess over XBI by volatility third (low, mid, high)"] = [round(float(A[A.pick & (A.vrank <= 1/3)].ex.mean()), 4), round(float(A[A.pick & (A.vrank > 1/3) & (A.vrank <= 2/3)].ex.mean()), 4), round(float(A[A.pick & (A.vrank > 2/3)].ex.mean()), 4)]
D["Q3 pool: same, all pool names"] = [round(float(A[(A.vrank <= 1/3)].ex.mean()), 4), round(float(A[(A.vrank > 1/3) & (A.vrank <= 2/3)].ex.mean()), 4), round(float(A[(A.vrank > 2/3)].ex.mean()), 4)]
A["sizebin"] = pd.cut(A.mcap, [0, 1e9, 5e9, 10e9, 1e12], labels=["<1B", "1-5B", "5-10B", ">10B"])
D["Q39 picks: share of picks and mean excess by size"] = {str(k): [int(len(g)), round(float(g.ex.mean()), 4)] for k, g in A[A.pick].groupby("sizebin", observed=True)}
D["Q40 picks: mean excess by stage multiplier"] = {str(k): [int(len(g)), round(float(g.ex.mean()), 4)] for k, g in A[A.pick].groupby("st")}
D["Q7 pool: mean excess, 2+ funds cut vs fewer"] = [round(float(A[A.cut >= 2].ex.mean()), 4), int((A.cut >= 2).sum()), round(float(A[A.cut < 2].ex.mean()), 4)]
lastq = Q[-1]; w = select(lastq["P"], {}); Rq = lastq["R"]
so = Rq[Rq.index <= "2026-10-30"].iloc[-1] / Rq[Rq.index <= "2026-08-31"].iloc[-1] - 1
contrib = (so[w.index] * w).sort_values()
D["Q2 Sep-Oct 2026: basket loss, worst 5 names' share of it"] = [round(float(contrib.sum()), 4), round(float(contrib.head(5).sum() / contrib.sum()), 2), {t: round(float(so[t]), 3) for t in contrib.head(5).index}]
dl = A[A.pick & A.deal]
D["Q10 deal targets picked; how many fell 20%+ before the premium (with price history)"] = [int(len(dl)), int((dl.minpath <= 0.8).sum())]
chg = [(q["pairs_now"] / q["pairs_prev"] - 1) if q["pairs_prev"] else np.nan for q in Q]
pex = [q["R"].iloc[-1].mean() - 1 - (xbi.at[q["s1"]] / xbi.at[q["s0"]] - 1) for q in Q]
cc = pd.DataFrame({"chg": chg, "pex": pex}).dropna()
D["Q33 corr(change in specialist positions, next-quarter pool excess), n"] = [round(float(cc.corr().iloc[0, 1]), 2), len(cc)]
pk = b.cummax(); hit = b[b / pk - 1 <= -0.35]
D["Q44 kill rule 35% below peak first fired (base, full span)"] = hit.index[0] if len(hit) else None
pool_full = pool_idx.loc[b.index] / pool_idx.loc[b.index[0]]
gap = (b / b.iloc[0]) - pool_full
D["Q44 kill rule 10 points behind pool first fired"] = gap[gap <= -0.10].index[0] if (gap <= -0.10).any() else None
two = F[F.index >= "2024-11-15"]; tg = two / two.iloc[0]
D["Q1 base minus XBI: at Aug 31, 2026 and at Nov 13, 2026 (two-year window)"] = [round(float(tg.loc[tg.index <= "2026-08-31", "Base system"].iloc[-1] - tg.loc[tg.index <= "2026-08-31", "XBI"].iloc[-1]), 4), round(float(tg["Base system"].iloc[-1] - tg["XBI"].iloc[-1]), 4)]
json.dump({"verdict": verdict, "package": out, "diagnostics": D}, open("out_loss_lab2.json", "w"), indent=1, default=str)
print(json.dumps(D, indent=1, default=str))
