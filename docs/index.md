# rheofit

**Fit flow curves (viscosity vs shear rate) to rheological models — from Python, the
command line, or an AI agent.**

A flow curve is the fingerprint of a non-Newtonian fluid. Fitting it with a
physically-based model quantifies material properties (yield stress, zero-shear
viscosity, relaxation time, thinning exponent), gives a concise description of the
material, and — when tied to the formulation — tells a formulator which lever to move
to hit a property target.

Every fit minimises the *relative* residual `(model − data) / |data|`, so `RedChi2` is
dimensionless and comparable across steps, samples, and models.

## Installation

```bash
pip install rheofit
```

or, from source:

```bash
git clone https://github.com/rheopy/rheofit
cd rheofit
uv sync
```

## Quickstart

```python
import rheofit

rheofit.print_steps("sample.json")                  # 1. discover steps
df = rheofit.load_step("sample.json", 0)            # 2. load one step
res = rheofit.fit(df, "tc")                         # 3. fit it
rheofit.plot(df, fits=res)                          # 4. look at it
a = rheofit.analyze("sample.json", steps=[0, 2],    # or do it all at once
                    model="tc", labels=["25C", "40C"])
```

The same analysis runs from the command line:

```bash
rheofit sample.json --steps 0 --model tc --effort thorough --seed 0
```

…or through the bundled `flow-curve-analysis` AI skill, which teaches an agent the
whole workflow — interview, model choice, guardrails — from the same codebase:

```bash
rheofit install-skill
```

## Contents

```{toctree}
:maxdepth: 2

walkthrough
api
```
