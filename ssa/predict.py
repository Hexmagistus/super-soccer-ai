"""Build full prediction payloads for upcoming fixtures using all finished matches before now."""
import json, datetime as dt, numpy as np, pandas as pd
from .config import REPORTS, MODEL_VERSION, MAIN_LEAGUES, EXTRA
from .models import fit_predict, ensemble, MODELS, elo_history
from .markets import markets, value_check, ssi, agreement, quality_grade, categories, SSI_DOC

def load_bt():
    p = REPORTS / "backtest.json"; return json.loads(p.read_text()) if p.exists() else None

def team_rows(m, team, before, n=5):
    t = m[((m.home == team) | (m.away == team)) & (m.date < before) & m.hg.notna()].tail(n)
    return [{"date": str(r.date.date()), "home": r.home, "away": r.away, "score": f"{int(r.hg)}-{int(r.ag)}",
             "league": r.league} for r in t.itertuples()]

def predict_fixtures(m, fx, now=None):
    bt = load_bt(); now = pd.Timestamp(now or dt.date.today())
    w = bt["weights"] if bt else {k: 0.25 for k in MODELS}
    validated = set(bt["validated_leagues"]) if bt else set()
    created = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"); out = []
    if fx.empty: return out
    # pre-match Elo for fixtures: final ratings after all finished matches
    _, _, ratings = elo_history(m[m.hg.notna()])
    for lg, grp in fx.groupby("league"):
        L = m[(m.league == lg) & m.hg.notna()]
        ref = grp.date.min()
        train = L[(L.date < ref) & (L.date >= ref - pd.Timedelta(days=3 * 365))]
        if len(train) < 200: continue
        g = grp.copy(); g["elo_h"] = g.home.map(ratings).fillna(1500.0); g["elo_a"] = g.away.map(ratings).fillna(1500.0); g["elo_diff"] = g.elo_h - g.elo_a
        # latest available rolling-form features for each team (pre-match by construction: only past matches)
        for side, col in (("h", "home"), ("a", "away")):
            for c in ["pts5", "gf5", "ga5", "sot5", "sota5"]:
                g[f"{side}_{c}"] = g[col].map(_last_form(L, c))
        outs = fit_predict(train, g, ref)
        lgbt = (bt or {}).get("by_league", {}).get(lg)
        for r, o in zip(g.itertuples(index=False), outs):
            M, p = ensemble(o, w); mk = markets(M)
            last = lambda t: L[(L.home == t) | (L.away == t)].date.max()
            days = max((ref - last(r.home)).days, (ref - last(r.away)).days)
            nmin = min(o["n_home"], o["n_away"])
            comp = np.mean([o["n_home"] >= 20, o["n_away"] >= 20, train.hst.notna().mean() > 0.8, np.isfinite(r.oh)])
            fresh = float(np.clip(1 - (days - 14) / 106, 0, 1))
            factors = {"completeness": comp, "freshness": fresh, "agreement": agreement([o[k] for k in MODELS]),
                       "calibration": (1 - 10 * lgbt["ece"]) if lgbt else 0.0, "decisiveness": 1 - mk["entropy_1x2"] / np.log(3)}
            score, f = ssi(factors)
            pick = ["home", "draw", "away"][int(np.argmax(p))]
            val = value_check(p, [r.oh, r.od, r.oa], lg in validated and nmin >= 20) if np.isfinite(r.oh) else None
            out.append({"match_id": r.match_id, "league": lg, "league_name": MAIN_LEAGUES.get(lg, EXTRA.get(lg, lg)),
                "date": str(r.date.date()), "kickoff_utc6": r.kickoff_utc6, "home": r.home, "away": r.away,
                "created_at": created, "model_version": MODEL_VERSION,
                "predicted_outcome": pick, "probability": float(max(p)),
                "confidence": "high" if max(p) >= 0.6 else "medium" if max(p) >= 0.45 else "low",
                "data_quality": quality_grade(comp, fresh), "model_agreement": factors["agreement"],
                "ssi": score, "ssi_factors": f, "markets": mk, "score_matrix": np.round(M, 5).tolist(),
                "per_model_1x2": {k: [round(float(x), 4) for x in o[k]] for k in MODELS},
                "categories": categories(mk, nmin), "value": val,
                "odds": {"home": _f(r.oh), "draw": _f(r.od), "away": _f(r.oa), "over25": _f(r.o25), "under25": _f(r.u25),
                         "source": "football-data.co.uk fixtures.csv (average pre-match odds)"},
                "notes": ["Model expected goals are model outputs, not shot-based xG (no real xG data source is used).",
                          f"Most likely score has only {mk['top_scores'][0]['p']:.1%} probability."],
                "form_home": team_rows(m, r.home, ref), "form_away": team_rows(m, r.away, ref),
                "h2h": [x for x in team_rows(m, r.home, ref, 400) if r.away in (x["home"], x["away"])][-6:],
                "training_matches": int(len(train)), "team_matches": {"home": int(o["n_home"]), "away": int(o["n_away"])}})
    return out

def _f(x): return float(x) if x is not None and np.isfinite(x) else None

def _last_form(L, c):
    d = {}
    for side in "ha":
        col = "home" if side == "h" else "away"
        s = L[[col, "date"]].assign(v=L[f"{side}_{c}"]); d[side] = s
    # use features as of each team's most recent match (shifted, so excludes that match); good enough & leak-free
    long = pd.concat([d["h"].rename(columns={"home": "team"}), d["a"].rename(columns={"away": "team"})]).sort_values("date")
    return long.dropna(subset=["v"]).groupby("team").v.last().to_dict()

SSI_DOCS = SSI_DOC
