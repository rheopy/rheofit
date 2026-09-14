"""
Bingham — yield stress + linear plastic flow
  σ = σ_y + K·γ̇
"""
import numpy as np

from ._fitcore import DEFAULT_EFFORT, est_power_law, est_sigma_y, robust_fit

MODEL_NAME = "bingham"
PARAMS = ["sigma_y", "K"]
SCORECARD_PARAMS = ["sigma_y", "K"]

LOG_PARAMS = ("sigma_y", "K")
BOUNDS = {
    "sigma_y": (1e-12, np.inf),
    "K": (1e-12, np.inf),
}
PARENT = None


def _func(x, sigma_y, K):
    return sigma_y + K * x


def get_equation_latex() -> str:
    return "σ = σ_y + K·γ̇"


def initial_guess(x, y, eta) -> dict:
    sigma_y = est_sigma_y(x, y)
    residual_stress = np.maximum(y - 0.9 * sigma_y, y.max() * 1e-6)
    K, _ = est_power_law(x, residual_stress)
    return {"sigma_y": sigma_y, "K": K}


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)

