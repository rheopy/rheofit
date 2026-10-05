"""
Carreau — single shear-thinning component
  σ = η₀·γ̇·[1+(λ·γ̇)²]^((n-1)/2)
"""
import numpy as np

from rheomodel import get_model as _get_model

from ._fitcore import (DEFAULT_EFFORT, est_eta_0, est_lambda, est_power_law,
                       robust_fit)
_model = _get_model("carreau")

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
