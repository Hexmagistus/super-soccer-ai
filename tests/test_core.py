import numpy as np, pandas as pd, pytest
from ssa.models import score_matrix, outcome_probs, add_features, PoissonModel, ensemble
from ssa.markets import markets, implied, ev, value_check

def test_matrix_sums_to_one():
    for lh, la, rho in [(1.5, 1.1, 0), (2.8, 0.4, -0.1), (0.3, 0.3, 0.1)]:
        M = score_matrix(lh, la, rho); assert M.shape == (7, 7); assert abs(M.sum() - 1) < 1e-12; assert (M >= 0).all()

def test_market_consistency():
    mk = markets(score_matrix(1.6, 1.2, -0.05)); x = mk["1X2"]
    assert abs(x["home"] + x["draw"] + x["away"] - 1) < 1e-4
    assert abs(mk["double_chance"]["1X"] - x["home"] - x["draw"]) < 1e-4
    assert abs(mk["draw_no_bet"]["home"] + mk["draw_no_bet"]["away"] - 1) < 1e-4
    for t, v in mk["over_under"].items(): assert abs(v["over"] + v["under"] - 1) < 1e-4
    ou = [mk["over_under"][k]["over"] for k in ("0.5", "1.5", "2.5", "3.5")]; assert ou == sorted(ou, reverse=True)
    assert abs(mk["btts"]["yes"] + mk["btts"]["no"] - 1) < 1e-4
    assert mk["top_scores"][0]["p"] < 0.20

def test_ev_maths():
    raw, fair, margin = implied([2.0, 3.5, 4.0])
    assert np.allclose(raw, [0.5, 1 / 3.5, 0.25]); assert abs(fair.sum() - 1) < 1e-12; assert abs(margin - (raw.sum() - 1)) < 1e-12
    assert abs(ev(0.55, 2.0) - 0.10) < 1e-12; assert ev(0.5, 2.0) == 0
    v = value_check(np.array([0.6, 0.25, 0.15]), [2.0, 3.5, 4.0], validated=False)
    assert not any(s["potential_value"] for s in v["selections"])  # unvalidated model never flags value
    v = value_check(np.array([0.6, 0.25, 0.15]), [2.0, 3.5, 4.0], validated=True)
    assert v["selections"][0]["potential_value"] and not v["selections"][2]["potential_value"]

def test_ensemble_matrix_matches_1x2():
    o = {"p_lh": 1.4, "p_la": 1.0, "dc_rho": -0.06, "e_lh": 1.5, "e_la": 0.9, "poisson": [0.45, 0.28, 0.27],
         "dc": [0.44, 0.29, 0.27], "elo": [0.5, 0.25, 0.25], "logit": [0.4, 0.3, 0.3]}
    M, p = ensemble(o, {"poisson": .3, "dc": .3, "elo": .2, "logit": .2})
    assert abs(M.sum() - 1) < 1e-9 and np.allclose(outcome_probs(M), p)

def _toy():
    rng = np.random.default_rng(0); teams = list("ABCDEF"); rows = []
    d = pd.Timestamp("2024-01-01")
    for k in range(120):
        h, a = rng.choice(teams, 2, replace=False)
        rows.append({"league": "X", "date": d + pd.Timedelta(days=k), "home": h, "away": a, "hg": float(rng.poisson(1.5)), "ag": float(rng.poisson(1.1)),
                     "hst": float(rng.poisson(4)), "ast": float(rng.poisson(3))})
    return pd.DataFrame(rows)

def test_no_leakage_features():
    """Changing a match's result must not change ANY pre-match feature of that match or earlier matches."""
    m = _toy(); f1 = add_features(m)
    m2 = m.copy(); m2.loc[60, ["hg", "ag", "hst", "ast"]] = [9.0, 0.0, 20.0, 0.0]; f2 = add_features(m2)
    cols = ["elo_h", "elo_a", "h_pts5", "a_pts5", "h_gf5", "a_gf5", "h_sot5", "a_sot5"]
    pd.testing.assert_frame_equal(f1.loc[:60, cols], f2.loc[:60, cols])
    assert not f1.loc[61:, cols].equals(f2.loc[61:, cols])  # sanity: later matches do change

def test_no_leakage_model_fit():
    """Poisson fit uses only rows passed in; future rows cannot influence it."""
    m = _toy(); ref = m.date.iloc[80]; tr = m[m.date < ref]
    p1 = PoissonModel().fit(tr, ref).lambdas("A", "B")
    m.loc[m.date >= ref, "hg"] = 9; p2 = PoissonModel().fit(m[m.date < ref], ref).lambdas("A", "B")
    assert np.allclose(p1, p2)

def test_backtest_train_strictly_before():
    import inspect, ssa.backtest as bt
    src = inspect.getsource(bt._walk_league); assert "L.date < start" in src

WIKI_SAMPLE = """==Results==
{{#invoke:sports results|main
| update = complete
|name_AAA=[[Alpha F.C.|Alpha]]
|name_BBB=[[Lamontville Golden Arrows F.C.|Lamontville Golden Arrows]]
|name_CCC=Gamma
|match_AAA_BBB=2–1 |match_AAA_CCC=<s>1–0</s>
|match_BBB_AAA=[[Derby|0-3]]
|match_BBB_CCC={{small|30 Jan}}
|match_CCC_AAA=
|match_CCC_BBB=1–1
}}"""

def test_psl_parser_excludes_struck_and_unplayed():
    from ssa.psl import parse
    rows, excl, teams = parse(WIKI_SAMPLE, "2024–25")
    assert teams == ["Alpha", "Gamma", "Golden Arrows"]
    got = {(r["home"], r["away"]): (r["hg"], r["ag"]) for r in rows}
    assert got == {("Alpha", "Golden Arrows"): (2, 1), ("Golden Arrows", "Alpha"): (0, 3), ("Gamma", "Golden Arrows"): (1, 1)}
    assert len(excl) == 2 and all(r["season"] == "2024-25" for r in rows)

def test_openfootball_parser():
    from ssa.psl import parse_openfootball
    txt = "  Sat Sep 14 2024\n    17:30  Marumo Gallants         v Kaizer Chiefs            1-2 (1-1)\n    15:00  Royal AM                v Cape Town City FC        [cancelled]\n  Sun Sep 15\n    15:00  Richards Bay FC         v TS Galaxy                1-0 (1-0)\n"
    df = parse_openfootball(txt)
    assert df.to_dict("records") == [{"date": "2024-09-14", "home": "Marumo Gallants", "away": "Kaizer Chiefs", "hg": 1, "ag": 2},
                                     {"date": "2024-09-15", "home": "Richards Bay", "away": "TS Galaxy", "hg": 1, "ag": 0}]

# ---- v0.2 components ----
from ssa.models import DixonColesJoint, ShotsModel, elo_history, ensemble_v2, promoted_flags
from ssa.stack import fit_pool, recal, fit_recal, log_pool

def _sim(n_days=900, seed=1, rho=-0.1):
    rng = np.random.default_rng(seed); teams = [f"T{i}" for i in range(10)]; att = rng.normal(0, .3, 10); rows = []
    d0 = pd.Timestamp("2022-01-01")
    for k in range(n_days):
        i, j = rng.choice(10, 2, replace=False); lh, la = np.exp(.25 + .2 + att[i] - att[j] * .5), np.exp(.25 + att[j] - att[i] * .5)
        M = score_matrix(lh, la, rho); c = rng.choice(49, p=M.ravel()); rows.append({"league": "X", "date": d0 + pd.Timedelta(days=k),
            "home": teams[i], "away": teams[j], "hg": float(c // 7), "ag": float(c % 7), "hst": float(rng.poisson(4 * lh)), "ast": float(rng.poisson(4 * la))})
    return pd.DataFrame(rows)

def test_dcj_gradient_and_rho_recovery():
    m = _sim(3000); ref = m.date.max() + pd.Timedelta(days=1)
    J = DixonColesJoint(xi=0.0, ridge=0.01, promo=False).fit(m, ref)
    assert -0.2 < J.rho < -0.02 and abs(J.ha - 0.2) < 0.08

def test_dcj_promoted_prior_for_unseen_team():
    m = _sim(900); ref = m.date.max() + pd.Timedelta(days=1)
    J = DixonColesJoint().fit(m, ref); lh, la = J.lambdas("NEWTEAM", "T0")
    assert np.isclose(np.log(lh), J.mu + J.ha + J.c_att + J.de[J.idx["T0"]])
    late = m.copy(); late.loc[late.index > 600, "home"] = late.loc[late.index > 600, "home"].replace("T1", "P1")
    assert promoted_flags(late).get("P1") and not promoted_flags(late).get("T0")

def test_shots_model_leak_free_and_flags():
    m = _sim(600); ref = m.date.iloc[400]; tr = m[m.date < ref]
    a = ShotsModel().fit(tr, ref).lambdas("T0", "T1"); m.loc[m.date >= ref, ["hst", "ast"]] = 50
    assert np.allclose(a, ShotsModel().fit(m[m.date < ref], ref).lambdas("T0", "T1"))
    assert not ShotsModel().fit(tr.assign(hst=np.nan), ref).ok

def test_elo_promo_inherit_is_pre_match():
    m = _sim(400); m["season"] = np.where(m.index < 200, "a", "b")
    h1, a1, _ = elo_history(m, promo_inherit=True); m2 = m.copy(); m2.loc[300, ["hg", "ag"]] = [9.0, 0.0]
    h2, a2, _ = elo_history(m2, promo_inherit=True); assert np.allclose(h1[:301], h2[:301]) and np.allclose(a1[:301], a2[:301])

def test_stack_pool_and_recal():
    rng = np.random.default_rng(0); y = rng.integers(0, 3, 2000); good = np.full((2000, 3), .2); good[np.arange(2000), y] = .6
    noise = rng.dirichlet([1, 1, 1], 2000); w = fit_pool([good, noise], y); assert w[0] > 0.8
    P = recal(good, 1.0, 0.0); assert np.allclose(P, good)
    T, d = fit_recal(good, y); assert np.allclose(recal(good, T, d).sum(1), 1)
    assert np.allclose(log_pool([good, good], [0.5, 0.5]), good)

def test_ensemble_v2_matrix_matches_1x2():
    o = {"j_lh": 1.4, "j_la": 1.0, "j_rho": -0.05, "s_lh": 1.6, "s_la": 0.9, "logit": [0.4, 0.3, 0.3]}
    cfg = {"alpha": 0.6, "w_core": 0.77, "w_logit": 0.23, "T": 0.9, "d": 0.1}
    M, p = ensemble_v2(o, cfg); assert abs(M.sum() - 1) < 1e-9 and np.allclose(outcome_probs(M), p)
    M2, p2 = ensemble_v2({**o, "s_lh": None, "s_la": None}, cfg); assert abs(p2.sum() - 1) < 1e-9

def test_new_league_fixtures_parse(tmp_path, monkeypatch):
    import ssa.ingest as ing
    (tmp_path / "new_league_fixtures.csv").write_text("Country,League,Date,Time,Home,Away,AvgH,AvgD,AvgA\nBrazil,Serie A,10/10/2026,20:00,Flamengo RJ,Palmeiras,2.1,3.2,3.6\nNarnia,X,10/10/2026,20:00,A,B,2,3,4\n")
    monkeypatch.setattr(ing, "RAW", tmp_path); f = ing.load_fixtures()
    assert list(f.league) == ["BRA"] and f.kickoff_utc6.iloc[0] == "2026-10-10 13:00" and f.fixture_source.iloc[0].endswith("new_league_fixtures.csv")


def test_fixtures_exclude_past_kickoffs(monkeypatch):
    import datetime as dt, app
    now = dt.datetime.now(dt.timezone.utc); f = lambda d: (now + d).astimezone(app.UTC6).strftime("%Y-%m-%d %H:%M")
    base = {"league": "E0", "date": "2000-01-01", "home": "A", "away": "B", "value": None, "odds": None}
    rows = [{**base, "match_id": "past", "kickoff_utc6": f(dt.timedelta(hours=-2))},
            {**base, "match_id": "future", "kickoff_utc6": f(dt.timedelta(hours=2))},
            {**base, "match_id": "old_dateonly", "kickoff_utc6": None}]
    monkeypatch.setattr(app, "latest_preds", lambda: [dict(r) for r in rows])
    assert [x["match_id"] for x in app.fixtures()] == ["future"]
    assert [x["match_id"] for x in app.upcoming_preds()] == ["future"]
    assert not app.is_upcoming(rows[0], now) and app.is_upcoming(rows[1], now)
