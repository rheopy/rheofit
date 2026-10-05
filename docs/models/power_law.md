[← All models](index)

# Fitting the power law model

> 🧬 **The model itself lives in [rheomodel](https://rheomodel.readthedocs.io/en/latest/models/power_law.html).** Equations, parameters, history, applicability, and references are documented there. In code, `rheofit.models.power_law` is a thin adapter over `rheomodel` — same physics, same parameters. This page is about *fitting* it to your data.

The constitutive equation, for reference:

$$
\sigma = K\dot{\gamma}^n
$$

## 🔬 Interactive explorer

Drag the sliders to feel what each parameter does — the equation you just read, recomputed
live in your browser (Python via WebAssembly, no server involved). The dashed line is the
Newtonian reference ($n = 1$, same $K$). The blue axis shows the apparent viscosity
$\eta = \sigma/\dot{\gamma}$.

````{only} builder_html
```{raw} html
<iframe src="../_static/interactive/power_law/index.html" width="100%" height="760" style="border: 1px solid #ddd; border-radius: 8px;" title="Power Law model interactive explorer" loading="lazy"></iframe>
```

*Tip: [open the explorer full-screen](../_static/interactive/power_law/index.html).*
````

*Static preview
($K$ = 10 Pa·sⁿ, $n$ = 0.6):*

![Power Law model explorer preview](power_law_explorer_preview.png)

---

## Parameter Fitting Best Practices

1. **Fit in log–log space:** $\log \sigma = \log K + n \log \dot{\gamma}$ is linear,
   so ordinary least squares on logarithms gives $n$ (slope) and $K$ (intercept) —
   and weights each decade of shear rate equally.
2. **Check the residuals:** systematic curvature on log–log axes means the fluid has
   a plateau the Power Law cannot follow — step up to [Carreau](carreau).
3. **Low-shear cutoff:** exclude the yield-dominated or slip-corrupted low-rate tail
   before fitting; it bends the log–log line and corrupts $n$.
