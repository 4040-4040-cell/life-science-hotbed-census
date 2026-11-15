# Loss control: results against the pre-registered pass marks

Run Nov 15, 2026 (loss_lab.py, loss_lab2.py). Rules and pass marks were committed first (830f672). Picks use the ticker as a fixed tiebreak so results reproduce exactly; before that fix, tie order moved the base two-year total between 55% and 57%.

## The verdict: one package goes to shadow

Twelve rules were tested with two pre-set settings each. Seven passed the tuning window (Nov 2024 to Nov 2026). Only three survived the holdout (Aug 2023 to Nov 2024): the relative-strength switch, the 200-day trend filter and monthly rescoring. Together they form the package now running in shadow on the paper portfolio.

| | Package | Base system | XBI | IBB | S&P 500 |
|---|---:|---:|---:|---:|---:|
| Holdout total, Aug 2023 to Nov 2024 | 35.6% | 26.3% | 15.0% | 4.2% | 32.3% |
| Holdout worst drop | -17.4% | -22.2% | -21.0% | -13.5% | -9.0% |
| Two-year total, Nov 2024 to Nov 2026 | 85.0% | 55.1% | 63.9% | 59.3% | 28.8% |
| Two-year worst drop | -25.0% | -35.4% | -30.2% | -21.3% | -19.0% |
| $5,000 over the two years | $9,249 | $7,753 | $8,197 | $7,966 | $6,439 |
| Full span total, Aug 2023 to Nov 2026 | 150.4% | 95.5% | 88.6% | 66.0% | 70.3% |
| Full span worst drop | -30.0% | -40.3% | -33.0% | -25.1% | -19.0% |
| Average share in stocks, full span | 75% | 100% | | | |

Calendar years (continuous run from Aug 15, 2023): 2023 from Aug 15: package 19.9%, base 15.9%, XBI 11.9%, IBB 6.1%, S&P 500 7.3%. 2024: 5.3%, 4.9%, 0.9%, -2.7%, 23.3%. 2025: 60.7%, 39.5%, 35.4%, 27.7%, 16.4%. 2026 to Nov 13: 23.5%, 15.3%, 23.5%, 25.9%, 10.6%.

Price returns. Assumptions are mine: cash at 4% a year, 0.5% cost on every switch and stop, 0.2% per quarterly rebalance. With a 1% switch cost the package's two-year total falls from 85.0% to 79.1%.

## What the package does and does not do

It does not stop the first leg of a sell-off. In September 2026 it fell 13.4%, the same as the base system, because the relative-strength signal needs a month of underperformance to fire. It switched to XBI on Sep 29 and lost 1.1% in October against the base system's 7.1%. It also sat in XBI from December 2024 to February 2025, which cut that drawdown.

## Three findings that weaken the result

Praxis. Monthly rescoring added Praxis on Oct 1, 2025, the month it rose 275%. Without Praxis the package still beats XBI (two years 71.6% with a -25.0% worst drop; holdout 30.5%), but monthly rescoring on its own no longer passes the tuning window. It passes the holdout with or without Praxis.

The relative-strength switch never fired in the holdout. Its confirmation there is "did no harm", not evidence. Its evidence is two episodes in the tuning window.

Top 10 failed. It earned 92.1% in the tuning window and 14.5% in the holdout, little more than half the base system's 26.3%, with a deeper worst drop (-22.7%) and less return per unit of drawdown than XBI (0.64 against 0.72). The concentration idea (C7) was fitted to the last two years. It stays a shadow line until the 2018 to 2023 retest, but the holdout is evidence against it.

## Rules: tuning window, then holdout

| Rule (setting carried) | Tuning window | Holdout |
|---|---|---|
| R1 stop 20% from entry | pass (55.6%, -32.4%) | rejected (24.1%, ret/drop below base) |
| R2 stop 20 or 30 points behind XBI | fail | |
| R3 drawdown brake | fail (cuts return 18 to 28 points) | |
| R4 relative-strength switch, 8 points | pass (65.2%, -31.0%) | confirmed, never fired |
| R5 below 200-day average, half cash | pass (57.9%, -30.2%) | confirmed (26.5%, -18.0%) |
| R6 drop most volatile third | pass (90.5%, -30.6%) | rejected (18.6%, -23.5%) |
| R7 inverse-volatility weights | fail | |
| R8 drop names 2 or 3 funds cut | fail | |
| R9 VIX filter | fail | |
| R10 70% XBI, 30% system | pass (60.6%, -31.9%) | rejected (17.8%) |
| R11 monthly rescore | pass (75.0%, -38.5%) | confirmed (39.2%, -22.2%) |
| R12 top 10 | pass (92.1%, -29.8%) | rejected (14.5%, -22.7%) |

Base system for reference: tuning 55.1%, -35.4%; holdout 26.3%, -22.2%.

## Answers to the 50 questions

Where the losses came from
1. All of the two-year shortfall, and more. The system was 16.1 points ahead of XBI on Aug 31, 2026 and 8.9 points behind on Nov 13: a 25-point swing in ten weeks.
2. Spread across the basket. The basket lost 19.8% in September and October 2026; the five worst names (AVBP -50.5%, NKTR -45.5%, ANRO -36.1%, SLDB -35.3%, DYN -34.4%) were 28% of the loss.
3. Not volatility in a clean way. Picks in the calmest third of the pool trailed XBI by 1.7 points a quarter, the most volatile third by 1.5, the middle third beat it by 4.8. That shape is why the volatility screen failed the holdout. Cash runway is still a data gap.
4. Mostly market. Beta to XBI 1.08; XBI explains 81% of the system's daily variance. That is why the rules that work act on the whole book and the single-name rules do not.
5. Yes, twice: the relative-strength switch caught December 2024 and late September 2026.
6. No reliable seasonality (see 38).
7. The opposite. Pool names that 2 or more funds cut beat the rest by 1.5 points a quarter (544 cases). Cuts are often profit-taking on winners. R8 failed.
8. Not tested: needs a catalyst calendar history (D).
9. Not tested: needs the FDA withdrawal list joined to holdings (D).
10. No. Of 11 deal targets picked, none with price history fell 20% before its premium. Stops would not have sold deals; they failed for other reasons.

Name-level protection
11. No. The 20% stop passed the tuning window and failed the holdout.
12. No. Relative stops failed the tuning window.
13. XBI, as tested. Moving to the next-ranked name is untested.
14. No. Passed tuning, failed holdout.
15. No. Failed tuning after the tiebreak fix.
16. Equal weight already caps each name near 3%; no further cap.
17. Open: point-in-time cash from XBRL company facts (files on hand for most names; next build).
18. Open: trial primary-completion history (D).
19. No (see 7).
20. Open: FINRA short interest history (D).
21. Open: Form 4 history beyond 39 names (D).
22. Policy for real money: no name under $5 million average daily trading value.

Portfolio-level protection
23. No. The brake cut drawdowns but cost 18 to 28 points of return in the tuning window; it re-fires after every rebalance in a long decline.
24. Yes, adopted (R4), with the caveat that it never fired in the holdout.
25. Yes at 200 days (R5), confirmed in the holdout; no at 100 days (too many false exits).
26. No. VIX filters cost return and did not reduce drawdowns.
27. Both are used: XBI when the specialist names are lagging the index, cash when the whole sector is in a downtrend.
28. No. 70/30 passed tuning and failed the holdout.
29. Open: options price history (D).
30. Open; the pool hedge already failed (C1).
31. Yes, adopted (R11), with the Praxis caveat.
32. Next run.
33. No. The change in specialist positions had a -0.37 correlation with the next quarter's pool return against XBI over 12 quarters: wrong sign for a selling warning, and 13F data arrives 45 days late.
34 to 37. Open (D): 13G/A amendments, XBI share redemptions, rates and credit spreads, offering calendar.
38. No pattern. Septembers, system against XBI: 2023 -7.9% vs -7.8%; 2024 +0.7% vs -2.4%; 2025 +8.6% vs +11.5%; 2026 -13.5% vs -3.0%.

Model design
39. Every pick in 13 quarters (359 of 359) was a $1 to $5 billion company. The size multiplier makes the top quarter a mid-cap bucket. Mean excess over XBI +0.9 points a quarter.
40. Commercial-stage picks beat XBI by 2.0 points a quarter; late-stage picks by 0.1.
41. No. Top 20 failed the tuning window on drawdown; top 10 passed it and failed the holdout (14.5% against the base system's 26.3%).
42. Open: point-in-time therapeutic-area tags (D).
43. Doubling switch cost to 1% takes the package's two-year total from 85.0% to 79.1%; it still beats XBI.

Governance
44. Yes, and early. The base system breached 35% below peak on Apr 4, 2025, and fell 10 points behind the pool basket on Feb 9, 2024. Either kill rule would have shut it down. The package's worst drop over the full span is 30.0%, inside the 35% rule.
45. No overrides in paper; any future override is logged with a reason.
46. Pre-registration (830f672), a holdout the rules never saw, two settings per rule, one carried forward.
47. If the package trails XBI on return per unit of drawdown over two live quarters, the takeover sleeve becomes a satellite next to XBI.
48. Package average share in stocks: 67% in the tuning window, 87% in the holdout, 75% over the full span.
49. In rising markets it did not cost return: 2025 package 60.7% against base 39.5%. The two overlay rules alone cost 4.9 points in 2024 (0.0% against 4.9%).
50. Two live quarters in shadow before it can replace the live rules.

Files: out_loss_lab.json (all variants), out_loss_lab2.json (verdicts, package, diagnostics), out_loss_sens.json (Praxis test), out_loss_monthly.csv, out_loss_years.csv, out_loss_lab_full_daily.csv.
