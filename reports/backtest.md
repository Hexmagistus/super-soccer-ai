# SUPER SOCCER AI - walk-forward backtest

Model ssa-0.2.0. v0.2 combination (all chosen on the validation season, n=3205): {'alpha': 0.6, 'w_core': 0.7659961188039859, 'w_logit': 0.23400388119601412, 'T': 0.9032678956981768, 'd': 0.10611251112664781, 'val_log_loss': 1.0035420970671318, 'n_val': 3205, 'market': {'w_model': -0.2625802117515806, 'w_market': 1.3821709644432099, 'val_log_loss': 0.9673824455491911, 'n_val': 2304, 'val_market_only_log_loss': 0.9696827142157589, 'odds': 'average pre-closing odds (football-data Avg/BbAv columns), NOT closing'}}

v0.1 ensemble weights (kept as the 'before' baseline): {'poisson': 0.0, 'dc': 0.7, 'elo': 0.0, 'logit': 0.3}

Test matches: 7668. 95% bootstrap CIs in brackets.

| Model | n | Accuracy | Log loss | Brier | RPS |
|---|---|---|---|---|---|
| Ensemble v0.2 | 7668 | 0.5027 [0.4922, 0.5143] | 1.0124 [1.0037, 1.0215] | 0.6060 [0.5992, 0.6124] | 0.2079 [0.2051, 0.2107] |
| Ensemble v0.1 (before) | 7668 | 0.5007 [0.4902, 0.5108] | 1.0139 [1.0051, 1.0240] | 0.6070 [0.6006, 0.6134] | 0.2084 [0.2056, 0.2110] |
| Poisson | 7668 | 0.4993 [0.4879, 0.5098] | 1.0162 [1.0069, 1.0254] | 0.6087 [0.6021, 0.6148] | 0.2092 [0.2066, 0.2119] |
| Dixon-Coles | 7668 | 0.4993 [0.4886, 0.5104] | 1.0164 [1.0068, 1.0260] | 0.6087 [0.6023, 0.6150] | 0.2092 [0.2067, 0.2118] |
| Elo | 7668 | 0.4979 [0.4867, 0.5097] | 1.0166 [1.0072, 1.0258] | 0.6089 [0.6028, 0.6154] | 0.2092 [0.2065, 0.2119] |
| Logistic | 7668 | 0.4947 [0.4838, 0.5057] | 1.0235 [1.0133, 1.0335] | 0.6127 [0.6054, 0.6197] | 0.2104 [0.2074, 0.2134] |
| Base rates | 7668 | 0.4427 [0.4322, 0.4533] | 1.0715 [1.0661, 1.0774] | 0.6479 [0.6439, 0.6520] | 0.2282 [0.2263, 0.2301] |
| Bookmaker closing (subset) | 5714 | 0.5194 [0.5065, 0.5326] | 0.9887 [0.9771, 0.9995] | 0.5904 [0.5824, 0.5981] | 0.2012 [0.1981, 0.2041] |
| Ensemble v0.2 (same subset) | 5714 | 0.5070 [0.4940, 0.5196] | 1.0078 [0.9970, 1.0198] | 0.6028 [0.5953, 0.6103] | 0.2069 [0.2036, 0.2103] |
| Ensemble v0.1 (same subset) | 5714 | 0.5040 [0.4905, 0.5168] | 1.0094 [0.9990, 1.0200] | 0.6039 [0.5965, 0.6116] | 0.2074 [0.2045, 0.2104] |
| Model + market (pre-closing avg odds) | 3951 | 0.5201 [0.5042, 0.5348] | 0.9809 [0.9651, 0.9964] | 0.5854 [0.5751, 0.5959] | 0.1985 [0.1945, 0.2025] |
| Bookmaker pre-closing avg (market subset) | 3951 | 0.5227 [0.5067, 0.5381] | 0.9814 [0.9672, 0.9950] | 0.5853 [0.5763, 0.5955] | 0.1986 [0.1947, 0.2026] |
| Bookmaker closing (market subset) | 3951 | 0.5270 [0.5113, 0.5416] | 0.9797 [0.9670, 0.9932] | 0.5842 [0.5746, 0.5938] | 0.1981 [0.1942, 0.2021] |
| Home always | 7668 | 0.4427 [0.4313, 0.4545] | - | - | - |

v0.2 minus v0.1 (paired bootstrap 95% CI): {'log_loss': -0.0015, 'log_loss_ci': [-0.0027, -0.0004], 'rps': -0.00051, 'rps_ci': [-0.00082, -0.00023]}
v0.1 minus bookmaker closing log loss: {'mean': 0.0207, 'ci': [0.0161, 0.0253]}
v0.2 minus bookmaker closing RPS: {'mean': 0.00567, 'ci': [0.00439, 0.00705]}
Model+market minus closing log loss: {'mean': 0.0011, 'ci': [-0.0019, 0.004]}; minus pre-closing: {'mean': -0.0005, 'ci': [-0.0025, 0.0016]}
Ensemble minus bookmaker log loss: {'mean': 0.0191, 'ci': [0.0148, 0.0235]}
Ensemble minus base-rate log loss: {'mean': -0.0591, 'ci': [-0.0665, -0.0518]}
Exact-score hit rate (top score): {'rate': 0.1236, 'ci': [0.1162, 0.1305], 'mean_top_score_prob': 0.1307}
Total goals MAE: {'model': 1.3048, 'ci': [1.2828, 1.3246], 'baseline_train_mean': 1.3125}
ECE: 0.0069

## Calibration (all outcomes pooled)

| bin | n | mean predicted | observed |
|---|---|---|---|
| 0.0-0.1 | 418 | 0.0733 | 0.0742 |
| 0.1-0.2 | 2632 | 0.16 | 0.171 |
| 0.2-0.3 | 9072 | 0.2582 | 0.258 |
| 0.3-0.4 | 4703 | 0.3402 | 0.3289 |
| 0.4-0.5 | 2923 | 0.4473 | 0.4595 |
| 0.5-0.6 | 1837 | 0.5464 | 0.534 |
| 0.6-0.7 | 997 | 0.6423 | 0.655 |
| 0.7-0.8 | 337 | 0.7441 | 0.7418 |
| 0.8-0.9 | 81 | 0.8409 | 0.8642 |
| 0.9-1.0 | 4 | 0.9108 | 0.5 |

## By league

| League | n | v0.2 log loss | v0.1 log loss | v0.2-v0.1 [95% CI] | v0.2 RPS | v0.1 RPS | Base LL | Book closing LL (subset) | v0.2-book [95% CI] | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| BRA | 1069 | 1.0109 [0.9889, 1.0344] | 1.0122 | -0.0013 [-0.0038, 0.0013] | 0.2048 | 0.205 | 1.0514 | 0.9804 | 0.0274 [0.0142, 0.0423] | 0.0095 |
| D1 | 666 | 0.9927 [0.9571, 1.0264] | 0.9951 | -0.0025 [-0.0068, 0.0021] | 0.2027 | 0.2038 | 1.0787 | 0.968 | 0.0279 [0.0127, 0.043] | 0.018 |
| E0 | 830 | 1.0019 [0.9705, 1.0299] | 1.0055 | -0.0036 [-0.0075, 0.0006] | 0.2042 | 0.2049 | 1.0841 | 0.9773 | 0.012 [-0.0003, 0.0244] | 0.0102 |
| E1 | 1236 | 1.0504 [1.0308, 1.0689] | 1.0542 | -0.0038 [-0.0068, -0.001] | 0.2167 | 0.2178 | 1.079 | 1.0376 | 0.0111 [0.0017, 0.021] | 0.0183 |
| F1 | 675 | 0.9817 [0.9474, 1.0131] | 0.9836 | -0.0019 [-0.0061, 0.0024] | 0.2052 | 0.206 | 1.0593 | 0.9588 | 0.0175 [0.0025, 0.0325] | 0.0225 |
| I1 | 830 | 0.9750 [0.9466, 1.0053] | 0.9779 | -0.0028 [-0.0063, 0.0007] | 0.195 | 0.1959 | 1.0874 | 0.9605 | 0.0123 [-0.0, 0.0236] | 0.022 |
| SP1 | 849 | 0.9692 [0.9378, 0.9987] | 0.972 | -0.0028 [-0.0065, 0.0015] | 0.1954 | 0.1962 | 1.0618 | 0.9428 | 0.0177 [0.008, 0.0278] | 0.0115 |
| USA | 1513 | 1.0554 [1.0354, 1.0742] | 1.0521 | 0.0033 [0.001, 0.0058] | 0.2225 | 0.2218 | 1.0717 | 1.0281 | 0.0268 [0.015, 0.0392] | 0.0184 |
| PSL | 690 | 1.0141 [0.9883, 1.0404] | - | - | 0.2029 | - | 1.0823 | n/a | - | 0.0096 |

## By league and season

| League season | n | Ens LL | Base LL | Book LL | Ens RPS | Book RPS |
|---|---|---|---|---|---|---|
| BRA 2024 | 380 | 1.0301 | 1.0574 | 0.9854 | 0.2116 | 0.1969 |
| BRA 2025 | 380 | 0.9901 | 1.0403 | 0.9748 | 0.2 | 0.1965 |
| BRA 2026 | 309 | 1.013 | 1.0578 | n/a | 0.2024 | n/a |
| D1 2024-25 | 306 | 1.0158 | 1.0929 | 0.9882 | 0.209 | 0.2019 |
| D1 2025-26 | 306 | 0.9672 | 1.0712 | 0.9205 | 0.1943 | 0.1857 |
| D1 2026-27 | 54 | 1.0058 | 1.0412 | 0.9845 | 0.2149 | 0.2115 |
| E0 2024-25 | 380 | 0.9842 | 1.0826 | 0.9664 | 0.2021 | 0.1961 |
| E0 2025-26 | 380 | 1.0186 | 1.0841 | 0.9875 | 0.2067 | 0.1994 |
| E0 2026-27 | 70 | 1.0074 | 1.0931 | 1.0055 | 0.2012 | 0.1982 |
| E1 2024-25 | 552 | 1.0248 | 1.0714 | 1.0274 | 0.2067 | 0.2076 |
| E1 2025-26 | 552 | 1.065 | 1.0831 | 1.0502 | 0.2234 | 0.2198 |
| E1 2026-27 | 132 | 1.0963 | 1.0935 | 1.0545 | 0.2304 | 0.2158 |
| F1 2024-25 | 306 | 0.9757 | 1.0513 | 0.955 | 0.2075 | 0.2009 |
| F1 2025-26 | 306 | 0.9884 | 1.0655 | 0.9592 | 0.204 | 0.2018 |
| F1 2026-27 | 63 | 0.9778 | 1.0683 | 0.9757 | 0.1998 | 0.1998 |
| I1 2024-25 | 380 | 0.9631 | 1.0906 | 0.9513 | 0.1885 | 0.1841 |
| I1 2025-26 | 380 | 0.9964 | 1.0899 | 0.9907 | 0.2015 | 0.1933 |
| I1 2026-27 | 70 | 0.9239 | 1.0567 | 0.9246 | 0.1952 | 0.199 |
| SP1 2024-25 | 380 | 0.9735 | 1.0713 | 0.9463 | 0.1953 | 0.1875 |
| SP1 2025-26 | 380 | 0.9738 | 1.0488 | 0.9484 | 0.1989 | 0.1867 |
| SP1 2026-27 | 89 | 0.9314 | 1.0773 | 0.9164 | 0.1803 | 0.1758 |
| USA 2024 | 522 | 1.064 | 1.0731 | 1.0296 | 0.2263 | 0.2165 |
| USA 2025 | 540 | 1.044 | 1.0742 | 1.0267 | 0.2194 | 0.2152 |
| USA 2026 | 451 | 1.0592 | 1.0672 | n/a | 0.2218 | n/a |

## Value rule ROI (test seasons, average pre-closing odds)

v0.2, all leagues: {'n_bets': 1571, 'roi': -0.1239, 'roi_ci95': [-0.1945, -0.0556], 'profit_units': -194.65, 'mean_odds': 3.238, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

v0.1, all leagues: {'n_bets': 1809, 'roi': -0.1474, 'roi_ci95': [-0.2145, -0.0788], 'profit_units': -266.66, 'mean_odds': 3.193, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

Model + market variant, all leagues: {'n_bets': 101, 'roi': 0.1146, 'roi_ci95': [-0.0765, 0.3012], 'profit_units': 11.57, 'mean_odds': 1.882, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

Validated leagues only (['E0', 'I1']): {'n_bets': 567, 'roi': -0.1107, 'roi_ci95': [-0.2295, 0.0239], 'profit_units': -62.78, 'mean_odds': 3.507, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

By league:

- BRA: {'n_bets': 0, 'roi': None, 'roi_ci95': [None, None], 'profit_units': 0.0, 'mean_odds': None, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- D1: {'n_bets': 173, 'roi': -0.302, 'roi_ci95': [-0.4837, -0.1159], 'profit_units': -52.24, 'mean_odds': 3.057, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E0: {'n_bets': 261, 'roi': -0.0412, 'roi_ci95': [-0.2335, 0.1393], 'profit_units': -10.76, 'mean_odds': 3.47, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E1: {'n_bets': 383, 'roi': -0.1585, 'roi_ci95': [-0.308, -0.015], 'profit_units': -60.72, 'mean_odds': 3.206, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- F1: {'n_bets': 230, 'roi': 0.0743, 'roi_ci95': [-0.1179, 0.2773], 'profit_units': 17.08, 'mean_odds': 3.113, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- I1: {'n_bets': 306, 'roi': -0.17, 'roi_ci95': [-0.3186, 0.0081], 'profit_units': -52.02, 'mean_odds': 3.539, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- SP1: {'n_bets': 218, 'roi': -0.1651, 'roi_ci95': [-0.3323, 0.0238], 'profit_units': -35.99, 'mean_odds': 2.87, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- USA: {'n_bets': 0, 'roi': None, 'roi_ci95': [None, None], 'profit_units': 0.0, 'mean_odds': None, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

## South Africa PSL (season-ahead, separate method)

Season-ahead backtest (the source has no dates, so no in-season refits are possible): for each test season,
    fit Poisson and Dixon-Coles on ALL usable earlier seasons (season-level decay: weight 0.5 per season back),
    predict every match of the test season, and compare with base rates of the training seasons and 'always home'.
    Ensemble = fixed 50/50 Poisson/DC (no weight tuning, so no validation season is consumed).
    v0.2: also fits the joint Dixon-Coles with the promoted-team prior ('dcj'); teams new to the PSL get the jointly
    estimated promoted-team strength instead of the league average. 'ens_v2' = 50/50 Poisson/DCJ. It is adopted for
    PSL predictions only if it beats 'ens' on the FIRST test season (used as validation, reported as 'v2_gate').

Test matches: 690 (seasons ['2023-24', '2024-25', '2025-26']); data seasons used: ['2022-23', '2023-24', '2024-25', '2025-26', '2026-27']

- ens: log loss 1.0141 [0.9883, 1.0404], RPS 0.2029 [0.1952, 0.2112], Brier 0.6089 [0.5900, 0.6268], accuracy 0.4797 [0.4449, 0.5174]
- ens_v2: log loss 1.0125 [0.9841, 1.0370], RPS 0.2025 [0.1941, 0.2106], Brier 0.6081 [0.5878, 0.6268], accuracy 0.4638 [0.4261, 0.5014]
- poisson: log loss 1.0136 [0.9861, 1.0416], RPS 0.2029 [0.1947, 0.2116], Brier 0.6086 [0.5889, 0.6282], accuracy 0.4754 [0.4391, 0.5130]
- dc: log loss 1.0148 [0.9872, 1.0407], RPS 0.2030 [0.1950, 0.2112], Brier 0.6094 [0.5902, 0.6284], accuracy 0.4696 [0.4304, 0.5116]
- dcj: log loss 1.0133 [0.9860, 1.0404], RPS 0.2026 [0.1937, 0.2116], Brier 0.6089 [0.5896, 0.6277], accuracy 0.4594 [0.4246, 0.4957]
- base: log loss 1.0823 [1.0673, 1.0955], RPS 0.2248 [0.2186, 0.2310], Brier 0.6553 [0.6461, 0.6638], accuracy 0.4232 [0.3855, 0.4566]
- always home: accuracy 0.4232 [0.3826, 0.4623]
- ensemble minus base log loss: {'mean': -0.0682, 'ci': [-0.0905, -0.0456]}; ECE 0.0096
- v2 (Poisson/DCJ) minus v1: {'mean': -0.0016, 'ci': [-0.0046, 0.0013]}; gate: {'season': '2023-24', 'ens_v2_log_loss': 1.0272, 'ens_log_loss': 1.0273, 'adopted': True}
- missing: No odds (no bookmaker benchmark, no value backtest), no shots, no dates (no Elo/form/logit models).

Past performance does not guarantee future results. No betting outcome is guaranteed.