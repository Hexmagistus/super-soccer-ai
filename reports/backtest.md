# SUPER SOCCER AI - walk-forward backtest

Model ssa-0.2.0. v0.2 combination (all chosen on the validation season, n=3205): {'alpha': 0.6, 'w_core': 0.7659961188039859, 'w_logit': 0.23400388119601412, 'T': 0.9032678956981768, 'd': 0.10611251112664781, 'val_log_loss': 1.0035420968935516, 'n_val': 3205, 'market': {'w_model': -0.2625802117515806, 'w_market': 1.3821709644432099, 'val_log_loss': 0.9673824456130709, 'n_val': 2304, 'val_market_only_log_loss': 0.9696827142157589, 'odds': 'average pre-closing odds (football-data Avg/BbAv columns), NOT closing'}}

v0.1 ensemble weights (kept as the 'before' baseline): {'poisson': 0.0, 'dc': 0.7, 'elo': 0.0, 'logit': 0.3}

Test matches: 7840. 95% bootstrap CIs in brackets.

| Model | n | Accuracy | Log loss | Brier | RPS |
|---|---|---|---|---|---|
| Ensemble v0.2 | 7840 | 0.5040 [0.4925, 0.5151] | 1.0114 [1.0024, 1.0213] | 0.6052 [0.5991, 0.6112] | 0.2078 [0.2053, 0.2108] |
| Ensemble v0.1 (before) | 7840 | 0.5017 [0.4914, 0.5128] | 1.0129 [1.0040, 1.0226] | 0.6062 [0.6001, 0.6126] | 0.2083 [0.2057, 0.2110] |
| Poisson | 7840 | 0.5006 [0.4894, 0.5114] | 1.0151 [1.0052, 1.0246] | 0.6079 [0.6010, 0.6141] | 0.2091 [0.2064, 0.2115] |
| Dixon-Coles | 7840 | 0.5006 [0.4899, 0.5119] | 1.0153 [1.0062, 1.0243] | 0.6079 [0.6015, 0.6149] | 0.2091 [0.2065, 0.2116] |
| Elo | 7840 | 0.4985 [0.4872, 0.5101] | 1.0156 [1.0064, 1.0251] | 0.6081 [0.6022, 0.6144] | 0.2091 [0.2067, 0.2116] |
| Logistic | 7840 | 0.4948 [0.4833, 0.5056] | 1.0224 [1.0124, 1.0323] | 0.6119 [0.6051, 0.6187] | 0.2103 [0.2074, 0.2132] |
| Base rates | 7840 | 0.4441 [0.4339, 0.4555] | 1.0709 [1.0656, 1.0764] | 0.6475 [0.6434, 0.6517] | 0.2282 [0.2263, 0.2300] |
| Bookmaker closing (subset) | 5839 | 0.5212 [0.5076, 0.5345] | 0.9873 [0.9775, 0.9979] | 0.5894 [0.5816, 0.5965] | 0.2011 [0.1979, 0.2043] |
| Ensemble v0.2 (same subset) | 5839 | 0.5088 [0.4960, 0.5205] | 1.0065 [0.9971, 1.0178] | 0.6019 [0.5945, 0.6091] | 0.2068 [0.2034, 0.2102] |
| Ensemble v0.1 (same subset) | 5839 | 0.5056 [0.4920, 0.5186] | 1.0081 [0.9975, 1.0190] | 0.6029 [0.5962, 0.6103] | 0.2073 [0.2044, 0.2103] |
| Model + market (pre-closing avg odds) | 4076 | 0.5223 [0.5074, 0.5378] | 0.9790 [0.9646, 0.9942] | 0.5840 [0.5736, 0.5947] | 0.1984 [0.1943, 0.2023] |
| Bookmaker pre-closing avg (market subset) | 4076 | 0.5248 [0.5091, 0.5407] | 0.9798 [0.9671, 0.9932] | 0.5841 [0.5748, 0.5938] | 0.1986 [0.1946, 0.2022] |
| Bookmaker closing (market subset) | 4076 | 0.5292 [0.5145, 0.5442] | 0.9780 [0.9642, 0.9910] | 0.5829 [0.5729, 0.5927] | 0.1980 [0.1944, 0.2020] |
| Home always | 7840 | 0.4441 [0.4329, 0.4547] | - | - | - |

v0.2 minus v0.1 (paired bootstrap 95% CI): {'log_loss': -0.0015, 'log_loss_ci': [-0.0027, -0.0003], 'rps': -0.00052, 'rps_ci': [-0.00083, -0.00021]}
v0.1 minus bookmaker closing log loss: {'mean': 0.0208, 'ci': [0.0164, 0.0253]}
v0.2 minus bookmaker closing RPS: {'mean': 0.00571, 'ci': [0.0045, 0.00696]}
Model+market minus closing log loss: {'mean': 0.001, 'ci': [-0.002, 0.004]}; minus pre-closing: {'mean': -0.0007, 'ci': [-0.0028, 0.0013]}
Ensemble minus bookmaker log loss: {'mean': 0.0192, 'ci': [0.0146, 0.0235]}
Ensemble minus base-rate log loss: {'mean': -0.0595, 'ci': [-0.067, -0.0525]}
Exact-score hit rate (top score): {'rate': 0.1231, 'ci': [0.1161, 0.1304], 'mean_top_score_prob': 0.1305}
Total goals MAE: {'model': 1.306, 'ci': [1.2857, 1.3284], 'baseline_train_mean': 1.315}
ECE: 0.0065

## Calibration (all outcomes pooled)

| bin | n | mean predicted | observed |
|---|---|---|---|
| 0.0-0.1 | 425 | 0.0734 | 0.0729 |
| 0.1-0.2 | 2700 | 0.16 | 0.1704 |
| 0.2-0.3 | 9274 | 0.2581 | 0.2575 |
| 0.3-0.4 | 4806 | 0.3402 | 0.3298 |
| 0.4-0.5 | 2979 | 0.4474 | 0.4582 |
| 0.5-0.6 | 1876 | 0.5463 | 0.5362 |
| 0.6-0.7 | 1029 | 0.6425 | 0.656 |
| 0.7-0.8 | 344 | 0.7438 | 0.7442 |
| 0.8-0.9 | 83 | 0.8404 | 0.8675 |
| 0.9-1.0 | 4 | 0.9108 | 0.5 |

## By league

| League | n | v0.2 log loss | v0.1 log loss | v0.2-v0.1 [95% CI] | v0.2 RPS | v0.1 RPS | Base LL | Book closing LL (subset) | v0.2-book [95% CI] | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| BRA | 1087 | 1.0093 [0.9844, 1.0318] | 1.0106 | -0.0013 [-0.004, 0.0012] | 0.2045 | 0.2047 | 1.0501 | 0.9804 | 0.0274 [0.012, 0.0417] | 0.0089 |
| D1 | 684 | 0.9946 [0.9624, 1.0337] | 0.9967 | -0.0021 [-0.0064, 0.002] | 0.2034 | 0.2043 | 1.0791 | 0.9728 | 0.0256 [0.0099, 0.0404] | 0.0172 |
| E0 | 849 | 1.0038 [0.9736, 1.0336] | 1.0074 | -0.0036 [-0.0073, 0.0007] | 0.2048 | 0.2056 | 1.0841 | 0.9795 | 0.0125 [0.0009, 0.0245] | 0.0106 |
| E1 | 1260 | 1.0491 [1.0294, 1.0669] | 1.053 | -0.004 [-0.0069, -0.0011] | 0.2168 | 0.2179 | 1.0776 | 1.0342 | 0.0129 [0.003, 0.0223] | 0.0159 |
| F1 | 692 | 0.9794 [0.9459, 1.0127] | 0.9817 | -0.0023 [-0.0063, 0.0019] | 0.2044 | 0.2053 | 1.0579 | 0.9559 | 0.0176 [0.0025, 0.0326] | 0.02 |
| I1 | 858 | 0.9689 [0.9378, 0.9958] | 0.9713 | -0.0025 [-0.0063, 0.0013] | 0.1937 | 0.1946 | 1.086 | 0.9541 | 0.0109 [-0.0002, 0.0229] | 0.0246 |
| SP1 | 868 | 0.9686 [0.9387, 0.9986] | 0.971 | -0.0024 [-0.0062, 0.0017] | 0.1959 | 0.1967 | 1.0609 | 0.9408 | 0.0192 [0.0087, 0.029] | 0.0123 |
| USA | 1542 | 1.0557 [1.0361, 1.0754] | 1.0525 | 0.0033 [0.0011, 0.0055] | 0.2224 | 0.2217 | 1.072 | 1.0281 | 0.0268 [0.0153, 0.0384] | 0.0173 |
| PSL | 690 | 1.0141 [0.9866, 1.0407] | - | - | 0.2029 | - | 1.0823 | n/a | - | 0.0096 |

## By league and season

| League season | n | Ens LL | Base LL | Book LL | Ens RPS | Book RPS |
|---|---|---|---|---|---|---|
| BRA 2024 | 380 | 1.0301 | 1.0574 | 0.9854 | 0.2116 | 0.1969 |
| BRA 2025 | 380 | 0.9901 | 1.0403 | 0.9748 | 0.2 | 0.1965 |
| BRA 2026 | 327 | 1.0075 | 1.0531 | n/a | 0.2015 | n/a |
| D1 2024-25 | 306 | 1.0158 | 1.0929 | 0.9882 | 0.209 | 0.2019 |
| D1 2025-26 | 306 | 0.9672 | 1.0712 | 0.9205 | 0.1943 | 0.1857 |
| D1 2026-27 | 72 | 1.0214 | 1.0538 | 1.0155 | 0.2179 | 0.218 |
| E0 2024-25 | 380 | 0.9842 | 1.0826 | 0.9664 | 0.2021 | 0.1961 |
| E0 2025-26 | 380 | 1.0186 | 1.0841 | 0.9875 | 0.2067 | 0.1994 |
| E0 2026-27 | 89 | 1.0245 | 1.0904 | 1.0166 | 0.2084 | 0.2042 |
| E1 2024-25 | 552 | 1.0248 | 1.0714 | 1.0274 | 0.2067 | 0.2076 |
| E1 2025-26 | 552 | 1.065 | 1.0831 | 1.0502 | 0.2234 | 0.2198 |
| E1 2026-27 | 156 | 1.0787 | 1.0803 | 1.0303 | 0.2287 | 0.2121 |
| F1 2024-25 | 306 | 0.9757 | 1.0513 | 0.955 | 0.2075 | 0.2009 |
| F1 2025-26 | 306 | 0.9884 | 1.0655 | 0.9592 | 0.204 | 0.2018 |
| F1 2026-27 | 80 | 0.9588 | 1.0545 | 0.9526 | 0.1941 | 0.1926 |
| I1 2024-25 | 380 | 0.9631 | 1.0906 | 0.9513 | 0.1885 | 0.1841 |
| I1 2025-26 | 380 | 0.9964 | 1.0899 | 0.9907 | 0.2015 | 0.1933 |
| I1 2026-27 | 98 | 0.8846 | 1.0527 | 0.891 | 0.1841 | 0.1884 |
| SP1 2024-25 | 380 | 0.9735 | 1.0713 | 0.9463 | 0.1953 | 0.1875 |
| SP1 2025-26 | 380 | 0.9738 | 1.0488 | 0.9484 | 0.1989 | 0.1867 |
| SP1 2026-27 | 108 | 0.9334 | 1.0671 | 0.9083 | 0.1871 | 0.1805 |
| USA 2024 | 522 | 1.064 | 1.0731 | 1.0296 | 0.2263 | 0.2165 |
| USA 2025 | 540 | 1.044 | 1.0742 | 1.0267 | 0.2194 | 0.2152 |
| USA 2026 | 480 | 1.06 | 1.0684 | n/a | 0.2217 | n/a |

## Value rule ROI (test seasons, average pre-closing odds)

v0.2, all leagues: {'n_bets': 1615, 'roi': -0.1204, 'roi_ci95': [-0.191, -0.0512], 'profit_units': -194.51, 'mean_odds': 3.241, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

v0.1, all leagues: {'n_bets': 1852, 'roi': -0.1462, 'roi_ci95': [-0.2114, -0.0818], 'profit_units': -270.75, 'mean_odds': 3.192, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

Model + market variant, all leagues: {'n_bets': 104, 'roi': 0.1125, 'roi_ci95': [-0.0598, 0.2805], 'profit_units': 11.7, 'mean_odds': 1.874, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

Validated leagues only (['I1']): {'n_bets': 314, 'roi': -0.1511, 'roi_ci95': [-0.3121, 0.0119], 'profit_units': -47.43, 'mean_odds': 3.529, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

By league:

- BRA: {'n_bets': 0, 'roi': None, 'roi_ci95': [None, None], 'profit_units': 0.0, 'mean_odds': None, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- D1: {'n_bets': 178, 'roi': -0.2676, 'roi_ci95': [-0.4473, -0.0631], 'profit_units': -47.63, 'mean_odds': 3.067, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E0: {'n_bets': 272, 'roi': -0.0346, 'roi_ci95': [-0.2061, 0.141], 'profit_units': -9.41, 'mean_odds': 3.492, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E1: {'n_bets': 390, 'roi': -0.1675, 'roi_ci95': [-0.2988, -0.027], 'profit_units': -65.34, 'mean_odds': 3.207, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- F1: {'n_bets': 236, 'roi': 0.0685, 'roi_ci95': [-0.1178, 0.2497], 'profit_units': 16.17, 'mean_odds': 3.1, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- I1: {'n_bets': 314, 'roi': -0.1511, 'roi_ci95': [-0.2925, 0.0218], 'profit_units': -47.43, 'mean_odds': 3.529, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- SP1: {'n_bets': 225, 'roi': -0.1816, 'roi_ci95': [-0.3476, 0.0038], 'profit_units': -40.87, 'mean_odds': 2.882, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
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

- ens: log loss 1.0141 [0.9866, 1.0407], RPS 0.2029 [0.1941, 0.2112], Brier 0.6089 [0.5906, 0.6285], accuracy 0.4797 [0.4420, 0.5174]
- ens_v2: log loss 1.0125 [0.9864, 1.0390], RPS 0.2025 [0.1943, 0.2105], Brier 0.6081 [0.5899, 0.6261], accuracy 0.4638 [0.4304, 0.4986]
- poisson: log loss 1.0136 [0.9862, 1.0398], RPS 0.2029 [0.1944, 0.2118], Brier 0.6086 [0.5881, 0.6277], accuracy 0.4754 [0.4362, 0.5130]
- dc: log loss 1.0148 [0.9878, 1.0414], RPS 0.2030 [0.1945, 0.2124], Brier 0.6094 [0.5901, 0.6277], accuracy 0.4696 [0.4348, 0.5058]
- dcj: log loss 1.0133 [0.9854, 1.0394], RPS 0.2026 [0.1942, 0.2111], Brier 0.6089 [0.5888, 0.6284], accuracy 0.4594 [0.4217, 0.4971]
- base: log loss 1.0823 [1.0690, 1.0952], RPS 0.2248 [0.2193, 0.2306], Brier 0.6553 [0.6453, 0.6643], accuracy 0.4232 [0.3870, 0.4609]
- always home: accuracy 0.4232 [0.3841, 0.4609]
- ensemble minus base log loss: {'mean': -0.0682, 'ci': [-0.0919, -0.0462]}; ECE 0.0096
- v2 (Poisson/DCJ) minus v1: {'mean': -0.0016, 'ci': [-0.0047, 0.0013]}; gate: {'season': '2023-24', 'ens_v2_log_loss': 1.0272, 'ens_log_loss': 1.0273, 'adopted': True}
- missing: No odds (no bookmaker benchmark, no value backtest), no shots, no dates (no Elo/form/logit models).

Past performance does not guarantee future results. No betting outcome is guaranteed.