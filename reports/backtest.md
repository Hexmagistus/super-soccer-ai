# SUPER SOCCER AI - walk-forward backtest

Ensemble weights (chosen on validation season, n=3205): {'poisson': 0.0, 'dc': 0.7, 'elo': 0.0, 'logit': 0.3}

Test matches: 7469. 95% bootstrap CIs in brackets.

| Model | n | Accuracy | Log loss | Brier | RPS |
|---|---|---|---|---|---|
| Ensemble | 7469 | 0.4993 [0.4884, 0.5108] | 1.0148 [1.0054, 1.0248] | 0.6076 [0.6015, 0.6139] | 0.2087 [0.2059, 0.2116] |
| Poisson | 7469 | 0.4979 [0.4864, 0.5096] | 1.0170 [1.0075, 1.0262] | 0.6093 [0.6021, 0.6160] | 0.2094 [0.2066, 0.2123] |
| Dixon-Coles | 7469 | 0.4979 [0.4865, 0.5094] | 1.0172 [1.0083, 1.0272] | 0.6093 [0.6031, 0.6160] | 0.2094 [0.2066, 0.2123] |
| Elo | 7469 | 0.4963 [0.4852, 0.5076] | 1.0177 [1.0082, 1.0270] | 0.6097 [0.6030, 0.6162] | 0.2096 [0.2070, 0.2122] |
| Logistic | 7469 | 0.4932 [0.4823, 0.5042] | 1.0245 [1.0136, 1.0342] | 0.6133 [0.6062, 0.6205] | 0.2106 [0.2077, 0.2135] |
| Base rates | 7469 | 0.4425 [0.4307, 0.4536] | 1.0716 [1.0663, 1.0780] | 0.6480 [0.6442, 0.6520] | 0.2282 [0.2264, 0.2301] |
| Bookmaker closing (subset) | 5581 | 0.5173 [0.5035, 0.5300] | 0.9896 [0.9781, 1.0006] | 0.5911 [0.5833, 0.5991] | 0.2013 [0.1981, 0.2046] |
| Ensemble (same subset) | 5581 | 0.5026 [0.4899, 0.5157] | 1.0101 [1.0000, 1.0209] | 0.6043 [0.5968, 0.6116] | 0.2074 [0.2043, 0.2107] |
| Home always | 7469 | 0.4425 [0.4312, 0.4539] | - | - | - |

Ensemble minus bookmaker log loss: {'mean': 0.0205, 'ci': [0.0161, 0.0249]}
Ensemble minus base-rate log loss: {'mean': -0.0568, 'ci': [-0.0639, -0.0487]}
Exact-score hit rate (top score): {'rate': 0.1209, 'ci': [0.1137, 0.1285], 'mean_top_score_prob': 0.1271}
Total goals MAE: {'model': 1.3044, 'ci': [1.2831, 1.3266], 'baseline_train_mean': 1.3092}
ECE: 0.0061

## Calibration (all outcomes pooled)

| bin | n | mean predicted | observed |
|---|---|---|---|
| 0.0-0.1 | 327 | 0.0741 | 0.0734 |
| 0.1-0.2 | 2438 | 0.1622 | 0.162 |
| 0.2-0.3 | 9400 | 0.2548 | 0.259 |
| 0.3-0.4 | 4035 | 0.3436 | 0.3358 |
| 0.4-0.5 | 3001 | 0.4473 | 0.4512 |
| 0.5-0.6 | 1867 | 0.5458 | 0.5265 |
| 0.6-0.7 | 947 | 0.6417 | 0.6505 |
| 0.7-0.8 | 307 | 0.7414 | 0.7655 |
| 0.8-0.9 | 83 | 0.8374 | 0.8554 |
| 0.9-1.0 | 2 | 0.9034 | 0.5 |

## By league

| League | n | Ens log loss | Base log loss | Book log loss | Ens acc | Book acc | ECE |
|---|---|---|---|---|---|---|---|
| BRA | 1049 | 1.0144 [0.9908, 1.0383] | 1.0516 | 0.9804 | 0.5081 | 0.5349 | 0.0096 |
| D1 | 648 | 0.9942 [0.9575, 1.0272] | 1.0795 | 0.9653 | 0.5201 | 0.5418 | 0.0187 |
| E0 | 810 | 1.0064 [0.9741, 1.0368] | 1.0852 | 0.9802 | 0.5025 | 0.5328 | 0.0149 |
| E1 | 1199 | 1.0530 [1.0336, 1.0711] | 1.0783 | 1.0373 | 0.452 | 0.4673 | 0.0176 |
| F1 | 657 | 0.9883 [0.9553, 1.0241] | 1.0612 | 0.9631 | 0.5373 | 0.5377 | 0.0148 |
| I1 | 810 | 0.9781 [0.9482, 1.0067] | 1.0887 | 0.9611 | 0.5296 | 0.535 | 0.0134 |
| SP1 | 829 | 0.9738 [0.9429, 1.0050] | 1.0608 | 0.9451 | 0.5247 | 0.562 | 0.0235 |
| USA | 1467 | 1.0531 [1.0339, 1.0725] | 1.0709 | 1.0281 | 0.4724 | 0.4804 | 0.0134 |
| PSL | 690 | 1.0141 [0.9875, 1.0424] | 1.0823 | n/a | 0.4797 | n/a | 0.0096 |

## By league and season

| League season | n | Ens LL | Base LL | Book LL | Ens RPS | Book RPS |
|---|---|---|---|---|---|---|
| BRA 2024 | 380 | 1.0296 | 1.0574 | 0.9854 | 0.2113 | 0.1969 |
| BRA 2025 | 380 | 0.993 | 1.0403 | 0.9748 | 0.2007 | 0.1965 |
| BRA 2026 | 289 | 1.0226 | 1.0589 | n/a | 0.205 | n/a |
| D1 2024-25 | 306 | 1.019 | 1.0929 | 0.9882 | 0.2103 | 0.2019 |
| D1 2025-26 | 306 | 0.9704 | 1.0712 | 0.9205 | 0.1953 | 0.1857 |
| D1 2026-27 | 36 | 0.9859 | 1.037 | 0.9562 | 0.2115 | 0.2071 |
| E0 2024-25 | 380 | 0.9889 | 1.0826 | 0.9664 | 0.2033 | 0.1961 |
| E0 2025-26 | 380 | 1.0223 | 1.0841 | 0.9875 | 0.2075 | 0.1994 |
| E0 2026-27 | 50 | 1.0185 | 1.114 | 1.0549 | 0.1959 | 0.2061 |
| E1 2024-25 | 552 | 1.0312 | 1.0714 | 1.0274 | 0.2083 | 0.2076 |
| E1 2025-26 | 552 | 1.0652 | 1.0831 | 1.0502 | 0.2237 | 0.2198 |
| E1 2026-27 | 95 | 1.1093 | 1.0902 | 1.058 | 0.2292 | 0.2117 |
| F1 2024-25 | 306 | 0.9706 | 1.0513 | 0.955 | 0.2068 | 0.2009 |
| F1 2025-26 | 306 | 0.9967 | 1.0655 | 0.9592 | 0.2062 | 0.2018 |
| F1 2026-27 | 45 | 1.0523 | 1.0991 | 1.031 | 0.2118 | 0.2066 |
| I1 2024-25 | 380 | 0.9681 | 1.0906 | 0.9513 | 0.19 | 0.1841 |
| I1 2025-26 | 380 | 0.9982 | 1.0899 | 0.9907 | 0.2021 | 0.1933 |
| I1 2026-27 | 50 | 0.9003 | 1.0655 | 0.9178 | 0.1863 | 0.1955 |
| SP1 2024-25 | 380 | 0.9754 | 1.0713 | 0.9463 | 0.1959 | 0.1875 |
| SP1 2025-26 | 380 | 0.9755 | 1.0488 | 0.9484 | 0.1997 | 0.1867 |
| SP1 2026-27 | 69 | 0.9559 | 1.0694 | 0.9299 | 0.1958 | 0.1884 |
| USA 2024 | 522 | 1.0584 | 1.0731 | 1.0296 | 0.2252 | 0.2165 |
| USA 2025 | 540 | 1.0419 | 1.0742 | 1.0267 | 0.2191 | 0.2152 |
| USA 2026 | 405 | 1.0612 | 1.0636 | n/a | 0.2248 | n/a |

## Value rule ROI

All leagues: {'n_bets': 1753, 'roi': -0.1486, 'roi_ci95': [-0.2123, -0.0818], 'profit_units': -260.44, 'mean_odds': 3.193, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

Validated leagues only (['E0']): {'n_bets': 291, 'roi': -0.1078, 'roi_ci95': [-0.2701, 0.0643], 'profit_units': -31.36, 'mean_odds': 3.424, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

By league:

- BRA: {'n_bets': 0, 'roi': None, 'roi_ci95': [None, None], 'profit_units': 0.0, 'mean_odds': None, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- D1: {'n_bets': 192, 'roi': -0.3049, 'roi_ci95': [-0.4825, -0.1244], 'profit_units': -58.55, 'mean_odds': 2.915, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E0: {'n_bets': 291, 'roi': -0.1078, 'roi_ci95': [-0.2686, 0.0634], 'profit_units': -31.36, 'mean_odds': 3.424, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- E1: {'n_bets': 459, 'roi': -0.1454, 'roi_ci95': [-0.2574, -0.0106], 'profit_units': -66.76, 'mean_odds': 3.213, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- F1: {'n_bets': 248, 'roi': -0.0138, 'roi_ci95': [-0.1896, 0.1701], 'profit_units': -3.41, 'mean_odds': 3.128, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- I1: {'n_bets': 310, 'roi': -0.1781, 'roi_ci95': [-0.3464, -0.0221], 'profit_units': -55.22, 'mean_odds': 3.334, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- SP1: {'n_bets': 253, 'roi': -0.1784, 'roi_ci95': [-0.3468, -0.0266], 'profit_units': -45.14, 'mean_odds': 2.996, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}
- USA: {'n_bets': 0, 'roi': None, 'roi_ci95': [None, None], 'profit_units': 0.0, 'mean_odds': None, 'rule': 'edge>=0.05, EV>=0.05, odds<=6.0, average pre-closing odds, 1 unit flat'}

## South Africa PSL (season-ahead, separate method)

Season-ahead backtest (the source has no dates, so no in-season refits are possible): for each test season,
fit Poisson and Dixon-Coles on ALL usable earlier seasons (season-level decay: weight 0.5 per season back),
predict every match of the test season, and compare with base rates of the training seasons and 'always home'.
Ensemble = fixed 50/50 Poisson/DC (no weight tuning, so no validation season is consumed).

Test matches: 690 (seasons ['2023-24', '2024-25', '2025-26']); data seasons used: ['2022-23', '2023-24', '2024-25', '2025-26', '2026-27']

- ens: log loss 1.0141 [0.9875, 1.0424], RPS 0.2029 [0.1943, 0.2115], Brier 0.6089 [0.5906, 0.6265], accuracy 0.4797 [0.4420, 0.5160]
- poisson: log loss 1.0136 [0.9886, 1.0391], RPS 0.2029 [0.1946, 0.2112], Brier 0.6086 [0.5905, 0.6261], accuracy 0.4754 [0.4391, 0.5116]
- dc: log loss 1.0148 [0.9883, 1.0410], RPS 0.2030 [0.1945, 0.2119], Brier 0.6094 [0.5905, 0.6271], accuracy 0.4696 [0.4319, 0.5072]
- base: log loss 1.0823 [1.0697, 1.0957], RPS 0.2248 [0.2189, 0.2313], Brier 0.6553 [0.6459, 0.6644], accuracy 0.4232 [0.3884, 0.4609]
- always home: accuracy 0.4232 [0.3884, 0.458]
- ensemble minus base log loss: {'mean': -0.0682, 'ci': [-0.0903, -0.0448]}; ECE 0.0096
- missing: No odds (no bookmaker benchmark, no value backtest), no shots, no dates (no Elo/form/logit models).

Past performance does not guarantee future results. No betting outcome is guaranteed.