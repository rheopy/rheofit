#!/usr/bin/env python3
"""Export marimo interactive explorers to self-contained HTML for the docs.

Runs at docs build time (Read the Docs `pre_build` + CI), so the committed
notebook sources under ``docs/interactive/`` are always what readers get.
Generated HTML goes to ``docs/_static/interactive/<name>/`` (gitignored);
static preview PNGs are committed next to the model pages.

To add a model: write ``docs/interactive/<name>_explorer.py`` (marimo
notebook, same layout as the others), add an entry to ``MODELS`` below,
and add the iframe section to the model page.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent
STATIC_OUT = DOCS / "_static" / "interactive"

# name -> {notebook, preview png, title template, default params, stress equation}
MODELS = {
    "hb": {
        "notebook": DOCS / "interactive" / "hb_explorer.py",
        "preview": DOCS / "models" / "hb_explorer_preview.png",
        "title": "τ₀ = {tau0} Pa, K = {K} Pa·sⁿ, n = {n}",
        "defaults": {"tau0": 20.0, "K": 10.0, "n": 0.6},
        "stress": lambda gd, p: p["tau0"] + p["K"] * gd ** p["n"],
    },
    "bingham": {
        "notebook": DOCS / "interactive" / "bingham_explorer.py",
        "preview": DOCS / "models" / "bingham_explorer_preview.png",
        "title": "τ₀ = {tau0} Pa, μ_p = {mu_p} Pa·s",
        "defaults": {"tau0": 20.0, "mu_p": 5.0},
        "stress": lambda gd, p: p["tau0"] + p["mu_p"] * gd,
    },
}


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


def preview_png(spec: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    p = spec["defaults"]
    gd = np.logspace(-3, 3, 200)
    sigma = spec["stress"](gd, p)
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
    fig.suptitle(spec["title"].format(**p))
    fig.tight_layout()

    dest = spec["preview"]
    fig.savefig(dest, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"preview -> {dest}")


def main() -> None:
    STATIC_OUT.mkdir(parents=True, exist_ok=True)
    for name, spec in MODELS.items():
        export_wasm(name, spec["notebook"])
        preview_png(spec)


if __name__ == "__main__":
    main()
