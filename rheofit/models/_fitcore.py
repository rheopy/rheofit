"""
Shared robust fitting core for all rheological models.

Single source of truth for:
  * RELATIVE WEIGHTING  — the objective is always (f(x,p) - y) / |y|, so every
    decade of stress contributes equally and RedChi2 is dimensionless.
  * Log-space reparameterisation of strictly-positive, multi-decade parameters.
  * Physics-informed initial estimates read off the data.
  * Multi-start global search (Sobol) + ladder seeding from the simpler parent
    model + optional differential evolution, followed by a tight local polish.
  * Covariance / standard errors transformed back to physical units.

A model module must declare:
    MODEL_NAME, PARAMS, SCORECARD_PARAMS
    LOG_PARAMS   : tuple of parameter names fitted in log10 space
    BOUNDS       : dict name -> (lo, hi) in PHYSICAL units (lo > 0 for log params)
    PARENT       : name of the simpler nested model, or None
    _func(x, *params)
    initial_guess(x, y, eta) -> dict name -> value
    seed_from_parent(parent_values, x, y, eta) -> dict name -> value   (if PARENT)
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import differential_evolution, least_squares
from scipy.stats import qmc

TINY = 1e-30
BIG = 1e30

# number of Sobol starts / number of survivors polished, per effort level
EFFORT = {
    "fast":     (32,   4),
    "normal":   (128,  8),
    "thorough": (512, 16),
}
DEFAULT_EFFORT = "thorough"

# half-width of the Sobol window around the physics estimate, in decades
LOG_SPREAD = 3.0


# ══════════════════════════════════════════════════════════════════════════════
# Data cleaning
# ══════════════════════════════════════════════════════════════════════════════

def clean_data(df):
    """Return (x, y, eta, n_dropped) keeping only points valid for relative fitting.

    Relative residuals divide by y, so non-finite or non-positive stress points
    must be removed rather than silently producing inf/nan.
    """
    x = np.asarray(df["Shear rate / 1/s"].values, dtype=float)
    y = np.asarray(df["Stress / Pa"].values, dtype=float)
    if "Viscosity / Pa.s" in df:
        eta = np.asarray(df["Viscosity / Pa.s"].values, dtype=float)
    else:
        eta = np.full_like(x, np.nan)

    ok = np.isfinite(x) & np.isfinite(y) & (x > 0.0) & (y > 0.0)
    n_dropped = int((~ok).sum())
    x, y, eta = x[ok], y[ok], eta[ok]

    # rebuild viscosity where the instrument column is missing/invalid
    bad_eta = ~np.isfinite(eta) | (eta <= 0.0)
    if bad_eta.any():
        eta = eta.copy()
        eta[bad_eta] = y[bad_eta] / x[bad_eta]

    order = np.argsort(x)
    return x[order], y[order], eta[order], n_dropped


# ══════════════════════════════════════════════════════════════════════════════
# Physics-informed estimators
# ══════════════════════════════════════════════════════════════════════════════

def _low_decade(x):
    """Boolean mask for the lowest decade of shear rate."""
    return x <= x.min() * 10.0


def _high_decade(x):
    """Boolean mask for the highest decade of shear rate."""
    return x >= x.max() / 10.0


def est_sigma_y(x, y):
    """Yield stress ~ the stress plateau at the lowest shear rates."""
    m = _low_decade(x)
    val = float(np.median(y[m])) if m.any() else float(y.min())
    return max(val, TINY)


def est_eta_bg(x, y):
    """Newtonian background viscosity ~ slope of sigma vs gamma-dot at high rate."""
    m = _high_decade(x)
    if m.sum() >= 2:
        slope, _ = np.polyfit(x[m], y[m], 1)
        if np.isfinite(slope) and slope > 0:
            return float(slope)
    return max(float(np.min(y / x)), TINY)


def est_eta_0(x, eta):
    """Zero-shear viscosity ~ the viscosity plateau at the lowest shear rates."""
    m = _low_decade(x)
    val = float(np.median(eta[m])) if m.any() else float(eta.max())
    return max(val, TINY)


def est_lambda(x, eta):
    """Carreau time constant ~ 1 / (shear rate where eta has fallen to eta_0/2)."""
    eta_0 = est_eta_0(x, eta)
    half = eta_0 / 2.0
    below = np.nonzero(eta <= half)[0]
    if below.size:
        x_c = float(x[below[0]])
    else:
        x_c = float(np.sqrt(x.min() * x.max()))
    return max(1.0 / max(x_c, TINY), TINY)


def est_power_law(x, y):
    """(K, n) from a straight line through log(sigma) vs log(gamma-dot)."""
    n, logK = np.polyfit(np.log10(x), np.log10(y), 1)
    n = float(np.clip(n, 0.01, 2.0))
    K = float(10.0 ** np.clip(logK, -20, 20))
    return max(K, TINY), n


def est_gamma_dot_c(x):
    """Critical shear rate ~ the top of the measured window."""
    return max(float(x.max()), 1e-6)


# ══════════════════════════════════════════════════════════════════════════════
# Log-space transform
# ══════════════════════════════════════════════════════════════════════════════

class Transform:
    """Maps physical parameters <-> optimiser coordinates (log10 for LOG_PARAMS)."""

    def __init__(self, params, log_params, bounds):
        self.params = list(params)
        self.is_log = np.array([p in set(log_params) for p in self.params], dtype=bool)
        lo = np.array([float(bounds[p][0]) for p in self.params], dtype=float)
        hi = np.array([float(bounds[p][1]) for p in self.params], dtype=float)
        self.lo_phys, self.hi_phys = lo, hi

        with np.errstate(divide="ignore"):
            self.lo = np.where(self.is_log, np.log10(np.maximum(lo, TINY)), lo)
            self.hi = np.where(self.is_log, np.log10(np.where(np.isfinite(hi), np.maximum(hi, TINY), 1.0)), hi)
        self.hi = np.where(self.is_log & ~np.isfinite(hi), 20.0, self.hi)

    def to_theta(self, p_vec):
        p = np.clip(np.asarray(p_vec, dtype=float), self.lo_phys, self.hi_phys)
        with np.errstate(divide="ignore", invalid="ignore"):
            theta = np.where(self.is_log, np.log10(np.maximum(p, TINY)), p)
        return np.clip(theta, self.lo, self.hi)

    def to_phys(self, theta):
        t = np.asarray(theta, dtype=float)
        return np.where(self.is_log, 10.0 ** np.clip(t, -300, 300), t)

    def dphys_dtheta(self, p_phys):
        """Diagonal Jacobian of the transform, for propagating standard errors."""
        return np.where(self.is_log, np.asarray(p_phys) * np.log(10.0), 1.0)

    def sample_window(self, theta0):
        """Sobol sampling window: +/- LOG_SPREAD decades for log params, full range otherwise."""
        lo_w = np.where(self.is_log, theta0 - LOG_SPREAD, self.lo)
        hi_w = np.where(self.is_log, theta0 + LOG_SPREAD, self.hi)
        return np.maximum(lo_w, self.lo), np.minimum(hi_w, self.hi)


# ══════════════════════════════════════════════════════════════════════════════
# Objective — relative residuals, always
# ══════════════════════════════════════════════════════════════════════════════

def make_residual(func, x, y, tr):
    denom = np.maximum(np.abs(y), TINY)

    def resid(theta):
        p = tr.to_phys(theta)
        with np.errstate(all="ignore"):
            model = func(x, *p)
        model = np.nan_to_num(np.asarray(model, dtype=float),
                              nan=BIG, posinf=BIG, neginf=-BIG)
        return (model - y) / denom

    return resid


def _cost(resid, theta):
    try:
        r = resid(theta)
        c = float(0.5 * np.sum(r ** 2))
        return c if np.isfinite(c) else np.inf
    except Exception:
        return np.inf


# ══════════════════════════════════════════════════════════════════════════════
# Main entry point
# ══════════════════════════════════════════════════════════════════════════════

def robust_fit(model, df, effort: str = DEFAULT_EFFORT, seed: int = 0,
               _depth: int = 0) -> dict:
    """Globally-seeded, relatively-weighted fit of `model` to a flow-curve frame."""
    if effort not in EFFORT:
        raise ValueError(f"effort must be one of {sorted(EFFORT)}")
    n_starts, n_polish = EFFORT[effort]

    x, y, eta, n_dropped = clean_data(df)
    params = list(model.PARAMS)
    tr = Transform(params, getattr(model, "LOG_PARAMS", ()), model.BOUNDS)
    resid = make_residual(model._func, x, y, tr)

    notes: list[str] = []
    if n_dropped:
        notes.append(f"dropped {n_dropped} non-finite/non-positive point(s)")

    # ── 1. physics-informed start ────────────────────────────────────────────
    guess = model.initial_guess(x, y, eta)
    theta_phys = tr.to_theta([guess[p] for p in params])
    starts = [theta_phys]

    # ── 2. ladder seeding from the simpler nested parent ─────────────────────
    parent_redchi = None
    parent_name = getattr(model, "PARENT", None)
    if parent_name and _depth < 4:
        from . import MODELS  # local import avoids a circular import at module load
        parent_res = robust_fit(MODELS[parent_name], df, effort=effort,
                                seed=seed + 1, _depth=_depth + 1)
        parent_redchi = parent_res["redchi"]
        parent_vals = {k: v["value"] for k, v in parent_res["params"].items()}
        seeded = model.seed_from_parent(parent_vals, x, y, eta)
        starts.append(tr.to_theta([seeded[p] for p in params]))

    # ── 3. Sobol multi-start around the physics estimate ─────────────────────
    lo_w, hi_w = tr.sample_window(theta_phys)
    dim = len(params)
    sampler = qmc.Sobol(d=dim, scramble=True, seed=seed)
    n_pow = max(1, int(np.ceil(np.log2(max(n_starts, 2)))))
    u = sampler.random_base2(m=n_pow)
    starts.extend(list(lo_w + u * (hi_w - lo_w)))

    # ── 4. coarse pass over every start ──────────────────────────────────────
    coarse = []
    for th0 in starts:
        try:
            sol = least_squares(resid, np.clip(th0, tr.lo, tr.hi),
                                bounds=(tr.lo, tr.hi), method="trf",
                                x_scale="jac", ftol=1e-8, xtol=1e-8, gtol=1e-8,
                                max_nfev=200 * dim)
            coarse.append((float(sol.cost), sol.x))
        except Exception:
            continue
    if not coarse:
        coarse = [(_cost(resid, theta_phys), theta_phys)]

    # ── 5. optional global pre-pass for the harder, higher-dimensional models ─
    if effort == "thorough" and dim >= 4:
        try:
            de = differential_evolution(
                lambda th: _cost(resid, th),
                bounds=list(zip(lo_w, hi_w)), seed=seed, tol=1e-8,
                maxiter=300, popsize=20, polish=False, init="sobol",
            )
            coarse.append((float(de.fun), de.x))
        except Exception:
            pass

    # ── 6. tight polish of the best survivors ────────────────────────────────
    coarse.sort(key=lambda t: t[0])
    best_sol, best_cost = None, np.inf
    for _, th in coarse[:n_polish]:
        try:
            sol = least_squares(resid, np.clip(th, tr.lo, tr.hi),
                                bounds=(tr.lo, tr.hi), method="trf",
                                x_scale="jac", ftol=1e-14, xtol=1e-14, gtol=1e-14,
                                max_nfev=5000 * dim)
        except Exception:
            continue
        if float(sol.cost) < best_cost:
            best_sol, best_cost = sol, float(sol.cost)

    if best_sol is None:
        raise RuntimeError(f"{model.MODEL_NAME}: all optimisation attempts failed")

    result = _pack(model, best_sol, tr, x, y, params)
    result["n_starts"] = len(starts)
    result["n_dropped"] = n_dropped
    result["effort"] = effort
    result["parent"] = parent_name
    result["parent_redchi"] = parent_redchi

    # exactly-nested models can never legitimately fit worse than their parent
    if (parent_redchi is not None and getattr(model, "PARENT_EXACT", False)
            and result["redchi"] > parent_redchi * 1.05):
        notes.append(
            f"RedChi2 worse than nested parent '{parent_name}' "
            f"({result['redchi']:.3E} vs {parent_redchi:.3E}) - suspect convergence"
        )

    for name, info in result["params"].items():
        v, e = info["value"], info["stderr"]
        if np.isfinite(e) and v > 0 and e > abs(v):
            notes.append(f"'{name}' has >100% relative error - poorly identified")
    if result["cond"] > 1e12:
        notes.append(f"Jacobian condition number {result['cond']:.1E} - near-degenerate")

    result["notes"] = notes
    return result


def _pack(model, sol, tr, x, y, params) -> dict:
    """Convert a least_squares solution into the plain result dict the report uses."""
    n, p = len(y), len(params)
    theta = sol.x
    p_phys = tr.to_phys(theta)

    redchi = float(np.sum(sol.fun ** 2) / max(n - p, 1))

    # covariance in optimiser space, then chain-rule back to physical units
    jac = np.asarray(sol.jac, dtype=float)
    try:
        _, s, Vt = np.linalg.svd(jac, full_matrices=False)
        thresh = np.finfo(float).eps * max(jac.shape) * (s[0] if s.size else 0.0)
        s_inv = np.where(s > thresh, 1.0 / np.maximum(s, TINY), 0.0)
        cov_theta = (Vt.T @ np.diag(s_inv ** 2) @ Vt) * redchi
        cond = float(s[0] / s[-1]) if s.size and s[-1] > 0 else np.inf
    except np.linalg.LinAlgError:
        cov_theta = np.full((p, p), np.nan)
        cond = np.inf

    D = tr.dphys_dtheta(p_phys)
    cov_phys = cov_theta * np.outer(D, D)
    stderr = np.sqrt(np.maximum(np.diag(cov_phys), 0.0))

    return {
        "success": bool(sol.success),
        "params": {name: {"value": float(v), "stderr": float(e)}
                   for name, v, e in zip(params, p_phys, stderr)},
        "redchi": redchi,
        "cond": cond,
        "x": x,
        "y_data": y,
        "y_fit": np.asarray(model._func(x, *p_phys), dtype=float),
    }
