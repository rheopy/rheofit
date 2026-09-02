"""Shared plotting primitives for rheofit visualization modules.

Every test-type module builds on the same three pieces:

* :func:`normalize_datasets` / :func:`normalize_fits` accept whatever the user
  has at hand (one DataFrame, a list, or a labelled dict) and return aligned
  ``{label: ...}`` mappings.
* :func:`make_panels` decides the figure layout: one panel for data only, two
  panels (with a residual strip) as soon as fits are supplied.
* :func:`style_axis`, :func:`plot_residuals` and :func:`param_textbox` keep the
  look consistent across test types.

Colour convention
-----------------
Hue always encodes the *quantity*, never the dataset: stress and the elastic
modulus G' are red, viscosity and the viscous modulus G'' are blue. Multiple
datasets on one figure are told apart by marker shape and by a lighter shade of
the same hue, so the meaning of a colour never shifts between figures.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

# Quantity -> hue. Reds and blues match report.SCORECARD_COLORS.
COLORS = {
    "stress": "#E74C3C",     # red
    "viscosity": "#3498DB",  # blue
    "storage": "#E74C3C",    # G'  (elastic)  red
    "loss": "#3498DB",       # G'' (viscous)  blue
}

# Dataset -> marker / line style, so several curves of the same quantity stay
# distinguishable without changing hue.
MARKERS = ("o", "s", "^", "D", "v", "P", "X", "*")
LINESTYLES = ("-", "--", "-.", ":")

# How far the shade of a hue may be washed out toward white for later datasets.
_MAX_TINT = 0.45


def marker_for(index: int) -> str:
    return MARKERS[index % len(MARKERS)]


def linestyle_for(index: int) -> str:
    return LINESTYLES[index % len(LINESTYLES)]


def shade(color: str, index: int = 0, n: int = 1) -> tuple[float, float, float]:
    """Tint ``color`` toward white so dataset ``index`` of ``n`` stands apart.

    Dataset 0 always keeps the pure hue, so a single-dataset figure uses exactly
    the canonical red or blue.
    """
    rgb = np.array(mcolors.to_rgb(color))
    if n <= 1 or index <= 0:
        return tuple(rgb)
    tint = _MAX_TINT * (index % n) / max(1, n - 1)
    return tuple(rgb + (1.0 - rgb) * tint)


def color_for(quantity: str, index: int = 0, n: int = 1) -> tuple[float, float, float]:
    """Colour for a named quantity (``'stress'``, ``'viscosity'``, ...)."""
    return shade(COLORS[quantity], index, n)


def label_axis_color(ax, color) -> None:
    """Tint an axis label and ticks to match the quantity drawn against it."""
    ax.yaxis.label.set_color(color)
    ax.tick_params(axis="y", colors=color)


# ── Input normalisation ────────────────────────────────────────────────────────

def normalize_datasets(data) -> dict[str, pd.DataFrame]:
    """Coerce ``data`` into an ordered ``{label: DataFrame}`` mapping.

    Accepts ``None``, a single DataFrame, a sequence of DataFrames, or an
    already-labelled mapping. Unlabelled inputs fall back to the step name
    recorded in ``df.attrs`` and then to ``"dataset N"``.
    """
    if data is None:
        return {}
    if isinstance(data, pd.DataFrame):
        data = [data]
    if isinstance(data, Mapping):
        return {str(k): v for k, v in data.items()}
    if isinstance(data, Sequence):
        out: dict[str, pd.DataFrame] = {}
        for i, df in enumerate(data):
            label = str(df.attrs.get("step_name", "") or f"dataset {i + 1}")
            while label in out:
                label = f"{label} ({i + 1})"
            out[label] = df
        return out
    raise TypeError(
        "data must be a DataFrame, a sequence of DataFrames, or a {label: DataFrame} mapping"
    )


def normalize_fits(fits, labels: Sequence[str]) -> dict[str, dict]:
    """Align fit results to dataset labels.

    Mappings are matched by key, sequences by position. Datasets without a fit
    are simply absent from the result, so a fit can be overlaid on one curve
    only. A fit result is the dict returned by ``rheofit.fit`` -- it already
    carries ``x``, ``y_data``, ``y_fit``, ``params`` and ``redchi``.
    """
    if fits is None:
        return {}
    if isinstance(fits, Mapping) and "y_fit" in fits:
        fits = [fits]  # a single fit-result dict, not a mapping of them
    if isinstance(fits, Mapping):
        return {str(k): v for k, v in fits.items() if v is not None}
    if isinstance(fits, Sequence):
        out = {}
        for i, f in enumerate(fits):
            if f is None:
                continue
            # Fits may arrive without data (report.plot_fit passes a result only),
            # in which case they define the labels rather than borrow them.
            out[labels[i] if i < len(labels) else f"dataset {i + 1}"] = f
        return out
    raise TypeError("fits must be a fit-result dict, a sequence of them, or a {label: fit} mapping")


def labels_from(datasets: Mapping[str, pd.DataFrame], fits: Mapping[str, dict]) -> list[str]:
    """Ordered labels covering both datasets and fit-only inputs."""
    labels = list(datasets)
    labels += [k for k in fits if k not in datasets]
    return labels


def datasets_from_fits(fits: Mapping[str, dict], x_col: str, y_col: str) -> dict[str, pd.DataFrame]:
    """Rebuild plottable frames from fit results alone (no raw data supplied)."""
    return {
        label: pd.DataFrame({x_col: np.asarray(f["x"], float), y_col: np.asarray(f["y_data"], float)})
        for label, f in fits.items()
    }


# ── Layout ─────────────────────────────────────────────────────────────────────

def make_panels(with_residuals: bool, figsize: tuple[float, float] | None = None):
    """Return ``(fig, main_ax, residual_ax)``; ``residual_ax`` is ``None`` if unused.

    This is the single place the fit / no-fit switch changes the layout.
    Constrained layout is used because these figures carry twinned axes, which
    ``tight_layout`` cannot handle.
    """
    if with_residuals:
        fig, (ax_main, ax_res) = plt.subplots(
            2, 1, sharex=True,
            figsize=figsize or (8.0, 8.0),
            gridspec_kw={"height_ratios": [3, 1]},
            layout="constrained",
        )
        return fig, ax_main, ax_res
    fig, ax_main = plt.subplots(figsize=figsize or (8.0, 6.0), layout="constrained")
    return fig, ax_main, None


def style_axis(ax, xlabel=None, ylabel=None, xscale="log", yscale="log", title=None):
    if xscale:
        ax.set_xscale(xscale)
    if yscale:
        ax.set_yscale(yscale)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=11)
    ax.grid(alpha=0.25, which="both")
    return ax


def plot_residuals(ax, fits: Mapping[str, dict], labels: Sequence[str], exp_err: float = 0.05):
    """Relative residuals ``(data - fit) / data`` for every fitted dataset.

    Residuals belong to the fitted quantity (stress), so they carry the stress
    hue and reuse each dataset's marker.
    """
    n = len(labels)
    for label, fit in fits.items():
        idx = labels.index(label) if label in labels else 0
        x = np.asarray(fit["x"], float)
        y_data = np.asarray(fit["y_data"], float)
        y_fit = np.asarray(fit["y_fit"], float)
        with np.errstate(divide="ignore", invalid="ignore"):
            resid = np.where(y_data != 0, (y_data - y_fit) / y_data, np.nan)
        ax.plot(x, resid, marker_for(idx), ms=4, mfc="none",
                mec=color_for("stress", idx, n), ls="none", label=label)

    ax.axhline(0.0, color="black", lw=0.9)
    ax.axhspan(-exp_err, exp_err, color="grey", alpha=0.18,
               label=f"\u00b1{exp_err * 100:.0f}%")
    ax.set_ylabel("relative residuals")
    ax.set_ylim(-5 * exp_err, 5 * exp_err)
    ax.grid(alpha=0.25, which="both")
    return ax


def param_textbox(ax, fit: dict) -> None:
    """Parameter/RedChi2 annotation, used only when a single fit is shown."""
    lines = [f"{k}: {v['value']:.2E}" for k, v in fit.get("params", {}).items()]
    lines.append(f"RedChi2: {float(fit.get('redchi', np.nan)):.2E}")
    ax.text(
        0.02, 0.97, "\n".join(lines), transform=ax.transAxes, fontsize=7.5,
        verticalalignment="top", family="monospace",
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.7),
    )


def redchi_legend_labels(labels: Sequence[str], fits: Mapping[str, dict]) -> dict[str, str]:
    """Legend text per label, appending RedChi2 when several fits are compared."""
    out = {}
    for label in labels:
        fit = fits.get(label)
        if fit is None:
            out[label] = label
        else:
            out[label] = f"{label} (RedChi2 {float(fit.get('redchi', np.nan)):.1E})"
    return out


def dataset_handles(labels: Sequence[str], legend_text: Mapping[str, str]) -> list:
    """One neutral marker proxy per dataset -- marker shape identifies the dataset."""
    return [
        Line2D([], [], marker=marker_for(i), color="0.35", ls="none", ms=6,
               mfc="none", label=legend_text.get(label, label))
        for i, label in enumerate(labels)
    ]


def quantity_handles(specs: Sequence[tuple[str, str, bool]]) -> list:
    """Colour-key proxies: ``(quantity, display_label, filled)`` per entry."""
    handles = []
    for quantity, text, filled in specs:
        color = COLORS[quantity]
        handles.append(
            Line2D([], [], marker="o", ms=6, ls="none", color=color,
                   mfc=color if filled else "none", mec=color, label=text)
        )
    return handles


def require_columns(df: pd.DataFrame, columns: Sequence[str], label: str, test_name: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(
            f"dataset '{label}' cannot be plotted as {test_name}: missing column(s) "
            f"{missing}. Available columns: {sorted(df.columns)[:12]}..."
        )


def sorted_xy(df: pd.DataFrame, x_col: str, *y_cols: str):
    """Positive, finite, x-ascending arrays -- log axes need this."""
    cols = [x_col, *y_cols]
    sub = df[cols].apply(pd.to_numeric, errors="coerce").dropna()
    sub = sub[sub[x_col] > 0].sort_values(x_col)
    return tuple(sub[c].to_numpy(dtype=float) for c in cols)


def log_crossover(x: np.ndarray, y1: np.ndarray, y2: np.ndarray) -> float | None:
    """First x where ``y1`` crosses ``y2``, interpolated in log-log space."""
    mask = (x > 0) & (y1 > 0) & (y2 > 0)
    if mask.sum() < 2:
        return None
    lx, d = np.log10(x[mask]), np.log10(y1[mask]) - np.log10(y2[mask])
    sign_change = np.where(np.diff(np.sign(d)) != 0)[0]
    if len(sign_change) == 0:
        return None
    i = sign_change[0]
    if d[i + 1] == d[i]:
        return None
    frac = -d[i] / (d[i + 1] - d[i])
    return float(10 ** (lx[i] + frac * (lx[i + 1] - lx[i])))
