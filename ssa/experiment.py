"""Model-improvement experiment harness (v0.2). Runs the SAME strict walk-forward as backtest.py (weekly refit on
matches dated before the week, 3-year window) but records every candidate component per match, caches the rows,
and lets selection happen on the validation season only. Usage: python -m ssa.experiment"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import pickle, numpy as np, pandas as pd
from multiprocessing import Pool
from sklearn.ensemble import HistGradientBoostingClassifier
from .config import ROOT
from .models import (fit_predict, DixonColesJoint, ShotsModel, EloGoals, LogitModel, outcome_probs, score_matrix,
                     time_weights, add_features)
from .backtest import bt_seasons, WINDOW_DAYS

XIS = [0.001, 0.0019, 0.0035, 0.006]
SOT_XIS = [0.0019, 0.0035]
FEATS2 = ["elo2_diff", "h_pts5", "a_pts5", "h_gf5", "h_ga5", "a_gf5", "a_ga5", "h_sot5", "a_sot5", "h_sota5", "a_sota5",
          "h_s5", "a_s5", "h_rest", "a_rest"]
CACHE = ROOT / "data" / "experiment_rows.pkl"

class Elo2Goals(EloGoals):
    def fit(self, df, ref): return super().fit(df.assign(elo_h=df.elo2_h, elo_a=df.elo2_a), ref)

class Logit2(LogitModel):
    def fit(self, df, ref):
        import ssa.models as M; old = M.FEATS; M.FEATS = FEATS2
        try: return super().fit(df, ref)
        finally: M.FEATS = old

class GBM:
    """sklearn HistGradientBoosting on pre-match features only (no in-sample model outputs, which would leak)."""
    def fit(self, df, ref):
        self.feats = [f for f in FEATS2 if df[f].notna().mean() > 0.8]
        d = df.dropna(subset=["hg", "ag"]); y = np.where(d.hg > d.ag, 0, np.where(d.hg == d.ag, 1, 2))
        self.clf = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.03, max_depth=3, min_samples_leaf=40,
                                                  l2_regularization=1.0, random_state=0)
        self.clf.fit(d[self.feats].values, y, sample_weight=time_weights(d.date, ref)); return self
    def predict_rows(self, rows):
        p = self.clf.predict_proba(rows[self.feats].values); out = np.zeros((len(rows), 3)); out[:, self.clf.classes_] = p; return out

def components(train, rows, ref, gbm=True):
    base = fit_predict(train, rows, ref)
    dcj = {xi: DixonColesJoint(xi).fit(train, ref) for xi in XIS}
    nop = DixonColesJoint(0.0019, promo=False).fit(train, ref)
    sot = {xi: ShotsModel(xi).fit(train, ref) for xi in SOT_XIS}
    e2 = Elo2Goals().fit(train, ref); l2 = Logit2().fit(train, ref).predict_rows(rows)
    gb = GBM().fit(train, ref).predict_rows(rows) if gbm else None
    for k, (r, o) in enumerate(zip(rows.itertuples(index=False), base)):
        for xi, D in dcj.items():
            lh, la = D.lambdas(r.home, r.away); o[f"dcj_{xi}"] = (lh, la, D.rho)
        lh, la = nop.lambdas(r.home, r.away); o["dcj_nopromo"] = (lh, la, nop.rho)
        for xi, S in sot.items():
            o[f"sot_{xi}"] = S.lambdas(r.home, r.away) if S.ok else None
        _, eh, ea = e2.predict_row(r.elo2_h, r.elo2_a); o["elo2_l"] = (eh, ea)
        o["logit2"] = l2[k]; o["gbm"] = gb[k] if gb is not None else None
    return base

def _league(args):
    m, lg = args; rows = []; seasons = bt_seasons(m, lg); L = m[m.league == lg]
    target = L[L.season.isin(seasons) & L.hg.notna()]
    for wk, grp in target.groupby(target.date.dt.to_period("W-SUN")):
        start = wk.start_time
        train = L[(L.date < start) & (L.date >= start - pd.Timedelta(days=WINDOW_DAYS)) & L.hg.notna()]
        if len(train) < 200: continue
        for r, o in zip(grp.itertuples(index=False), components(train, grp, start)):
            o.update({"match_id": r.match_id, "league": lg, "season": r.season, "date": str(r.date.date()), "home": r.home, "away": r.away,
                      "hg": int(r.hg), "ag": int(r.ag), "val": r.season == seasons[0], "ch": r.ch, "cd": r.cd, "ca": r.ca,
                      "oh": r.oh, "od": r.od, "oa": r.oa, "train_mean_goals": float((train.hg + train.ag).mean()),
                      "base": train.assign(res=np.sign(train.hg - train.ag)).res.value_counts(normalize=True).reindex([1, 0, -1]).fillna(0).values})
            rows.append(o)
    print("done", lg, len(rows), flush=True); return rows

def run(m):
    with Pool(8) as p: parts = p.map(_league, [(m, lg) for lg in m.league.unique()])
    rows = [o for part in parts for o in part]; CACHE.write_bytes(pickle.dumps(rows)); return rows

if __name__ == "__main__":
    from . import ingest
    from .config import BACKTEST_LEAGUES
    m, _, _ = ingest.load_all(); run(add_features(m[m.league.isin(BACKTEST_LEAGUES)].reset_index(drop=True)))
