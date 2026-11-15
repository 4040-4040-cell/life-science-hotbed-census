"""Candidate pool for the shadow package: drug companies held by 3+ specialist funds in the latest 13F set on file,
not yet announced as deal targets, not restricted. Stores holder count, stage multiplier, shares outstanding."""
import json, sys
src = open("/home/claude/lsbook/loss_lab.py").read()
exec(src[:src.index("# ---- quarterly candidate pools")])
asof = "2026-11-15"
h = holdings_at(asof); n = h.groupby("Ticker").cik.nunique()
latest = max(f[-1][0] for f in files.values())
c = {}
for t in sorted(names):
    if n.get(t, 0) < 3 or t in deals.index: continue
    if t not in u.index or pd.isna(u.loc[t, "shares_out"]): continue
    c[t] = {"n": int(n[t]), "st": float(stage_m(t)), "sh": float(u.loc[t, "shares_out"])}
s = json.load(open("/home/claude/pp/ledger.json"))
s["package"] = {"cands": c, "cands_asof": f"13F filings filed on or before {latest}", "rebalance_due": False,
                "rules": "Shadow, not traded. Top quarter of candidates by holders x size x stage, rescored monthly at current value; "
                         "hold XBI instead when the candidate basket trails XBI by 8+ points over 21 trading days (back when the gap is above zero); "
                         "half in cash when XBI closes below its 200-day average; signals act at the next close; switches cost 0.5%, "
                         "rebalances 0.2% of turnover, cash earns 4% a year. Pre-registered in loss_control_prereg.md (830f672).",
                "state": None}
json.dump(s, open("/home/claude/pp/ledger.json", "w"), indent=1)
print(len(c), "candidates;", latest)
