# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "rheofit>=1.0.1",
#     "numpy",
#     "pandas",
#     "matplotlib",
#     "openpyxl",
#     "xlrd",
# ]
# ///
"""rheofit flow-curve fitting app.

Upload a flow curve (TRIOS JSON or Excel), pick a model, preview the curve
with sliders, then fit — all in the browser via WebAssembly.
"""

import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="full",
    app_title="rheofit — flow curve fitting",
    auto_download=["html"],
)


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import io
    import json
    import os
    import tempfile
    import rheofit.io
    from rheofit.models import MODELS

    return MODELS, io, json, mo, np, os, pd, plt, rheofit, tempfile


@app.cell
def _(mo):
    mo.md("""
    # 🧪 rheofit — flow curve fitting

    Fit a measured flow curve with any rheofit model, right in your browser —
    no install, no server. **1.** Upload a file · **2.** pick the step ·
    **3.** pick a model and preview it with the sliders · **4.** hit **Fit**.
    """)
    return


@app.cell
def _(mo):
    upload = mo.ui.file(
        filetypes=[".json", ".xls", ".xlsx"],
        label="Flow curve file (TRIOS JSON or Excel)",
    )
    mo.vstack([mo.md("## 📁 Data"), upload])
    return (upload,)


@app.cell
def _(io, mo, os, pd, rheofit, tempfile, upload):
    mo.stop(not upload.value, mo.md("👆 Upload a flow curve file to begin."))

    _f = upload.value[0]
    content = _f.contents
    ext = os.path.splitext(_f.name)[1].lower()
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    tmp.write(content)
    tmp.close()

    if ext == ".json":
        _steps = rheofit.io.discover_steps(tmp.name)
        _options = {f"{_s['name']} — {_s['n_rows']} pts": _i for _i, _s in enumerate(_steps)}
        step_pick = mo.ui.dropdown(_options, label="Measurement step")
    else:
        _sheets = pd.ExcelFile(io.BytesIO(content)).sheet_names
        step_pick = mo.ui.dropdown(_sheets, label="Worksheet")

    mo.vstack([mo.md("## 📑 Step"), step_pick])
    return content, ext, step_pick, tmp


@app.cell
def _(io, pd):
    def parse_excel_sheet(content: bytes, sheet) -> pd.DataFrame:
        """Find shear-rate / stress columns in a worksheet, trying header rows 0-5."""
        for _hr in range(6):
            _raw = pd.read_excel(io.BytesIO(content), sheet_name=sheet, header=_hr)
            _cols = [(str(_c), _c) for _c in _raw.columns]
            _shear = next(
                (_c for _s, _c in _cols if "shear" in _s.lower() and "rate" in _s.lower()),
                next((_c for _s, _c in _cols if "shear" in _s.lower()), None),
            )
            _stress = next(
                (_c for _s, _c in _cols if "stress" in _s.lower() and _c != _shear), None
            )
            if _shear is not None and _stress is not None:
                _out = pd.DataFrame(
                    {
                        "Shear rate / 1/s": pd.to_numeric(_raw[_shear], errors="coerce"),
                        "Stress / Pa": pd.to_numeric(_raw[_stress], errors="coerce"),
                    }
                ).dropna()
                _out = _out[(_out["Shear rate / 1/s"] > 0) & (_out["Stress / Pa"] > 0)]
                if len(_out) >= 5:
                    return _out.reset_index(drop=True)
        raise ValueError("Could not find shear-rate / stress columns in this sheet.")

    return (parse_excel_sheet,)


@app.cell
def _(content, ext, mo, parse_excel_sheet, rheofit, step_pick, tmp):
    mo.stop(step_pick.value is None, mo.md("👆 Pick a measurement step."))

    if ext == ".json":
        df = rheofit.io.load_step(tmp.name, step_pick.value)
        df = df[["Shear rate / 1/s", "Stress / Pa"]].dropna()
        df = df[(df["Shear rate / 1/s"] > 0) & (df["Stress / Pa"] > 0)]
        df = df.reset_index(drop=True)
    else:
        try:
            df = parse_excel_sheet(content, step_pick.value)
        except ValueError:
            mo.stop(
                True,
                mo.md("⚠️ Could not find shear-rate / stress columns in this sheet — pick another one."),
            )

    mo.stop(len(df) < 5, mo.md("⚠️ Fewer than 5 valid points — check the file."))
    return (df,)


@app.cell
def _(df, mo, plt):
    _fig_data, _ax = plt.subplots(figsize=(6, 4))
    _x = df["Shear rate / 1/s"].to_numpy()
    _y = df["Stress / Pa"].to_numpy()
    _ax.loglog(_x, _y, "o", color="red", mfc="none", label="measured stress")
    _ax.loglog(_x, _y / _x, "o", color="blue", mfc="none", markersize=4, label="viscosity")
    _ax.set_xlabel("shear rate γ̇ (s⁻¹)")
    _ax.set_ylabel("stress σ (Pa) · viscosity η (Pa·s)")
    _ax.set_title(f"Uploaded data — {len(df)} points")
    _ax.grid(True, which="both", alpha=0.3)
    _ax.legend(fontsize=8)
    _fig_data.tight_layout()

    mo.vstack(
        [
            mo.md(f"### 📊 Data — {len(df)} points"),
            mo.ui.table(df.head(10), label="First rows"),
            _fig_data,
        ]
    )
    return


@app.cell
def _(MODELS, mo, model_sel):
    # Display labels are lowercase and human-readable; the dropdown *values*
    # are the exact rheofit model keys, so they always stay compatible with
    # the library (the dict is built from MODELS itself, no hardcoded list).

    effort_sel = mo.ui.radio(
        ["fast", "normal", "thorough"], value="fast", label="Fit effort"
    )
    mod = MODELS[model_sel.value]
    mo.vstack(
        [
            mo.md("## ⚙️ Model"),
            model_sel,
            effort_sel,
            mo.md(
                "_Tip: `fast` is plenty in the browser; `thorough` can take a while._"
            ),
            mo.md(f"### {model_sel.value}"),
            mo.md(f"`{mod.get_equation_latex()}`"),
        ]
    )
    return effort_sel, mod


@app.cell
def _(MODELS, mo):
    _DISPLAY = {
        "power_law": "power law",
        "carreau": "carreau",
        "carreau_carreau": "carreau–carreau",
        "bingham": "bingham",
        "casson": "casson",
        "herschel_bulkley": "herschel–bulkley",
        "tc": "tc",
        "tc_carreau": "tc–carreau",
        "tccc": "tccc",
    }
    _options = {_DISPLAY.get(_k, _k): _k for _k in MODELS}
    model_sel = mo.ui.dropdown(_options, value="tc", label="Model")
    model_sel
    return (model_sel,)


@app.cell
def _(df, mo):
    _xmin = float(df["Shear rate / 1/s"].min())
    _xmax = float(df["Shear rate / 1/s"].max())
    lo_in = mo.ui.number(_xmin * 0.999, _xmax * 1.001, value=_xmin, label="Min γ̇ (s⁻¹)")
    hi_in = mo.ui.number(_xmin * 0.999, _xmax * 1.001, value=_xmax, label="Max γ̇ (s⁻¹)")

    return hi_in, lo_in


@app.cell
def _(df, hi_in, lo_in, mo, mod, np):


    _sel = (df["Shear rate / 1/s"] >= lo_in.value) & (
        df["Shear rate / 1/s"] <= hi_in.value
    )
    sel_df = df[_sel].reset_index(drop=True)
    mo.stop(len(sel_df) < 5, mo.md("⚠️ Fewer than 5 points in the fit range."))

    _x = sel_df["Shear rate / 1/s"].to_numpy()
    _y = sel_df["Stress / Pa"].to_numpy()
    _guess = mod.initial_guess(_x, _y, _y / _x)

    _sliders = {}
    for _p in mod.PARAMS:
        _g = max(float(_guess[_p]), 1e-12)
        _sliders[_p] = mo.ui.slider(
            np.log10(_g) - 3,
            np.log10(_g) + 3,
            step=0.05,
            value=np.log10(_g),
            label=f"{_p} (log₁₀)",
        )
    ui = mo.ui.dictionary(_sliders)
    mo.vstack(
        [
            mo.md("#### 🔍 Curve preview — drag to explore"),
            mo.hstack([lo_in, hi_in], justify="start"),
            ui,
        ]
    )
    return sel_df, ui


@app.cell
def _(mod, np, plt, sel_df, ui):
    _x = sel_df["Shear rate / 1/s"].to_numpy()
    _xf = np.logspace(np.log10(_x.min()), np.log10(_x.max()), 200)
    _pv = {_p: 10.0 ** ui[_p].value for _p in mod.PARAMS}
    _yc = mod._func(_xf, **_pv)

    _fig_prev, _ax1 = plt.subplots(figsize=(7, 4.5))
    _ax1.loglog(
        _x, sel_df["Stress / Pa"].to_numpy(), "o", color="red", mfc="none",
        markersize=5, label="data",
    )
    _ax1.loglog(_xf, _yc, color="red", lw=2.5, label="preview")
    _ax1.set_xlabel("shear rate γ̇ (s⁻¹)")
    _ax1.set_ylabel("stress σ (Pa)", color="red")
    _ax1.tick_params(axis="y", labelcolor="red")
    _ax1.grid(True, which="both", alpha=0.3)
    _ax1.legend(loc="upper left", fontsize=8)
    _ax2 = _ax1.twinx()
    _ax2.loglog(_xf, _yc / _xf, color="blue", lw=2)
    _ax2.set_ylabel("viscosity η (Pa·s)", color="blue")
    _ax2.tick_params(axis="y", labelcolor="blue")
    _fig_prev.tight_layout()
    _fig_prev
    return


@app.cell
def _(mo, model_sel, sel_df):
    run_btn = mo.ui.run_button(label="▶ Fit model")
    mo.vstack(
        [
            mo.md("## ▶ Fit"),
            mo.md(
                f"Fit **{model_sel.value}** on "
                f"**{len(sel_df)}** points in the selected range."
            ),
            run_btn,
        ]
    )
    return (run_btn,)


@app.cell
def _(effort_sel, mo, mod, model_sel, run_btn, sel_df):
    mo.stop(run_btn.value == 0)
    with mo.status.spinner(f"Fitting {model_sel.value}…"):
        res = mod.fit_model(sel_df, effort=effort_sel.value, seed=0)
    return (res,)


@app.cell
def _(mo, model_sel, pd, plt, res):
    _rx = res["x"]
    _yd, _yf = res["y_data"], res["y_fit"]

    # ── fit + residuals figure ──────────────────────────────────────────
    _fig_fit, (_ax1, _ax3) = plt.subplots(
        2, 1, figsize=(7, 6), sharex=True, gridspec_kw={"height_ratios": [3, 1]}
    )
    _ax1.loglog(_rx, _yd, "o", color="red", mfc="none", markersize=5, label="data")
    _ax1.loglog(_rx, _yf, color="black", lw=2, label="best fit")
    _ax1.set_ylabel("stress σ (Pa)")
    _ax1.grid(True, which="both", alpha=0.3)
    _ax1.legend(fontsize=8)
    _ax2 = _ax1.twinx()
    _ax2.loglog(_rx, _yd / _rx, "o", color="blue", mfc="none", markersize=4)
    _ax2.loglog(_rx, _yf / _rx, color="blue", lw=1.5, alpha=0.7)
    _ax2.set_ylabel("viscosity η (Pa·s)", color="blue")
    _ax2.tick_params(axis="y", labelcolor="blue")
    _rres = (_yd - _yf) / _yd
    _ax3.semilogx(_rx, _rres, "o", color="blue", mfc="none", markersize=4)
    _ax3.axhline(0, color="black", lw=1)
    _ax3.fill_between(_rx, -0.05, 0.05, color="blue", alpha=0.15)
    _ax3.set_xlabel("shear rate γ̇ (s⁻¹)")
    _ax3.set_ylabel("rel. residuals")
    _ax3.set_ylim(-0.25, 0.25)
    _fig_fit.suptitle(f"{model_sel.value} — RedChi2 = {res['redchi']:.3g}")
    _fig_fit.tight_layout()

    # ── parameter table ─────────────────────────────────────────────────
    _rows = []
    for _p, _d in res["params"].items():
        _v, _e = _d["value"], _d["stderr"]
        _rel = f"{100 * _e / _v:.1f} %" if _v else "—"
        _rows.append(
            {"parameter": _p, "value": f"{_v:.4g}",
             "± stderr": f"{_e:.2g}", "rel. err": _rel}
        )
    _ptab = mo.ui.table(pd.DataFrame(_rows), label="Fitted parameters")

    _notes = [f"**RedChi2** = `{res['redchi']:.4g}` · **cond** = `{res['cond']:.2g}`"]
    if not res["success"]:
        _notes.append("⚠️ _The optimizer reported failure — treat this fit with caution._")
    if res["cond"] > 1e10:
        _notes.append(
            "⚠️ _Very high condition number: parameters are poorly identified._"
        )
    for _p, _d in res["params"].items():
        if _d["value"] and _d["stderr"] / _d["value"] > 0.5:
            _notes.append(
                f"⚠️ _{_p} has >50% relative uncertainty — consider a simpler model._"
            )

    mo.ui.tabs(
        {
            "📈 Fit": _fig_fit,
            "🧮 Parameters": mo.vstack([_ptab, mo.md("\n\n".join(_notes))]),
        }
    )
    return


@app.cell
def _(effort_sel, json, mo, model_sel, pd, res):
    _key = model_sel.value
    _params_csv = pd.DataFrame(
        [
            {"parameter": _p, "value": _d["value"], "stderr": _d["stderr"]}
            for _p, _d in res["params"].items()
        ]
    ).to_csv(index=False)
    _report = {
        "model": _key,
        "effort": effort_sel.value,
        "redchi": res["redchi"],
        "cond": res["cond"],
        "success": res["success"],
        "params": {_p: _d["value"] for _p, _d in res["params"].items()},
    }
    mo.hstack(
        [
            mo.download(
                _params_csv.encode(),
                f"rheofit_{_key}_params.csv",
                label="⬇ Parameters (CSV)",
            ),
            mo.download(
                json.dumps(_report, indent=2).encode(),
                f"rheofit_{_key}_report.json",
                label="⬇ Report (JSON)",
            ),
        ],
        justify="start",
    )
    return


@app.cell
def _(mo):
    cmp_btn = mo.ui.run_button(label="⚖️ Fit all models & rank")
    mo.vstack(
        [
            mo.md("## 🏆 Compare"),
            mo.md("_Ranks every model by RedChi2 on the current fit range._"),
            cmp_btn,
        ]
    )
    return (cmp_btn,)


@app.cell
def _(MODELS, cmp_btn, mo, pd, sel_df):
    mo.stop(cmp_btn.value == 0)
    _rows = []
    with mo.status.spinner("Fitting all models (fast effort)…"):
        for _key, _m in MODELS.items():
            try:
                _r = _m.fit_model(sel_df, effort="fast", seed=0)
                _rows.append(
                    {"model": _key, "RedChi2": f"{_r['redchi']:.4g}",
                     "_rc": _r["redchi"], "success": _r["success"]}
                )
            except Exception as _exc:  # noqa: BLE001
                _rows.append(
                    {"model": _key, "RedChi2": "failed",
                     "_rc": float("inf"), "success": False}
                )
    _ranking = pd.DataFrame(_rows).sort_values("_rc").drop(columns="_rc")
    _best = _ranking.iloc[0]["model"]
    mo.vstack(
        [
            mo.md(f"### 🏆 Model ranking — best: **{_best}**"),
            mo.ui.table(_ranking.reset_index(drop=True)),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
