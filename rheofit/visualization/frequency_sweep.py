"""Frequency sweep view: G' and G'' versus angular frequency.

No fitting models exist for oscillatory data yet, so this module is
visualisation only -- passing ``fits`` raises a clear error.
"""
from __future__ import annotations

import numpy as np

from . import _plotcore as core

TEST_NAME = "frequency_sweep"
X_COLUMN = "Angular frequency / rad/s"
Y_COLUMNS = {
    "storage": "Storage modulus / Pa",
    "loss": "Loss modulus / Pa",
    "tan_delta": "Tan(delta)",
    "complex_viscosity": "Complex viscosity / Pa.s",
}
SUPPORTS_FIT = False

AXES = {
    "xlabel": "angular frequency [rad/s]",
    "ylabel": "modulus [Pa]",
    "xscale": "log",
    "yscale": "log",
}

_SECONDARY = {
    "tan_delta": ("Tan(delta)", "tan(delta)", "log"),
    "complex_viscosity": ("Complex viscosity / Pa.s", "|\u03b7*| [Pa.s]", "log"),
}

# Neutral grey: red and blue are reserved for G' and G''.
_SECONDARY_COLOR = "#555555"


def describe() -> dict:
    return {
        "name": TEST_NAME,
        "x": X_COLUMN,
        "y": dict(Y_COLUMNS),
        "supports_fit": SUPPORTS_FIT,
        "axes": dict(AXES),
    }


def plot(data=None, fits=None, *, secondary=None, show_crossover=False,
         title="", figsize=None, legend=True):
    """Plot one or more frequency sweeps.

    Parameters
    ----------
    secondary
        ``"tan_delta"`` or ``"complex_viscosity"`` to add a twinned right axis.
    show_crossover
        Annotate the G'/G'' crossover frequency (the terminal relaxation time is
        ``1 / omega_c``) when one exists inside the measured window.
    """
    if fits is not None:
        raise ValueError(
            "frequency_sweep is visualisation only: rheofit has no oscillatory "
            "models yet, so 'fits' cannot be plotted."
        )
    if secondary is not None and secondary not in _SECONDARY:
        raise ValueError(f"secondary must be one of {sorted(_SECONDARY)} or None")

    datasets = core.normalize_datasets(data)
    if not datasets:
        raise ValueError("nothing to plot: provide data")

    labels = list(datasets)
    fig, ax, _ = core.make_panels(with_residuals=False, figsize=figsize)
    ax_sec = ax.twinx() if secondary else None
    n = len(labels)

    for i, label in enumerate(labels):
        df = datasets[label]
        core.require_columns(df, [X_COLUMN, Y_COLUMNS["storage"], Y_COLUMNS["loss"]], label, TEST_NAME)
        marker = core.marker_for(i)
        c_storage = core.color_for("storage", i, n)
        c_loss = core.color_for("loss", i, n)
        x, g_p, g_pp = core.sorted_xy(df, X_COLUMN, Y_COLUMNS["storage"], Y_COLUMNS["loss"])

        # Filled = elastic G' (red), open = viscous G'' (blue).
        ax.plot(x, g_p, marker, ms=5, color=c_storage, ls="none")
        ax.plot(x, g_pp, marker, ms=5, mfc="none", mec=c_loss, ls="none")

        if ax_sec is not None:
            col, _, _ = _SECONDARY[secondary]
            core.require_columns(df, [col], label, TEST_NAME)
            xs, ys = core.sorted_xy(df, X_COLUMN, col)
            ax_sec.plot(xs, ys, marker=marker, ms=4, lw=1.0, ls=core.linestyle_for(i),
                        color=_SECONDARY_COLOR, alpha=0.55)

        if show_crossover:
            omega_c = core.log_crossover(x, g_p, g_pp)
            if omega_c is not None:
                ax.axvline(omega_c, color=c_storage, ls=":", lw=1.2)
                # Flip the label inward when the crossover sits near the right edge.
                span = np.log10(x.max() / x.min()) or 1.0
                near_right = np.log10(omega_c / x.min()) / span > 0.65
                ax.annotate(
                    f"\u03c9c = {omega_c:.3g} rad/s\n\u03c4 = {1 / omega_c:.3g} s",
                    xy=(omega_c, 0.02), xycoords=ax.get_xaxis_transform(),
                    xytext=(-5 if near_right else 5, 0), textcoords="offset points",
                    fontsize=7.5, color=c_storage, family="monospace",
                    ha="right" if near_right else "left", va="bottom",
                )

    core.style_axis(ax, xlabel=AXES["xlabel"], ylabel=AXES["ylabel"],
                    xscale=AXES["xscale"], yscale=AXES["yscale"])
    if ax_sec is not None:
        _, sec_label, sec_scale = _SECONDARY[secondary]
        ax_sec.set_yscale(sec_scale)
        ax_sec.set_ylabel(sec_label)
        core.label_axis_color(ax_sec, _SECONDARY_COLOR)

    if legend:
        handles = core.quantity_handles(
            [("storage", "G' (elastic)", True), ("loss", "G'' (viscous)", False)]
        )
        if len(labels) > 1:
            handles += core.dataset_handles(labels, {k: k for k in labels})
        ax.legend(handles=handles, loc="best", fontsize=8, framealpha=0.9)
    if title:
        fig.suptitle(title, fontsize=11, family="monospace")
    return fig
