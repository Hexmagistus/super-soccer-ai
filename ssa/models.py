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

HIGHER = {"E1": "E0"}  # league -> the league directly above it (only pair present in the data)

def elo_history(m, k=20, hfa=60, promo_inherit=False):
    """Sequential Elo with goal-margin multiplier (World Football Elo style). Returns PRE-match ratings
    (so using them as features never leaks the match result).
    promo_inherit=False (v0.1): a team new to a league enters at the league's 20th percentile (or keeps its rating
    if it already has one from another league, e.g. Championship -> EPL).
    promo_inherit=True (v0.2): a team new to league L in season S takes the mean END-OF-SEASON rating of the 3
    lowest-rated teams of L's previous season (the relegated places it fills); a team dropping in from the league
    above takes the mean of L's 3 highest-rated teams of the previous season (the promoted places it fills).
    Only ratings available before the team's first match are used."""
    r, pre_h, pre_a = {}, [], []
    lg, seen, last_lg, prev_end, cur_season = {}, {}, {}, {}, {}
    for row in m.itertuples(index=False):
        L = lg.setdefault(row.league, {})
        if promo_inherit and cur_season.get(row.league) != row.season:
            if row.league in cur_season and seen.get(row.league):
                prev_end[row.league] = sorted(r[t] for t in seen[row.league])
            cur_season[row.league] = row.season; seen[row.league] = set()
        for t in (row.home, row.away):
            if promo_inherit:
                new_here = t not in L
                if new_here and row.league in prev_end and len(prev_end[row.league]) >= 6:
                    pe = prev_end[row.league]
                    r[t] = float(np.mean(pe[-3:])) if last_lg.get(t) == HIGHER.get(row.league) else float(np.mean(pe[:3]))
                seen[row.league].add(t); last_lg[t] = row.league
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
    if "season" in m:
        m["elo2_h"], m["elo2_a"], _ = elo_history(m, promo_inherit=True); m["elo2_diff"] = m.elo2_h - m.elo2_a
    long = pd.concat([
        pd.DataFrame({"i": m.index, "side": "h", "team": m.home, "date": m.date, "gf": m.hg, "ga": m.ag, "sot": m.hst, "sota": m.ast, "s": m.get("hs", np.nan)}),
        pd.DataFrame({"i": m.index, "side": "a", "team": m.away, "date": m.date, "gf": m.ag, "ga": m.hg, "sot": m.ast, "sota": m.hst, "s": m.get("as_", np.nan)})])
    long["pts"] = np.where(long.gf > long.ga, 3, np.where(long.gf == long.ga, 1, 0)).astype(float)
    long.loc[long.gf.isna(), "pts"] = np.nan
    long = long.sort_values(["date", "i"])
    long["rest"] = long.groupby("team").date.diff().dt.days.clip(upper=21)   # days since previous match in the data
    for c in ["pts", "gf", "ga", "sot", "sota", "s"]:
        long[c + "5"] = long.groupby("team")[c].transform(lambda s: s.shift(1).rolling(5, min_periods=3).mean())
    for side in "ha":
        sub = long[long.side == side].set_index("i")
        for c in ["pts5", "gf5", "ga5", "sot5", "sota5", "s5", "rest"]:
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
V2_XI, V2_SOT_XI = 0.0019, 0.0035     # chosen on the validation season (see reports/experiments.md)

def v2_lambdas(o, alpha):
    """Goals lambdas of the v0.2 core model: geometric blend of joint Dixon-Coles lambdas and shots-on-target
    (xG-proxy) lambdas, lambda = dcj^alpha * sot^(1-alpha). Falls back to joint DC when shots are unavailable."""
    lh, la = o["j_lh"], o["j_la"]
    if o.get("s_lh") is not None: lh, la = lh ** alpha * o["s_lh"] ** (1 - alpha), la ** alpha * o["s_la"] ** (1 - alpha)
    return lh, la

def fit_predict(train, rows, ref):
    """Fit every model on `train` (strictly earlier rows) and return per-model outputs for `rows`."""
    P = PoissonModel().fit(train, ref); D = DixonColes().fit(train, ref); E = EloGoals().fit(train, ref); Lg = LogitModel().fit(train, ref)
    J = DixonColesJoint(V2_XI).fit(train, ref); S = ShotsModel(V2_SOT_XI).fit(train, ref)
    lp = Lg.predict_rows(rows); out = []
    for k, r in enumerate(rows.itertuples(index=False)):
        mp, lh, la = P.predict(r.home, r.away); md, _, _ = D.predict(r.home, r.away); me, eh, ea = E.predict_row(r.elo_h, r.elo_a)
        jh, ja = J.lambdas(r.home, r.away); sh, sa = S.lambdas(r.home, r.away) if S.ok else (None, None)
        out.append({"p_lh": lh, "p_la": la, "dc_rho": D.rho, "e_lh": eh, "e_la": ea,
                    "j_lh": jh, "j_la": ja, "j_rho": J.rho, "s_lh": sh, "s_la": sa,
                    "poisson": outcome_probs(mp), "dc": outcome_probs(md), "elo": outcome_probs(me), "logit": lp[k],
                    "n_home": P.counts.get(r.home, 0), "n_away": P.counts.get(r.away, 0)})
    return out

def ensemble_v2(o, cfg):
    """v0.2: p = recal(w_core * DCJ+SOT-blend + w_logit * logistic; T, d), score matrix = DC matrix of the blended
    lambdas rescaled per H/D/A region to agree exactly with p. cfg keys: alpha, w_core, w_logit, T, d."""
    from .stack import recal
    lh, la = v2_lambdas(o, cfg["alpha"]); M = score_matrix(lh, la, o["j_rho"]); q = outcome_probs(M)
    p = recal((cfg["w_core"] * q + cfg["w_logit"] * np.asarray(o["logit"]))[None, :], cfg["T"], cfg["d"])[0]
    low, diag, up = np.tril(np.ones_like(M), -1), np.eye(len(M)), np.triu(np.ones_like(M), 1)
    M = M * (low * p[0] / q[0] + diag * p[1] / q[1] + up * p[2] / q[2]); return M / M.sum(), p

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

# ---------------------------------------------------------------------------------------------------
# v0.2 components (see README "Model v0.2"). Every one is fit only on the rows passed in.

def promoted_flags(df, grace_days=60):
    """A team is 'promoted' (new to this league inside the training window) if its first match in `df`
    is more than `grace_days` after the window's first match. Uses only training rows."""
    first = pd.concat([df[["home", "date"]].rename(columns={"home": "t"}), df[["away", "date"]].rename(columns={"away": "t"})]).groupby("t").date.min()
    return (first > df.date.min() + pd.Timedelta(days=grace_days)).to_dict()

class DixonColesJoint(PoissonModel):
    """Dixon-Coles with ALL parameters (attack, defence, mu, home advantage, rho) fitted jointly by weighted MLE,
    time decay xi (tuned on validation), ridge shrinkage, and a promoted-team prior: teams that entered the league
    inside the training window are shrunk towards a shared, jointly-estimated 'promoted team' strength
    (c_att, c_def) instead of towards the league average; teams with no training match at all get that prior.
    Home advantage is per league because every league is fitted separately."""
    def __init__(self, xi=0.0019, ridge=1.0, promo=True, fit_rho=True):
        self.xi, self.ridge, self.promo, self.fit_rho = xi, ridge, promo, fit_rho
    def fit(self, df, ref):
        teams = sorted(set(df.home) | set(df.away)); self.idx = {t: i for i, t in enumerate(teams)}; n = len(teams)
        h = df.home.map(self.idx).values; a = df.away.map(self.idx).values
        yh, ya = df.hg.values, df.ag.values; w = time_weights(df.date, ref, self.xi)
        self.counts = pd.concat([df.home, df.away]).value_counts().to_dict()
        pf = promoted_flags(df) if self.promo else {}
        P = np.array([float(pf.get(t, False)) for t in teams]); R = self.ridge
        m00, m01, m10, m11 = (yh == 0) & (ya == 0), (yh == 0) & (ya == 1), (yh == 1) & (ya == 0), (yh == 1) & (ya == 1)
        def f(p):
            att, de, mu, ha, rho, ca, cd = p[:n], p[n:2 * n], p[-5], p[-4], p[-3], p[-2], p[-1]
            lh = np.exp(mu + ha + att[h] + de[a]); la = np.exp(mu + att[a] + de[h])
            t = np.ones(len(yh)); dr = np.zeros(len(yh)); dlh = np.zeros(len(yh)); dla = np.zeros(len(yh))
            t[m00] = 1 - lh[m00] * la[m00] * rho; t[m01] = 1 + lh[m01] * rho; t[m10] = 1 + la[m10] * rho; t[m11] = 1 - rho
            if (t <= 1e-9).any(): return 1e12, np.zeros_like(p)  # outside the valid tau region
            dr[m00] = -lh[m00] * la[m00] / t[m00]; dlh[m00] = dla[m00] = -lh[m00] * la[m00] * rho / t[m00]
            dr[m01] = lh[m01] / t[m01]; dlh[m01] = lh[m01] * rho / t[m01]
            dr[m10] = la[m10] / t[m10]; dla[m10] = la[m10] * rho / t[m10]
            dr[m11] = -1 / t[m11]
            ea, ed = att - ca * P, de - cd * P
            nll = np.sum(w * (lh - yh * np.log(lh) + la - ya * np.log(la) - np.log(t))) + R * (ea @ ea + ed @ ed)
            rh, ra = w * (lh - yh - dlh), w * (la - ya - dla)   # d nll / d log(lambda)
            g_att = np.bincount(h, rh, n) + np.bincount(a, ra, n) + 2 * R * ea
            g_def = np.bincount(a, rh, n) + np.bincount(h, ra, n) + 2 * R * ed
            return nll, np.concatenate([g_att, g_def, [rh.sum() + ra.sum(), rh.sum(), -np.sum(w * dr), -2 * R * (ea @ P), -2 * R * (ed @ P)]])
        p0 = np.zeros(2 * n + 5); p0[-5] = np.log(max(df[["hg", "ag"]].values.mean(), 0.1)); p0[-4] = 0.2
        bounds = [(None, None)] * (2 * n + 2) + [(-0.2, 0.2) if self.fit_rho else (0, 0), (-1, 1) if self.promo else (0, 0), (-1, 1) if self.promo else (0, 0)]
        r = minimize(f, p0, jac=True, method="L-BFGS-B", bounds=bounds)
        x = r.x; self.att, self.de, self.mu, self.ha, self.rho, self.c_att, self.c_def = x[:n], x[n:2 * n], x[-5], x[-4], x[-3], x[-2], x[-1]
        if not self.promo: self.c_att = self.c_def = 0.0
        return self
    def lambdas(self, home, away):
        ai = lambda t, arr, c: arr[self.idx[t]] if t in self.idx else c   # unseen team -> promoted-team prior
        lh = np.exp(self.mu + self.ha + ai(home, self.att, self.c_att) + ai(away, self.de, self.c_def))
        la = np.exp(self.mu + ai(away, self.att, self.c_att) + ai(home, self.de, self.c_def))
        return lh, la
    def predict(self, home, away):
        lh, la = self.lambdas(home, away); return score_matrix(lh, la, self.rho), lh, la

class ShotsModel:
    """Shots-on-target ratings - an xG PROXY, not real xG. Poisson attack/defence model (with time decay and the
    promoted-team prior, no rho) fitted on shots on target (hst/ast) instead of goals; expected SOT are converted
    to expected goals with the training-window goals-per-SOT ratio (home and away separately).
    Rows without shots data are dropped; ok=False when fewer than 100 such rows."""
    def __init__(self, xi=0.0019, ridge=1.0):
        self.xi, self.ridge = xi, ridge
    def fit(self, df, ref):
        d = df.dropna(subset=["hst", "ast"]); self.ok = len(d) >= 100
        if not self.ok: return self
        w = time_weights(d.date, ref, self.xi)
        self.kh = np.sum(w * d.hg) / max(np.sum(w * d.hst), 1); self.ka = np.sum(w * d.ag) / max(np.sum(w * d.ast), 1)
        self.m = DixonColesJoint(self.xi, self.ridge, fit_rho=False).fit(d.assign(hg=d.hst, ag=d.ast), ref); return self
    def lambdas(self, home, away):
        sh, sa = self.m.lambdas(home, away); return sh * self.kh, sa * self.ka
