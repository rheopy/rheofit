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
        ### 🔬 TCCC model explorer

        Drag the sliders to feel what each parameter does — the equation from
        §2, recomputed live. **Red** — total shear stress $\\sigma$ ·
        **Blue** — apparent viscosity $\\eta = \\sigma / \\dot{\\gamma}$ (log–log).
        Dashed lines show the four additive terms: the TC yield stress, the TC
        plastic $\\dot{\\gamma}^{1/2}$ term, and two Carreau thinning terms with
        distinct relaxation times — a yield-stress network plus two relaxing
        microstructures.
        """
    )
    return


@app.cell
def _(mo):
    sigma_y = mo.ui.slider(0.0, 100.0, value=20.0, step=0.5, label="σ_y — yield stress (Pa)")
    gdot_c = mo.ui.slider(0.01, 20.0, value=1.0, step=0.01, label="γ̇_c — plastic transition rate (s⁻¹)")
    eta0_1 = mo.ui.slider(0.1, 50.0, value=3.0, step=0.1, label="η₀,₁ — Carreau 1 plateau (Pa·s)")
    lam1 = mo.ui.slider(0.01, 5.0, value=0.5, step=0.01, label="λ₁ — Carreau 1 relaxation time (s)")
    eta0_2 = mo.ui.slider(0.1, 50.0, value=7.0, step=0.1, label="η₀,₂ — Carreau 2 plateau (Pa·s)")
    lam2 = mo.ui.slider(1.0, 100.0, value=20.0, step=0.5, label="λ₂ — Carreau 2 relaxation time (s)")
    mo.vstack([sigma_y, gdot_c, eta0_1, lam1, eta0_2, lam2])
    return eta0_1, eta0_2, gdot_c, lam1, lam2, sigma_y


@app.cell
def _(eta0_1, eta0_2, gdot_c, lam1, lam2, mo, np, plt, sigma_y):
    gd = np.logspace(-3, 3, 200)
    sy, gdc = sigma_y.value, gdot_c.value
    e01, l1, e02, l2 = eta0_1.value, lam1.value, eta0_2.value, lam2.value
    yield_term = np.full_like(gd, sy)
    plastic_term = sy * np.sqrt(gd / gdc)
    c1 = e01 * gd * (1.0 + (l1 * gd) ** 2) ** (-0.25)
    c2 = e02 * gd * (1.0 + (l2 * gd) ** 2) ** (-0.5)
    sigma = yield_term + plastic_term + c1 + c2
    eta = sigma / gd

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.loglog(gd, yield_term, color="red", lw=1, ls=":", alpha=0.6, label="yield σ_y")
    ax1.loglog(gd, plastic_term, color="red", lw=1, ls="--", alpha=0.6, label="plastic term")
    ax1.loglog(gd, c1, color="red", lw=1, ls="-.", alpha=0.6, label="Carreau 1")
    ax1.loglog(gd, c2, color="red", lw=1, ls=(0, (3, 1, 1, 1)), alpha=0.6, label="Carreau 2")
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

    mo.md(f"**σ_y** = {sy} Pa · **γ̇_c** = {gdc} s⁻¹ · **η₀,₁** = {e01} Pa·s · **λ₁** = {l1} s · **η₀,₂** = {e02} Pa·s · **λ₂** = {l2} s")
    return fig, gd


@app.cell
def _(fig):
    fig
    return


if __name__ == "__main__":
    app.run()
