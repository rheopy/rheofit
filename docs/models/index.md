# 🧪 Models

Each model gets its own fitting page: how to fit it well with `rheofit`,
with a live interactive explorer per model. The model science itself — historical
foundations, the physics it captures, the materials it describes, intrinsic limitations,
and verified references — lives in [rheomodel](https://rheomodel.readthedocs.io/en/latest/),
which `rheofit` consumes directly (`rheofit.models.<name>` is a thin adapter over `rheomodel`).

Within each family the models form a ladder 🪜 — climb only if the residuals show structure
the simpler model missed. Prefer the simplest model that fits: extra parameters buy little
once `RedChi2` is below `0.01`, and they cost identifiability.

## 🧱 With yield stress (structured)

| Model | Equation | Page |
| ----- | -------- | ---- |
| `herschel_bulkley` | $\tau = \tau_0 + K\dot{\gamma}^n$ | [🔧 fitting guide](herschel_bulkley) |
| `bingham` | $\tau = \tau_0 + \mu_p\dot{\gamma}$ | [🔧 fitting guide](bingham) |
| `casson` | $\sigma = (\sqrt{\sigma_y} + \sqrt{K\dot{\gamma}})^2$ | [🔧 fitting guide](casson) |
| `tc` | $\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2} + \eta_{bg}\dot{\gamma}$ | [🔧 fitting guide](tc) |
| `tc_carreau` | $\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2} + \eta_0\dot{\gamma}[1+(\lambda\dot{\gamma})^2]^{-1/2}$ | [🔧 fitting guide](tc_carreau) |
| `tccc` | $\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2} + \sum_i \eta_{0,i}\dot{\gamma}[1+(\lambda_i\dot{\gamma})^2]^{-1/4,-1/2}$ | [🔧 fitting guide](tccc) |

## 💧 No yield stress

| Model | Equation | Page |
| ----- | -------- | ---- |
| `power_law` | $\sigma = K\dot{\gamma}^n$ | [🔧 fitting guide](power_law) |
| `carreau` | $\sigma = \eta_0\dot{\gamma}[1+(\lambda\dot{\gamma})^2]^{(n-1)/2}$ | [🔧 fitting guide](carreau) |
| `carreau_carreau` | $\sigma = \sum_{i=1,2} \eta_{0,i}\dot{\gamma}[1+(\lambda_i\dot{\gamma})^2]^{-1/4,-1/2}$ | [🔧 fitting guide](carreau_carreau) |

```{toctree}
:maxdepth: 2
:hidden:
:caption: 🧱 With yield stress

herschel_bulkley
bingham
casson
tc
tc_carreau
tccc
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: 💧 No yield stress

power_law
carreau
carreau_carreau
```
