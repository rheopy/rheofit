"""
Herschel-Bulkley — yield stress + power-law flow
  σ = σ_y + K·γ̇ⁿ
"""
import numpy as np

from ._fitcore import DEFAULT_EFFORT, est_power_law, est_sigma_y, robust_fit

MODEL_NAME = "herschel_bulkley"
PARAMS = ["sigma_y", "K", "n"]
SCORECARD_PARAMS = ["sigma_y", "K", "n"]

LOG_PARAMS = ("sigma_y", "K")
BOUNDS = {
    "sigma_y": (1e-12, np.inf),
    "K": (1e-12, np.inf),
    "n": (0.01, 2.0),
}
# exact reduction: sigma_y -> 0 recovers the power law
PARENT = "power_law"
PARENT_EXACT = True


def _func(x, sigma_y, K, n):
    return sigma_y + K * x ** n


def get_equation_latex() -> str:
    return "σ = σ_y + K·γ̇ⁿ"


def initial_guess(x, y, eta) -> dict:
    sigma_y = est_sigma_y(x, y)
    # strip the plateau before reading the power-law slope
    residual_stress = np.maximum(y - 0.9 * sigma_y, y.max() * 1e-6)
    K, n = est_power_law(x, residual_stress)
    return {"sigma_y": sigma_y, "K": K, "n": n}


def seed_from_parent(pv, x, y, eta) -> dict:
    return {"sigma_y": max(y.max() * 1e-10, 1e-12), "K": pv["K"], "n": pv["n"]}


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)
