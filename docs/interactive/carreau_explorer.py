# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "numpy",
#     "matplotlib",
# ]
# ///

import marimo

__generated_with = "0.24.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    return mo, np, plt


@app.cell
def _(mo):
    mo.md(
        """
        ### 🔬 Carreau model explorer

        Drag the sliders to feel what each parameter does — the equation from
        §2, recomputed live. **Red** — total shear stress $\\sigma$ ·
        **Blue** — apparent viscosity $\\eta = \\sigma / \\dot{\\gamma}$ (log–log).
        Dashed lines are the low-shear Newtonian asymptote ($\\eta_0 \\dot{\\gamma}$)
        and the high-shear power-law asymptote ($\\eta_0 \\lambda^{n-1} \\dot{\\gamma}^n$);
        $\\lambda$ sets where the curve bends between them.
        """
    )
    return


@app.cell
def _(mo):
    eta0 = mo.ui.slider(1.0, 500.0, value=100.0, step=1.0, label="η₀ — zero-shear viscosity (Pa·s)")
    lam = mo.ui.slider(0.01, 20.0, value=1.0, step=0.01, label="λ — relaxation time (s)")
    n = mo.ui.slider(0.1, 1.0, value=0.5, step=0.01, label="n — power-law index (–)")
    mo.vstack([eta0, lam, n])
    return eta0, lam, n


@app.cell
def _(eta0, lam, mo, n, np, plt):
    gd = np.logspace(-3, 3, 200)
    e0, la, nn = eta0.value, lam.value, n.value
    sigma = e0 * gd * (1.0 + (la * gd) ** 2) ** ((nn - 1.0) / 2.0)
    low_asym = e0 * gd
    high_asym = e0 * la ** (nn - 1.0) * gd ** nn
    eta = sigma / gd

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.loglog(gd, low_asym, color="red", lw=1, ls="--", alpha=0.6, label="low-shear Newtonian")
    ax1.loglog(gd, high_asym, color="red", lw=1, ls="-.", alpha=0.6, label="high-shear power law")
    ax1.loglog(gd, sigma, color="red", lw=2.5, label="total stress")
    ax1.set_xlabel("shear rate γ̇ (s⁻¹)")
    ax1.set_ylabel("stress σ (Pa)", color="red")
    ax1.tick_params(axis="y", labelcolor="red")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(loc="upper left", fontsize=8)
    ax2 = ax1.twinx()
    ax2.loglog(gd, eta, color="blue", lw=2, label="viscosity")
    ax2.set_ylabel("viscosity η (Pa·s)", color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")
    fig.tight_layout()

    mo.md(f"**η₀** = {e0} Pa·s · **λ** = {la} s · **n** = {nn}")
    return fig, gd


@app.cell
def _(fig):
    fig
    return


if __name__ == "__main__":
    app.run()
