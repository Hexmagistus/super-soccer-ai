# SUPER SOCCER AI
**Research the Game. Predict the Score. Measure the Evidence.**

A working MVP that turns real, free football data into probabilistic match research. Core rule: **no fabricated data**. Every number comes
from a downloaded file whose URL, fetch time and HTTP `Last-Modified` are recorded (`data/raw/_meta.json`, table `sources`, shown on Home).
Anything missing is shown as `unavailable`.

## Run
```bash
cd /workspace/super-soccer-ai
python3 -m venv .venv && .venv/bin/pip install pandas numpy scipy scikit-learn fastapi uvicorn pytest requests
.venv/bin/python pipeline.py --backtest     # download (12h cache) -> validate -> SQLite -> walk-forward backtest -> predict -> store
.venv/bin/python pipeline.py                # daily run (re-uses backtest.json; add --force to bypass the download cache)
.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000    # dashboard at http://localhost:8000
.venv/bin/python -m pytest -q tests
```
Daily cron example: `0 6 * * * cd /workspace/super-soccer-ai && .venv/bin/python pipeline.py >> reports/pipeline.log 2>&1`

## Model v0.2 (2026-10-11) - what changed and the honest result
Everything below was selected on the **validation season only** (n=3,205) and then scored once on the untouched test seasons
(n=7,469, 8 leagues). Full candidate list with validation numbers: `reports/experiments.md` (harness: `python -m ssa.experiment`).
- **Joint Dixon-Coles MLE** (`DixonColesJoint`): attack, defence, mu, home advantage and rho fitted together (analytic gradient), time-decay half-life
  tuned (365 d won over 116/198/693 d). Home advantage is per league (every league is fitted separately).
- **Promoted-team prior**: teams that entered the league inside the training window are shrunk towards a jointly estimated "promoted team"
  strength; teams never seen get that prior instead of the league average.
- **Shots-on-target ratings - an xG proxy, not real xG** (`ShotsModel`): attack/defence fitted on SOT, converted to goals with the window's goals/SOT ratio,
  blended geometrically with the DC lambdas (alpha=0.6 goals / 0.4 shots).
- **Combination layer** (`ssa/stack.py`): linear pool of the core model and the logistic model (weights 0.77/0.23 by validation log loss), then
  temperature (T=0.90) and draw-shift (+0.106) recalibration fitted on validation.
- Tried and **rejected** on validation: other half-lives, Elo with promoted/relegated rating inheritance, extra logistic features (rest days, total shots),
  HistGradientBoosting on pre-match features (much worse, 1.058). Not tried: bivariate Poisson / negative binomial, daily refits.

| Test seasons (7,469 matches) | v0.1 | v0.2 | v0.2 - v0.1, paired bootstrap 95% CI |
|---|---|---|---|
| Log loss | 1.0148 | **1.0136** | -0.0012 [-0.0024, -0.0001] |
| RPS | 0.2087 | **0.2083** | -0.00042 [-0.00074, -0.00013] |
| Accuracy | 49.9% | 50.1% | |
| Goals MAE (league-mean baseline 1.309) | 1.30 | 1.301 | |
| Minus bookmaker closing log loss (5,581 matches with closing odds) | +0.0205 | +0.0191 [0.0146, 0.0236] | |

Per league, v0.2 improved E1 (-0.0039, CI excludes 0), E0, I1, SP1, D1, F1, BRA (CIs include 0), and was **worse in MLS** (+0.0040 [0.0017, 0.0064]).
The gain is real but small; the model is still clearly worse than closing odds everywhere. Value rule (average pre-closing odds, test seasons):
v0.1 1,753 bets ROI -14.9%, v0.2 1,519 bets ROI -12.4% [-19.5%, -5.0%] - still losing.
**Model + market** variant (separate, labelled; uses average PRE-CLOSING odds as an input, never closing): log loss 0.9822 vs 0.9826 for the pre-closing
market and 0.9808 for closing on the same 3,818 matches, i.e. no real gain over the market; its value rule made 98 bets, ROI +11.7% [-6.9%, +31.4%] (not significant).
PSL (season-ahead): joint DC with promoted-team prior, 50/50 with Poisson: 1.0125 vs 1.0141 (-0.0016 [-0.0046, 0.0013], not significant).

## Fixtures coverage (v0.2)
Upcoming fixtures now come from two free, key-less football-data.co.uk files, each row carrying its source URL and fetch time (shown in the dashboard):
`fixtures.csv` (22 European divisions: the 6 backtested leagues + E2, E3, EC, SP2, I2, D2, F2, B1, N1, P1, T1, G1, SC0-SC3) and
`new_league_fixtures.csv` (Brazil Serie A, MLS, Argentina, Austria, China, Denmark, Finland, Ireland, Japan, Mexico, Norway, Poland, Romania,
Sweden, Switzerland). History for the new leagues is downloaded from the same site. Only fixtures not yet kicked off are predicted; leagues with
<200 training matches are listed as "insufficient data" without probabilities. Leagues outside the walk-forward backtest are marked "untested"
and never get value flags. **Unavailable** (no free, key-less, terms-compatible dated source found): South Africa PSL fixtures, Champions League,
Europa League, internationals, women's football (ESPN's public JSON returned "Access Denied" from this server; openfootball has no 2026-27 files).

## Layout
- `ssa/ingest.py` download/cache/validate/normalize, SQLite (`data/ssa.db`: `matches`, `sources`, `predictions`).
- `ssa/models.py` Poisson (weighted MLE, attack/defence, home advantage, time decay xi=0.0019/day, small ridge), Dixon-Coles (rho by MLE given strengths, two-stage), Elo (goal-margin multiplier, +60 home), Elo->goals Poisson GLM, multinomial logistic regression on pre-match features (pre-match Elo diff, last-5 points/goals/shots-on-target, shifted), ensemble.
- `ssa/markets.py` all markets from one 7x7 score matrix; implied probability, margin removal, EV; SSI; categories.
- `ssa/backtest.py` weekly walk-forward backtest -> `reports/backtest.json`, `reports/backtest.md`.
- `ssa/predict.py` predictions for upcoming fixtures; `pipeline.py` daily pipeline; `app.py` FastAPI; `static/index.html` dashboard.
- `ssa/adapters.py` optional key-based sources (`FOOTBALL_DATA_ORG_KEY`, `ODDS_API_KEY`, `API_FOOTBALL_KEY`); disabled and failing gracefully when unset.

## Method notes
- **Ensemble (v0.1, kept as baseline)**: weights over {Poisson, DC, Elo, Logistic} chosen by grid search (step 0.1) minimising 1X2 log loss on the validation season
  (first backtest season of each league). The score matrix is a weighted mix of the matrix models, rescaled per home/draw/away region so it agrees exactly with the ensemble 1X2.
- **Model expected goals** are model outputs (expected value of the score matrix). They use shots-on-target ratings as an xG proxy; no real xG data is used.
- **Value**: implied = 1/odds, fair = implied normalised (proportional margin removal), EV = p*odds-1. "Potential value" only if the league passes the
  validation gate (beats base rates, ECE<0.03, AND not significantly worse than closing-odds probabilities) and edge>=5pp, EV>=5%, odds<=6.
- **SSI (0-100)**: reliability of the research, kept separate from outcome/probability/confidence/data quality/agreement/value fields.
  Weights: completeness 25%, freshness 15%, model agreement 25%, competition calibration 20%, decisiveness (1-entropy/ln3) 15%. See `/api/ssi`.
- **Backtest**: for every league and week of the last 4 seasons, all models are refit on matches dated strictly before that week (3-year window)
  and predict that week. Season 1 = validation, rest = test. 95% CIs from 1000 bootstrap resamples of matches. Bookmaker baseline = Pinnacle closing
  (fallback average closing) odds, margin removed. Value-rule ROI uses average pre-closing odds.
- **Predictions are immutable**: an SQLite trigger blocks updates to payload/created_at; each pipeline run inserts new timestamped rows, and later
  runs fill only the evaluation columns once results arrive.

## Data sources compared
| Source | Cost / key | Content | Licensing / notes |
|---|---|---|---|
| football-data.co.uk (used) | Free, no key | Results, shots, corners, cards, many bookmakers' pre-match + closing odds; `fixtures.csv` with upcoming odds; extra leagues (BRA, USA, ...) results + closing odds only | Free for personal/research use; credit the site. No xG. |
| football-data.org | Free tier with key (`FOOTBALL_DATA_ORG_KEY`) | Fixtures, results, standings for ~12 competitions, rate-limited | API ToS; free tier restricted competitions. Stub in `adapters.py`. |
| API-Football (api-sports) | Freemium, key (`API_FOOTBALL_KEY`) | Very broad coverage incl. South Africa PSL, lineups, stats, some odds | Commercial ToS; daily request caps on free plan. Not implemented. |
| The Odds API | Freemium, key (`ODDS_API_KEY`) | Live/upcoming odds from many bookmakers | Commercial ToS; monthly credit quota. Stub in `adapters.py`. |
| Understat | Free website, no official API | Shot-level xG for top-5 leagues + RPL | No explicit open licence; scraping may breach ToS - not used. |
| FBref (Opta/StatsBomb data) | Free website | xG and advanced stats | ToS restricts scraping/redistribution, rate limits - not used. |
| openfootball (GitHub) | Free, CC0 | Fixtures/results JSON for some leagues | Public domain; no odds/shots; coverage/updates vary. Not wired in (fixtures.csv sufficed). |

## Limitations
- Only free football-data.co.uk data; no xG, lineups, injuries, transfers or weather. South Africa PSL is **unavailable** (the `new/RSA.csv` URL served MLS data on 2026-10-10).
- Extra leagues (BRA, USA and the v0.2 additions) have no shots and no pre-closing odds in the history files, so the logistic model uses fewer features, the SOT blend falls back to goals only, and the value backtest excludes them.
- Kickoffs are converted from UK time to UTC-6.
- Elo is per league (promoted teams re-enter at the league's 20th percentile; the inheritance variant was tested and rejected).
- Weekly (not per-matchday) refits in the backtest.
- The model is **worse than closing bookmaker odds** in the backtest, and the value rule lost money. Treat outputs as research, not betting advice.

## South Africa PSL (Betway Premiership)
Results come from Wikipedia season results matrices (MediaWiki API, CC BY-SA 4.0; revision id + timestamp recorded in
`data/raw/_psl_meta.json`), parsed by `ssa/psl.py`, cross-checked against openfootball 2024-25 and each page's own league
table (`reports/psl_validation.json`). The source has no dates, odds or shots, so PSL uses a separate season-ahead
Poisson/Dixon-Coles (v0.2: joint DC with promoted-team prior) backtest and has no upcoming-fixture predictions (optional `API_FOOTBALL_KEY` stub, league 288).
football-data.co.uk `new/RSA.csv` redirects to the MLS file and is not used. Raw files are in `data/raw/` and ship in the Docker image (`COPY . .`).
