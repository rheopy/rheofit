[← All models](index)

# Fitting the Bingham plastic model

> 🧬 **The model itself lives in [rheomodel](https://rheomodel.readthedocs.io/en/latest/models/bingham.html).** Equations, parameters, history, applicability, and references are documented there. In code, `rheofit.models.bingham` is a thin adapter over `rheomodel` — same physics, same parameters. This page is about *fitting* it to your data.

The constitutive equation, for reference:

$$
\tau = \tau_0 + \mu_p\dot{\gamma}
$$

## 🔬 Interactive explorer

Drag the sliders to feel what each parameter does — the equation you just read, recomputed
live in your browser (Python via WebAssembly, no server involved).

````{only} builder_html
```{raw} html
<iframe src="../_static/interactive/bingham/index.html" width="100%" height="760" style="border: 1px solid #ddd; border-radius: 8px;" title="Bingham plastic interactive explorer" loading="lazy"></iframe>
```

*Tip: [open the explorer full-screen](../_static/interactive/bingham/index.html).*
````

*Static preview
(τ₀ = 20 Pa, μ_p = 5 Pa·s):*

![Bingham plastic explorer preview](bingham_explorer_preview.png)

---

## Parameter Fitting Challenges and Objective Functions

Because the Bingham equation is linear in the yielded domain ($\tau = \tau_0 + \mu_p \dot{\gamma}$), fitting appears simpler than for 3-parameter non-linear models. However, practical fitting introduces distinct analytical challenges:

1. **Identification of the Yield Boundary:** Including data points from the unyielded or transition regime ($\vert{}\tau\vert{} \le \tau_0$) in linear regression corrupts the line of best fit, distorting both $\tau_0$ and $\mu_p$.
2. **Instrument Limitations at Low Shear:** Rotational rheometers encounter torque limits and wall slip at low shear rates, generating erroneous stress values near yielding.

### Residual Weighting Schemes

The choice of objective function in least-squares regression heavily determines parameter accuracy:

#### 1. Absolute Residual Sum of Squares ($S_{abs}$)

$$
S_{abs} = \sum_{i=1}^{N} \left( \tau_{i, \text{measured}} - (\tau_0 + \mu_p \dot{\gamma}_i) \right)^2
$$

* **Behavior:** Weighting scales with the magnitude of shear stress (in Pascals).
* **Consequence:** High shear rate measurements (where $\tau$ is largest) dominate the sum. Errors in low shear rate measurements contribute negligibly, leading to inaccurate extrapolations of the yield stress intercept ($\tau_0$).

#### 2. Relative Residual Sum of Squares ($S_{rel}$)

$$
S_{rel} = \sum_{i=1}^{N} \left( \frac{\tau_{i, \text{measured}} - (\tau_0 + \mu_p \dot{\gamma}_i)}{\tau_{i, \text{measured}}} \right)^2 = \sum_{i=1}^{N} \left( 1 - \frac{\tau_0 + \mu_p \dot{\gamma}_i}{\tau_i} \right)^2
$$

* **Behavior:** Normalizes each error term by the measured stress value.
* **Consequence:** Equal weight is given to data across low, medium, and high shear rate regimes, yielding more accurate estimations of $\tau_0$.

#### 3. Weighted Linear Least Squares (WLLS)

$$
S_{weighted} = \sum_{i=1}^{N} w_i \left( \tau_i - (\tau_0 + \mu_p \dot{\gamma}_i) \right)^2 \quad \text{where } w_i = \frac{1}{\dot{\gamma}_i} \text{ or } \frac{1}{\tau_i^2}
$$

* **Behavior:** Applies inverse variance or magnitude weighting to balance high-shear leverage with low-shear intercept sensitivity.

## Recommended Fitting Best Practices

1. **Unyielded Data Truncation:** Inspect raw flow curves on a linear scale $(\dot{\gamma}, \tau)$ and restrict the regression dataset strictly to points where flow is established ($\vert{}\tau\vert{} > \tau_0$).
2. **Two-Stage Experimental Hybrid Method:**
   * Measure the static yield stress ($\tau_0$) independently using direct methods (vane geometry stress ramps, stress-growth tests, or creep compliance).
   * Substitute the measured $\tau_0$ into the Bingham model and perform a single-parameter linear regression to determine $\mu_p$:
     $$
     \mu_p = \frac{\sum_{i=1}^{N} \dot{\gamma}_i (\tau_i - \tau_0)}{\sum_{i=1}^{N} \dot{\gamma}_i^2}
     $$
3. **Model Selection Verification:** If a plot of residual values $(\tau_i - \tau_{\text{predicted}})$ shows systematic curvature rather than random scatter around zero, transition from the 2-parameter Bingham model to a 3-parameter model (Herschel–Bulkley or Casson).
