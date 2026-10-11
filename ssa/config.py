"""Central configuration. API keys are optional and read from env vars only."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DB = ROOT / "data" / "ssa.db"
REPORTS = ROOT / "reports"
SETTINGS = ROOT / "data" / "settings.json"
MODEL_VERSION = "ssa-0.1.0"
USER_TZ = "Etc/GMT+6"   # UTC-6 default
SOURCE_TZ = "Europe/London"  # football-data.co.uk kickoff times are UK local time
MAIN_LEAGUES = {"E0": "England Premier League", "E1": "England Championship", "SP1": "Spain La Liga",
                "I1": "Italy Serie A", "D1": "Germany Bundesliga", "F1": "France Ligue 1"}
SEASONS = ["2122", "2223", "2324", "2425", "2526", "2627"]
EXTRA = {"BRA": "Brazil Serie A", "USA": "USA MLS"}
# Checked 2026-10-10: https://www.football-data.co.uk/new/RSA.csv redirects to the USA (MLS) file -> South Africa unavailable.
UNAVAILABLE = {"RSA": "South Africa PSL: no football-data.co.uk file (RSA.csv URL served MLS data on 2026-10-10)"}
BASE = "https://www.football-data.co.uk"
FOOTBALL_DATA_ORG_KEY = os.getenv("FOOTBALL_DATA_ORG_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
MAX_GOALS = 6
# value rule safety margins
VALUE_MIN_EDGE = 0.05
VALUE_MIN_EV = 0.05
VALUE_MAX_ODDS = 6.0
