# SUPER SOCCER AI - walk-forward backtest

Model ssa-0.2.0. v0.2 combination (all chosen on the validation season, n=3205): {'alpha': 0.6, 'w_core': 0.7659961188039859, 'w_logit': 0.23400388119601412, 'T': 0.9032678956981768, 'd': 0.10611251112664781, 'val_log_loss': 1.0035420968935516, 'n_val': 3205, 'market': {'w_model': -0.2625802117515806, 'w_market': 1.3821709644432099, 'val_log_loss': 0.9673824456130709, 'n_val': 2304, 'val_market_only_log_loss': 0.9696827142157589, 'odds': 'average pre-closing odds (football-data Avg/BbAv columns), NOT closing'}}

v0.1 ensemble weights (kept as the 'before' baseline): {'poisson': 0.0, 'dc': 0.7, 'elo': 0.0, 'logit': 0.3}

Test matches: 7580. 95% bootstrap CIs in brackets.

| Model | n | Accuracy | Log loss | Brier | RPS |
|---|---|---|---|---|---|
| Ensemble v0.2 | 7580 | 0.5020 [0.4912, 0.5133] | 1.0127 [1.0030, 1.0215] | 0.6062 [0.5997, 0.6127] | 0.2079 [0.2049, 0.2108] |
| Ensemble v0.1 (before) | 7580 | 0.5000 [0.4897, 0.5108] | 1.0142 [1.0048, 1.0233] | 0.6072 [0.6003, 0.6143] | 0.2084 [0.2058, 0.2113] |
| Poisson | 7580 | 0.4988 [0.4871, 0.5106] | 1.0166 [1.0071, 1.0256] | 0.6089 [0.6023, 0.6153] | 0.2092 [0.2066, 0.2120] |
| Dixon-Coles | 7580 | 0.4988 [0.4876, 0.5107] | 1.0167 [1.0072, 1.0259] | 0.6089 [0.6024, 0.6156] | 0.2092 [0.2066, 0.2120] |
| Elo | 7580 | 0.4979 [0.4867, 0.5087] | 1.0167 [1.0078, 1.0258] | 0.6089 [0.6023, 0.6156] | 0.2092 [0.2068, 0.2117] |
| Logistic | 7580 | 0.4943 [0.4831, 0.5054] | 1.0235 [1.0140, 1.0335] | 0.6126 [0.6053, 0.6191] | 0.2103 [0.2073, 0.2130] |
| Base rates | 7580 | 0.4434 [0.4317, 0.4546] | 1.0713 [1.0654, 1.0769] | 0.6477 [0.6437, 0.6516] | 0.2281 [0.2261, 0.2301] |
| Bookmaker closing (subset) | 5652 | 0.5180 [0.5060, 0.5303] | 0.9892 [0.9778, 1.0001] | 0.5908 [0.5831, 0.5982] | 0.2012 [0.1983, 0.2044] |
| Ensemble v0.2 (same subset) | 5652 | 0.5060 [0.4926, 0.5189] | 1.0081 [0.9981, 1.0186] | 0.6031 [0.5953, 0.6110] | 0.2068 [0.2037, 0.2101] |
| Ensemble v0.1 (same subset) | 5652 | 0.5032 [0.4915, 0.5166] | 1.0097 [0.9988, 1.0202] | 0.6041 [0.5971, 0.6120] | 0.2074 [0.2042, 0.2105] |
| Model + market (pre-closing avg odds) | 3889 | 0.5186 [0.5027, 0.5346] | 0.9815 [0.9661, 0.9968] | 0.5858 [0.5749, 0.5972] | 0.1985 [0.1947, 0.2028] |
| Bookmaker pre-closing avg (market subset) | 3889 | 0.5210 [0.5055, 0.5366] | 0.9819 [0.9684, 0.9949] | 0.5857 [0.5763, 0.5954] | 0.1986 [0.1949, 0.2026] |
| Bookmaker closing (market subset) | 3889 | 0.5251 [0.5099, 0.5402] | 0.9803 [0.9685, 0.9932] | 0.5846 [0.5761, 0.5942] | 0.1981 [0.1941, 0.2021] |
| Home always | 7580 | 0.4434 [0.4334, 0.4545] | - | - | - |

v0.2 minus v0.1 (paired bootstrap 95% CI): {'log_loss': -0.0015, 'log_loss_ci': [-0.0026, -0.0003], 'rps': -0.00049, 'rps_ci': [-0.00081, -0.00019]}
v0.1 minus bookmaker closing log loss: {'mean': 0.0205, 'ci': [0.0162, 0.025]}
v0.2 minus bookmaker closing RPS: {'mean': 0.00561, 'ci': [0.00421, 0.00692]}
Model+market minus closing log loss: {'mean': 0.0011, 'ci': [-0.0018, 0.004]}; minus pre-closing: {'mean': -0.0004, 'ci': [-0.0023, 0.0016]}
Ensemble minus bookmaker log loss: {'mean': 0.019, 'ci': [0.0144, 0.0234]}
Ensemble minus base-rate log loss: {'mean': -0.0585, 'ci': [-0.0655, -0.0513]}
Exact-score hit rate (top score): {'rate': 0.1241, 'ci': [0.1165, 0.1318], 'mean_top_score_prob': 0.1307}
Total goals MAE: {'model': 1.3027, 'ci': [1.2821, 1.3247], 'baseline_train_mean': 1.3104}
ECE: 0.0068

## Calibration (all outcomes pooled)

| bin | n | mean predicted | observed |
|---|---|---|---|
| 0.0-0.1 | 415 | 0.0734 | 0.0747 |
| 0.1-0.2 | 2600 | 0.16 | 0.1704 |
| 0.2-0.3 | 8968 | 0.2582 | 0.2586 |
| 0.3-0.4 | 4652 | 0.3402 | 0.3293 |
| 0.4-0.5 | 2889 | 0.4473 | 0.4579 |
| 0.5-0.6 | 1811 | 0.5464 | 0.5334 |
| 0.6-0.7 | 987 | 0.6422 | 0.6565 |
| 0.7-0.8 | 333 | 0.7438 | 0.7387 |
| 0.8-0.9 | 81 | 0.8409 | 0.8642 |
| 0.9-1.0 | 4 | 0.9108 | 0.5 |

## By league

| League | n | v0.2 log loss | v0.1 log loss | v0.2-v0.1 [95% CI] | v0.2 RPS | v0.1 RPS | Base LL | Book closing LL (subset) | v0.2-book [95% CI] | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| BRA | 1059 | 1.0119 [0.9894, 1.0363] | 1.0131 | -0.0012 [-0.0038, 0.0014] | 0.205 | 0.2052 | 1.0509 | 0.9804 | 0.0274 [0.0133, 0.0429] | 0.0106 |
| D1 | 657 | 0.9940 [0.9577, 1.0288] | 0.9964 | -0.0024 [-0.0064, 0.0019] | 0.203 | 0.2041 | 1.0793 | 0.968 | 0.0297 [0.0132, 0.0456] | 0.0181 |
| E0 | 820 | 1.0039 [0.9723, 1.0317] | 1.0075 | -0.0036 [-0.0077, 0.0007] | 0.2044 | 0.2051 | 1.085 | 0.9811 | 0.0105 [-0.0022, 0.0229] | 0.0121 |
| E1 | 1223 | 1.0490 [1.0314, 1.0672] | 1.0528 | -0.0039 [-0.0071, -0.001] | 0.2164 | 0.2174 | 1.0785 | 1.0366 | 0.0103 [0.0003, 0.0206] | 0.0184 |
| F1 | 666 | 0.9832 [0.9501, 1.0162] | 0.9851 | -0.0019 [-0.0057, 0.0023] | 0.2054 | 0.2062 | 1.0593 | 0.9602 | 0.0181 [0.003, 0.0329] | 0.0228 |
| I1 | 820 | 0.9735 [0.9432, 1.0023] | 0.9766 | -0.0031 [-0.0068, 0.0006] | 0.1939 | 0.1948 | 1.0882 | 0.9598 | 0.0109 [-0.0009, 0.0238] | 0.022 |
| SP1 | 838 | 0.9702 [0.9385, 1.0005] | 0.9727 | -0.0026 [-0.0069, 0.0014] | 0.196 | 0.1968 | 1.0611 | 0.9432 | 0.0184 [0.0085, 0.0291] | 0.0114 |
| USA | 1497 | 1.0552 [1.0350, 1.0765] | 1.0516 | 0.0036 [0.0013, 0.006] | 0.2228 | 0.2221 | 1.0706 | 1.0281 | 0.0268 [0.0151, 0.0388] | 0.019 |
| PSL | 690 | 1.0141 [0.9880, 1.0402] | - | - | 0.2029 | - | 1.0823 | n/a | - | 0.0096 |

## By league and season

| League season | n | Ens LL | Base LL | Book LL | Ens RPS | Book RPS |
|---|---|---|---|---|---|---|
| BRA 2024 | 380 | 1.0301 | 1.0574 | 0.9854 | 0.2116 | 0.1969 |
| BRA 2025 | 380 | 0.9901 | 1.0403 | 0.9748 | 0.2 | 0.1965 |
| BRA 2026 | 299 | 1.0166 | 1.0563 | n/a | 0.203 | n/a |
| D1 2024-25 | 306 | 1.0158 | 1.0929 | 0.9882 | 0.209 | 0.2019 |
| D1 2025-26 | 306 | 0.9672 | 1.0712 | 0.9205 | 0.1943 | 0.1857 |
| D1 2026-27 | 45 | 1.0278 | 1.0424 | 0.9881 | 0.2211 | 0.2131 |
| E0 2024-25 | 380 | 0.9842 | 1.0826 | 0.9664 | 0.2021 | 0.1961 |
| E0 2025-26 | 380 | 1.0186 | 1.0841 | 0.9875 | 0.2067 | 0.1994 |
| E0 2026-27 | 60 | 1.0357 | 1.1058 | 1.0522 | 0.2041 | 0.2063 |
| E1 2024-25 | 552 | 1.0248 | 1.0714 | 1.0274 | 0.2067 | 0.2076 |
| E1 2025-26 | 552 | 1.065 | 1.0831 | 1.0502 | 0.2234 | 0.2198 |
| E1 2026-27 | 119 | 1.0869 | 1.0895 | 1.0483 | 0.2281 | 0.2147 |
| F1 2024-25 | 306 | 0.9757 | 1.0513 | 0.955 | 0.2075 | 0.2009 |
| F1 2025-26 | 306 | 0.9884 | 1.0655 | 0.9592 | 0.204 | 0.2018 |
| F1 2026-27 | 54 | 0.9965 | 1.0695 | 0.992 | 0.2008 | 0.2004 |
| I1 2024-25 | 380 | 0.9631 | 1.0906 | 0.9513 | 0.1885 | 0.1841 |
| I1 2025-26 | 380 | 0.9964 | 1.0899 | 0.9907 | 0.2015 | 0.1933 |
| I1 2026-27 | 60 | 0.895 | 1.0625 | 0.9118 | 0.1797 | 0.1887 |
| SP1 2024-25 | 380 | 0.9735 | 1.0713 | 0.9463 | 0.1953 | 0.1875 |
| SP1 2025-26 | 380 | 0.9738 | 1.0488 | 0.9484 | 0.1989 | 0.1867 |
| SP1 2026-27 | 78 | 0.9362 | 1.0714 | 0.9153 | 0.1846 | 0.1784 |
| USA 2024 | 522 | 1.064 | 1.0731 | 1.0296 | 0.2263 | 0.2165 |
| USA 2025 | 540 | 1.044 | 1.0742 | 1.0267 | 0.2194 | 0.2152 |
| USA 2026 | 435 | 1.0587 | 1.063 | n/a | 0.223 | n/a |

## Value rule ROI (test seasons, average pre-closing odds)

v0.2, all leagues: {'n_bets': 1545, 'roi': -0.1255, 'roi_ci95': [-0.1969, -0.0526], 'profit_units': -193.85, 'mean_odds': 3.238, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

v0.1, all leagues: {'n_bets': 1785, 'roi': -0.1503, 'roi_ci95': [-0.2151, -0.0834], 'profit_units': -268.22, 'mean_odds': 3.193, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

Model + market variant, all leagues: {'n_bets': 100, 'roi': 0.1111, 'roi_ci95': [-0.0918, 0.2916], 'profit_units': 11.11, 'mean_odds': 1.886, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

Validated leagues only (['E0', 'I1']): {'n_bets': 554, 'roi': -0.1, 'roi_ci95': [-0.2193, 0.0221], 'profit_units': -55.39, 'mean_odds': 3.51, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

By league:

- BRA: {'n_bets': 0, 'roi': None, 'roi_ci95': [None, None], 'profit_units': 0.0, 'mean_odds': None, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- D1: {'n_bets': 170, 'roi': -0.3298, 'roi_ci95': [-0.506, -0.1312], 'profit_units': -56.06, 'mean_odds': 3.049, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E0: {'n_bets': 253, 'roi': -0.0249, 'roi_ci95': [-0.2232, 0.1622], 'profit_units': -6.31, 'mean_odds': 3.455, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E1: {'n_bets': 381, 'roi': -0.1541, 'roi_ci95': [-0.2863, -0.0123], 'profit_units': -58.72, 'mean_odds': 3.208, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- F1: {'n_bets': 225, 'roi': 0.0654, 'roi_ci95': [-0.1308, 0.2516], 'profit_units': 14.71, 'mean_odds': 3.129, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- I1: {'n_bets': 301, 'roi': -0.1631, 'roi_ci95': [-0.3132, 0.0049], 'profit_units': -49.08, 'mean_odds': 3.556, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- SP1: {'n_bets': 215, 'roi': -0.1786, 'roi_ci95': [-0.3377, -0.0071], 'profit_units': -38.39, 'mean_odds': 2.857, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
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

- ens: log loss 1.0141 [0.9880, 1.0402], RPS 0.2029 [0.1942, 0.2108], Brier 0.6089 [0.5909, 0.6273], accuracy 0.4797 [0.4420, 0.5174]
- ens_v2: log loss 1.0125 [0.9856, 1.0395], RPS 0.2025 [0.1938, 0.2106], Brier 0.6081 [0.5908, 0.6268], accuracy 0.4638 [0.4275, 0.5014]
- poisson: log loss 1.0136 [0.9871, 1.0398], RPS 0.2029 [0.1940, 0.2111], Brier 0.6086 [0.5896, 0.6289], accuracy 0.4754 [0.4362, 0.5131]
- dc: log loss 1.0148 [0.9883, 1.0424], RPS 0.2030 [0.1941, 0.2106], Brier 0.6094 [0.5906, 0.6274], accuracy 0.4696 [0.4319, 0.5043]
- dcj: log loss 1.0133 [0.9852, 1.0390], RPS 0.2026 [0.1945, 0.2117], Brier 0.6089 [0.5898, 0.6276], accuracy 0.4594 [0.4261, 0.4971]
- base: log loss 1.0823 [1.0681, 1.0951], RPS 0.2248 [0.2187, 0.2303], Brier 0.6553 [0.6451, 0.6648], accuracy 0.4232 [0.3841, 0.4623]
- always home: accuracy 0.4232 [0.3884, 0.458]
- ensemble minus base log loss: {'mean': -0.0682, 'ci': [-0.0918, -0.0454]}; ECE 0.0096
- v2 (Poisson/DCJ) minus v1: {'mean': -0.0016, 'ci': [-0.0047, 0.0014]}; gate: {'season': '2023-24', 'ens_v2_log_loss': 1.0272, 'ens_log_loss': 1.0273, 'adopted': True}
- missing: No odds (no bookmaker benchmark, no value backtest), no shots, no dates (no Elo/form/logit models).

Past performance does not guarantee future results. No betting outcome is guaranteed.