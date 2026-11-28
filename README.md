# Takeover paper portfolio

Pretend-money test of the biotech takeover score, started Nov 15, 2026 with $5,000. A scheduled task runs every day at 3:52pm Pacific: it clones this branch, checks holdings for deal filings and 25% moves, fills queued orders at the latest close, commits ledger.json and nav_history.csv back here, and sends one email.

Rules, frozen Nov 15, 2026 (also in ledger.json "rules"): equal weight across the 34 top-quarter names of the Nov 8, 2026 scores; fractional shares; each order fills at the first market close after the day it is queued, plus 10 bps slippage; no commission; a holding is sold once a definitive merger agreement or tender offer is confirmed by a primary source; cash is held until the quarterly rebalance; ERAS, NBIX and BOLD are never bought. Benchmarks bought at the same first close: XBI, the 128-name pool basket and the 87-name five-holder basket. Kill rule: stop and review if the portfolio trails the pool basket by 10 points or falls 35% from its peak.

Files: engine.py (the engine), ledger.json (state, orders, trades), nav_history.csv (one row per close), challengers.md (pre-registered challenger rules), backtest_6m.py and out_backtest_6m.* (the May 18 to Nov 13, 2026 backtest).

## Active rules, from Nov 28, 2026

On the owner's instruction the daily run now manages the book instead of only reporting. After `engine.py run`, `engine.py decide` reads two signals at the close and sets the day's call (HOLD, REBALANCE, DE-RISK or RE-RISK), queues any orders to fill at the next close, and puts the call at the top of the email.

1. Monthly rescore at the first close of each month: top quarter of the specialist-held candidates by holders x size x stage at current value, equal weight.
2. Rotate the stock sleeve into XBI when those candidates trail XBI by 8 points or more over 21 trading days; return when the gap turns positive.
3. Half in cash when XBI closes below its 200-day average.
4. Deal targets sold once a primary source confirms the agreement; cash goes back to work at the next rescore.

These are the loss-control package rules (R4, R5, R11) that ran in shadow from Nov 16. They were promoted before their planned two-quarter trial ended. The Nov 15 frozen book is tracked as a comparison column ("Frozen rules"), and the package's own shadow line from Nov 16 stays in the table. The old rules are kept in ledger.json "rules_v1_frozen_2026_11_15"; every call is logged in ledger.json "live.decisions".

Still manual: rebuilding the candidate pool from new 13F filings (needs the 30-fund research data set). Until it runs, the monthly rescore uses the holder counts from 13F filings filed on or before Aug 14, 2026.

Not automated yet: the quarterly rescore (13F rebuild) runs in a working session and is logged in ledger.json "rebalances".
