# Smoke test result

- Started: Sun Nov 15 18:41:06 UTC 2026
- add_repo: tool not found via ToolSearch; repo was already in this session's GitHub scope, so proceeded without it
- Clone (paper-portfolio, depth 1): worked (exit 0)
- Gmail send tool (mcp__Gmail__send_message) loadable via ToolSearch: yes (not called)
- Report files created by `engine.py run`: report.html yes (1162 B), report.txt yes (1024 B), report_subject.txt yes (91 B)

## `python3 engine.py flags` (exit 0)

```
{
 "market_date": "2026-11-13",
 "big_moves": [],
 "no_price_today": [],
 "deal_type_filings_last_4_days": []
}
```

## `python3 engine.py run` (exit 0)

```
Takeover paper portfolio, Sun Nov 15, 2026: 34 orders queued, first fills at the next close
The paper portfolio starts with $5,000.00 of pretend money. 34 buy orders are queued at about $147.06 each and fill at the next market close. Benchmarks bought at the same close: $5,000.00 in XBI, and $5,000.00 spread equally across all 128 names in the scored pool, and $5,000.00 across the 87 pool names with 5 or more specialist holders.

Queued: URGN, ZLAB, IMCR, MIRM, CYTK, MDGL, DBVT, VERA, RYTM, ACAD, VOR, GPCR, IRON, RLAY, DYN, VRDN, MLYS, NAMS, CLDX, IDYA, PHVS, DNTH, BCRX, XENE, MBX, TSHA, LBRX, AMLX, TYRA, KRYS, OCUL, AVBP, RAPP, NKTR

Pretend money only; no real orders. Rules: equal weight across the 34 top-quarter names of the Nov 8, 2026 takeover scores; every order fills at the first close after it is queued, plus 10 bps slippage; deal targets sold once an agreement is confirmed, cash held until the quarterly rebalance. Pool basket = all 128 scored names; 5+ holders = the pool names with five or more specialist holders; both equal weight. Prices: Yahoo Finance closes, Nasdaq fallback; unofficial.
```

No email sent; paper-portfolio branch not modified.
