# ⚗️ rheofit

**Turn flow curves into material physics — with a little help from your AI.**

`rheofit` fits rheological flow curves (viscosity vs shear rate) to constitutive models whose
parameters map onto real material properties: yield stress $\sigma_y$, zero-shear viscosity
$\eta_0$, relaxation time $\lambda$, thinning index $n$. Every fit minimises the *relative*
residual, so `RedChi2` is dimensionless and comparable across steps, samples, and models.

But the fitting engine is only half the story. `rheofit` is also an experiment in **how
domain knowledge should be delivered in the age of AI assistants**: not as a document to be
read, but as curated content *bundled with the code that executes it* — maintained once,
delivered twice: as documentation for humans 📖 and as a skill for AI agents 🤖.

## 💡 The idea: knowledge bundled with execution

A rheology textbook can tell you *what* the TC model means. It cannot fit your data. A code
library can fit your data, but it cannot tell you *when the fit is trustworthy* — which model
to pick, which parameter the data actually earned, when to stop climbing the model ladder.
That judgment is domain expertise, and until now it lived in people's heads.

`rheofit` bundles the two together:

- 🧮 **Executable mathematics** — the nonlinear regression engine: log-space parameters,
  physics-informed starting points, ladder seeding, Sobol multi-start, self-diagnostics.
- 📚 **Curated domain knowledge** — which model for which material, what each parameter means
  physically, how to read residuals, when a parameter isn't earned by the data.
- 🤖 **An AI skill** (`flow-curve-analysis`) — the same knowledge rewritten specifically for
  a large language model: how to use the tool, when to use it, and exactly how the code must
  be run.

### Bring your own model 🧑‍🔬

You don't need our agent — **bring yours**. Point any LLM at the skill and it rapidly learns
the workflow: interview the user (is the sample structured? which steps?), choose the model,
run the analysis, read the diagnostics. The expertise transfers in minutes, not months.

### Sustainable by design 🌱

Without the skill, every session pays the same tax: the model must rediscover the tool,
re-derive the workflow, re-invent glue code — burning tokens and inviting errors. With the
skill, the knowledge is loaded once and reused: **fewer tokens, less reinvention, lower cost
per analysis**. Sustainability here is literal: less compute spent re-learning what is already
written down.

### Safe by construction 🛡️

The skill specifies exactly how the code is invoked — functions, arguments, order of
operations, how results are read. The model doesn't improvise the analysis; it *executes a
specified procedure*. That collapses the hallucination surface: there is far less room to
invent a plausible-looking but wrong workflow when the correct one is spelled out.

### Reproducible and scientifically valuable 🔬

Same versioned code, same specified workflow, every time — regardless of which agent runs
it. An analysis done through the skill can be re-run, audited, and cited. The judgment calls
(model choice, identifiability checks) are recorded as data, not lore.

### Learn as you use 🎓

Because the agent works from the same content as these docs, you can interrupt at any point
and ask *why*: why this model, why that parameter is flagged, what the residual pattern
means. The answer comes back grounded in the documentation, with links — a customized
learning experience that turns each analysis into a short lesson, and each lesson into faster
adoption.

## 🤝 Who builds what

The key is a division of labour:

- **Domain experts and the community** curate the content — the models, the physics, the
  diagnostics, the judgment. This is the hard part, and it stays human.
- **The open-source workflow** (issues, pull requests, reviews) keeps improving the tool and
  the documentation continuously — and every improvement is immediately available to the whole
  user base.
- **The AI** handles delivery — guiding each user through the analysis, answering questions,
  adapting the pace. Adoption becomes easy without becoming shallow.

Experts focus on being right; the agent focuses on being helpful. Neither has to do the
other's job.

## 📦 Installation

```bash
pip install rheofit
```

or from source (`uv` recommended):

```bash
git clone https://github.com/rheopy/rheofit
cd rheofit
uv sync
```

## 🚀 Quickstart

```python
import rheofit

rheofit.print_steps("sample.json")                  # 1. discover steps
df = rheofit.load_step("sample.json", 0)            # 2. load one step
res = rheofit.fit(df, "tc")                         # 3. fit it
rheofit.plot(df, fits=res)                          # 4. look at it
```

or from the command line:

```bash
rheofit sample.json --steps 0 --model tc --effort thorough --seed 0
```

or through the skill, which teaches an agent this whole workflow:

```bash
rheofit install-skill
```

## 🗺️ Where to start

New here? Read the **[Carbopol case study](walkthrough)** — a complete, reproducible
head-to-head of the TC model against Herschel–Bulkley on real data, run the way the skill
runs it. Then see the **[wormlike-micelle + polymer case study](walkthrough-carreau-carreau)**,
where the microstructure-informed `carreau_carreau` model resolves two relaxation times across
a temperature series. And don't miss the **[polymer solution case study](walkthrough-carreau)**,
where a Carreau fit meets the Cox–Merz and Delaware–Rutgers rules on amplitude, flow, and
frequency sweeps. For yield-stress fluids, the **[Carbopol in glycerin case study](walkthrough-carbopol-glycerin)**
pits Herschel–Bulkley against the three-component model and shows how a viscous continuous
phase rewrites the flow curve. Then browse the **[API reference](api)**.

## 🧪 Try it in your browser

The **[rheofit fit app](https://rheopy.github.io/rheofit/)** runs the whole
fitting workflow in your browser — upload a flow curve, preview any model with
sliders, fit it, and rank all nine models by RedChi2. No install, no server;
the calculations are done by the `rheofit` library itself, compiled to
WebAssembly.

## 📥 Download

Prefer to read offline? Every docs build produces **PDF** and **EPUB** versions of
these pages, attached as `rheofit-pdf` and `rheofit-epub` artifacts on the
[latest docs CI run](https://github.com/rheopy/rheofit/actions/workflows/docs.yml) —
open the most recent successful run and grab them from the Artifacts section at the
bottom of the page.

```{toctree}
:maxdepth: 2
:caption: Case studies

walkthrough
walkthrough-carreau-carreau
walkthrough-carreau
walkthrough-carbopol-glycerin
```

```{toctree}
:maxdepth: 2
:caption: Models

models/index
```

```{toctree}
:maxdepth: 2
:caption: Reference

api
```
