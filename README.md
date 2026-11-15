# Takeover paper portfolio

Pretend-money test of the biotech takeover score, started Nov 15, 2026 with $5,000. A scheduled task runs every day at 3:52pm Pacific: it clones this branch, checks holdings for deal filings and 25% moves, fills queued orders at the latest close, commits ledger.json and nav_history.csv back here, and sends one email.

Rules, frozen Nov 15, 2026 (also in ledger.json "rules"): equal weight across the 34 top-quarter names of the Nov 8, 2026 scores; fractional shares; each order fills at the first market close after the day it is queued, plus 10 bps slippage; no commission; a holding is sold once a definitive merger agreement or tender offer is confirmed by a primary source; cash is held until the quarterly rebalance; ERAS, NBIX and BOLD are never bought. Benchmarks bought at the same first close: XBI, the 128-name pool basket and the 87-name five-holder basket. Kill rule: stop and review if the portfolio trails the pool basket by 10 points or falls 35% from its peak.

Files: engine.py (the engine), ledger.json (state, orders, trades), nav_history.csv (one row per close), challengers.md (pre-registered challenger rules), backtest_6m.py and out_backtest_6m.* (the May 18 to Nov 13, 2026 backtest).

Not automated yet: the quarterly rescore (13F rebuild) runs in a working session and is logged in ledger.json "rebalances".
