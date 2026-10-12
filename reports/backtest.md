# SUPER SOCCER AI - walk-forward backtest

Model ssa-0.2.0. v0.2 combination (all chosen on the validation season, n=3205): {'alpha': 0.6, 'w_core': 0.7659961188039859, 'w_logit': 0.23400388119601412, 'T': 0.9032678956981768, 'd': 0.10611251112664781, 'val_log_loss': 1.0035420968935516, 'n_val': 3205, 'market': {'w_model': -0.2625802117515806, 'w_market': 1.3821709644432099, 'val_log_loss': 0.9673824456130709, 'n_val': 2304, 'val_market_only_log_loss': 0.9696827142157589, 'odds': 'average pre-closing odds (football-data Avg/BbAv columns), NOT closing'}}

v0.1 ensemble weights (kept as the 'before' baseline): {'poisson': 0.0, 'dc': 0.7, 'elo': 0.0, 'logit': 0.3}

Test matches: 7469. 95% bootstrap CIs in brackets.

| Model | n | Accuracy | Log loss | Brier | RPS |
|---|---|---|---|---|---|
| Ensemble v0.2 | 7469 | 0.5010 [0.4903, 0.5120] | 1.0136 [1.0046, 1.0236] | 0.6068 [0.6008, 0.6132] | 0.2083 [0.2054, 0.2113] |
| Ensemble v0.1 (before) | 7469 | 0.4993 [0.4883, 0.5112] | 1.0148 [1.0054, 1.0236] | 0.6076 [0.6007, 0.6142] | 0.2087 [0.2060, 0.2113] |
| Poisson | 7469 | 0.4979 [0.4864, 0.5096] | 1.0170 [1.0075, 1.0262] | 0.6093 [0.6021, 0.6160] | 0.2094 [0.2066, 0.2123] |
| Dixon-Coles | 7469 | 0.4979 [0.4865, 0.5094] | 1.0172 [1.0083, 1.0272] | 0.6093 [0.6031, 0.6160] | 0.2094 [0.2066, 0.2123] |
| Elo | 7469 | 0.4963 [0.4852, 0.5076] | 1.0177 [1.0082, 1.0270] | 0.6097 [0.6030, 0.6162] | 0.2096 [0.2070, 0.2122] |
| Logistic | 7469 | 0.4932 [0.4823, 0.5042] | 1.0245 [1.0136, 1.0342] | 0.6133 [0.6062, 0.6205] | 0.2106 [0.2077, 0.2135] |
| Base rates | 7469 | 0.4425 [0.4307, 0.4536] | 1.0716 [1.0663, 1.0780] | 0.6480 [0.6442, 0.6520] | 0.2282 [0.2264, 0.2301] |
| Bookmaker closing (subset) | 5581 | 0.5173 [0.5046, 0.5313] | 0.9896 [0.9779, 1.0010] | 0.5911 [0.5833, 0.5993] | 0.2013 [0.1980, 0.2048] |
| Ensemble v0.2 (same subset) | 5581 | 0.5051 [0.4931, 0.5180] | 1.0087 [0.9983, 1.0196] | 0.6034 [0.5960, 0.6103] | 0.2070 [0.2039, 0.2102] |
| Ensemble v0.1 (same subset) | 5581 | 0.5026 [0.4892, 0.5142] | 1.0101 [1.0003, 1.0206] | 0.6043 [0.5965, 0.6123] | 0.2074 [0.2041, 0.2106] |
| Model + market (pre-closing avg odds) | 3818 | 0.5173 [0.5016, 0.5330] | 0.9822 [0.9668, 0.9975] | 0.5864 [0.5756, 0.5968] | 0.1987 [0.1946, 0.2027] |
| Bookmaker pre-closing avg (market subset) | 3818 | 0.5196 [0.5039, 0.5375] | 0.9826 [0.9693, 0.9976] | 0.5862 [0.5772, 0.5956] | 0.1988 [0.1952, 0.2024] |
| Bookmaker closing (market subset) | 3818 | 0.5241 [0.5081, 0.5401] | 0.9808 [0.9669, 0.9949] | 0.5850 [0.5756, 0.5943] | 0.1982 [0.1942, 0.2020] |
| Home always | 7469 | 0.4425 [0.4317, 0.4543] | - | - | - |

v0.2 minus v0.1 (paired bootstrap 95% CI): {'log_loss': -0.0012, 'log_loss_ci': [-0.0024, -0.0001], 'rps': -0.00042, 'rps_ci': [-0.00074, -0.00013]}
v0.1 minus bookmaker closing log loss: {'mean': 0.0205, 'ci': [0.0159, 0.025]}
v0.2 minus bookmaker closing RPS: {'mean': 0.00564, 'ci': [0.00436, 0.00703]}
Model+market minus closing log loss: {'mean': 0.0015, 'ci': [-0.0015, 0.0047]}; minus pre-closing: {'mean': -0.0003, 'ci': [-0.0025, 0.0017]}
Ensemble minus bookmaker log loss: {'mean': 0.0191, 'ci': [0.0146, 0.0236]}
Ensemble minus base-rate log loss: {'mean': -0.058, 'ci': [-0.0656, -0.0507]}
Exact-score hit rate (top score): {'rate': 0.1244, 'ci': [0.1169, 0.1315], 'mean_top_score_prob': 0.1308}
Total goals MAE: {'model': 1.3013, 'ci': [1.2783, 1.3251], 'baseline_train_mean': 1.3092}
ECE: 0.0068

## Calibration (all outcomes pooled)

| bin | n | mean predicted | observed |
|---|---|---|---|
| 0.0-0.1 | 409 | 0.0733 | 0.0758 |
| 0.1-0.2 | 2563 | 0.16 | 0.1709 |
| 0.2-0.3 | 8838 | 0.2582 | 0.259 |
| 0.3-0.4 | 4575 | 0.3401 | 0.3298 |
| 0.4-0.5 | 2849 | 0.4474 | 0.4567 |
| 0.5-0.6 | 1789 | 0.5464 | 0.5316 |
| 0.6-0.7 | 973 | 0.6421 | 0.6547 |
| 0.7-0.8 | 327 | 0.7436 | 0.7401 |
| 0.8-0.9 | 80 | 0.8412 | 0.8625 |
| 0.9-1.0 | 4 | 0.9108 | 0.5 |

## By league

| League | n | v0.2 log loss | v0.1 log loss | v0.2-v0.1 [95% CI] | v0.2 RPS | v0.1 RPS | Base LL | Book closing LL (subset) | v0.2-book [95% CI] | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| BRA | 1049 | 1.0134 [0.9889, 1.0393] | 1.0144 | -0.001 [-0.0035, 0.0018] | 0.2056 | 0.2057 | 1.0516 | 0.9804 | 0.0274 [0.0124, 0.0426] | 0.011 |
| D1 | 648 | 0.9925 [0.9547, 1.0295] | 0.9942 | -0.0017 [-0.0062, 0.0027] | 0.2025 | 0.2033 | 1.0795 | 0.9653 | 0.0306 [0.0152, 0.0463] | 0.018 |
| E0 | 810 | 1.0029 [0.9750, 1.0311] | 1.0064 | -0.0035 [-0.0078, 0.0002] | 0.2041 | 0.2048 | 1.0852 | 0.9802 | 0.0099 [-0.0027, 0.0221] | 0.0113 |
| E1 | 1199 | 1.0492 [1.0313, 1.0681] | 1.053 | -0.0039 [-0.0069, -0.0007] | 0.216 | 0.217 | 1.0783 | 1.0373 | 0.0098 [0.0003, 0.0205] | 0.0205 |
| F1 | 657 | 0.9868 [0.9554, 1.0200] | 0.9883 | -0.0015 [-0.0057, 0.0027] | 0.2062 | 0.2069 | 1.0612 | 0.9631 | 0.0197 [0.0037, 0.0339] | 0.022 |
| I1 | 810 | 0.9749 [0.9481, 1.0030] | 0.9781 | -0.0032 [-0.0069, 0.0007] | 0.1944 | 0.1954 | 1.0887 | 0.9611 | 0.0114 [-0.0009, 0.0231] | 0.0216 |
| SP1 | 829 | 0.9716 [0.9419, 1.0019] | 0.9738 | -0.0023 [-0.006, 0.0017] | 0.1969 | 0.1976 | 1.0608 | 0.9451 | 0.0182 [0.0078, 0.0292] | 0.0117 |
| USA | 1467 | 1.0570 [1.0374, 1.0771] | 1.0531 | 0.004 [0.0017, 0.0064] | 0.2237 | 0.2229 | 1.0709 | 1.0281 | 0.0268 [0.0156, 0.0383] | 0.0194 |
| PSL | 690 | 1.0141 [0.9871, 1.0409] | - | - | 0.2029 | - | 1.0823 | n/a | - | 0.0096 |

## By league and season

| League season | n | Ens LL | Base LL | Book LL | Ens RPS | Book RPS |
|---|---|---|---|---|---|---|
| BRA 2024 | 380 | 1.0301 | 1.0574 | 0.9854 | 0.2116 | 0.1969 |
| BRA 2025 | 380 | 0.9901 | 1.0403 | 0.9748 | 0.2 | 0.1965 |
| BRA 2026 | 289 | 1.0221 | 1.0589 | n/a | 0.2051 | n/a |
| D1 2024-25 | 306 | 1.0158 | 1.0929 | 0.9882 | 0.209 | 0.2019 |
| D1 2025-26 | 306 | 0.9672 | 1.0712 | 0.9205 | 0.1943 | 0.1857 |
| D1 2026-27 | 36 | 1.0104 | 1.037 | 0.9562 | 0.2159 | 0.2071 |
| E0 2024-25 | 380 | 0.9842 | 1.0826 | 0.9664 | 0.2021 | 0.1961 |
| E0 2025-26 | 380 | 1.0186 | 1.0841 | 0.9875 | 0.2067 | 0.1994 |
| E0 2026-27 | 50 | 1.0265 | 1.114 | 1.0549 | 0.1994 | 0.2061 |
| E1 2024-25 | 552 | 1.0248 | 1.0714 | 1.0274 | 0.2067 | 0.2076 |
| E1 2025-26 | 552 | 1.065 | 1.0831 | 1.0502 | 0.2234 | 0.2198 |
| E1 2026-27 | 95 | 1.0989 | 1.0902 | 1.058 | 0.2264 | 0.2117 |
| F1 2024-25 | 306 | 0.9757 | 1.0513 | 0.955 | 0.2075 | 0.2009 |
| F1 2025-26 | 306 | 0.9884 | 1.0655 | 0.9592 | 0.204 | 0.2018 |
| F1 2026-27 | 45 | 1.0512 | 1.0991 | 1.031 | 0.2122 | 0.2066 |
| I1 2024-25 | 380 | 0.9631 | 1.0906 | 0.9513 | 0.1885 | 0.1841 |
| I1 2025-26 | 380 | 0.9964 | 1.0899 | 0.9907 | 0.2015 | 0.1933 |
| I1 2026-27 | 50 | 0.9012 | 1.0655 | 0.9178 | 0.186 | 0.1955 |
| SP1 2024-25 | 380 | 0.9735 | 1.0713 | 0.9463 | 0.1953 | 0.1875 |
| SP1 2025-26 | 380 | 0.9738 | 1.0488 | 0.9484 | 0.1989 | 0.1867 |
| SP1 2026-27 | 69 | 0.9489 | 1.0694 | 0.9299 | 0.1938 | 0.1884 |
| USA 2024 | 522 | 1.064 | 1.0731 | 1.0296 | 0.2263 | 0.2165 |
| USA 2025 | 540 | 1.044 | 1.0742 | 1.0267 | 0.2194 | 0.2152 |
| USA 2026 | 405 | 1.0655 | 1.0636 | n/a | 0.2261 | n/a |

## Value rule ROI (test seasons, average pre-closing odds)

v0.2, all leagues: {'n_bets': 1519, 'roi': -0.1238, 'roi_ci95': [-0.1946, -0.0502], 'profit_units': -188.01, 'mean_odds': 3.237, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

v0.1, all leagues: {'n_bets': 1753, 'roi': -0.1486, 'roi_ci95': [-0.2098, -0.0861], 'profit_units': -260.44, 'mean_odds': 3.193, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

Model + market variant, all leagues: {'n_bets': 98, 'roi': 0.1168, 'roi_ci95': [-0.0694, 0.3139], 'profit_units': 11.45, 'mean_odds': 1.887, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

Validated leagues only (['E0', 'I1']): {'n_bets': 546, 'roi': -0.0959, 'roi_ci95': [-0.2213, 0.029], 'profit_units': -52.34, 'mean_odds': 3.509, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

By league:

- BRA: {'n_bets': 0, 'roi': None, 'roi_ci95': [None, None], 'profit_units': 0.0, 'mean_odds': None, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- D1: {'n_bets': 168, 'roi': -0.3218, 'roi_ci95': [-0.4924, -0.1246], 'profit_units': -54.06, 'mean_odds': 3.042, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E0: {'n_bets': 248, 'roi': -0.019, 'roi_ci95': [-0.2118, 0.1694], 'profit_units': -4.71, 'mean_odds': 3.451, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E1: {'n_bets': 375, 'roi': -0.1476, 'roi_ci95': [-0.2767, 0.0], 'profit_units': -55.36, 'mean_odds': 3.204, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- F1: {'n_bets': 220, 'roi': 0.0469, 'roi_ci95': [-0.1484, 0.2526], 'profit_units': 10.32, 'mean_odds': 3.136, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- I1: {'n_bets': 298, 'roi': -0.1598, 'roi_ci95': [-0.3173, 0.0072], 'profit_units': -47.63, 'mean_odds': 3.557, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- SP1: {'n_bets': 210, 'roi': -0.1741, 'roi_ci95': [-0.3343, 0.0037], 'profit_units': -36.57, 'mean_odds': 2.85, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
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

- ens: log loss 1.0141 [0.9871, 1.0409], RPS 0.2029 [0.1946, 0.2111], Brier 0.6089 [0.5896, 0.6255], accuracy 0.4797 [0.4435, 0.5159]
- ens_v2: log loss 1.0125 [0.9861, 1.0387], RPS 0.2025 [0.1945, 0.2105], Brier 0.6081 [0.5894, 0.6257], accuracy 0.4638 [0.4275, 0.5029]
- poisson: log loss 1.0136 [0.9869, 1.0402], RPS 0.2029 [0.1951, 0.2111], Brier 0.6086 [0.5912, 0.6271], accuracy 0.4754 [0.4377, 0.5145]
- dc: log loss 1.0148 [0.9881, 1.0427], RPS 0.2030 [0.1949, 0.2112], Brier 0.6094 [0.5922, 0.6273], accuracy 0.4696 [0.4319, 0.5087]
- dcj: log loss 1.0133 [0.9867, 1.0415], RPS 0.2026 [0.1937, 0.2111], Brier 0.6089 [0.5889, 0.6266], accuracy 0.4594 [0.4203, 0.4957]
- base: log loss 1.0823 [1.0687, 1.0947], RPS 0.2248 [0.2193, 0.2306], Brier 0.6553 [0.6467, 0.6639], accuracy 0.4232 [0.3870, 0.4623]
- always home: accuracy 0.4232 [0.384, 0.4595]
- ensemble minus base log loss: {'mean': -0.0682, 'ci': [-0.0914, -0.045]}; ECE 0.0096
- v2 (Poisson/DCJ) minus v1: {'mean': -0.0016, 'ci': [-0.0046, 0.0013]}; gate: {'season': '2023-24', 'ens_v2_log_loss': 1.0272, 'ens_log_loss': 1.0273, 'adopted': True}
- missing: No odds (no bookmaker benchmark, no value backtest), no shots, no dates (no Elo/form/logit models).

Past performance does not guarantee future results. No betting outcome is guaranteed.