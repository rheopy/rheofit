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
        ### 🔬 Three-Component (TC) explorer

        Drag the sliders to feel what each parameter does — the equation from
        §2, recomputed live. **Red** — total shear stress $\\tau$ ·
        **Blue** — apparent viscosity $\\eta = \\tau / \\dot{\\gamma}$ (log–log).
        Dashed lines decompose the stress into its elastic, plastic, and
        viscous contributions (§3).
        """
    )
    return


@app.cell
def _(mo):
    tau0 = mo.ui.slider(0.0, 100.0, value=20.0, step=0.5, label="τ₀ — yield stress (Pa)")
    gdot_c = mo.ui.slider(0.05, 50.0, value=1.0, step=0.05, label="γ̇_c — critical shear rate (s⁻¹)")
    eta_bg = mo.ui.slider(0.01, 20.0, value=0.5, step=0.01, label="η_bg — background viscosity (Pa·s)")
    mo.vstack([tau0, gdot_c, eta_bg])
    return eta_bg, gdot_c, tau0


@app.cell
def _(eta_bg, gdot_c, mo, np, plt, tau0):
    gd = np.logspace(-3, 3, 200)
    t0, gc, eb = tau0.value, gdot_c.value, eta_bg.value
    elastic = np.full_like(gd, t0)
    plastic = t0 * np.sqrt(gd / gc)
    viscous = eb * gd
    sigma = elastic + plastic + viscous
    eta = sigma / gd

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.loglog(gd, elastic, color="red", lw=1, ls=":", alpha=0.6, label="elastic τ₀")
    ax1.loglog(gd, plastic, color="red", lw=1, ls="--", alpha=0.6, label="plastic")
    ax1.loglog(gd, viscous, color="red", lw=1, ls="-.", alpha=0.6, label="viscous")
    ax1.loglog(gd, sigma, color="red", lw=2.5, label="total stress")
    ax1.set_xlabel("shear rate γ̇ (s⁻¹)")
    ax1.set_ylabel("stress τ (Pa)", color="red")
    ax1.tick_params(axis="y", labelcolor="red")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(loc="upper left", fontsize=8)
    ax2 = ax1.twinx()
    ax2.loglog(gd, eta, color="blue", lw=2, label="viscosity")
    ax2.set_ylabel("viscosity η (Pa·s)", color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")
    fig.tight_layout()

    mo.md(f"**τ₀** = {t0} Pa · **γ̇_c** = {gc} s⁻¹ · **η_bg** = {eb} Pa·s")
    return fig, gd


@app.cell
def _(fig):
    fig
    return


if __name__ == "__main__":
    app.run()
