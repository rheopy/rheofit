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
        ### 🔬 TC-Carreau model explorer

        Drag the sliders to feel what each parameter does — the equation from
        §2, recomputed live. **Red** — total shear stress $\\sigma$ ·
        **Blue** — apparent viscosity $\\eta = \\sigma / \\dot{\\gamma}$ (log–log).
        Dashed lines show the three additive terms: the TC yield stress, the TC
        plastic $\\dot{\\gamma}^{1/2}$ term, and the Carreau thinning term — a
        yield-stress network plus one relaxing microstructure.
        """
    )
    return


@app.cell
def _(mo):
    sigma_y = mo.ui.slider(0.0, 100.0, value=20.0, step=0.5, label="σ_y — yield stress (Pa)")
    gdot_c = mo.ui.slider(0.01, 20.0, value=1.0, step=0.01, label="γ̇_c — plastic transition rate (s⁻¹)")
    eta0 = mo.ui.slider(0.1, 50.0, value=5.0, step=0.1, label="η₀ — Carreau plateau (Pa·s)")
    lam = mo.ui.slider(0.01, 20.0, value=2.0, step=0.01, label="λ — Carreau relaxation time (s)")
    mo.vstack([sigma_y, gdot_c, eta0, lam])
    return eta0, gdot_c, lam, sigma_y


@app.cell
def _(eta0, gdot_c, lam, mo, np, plt, sigma_y):
    gd = np.logspace(-3, 3, 200)
    sy, gdc, e0, la = sigma_y.value, gdot_c.value, eta0.value, lam.value
    yield_term = np.full_like(gd, sy)
    plastic_term = sy * np.sqrt(gd / gdc)
    carreau_term = e0 * gd * (1.0 + (la * gd) ** 2) ** (-0.5)
    sigma = yield_term + plastic_term + carreau_term
    eta = sigma / gd

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.loglog(gd, yield_term, color="red", lw=1, ls=":", alpha=0.6, label="yield σ_y")
    ax1.loglog(gd, plastic_term, color="red", lw=1, ls="--", alpha=0.6, label="plastic term")
    ax1.loglog(gd, carreau_term, color="red", lw=1, ls="-.", alpha=0.6, label="Carreau term")
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

    mo.md(f"**σ_y** = {sy} Pa · **γ̇_c** = {gdc} s⁻¹ · **η₀** = {e0} Pa·s · **λ** = {la} s")
    return fig, gd


@app.cell
def _(fig):
    fig
    return


if __name__ == "__main__":
    app.run()
