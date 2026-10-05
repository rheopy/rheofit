"""
Power Law — simple shear-thinning, no yield stress
  σ = K·γ̇ⁿ
"""

from rheomodel import get_model as _get_model

from ._fitcore import DEFAULT_EFFORT, est_power_law, robust_fit

MODEL_NAME = "power_law"
PARAMS = ["K", "n"]
SCORECARD_PARAMS = ["K", "n"]

LOG_PARAMS = ("K",)
_model = _get_model("power_law")

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
    K, n = est_power_law(x, y)
    return {"K": K, "n": n}


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)
