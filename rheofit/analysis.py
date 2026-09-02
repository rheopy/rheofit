"""High-level analysis workflow: load steps, fit a model, save artifacts."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import io as trios_io
from . import report
from .models import MODELS


def list_models() -> list[str]:
    """Names of the available rheological models."""
    return sorted(MODELS)


def get_model(name: str):
    """Return the model module for ``name`` (raises for unknown models)."""
    try:
        return MODELS[name]
    except KeyError:
        raise ValueError(f"Unknown model '{name}'. Available: {list_models()}") from None


def model_info(name: str) -> dict:
    """Metadata of a model: equation, parameters, scorecard params, nested parent."""
    m = get_model(name)
    return {
        "name": m.MODEL_NAME,
        "equation": m.get_equation_latex(),
        "params": list(m.PARAMS),
        "scorecard_params": list(m.SCORECARD_PARAMS),
        "parent": getattr(m, "PARENT", None),
        "parent_exact": getattr(m, "PARENT_EXACT", False),
    }


def fit(df: pd.DataFrame, model: str, effort: str = "thorough", seed: int = 0) -> dict:
    """Fit one flow-curve DataFrame with ``model``.

    ``df`` needs a ``'Shear rate / 1/s'`` and a ``'Stress / Pa'`` column
    (``'Viscosity / Pa.s'`` is used when present, otherwise derived).
    Returns the result dict: ``params`` (value/stderr), ``redchi``, ``cond``,
    ``x``, ``y_data``, ``y_fit``, ``notes``.
    """
    return get_model(model).fit_model(df, effort=effort, seed=seed)


@dataclass
class Analysis:
    """Result of :func:`analyze` — fits, summary table and saved artifact paths."""

    sample_name: str
    model: str
    equation: str
    results: dict = field(default_factory=dict)
    summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    outputs: list[str] = field(default_factory=list)
    output_dir: Path | None = None


def analyze(
    source: str,
    steps: list[int],
    model: str,
    labels: list[str] | None = None,
    effort: str = "thorough",
    seed: int = 0,
    output: str = "png_csv",
    sample_name: str | None = None,
    results_base: str | Path | None = None,
    verbose: bool = True,
) -> Analysis:
    """Fit selected TRIOS steps and write the requested artifacts.

    ``source`` is a local TRIOS JSON path or an HTTP(S) URL.
    ``output`` is ``'png_csv'`` (default), ``'pptx'``, ``'both'`` or ``'none'``
    (fit only, write nothing).
    """
    if output not in {"png_csv", "pptx", "both", "none"}:
        raise ValueError("output must be one of 'png_csv', 'pptx', 'both', 'none'")

    model_mod = get_model(model)
    json_path, cleanup_tmp = trios_io.materialize(source)

    name = (sample_name or "").strip() or json_path.stem or "remote_sample"

    if results_base is not None:
        base_dir = Path(results_base)
    else:
        base_dir = Path.cwd() if trios_io.is_http_url(source) else json_path.parent
    out_dir = base_dir / "results" / name

    def log(msg: str) -> None:
        if verbose:
            print(msg)

    try:
        if labels is None or len(labels) != len(steps):
            labels = [f"Step {i}" for i in steps]

        log(f"\n[*] Sample : {name}")
        log(f"    Model  : {model_mod.MODEL_NAME}")
        log(f"    Source : {source}")
        log(f"    Steps  : {steps}  ->  labels: {labels}")
        log(f"    Fit    : relative-weighted, effort={effort}, seed={seed}")
        log(f"    Output : {output}")

        step_data = trios_io.load_steps(json_path, steps)

        res_dict: dict = {}
        for idx, label in zip(steps, labels):
            df = step_data[idx]
            log(f"\n    Fitting [{label}]  ({len(df)} pts) ...")
            result = model_mod.fit_model(df, effort=effort, seed=seed)
            log(f"    [OK] success={result['success']}  RedChi2={result['redchi']:.3E}"
                f"  starts={result.get('n_starts', '?')}")
            if result.get("parent"):
                log(f"         nested parent '{result['parent']}'"
                    f"  RedChi2={result['parent_redchi']:.3E}")
            for note in result.get("notes", []):
                log(f"    [!]  {note}")
            res_dict[label] = result

        summary_df = report.build_parameter_summary(res_dict, model_mod.SCORECARD_PARAMS)
        analysis = Analysis(
            sample_name=name,
            model=model_mod.MODEL_NAME,
            equation=model_mod.get_equation_latex(),
            results=res_dict,
            summary=summary_df,
        )

        if output == "none":
            return analysis

        out_dir.mkdir(parents=True, exist_ok=True)
        analysis.output_dir = out_dir
        outputs: list[str] = []
        model_tag = model_mod.MODEL_NAME.upper()

        if output in {"png_csv", "both"}:
            # One scorecard per step label when several flow sweeps are selected.
            if len(res_dict) == 1:
                only_label = next(iter(res_dict))
                png_path = out_dir / f"{name} - {model_tag} Scorecard.png"
                report.build_png_scorecard(
                    sample_name=name,
                    model_name=model_mod.MODEL_NAME,
                    equation=analysis.equation,
                    res_dict=res_dict,
                    summary_df=summary_df,
                    output_path=png_path,
                    title_suffix=only_label,
                )
                outputs.append(str(png_path))
            else:
                for label, single_res in res_dict.items():
                    single_res_dict = {label: single_res}
                    single_summary = report.build_parameter_summary(
                        single_res_dict, model_mod.SCORECARD_PARAMS
                    )
                    safe_label = report.safe_label_for_filename(label)
                    png_path = out_dir / (
                        f"{name} - {safe_label} - {model_tag} Scorecard.png"
                    )
                    report.build_png_scorecard(
                        sample_name=name,
                        model_name=model_mod.MODEL_NAME,
                        equation=analysis.equation,
                        res_dict=single_res_dict,
                        summary_df=single_summary,
                        output_path=png_path,
                        title_suffix=label,
                    )
                    outputs.append(str(png_path))

            csv_path = out_dir / f"{name} - {model_tag} Scorecard Summary.csv"
            summary_df.to_csv(csv_path, index=False)
            outputs.append(str(csv_path))

        if output in {"pptx", "both"}:
            tmp_diag_paths = [
                report._save_temp(report.plot_fit(res, title=f"{name}  [{label}]"))
                for label, res in res_dict.items()
            ]
            sc_fig, val_tbl, err_tbl = report.plot_scorecard(res_dict, model_mod.SCORECARD_PARAMS)
            tmp_sc_path = report._save_temp(sc_fig)

            prs = report.build_pptx(
                sample_name=name,
                model_name=model_mod.MODEL_NAME,
                equation=analysis.equation,
                step_labels=list(res_dict),
                tmp_diag_paths=tmp_diag_paths,
                tmp_sc_path=tmp_sc_path,
                val_tbl=val_tbl,
                err_tbl=err_tbl,
            )
            pptx_path = out_dir / f"{name} - {model_tag} Scorecard.pptx"
            prs.save(str(pptx_path))
            outputs.append(str(pptx_path))

            for f in tmp_diag_paths + [tmp_sc_path]:
                Path(f).unlink(missing_ok=True)

        analysis.outputs = outputs
        log("")
        for out in outputs:
            log(f"[>] Saved: {out}")
        log("")
        return analysis
    finally:
        if cleanup_tmp:
            json_path.unlink(missing_ok=True)


def print_steps(source: str) -> list[dict]:
    """Print the step table for a TRIOS file and return the step descriptors."""
    steps = trios_io.discover_steps(source)
    print(trios_io.format_step_table(steps, Path(str(source)).name))
    return steps
