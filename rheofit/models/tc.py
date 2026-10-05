"""
TC — Two-Component (yield stress + Newtonian background)
  σ = σ_y + σ_y·(γ̇/γ̇_c)^½ + η_bg·γ̇
"""

from rheomodel import get_model as _get_model

from ._fitcore import (DEFAULT_EFFORT, est_eta_bg, est_gamma_dot_c,
                       est_sigma_y, robust_fit)
_model = _get_model("tc")

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
        "eta_bg": est_eta_bg(x, y),
    }


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)
