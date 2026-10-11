"""Poisson, Dixon-Coles, Elo, logistic regression and ensemble. All fit only on the rows passed in."""
import numpy as np, pandas as pd
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import poisson
from sklearn.linear_model import LogisticRegression, PoissonRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from .config import MAX_GOALS

G = np.arange(MAX_GOALS + 1)

def time_weights(dates, ref, xi=0.0019):
    """Exponential time decay (Dixon & Coles 1997); xi per day -> half-life ~ 365 days."""
    return np.exp(-xi * (pd.Timestamp(ref) - pd.to_datetime(dates)).dt.days.values)

def score_matrix(lh, la, rho=0.0):
    """P(home=i, away=j) for i,j in 0..6, Dixon-Coles tau applied, renormalised to sum to 1
    (mass above 6 goals, typically <0.5%, is redistributed proportionally)."""
    M = np.outer(poisson.pmf(G, lh), poisson.pmf(G, la))
    if rho:
        M[0, 0] *= 1 - lh * la * rho; M[0, 1] *= 1 + lh * rho; M[1, 0] *= 1 + la * rho; M[1, 1] *= 1 - rho
    M = np.clip(M, 0, None)
    return M / M.sum()

def outcome_probs(M):
    return np.array([np.tril(M, -1).sum(), np.trace(M), np.triu(M, 1).sum()])

class PoissonModel:
    """log(lambda_home) = mu + home + att[h] + def[a]; log(lambda_away) = mu + att[a] + def[h].
    Weighted MLE with small ridge penalty (shrinks teams with few matches towards average)."""
    def __init__(self, xi=0.0019, ridge=1.0):
        self.xi, self.ridge = xi, ridge
    def fit(self, df, ref):
        teams = sorted(set(df.home) | set(df.away)); self.idx = {t: i for i, t in enumerate(teams)}; n = len(teams)
        h = df.home.map(self.idx).values; a = df.away.map(self.idx).values
        yh, ya = df.hg.values, df.ag.values; w = time_weights(df.date, ref, self.xi)
        self.counts = pd.concat([df.home, df.away]).value_counts().to_dict()
        def f(p):
            att, de, mu, ha = p[:n], p[n:2 * n], p[-2], p[-1]
            lh = np.exp(mu + ha + att[h] + de[a]); la = np.exp(mu + att[a] + de[h])
            nll = np.sum(w * (lh - yh * np.log(lh))) + np.sum(w * (la - ya * np.log(la)))
            nll += self.ridge * (att @ att + de @ de)
            rh, ra = w * (lh - yh), w * (la - ya)
            g_att = np.bincount(h, rh, n) + np.bincount(a, ra, n) + 2 * self.ridge * att
            g_def = np.bincount(a, rh, n) + np.bincount(h, ra, n) + 2 * self.ridge * de
            return nll, np.concatenate([g_att, g_def, [rh.sum() + ra.sum(), rh.sum()]])
        p0 = np.zeros(2 * n + 2); p0[-2] = np.log(max(df[["hg", "ag"]].values.mean(), 0.1))
        r = minimize(f, p0, jac=True, method="L-BFGS-B")
        self.att, self.de, self.mu, self.ha = r.x[:n], r.x[n:2 * n], r.x[-2], r.x[-1]
        self._df, self._w = df, w
        return self
    def lambdas(self, home, away):
        ai = lambda t, arr: arr[self.idx[t]] if t in self.idx else 0.0  # unseen team -> league average (flagged elsewhere)
        lh = np.exp(self.mu + self.ha + ai(home, self.att) + ai(away, self.de))
        la = np.exp(self.mu + ai(away, self.att) + ai(home, self.de))
        return lh, la
    def predict(self, home, away):
        lh, la = self.lambdas(home, away); return score_matrix(lh, la), lh, la

class DixonColes(PoissonModel):
    """Dixon-Coles: Poisson strengths + rho low-score correction. Two-stage MLE: strengths by weighted
    Poisson MLE, then rho by maximising the weighted DC likelihood given those strengths."""
    def fit(self, df, ref):
        super().fit(df, ref)
        lh, la = zip(*[self.lambdas(x, y) for x, y in zip(df.home, df.away)]); lh, la = np.array(lh), np.array(la)
        yh, ya, w = df.hg.values, df.ag.values, self._w
        def nll(rho):
            t = np.ones(len(yh))
            t = np.where((yh == 0) & (ya == 0), 1 - lh * la * rho, t); t = np.where((yh == 0) & (ya == 1), 1 + lh * rho, t)
            t = np.where((yh == 1) & (ya == 0), 1 + la * rho, t); t = np.where((yh == 1) & (ya == 1), 1 - rho, t)
            return np.inf if (t <= 0).any() else -np.sum(w * np.log(t))
        self.rho = minimize_scalar(nll, bounds=(-0.25, 0.25), method="bounded").x
        return self
    def predict(self, home, away):
        lh, la = self.lambdas(home, away); return score_matrix(lh, la, self.rho), lh, la

def elo_history(m, k=20, hfa=60):
    """Sequential Elo with goal-margin multiplier (World Football Elo style). Returns PRE-match ratings
    (so using them as features never leaks the match result). New teams enter at the league's 20th percentile."""
    r, pre_h, pre_a = {}, [], []
    lg = {}
    for row in m.itertuples(index=False):
        L = lg.setdefault(row.league, {})
        for t in (row.home, row.away):
            if t not in r:
                vals = [r[x] for x in L] or [1500]; r[t] = float(np.percentile(vals, 20)) if len(vals) > 5 else 1500.0
            L[t] = 1
        rh, ra = r[row.home], r[row.away]; pre_h.append(rh); pre_a.append(ra)
        if np.isnan(row.hg) or np.isnan(row.ag): continue
        e = 1 / (1 + 10 ** (-(rh + hfa - ra) / 400)); s = 1.0 if row.hg > row.ag else 0.5 if row.hg == row.ag else 0.0
        gd = abs(row.hg - row.ag); gm = 1 if gd <= 1 else 1.5 if gd == 2 else (11 + gd) / 8
        d = k * gm * (s - e); r[row.home] += d; r[row.away] -= d
    return np.array(pre_h), np.array(pre_a), r

class EloGoals:
    """Maps pre-match Elo difference (+home advantage) to expected goals with two Poisson GLMs fit on training rows."""
    def fit(self, df, ref):
        X = ((df.elo_h - df.elo_a + 60) / 100).values.reshape(-1, 1); w = time_weights(df.date, ref)
        self.gh = PoissonRegressor(alpha=0).fit(X, df.hg, sample_weight=w)
        self.ga = PoissonRegressor(alpha=0).fit(X, df.ag, sample_weight=w); return self
    def predict_row(self, eh, ea):
        x = np.array([[(eh - ea + 60) / 100]]); lh, la = self.gh.predict(x)[0], self.ga.predict(x)[0]
        return score_matrix(lh, la), lh, la

FEATS = ["elo_diff", "h_pts5", "a_pts5", "h_gf5", "h_ga5", "a_gf5", "a_ga5", "h_sot5", "a_sot5", "h_sota5", "a_sota5"]

def add_features(m):
    """Pre-match features only: Elo before the match, rolling last-5 form shifted by one match."""
    m = m.copy(); m["elo_h"], m["elo_a"], _ = elo_history(m); m["elo_diff"] = m.elo_h - m.elo_a
    long = pd.concat([
        pd.DataFrame({"i": m.index, "side": "h", "team": m.home, "date": m.date, "gf": m.hg, "ga": m.ag, "sot": m.hst, "sota": m.ast}),
        pd.DataFrame({"i": m.index, "side": "a", "team": m.away, "date": m.date, "gf": m.ag, "ga": m.hg, "sot": m.ast, "sota": m.hst})])
    long["pts"] = np.where(long.gf > long.ga, 3, np.where(long.gf == long.ga, 1, 0)).astype(float)
    long.loc[long.gf.isna(), "pts"] = np.nan
    long = long.sort_values(["date", "i"])
    for c in ["pts", "gf", "ga", "sot", "sota"]:
        long[c + "5"] = long.groupby("team")[c].transform(lambda s: s.shift(1).rolling(5, min_periods=3).mean())
    for side in "ha":
        sub = long[long.side == side].set_index("i")
        for c in ["pts5", "gf5", "ga5", "sot5", "sota5"]:
            m[f"{side}_{c}"] = sub[c]
    return m

class LogitModel:
    def fit(self, df, ref):
        self.feats = [f for f in FEATS if df[f].notna().mean() > 0.8]
        d = df.dropna(subset=self.feats + ["hg", "ag"])
        y = np.where(d.hg > d.ag, 0, np.where(d.hg == d.ag, 1, 2))
        self.clf = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=500))
        self.clf.fit(d[self.feats].values, y, logisticregression__sample_weight=time_weights(d.date, ref))
        self.fill = d[self.feats].mean(); return self
    def predict_rows(self, rows):
        X = rows[self.feats].fillna(self.fill).values; p = self.clf.predict_proba(X)
        out = np.zeros((len(rows), 3)); out[:, self.clf.classes_] = p; return out

MODELS = ["poisson", "dc", "elo", "logit"]

def fit_predict(train, rows, ref):
    """Fit every model on `train` (strictly earlier rows) and return per-model outputs for `rows`."""
    P = PoissonModel().fit(train, ref); D = DixonColes().fit(train, ref); E = EloGoals().fit(train, ref); Lg = LogitModel().fit(train, ref)
    lp = Lg.predict_rows(rows); out = []
    for k, r in enumerate(rows.itertuples(index=False)):
        mp, lh, la = P.predict(r.home, r.away); md, _, _ = D.predict(r.home, r.away); me, eh, ea = E.predict_row(r.elo_h, r.elo_a)
        out.append({"p_lh": lh, "p_la": la, "dc_rho": D.rho, "e_lh": eh, "e_la": ea,
                    "poisson": outcome_probs(mp), "dc": outcome_probs(md), "elo": outcome_probs(me), "logit": lp[k],
                    "n_home": P.counts.get(r.home, 0), "n_away": P.counts.get(r.away, 0)})
    return out

def ensemble(o, w):
    """w: dict model->weight. Score matrix = weighted mix of matrix models, rescaled per H/D/A region so the
    matrix agrees exactly with the ensemble 1X2 (which also includes the logistic model)."""
    mats = {"poisson": score_matrix(o["p_lh"], o["p_la"]), "dc": score_matrix(o["p_lh"], o["p_la"], o["dc_rho"]),
            "elo": score_matrix(o["e_lh"], o["e_la"])}
    mw = {k: w[k] for k in mats}; sw = sum(mw.values())
    if sw <= 0: mw, sw = {k: 1.0 for k in mats}, 3.0
    M = sum(mw[k] * mats[k] for k in mats) / sw
    p = sum(w[k] * np.asarray(o[k]) for k in MODELS); p = p / p.sum()
    q = outcome_probs(M); low, diag, up = np.tril(np.ones_like(M), -1), np.eye(len(M)), np.triu(np.ones_like(M), 1)
    M = M * (low * p[0] / q[0] + diag * p[1] / q[1] + up * p[2] / q[2])
    return M / M.sum(), p
