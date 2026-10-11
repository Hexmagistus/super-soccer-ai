"""Derive every market from one score matrix, value maths, SSI and categories."""
import numpy as np
from .config import VALUE_MIN_EDGE, VALUE_MIN_EV, VALUE_MAX_ODDS
from .models import outcome_probs

def markets(M):
    n = len(M); i, j = np.indices(M.shape); tot = i + j
    H, D, A = outcome_probs(M)
    flat = [(M[a, b], f"{a}-{b}") for a in range(n) for b in range(n)]; flat.sort(reverse=True)
    out = {"1X2": {"home": H, "draw": D, "away": A},
           "double_chance": {"1X": H + D, "12": H + A, "X2": D + A},
           "draw_no_bet": {"home": H / (H + A), "away": A / (H + A)},
           "over_under": {f"{t}": {"over": M[tot > t].sum(), "under": M[tot < t].sum()} for t in (0.5, 1.5, 2.5, 3.5)},
           "btts": {"yes": M[1:, 1:].sum(), "no": 1 - M[1:, 1:].sum()},
           "team_goals": {"home": {f"over_{t}": M[i > t].sum() for t in (0.5, 1.5, 2.5)},
                          "away": {f"over_{t}": M[j > t].sum() for t in (0.5, 1.5, 2.5)}},
           "top_scores": [{"score": s, "p": p} for p, s in flat[:3]],
           "model_expected_goals": {"home": (i * M).sum(), "away": (j * M).sum(), "total": (tot * M).sum()},
           "entropy_1x2": float(-sum(p * np.log(p) for p in (H, D, A) if p > 0))}
    return _floatify(out)

def _floatify(x):
    if isinstance(x, dict): return {k: _floatify(v) for k, v in x.items()}
    if isinstance(x, list): return [_floatify(v) for v in x]
    if isinstance(x, (np.floating, float)): return round(float(x), 5)
    return x

def implied(odds):
    """Raw implied probabilities and proportional margin removal."""
    raw = np.array([1 / o for o in odds]); return raw, raw / raw.sum(), raw.sum() - 1

def ev(p, odds): return p * odds - 1

def value_check(p_model, odds, validated):
    """Potential value only if the model is validated on this competition AND edge/EV pass safety margins."""
    if any(o is None or not np.isfinite(o) for o in odds): return None
    raw, fair, margin = implied(odds); res = []
    for k, name in enumerate(["home", "draw", "away"]):
        e, edge = ev(p_model[k], odds[k]), p_model[k] - fair[k]
        flag = bool(validated and edge >= VALUE_MIN_EDGE and e >= VALUE_MIN_EV and odds[k] <= VALUE_MAX_ODDS)
        res.append({"selection": name, "odds": float(odds[k]), "implied": float(raw[k]), "fair_implied": float(fair[k]),
                    "model_p": float(p_model[k]), "edge": float(edge), "ev": float(e), "potential_value": flag})
    return {"bookmaker_margin": float(margin), "selections": res, "model_validated": bool(validated)}

SSI_WEIGHTS = {"completeness": 0.25, "freshness": 0.15, "agreement": 0.25, "calibration": 0.20, "decisiveness": 0.15}
SSI_DOC = {"completeness": "share of: both teams >=20 training matches, shots data, odds present",
           "freshness": "1 if both teams played within 14 days, linear to 0 at 120 days",
           "agreement": "1 - max total-variation distance between any two models' 1X2, scaled by 2 (TV>=0.5 -> 0)",
           "calibration": "1 - 10*ECE of ensemble on this competition in walk-forward backtest (0 if not backtested)",
           "decisiveness": "1 - entropy(1X2)/ln(3): how far from a coin-flip the outcome is"}

def ssi(factors):
    f = {k: float(np.clip(v, 0, 1)) for k, v in factors.items()}
    return round(100 * sum(SSI_WEIGHTS[k] * f[k] for k in SSI_WEIGHTS), 1), f

def agreement(per_model):
    ps = [np.asarray(p) for p in per_model]; tv = max(0.5 * np.abs(a - b).sum() for a in ps for b in ps)
    return float(max(0, 1 - 2 * tv))

def quality_grade(completeness, freshness):
    s = 0.6 * completeness + 0.4 * freshness
    return "A" if s >= 0.85 else "B" if s >= 0.65 else "C" if s >= 0.4 else "D"

def categories(mk, n_min):
    H, D, A = mk["1X2"]["home"], mk["1X2"]["draw"], mk["1X2"]["away"]; xg = mk["model_expected_goals"]["total"]; c = []
    if n_min < 10: c.append("insufficient data")
    if max(H, A) >= 0.60: c.append("strong favourite")
    if D >= 0.30: c.append("high draw probability")
    if xg >= 3.0: c.append("high scoring")
    if xg <= 2.2: c.append("low scoring")
    if mk["btts"]["yes"] >= 0.55: c.append("BTTS candidate")
    if abs(H - A) < 0.08: c.append("close match")
    if mk["entropy_1x2"] >= 0.95 * np.log(3): c.append("high uncertainty")
    return c
