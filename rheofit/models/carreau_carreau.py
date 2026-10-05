"""
Carreau-Carreau — two shear-thinning components, no yield stress
  σ = η₀,₁·γ̇·[1+(λ₁·γ̇)²]^(-¼) + η₀,₂·γ̇·[1+(λ₂·γ̇)²]^(-½)
"""

from rheomodel import get_model as _get_model

from ._fitcore import DEFAULT_EFFORT, est_eta_0, est_lambda, robust_fit

MODEL_NAME = "carreau_carreau"
PARAMS = ["eta_0_1", "lambda_val_1", "eta_0_2", "lambda_val_2"]
SCORECARD_PARAMS = ["eta_0_1", "eta_0_2"]

LOG_PARAMS = ("eta_0_1", "lambda_val_1", "eta_0_2", "lambda_val_2")
_model = _get_model("carreau_carreau")

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
