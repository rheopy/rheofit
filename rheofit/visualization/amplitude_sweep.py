"""Amplitude sweep view: G' and G'' versus oscillation strain (or stress).

No fitting models exist for oscillatory data yet, so this module is
visualisation only. It can, however, mark two model-free landmarks read
straight off the curve: the end of the linear viscoelastic region and the flow
point where G' and G'' cross.
"""
from __future__ import annotations

import numpy as np

from . import _plotcore as core

TEST_NAME = "amplitude_sweep"
X_COLUMN = "Oscillation strain / %"
Y_COLUMNS = {
    "storage": "Storage modulus / Pa",
    "loss": "Loss modulus / Pa",
}
X_ALTERNATIVES = {
    "strain": ("Oscillation strain / %", "oscillation strain [%]"),
    "stress": ("Oscillation stress / Pa", "oscillation stress [Pa]"),
}
SUPPORTS_FIT = False

AXES = {
    "xlabel": "oscillation strain [%]",
    "ylabel": "modulus [Pa]",
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


def lvr_limit(x: np.ndarray, g_p: np.ndarray, tol: float = 0.05,
              n_plateau: int = 5) -> tuple[float | None, float]:
    """End of the linear viscoelastic region.

    The plateau modulus is the median G' over the ``n_plateau`` lowest-amplitude
    points; the LVR ends at the first amplitude where G' falls more than ``tol``
    below it *and stays below* for the rest of the sweep. Requiring a sustained
    drop matters because G' is often scattered by several percent at low
    amplitude, where an isolated dip would otherwise be read as yielding.

    Returns ``(x_limit_or_None, plateau_modulus)``.
    """
    if len(x) < 3:
        return None, float("nan")
    plateau = float(np.median(g_p[: max(1, min(n_plateau, len(g_p)))]))
    if not np.isfinite(plateau) or plateau <= 0:
        return None, float("nan")

    below = g_p < (1.0 - tol) * plateau
    # First index from which every later point is also below the threshold.
    sustained = np.flatnonzero(below & (np.cumsum(~below[::-1])[::-1] == 0))
    if len(sustained) == 0:
        return None, plateau
    return float(x[sustained[0]]), plateau


def plot(data=None, fits=None, *, x="strain", show_lvr=False, lvr_tol=0.05,
         show_flow_point=False, title="", figsize=None, legend=True):
    """Plot one or more amplitude sweeps.

    Parameters
    ----------
    x
        ``"strain"`` (default) or ``"stress"`` for the control axis.
    show_lvr
        Mark the end of the linear viscoelastic region (see :func:`lvr_limit`).
    show_flow_point
        Mark the G'/G'' crossover, i.e. the yield/flow point.
    """
    if fits is not None:
        raise ValueError(
            "amplitude_sweep is visualisation only: rheofit has no oscillatory "
            "models yet, so 'fits' cannot be plotted."
        )
    if x not in X_ALTERNATIVES:
        raise ValueError(f"x must be one of {sorted(X_ALTERNATIVES)}")

    x_col, xlabel = X_ALTERNATIVES[x]
    datasets = core.normalize_datasets(data)
    if not datasets:
        raise ValueError("nothing to plot: provide data")

    labels = list(datasets)
    fig, ax, _ = core.make_panels(with_residuals=False, figsize=figsize)
    n = len(labels)

    for i, label in enumerate(labels):
        df = datasets[label]
        core.require_columns(df, [x_col, Y_COLUMNS["storage"], Y_COLUMNS["loss"]], label, TEST_NAME)
        marker = core.marker_for(i)
        c_storage = core.color_for("storage", i, n)
        c_loss = core.color_for("loss", i, n)
        xv, g_p, g_pp = core.sorted_xy(df, x_col, Y_COLUMNS["storage"], Y_COLUMNS["loss"])

        # Filled = elastic G' (red), open = viscous G'' (blue).
        ax.plot(xv, g_p, marker, ms=5, color=c_storage, ls="none")
        ax.plot(xv, g_pp, marker, ms=5, mfc="none", mec=c_loss, ls="none")

        if show_lvr:
            x_lvr, plateau = lvr_limit(xv, g_p, tol=lvr_tol)
            if np.isfinite(plateau):
                ax.axhline(plateau, color=c_storage, ls="--", lw=0.9, alpha=0.5)
            if x_lvr is not None:
                ax.axvline(x_lvr, color=c_storage, ls=":", lw=1.2)
                ax.annotate(
                    f"LVR end {x_lvr:.3g}\nG0 = {plateau:.3g} Pa",
                    xy=(x_lvr, plateau), xytext=(4, 8), textcoords="offset points",
                    fontsize=7.5, color=c_storage, family="monospace",
                )

        if show_flow_point:
            x_flow = core.log_crossover(xv, g_p, g_pp)
            if x_flow is not None:
                g_flow = np.interp(np.log10(x_flow), np.log10(xv), g_p)
                ax.plot([x_flow], [g_flow], "*", ms=13, color=c_storage,
                        mec="black", mew=0.6)
                ax.annotate(
                    f"flow point {x_flow:.3g}",
                    xy=(x_flow, g_flow),
                    xytext=(6, -14), textcoords="offset points",
                    fontsize=7.5, color=c_storage, family="monospace",
                )

    core.style_axis(ax, xlabel=xlabel, ylabel=AXES["ylabel"],
                    xscale=AXES["xscale"], yscale=AXES["yscale"])

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
