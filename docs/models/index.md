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
| `casson` | $\sigma = (\sqrt{\sigma_y} + \sqrt{K\dot{\gamma}})^2$ | 🚧 coming soon |
| `tc` | $\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2} + \eta_{bg}\dot{\gamma}$ | [📖 guide](tc) |
| `tc_carreau` | tc + Carreau term | 🚧 coming soon |
| `tccc` | tc + two Carreau terms | 🚧 coming soon |

## 💧 No yield stress

| Model | Equation | Page |
| ----- | -------- | ---- |
| `power_law` | $\sigma = K\dot{\gamma}^n$ | 🚧 coming soon |
| `carreau` | $\sigma = \eta_0\dot{\gamma}[1+(\lambda\dot{\gamma})^2]^{(n-1)/2}$ | 🚧 coming soon |
| `carreau_carreau` | two relaxation-time components | 🚧 coming soon |

```{toctree}
:maxdepth: 1
:hidden:

herschel_bulkley
bingham
tc
```
