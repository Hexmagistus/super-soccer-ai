"""Combination layer (v0.2): linear opinion pool with weights fitted by log loss on the validation season, then a
2-parameter recalibration (temperature T and draw shift d) also fitted on validation:
    p'_k  proportional to  p_k^(1/T) * exp(d * [k == draw])
Nothing here ever sees test-season rows."""
import numpy as np
from scipy.optimize import minimize

def _ll(P, y): return -np.mean(np.log(np.clip(P[np.arange(len(y)), y], 1e-12, None)))

def fit_pool(Ps, y):
    """Ps: list of (n,3) arrays. Returns simplex weights minimising validation log loss (softmax parametrisation)."""
    k = len(Ps); S = np.stack(Ps)
    def f(z):
        w = np.exp(z - z.max()); w /= w.sum(); return _ll(np.tensordot(w, S, 1), y)
    best = min((minimize(f, z0, method="Nelder-Mead" if k <= 2 else "Powell") for z0 in [np.zeros(k)] + [np.eye(k)[i] * 2 for i in range(k)]), key=lambda r: r.fun)
    w = np.exp(best.x - best.x.max()); return w / w.sum()

def recal(P, T=1.0, d=0.0):
    L = np.log(np.clip(P, 1e-12, None)) / T; L[:, 1] += d; L -= L.max(1, keepdims=True); E = np.exp(L); return E / E.sum(1, keepdims=True)

def fit_recal(P, y):
    r = minimize(lambda x: _ll(recal(P, x[0], x[1]), y), [1.0, 0.0], method="Nelder-Mead"); return float(r.x[0]), float(r.x[1])

def log_pool(Ps, w, b=None):
    """Logarithmic pool sum_k w_k log p_k (+ per-outcome bias), used for the model+market variant."""
    L = sum(wi * np.log(np.clip(P, 1e-12, None)) for wi, P in zip(w, Ps))
    if b is not None: L = L + b
    L -= L.max(1, keepdims=True); E = np.exp(L); return E / E.sum(1, keepdims=True)
