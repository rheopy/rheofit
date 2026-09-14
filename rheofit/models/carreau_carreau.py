"""
Carreau-Carreau — two shear-thinning components, no yield stress
  σ = η₀,₁·γ̇·[1+(λ₁·γ̇)²]^(-¼) + η₀,₂·γ̇·[1+(λ₂·γ̇)²]^(-½)
"""
import numpy as np

from ._fitcore import DEFAULT_EFFORT, est_eta_0, est_lambda, robust_fit

MODEL_NAME = "carreau_carreau"
PARAMS = ["eta_0_1", "lambda_val_1", "eta_0_2", "lambda_val_2"]
SCORECARD_PARAMS = ["eta_0_1", "eta_0_2"]

LOG_PARAMS = ("eta_0_1", "lambda_val_1", "eta_0_2", "lambda_val_2")
BOUNDS = {
    "eta_0_1": (1e-12, np.inf),
    "lambda_val_1": (1e-12, np.inf),
    "eta_0_2": (1e-12, np.inf),
    "lambda_val_2": (1e-12, np.inf),
}
# advisory seed only: the fixed exponents mean this is not an exact reduction
PARENT = "carreau"
PARENT_EXACT = False


def _func(x, eta_0_1, lambda_val_1, eta_0_2, lambda_val_2):
    c1 = eta_0_1 * x * (1.0 + (lambda_val_1 * x) ** 2) ** (-0.25)
    c2 = eta_0_2 * x * (1.0 + (lambda_val_2 * x) ** 2) ** (-0.5)
    return c1 + c2


def get_equation_latex() -> str:
    return r"$\sigma = \eta_{0,1} \dot{\gamma} \left[1+(\lambda_1 \dot{\gamma})^2\right]^{-1/4} + \eta_{0,2} \dot{\gamma} \left[1+(\lambda_2 \dot{\gamma})^2\right]^{-1/2}$"


def initial_guess(x, y, eta) -> dict:
    eta_0 = est_eta_0(x, eta)
    lam = est_lambda(x, eta)
    # split the plateau between the two components, separating their time constants
    return {
        "eta_0_1": eta_0 * 0.3,
        "lambda_val_1": lam * 0.1,
        "eta_0_2": eta_0 * 0.7,
        "lambda_val_2": lam,
    }


def seed_from_parent(pv, x, y, eta) -> dict:
    return {
        "eta_0_1": max(pv["eta_0"] * 1e-6, 1e-12),
        "lambda_val_1": pv["lambda_val"],
        "eta_0_2": pv["eta_0"],
        "lambda_val_2": pv["lambda_val"],
    }


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)
