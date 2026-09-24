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
        ### 🔬 Carreau-Carreau model explorer

        Drag the sliders to feel what each parameter does — the equation from
        §2, recomputed live. **Red** — total shear stress $\\sigma$ ·
        **Blue** — apparent viscosity $\\eta = \\sigma / \\dot{\\gamma}$ (log–log).
        Dashed lines show the two Carreau components: component 1 thins first
        (short $\\lambda_1$), component 2 later (long $\\lambda_2$) — two bends,
        two microstructural contributors.
        """
    )
    return


@app.cell
def _(mo):
    eta0_1 = mo.ui.slider(1.0, 200.0, value=30.0, step=1.0, label="η₀,₁ — component 1 plateau (Pa·s)")
    lam1 = mo.ui.slider(0.01, 5.0, value=0.3, step=0.01, label="λ₁ — component 1 relaxation time (s)")
    eta0_2 = mo.ui.slider(1.0, 200.0, value=70.0, step=1.0, label="η₀,₂ — component 2 plateau (Pa·s)")
    lam2 = mo.ui.slider(1.0, 50.0, value=10.0, step=0.5, label="λ₂ — component 2 relaxation time (s)")
    mo.vstack([eta0_1, lam1, eta0_2, lam2])
    return eta0_1, eta0_2, lam1, lam2


@app.cell
def _(eta0_1, eta0_2, lam1, lam2, mo, np, plt):
    gd = np.logspace(-3, 3, 200)
    e01, l1, e02, l2 = eta0_1.value, lam1.value, eta0_2.value, lam2.value
    c1 = e01 * gd * (1.0 + (l1 * gd) ** 2) ** (-0.25)
    c2 = e02 * gd * (1.0 + (l2 * gd) ** 2) ** (-0.5)
    sigma = c1 + c2
    eta = sigma / gd

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.loglog(gd, c1, color="red", lw=1, ls="--", alpha=0.6, label="component 1")
    ax1.loglog(gd, c2, color="red", lw=1, ls="-.", alpha=0.6, label="component 2")
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

    mo.md(f"**η₀,₁** = {e01} Pa·s · **λ₁** = {l1} s · **η₀,₂** = {e02} Pa·s · **λ₂** = {l2} s")
    return fig, gd


@app.cell
def _(fig):
    fig
    return


if __name__ == "__main__":
    app.run()
