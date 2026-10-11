"""Strict chronological walk-forward backtest. For each league and each calendar week of the backtest
seasons, all models are refit on matches dated BEFORE that week's first day and then predict that week.
(Weekly refit ~= matchday refit; a few midweek rounds share a refit with the preceding weekend, which only
makes the model slightly staler, never leaky.)"""
import json, itertools, numpy as np, pandas as pd
from .config import REPORTS, MAIN_LEAGUES, EXTRA, BACKTEST_LEAGUES, VALUE_MIN_EDGE, VALUE_MIN_EV, VALUE_MAX_ODDS
from .models import fit_predict, ensemble, ensemble_v2, v2_lambdas, MODELS, outcome_probs, score_matrix, add_features
from .stack import fit_pool, fit_recal, log_pool, _ll
from .markets import implied

RNG = np.random.default_rng(42)
WINDOW_DAYS = 3 * 365

def bt_seasons(m, league):
    s = sorted(m[m.league == league].season.unique())
    return s[-4:]  # first = validation (ensemble weights), rest = test

def _walk_league(args):
    m, lg = args; rows = []
    seasons = bt_seasons(m, lg); L = m[m.league == lg]
    target = L[L.season.isin(seasons) & L.hg.notna()]
    for wk, grp in target.groupby(target.date.dt.to_period("W-SUN")):
        start = wk.start_time
        train = L[(L.date < start) & (L.date >= start - pd.Timedelta(days=WINDOW_DAYS)) & L.hg.notna()]
        if len(train) < 200: continue
        for r, o in zip(grp.itertuples(index=False), fit_predict(train, grp, start)):
            o.update({"match_id": r.match_id, "league": lg, "season": r.season, "date": str(r.date.date()),
                      "home": r.home, "away": r.away, "hg": int(r.hg), "ag": int(r.ag), "val": r.season == seasons[0],
                      "ch": r.ch, "cd": r.cd, "ca": r.ca, "oh": r.oh, "od": r.od, "oa": r.oa,
                      "base": train.assign(res=np.sign(train.hg - train.ag)).res.value_counts(normalize=True).reindex([1, 0, -1]).fillna(0).values,
                      "train_mean_goals": float((train.hg + train.ag).mean())})
            rows.append(o)
    print("backtested", lg, len(rows), flush=True)
    return rows

def run_walkforward(m, processes=8):
    """Leagues are independent, so they run in parallel; inside each league training rows are strictly
    earlier than the predicted week (see _walk_league: L.date < start)."""
    from multiprocessing import get_context
    jobs = [(m, lg) for lg in m.league.unique()]
    if processes > 1:
        with get_context("fork").Pool(min(processes, len(jobs))) as p: parts = p.map(_walk_league, jobs)
    else: parts = [_walk_league(j) for j in jobs]
    return [o for part in parts for o in part]

def y_of(o): return 0 if o["hg"] > o["ag"] else 1 if o["hg"] == o["ag"] else 2

def logloss(p, y): return -np.log(max(p[y], 1e-12))
def brier(p, y): e = np.zeros(3); e[y] = 1; return float(((np.asarray(p) - e) ** 2).sum())
def rps(p, y): e = np.zeros(3); e[y] = 1; c = np.cumsum(p)[:2] - np.cumsum(e)[:2]; return float((c ** 2).sum() / 2)

def choose_weights(rows):
    val = [o for o in rows if o["val"]]; best = None
    grid = [w for w in itertools.product(np.arange(0, 1.01, 0.1), repeat=4) if abs(sum(w) - 1) < 1e-9]
    P = {k: np.array([o[k] for o in val]) for k in MODELS}; y = np.array([y_of(o) for o in val])
    for w in grid:
        p = sum(wi * P[k] for wi, k in zip(w, MODELS)); ll = -np.mean(np.log(p[np.arange(len(y)), y]))
        if best is None or ll < best[0]: best = (ll, w)
    return dict(zip(MODELS, [round(float(x), 2) for x in best[1]])), float(best[0]), len(val)

def ci(x, n=1000, digits=4):
    """Bootstrap 95% CI of the mean. For paired differences pass the per-match differences (paired bootstrap)."""
    x = np.asarray(x, float)
    if len(x) == 0: return [None, None]
    b = [x[RNG.integers(0, len(x), len(x))].mean() for _ in range(n)]
    return [round(float(np.percentile(b, 2.5)), digits), round(float(np.percentile(b, 97.5)), digits)]

ALPHAS = [1.0, 0.8, 0.7, 0.6, 0.5, 0.4, 0.2]

def _v2_core(o, a): return outcome_probs(score_matrix(*v2_lambdas(o, a), o["j_rho"]))

def fair_prematch(o):
    odds = [o["oh"], o["od"], o["oa"]]; return implied(odds)[1] if all(np.isfinite(odds)) else None

def choose_v2(rows):
    """All on the VALIDATION season only: (1) alpha of the DCJ/SOT lambda blend by log loss, (2) linear-pool weights
    of core + logistic by log loss, (3) temperature T and draw shift d by log loss, (4) separately, the log-pool
    weights of the 'model + market' variant (v0.2 model and average PRE-CLOSING odds)."""
    val = [o for o in rows if o["val"]]; y = np.array([y_of(o) for o in val])
    alpha = min(ALPHAS, key=lambda a: _ll(np.array([_v2_core(o, a) for o in val]), y))
    C = np.array([_v2_core(o, alpha) for o in val]); Lg = np.array([o["logit"] for o in val])
    w = fit_pool([C, Lg], y); T, d = fit_recal(w[0] * C + w[1] * Lg, y)
    cfg = {"alpha": float(alpha), "w_core": float(w[0]), "w_logit": float(w[1]), "T": T, "d": d}
    P = np.array([ensemble_v2(o, cfg)[1] for o in val]); cfg["val_log_loss"] = float(_ll(P, y)); cfg["n_val"] = len(val)
    mk = [fair_prematch(o) for o in val]; ok = np.array([m is not None for m in mk])
    from scipy.optimize import minimize
    MK = np.array([m for m in mk if m is not None])
    r = minimize(lambda z: _ll(log_pool([P[ok], MK], z), y[ok]), [0.5, 0.5], method="Nelder-Mead")
    cfg["market"] = {"w_model": float(r.x[0]), "w_market": float(r.x[1]), "val_log_loss": float(r.fun), "n_val": int(ok.sum()),
                     "val_market_only_log_loss": float(_ll(MK, y[ok])), "odds": "average pre-closing odds (football-data Avg/BbAv columns), NOT closing"}
    return cfg

def evaluate(rows, w, cfg=None):
    test = [o for o in rows if not o["val"]]
    for o in test:
        M, p = ensemble(o, w); o["ens_v01"] = p
        if cfg: M, p = ensemble_v2(o, cfg)
        o["ens"] = p; i, j = np.unravel_index(M.argmax(), M.shape)
        o["top_score"] = f"{i}-{j}"; o["top_p"] = float(M.max())
        o["exp_goals"] = float((np.indices(M.shape).sum(0) * M).sum())
        bk = [o["ch"], o["cd"], o["ca"]]
        o["book"] = implied(bk)[1] if all(np.isfinite(bk)) else None
        fm = fair_prematch(o); o["book_pre"] = fm
        o["ens_market"] = log_pool([np.asarray(p)[None, :], fm[None, :]], [cfg["market"]["w_model"], cfg["market"]["w_market"]])[0] if (cfg and fm is not None) else None
    return test

def metric_block(sub, key):
    y = [y_of(o) for o in sub]; P = [o[key] for o in sub]
    ll = [logloss(p, t) for p, t in zip(P, y)]; br = [brier(p, t) for p, t in zip(P, y)]; rp = [rps(p, t) for p, t in zip(P, y)]
    acc = [float(np.argmax(p) == t) for p, t in zip(P, y)]
    return {"n": len(sub), "accuracy": round(float(np.mean(acc)), 4), "accuracy_ci": ci(acc), "log_loss": round(float(np.mean(ll)), 4), "log_loss_ci": ci(ll),
            "brier": round(float(np.mean(br)), 4), "brier_ci": ci(br), "rps": round(float(np.mean(rp)), 4), "rps_ci": ci(rp)}

def calibration(sub, key="ens", bins=10):
    ps, hit = [], []
    for o in sub:
        y = y_of(o)
        for k in range(3): ps.append(o[key][k]); hit.append(float(k == y))
    ps, hit = np.array(ps), np.array(hit); edges = np.linspace(0, 1, bins + 1); out = []; ece = 0
    for a, b in zip(edges[:-1], edges[1:]):
        m = (ps >= a) & (ps < b) if b < 1 else (ps >= a)
        if m.sum():
            out.append({"bin": f"{a:.1f}-{b:.1f}", "n": int(m.sum()), "mean_pred": round(float(ps[m].mean()), 4), "observed": round(float(hit[m].mean()), 4)})
            ece += m.sum() / len(ps) * abs(ps[m].mean() - hit[m].mean())
    return out, round(float(ece), 4)

def summarize(sub):
    res = {"n_matches": len(sub)}
    for o in sub: o["home_always"] = np.array([1.0, 0, 0])
    for k in MODELS + ["ens", "base"] + (["ens_v01"] if "ens_v01" in sub[0] else []): res[k] = metric_block(sub, k)
    if "ens_v01" in sub[0]:
        d = [logloss(o["ens"], y_of(o)) - logloss(o["ens_v01"], y_of(o)) for o in sub]; dr = [rps(o["ens"], y_of(o)) - rps(o["ens_v01"], y_of(o)) for o in sub]
        res["v02_minus_v01"] = {"log_loss": round(float(np.mean(d)), 4), "log_loss_ci": ci(d), "rps": round(float(np.mean(dr)), 5), "rps_ci": ci(dr, digits=5)}
    ha = [float(y_of(o) == 0) for o in sub]; res["home_always"] = {"n": len(sub), "accuracy": round(float(np.mean(ha)), 4), "accuracy_ci": ci(ha), "note": "log loss undefined (p=0 events)"}
    bsub = [o for o in sub if o["book"] is not None]
    if bsub:
        for o in bsub: o["bookp"] = o["book"]
        res["bookmaker_closing"] = metric_block(bsub, "bookp"); res["ensemble_on_same_matches"] = metric_block(bsub, "ens")
        d = [logloss(o["ens"], y_of(o)) - logloss(o["book"], y_of(o)) for o in bsub]
        res["ens_minus_book_logloss"] = {"mean": round(float(np.mean(d)), 4), "ci": ci(d)}
        dr = [rps(o["ens"], y_of(o)) - rps(o["book"], y_of(o)) for o in bsub]; res["ens_minus_book_rps"] = {"mean": round(float(np.mean(dr)), 5), "ci": ci(dr, digits=5)}
        if "ens_v01" in bsub[0]:
            res["ens_v01_on_same_matches"] = metric_block(bsub, "ens_v01")
            d = [logloss(o["ens_v01"], y_of(o)) - logloss(o["book"], y_of(o)) for o in bsub]; res["ens_v01_minus_book_logloss"] = {"mean": round(float(np.mean(d)), 4), "ci": ci(d)}
    msub = [o for o in sub if o.get("ens_market") is not None and o["book"] is not None]
    if msub:
        for o in msub: o["bookp"] = o["book"]; o["bookpre"] = o["book_pre"]
        res["model_plus_market"] = metric_block(msub, "ens_market"); res["bookmaker_prematch_avg"] = metric_block(msub, "bookpre")
        res["bookmaker_closing_on_market_subset"] = metric_block(msub, "bookp")
        d = [logloss(o["ens_market"], y_of(o)) - logloss(o["book"], y_of(o)) for o in msub]; res["model_plus_market_minus_closing_logloss"] = {"mean": round(float(np.mean(d)), 4), "ci": ci(d)}
        d = [logloss(o["ens_market"], y_of(o)) - logloss(o["book_pre"], y_of(o)) for o in msub]; res["model_plus_market_minus_prematch_logloss"] = {"mean": round(float(np.mean(d)), 4), "ci": ci(d)}
    d = [logloss(o["ens"], y_of(o)) - logloss(o["base"], y_of(o)) for o in sub]
    res["ens_minus_base_logloss"] = {"mean": round(float(np.mean(d)), 4), "ci": ci(d)}
    ex = [float(o["top_score"] == f"{o['hg']}-{o['ag']}") for o in sub]
    res["exact_score_hit_rate"] = {"rate": round(float(np.mean(ex)), 4), "ci": ci(ex), "mean_top_score_prob": round(float(np.mean([o["top_p"] for o in sub])), 4)}
    mae = [abs(o["exp_goals"] - o["hg"] - o["ag"]) for o in sub]; bm = [abs(o["train_mean_goals"] - o["hg"] - o["ag"]) for o in sub]
    res["goals_mae"] = {"model": round(float(np.mean(mae)), 4), "ci": ci(mae), "baseline_train_mean": round(float(np.mean(bm)), 4)}
    res["calibration_bins"], res["ece"] = calibration(sub)
    return res

def value_backtest(sub, validated_leagues=None, key="ens"):
    """Bet 1 unit when edge >= VALUE_MIN_EDGE, EV >= VALUE_MIN_EV, odds <= VALUE_MAX_ODDS, using average
    PRE-CLOSING odds (Avg columns) - the price available when football-data collected it. Extra leagues lack
    pre-closing odds and are excluded."""
    bets = []
    for o in sub:
        if validated_leagues is not None and o["league"] not in validated_leagues: continue
        odds = [o["oh"], o["od"], o["oa"]]
        if not all(np.isfinite(odds)): continue
        fair = implied(odds)[1]; y = y_of(o)
        for k in range(3):
            if o.get(key) is None: break
            p = o[key][k]
            if p - fair[k] >= VALUE_MIN_EDGE and p * odds[k] - 1 >= VALUE_MIN_EV and odds[k] <= VALUE_MAX_ODDS:
                bets.append({"league": o["league"], "profit": odds[k] - 1 if k == y else -1.0, "odds": odds[k]})
    pr = [b["profit"] for b in bets]
    return {"n_bets": len(bets), "roi": round(float(np.mean(pr)), 4) if pr else None, "roi_ci95": ci(pr),
            "profit_units": round(float(np.sum(pr)), 2), "mean_odds": round(float(np.mean([b["odds"] for b in bets])), 3) if bets else None,
            "rule": f"edge>={VALUE_MIN_EDGE}, EV>={VALUE_MIN_EV}, odds<={VALUE_MAX_ODDS}, average pre-closing odds, 1 unit flat"}

def run(m, psl_matches=None):
    m = m[m.league.isin(BACKTEST_LEAGUES)].reset_index(drop=True)
    m = add_features(m)  # recompute on backtest leagues only (Elo identical to v0.1)
    rows = run_walkforward(m)
    w, val_ll, n_val = choose_weights(rows)
    cfg = choose_v2(rows)
    test = evaluate(rows, w, cfg)
    out = {"model_version": "ssa-0.2.0", "weights_v01": w, "weights": w, "v2": cfg,
           "validation": {"n": n_val, "log_loss": round(cfg["val_log_loss"], 4), "log_loss_v01": round(val_ll, 4), "note": "first backtest season of each league"},
           "overall": summarize(test), "by_league": {}, "by_season": {}, "by_league_season": {}}
    for lg in sorted({o["league"] for o in test}):
        out["by_league"][lg] = summarize([o for o in test if o["league"] == lg])
        for s in sorted({o["season"] for o in test if o["league"] == lg}):
            sub = [o for o in test if o["league"] == lg and o["season"] == s]
            out["by_league_season"][f"{lg} {s}"] = {k: v for k, v in summarize(sub).items() if k in ("n_matches", "ens", "base", "bookmaker_closing")}
    for s in sorted({o["season"] for o in test}):
        out["by_season"][s] = {k: v for k, v in summarize([o for o in test if o["season"] == s]).items() if k in ("n_matches", "ens", "base", "bookmaker_closing", "home_always")}
    # validation gate: ensemble must beat base rates (CI of log-loss diff entirely < 0) and ECE < 0.03
    validated = [lg for lg, r in out["by_league"].items() if r["ens_minus_base_logloss"]["ci"][1] < 0 and r["ece"] < 0.03
                 and "ens_minus_book_logloss" in r and r["ens_minus_book_logloss"]["ci"][0] <= 0]
    out["validated_leagues"] = validated
    out["validation_gate"] = "ensemble log loss beats training base rates (95% CI of difference < 0) AND ECE < 0.03 AND ensemble is NOT significantly worse than closing-odds-implied probabilities (95% CI lower bound of ens-book log-loss difference <= 0)"
    out["value_rule_all_leagues"] = value_backtest(test)
    out["value_rule_validated_only"] = value_backtest(test, set(validated))
    out["value_rule_by_league"] = {lg: value_backtest([o for o in test if o["league"] == lg]) for lg in out["by_league"]}
    out["value_rule_v01_all_leagues"] = value_backtest(test, key="ens_v01")
    out["value_rule_model_plus_market_all_leagues"] = value_backtest(test, key="ens_market")
    if psl_matches is not None and len(psl_matches):
        from . import psl
        out["psl"] = psl.backtest(psl_matches)
        if out["psl"]["n_matches"]:
            out["by_league"]["PSL"] = {k: out["psl"][k] for k in ("n_matches", "poisson", "dc", "ens", "base", "home_always", "ens_minus_base_logloss", "ece")}
            out["by_league"]["PSL"]["note"] = "season-ahead backtest, Poisson+DC only, not part of 'overall' (see psl.method)"
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "backtest.json").write_text(json.dumps(out, indent=1, default=float))
    (REPORTS / "backtest.md").write_text(to_md(out)); return out

def fmt(b, k): return f"{b[k]:.4f} [{b[k+'_ci'][0]:.4f}, {b[k+'_ci'][1]:.4f}]"

def to_md(r):
    o = r["overall"]; L = ["# SUPER SOCCER AI - walk-forward backtest", "",
        f"Model {r.get('model_version','')}. v0.2 combination (all chosen on the validation season, n={r['validation']['n']}): {r.get('v2')}", "",
        f"v0.1 ensemble weights (kept as the 'before' baseline): {r['weights']}", "",
        f"Test matches: {o['n_matches']}. 95% bootstrap CIs in brackets.", "",
        "| Model | n | Accuracy | Log loss | Brier | RPS |", "|---|---|---|---|---|---|"]
    names = {"ens": "Ensemble v0.2", "ens_v01": "Ensemble v0.1 (before)", "poisson": "Poisson", "dc": "Dixon-Coles", "elo": "Elo", "logit": "Logistic", "base": "Base rates", "bookmaker_closing": "Bookmaker closing (subset)", "ensemble_on_same_matches": "Ensemble v0.2 (same subset)", "ens_v01_on_same_matches": "Ensemble v0.1 (same subset)",
             "model_plus_market": "Model + market (pre-closing avg odds)", "bookmaker_prematch_avg": "Bookmaker pre-closing avg (market subset)",
             "bookmaker_closing_on_market_subset": "Bookmaker closing (market subset)"}
    for k, nm in names.items():
        if k in o: b = o[k]; L.append(f"| {nm} | {b['n']} | {fmt(b,'accuracy')} | {fmt(b,'log_loss')} | {fmt(b,'brier')} | {fmt(b,'rps')} |")
    L.append(f"| Home always | {o['home_always']['n']} | {fmt(o['home_always'],'accuracy')} | - | - | - |")
    L += ["", f"v0.2 minus v0.1 (paired bootstrap 95% CI): {o.get('v02_minus_v01')}",
          f"v0.1 minus bookmaker closing log loss: {o.get('ens_v01_minus_book_logloss')}", f"v0.2 minus bookmaker closing RPS: {o.get('ens_minus_book_rps')}",
          f"Model+market minus closing log loss: {o.get('model_plus_market_minus_closing_logloss')}; minus pre-closing: {o.get('model_plus_market_minus_prematch_logloss')}",
          f"Ensemble minus bookmaker log loss: {o.get('ens_minus_book_logloss')}", f"Ensemble minus base-rate log loss: {o['ens_minus_base_logloss']}",
          f"Exact-score hit rate (top score): {o['exact_score_hit_rate']}", f"Total goals MAE: {o['goals_mae']}", f"ECE: {o['ece']}", "",
          "## Calibration (all outcomes pooled)", "", "| bin | n | mean predicted | observed |", "|---|---|---|---|"]
    L += [f"| {c['bin']} | {c['n']} | {c['mean_pred']} | {c['observed']} |" for c in o["calibration_bins"]]
    L += ["", "## By league", "", "| League | n | v0.2 log loss | v0.1 log loss | v0.2-v0.1 [95% CI] | v0.2 RPS | v0.1 RPS | Base LL | Book closing LL (subset) | v0.2-book [95% CI] | ECE |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for lg, b in r["by_league"].items():
        bk = b.get("bookmaker_closing", {}); dv = b.get("v02_minus_v01"); db = b.get("ens_minus_book_logloss")
        L.append(f"| {lg} | {b['n_matches']} | {fmt(b['ens'],'log_loss')} | {b.get('ens_v01',{}).get('log_loss','-')} | {(str(dv['log_loss']) + ' ' + str(dv['log_loss_ci'])) if dv else '-'} | {b['ens']['rps']} | {b.get('ens_v01',{}).get('rps','-')} | {b['base']['log_loss']} | {bk.get('log_loss','n/a')} | {(str(db['mean']) + ' ' + str(db['ci'])) if db else '-'} | {b['ece']} |")
    L += ["", "## By league and season", "", "| League season | n | Ens LL | Base LL | Book LL | Ens RPS | Book RPS |", "|---|---|---|---|---|---|---|"]
    for k, b in r["by_league_season"].items():
        bk = b.get("bookmaker_closing", {}); L.append(f"| {k} | {b['n_matches']} | {b['ens']['log_loss']} | {b['base']['log_loss']} | {bk.get('log_loss','n/a')} | {b['ens']['rps']} | {bk.get('rps','n/a')} |")
    L += ["", "## Value rule ROI (test seasons, average pre-closing odds)", "", f"v0.2, all leagues: {r['value_rule_all_leagues']}", "",
          f"v0.1, all leagues: {r.get('value_rule_v01_all_leagues')}", "", f"Model + market variant, all leagues: {r.get('value_rule_model_plus_market_all_leagues')}", "", f"Validated leagues only ({r['validated_leagues']}): {r['value_rule_validated_only']}", "",
          "By league:", ""] + [f"- {k}: {v}" for k, v in r["value_rule_by_league"].items()]
    if r.get("psl"):
        p = r["psl"]; L += ["", "## South Africa PSL (season-ahead, separate method)", "", p["method"], "",
             f"Test matches: {p['n_matches']} (seasons {list(p['by_season'])}); data seasons used: {p['seasons_used']}", ""]
        for k in ("ens", "ens_v2", "poisson", "dc", "dcj", "base"):
            if k not in p: continue
            L.append(f"- {k}: log loss {fmt(p[k], 'log_loss')}, RPS {fmt(p[k], 'rps')}, Brier {fmt(p[k], 'brier')}, accuracy {fmt(p[k], 'accuracy')}")
        L += [f"- always home: accuracy {p['home_always']['accuracy']} {p['home_always']['accuracy_ci']}",
              f"- ensemble minus base log loss: {p['ens_minus_base_logloss']}; ECE {p['ece']}", f"- v2 (Poisson/DCJ) minus v1: {p.get('v2_minus_v1_logloss')}; gate: {p.get('v2_gate')}", f"- missing: {p['missing']}"]
    L += ["", "Past performance does not guarantee future results. No betting outcome is guaranteed."]
    return "\n".join(L)
