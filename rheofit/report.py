"""Reporting helpers for rheofit: diagnostic plots, PNG scorecard, CSV summary, PPTX."""
from __future__ import annotations

import importlib
import re
import tempfile
from datetime import date
from pathlib import Path

import matplotlib


def _use_headless_backend_if_needed() -> None:
    """Force Agg only outside IPython/Jupyter, so notebooks keep their inline backend."""
    try:
        from IPython import get_ipython
    except ImportError:
        get_ipython = None
    if get_ipython is None or get_ipython() is None:
        matplotlib.use("Agg")


_use_headless_backend_if_needed()

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCORECARD_COLORS = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6", "#1ABC9C", "#E67E22"]


def fit_quality_band(redchi: float) -> str:
    """Qualitative band for a relative-weighted reduced chi-square."""
    if not np.isfinite(redchi):
        return "unknown"
    if redchi < 1e-2:
        return "excellent"
    if redchi < 1e-1:
        return "acceptable"
    return "watchout"


def safe_label_for_filename(label: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", str(label).strip())
    return sanitized.strip("_") or "step"


# ── Diagnostic plots ───────────────────────────────────────────────────────────

def plot_fit(result: dict, title: str = "", exp_err: float = 0.05):
    """Two-panel diagnostic: stress+viscosity overlay (top) and relative residuals (bottom)."""
    from .visualization import flow_curve

    return flow_curve.plot(fits=result, exp_err=exp_err, title=title)


def _save_temp(fig) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    fig.savefig(tmp.name, dpi=150, bbox_inches="tight")
    tmp.close()
    plt.close(fig)
    return tmp.name


# ── Tables ─────────────────────────────────────────────────────────────────────

def build_tables(res_dict: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Value and stderr DataFrames indexed by step label, columns = all parameters."""
    val_rows, err_rows = {}, {}
    for label, res in res_dict.items():
        val_rows[label] = {k: v["value"] for k, v in res["params"].items()}
        err_rows[label] = {k: v["stderr"] for k, v in res["params"].items()}
    return pd.DataFrame(val_rows).T, pd.DataFrame(err_rows).T


def build_parameter_summary(res_dict: dict, scorecard_params: list[str]) -> pd.DataFrame:
    """Compact long-form table: step, parameter, value/error, and fit quality."""
    rows = []
    scorecard_set = set(scorecard_params)
    for step_label, res in res_dict.items():
        redchi = float(res.get("redchi", np.nan))
        quality = fit_quality_band(redchi)
        for pname, p in res.get("params", {}).items():
            value = float(p.get("value", np.nan))
            stderr = float(p.get("stderr", np.nan))
            rel_pct = np.nan
            if np.isfinite(value) and value != 0 and np.isfinite(stderr):
                rel_pct = abs(stderr / value) * 100.0
            rows.append(
                {
                    "step": step_label,
                    "parameter": pname,
                    "value": value,
                    "stderr": stderr,
                    "rel_error_pct": rel_pct,
                    "redchi2": redchi,
                    "fit_quality": quality,
                    "scorecard_param": pname in scorecard_set,
                }
            )
    return pd.DataFrame(rows)


# ── Scorecard bar chart ────────────────────────────────────────────────────────

def plot_scorecard(res_dict: dict, scorecard_params: list[str]) -> tuple:
    val_tbl, err_tbl = build_tables(res_dict)

    labels = list(val_tbl.index)
    n_params = len(scorecard_params)

    fig, axes = plt.subplots(1, n_params, figsize=(6 * n_params, max(4, len(labels) * 1.5 + 2)))
    if n_params == 1:
        axes = [axes]

    y_pos = np.arange(len(labels))

    for i, param in enumerate(scorecard_params):
        ax = axes[i]
        vals = val_tbl[param].values.astype(float)
        errs = err_tbl[param].values.astype(float)
        color = SCORECARD_COLORS[i % len(SCORECARD_COLORS)]

        ax.barh(y_pos, vals, xerr=errs, capsize=4, alpha=0.85,
                color=color, edgecolor="black", linewidth=1.2)

        for j, v in enumerate(vals):
            ax.text(v, j, f"  {v:.2e}", va="center", fontsize=9,
                    fontweight="bold", family="monospace")

        ax.set_title(f">> {param}", fontsize=12, fontweight="bold", family="monospace")
        ax.set_xlabel("Value +/- Std Error")
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=10, family="monospace")
        ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    return fig, val_tbl, err_tbl


# ── PNG scorecard ──────────────────────────────────────────────────────────────

def _render_png_notes(res_dict: dict) -> str:
    note_lines = []
    for step_label, res in res_dict.items():
        for note in res.get("notes", []):
            note_lines.append(f"- {step_label}: {note}")

    if not note_lines:
        note_lines.append("- No fit warnings were triggered.")

    note_lines.extend(
        [
            "- RedChi2 < 0.01 is generally excellent for this relative-weighted objective.",
            "- Parameters with rel_error_pct > 100% are weakly identified (treat cautiously).",
            "- If a richer nested model scores worse than its parent, re-run with higher effort/seed.",
        ]
    )
    return "\n".join(note_lines)


def build_png_scorecard(
    sample_name: str,
    model_name: str,
    equation: str,
    res_dict: dict,
    summary_df: pd.DataFrame,
    output_path: str | Path,
    title_suffix: str | None = None,
) -> str:
    """Single-page PNG scorecard: header, fit snapshot, parameter table, notes."""
    n_rows = max(1, len(summary_df))
    fig_h = max(9, min(20, 6 + 0.32 * n_rows))

    fig = plt.figure(figsize=(14, fig_h))
    gs = fig.add_gridspec(
        3, 2,
        height_ratios=[0.9, 3.4, 1.4],
        width_ratios=[1.0, 1.6],
        hspace=0.35,
        wspace=0.25,
    )

    # Header textbox
    ax_head = fig.add_subplot(gs[0, :])
    ax_head.axis("off")
    task_header = (
        f"Task: Fit TRIOS flow-curve data with {model_name.upper()} and summarize key rheology parameters\n"
        f"Sample: {sample_name}   |   Steps: {', '.join(res_dict.keys())}   |   Date: {date.today().isoformat()}"
    )
    ax_head.text(
        0.01, 0.5, task_header, va="center", ha="left", fontsize=11, family="monospace",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#EEF3FA", edgecolor="#1F497D"),
    )

    # Fit visualization (top: stress+viscosity, bottom: % residuals)
    fit_gs = gs[1, 0].subgridspec(2, 1, height_ratios=[3.0, 1.2], hspace=0.08)
    ax_fit = fig.add_subplot(fit_gs[0, 0])
    ax_fit_eta = ax_fit.twinx()
    ax_res = fig.add_subplot(fit_gs[1, 0], sharex=ax_fit)
    for label, res in res_dict.items():
        x = np.asarray(res["x"], dtype=float)
        y_data = np.asarray(res["y_data"], dtype=float)
        y_fit = np.asarray(res["y_fit"], dtype=float)
        eta_data = y_data / x
        eta_fit = y_fit / x
        residual_pct = (y_data - y_fit) / y_data * 100.0

        ax_fit.plot(x, y_data, "o", ms=3.5, mfc="none", mec="red", label=f"{label} stress data")
        ax_fit.plot(x, y_fit, "-", lw=1.5, color="red", label=f"{label} stress fit")

        ax_fit_eta.plot(x, eta_data, "s", ms=3.0, mfc="none", mec="blue", alpha=0.65,
                        label=f"{label} viscosity data")
        ax_fit_eta.plot(x, eta_fit, "--", lw=1.3, color="blue", alpha=0.8,
                        label=f"{label} viscosity fit")

        ax_res.plot(x, residual_pct, "o", ms=3.0, mfc="none", mec="black", alpha=0.85,
                    label=f"{label} % residual")

    ax_fit.set_xscale("log")
    ax_fit.set_yscale("log")
    ax_fit_eta.set_yscale("log")
    ax_fit.set_ylabel("stress [Pa]", color="#202020")
    ax_fit_eta.set_ylabel("viscosity [Pa.s]", color="#404040")
    ax_fit.set_title("Fit snapshot (stress + viscosity overlays)", fontsize=10)
    ax_fit.grid(alpha=0.25, which="both")
    ax_fit.tick_params(axis="x", labelbottom=False)

    ax_res.set_xscale("log")
    ax_res.axhline(0.0, color="black", lw=0.9)
    ax_res.fill_between(x, -5.0, 5.0, color="blue", alpha=0.12, label="±5% band")
    ax_res.set_ylabel("% resid")
    ax_res.set_xlabel("shear rate [1/s]")
    ax_res.grid(alpha=0.25, which="both")
    ax_res.set_ylim(-25, 25)

    h1, l1 = ax_fit.get_legend_handles_labels()
    h2, l2 = ax_fit_eta.get_legend_handles_labels()
    ax_fit.legend(h1 + h2, l1 + l2, fontsize=6.5, loc="best", framealpha=0.85)
    ax_res.legend(fontsize=6.5, loc="best", framealpha=0.85)

    # Parameter table with fit quality metrics
    ax_tbl = fig.add_subplot(gs[1, 1])
    ax_tbl.axis("off")

    disp_cols = ["step", "parameter", "value", "stderr", "rel_error_pct", "redchi2", "fit_quality"]
    disp = summary_df[disp_cols].copy()
    disp["value"] = disp["value"].map(lambda v: f"{v:.3E}" if np.isfinite(v) else "NA")
    disp["stderr"] = disp["stderr"].map(lambda v: f"{v:.2E}" if np.isfinite(v) else "NA")
    disp["rel_error_pct"] = disp["rel_error_pct"].map(lambda v: f"{v:.1f}" if np.isfinite(v) else "NA")
    disp["redchi2"] = disp["redchi2"].map(lambda v: f"{v:.2E}" if np.isfinite(v) else "NA")
    disp.columns = ["Step", "Param", "Value", "±Error", "RelErr %", "RedChi2", "Quality"]

    table = ax_tbl.table(
        cellText=disp.values,
        colLabels=disp.columns,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.2)

    for (r, _c), cell in table.get_celld().items():
        if r == 0:
            cell.set_facecolor("#1F497D")
            cell.set_text_props(color="white", weight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#F5F7FA")

    ax_tbl.set_title("Parameter table (value, error, fit metric)", fontsize=10)

    # Notes / watchouts textbox
    ax_notes = fig.add_subplot(gs[2, :])
    ax_notes.axis("off")
    notes_txt = (
        "Interpretation notes & watchouts:\n"
        f"{_render_png_notes(res_dict)}\n"
        f"Model equation: {equation}"
    )
    ax_notes.text(
        0.01, 0.96, notes_txt, va="top", ha="left", fontsize=9, family="monospace",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFFBEA", edgecolor="#C8B66A"),
    )

    title = f"{sample_name} - {model_name.upper()} Scorecard"
    if title_suffix:
        title = f"{title} ({title_suffix})"
    fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.subplots_adjust(top=0.92, bottom=0.05, left=0.04, right=0.98, hspace=0.45, wspace=0.25)
    fig.savefig(output_path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    return str(output_path)


# ── PowerPoint builder ─────────────────────────────────────────────────────────

def build_pptx(
    sample_name: str,
    model_name: str,
    equation: str,
    step_labels: list[str],
    tmp_diag_paths: list[str],
    tmp_sc_path: str,
    val_tbl: pd.DataFrame,
    err_tbl: pd.DataFrame,
) -> object:
    try:
        pptx = importlib.import_module("pptx")
        dml_color = importlib.import_module("pptx.dml.color")
        enum_text = importlib.import_module("pptx.enum.text")
        util = importlib.import_module("pptx.util")
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "python-pptx is required for pptx output. "
            "Install with: python -m pip install python-pptx"
        ) from exc

    Presentation = pptx.Presentation
    RGBColor = dml_color.RGBColor
    PP_ALIGN = enum_text.PP_ALIGN
    Inches = util.Inches
    Pt = util.Pt

    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    BLACK = RGBColor(0x00, 0x00, 0x00)
    DARK = RGBColor(0x22, 0x22, 0x22)
    GREY = RGBColor(0x88, 0x88, 0x88)
    ALT = RGBColor(0xF2, 0xF2, 0xF2)
    HEAD = RGBColor(0x1F, 0x49, 0x7D)

    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)
    BLANK = prs.slide_layouts[6]

    def _white_bg(slide):
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = WHITE

    def txt_box(slide, text, left, top, width, height,
                size=12, bold=False, color=BLACK, align=PP_ALIGN.LEFT):
        tb = slide.shapes.add_textbox(left, top, width, height)
        tf = tb.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.alignment = align
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = "Courier New"

    def add_table(slide, df, left, top, width, height):
        rows, cols = df.shape
        tbl = slide.shapes.add_table(rows + 1, cols + 1, left, top, width, height).table
        col_w = width // (cols + 1)
        for c in range(cols + 1):
            tbl.columns[c].width = col_w

        def cell(r, c, text, bold=False, bg=None):
            cl = tbl.cell(r, c)
            cl.text = str(text)
            tf = cl.text_frame
            tf.paragraphs[0].alignment = PP_ALIGN.CENTER
            runs = tf.paragraphs[0].runs
            run = runs[0] if runs else tf.paragraphs[0].add_run()
            run.font.size = Pt(8)
            run.font.bold = bold
            run.font.name = "Courier New"
            if bg:
                cl.fill.solid()
                cl.fill.fore_color.rgb = bg
                run.font.color.rgb = WHITE if bg == HEAD else BLACK

        cell(0, 0, "Step", bold=True, bg=HEAD)
        for c, name in enumerate(df.columns):
            cell(0, c + 1, name, bold=True, bg=HEAD)
        for r, (idx, row) in enumerate(df.iterrows()):
            bg = ALT if r % 2 == 0 else None
            cell(r + 1, 0, str(idx), bold=True, bg=bg)
            for c, v in enumerate(row):
                cell(r + 1, c + 1, f"{v:.3E}", bg=bg)

    errrel_tbl = (err_tbl / val_tbl * 100).fillna(0)
    n_steps = len(step_labels)

    # Slide 1: Title
    sl = prs.slides.add_slide(BLANK)
    _white_bg(sl)
    txt_box(sl, f"[*] {sample_name}",
            Inches(1), Inches(1.8), Inches(11.3), Inches(1.2),
            size=28, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    txt_box(sl, f"Model: {model_name.upper()}",
            Inches(1), Inches(3.2), Inches(11.3), Inches(0.6),
            size=18, color=HEAD, align=PP_ALIGN.CENTER)
    txt_box(sl, equation,
            Inches(1), Inches(3.9), Inches(11.3), Inches(0.55),
            size=13, color=GREY, align=PP_ALIGN.CENTER)
    txt_box(sl, f"Steps: {', '.join(step_labels)}  |  {date.today().isoformat()}",
            Inches(1), Inches(4.6), Inches(11.3), Inches(0.45),
            size=11, color=GREY, align=PP_ALIGN.CENTER)

    # Slide 2: Fit Diagnostics
    sl = prs.slides.add_slide(BLANK)
    _white_bg(sl)
    txt_box(sl, "[>] Fit Diagnostics",
            Inches(0.3), Inches(0.15), Inches(12.7), Inches(0.55),
            size=22, bold=True, color=DARK)
    txt_box(sl, "Top: stress (red) & viscosity (blue)  |  Bottom: relative residuals",
            Inches(0.3), Inches(0.7), Inches(12.7), Inches(0.35),
            size=11, color=GREY)
    img_w = (13.33 - 0.6) / n_steps
    for i, img_path in enumerate(tmp_diag_paths):
        sl.shapes.add_picture(
            img_path,
            Inches(0.3 + i * img_w),
            Inches(1.1),
            Inches(img_w),
            Inches(6.1),
        )

    # Slide 3: Parameter Tables
    sl = prs.slides.add_slide(BLANK)
    _white_bg(sl)
    txt_box(sl, "[=] Parameters",
            Inches(0.3), Inches(0.15), Inches(12.7), Inches(0.55),
            size=22, bold=True, color=DARK)
    txt_box(sl, "Values",
            Inches(0.3), Inches(0.72), Inches(4), Inches(0.35),
            size=11, bold=True, color=HEAD)
    add_table(sl, val_tbl, Inches(0.3), Inches(1.1), Inches(12.7), Inches(1.1))
    txt_box(sl, "Standard Errors",
            Inches(0.3), Inches(2.35), Inches(4), Inches(0.35),
            size=11, bold=True, color=HEAD)
    add_table(sl, err_tbl, Inches(0.3), Inches(2.75), Inches(12.7), Inches(1.1))
    txt_box(sl, "Relative Errors (%)",
            Inches(0.3), Inches(4.0), Inches(4), Inches(0.35),
            size=11, bold=True, color=HEAD)
    add_table(sl, errrel_tbl, Inches(0.3), Inches(4.4), Inches(12.7), Inches(1.1))

    # Slide 4: Scorecard
    sl = prs.slides.add_slide(BLANK)
    _white_bg(sl)
    txt_box(sl, "[~] Scorecard",
            Inches(0.3), Inches(0.15), Inches(12.7), Inches(0.55),
            size=22, bold=True, color=DARK)
    sl.shapes.add_picture(tmp_sc_path, Inches(0.3), Inches(0.8), Inches(12.7), Inches(6.4))

    return prs
