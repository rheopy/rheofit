"""Plotting for rheofit, one module per measurement type.

Mirrors :mod:`rheofit.models`: each test type is a module registered in
:data:`PLOTS`, exposing ``TEST_NAME``, ``X_COLUMN``, ``Y_COLUMNS``,
``SUPPORTS_FIT``, ``AXES``, ``plot()`` and ``describe()``.

Every ``plot()`` accepts one dataset or many (a list or a ``{label: DataFrame}``
mapping). ``flow_curve`` additionally accepts ``fits``; supplying them adds the
residual panel. Frequency and amplitude sweeps are visualisation only for now.

Typical use::

    import rheofit

    df = rheofit.load_step("sample.json", 0)
    rheofit.plot(df)                                  # test type auto-detected
    rheofit.plot({"25C": df1, "40C": df2},
                 fits={"25C": res1, "40C": res2})     # overlay with residuals
"""
from __future__ import annotations

from . import amplitude_sweep, flow_curve, frequency_sweep

PLOTS: dict = {
    "amplitude_sweep": amplitude_sweep,
    "flow_curve": flow_curve,
    "frequency_sweep": frequency_sweep,
}


def list_plots() -> list[str]:
    """Names of the available measurement-type views."""
    return sorted(PLOTS)


def get_plot(name: str):
    """Return the plotting module registered under ``name``."""
    try:
        return PLOTS[name]
    except KeyError:
        raise ValueError(
            f"Unknown test type '{name}'. Available: {', '.join(list_plots())}"
        ) from None


def plot_info(name: str) -> dict:
    """Introspect a view: expected columns, axes and whether fits are supported."""
    return get_plot(name).describe()


def _infer_test_type(data) -> str:
    """Read the test type recorded by ``load_step`` on the first dataset."""
    from ._plotcore import normalize_datasets

    datasets = normalize_datasets(data)
    for df in datasets.values():
        test_type = df.attrs.get("test_type")
        if test_type in PLOTS:
            return test_type
    raise ValueError(
        "Could not infer the test type. Pass test_type=... explicitly "
        f"(one of: {', '.join(list_plots())})."
    )


def plot(data=None, fits=None, *, test_type: str | None = None, **kwargs):
    """Plot ``data`` using the view for its measurement type.

    ``test_type`` is inferred from ``df.attrs['test_type']`` (set by
    :func:`rheofit.load_step`) unless given explicitly. Remaining keyword
    arguments are forwarded to the selected module's ``plot()``.
    """
    if test_type is None:
        test_type = _infer_test_type(data)
    module = get_plot(test_type)
    if fits is not None and not module.SUPPORTS_FIT:
        raise ValueError(
            f"'{test_type}' does not support fits: rheofit has no models for this "
            "measurement type yet."
        )
    return module.plot(data, fits, **kwargs)


__all__ = ["PLOTS", "get_plot", "list_plots", "plot", "plot_info"]
