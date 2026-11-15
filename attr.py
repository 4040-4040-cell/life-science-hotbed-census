src = open("/home/claude/lsbook/loss_lab.py").read()
exec(src[:src.index("VARIANTS = {")])
q = [q for q in Q if q["d0"] == "2025-08-15"][0]; P, R = q["P"], q["R"]
wq = select(P, {})
days = q["days"]
for m0 in ["2025-09-01", "2025-10-01", "2025-11-01"]:
    d = min(x for x in days if x >= m0)
    wm = select(P, {}, rel=R.loc[d])
    add, drop = sorted(set(wm.index) - set(wq.index)), sorted(set(wq.index) - set(wm.index))
    end = days[-1] if m0 == "2025-11-01" else max(x for x in days if x < (m0[:5] + f"{int(m0[5:7])+1:02d}-01"))
    r = R.loc[end] / R.loc[d] - 1
    print(m0, "added", {t: round(float(r[t]), 3) for t in add}, "dropped", {t: round(float(r[t]), 3) for t in drop})
    print("   mean added", round(float(r[add].mean()), 3) if add else None, "mean dropped", round(float(r[drop].mean()), 3) if drop else None, "deal flags added", [t for t in add if P.loc[t, "deal"]])
# across all quarters: names added by monthly rescoring and their return until next month-start, deal share
rows = []
for q in Q:
    P, R, days = q["P"], q["R"], q["days"]; wq = select(P, {})
    ms = [d for i, d in enumerate(days) if i > 0 and d[:7] != days[i - 1][:7]]
    pts = ms + [days[-1]]
    for a, b in zip(ms, pts[1:]):
        wm = select(P, {}, rel=R.loc[a]); r = R.loc[b] / R.loc[a] - 1
        for t in set(wm.index) - set(wq.index): rows.append((q["d0"], a, t, "add", float(r[t]), bool(P.loc[t, "deal"])))
        for t in set(wq.index) - set(wm.index): rows.append((q["d0"], a, t, "drop", float(r[t]), bool(P.loc[t, "deal"])))
A = pd.DataFrame(rows, columns=["q", "month", "t", "kind", "r", "deal"])
print(A.groupby("kind").r.agg(["count", "mean", "median"]))
print("adds that were deal targets:", A[(A.kind == "add") & A.deal][["month", "t", "r"]].to_string())
ad = A[(A.kind == "add") & ~A.deal]
print("adds excluding deal targets: n", len(ad), "mean", round(ad.r.mean(), 4), "median", round(ad.r.median(), 4))
dr = A[(A.kind == "drop")]
print("dropped names: deals among drops", dr.deal.sum(), "mean ex deals", round(dr[~dr.deal].r.mean(), 4))
