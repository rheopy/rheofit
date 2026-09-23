#!/usr/bin/env python3
"""Export marimo interactive explorers to self-contained HTML for the docs.

Runs at docs build time (Read the Docs `pre_build` + CI), so the committed
notebook sources under ``docs/interactive/`` are always what readers get.
Generated HTML goes to ``docs/_static/interactive/<name>/`` (gitignored);
the static preview PNG is committed next to the model page.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent
STATIC_OUT = DOCS / "_static" / "interactive"

# name -> notebook source
NOTEBOOKS = {
    "hb": DOCS / "interactive" / "hb_explorer.py",
}

# default parameters for the static preview (must match notebook defaults)
PREVIEW_DEFAULTS = {"tau0": 20.0, "K": 10.0, "n": 0.6}


def export_wasm(name: str, notebook: Path) -> None:
    # marimo's wasm export shells out to `uv`; make sure it's on PATH.
    bindir = Path(sys.prefix) / ("Scripts" if os.name == "nt" else "bin")
    os.environ["PATH"] = str(bindir) + os.pathsep + os.environ["PATH"]
    out = STATIC_OUT / name
    if out.exists():
        shutil.rmtree(out)
    subprocess.run(
        [sys.executable, "-m", "marimo", "export", "html-wasm",
         str(notebook), "-o", str(out), "--mode", "run"],
        check=True,
    )
    print(f"exported {notebook.name} -> {out}")


def preview_png() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    p = PREVIEW_DEFAULTS
    gd = np.logspace(-3, 3, 200)
    sigma = p["tau0"] + p["K"] * gd ** p["n"]
    eta = sigma / gd

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.loglog(gd, sigma, color="red", lw=2)
    ax1.set_xlabel("shear rate γ̇ (s⁻¹)")
    ax1.set_ylabel("stress σ (Pa)", color="red")
    ax1.tick_params(axis="y", labelcolor="red")
    ax1.grid(True, which="both", alpha=0.3)
    ax2 = ax1.twinx()
    ax2.loglog(gd, eta, color="blue", lw=2)
    ax2.set_ylabel("viscosity η (Pa·s)", color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")
    fig.suptitle(f"τ₀ = {p['tau0']} Pa, K = {p['K']} Pa·sⁿ, n = {p['n']}")
    fig.tight_layout()

    dest = DOCS / "models" / "hb_explorer_preview.png"
    fig.savefig(dest, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"preview -> {dest}")


def main() -> None:
    STATIC_OUT.mkdir(parents=True, exist_ok=True)
    for name, notebook in NOTEBOOKS.items():
        export_wasm(name, notebook)
    preview_png()


if __name__ == "__main__":
    main()
