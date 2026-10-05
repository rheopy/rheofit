[← All models](index)

# Fitting the TC (three-component) model

> 🧬 **The model itself lives in [rheomodel](https://rheomodel.readthedocs.io/en/latest/models/tc.html).** Equations, parameters, history, applicability, and references are documented there. In code, `rheofit.models.tc` is a thin adapter over `rheomodel` — same physics, same parameters. This page is about *fitting* it to data.

The constitutive equation, for reference:

$$
\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2} + \eta_{bg}\dot{\gamma}
$$

## Worked example

Generate a flow curve from `rheomodel` with known parameters, add 2% noise, and fit it with `rheofit`:

```python
import numpy as np
import pandas as pd
from rheomodel import get_model
import rheofit

# 1. synthetic flow curve from rheomodel: known truth + 2% noise
model = get_model("tc")
gamma_dot = np.logspace(-2, 3, 25)
true = {"sigma_y": 10.0, "gamma_dot_c": 1.0, "eta_bg": 2.0}
rng = np.random.default_rng(0)
stress = model.equation(gamma_dot, **true)
stress = stress * (1 + 0.02 * rng.standard_normal(gamma_dot.size))

# 2. fit it with rheofit
df = pd.DataFrame({"Shear rate / 1/s": gamma_dot, "Stress / Pa": stress})
res = rheofit.fit(df, "tc", effort="fast", seed=0)

for name, p in res["params"].items():
    print(f"{name:12s} true={true[name]:8.3g}  fit={p['value']:8.3g} ± {p['stderr']:.2g}")
print(f"RedChi2 = {res['redchi']:.2e}")
```

Output:

```
sigma_y      true=      10  fit=    10.2 ± 0.083
gamma_dot_c  true=       1  fit=    1.13 ± 0.05
eta_bg       true=       2  fit=    2.05 ± 0.02
RedChi2 = 2.34e-04
```

![TC (three-component) — fit to synthetic data](tc_fit_example.png)

## 🔬 Interactive explorer

Drag the sliders to feel what each parameter does — the equation you just read, recomputed
live in your browser (Python via WebAssembly, no server involved). The dashed lines decompose
the total stress (red) into its three physical contributions: **elastic** τ₀,
**plastic** τ₀(γ̇/γ̇_c)^{1/2}, and **viscous** η_bg·γ̇ — the heart of §3. The blue axis shows
the apparent viscosity η = τ/γ̇.

````{only} builder_html
```{raw} html
<iframe src="../_static/interactive/tc/index.html" width="100%" height="760" style="border: 1px solid #ddd; border-radius: 8px;" title="Three-Component model interactive explorer" loading="lazy"></iframe>
```

*Tip: [open the explorer full-screen](../_static/interactive/tc/index.html).*
````

*Static preview
(τ₀ = 20 Pa, γ̇_c = 1.0 s⁻¹, η_bg = 0.5 Pa·s):*

![Three-Component model explorer preview](tc_explorer_preview.png)
