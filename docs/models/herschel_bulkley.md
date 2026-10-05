[← All models](index)

# Fitting the Herschel–Bulkley model

> 🧬 **The model itself lives in [rheomodel](https://rheomodel.readthedocs.io/en/latest/models/herschel_bulkley.html).** Equations, parameters, history, applicability, and references are documented there. In code, `rheofit.models.herschel_bulkley` is a thin adapter over `rheomodel` — same physics, same parameters. This page is about *fitting* it to data.

The constitutive equation, for reference:

$$
\tau = \tau_0 + K\dot{\gamma}^n
$$

## Worked example

Generate a flow curve from `rheomodel` with known parameters, add 2% noise, and fit it with `rheofit`:

```python
import numpy as np
import pandas as pd
from rheomodel import get_model
import rheofit

# 1. synthetic flow curve from rheomodel: known truth + 2% noise
model = get_model("herschel_bulkley")
gamma_dot = np.logspace(-2, 2, 25)
true = {"sigma_y": 15.0, "K": 8.0, "n": 0.5}
rng = np.random.default_rng(0)
stress = model.equation(gamma_dot, **true)
stress = stress * (1 + 0.02 * rng.standard_normal(gamma_dot.size))

# 2. fit it with rheofit
df = pd.DataFrame({"Shear rate / 1/s": gamma_dot, "Stress / Pa": stress})
res = rheofit.fit(df, "herschel_bulkley", effort="fast", seed=0)

for name, p in res["params"].items():
    print(f"{name:12s} true={true[name]:8.3g}  fit={p['value']:8.3g} ± {p['stderr']:.2g}")
print(f"RedChi2 = {res['redchi']:.2e}")
```

Output:

```
sigma_y      true=      15  fit=    15.2 ± 0.13
K            true=       8  fit=    7.55 ± 0.19
n            true=     0.5  fit=   0.517 ± 0.0068
RedChi2 = 2.57e-04
```

![Herschel–Bulkley — fit to synthetic data](herschel_bulkley_fit_example.png)

## 🔬 Interactive explorer

Drag the sliders to feel what each parameter does — the equation you just read, recomputed
live in your browser (Python via WebAssembly, no server involved).

````{only} builder_html
```{raw} html
<iframe src="../_static/interactive/hb/index.html" width="100%" height="760" style="border: 1px solid #ddd; border-radius: 8px;" title="Herschel–Bulkley interactive explorer" loading="lazy"></iframe>
```

*Tip: [open the explorer full-screen](../_static/interactive/hb/index.html).*
````

*Static preview
(τ₀ = 20 Pa, K = 10 Pa·sⁿ, n = 0.6):*

![Herschel–Bulkley explorer preview](hb_explorer_preview.png)
