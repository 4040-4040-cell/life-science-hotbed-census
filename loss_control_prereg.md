# Loss control: 50 questions and pre-registered rules

Written and committed Nov 15, 2026 before any loss-control rule was run. The pass marks below are fixed; results are judged against them as written.

## Windows

Tuning window: Nov 15, 2024 to Nov 13, 2026 (eight quarters, the two-year backtest). Rules are chosen here.
Holdout: Aug 15, 2023 to Nov 15, 2024 (five quarters, 13F filings from Aug 2023). Nothing is chosen here; it only confirms or rejects.
Known holdout gap: deal targets announced before Jan 2024 whose price history vanished (Karuna, Cerevel, RayzeBio, ImmunoGen, Mirati and others) are missing. This understates the system and pool against XBI in the holdout but affects every rule variant alike, so rule-against-base comparisons stand.

## Assumptions (mine, not sourced)

Cash earns 4.0% a year. Stops and overlay switches cost 0.5% of the amount moved (falling small caps trade wide). Quarterly rebalance costs 0.2% round trip, as before. Signals are read at a close and acted on at the next close.

## Pass marks

A rule passes the tuning window if either (a) max drawdown improves by at least 3 points and total return falls by no more than 3 points, or (b) total return divided by the absolute max drawdown improves by at least 20%.
A passing rule is confirmed if, in the holdout, its max drawdown is no worse than the base system's and its return per unit of drawdown is no worse.
Only one setting per rule may be carried forward: the better of the two pre-set settings in the tuning window.
The package (all confirmed rules together) goes to shadow on the paper portfolio if it beats XBI on return per unit of drawdown in both windows. It replaces the live rules only after two live quarters in shadow ahead of both the live rules and XBI.
If no rule is confirmed, the takeover sleeve's job is reduced to a satellite next to XBI and the next step is the data in the D list.

## Rules tested (two pre-set settings each)

R1 Name stop: sell a name down 20% / 30% from entry; proceeds to XBI until the next rebalance.
R2 Relative stop: sell a name that trails XBI by 20 / 30 points since entry; proceeds to XBI.
R3 Drawdown brake: when the portfolio is 15% / 20% below its peak, move half to cash until the next rebalance.
R4 Relative-strength switch: when the specialist pool basket trails XBI by 5 / 8 points over the last 21 trading days, hold XBI; return when the 21-day gap is back above zero.
R5 Trend filter: when XBI closes below its 100 / 200-day average, hold half in cash; return when it closes above.
R6 Volatility screen: drop the most volatile quarter / third of candidates (63-day volatility at decision) before ranking.
R7 Inverse-volatility weights instead of equal weights.
R8 Holder-exit screen: drop names where 2 / 3 or more specialist funds cut by 20%+ or exited in the latest 13F.
R9 VIX filter: half to cash when VIX closes above 25 / 30; return when it closes below 20 / 25.
R10 Core and satellite: 50% XBI, 50% system / 70% XBI, 30% system.
R11 Monthly rebalance using the same 13F set (drops losers sooner).
R12 Top 20 instead of top quarter (more names, less single-name risk) / top 10.

## The 50 questions

T = tested in this run. D = needs data we do not have point in time (source named). P = policy decision, answered in the register.

Where the losses came from
1. What share of the two-year shortfall to XBI came from September and October 2026? T
2. Were the losses in a few names or spread across the basket? T
3. Did the losers share a trait at purchase: small size, high volatility, early stage? T (cash runway is D)
4. How much of the loss is market beta and how much is stock-specific? T
5. Did the pool start falling against XBI before the deep drawdowns, so relative weakness is an early warning? T (R4)
6. Do losses cluster in particular months, such as September? T
7. Did names that specialists cut in the prior 13F fall further? T (R8)
8. Did failed trials and FDA rejections cause the largest single-day losses? D (catalyst calendar history, ClinicalTrials.gov and 8-K)
9. How much loss came from accelerated-approval withdrawals or label changes? D (FDA withdrawal list joined to holdings)
10. Did any deal target fall 20% or more before its announcement, so a stop would have sold it before the premium? T

Name-level protection
11. Should a name be sold after a 20% or 30% drop from entry? T (R1)
12. Is a stop relative to XBI better than an absolute stop? T (R2)
13. After a stop, should the money wait in XBI, cash, or the next-ranked name? T for XBI; P for the others
14. Should the most volatile candidates be excluded? T (R6)
15. Should weights be inverse to volatility instead of equal? T (R7)
16. Should any single name be capped? P (equal weight already caps each at 1/N)
17. Should names with under 18 months of cash be excluded? D (point-in-time cash from XBRL company facts)
18. Should names with a Phase 3 readout inside the holding quarter be excluded or sized down? D (primary completion date history)
19. Should names that 2 or 3 specialists cut or exited be excluded? T (R8)
20. Should names with high short interest be excluded? D (FINRA short interest history)
21. Should names with net insider selling be excluded? D (Form 4 history beyond 39 names)
22. Is a minimum daily trading value needed so stops can be executed? P

Portfolio-level protection
23. Should exposure drop when the portfolio is 15% or 20% below its peak? T (R3)
24. Should we hold XBI when the specialist pool lags XBI over a month? T (R4)
25. Should we hold half in cash when XBI is below its 100 or 200-day average? T (R5)
26. Should we cut exposure when VIX is high? T (R9)
27. When we step aside, is cash or XBI the better place to wait? T (R3 cash, R4 XBI)
28. Should the takeover sleeve be only half or 30% of the portfolio? T (R10)
29. Would XBI put spreads pay for themselves? D (options price history)
30. Would shorting the lowest-scored pool names offset losses? D (borrow cost history); the pool hedge already failed
31. Should we rebalance monthly to drop losers sooner? T (R11)
32. Does buying in thirds over three weeks reduce timing risk? P, next run
33. Does a fall in total specialist holdings across the pool predict the next quarter? T
34. Can 13G/A and 13D/A amendments show fund selling before the 13F? D (EDGAR amendment history)
35. Do XBI share redemptions show forced selling early? D (ETF shares outstanding history)
36. Do rate moves or credit spreads lead the drawdowns? D (FRED)
37. Does a heavy follow-on and IPO calendar lead the drawdowns? D (offering history)
38. Is September seasonally weak for this pool? T

Model design
39. Did the size multiplier tilt toward the most volatile small caps? T
40. Did the stage weight concentrate in names that fall more in selloffs? T
41. Is top 10 or top 20 safer than the top quarter? T (R12)
42. Is the basket concentrated in one therapeutic area? D (point-in-time area tags)
43. How much does realistic stop slippage erase the benefit? T (0.5% assumed on every stop and switch)

Governance
44. Would the current kill rule (35% below peak) have fired in the backtest, and when? T
45. Who may override a stop, and how is it logged? P (no overrides in paper; any override logged with reason)
46. How do we avoid fitting rules to two years? P (this file, the holdout, two settings per rule)
47. What result would make us drop the takeover sleeve? P (package fails to beat XBI on return per unit of drawdown in both windows)
48. Do stacked rules just leave us in XBI or cash most of the time? T (time out of the market reported)
49. What does each rule cost in a rising market? T (2025 returns reported)
50. Do the rules hold live before real money? P (two quarters in shadow)
