"""Central configuration. API keys are optional and read from env vars only."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DB = ROOT / "data" / "ssa.db"
REPORTS = ROOT / "reports"
SETTINGS = ROOT / "data" / "settings.json"
MODEL_VERSION = "ssa-0.2.0"
USER_TZ = "Etc/GMT+6"   # UTC-6 default
SOURCE_TZ = "Europe/London"  # football-data.co.uk kickoff times are UK local time
MAIN_LEAGUES = {"E0": "England Premier League", "E1": "England Championship", "SP1": "Spain La Liga",
                "I1": "Italy Serie A", "D1": "Germany Bundesliga", "F1": "France Ligue 1"}
SEASONS = ["2122", "2223", "2324", "2425", "2526", "2627"]
EXTRA = {"BRA": "Brazil Serie A", "USA": "USA MLS"}
# v0.2 fixture coverage: more leagues whose upcoming fixtures are in football-data.co.uk fixtures.csv /
# new_league_fixtures.csv. Their history is loaded for predictions, but they are NOT part of the walk-forward
# backtest (so they are never "validated" and never get value flags).
FD_MORE = {"E2": "England League One", "E3": "England League Two", "EC": "England National League", "SP2": "Spain Segunda",
           "I2": "Italy Serie B", "D2": "Germany 2. Bundesliga", "F2": "France Ligue 2", "B1": "Belgium Pro League",
           "N1": "Netherlands Eredivisie", "P1": "Portugal Primeira Liga", "T1": "Turkey Super Lig", "G1": "Greece Super League",
           "SC0": "Scotland Premiership", "SC1": "Scotland Championship", "SC2": "Scotland League One", "SC3": "Scotland League Two"}
EXTRA_MORE = {"ARG": "Argentina Liga Profesional", "AUT": "Austria Bundesliga", "CHN": "China Super League", "DNK": "Denmark Superliga",
              "FIN": "Finland Veikkausliiga", "IRL": "Ireland Premier Division", "JPN": "Japan J1 League", "MEX": "Mexico Liga MX",
              "NOR": "Norway Eliteserien", "POL": "Poland Ekstraklasa", "ROU": "Romania Superliga", "SWE": "Sweden Allsvenskan",
              "SWZ": "Switzerland Super League"}
# new_league_fixtures.csv "Country" -> code
NEW_FIX_COUNTRY = {"Brazil": "BRA", "USA": "USA", "Argentina": "ARG", "Austria": "AUT", "China": "CHN", "Denmark": "DNK", "Finland": "FIN",
                   "Ireland": "IRL", "Japan": "JPN", "Mexico": "MEX", "Norway": "NOR", "Poland": "POL", "Romania": "ROU", "Sweden": "SWE",
                   "Switzerland": "SWZ"}
BACKTEST_LEAGUES = list(MAIN_LEAGUES) + list(EXTRA)
ALL_LEAGUES = {**MAIN_LEAGUES, **EXTRA, **FD_MORE, **EXTRA_MORE}
# Checked 2026-10-10: https://www.football-data.co.uk/new/RSA.csv redirects to the USA (MLS) file -> South Africa unavailable.
# Re-checked 2026-10-11: RSA.csv still 302/301-redirects to USA.csv (identical SHA-1) -> not used.
# PSL results come from Wikipedia season results matrices instead (ssa/psl.py).
EXTRA_UNDATED = {"PSL": "South Africa Premiership (PSL)"}
UNAVAILABLE = {"PSL fixtures": "South Africa PSL upcoming fixtures: no free key-less dated source found (Wikipedia results matrix has no dates for unplayed games; openfootball has no 2026-27 file; football-data RSA.csv redirects to MLS). Optional API_FOOTBALL_KEY adapter stub, league id 288",
               "UEFA / international / women's fixtures": "Champions League, Europa League, internationals and women's football: no free key-less source reachable (ESPN's public scoreboard JSON returns 'Access Denied' from this server; openfootball has no 2026-27 files; football-data.co.uk does not cover them)",
               "PSL odds/shots/dates": "PSL source (Wikipedia results matrix) has final scores only: no odds, shots or match dates",
               "RSA.csv": "football-data.co.uk new/RSA.csv redirects to the MLS file (checked 2026-10-10 and 2026-10-11)"}
BASE = "https://www.football-data.co.uk"
FOOTBALL_DATA_ORG_KEY = os.getenv("FOOTBALL_DATA_ORG_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
MAX_GOALS = 6
# value rule safety margins
VALUE_MIN_EDGE = 0.05
VALUE_MIN_EV = 0.05
VALUE_MAX_ODDS = 6.0
