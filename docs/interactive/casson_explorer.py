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
        ### 🔬 Casson model explorer

        Drag the sliders to feel what each parameter does — the equation from
        §2, recomputed live. **Red** — total shear stress $\\tau$ ·
        **Blue** — apparent viscosity $\\eta = \\tau / \\dot{\\gamma}$ (log–log).
        Dashed lines show the three terms of the expanded form
        $\\tau = \\tau_0 + 2\\sqrt{\\tau_0 \\eta_{bg} \\dot{\\gamma}} + \\eta_{bg} \\dot{\\gamma}$.
        """
    )
    return


@app.cell
def _(mo):
    tau0 = mo.ui.slider(0.0, 100.0, value=20.0, step=0.5, label="τ₀ — yield stress (Pa)")
    eta_bg = mo.ui.slider(0.01, 20.0, value=0.5, step=0.01, label="η_bg — Casson plastic viscosity (Pa·s)")
    mo.vstack([tau0, eta_bg])
    return eta_bg, tau0


@app.cell
def _(eta_bg, mo, np, plt, tau0):
    gd = np.logspace(-3, 3, 200)
    t0, eb = tau0.value, eta_bg.value
    yield_term = np.full_like(gd, t0)
    cross_term = 2 * np.sqrt(t0 * eb * gd)
    viscous_term = eb * gd
    sigma = yield_term + cross_term + viscous_term
    eta = sigma / gd

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.loglog(gd, yield_term, color="red", lw=1, ls=":", alpha=0.6, label="yield τ₀")
    ax1.loglog(gd, cross_term, color="red", lw=1, ls="--", alpha=0.6, label="cross term")
    ax1.loglog(gd, viscous_term, color="red", lw=1, ls="-.", alpha=0.6, label="viscous")
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

    mo.md(f"**τ₀** = {t0} Pa · **η_bg** = {eb} Pa·s")
    return fig, gd


@app.cell
def _(fig):
    fig
    return


if __name__ == "__main__":
    app.run()
