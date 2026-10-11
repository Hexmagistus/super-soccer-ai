"""Optional key-based sources. Not used unless the env var is set; never signs up. Fail gracefully."""
import os, requests

class AdapterUnavailable(Exception): pass

def _need(var):
    k = os.getenv(var)
    if not k: raise AdapterUnavailable(f"{var} not set - optional source disabled")
    return k

def football_data_org_fixtures(competition="PL"):
    """football-data.org v4 (free tier needs a key in X-Auth-Token)."""
    try:
        k = _need("FOOTBALL_DATA_ORG_KEY")
        r = requests.get(f"https://api.football-data.org/v4/competitions/{competition}/matches?status=SCHEDULED",
                         headers={"X-Auth-Token": k}, timeout=20); r.raise_for_status(); return {"ok": True, "data": r.json()}
    except Exception as e: return {"ok": False, "error": str(e)}

def odds_api_odds(sport="soccer_epl"):
    """The Odds API v4 (key required)."""
    try:
        k = _need("ODDS_API_KEY")
        r = requests.get(f"https://api.the-odds-api.com/v4/sports/{sport}/odds", params={"apiKey": k, "regions": "uk,eu", "markets": "h2h,totals"}, timeout=20)
        r.raise_for_status(); return {"ok": True, "data": r.json()}
    except Exception as e: return {"ok": False, "error": str(e)}

def api_football_psl_fixtures(season=None):
    """API-Football v3 (api-sports.io) upcoming South Africa Premiership fixtures. League id 288 = South Africa
    'Premier Soccer League'. Requires API_FOOTBALL_KEY (x-apisports-key header); disabled otherwise. Not signed up."""
    try:
        k = _need("API_FOOTBALL_KEY")
        params = {"league": int(os.getenv("API_FOOTBALL_PSL_LEAGUE_ID", "288")), "next": 50}
        if season: params["season"] = season
        r = requests.get("https://v3.football.api-sports.io/fixtures", params=params, headers={"x-apisports-key": k}, timeout=20)
        r.raise_for_status(); return {"ok": True, "data": r.json()}
    except Exception as e: return {"ok": False, "error": str(e)}

def status():
    return {"football-data.org": bool(os.getenv("FOOTBALL_DATA_ORG_KEY")), "the-odds-api": bool(os.getenv("ODDS_API_KEY")),
            "api-football": bool(os.getenv("API_FOOTBALL_KEY"))}
