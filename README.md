# Takeover paper portfolio

Pretend-money test of the biotech takeover score, started Nov 15, 2026 with $5,000. Fully automated: a scheduled task runs every day at 3:47pm Pacific, reads engine.py, ledger.json and nav_history.csv from this project folder, checks holdings for deal filings and big moves, fills any queued orders at the latest close, writes the files back, and emails one report.

Rules, frozen Nov 15, 2026 (also in ledger.json "rules"): equal weight across the 34 top-quarter names of the Nov 8, 2026 scores; fractional shares; each order fills at the first market close after the day it is queued, plus 10 bps slippage; no commission; a holding is sold once a definitive merger agreement or tender offer is confirmed by a primary source; cash is held until the quarterly rebalance; ERAS, NBIX and BOLD are never bought. Benchmarks bought at the same first close: XBI, and an equal-weight basket of all 128 scored names. Kill rule: stop and review if the portfolio trails the pool basket by 10 points or falls 35% from its peak.

Not automated yet: the quarterly rescore (13F rebuild) runs in a working session.
