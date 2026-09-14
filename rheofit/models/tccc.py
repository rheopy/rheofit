"""
TCCC — Three-Component Carreau-Carreau
  σ = σ_y + σ_y·(γ̇/γ̇_c)^½ + η₀,₁·γ̇·[1+(λ₁·γ̇)²]^(-¼) + η₀,₂·γ̇·[1+(λ₂·γ̇)²]^(-½)

Fit backend: scipy.optimize.least_squares (no lmfit, no tadatakit).
"""
import numpy as np

from ._fitcore import (DEFAULT_EFFORT, est_eta_0, est_gamma_dot_c, est_lambda,
                       est_sigma_y, robust_fit)

MODEL_NAME = "tccc"
PARAMS = ["sigma_y", "gamma_dot_c", "eta_0_1", "lambda_val_1", "eta_0_2", "lambda_val_2"]
SCORECARD_PARAMS = ["sigma_y", "eta_0_1", "eta_0_2"]

LOG_PARAMS = ("sigma_y", "gamma_dot_c", "eta_0_1", "lambda_val_1",
              "eta_0_2", "lambda_val_2")
BOUNDS = {
    "sigma_y": (1e-12, np.inf),
    "gamma_dot_c": (1e-6, np.inf),
    "eta_0_1": (1e-12, np.inf),
    "lambda_val_1": (1e-12, np.inf),
    "eta_0_2": (1e-12, np.inf),
    "lambda_val_2": (1e-12, np.inf),
}
# exact reduction: eta_0_1 -> 0 recovers TC-Carreau
PARENT = "tc_carreau"
PARENT_EXACT = True


def _func(x, sigma_y, gamma_dot_c, eta_0_1, lambda_val_1, eta_0_2, lambda_val_2):
    tc = sigma_y + sigma_y * np.sqrt(x / gamma_dot_c)
    c1 = eta_0_1 * x * (1.0 + (lambda_val_1 * x) ** 2) ** (-0.25)
    c2 = eta_0_2 * x * (1.0 + (lambda_val_2 * x) ** 2) ** (-0.5)
    return tc + c1 + c2


def get_equation_latex() -> str:
    return "σ = σ_y + σ_y·(γ̇/γ̇_c)^½ + η₀,₁·γ̇·[1+(λ₁·γ̇)²]^(-¼) + η₀,₂·γ̇·[1+(λ₂·γ̇)²]^(-½)"


def initial_guess(x, y, eta) -> dict:
    eta_0 = est_eta_0(x, eta)
    lam = est_lambda(x, eta)
    return {
        "sigma_y": est_sigma_y(x, y),
        "gamma_dot_c": est_gamma_dot_c(x),
        "eta_0_1": eta_0 * 0.3,
        "lambda_val_1": lam * 0.1,
        "eta_0_2": eta_0 * 0.7,
        "lambda_val_2": lam,
    }


def seed_from_parent(pv, x, y, eta) -> dict:
    return {
        "sigma_y": pv["sigma_y"],
        "gamma_dot_c": pv["gamma_dot_c"],
        "eta_0_1": max(pv["eta_0"] * 1e-6, 1e-12),
        "lambda_val_1": pv["lambda_val"],
        "eta_0_2": pv["eta_0"],
        "lambda_val_2": pv["lambda_val"],
    }


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)
