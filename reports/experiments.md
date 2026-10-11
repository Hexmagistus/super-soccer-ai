# v0.2 model experiments (validation season only)

Harness: `python -m ssa.experiment` (same strict walk-forward as the backtest: weekly refit on matches dated
before the week, 3-year window). Selection used ONLY the validation season (first of the last four seasons of
each league, n = 3,205). Test seasons (n = 7,469) were evaluated once, after every choice below was frozen.

| Candidate (validation log loss, lower is better) | Val LL | Kept? |
|---|---|---|
| v0.1 ensemble (0.7 Dixon-Coles two-stage + 0.3 logistic) | 1.0059 | baseline |
| Dixon-Coles two-stage (v0.1) | 1.0078 | - |
| Joint DC MLE, xi=0.001 (half-life ~693 d) | 1.0083 | no |
| Joint DC MLE, xi=0.0019 (half-life ~365 d) + promoted-team prior | **1.0074** | yes |
| Joint DC MLE, xi=0.0035 (~198 d) | 1.0082 | no |
| Joint DC MLE, xi=0.006 (~116 d) | 1.0125 | no |
| Joint DC, xi=0.0019, NO promoted-team prior | 1.0078 | (prior worth -0.0004) |
| Joint DC lambdas ^0.6 x shots-on-target (xG proxy, xi=0.0035) lambdas ^0.4 | **1.0058** | yes |
| (same blend, alpha = 1 / 0.8 / 0.5 / 0.4 / 0.2 / 0) | 1.0074 / 1.0061 / 1.0060 / 1.0065 / 1.0082 / 1.0109 | - |
| Elo v0.1 (per-league entry at 20th pct) | 1.0155 | - |
| Elo with promoted/relegated inheritance (bottom-3 / top-3 of previous season) | 1.0163 | no (worse) |
| Logistic v0.1 features | 1.0191 | yes (in pool) |
| Logistic + rest days + total shots + inherited Elo | 1.0239 | no (alone); +0.0001 in pool -> not worth it |
| HistGradientBoosting on pre-match features | 1.0576 | no (overfits; weight 0.004 in pool) |
| Linear pool: 0.766 blend + 0.234 logistic | 1.0045 | yes |
| + Elo, + GBM in pool | 1.0045 (weights ~0) | no |
| + temperature T=0.903 and draw shift d=+0.106 (fitted on validation) | **1.0035** | yes |

Not tried (time): bivariate Poisson / negative binomial, Championship data as a prior for EPL promotions
(the promoted-team prior inside the joint DC fit covers the same weakness generically), daily refits.

Model + market variant (separate, clearly labelled): log pool of v0.2 and AVERAGE PRE-CLOSING odds
(football-data Avg columns; closing odds are never used as a feature). Fitted weights: model -0.263,
market 1.382 (i.e. the best use of the model is a slight contrarian correction that sharpens the market).
Validation: 0.9674 vs market-only 0.9697.

Test-set results: see `backtest.md`.
