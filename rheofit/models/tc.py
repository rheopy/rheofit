"""
TC — Two-Component (yield stress + Newtonian background)
  σ = σ_y + σ_y·(γ̇/γ̇_c)^½ + η_bg·γ̇
"""
import numpy as np

from ._fitcore import (DEFAULT_EFFORT, est_eta_bg, est_gamma_dot_c,
                       est_sigma_y, robust_fit)

MODEL_NAME = "tc"
PARAMS = ["sigma_y", "gamma_dot_c", "eta_bg"]
SCORECARD_PARAMS = ["sigma_y", "eta_bg"]

LOG_PARAMS = ("sigma_y", "gamma_dot_c", "eta_bg")
BOUNDS = {
    "sigma_y": (1e-12, np.inf),
    "gamma_dot_c": (1e-6, np.inf),
    "eta_bg": (1e-12, np.inf),
}
PARENT = None


def _func(x, sigma_y, gamma_dot_c, eta_bg):
    return sigma_y + sigma_y * np.sqrt(x / gamma_dot_c) + eta_bg * x


def get_equation_latex() -> str:
    return "σ = σ_y + σ_y·(γ̇/γ̇_c)^½ + η_bg·γ̇"


def initial_guess(x, y, eta) -> dict:
    return {
        "sigma_y": est_sigma_y(x, y),
        "gamma_dot_c": est_gamma_dot_c(x),
        "eta_bg": est_eta_bg(x, y),
    }


def fit_model(df, effort: str = DEFAULT_EFFORT, seed: int = 0) -> dict:
    import sys
    return robust_fit(sys.modules[__name__], df, effort=effort, seed=seed)
