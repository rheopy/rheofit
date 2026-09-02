"""
Carreau — single shear-thinning component
  σ = η₀·γ̇·[1+(λ·γ̇)²]^((n-1)/2)
"""
import numpy as np

from ._fitcore import (DEFAULT_EFFORT, est_eta_0, est_lambda, est_power_law,
                       robust_fit)

MODEL_NAME = "carreau"
PARAMS = ["eta_0", "lambda_val", "n"]
SCORECARD_PARAMS = ["eta_0"]

LOG_PARAMS = ("eta_0", "lambda_val")
BOUNDS = {
    "eta_0": (1e-12, np.inf),
    "lambda_val": (1e-12, np.inf),
    "n": (0.01, 1.0),
}
PARENT = None


def _func(x, eta_0, lambda_val, n):
    return eta_0 * x * (1.0 + (lambda_val * x) ** 2) ** ((n - 1.0) / 2.0)


def get_equation_latex() -> str:
    return "σ = η₀·γ̇·[1+(λ·γ̇)²]^((n-1)/2)"


def initial_guess(x, y, eta) -> dict:
    # the high-rate power-law slope of stress is the Carreau exponent n
    _, n_hi = est_power_law(x, y)
    return {
        "eta_0": est_eta_0(x, eta),
        "lambda_val": est_lambda(x, eta),
        "n": float(np.clip(n_hi, 0.01, 1.0)),
    }


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)
