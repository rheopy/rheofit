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
        ### 🔬 Power Law model explorer

        Drag the sliders to feel what each parameter does — the equation from
        §2, recomputed live. **Red** — total shear stress $\\sigma$ ·
        **Blue** — apparent viscosity $\\eta = \\sigma / \\dot{\\gamma}$ (log–log).
        The dashed line is the Newtonian reference ($n = 1$, same $K$): $n < 1$
        shear-thins below it, $n > 1$ shear-thickens above it.
        """
    )
    return


@app.cell
def _(mo):
    K = mo.ui.slider(0.1, 100.0, value=10.0, step=0.1, label="K — consistency index (Pa·sⁿ)")
    n = mo.ui.slider(0.1, 1.5, value=0.6, step=0.01, label="n — flow behavior index (–)")
    mo.vstack([K, n])
    return K, n


@app.cell
def _(K, mo, n, np, plt):
    gd = np.logspace(-3, 3, 200)
    kk, nn = K.value, n.value
    sigma = kk * gd ** nn
    newtonian = kk * gd
    eta = sigma / gd

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.loglog(gd, newtonian, color="red", lw=1, ls="--", alpha=0.6, label="Newtonian ref (n=1)")
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

    mo.md(f"**K** = {kk} Pa·sⁿ · **n** = {nn}")
    return fig, gd


@app.cell
def _(fig):
    fig
    return


if __name__ == "__main__":
    app.run()
