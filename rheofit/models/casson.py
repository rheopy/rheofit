"""
Casson — yield stress + square-root plastic flow
  σ = (√σ_y + √(K·γ̇))²
"""
import numpy as np

from ._fitcore import DEFAULT_EFFORT, est_sigma_y, robust_fit

MODEL_NAME = "casson"
PARAMS = ["sigma_y", "K"]
SCORECARD_PARAMS = ["sigma_y", "K"]

LOG_PARAMS = ("sigma_y", "K")
BOUNDS = {
    "sigma_y": (1e-12, np.inf),
    "K": (1e-12, np.inf),
}
PARENT = None


def _func(x, sigma_y, K):
    return (np.sqrt(sigma_y) + np.sqrt(K * x)) ** 2


def get_equation_latex() -> str:
    return "σ = (\\sqrt{\\sigma_y} + \\sqrt{K\\cdot\\dot\\gamma})^2"


def initial_guess(x, y, eta) -> dict:
    sigma_y = est_sigma_y(x, y)
    sqrt_y = np.sqrt(np.maximum(y, 1e-12))
    sqrt_sy = np.sqrt(min(sigma_y, y.max() * 0.9))
    sqrt_res = np.maximum(sqrt_y - sqrt_sy, 1e-6)
    slope = np.polyfit(np.sqrt(x), sqrt_res, 1)[0]
    K = max(slope ** 2, 1e-12)
    return {"sigma_y": sigma_y, "K": K}


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)

