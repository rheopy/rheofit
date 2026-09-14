"""rheofit — fit flow curves (viscosity vs shear rate) to rheological models.

A flow curve is the fingerprint of a non-Newtonian fluid. Fitting it with a
physically-based model quantifies material properties (yield stress, zero-shear
viscosity, relaxation time, thinning exponent), gives a concise description of
the material, and — when tied to the formulation — tells a formulator which
lever to move to hit a property target.

Typical use::

    import rheofit

    rheofit.print_steps("sample.json")                  # 1. discover steps
    df = rheofit.load_step("sample.json", 0)            # 2. load one step
    res = rheofit.fit(df, "tc")                         # 3. fit it
    rheofit.plot(df, fits=res)                          # 4. look at it
    a = rheofit.analyze("sample.json", steps=[0, 2],    # or do it all at once
                        model="tc", labels=["25C", "40C"])

Every fit minimises the *relative* residual ``(model - data) / |data|``, so
``RedChi2`` is dimensionless and comparable across steps, samples and models.
"""
from __future__ import annotations

from .analysis import Analysis, analyze, fit, get_model, list_models, model_info, print_steps
from .io import (DEMO_SAMPLE_NAME, demo_source, detect_test_type, discover_steps,
                 load_step, load_steps)
from .cli import install_skill
from .models import MODELS
from .visualization import PLOTS, get_plot, list_plots, plot, plot_info

__version__ = "0.1.0"

__all__ = [
    "Analysis",
    "DEMO_SAMPLE_NAME",
    "MODELS",
    "PLOTS",
    "analyze",
    "demo_source",
    "detect_test_type",
    "discover_steps",
    "fit",
    "get_model",
    "get_plot",
    "install_skill",
    "list_models",
    "list_plots",
    "load_step",
    "load_steps",
    "model_info",
    "plot",
    "plot_info",
    "print_steps",
    "__version__",
]
