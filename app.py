"""FastAPI backend for SUPER SOCCER AI. Run: .venv/bin/uvicorn app:app --port 8000"""
import json, sqlite3
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from ssa.config import DB, REPORTS, SETTINGS, ROOT, MAIN_LEAGUES, EXTRA, EXTRA_UNDATED, UNAVAILABLE, MODEL_VERSION, VALUE_MIN_EDGE, VALUE_MIN_EV, VALUE_MAX_ODDS
from ssa.markets import SSI_DOC, SSI_WEIGHTS
from ssa import adapters

app = FastAPI(title="SUPER SOCCER AI", description="Research the Game. Predict the Score. Measure the Evidence.")
DEFAULT_SETTINGS = {"leagues": list(MAIN_LEAGUES) + list(EXTRA) + list(EXTRA_UNDATED), "timezone": "UTC-6 (Etc/GMT+6)", "betting_module": False}

def q(sql, args=()):
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    try: return [dict(r) for r in con.execute(sql, args).fetchall()]
    finally: con.close()

def latest_preds():
    rows = q("""SELECT payload FROM predictions p WHERE id = (SELECT MAX(id) FROM predictions WHERE match_id=p.match_id)
                AND evaluated_at IS NULL ORDER BY match_date""")
    return [json.loads(r["payload"]) for r in rows]

@app.get("/")
def index(): return FileResponse(ROOT / "static" / "index.html")

@app.get("/api/status")
def status():
    src = q("SELECT * FROM sources ORDER BY file")
    counts = q("SELECT league, season, COUNT(*) n, MIN(date) first, MAX(date) last FROM matches GROUP BY league, season ORDER BY league, season")
    preds = latest_preds()
    return {"model_version": MODEL_VERSION, "sources": src, "counts": counts, "unavailable": UNAVAILABLE,
            "leagues": {**MAIN_LEAGUES, **EXTRA, **EXTRA_UNDATED},
            "psl": _psl_status(), "optional_api_keys": adapters.status(),
            "mode": "upcoming" if preds else "historical", "n_upcoming": len(preds),
            "predictions_created_at": max((p["created_at"] for p in preds), default=None),
            "fixtures_source": "https://www.football-data.co.uk/fixtures.csv (main 6 leagues only; no free fixtures for BRA/USA/PSL here - PSL upcoming fixtures unavailable)"}

def _psl_status():
    try: counts = q("SELECT season, COUNT(*) n, MIN(data_status) data_status, MIN(source_url) source_url FROM psl_matches GROUP BY season ORDER BY season")
    except sqlite3.OperationalError: counts = []
    v = REPORTS / "psl_validation.json"
    return {"name": EXTRA_UNDATED["PSL"], "results_by_season": counts, "fixtures": "unavailable (no free key-less source; set API_FOOTBALL_KEY to enable adapter stub)",
            "source": "Wikipedia season articles, Results matrix, via MediaWiki API (CC BY-SA 4.0)", "has_dates": False, "has_odds": False, "has_shots": False,
            "validation": json.loads(v.read_text()) if v.exists() else None}

@app.get("/api/psl")
def psl_info(): return _psl_status()

@app.get("/api/fixtures")
def fixtures(league: str = None, sort: str = "kickoff", desc: bool = False):
    p = latest_preds()
    if league: p = [x for x in p if x["league"] == league]
    key = {"kickoff": lambda x: x["kickoff_utc6"] or x["date"], "league": lambda x: (x["league"], x["kickoff_utc6"] or ""),
           "probability": lambda x: x["probability"], "ssi": lambda x: x["ssi"],
           "goals": lambda x: x["markets"]["model_expected_goals"]["total"], "quality": lambda x: x["data_quality"]}.get(sort)
    if key: p.sort(key=key, reverse=desc)
    for x in p: x.pop("score_matrix", None)
    return p

@app.get("/api/match/{mid}")
def match(mid: str):
    r = q("SELECT payload, created_at FROM predictions WHERE match_id=? ORDER BY id DESC", (mid,))
    if not r: raise HTTPException(404, "no prediction for this match")
    d = json.loads(r[0]["payload"]); d["prediction_history"] = [x["created_at"] for x in r]; return d

@app.get("/api/performance")
def performance():
    p = REPORTS / "backtest.json"
    if not p.exists(): return {"available": False}
    d = json.loads(p.read_text()); d["available"] = True; return d

@app.get("/api/value")
def value():
    s = get_settings(); out = []
    for x in latest_preds():
        if x.get("value"): out.append({k: x[k] for k in ("match_id", "league", "kickoff_utc6", "home", "away", "value", "odds")})
    return {"betting_module_enabled": s["betting_module"], "rows": out if s["betting_module"] else [],
            "rule": {"min_edge": VALUE_MIN_EDGE, "min_ev": VALUE_MIN_EV, "max_odds": VALUE_MAX_ODDS},
            "disclaimer": "Potential value is a statistical estimate, not a guarantee. Bookmaker closing prices beat this model in backtests."}

@app.get("/api/ssi")
def ssi_doc(): return {"weights": SSI_WEIGHTS, "factors": SSI_DOC}

@app.get("/api/settings")
def get_settings():
    return {**DEFAULT_SETTINGS, **(json.loads(SETTINGS.read_text()) if SETTINGS.exists() else {})}

@app.post("/api/settings")
def set_settings(s: dict = Body(...)):
    cur = get_settings(); cur.update({k: v for k, v in s.items() if k in DEFAULT_SETTINGS}); SETTINGS.write_text(json.dumps(cur)); return cur
