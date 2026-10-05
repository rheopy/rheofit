"""
TC-Carreau — yield stress + single Carreau shear-thinning
  σ = σ_y + σ_y·(γ̇/γ̇_c)^½ + η₀·γ̇·[1+(λ·γ̇)²]^(-½)
"""

from rheomodel import get_model as _get_model

from ._fitcore import (DEFAULT_EFFORT, est_eta_0, est_gamma_dot_c, est_lambda,
                       est_sigma_y, robust_fit)
_model = _get_model("tc_carreau")

# --- model physics (equations, parameters, bounds, citations): rheomodel ---
MODEL_NAME = _model.MODEL_NAME
PARAMS = _model.PARAMS
SCORECARD_PARAMS = _model.SCORECARD_PARAMS
LOG_PARAMS = _model.LOG_PARAMS
BOUNDS = _model.BOUNDS
PARENT = _model.PARENT
PARENT_EXACT = getattr(_model, "PARENT_EXACT", False)
CITATION = _model.CITATION
PARAM_INFO = _model.PARAM_INFO

equation = _model.equation
_func = equation  # the name _fitcore calls
get_equation_latex = _model.get_equation_latex


# --- fitting machinery (stays in rheofit) ---
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
