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
        ### 🔬 Bingham plastic explorer

        Drag the sliders to feel what each parameter does — the equation from
        §2, recomputed live. **Red** — shear stress $\\tau$ ·
        **Blue** — apparent viscosity $\\eta = \\tau / \\dot{\\gamma}$ (log–log).
        """
    )
    return


@app.cell
def _(mo):
    tau0 = mo.ui.slider(0.0, 100.0, value=20.0, step=0.5, label="τ₀ — yield stress (Pa)")
    mu_p = mo.ui.slider(0.1, 50.0, value=5.0, step=0.1, label="μ_p — plastic viscosity (Pa·s)")
    mo.vstack([tau0, mu_p])
    return mu_p, tau0


@app.cell
def _(mo, mu_p, np, plt, tau0):
    gd = np.logspace(-3, 3, 200)
    sigma = tau0.value + mu_p.value * gd
    eta = sigma / gd

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.loglog(gd, sigma, color="red", lw=2, label="stress")
    ax1.set_xlabel("shear rate γ̇ (s⁻¹)")
    ax1.set_ylabel("stress τ (Pa)", color="red")
    ax1.tick_params(axis="y", labelcolor="red")
    ax1.grid(True, which="both", alpha=0.3)
    ax2 = ax1.twinx()
    ax2.loglog(gd, eta, color="blue", lw=2, label="viscosity")
    ax2.set_ylabel("viscosity η (Pa·s)", color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")
    fig.tight_layout()

    mo.md(f"**τ₀** = {tau0.value} Pa · **μ_p** = {mu_p.value} Pa·s")
    return fig, gd


@app.cell
def _(fig):
    fig
    return


if __name__ == "__main__":
    app.run()
