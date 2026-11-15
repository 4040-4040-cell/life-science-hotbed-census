# Challenger register: takeover paper portfolio

Written Nov 15, 2026, before any of these was tested. Each challenger is judged on the 2018 to 2023 retest (2021 to 2023 sealed until the final run), then runs one quarter in shadow beside the frozen champion with the same $5,000 and costs. Promotion needs both. One change at a time. Ideas came from the six-month backtest (May 18 to Nov 13, 2026: system +6.0%, pool basket +2.3%, five-holder basket +4.2%, XBI +17.7%), so that window cannot be used to judge them.

C1. Hedge against what we own. Metric: return of the top quarter minus the equal-weight pool basket, and its volatility. Pass: positive spread in the retest with t-stat above 2 on monthly spreads, and the spread's volatility below half the long-only book's.

C2. Flat size factor above $5B (0.9 and 0.55 bands set to 1.0). Metric: AUC of the score for deals within 12 months. Pass: AUC up by 0.02 or more on development years, not lower on sealed years.

C3. Exit before binary readouts (Phase 3 topline or FDA action within 10 trading days). Metric: return and worst drawdown of the book. Pass: drawdown at least 5 points smaller with return no more than 1 point lower a year.

C4. Change in specialist holders (added in the latest quarter) instead of the level. Metric: AUC as in C2. Pass: as in C2.

Pre-registered tests from the 100 questions, to run this week on the 201-company sample: insider buying (Form 4) and short interest (FINRA). Pass for adding either as a factor: improves AUC by 0.02 with p below 0.005 after counting every test run so far.

Added Nov 15, 2026, from the team's week-of-Nov-9 note (Stifel State of Biotech, Nov 13; Convoke pipeline snapshot, Nov 11). Not yet tested.

C5. Stage weights from the current deal mix. Stifel reports approved assets fell from 55% to 30% of 2026 deal value and Phase II targets rose from 14% to 32%; our stage factor (selling 1.5, Phase 3 1.2, Phase 2 1.0) was set on 2024 to 2026 deal counts. Test: re-weight stage on a trailing 24-month deal mix at each rebalance. Metric and pass as in C2.

C6. Target crowding. Companies whose lead program sits on one of the 43 most crowded targets (Convoke) may be less likely to be bought. Test: crowded-target flag as a multiplier. Metric and pass as in C2.

Context, not a rule: Stifel describes hedge-fund degrossing as a mechanical seller in 2026, and sub-$100M companies up 30% YTD against a flat middle. Both bear on why the specialist pool trailed XBI from September; C1 (hedge against the pool) is the test.

Two-year quarterly backtest, Nov 15, 2024 to Nov 13, 2026 (backtest_2y.py, eight periods, 10 bps each way). Exploratory: these quarters overlap the data the factors were set on, so nothing here is a pass.
XBI +62.7%. Pool basket +55.6%. 5+ holders +56.6%. System (holders x size x stage) +54.8%. C2 flat size +63.2%. C4 holder change +42.7%. C1 hedge (system minus pool) -2.2%. XBI + tilt (5+ minus pool) +65.6%. Top 10 by score +85.8% (beat XBI in 5 of 8 quarters, t = 0.57).
Pool against XBI, quarterly: beta 1.41, alpha -2.5% a quarter. Top quarter held 9 of the 25 pool deals (36% against 25% by chance).
Added to shadow on the live paper portfolio Nov 15, 2026: Top 10 and XBI + tilt.
C7. Concentration: top 10 instead of top quarter. Judge on the 2018 to 2023 retest; pass = beats XBI after costs in at least 60% of quarters with t above 2.
C8. Event layer on XBI: buy a pool name only on a hard pre-deal filing (strategic 13D, 8-K 5.02 change-in-control or retention plan), hold 60 trading days. Build the 2019 to 2026 event history from EDGAR first; pass = mean 60-day excess return over XBI above 5% with t above 2.

Loss-control test, Nov 15, 2026 (loss_control_prereg.md committed first as 830f672; results in loss_control_results.md).
C7 top 10: failed the Aug 2023 to Nov 2024 holdout (14.5% against the base system's 26.3%; worst drop -22.7% against -22.2%). Kept in shadow for the 2018 to 2023 retest; the holdout is evidence against it.
C9 loss-control package, in shadow from the first fill: top quarter rescored monthly at current value (R11); hold XBI when the candidate basket trails XBI by 8+ points over 21 trading days, back when the gap is above zero (R4); half cash when XBI is below its 200-day average (R5). Tuning window 85.0% (worst drop -25.0%) against XBI 63.9% (-30.2%); holdout 35.6% (-17.4%) against XBI 15.0% (-21.0%). Without Praxis: 71.6% and 30.5%. R4 never fired in the holdout. Replaces the live rules only after two live quarters ahead of both the live rules and XBI.
Rejected in the holdout: R1 20% stop, R6 volatility screen, R10 70/30 core, R12 top 10. Failed the tuning window: R2, R3, R7, R8, R9.
