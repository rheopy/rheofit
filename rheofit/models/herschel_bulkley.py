"""
Herschel-Bulkley — yield stress + power-law flow
  σ = σ_y + K·γ̇ⁿ
"""
import numpy as np

from rheomodel import get_model as _get_model

from ._fitcore import DEFAULT_EFFORT, est_power_law, est_sigma_y, robust_fit

MODEL_NAME = "herschel_bulkley"
PARAMS = ["sigma_y", "K", "n"]
SCORECARD_PARAMS = ["sigma_y", "K", "n"]

LOG_PARAMS = ("sigma_y", "K")
_model = _get_model("herschel_bulkley")

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
    # strip the plateau before reading the power-law slope
    residual_stress = np.maximum(y - 0.9 * sigma_y, y.max() * 1e-6)
    K, n = est_power_law(x, residual_stress)
    return {"sigma_y": sigma_y, "K": K, "n": n}


def seed_from_parent(pv, x, y, eta) -> dict:
    return {"sigma_y": pv["sigma_y"], "K": pv["K"], "n": 1.0}


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)
