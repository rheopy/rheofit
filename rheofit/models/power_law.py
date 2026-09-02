"""
Power Law — simple shear-thinning, no yield stress
  σ = K·γ̇ⁿ
"""
import numpy as np

from ._fitcore import DEFAULT_EFFORT, est_power_law, robust_fit

MODEL_NAME = "power_law"
PARAMS = ["K", "n"]
SCORECARD_PARAMS = ["K", "n"]

LOG_PARAMS = ("K",)
BOUNDS = {
    "K": (1e-12, np.inf),
    "n": (0.01, 2.0),
}
PARENT = None


def _func(x, K, n):
    return K * x ** n


def get_equation_latex() -> str:
    return "σ = K·γ̇ⁿ"


def initial_guess(x, y, eta) -> dict:
    K, n = est_power_law(x, y)
    return {"K": K, "n": n}


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)
