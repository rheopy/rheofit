"""TRIOS JSON loading for rheofit.

Reads TA Instruments TRIOS JSON directly (no tadatakit):
  * steps come from ``Results.Processed.ResultsSteps`` (0-based list)
  * rows come from ``Results.Processed.Rows``, grouped by ``Results Step Id``

Inputs may be a local path or an HTTP(S) URL.
"""
from __future__ import annotations

import json
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
DEMO_JSON_FILE = DATA_DIR / "structured_shampoo.json"
DEMO_SAMPLE_NAME = "Structured Shampoo (demo)"

COLUMN_RENAME = {
    # flow curve
    "Shear rate_1/s": "Shear rate / 1/s",
    "Viscosity_Pa.s": "Viscosity / Pa.s",
    "Stress_Pa": "Stress / Pa",
    "Stress (step)_Pa": "Stress (step) / Pa",
    # oscillatory (frequency / amplitude sweeps)
    "Angular frequency_rad/s": "Angular frequency / rad/s",
    "Frequency_Hz": "Frequency / Hz",
    "Storage modulus_Pa": "Storage modulus / Pa",
    "Loss modulus_Pa": "Loss modulus / Pa",
    "Complex modulus_Pa": "Complex modulus / Pa",
    "Complex viscosity_Pa.s": "Complex viscosity / Pa.s",
    "Oscillation strain_%": "Oscillation strain / %",
    "Oscillation stress_Pa": "Oscillation stress / Pa",
    "Oscillation strain rate_1/s": "Oscillation strain rate / 1/s",
    "Temperature_\u00b0C": "Temperature / degC",
}

# Test types recognised by rheofit. TRIOS exports every column on every row, so
# the test type cannot be inferred from column presence -- it comes from the step
# name, with a fallback based on which control variable actually sweeps.
TEST_TYPES = ("flow_curve", "frequency_sweep", "amplitude_sweep")

_NAME_PATTERNS = (
    ("amplitude_sweep", ("amplitude", "strain sweep", "oscillation-amplitude")),
    ("frequency_sweep", ("frequency", "oscillation-frequency")),
    ("flow_curve", ("flow", "shear rate", "steady state")),
)

# Candidate x-axis column per test type, used by the variance fallback.
_SWEEP_COLUMNS = {
    "amplitude_sweep": "Oscillation strain / %",
    "frequency_sweep": "Angular frequency / rad/s",
    "flow_curve": "Shear rate / 1/s",
}

# Columns each test type needs before a row is considered usable.
_REQUIRED_COLUMNS = {
    "flow_curve": ["Shear rate / 1/s", "Stress / Pa"],
    "frequency_sweep": ["Angular frequency / rad/s", "Storage modulus / Pa", "Loss modulus / Pa"],
    "amplitude_sweep": ["Oscillation strain / %", "Storage modulus / Pa", "Loss modulus / Pa"],
}


def test_type_from_name(name: str) -> str | None:
    """Infer a test type from a TRIOS step name, or ``None`` if unrecognised."""
    low = str(name).lower()
    for test_type, keywords in _NAME_PATTERNS:
        if any(k in low for k in keywords):
            return test_type
    return None


def _sweep_span(series: pd.Series) -> float:
    """Ratio between largest and smallest positive value (1.0 when held constant)."""
    vals = pd.to_numeric(series, errors="coerce").dropna()
    vals = vals[vals > 0]
    if len(vals) < 3:
        return 1.0
    return float(vals.max() / vals.min())


def detect_test_type(df: pd.DataFrame, name: str | None = None) -> str:
    """Best-effort test type for a standardised step DataFrame.

    The step ``name`` wins when it is recognisable. Otherwise the control
    variable with the widest span decides: an amplitude sweep holds angular
    frequency fixed while strain sweeps, and a frequency sweep does the reverse.
    """
    if name is None:
        name = df.attrs.get("step_name", "")
    by_name = test_type_from_name(name)
    if by_name is not None:
        return by_name

    spans = {
        test_type: _sweep_span(df[col])
        for test_type, col in _SWEEP_COLUMNS.items()
        if col in df.columns
    }
    spans = {k: v for k, v in spans.items() if v > 1.5}
    if not spans:
        return "flow_curve"
    return max(spans, key=spans.get)


def demo_source() -> str:
    """Bundled demo TRIOS JSON."""
    if DEMO_JSON_FILE.is_file():
        return str(DEMO_JSON_FILE)
    raise FileNotFoundError(f"Demo file not found at {DEMO_JSON_FILE}")


def is_http_url(path_or_url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(str(path_or_url))
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"}


def _download_json_to_temp(url: str, timeout: int = 120) -> Path:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "rheofit/1.0",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - scheme validated
            payload = resp.read()
    except HTTPError as exc:
        if exc.code in {401, 403}:
            raise RuntimeError(
                "Cannot access the URL (HTTP 401/403). The file appears to require authentication. "
                "Please either download/upload the JSON locally, or provide a direct URL that is "
                "accessible from this Python session."
            ) from exc
        raise RuntimeError(f"Failed to download JSON from URL: HTTP {exc.code} {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"Failed to download JSON from URL: {exc.reason}") from exc

    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    tmp.write(payload)
    tmp.flush()
    tmp.close()
    return Path(tmp.name)


def materialize(path_or_url: str) -> tuple[Path, bool]:
    """Return ``(local_json_path, needs_cleanup)`` for a path or URL input."""
    if is_http_url(path_or_url):
        if not str(path_or_url).lower().startswith(("http://", "https://")):
            raise ValueError("Only http(s) URLs are supported")
        return _download_json_to_temp(str(path_or_url)), True
    return Path(path_or_url).resolve(), False


def _read_processed(json_path: str | Path) -> dict:
    with open(json_path, encoding="utf-8") as f:
        doc = json.load(f)
    return doc["Results"]["Processed"]


def discover_steps(json_path: str | Path) -> list[dict]:
    """List the steps of a TRIOS file as ``{step_index, name, n_rows}`` dicts.

    Accepts a local path or an HTTP(S) URL. Indices are 0-based ``ResultsSteps``
    indices, not TRIOS procedure step numbers.
    """
    local, cleanup = materialize(str(json_path))
    try:
        processed = _read_processed(local)
        steps_meta = processed["ResultsSteps"]
        rows = processed["Rows"]

        counts: dict[str, int] = {}
        for row in rows:
            sid = row.get("Results Step Id")
            if sid is not None:
                counts[sid] = counts.get(sid, 0) + 1

        return [
            {
                "step_index": i,
                "name": s.get("Name", f"Step {i}"),
                "n_rows": counts.get(s["Id"], 0),
                "test_type": test_type_from_name(s.get("Name", "")) or "unknown",
            }
            for i, s in enumerate(steps_meta)
        ]
    finally:
        if cleanup:
            local.unlink(missing_ok=True)


def load_step(json_path: str | Path, step_index: int) -> pd.DataFrame:
    """Load one step as a standardised DataFrame.

    Flow-curve columns become ``'Shear rate / 1/s'``, ``'Viscosity / Pa.s'`` and
    ``'Stress / Pa'`` (falling back to ``'Stress (step) / Pa'``); oscillatory
    columns become ``'Angular frequency / rad/s'``, ``'Oscillation strain / %'``,
    ``'Storage modulus / Pa'`` and ``'Loss modulus / Pa'``.

    The detected test type and step name are recorded in ``df.attrs`` so the
    plotting layer can pick the right view without being told.
    """
    local, cleanup = materialize(str(json_path))
    try:
        processed = _read_processed(local)
        step_meta = processed["ResultsSteps"][step_index]
        step_id = step_meta["Id"]
        step_name = step_meta.get("Name", f"Step {step_index}")
        step_rows = [r for r in processed["Rows"] if r.get("Results Step Id") == step_id]
        df = pd.DataFrame(step_rows).rename(columns=COLUMN_RENAME)

        if "Stress / Pa" not in df.columns and "Stress (step) / Pa" in df.columns:
            df["Stress / Pa"] = df["Stress (step) / Pa"]

        numeric_cols = set(COLUMN_RENAME.values()) | {"Tan(delta)"}
        for col in numeric_cols & set(df.columns):
            df[col] = pd.to_numeric(df[col], errors="coerce")

        test_type = detect_test_type(df, name=step_name)
        required = [c for c in _REQUIRED_COLUMNS[test_type] if c in df.columns]
        if required:
            df = df.dropna(subset=required)

        df = df.reset_index(drop=True)
        df.attrs["step_name"] = step_name
        df.attrs["step_index"] = step_index
        df.attrs["test_type"] = test_type
        return df
    finally:
        if cleanup:
            local.unlink(missing_ok=True)


def load_steps(json_path: str | Path, step_indices: list[int]) -> dict[int, pd.DataFrame]:
    """Load several steps at once, keyed by step index (single file read)."""
    local, cleanup = materialize(str(json_path))
    try:
        return {i: load_step(local, i) for i in step_indices}
    finally:
        if cleanup:
            local.unlink(missing_ok=True)


def format_step_table(steps: list[dict], source_name: str = "") -> str:
    """Render the step table used by the skill's step-discovery stage."""
    lines = [
        f"\nAvailable steps in: {source_name}" if source_name else "\nAvailable steps",
        "  NOTE: indices below are ResultsSteps indices (0-based), NOT procedure step indices.",
        f"{'Idx':<5} {'Name':<50} {'Rows':>6}  {'Test type':<16}",
        "-" * 82,
    ]
    for s in steps:
        marker = "  <-- data" if s["n_rows"] > 0 else ""
        test_type = s.get("test_type", "unknown")
        lines.append(
            f"{s['step_index']:<5} {s['name']:<50} {s['n_rows']:>6}  {test_type:<16}{marker}"
        )
    return "\n".join(lines) + "\n"
