"""
TC-Carreau — yield stress + single Carreau shear-thinning
  σ = σ_y + σ_y·(γ̇/γ̇_c)^½ + η₀·γ̇·[1+(λ·γ̇)²]^(-½)
"""
import numpy as np

from ._fitcore import (DEFAULT_EFFORT, est_eta_0, est_gamma_dot_c, est_lambda,
                       est_sigma_y, robust_fit)

MODEL_NAME = "tc_carreau"
PARAMS = ["sigma_y", "gamma_dot_c", "eta_0", "lambda_val"]
SCORECARD_PARAMS = ["sigma_y", "eta_0"]

LOG_PARAMS = ("sigma_y", "gamma_dot_c", "eta_0", "lambda_val")
BOUNDS = {
    "sigma_y": (1e-12, np.inf),
    "gamma_dot_c": (1e-6, np.inf),
    "eta_0": (1e-12, np.inf),
    "lambda_val": (1e-12, np.inf),
}
# exact reduction: lambda -> 0 turns the Carreau term into eta_bg * gamma_dot
PARENT = "tc"
PARENT_EXACT = True


def _func(x, sigma_y, gamma_dot_c, eta_0, lambda_val):
    tc = sigma_y + sigma_y * np.sqrt(x / gamma_dot_c)
    carreau = eta_0 * x * (1.0 + (lambda_val * x) ** 2) ** (-0.5)
    return tc + carreau


def get_equation_latex() -> str:
    return "σ = σ_y + σ_y·(γ̇/γ̇_c)^½ + η₀·γ̇·[1+(λ·γ̇)²]^(-½)"


def initial_guess(x, y, eta) -> dict:
    return {
        "sigma_y": est_sigma_y(x, y),
        "gamma_dot_c": est_gamma_dot_c(x),
        "eta_0": est_eta_0(x, eta),
        "lambda_val": est_lambda(x, eta),
    }


def seed_from_parent(pv, x, y, eta) -> dict:
    return {
        "sigma_y": pv["sigma_y"],
        "gamma_dot_c": pv["gamma_dot_c"],
        "eta_0": pv["eta_bg"],
        "lambda_val": 1e-12,
    }


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)
