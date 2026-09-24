# 🧪 Models

Each model in `rheofit` gets its own page: historical foundations, the physics it captures,
the materials it describes, its intrinsic limitations, and how to fit it well. The
[Herschel–Bulkley guide](herschel_bulkley) sets the template — one curated page per model,
written for humans and readable by the AI skill.

Within each family the models form a ladder 🪜 — climb only if the residuals show structure
the simpler model missed. Prefer the simplest model that fits: extra parameters buy little
once `RedChi2` is below `0.01`, and they cost identifiability.

## 🧱 With yield stress (structured)

| Model | Equation | Page |
| ----- | -------- | ---- |
| `herschel_bulkley` | $\tau = \tau_0 + K\dot{\gamma}^n$ | [📖 guide](herschel_bulkley) |
| `bingham` | $\tau = \tau_0 + \mu_p\dot{\gamma}$ | [📖 guide](bingham) |
| `casson` | $\sigma = (\sqrt{\sigma_y} + \sqrt{K\dot{\gamma}})^2$ | [📖 guide](casson) |
| `tc` | $\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2} + \eta_{bg}\dot{\gamma}$ | [📖 guide](tc) |
| `tc_carreau` | $\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2} + \eta_0\dot{\gamma}[1+(\lambda\dot{\gamma})^2]^{-1/2}$ | [📖 guide](tc_carreau) |
| `tccc` | $\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2} + \sum_i \eta_{0,i}\dot{\gamma}[1+(\lambda_i\dot{\gamma})^2]^{-1/4,-1/2}$ | [📖 guide](tccc) |

## 💧 No yield stress

| Model | Equation | Page |
| ----- | -------- | ---- |
| `power_law` | $\sigma = K\dot{\gamma}^n$ | 🚧 coming soon |
| `carreau` | $\sigma = \eta_0\dot{\gamma}[1+(\lambda\dot{\gamma})^2]^{(n-1)/2}$ | 🚧 coming soon |
| `carreau_carreau` | $\sigma = \sum_{i=1,2} \eta_{0,i}\dot{\gamma}[1+(\lambda_i\dot{\gamma})^2]^{-1/4,-1/2}$ | [📖 guide](carreau_carreau) |

```{toctree}
:maxdepth: 1
:hidden:

herschel_bulkley
bingham
tc
casson
power_law
carreau
carreau_carreau
tc_carreau
tccc
```
