"""
Casson — yield stress + square-root plastic flow
  σ = (√σ_y + √(K·γ̇))²
"""
import numpy as np

from rheomodel import get_model as _get_model

from ._fitcore import DEFAULT_EFFORT, est_sigma_y, robust_fit

MODEL_NAME = "casson"
PARAMS = ["sigma_y", "K"]
SCORECARD_PARAMS = ["sigma_y", "K"]

LOG_PARAMS = ("sigma_y", "K")
_model = _get_model("casson")

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

