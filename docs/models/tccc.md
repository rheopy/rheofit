[← All models](index)

# Fitting the TCCC model

> 🧬 **The model itself lives in [rheomodel](https://rheomodel.readthedocs.io/en/latest/models/tccc.html).** Equations, parameters, history, applicability, and references are documented there. In code, `rheofit.models.tccc` is a thin adapter over `rheomodel` — same physics, same parameters. This page is about *fitting* it to your data.

The constitutive equation, for reference:

$$
\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2} + \sum_i \eta_{0,i}\dot{\gamma}[1+(\lambda_i\dot{\gamma})^2]^{-1/4,-1/2}
$$

## 🔬 Interactive explorer

Drag the sliders to feel what each parameter does — the equation you just read, recomputed
live in your browser (Python via WebAssembly, no server involved). Dashed lines show the
four additive terms: yield, plastic, and the two Carreau components thinning at their own
timescales. The blue axis shows the apparent viscosity $\eta = \sigma/\dot{\gamma}$.

````{only} builder_html
```{raw} html
<iframe src="../_static/interactive/tccc/index.html" width="100%" height="760" style="border: 1px solid #ddd; border-radius: 8px;" title="TCCC model interactive explorer" loading="lazy"></iframe>
```

*Tip: [open the explorer full-screen](../_static/interactive/tccc/index.html).*
````

*Static preview
($\sigma_y$ = 20 Pa, $\dot{\gamma}_c$ = 1.0 s⁻¹, $\eta_{0,1}$ = 3 Pa·s, $\lambda_1$ = 0.5 s,
$\eta_{0,2}$ = 7 Pa·s, $\lambda_2$ = 20 s):*

![TCCC model explorer preview](tccc_explorer_preview.png)

---

## Parameter Fitting Best Practices

1. **Climb from below:** fit [TC](tc), then [TC-Carreau](tc_carreau), then TCCC —
   each rung must beat the last on cross-validated residuals, not just training error.
2. **Seed from the bends:** $\lambda_1$, $\lambda_2$ initial guesses come off the
   viscosity curve at $\dot{\gamma} \sim 1/\lambda_i$; bound them apart.
3. **Kill degenerate modes:** if a Carreau term's relative uncertainty exceeds ~50%,
   drop it and step back down the ladder — parsimony wins.
