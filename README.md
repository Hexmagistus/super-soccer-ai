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

## Layout
- `ssa/ingest.py` download/cache/validate/normalize, SQLite (`data/ssa.db`: `matches`, `sources`, `predictions`).
- `ssa/models.py` Poisson (weighted MLE, attack/defence, home advantage, time decay xi=0.0019/day, small ridge), Dixon-Coles (rho by MLE given strengths, two-stage), Elo (goal-margin multiplier, +60 home), Elo->goals Poisson GLM, multinomial logistic regression on pre-match features (pre-match Elo diff, last-5 points/goals/shots-on-target, shifted), ensemble.
- `ssa/markets.py` all markets from one 7x7 score matrix; implied probability, margin removal, EV; SSI; categories.
- `ssa/backtest.py` weekly walk-forward backtest -> `reports/backtest.json`, `reports/backtest.md`.
- `ssa/predict.py` predictions for upcoming fixtures; `pipeline.py` daily pipeline; `app.py` FastAPI; `static/index.html` dashboard.
- `ssa/adapters.py` optional key-based sources (`FOOTBALL_DATA_ORG_KEY`, `ODDS_API_KEY`, `API_FOOTBALL_KEY`); disabled and failing gracefully when unset.

## Method notes
- **Ensemble**: weights over {Poisson, DC, Elo, Logistic} chosen by grid search (step 0.1) minimising 1X2 log loss on the validation season
  (first backtest season of each league). The score matrix is a weighted mix of the matrix models, rescaled per home/draw/away region so it agrees exactly with the ensemble 1X2.
- **Model expected goals** are model outputs (expected value of the score matrix), not shot-based xG.
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
- Extra leagues (BRA, USA) have no shots and no pre-closing odds, so the logistic model uses fewer features and the value backtest excludes them; no free upcoming fixtures for them here.
- Upcoming fixtures come only from `fixtures.csv` (main 6 leagues used). Kickoffs are converted from UK time to UTC-6.
- Elo is per league (promoted/relegated teams re-enter at the league's 20th percentile); unseen teams get league-average strength and are flagged "insufficient data".
- Dixon-Coles rho is fitted in a second stage, not jointly; weekly (not per-matchday) refits in the backtest.
- The model is **worse than closing bookmaker odds** in the backtest, and the value rule lost money. Treat outputs as research, not betting advice.

## South Africa PSL (Betway Premiership)
Results come from Wikipedia season results matrices (MediaWiki API, CC BY-SA 4.0; revision id + timestamp recorded in
`data/raw/_psl_meta.json`), parsed by `ssa/psl.py`, cross-checked against openfootball 2024-25 and each page's own league
table (`reports/psl_validation.json`). The source has no dates, odds or shots, so PSL uses a separate season-ahead
Poisson/Dixon-Coles backtest and has no upcoming-fixture predictions (optional `API_FOOTBALL_KEY` stub, league 288).
football-data.co.uk `new/RSA.csv` redirects to the MLS file and is not used. Raw files are in `data/raw/` and ship in the Docker image (`COPY . .`).
