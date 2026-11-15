src = open("/home/claude/lsbook/loss_lab.py").read()
exec(src[:src.index("VARIANTS = {")])
exec(src[src.index("def bench("):src.index("res, series = {}, {}")])
import json
out = {}
for drop in ([], ["PRAX"]):
    Q2 = []
    for q in Q:
        q = dict(q); keep = [t for t in q["P"].index if t not in drop]
        q["P"], q["R"] = q["P"].loc[keep], q["R"][keep]; Q2.append(q)
    for w, D in (("tune", TUNE), ("hold", HOLD)):
        qs = [q for q in Q2 if q["d0"] in D]; days = sorted({d for q in qs for d in q["days"]}); xb = bench("XBI", days)
        for k, p in {"Base": {}, "Package": {"rs": 0.08, "trend": 200, "monthly": True}, "R11 monthly only": {"monthly": True}}.items():
            s, x = run(qs, p); out[f"{w} | {k} | {'ex PRAX' if drop else 'all'}"] = metrics(s, xb)
print(pd.DataFrame(out).T[["total", "maxdd", "ret_per_dd", "months_beat_xbi"]].to_string())
json.dump(out, open("/home/claude/lsbook/out_loss_sens.json", "w"), indent=1)
