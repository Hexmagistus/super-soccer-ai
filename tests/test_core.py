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
    src = inspect.getsource(bt.run_walkforward); assert "L.date < start" in src
