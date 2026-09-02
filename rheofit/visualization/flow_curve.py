"""Flow curve view: stress and viscosity versus shear rate, with optional fits.

Supplying ``fits`` switches the figure from one panel to two, adding the
relative-residual strip underneath.
"""
from __future__ import annotations

import numpy as np

from . import _plotcore as core

TEST_NAME = "flow_curve"
X_COLUMN = "Shear rate / 1/s"
Y_COLUMNS = {"primary": "Stress / Pa", "secondary": "Viscosity / Pa.s"}
SUPPORTS_FIT = True

AXES = {
    "xlabel": "shear rate [1/s]",
    "ylabel": "stress [Pa]",
    "ylabel_secondary": "viscosity [Pa.s]",
    "xscale": "log",
    "yscale": "log",
}


def describe() -> dict:
    return {
        "name": TEST_NAME,
        "x": X_COLUMN,
        "y": dict(Y_COLUMNS),
        "supports_fit": SUPPORTS_FIT,
        "axes": dict(AXES),
    }


def plot(data=None, fits=None, *, y="both", exp_err=0.05, title="", figsize=None, legend=True):
    """Plot one or more flow curves, optionally with their fits.

    Parameters
    ----------
    data
        A DataFrame, a list of them, or a ``{label: DataFrame}`` mapping. May be
        omitted when ``fits`` is given, since a fit result carries its own data.
    fits
        A fit-result dict from :func:`rheofit.fit`, a list, or a
        ``{label: fit}`` mapping aligned to ``data``. When present, a residual
        panel is added.
    y
        ``"stress"``, ``"viscosity"`` or ``"both"`` (stress left axis, viscosity
        on a twinned right axis).
    """
    if y not in {"stress", "viscosity", "both"}:
        raise ValueError("y must be 'stress', 'viscosity' or 'both'")

    datasets = core.normalize_datasets(data)
    fit_map = core.normalize_fits(fits, list(datasets))

    if not datasets:
        if not fit_map:
            raise ValueError("nothing to plot: provide data, fits, or both")
        datasets = core.datasets_from_fits(fit_map, X_COLUMN, Y_COLUMNS["primary"])

    labels = core.labels_from(datasets, fit_map)
    fig, ax, ax_res = core.make_panels(with_residuals=bool(fit_map), figsize=figsize)

    show_stress = y in {"stress", "both"}
    show_eta = y in {"viscosity", "both"}
    ax_eta = ax.twinx() if (show_stress and show_eta) else None
    eta_axis = ax_eta if ax_eta is not None else ax

    legend_text = core.redchi_legend_labels(labels, fit_map)
    n = len(labels)

    for i, label in enumerate(labels):
        df = datasets[label]
        core.require_columns(df, [X_COLUMN, Y_COLUMNS["primary"]], label, TEST_NAME)
        marker = core.marker_for(i)
        c_stress = core.color_for("stress", i, n)
        c_eta = core.color_for("viscosity", i, n)
        x, stress = core.sorted_xy(df, X_COLUMN, Y_COLUMNS["primary"])
        eta = np.divide(stress, x, out=np.full_like(stress, np.nan), where=x > 0)

        if show_stress:
            ax.plot(x, stress, marker, ms=5, mfc="none", mec=c_stress, ls="none")
        if show_eta:
            eta_axis.plot(x, eta, marker, ms=4.5, mfc="none", mec=c_eta, ls="none", alpha=0.85)

        fit = fit_map.get(label)
        if fit is not None:
            xf = np.asarray(fit["x"], float)
            yf = np.asarray(fit["y_fit"], float)
            order = np.argsort(xf)
            xf, yf = xf[order], yf[order]
            ls = core.linestyle_for(i)
            if show_stress:
                ax.plot(xf, yf, ls=ls, lw=1.6, color=c_stress)
            if show_eta:
                eta_axis.plot(xf, yf / xf, ls=ls, lw=1.3, color=c_eta, alpha=0.9)

    core.style_axis(
        ax,
        xlabel=None if ax_res is not None else AXES["xlabel"],
        ylabel=AXES["ylabel"] if show_stress else AXES["ylabel_secondary"],
        xscale=AXES["xscale"], yscale=AXES["yscale"],
    )
    # Tint the axis labels so the red/blue convention needs no legend lookup.
    if show_stress and show_eta:
        core.label_axis_color(ax, core.COLORS["stress"])
    if ax_eta is not None:
        ax_eta.set_yscale("log")
        ax_eta.set_ylabel(AXES["ylabel_secondary"])
        core.label_axis_color(ax_eta, core.COLORS["viscosity"])

    if ax_res is not None:
        core.plot_residuals(ax_res, fit_map, labels, exp_err=exp_err)
        ax_res.set_xscale(AXES["xscale"])
        ax_res.set_xlabel(AXES["xlabel"])
        if len(fit_map) == 1:
            core.param_textbox(ax_res, next(iter(fit_map.values())))

    if legend:
        # Marker shape identifies the dataset; colour identifies the quantity.
        handles = core.dataset_handles(labels, legend_text)
        if show_stress and show_eta:
            handles += core.quantity_handles(
                [("stress", "stress", False), ("viscosity", "viscosity", False)]
            )
        ax.legend(handles=handles, loc="best", fontsize=8, framealpha=0.9)
    if title:
        fig.suptitle(title, fontsize=11, family="monospace")
    return fig
