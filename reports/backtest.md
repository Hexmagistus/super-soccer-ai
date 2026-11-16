# SUPER SOCCER AI - walk-forward backtest

Model ssa-0.2.0. v0.2 combination (all chosen on the validation season, n=3205): {'alpha': 0.6, 'w_core': 0.7659961188039859, 'w_logit': 0.23400388119601412, 'T': 0.9032678956981768, 'd': 0.10611251112664781, 'val_log_loss': 1.0035420970671318, 'n_val': 3205, 'market': {'w_model': -0.2625802117515806, 'w_market': 1.3821709644432099, 'val_log_loss': 0.9673824455491911, 'n_val': 2304, 'val_market_only_log_loss': 0.9696827142157589, 'odds': 'average pre-closing odds (football-data Avg/BbAv columns), NOT closing'}}

v0.1 ensemble weights (kept as the 'before' baseline): {'poisson': 0.0, 'dc': 0.7, 'elo': 0.0, 'logit': 0.3}

Test matches: 7961. 95% bootstrap CIs in brackets.

| Model | n | Accuracy | Log loss | Brier | RPS |
|---|---|---|---|---|---|
| Ensemble v0.2 | 7961 | 0.5047 [0.4940, 0.5153] | 1.0105 [1.0012, 1.0195] | 0.6046 [0.5984, 0.6108] | 0.2078 [0.2052, 0.2105] |
| Ensemble v0.1 (before) | 7961 | 0.5023 [0.4900, 0.5125] | 1.0120 [1.0033, 1.0216] | 0.6057 [0.5993, 0.6122] | 0.2083 [0.2058, 0.2110] |
| Poisson | 7961 | 0.5019 [0.4908, 0.5125] | 1.0141 [1.0047, 1.0228] | 0.6072 [0.6007, 0.6133] | 0.2091 [0.2064, 0.2118] |
| Dixon-Coles | 7961 | 0.5019 [0.4899, 0.5138] | 1.0144 [1.0054, 1.0227] | 0.6073 [0.6013, 0.6135] | 0.2091 [0.2064, 0.2118] |
| Elo | 7961 | 0.5001 [0.4899, 0.5106] | 1.0147 [1.0055, 1.0235] | 0.6075 [0.6015, 0.6144] | 0.2092 [0.2066, 0.2117] |
| Logistic | 7961 | 0.4953 [0.4842, 0.5061] | 1.0217 [1.0115, 1.0316] | 0.6115 [0.6049, 0.6186] | 0.2104 [0.2075, 0.2131] |
| Base rates | 7961 | 0.4447 [0.4325, 0.4561] | 1.0704 [1.0646, 1.0757] | 0.6472 [0.6432, 0.6510] | 0.2284 [0.2267, 0.2303] |
| Bookmaker closing (subset) | 5916 | 0.5218 [0.5096, 0.5340] | 0.9868 [0.9769, 0.9972] | 0.5890 [0.5812, 0.5966] | 0.2011 [0.1980, 0.2037] |
| Ensemble v0.2 (same subset) | 5916 | 0.5086 [0.4961, 0.5220] | 1.0062 [0.9961, 1.0165] | 0.6017 [0.5946, 0.6090] | 0.2068 [0.2037, 0.2099] |
| Ensemble v0.1 (same subset) | 5916 | 0.5052 [0.4917, 0.5181] | 1.0078 [0.9979, 1.0177] | 0.6027 [0.5953, 0.6104] | 0.2074 [0.2042, 0.2106] |
| Model + market (pre-closing avg odds) | 4153 | 0.5225 [0.5076, 0.5386] | 0.9784 [0.9645, 0.9936] | 0.5835 [0.5738, 0.5939] | 0.1984 [0.1942, 0.2022] |
| Bookmaker pre-closing avg (market subset) | 4153 | 0.5249 [0.5107, 0.5391] | 0.9793 [0.9668, 0.9927] | 0.5837 [0.5745, 0.5930] | 0.1986 [0.1946, 0.2021] |
| Bookmaker closing (market subset) | 4153 | 0.5300 [0.5138, 0.5449] | 0.9775 [0.9645, 0.9893] | 0.5825 [0.5728, 0.5918] | 0.1981 [0.1942, 0.2020] |
| Home always | 7961 | 0.4447 [0.4335, 0.4561] | - | - | - |

v0.2 minus v0.1 (paired bootstrap 95% CI): {'log_loss': -0.0015, 'log_loss_ci': [-0.0026, -0.0003], 'rps': -0.00053, 'rps_ci': [-0.00082, -0.00023]}
v0.1 minus bookmaker closing log loss: {'mean': 0.0209, 'ci': [0.0167, 0.0253]}
v0.2 minus bookmaker closing RPS: {'mean': 0.00577, 'ci': [0.00432, 0.00716]}
Model+market minus closing log loss: {'mean': 0.0008, 'ci': [-0.0022, 0.004]}; minus pre-closing: {'mean': -0.0009, 'ci': [-0.0028, 0.001]}
Ensemble minus bookmaker log loss: {'mean': 0.0194, 'ci': [0.0149, 0.0237]}
Ensemble minus base-rate log loss: {'mean': -0.0599, 'ci': [-0.0672, -0.0529]}
Exact-score hit rate (top score): {'rate': 0.1226, 'ci': [0.1157, 0.1303], 'mean_top_score_prob': 0.1305}
Total goals MAE: {'model': 1.3064, 'ci': [1.2847, 1.328], 'baseline_train_mean': 1.3148}
ECE: 0.007

## Calibration (all outcomes pooled)

| bin | n | mean predicted | observed |
|---|---|---|---|
| 0.0-0.1 | 429 | 0.0733 | 0.0723 |
| 0.1-0.2 | 2728 | 0.1599 | 0.1701 |
| 0.2-0.3 | 9439 | 0.2581 | 0.2564 |
| 0.3-0.4 | 4879 | 0.3403 | 0.3306 |
| 0.4-0.5 | 3029 | 0.4475 | 0.4599 |
| 0.5-0.6 | 1902 | 0.5462 | 0.5368 |
| 0.6-0.7 | 1038 | 0.6425 | 0.657 |
| 0.7-0.8 | 351 | 0.7436 | 0.7464 |
| 0.8-0.9 | 84 | 0.8405 | 0.869 |
| 0.9-1.0 | 4 | 0.9108 | 0.5 |

## By league

| League | n | v0.2 log loss | v0.1 log loss | v0.2-v0.1 [95% CI] | v0.2 RPS | v0.1 RPS | Base LL | Book closing LL (subset) | v0.2-book [95% CI] | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| BRA | 1101 | 1.0071 [0.9835, 1.0298] | 1.0085 | -0.0014 [-0.0038, 0.0012] | 0.2041 | 0.2044 | 1.0495 | 0.9804 | 0.0274 [0.0129, 0.0419] | 0.0074 |
| D1 | 693 | 0.9898 [0.9575, 1.0262] | 0.9921 | -0.0022 [-0.0066, 0.0018] | 0.2022 | 0.2032 | 1.0778 | 0.9666 | 0.0255 [0.0121, 0.0407] | 0.0176 |
| E0 | 860 | 1.0032 [0.9750, 1.0310] | 1.0068 | -0.0037 [-0.0076, 0.0004] | 0.2049 | 0.2057 | 1.0833 | 0.9793 | 0.0121 [-0.0006, 0.0243] | 0.0101 |
| E1 | 1284 | 1.0502 [1.0332, 1.0670] | 1.0541 | -0.0039 [-0.0068, -0.0008] | 0.2174 | 0.2185 | 1.077 | 1.0355 | 0.0131 [0.0038, 0.0224] | 0.0168 |
| F1 | 702 | 0.9798 [0.9469, 1.0111] | 0.982 | -0.0022 [-0.0062, 0.0015] | 0.205 | 0.206 | 1.0581 | 0.9551 | 0.0191 [0.0045, 0.034] | 0.0209 |
| I1 | 870 | 0.9698 [0.9444, 0.9975] | 0.9721 | -0.0023 [-0.0057, 0.0015] | 0.1941 | 0.1949 | 1.0861 | 0.9551 | 0.0111 [-0.0004, 0.0228] | 0.0236 |
| SP1 | 879 | 0.9683 [0.9400, 0.9986] | 0.9708 | -0.0025 [-0.0062, 0.0014] | 0.1955 | 0.1964 | 1.0622 | 0.94 | 0.0198 [0.0102, 0.0303] | 0.0129 |
| USA | 1572 | 1.0537 [1.0347, 1.0729] | 1.0503 | 0.0033 [0.001, 0.0056] | 0.2224 | 0.2217 | 1.0708 | 1.0281 | 0.0268 [0.0148, 0.0387] | 0.0181 |
| PSL | 690 | 1.0141 [0.9869, 1.0399] | - | - | 0.2029 | - | 1.0823 | n/a | - | 0.0096 |

## By league and season

| League season | n | Ens LL | Base LL | Book LL | Ens RPS | Book RPS |
|---|---|---|---|---|---|---|
| BRA 2024 | 380 | 1.0301 | 1.0574 | 0.9854 | 0.2116 | 0.1969 |
| BRA 2025 | 380 | 0.9901 | 1.0403 | 0.9748 | 0.2 | 0.1965 |
| BRA 2026 | 341 | 1.0005 | 1.051 | n/a | 0.2004 | n/a |
| D1 2024-25 | 306 | 1.0158 | 1.0929 | 0.9882 | 0.209 | 0.2019 |
| D1 2025-26 | 306 | 0.9672 | 1.0712 | 0.9205 | 0.1943 | 0.1857 |
| D1 2026-27 | 81 | 0.9771 | 1.0458 | 0.9696 | 0.206 | 0.2054 |
| E0 2024-25 | 380 | 0.9842 | 1.0826 | 0.9664 | 0.2021 | 0.1961 |
| E0 2025-26 | 380 | 1.0186 | 1.0841 | 0.9875 | 0.2067 | 0.1994 |
| E0 2026-27 | 100 | 1.0168 | 1.0831 | 1.0108 | 0.2081 | 0.2047 |
| E1 2024-25 | 552 | 1.0248 | 1.0714 | 1.0274 | 0.2067 | 0.2076 |
| E1 2025-26 | 552 | 1.065 | 1.0831 | 1.0502 | 0.2234 | 0.2198 |
| E1 2026-27 | 180 | 1.083 | 1.0754 | 1.0381 | 0.2314 | 0.2163 |
| F1 2024-25 | 306 | 0.9757 | 1.0513 | 0.955 | 0.2075 | 0.2009 |
| F1 2025-26 | 306 | 0.9884 | 1.0655 | 0.9592 | 0.204 | 0.2018 |
| F1 2026-27 | 90 | 0.9643 | 1.0558 | 0.9482 | 0.2002 | 0.1949 |
| I1 2024-25 | 380 | 0.9631 | 1.0906 | 0.9513 | 0.1885 | 0.1841 |
| I1 2025-26 | 380 | 0.9964 | 1.0899 | 0.9907 | 0.2015 | 0.1933 |
| I1 2026-27 | 110 | 0.9007 | 1.0576 | 0.9041 | 0.1881 | 0.1908 |
| SP1 2024-25 | 380 | 0.9735 | 1.0713 | 0.9463 | 0.1953 | 0.1875 |
| SP1 2025-26 | 380 | 0.9738 | 1.0488 | 0.9484 | 0.1989 | 0.1867 |
| SP1 2026-27 | 119 | 0.9344 | 1.0762 | 0.9064 | 0.1854 | 0.1776 |
| USA 2024 | 522 | 1.064 | 1.0731 | 1.0296 | 0.2263 | 0.2165 |
| USA 2025 | 540 | 1.044 | 1.0742 | 1.0267 | 0.2194 | 0.2152 |
| USA 2026 | 510 | 1.0533 | 1.0649 | n/a | 0.2217 | n/a |

## Value rule ROI (test seasons, average pre-closing odds)

v0.2, all leagues: {'n_bets': 1646, 'roi': -0.1207, 'roi_ci95': [-0.1862, -0.0516], 'profit_units': -198.64, 'mean_odds': 3.24, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

v0.1, all leagues: {'n_bets': 1882, 'roi': -0.1455, 'roi_ci95': [-0.2044, -0.0794], 'profit_units': -273.88, 'mean_odds': 3.193, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

Model + market variant, all leagues: {'n_bets': 104, 'roi': 0.1125, 'roi_ci95': [-0.0659, 0.2978], 'profit_units': 11.7, 'mean_odds': 1.874, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

Validated leagues only (['E0', 'I1']): {'n_bets': 594, 'roi': -0.1012, 'roi_ci95': [-0.2227, 0.0226], 'profit_units': -60.09, 'mean_odds': 3.501, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

By league:

- BRA: {'n_bets': 0, 'roi': None, 'roi_ci95': [None, None], 'profit_units': 0.0, 'mean_odds': None, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- D1: {'n_bets': 180, 'roi': -0.2456, 'roi_ci95': [-0.4357, -0.0615], 'profit_units': -44.21, 'mean_odds': 3.063, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E0: {'n_bets': 274, 'roi': -0.0318, 'roi_ci95': [-0.2116, 0.1398], 'profit_units': -8.72, 'mean_odds': 3.492, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E1: {'n_bets': 403, 'roi': -0.1607, 'roi_ci95': [-0.2968, -0.0108], 'profit_units': -64.75, 'mean_odds': 3.211, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- F1: {'n_bets': 240, 'roi': 0.0637, 'roi_ci95': [-0.127, 0.2593], 'profit_units': 15.28, 'mean_odds': 3.102, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- I1: {'n_bets': 320, 'roi': -0.1605, 'roi_ci95': [-0.3193, 0.0025], 'profit_units': -51.37, 'mean_odds': 3.509, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- SP1: {'n_bets': 229, 'roi': -0.1959, 'roi_ci95': [-0.3637, -0.0274], 'profit_units': -44.87, 'mean_odds': 2.897, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
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

- ens: log loss 1.0141 [0.9869, 1.0399], RPS 0.2029 [0.1943, 0.2118], Brier 0.6089 [0.5908, 0.6286], accuracy 0.4797 [0.4420, 0.5160]
- ens_v2: log loss 1.0125 [0.9850, 1.0393], RPS 0.2025 [0.1939, 0.2109], Brier 0.6081 [0.5876, 0.6267], accuracy 0.4638 [0.4246, 0.4986]
- poisson: log loss 1.0136 [0.9866, 1.0400], RPS 0.2029 [0.1949, 0.2114], Brier 0.6086 [0.5901, 0.6272], accuracy 0.4754 [0.4362, 0.5116]
- dc: log loss 1.0148 [0.9869, 1.0428], RPS 0.2030 [0.1949, 0.2113], Brier 0.6094 [0.5917, 0.6287], accuracy 0.4696 [0.4319, 0.5072]
- dcj: log loss 1.0133 [0.9858, 1.0389], RPS 0.2026 [0.1944, 0.2106], Brier 0.6089 [0.5902, 0.6281], accuracy 0.4594 [0.4232, 0.4957]
- base: log loss 1.0823 [1.0692, 1.0952], RPS 0.2248 [0.2184, 0.2311], Brier 0.6553 [0.6458, 0.6643], accuracy 0.4232 [0.3855, 0.4594]
- always home: accuracy 0.4232 [0.387, 0.4595]
- ensemble minus base log loss: {'mean': -0.0682, 'ci': [-0.0918, -0.0467]}; ECE 0.0096
- v2 (Poisson/DCJ) minus v1: {'mean': -0.0016, 'ci': [-0.0046, 0.0012]}; gate: {'season': '2023-24', 'ens_v2_log_loss': 1.0272, 'ens_log_loss': 1.0273, 'adopted': True}
- missing: No odds (no bookmaker benchmark, no value backtest), no shots, no dates (no Elo/form/logit models).

Past performance does not guarantee future results. No betting outcome is guaranteed.