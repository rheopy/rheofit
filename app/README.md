# 🧪 rheofit fit app

A browser-based flow-curve fitting app built with [marimo](https://marimo.io).
All calculations run **in the browser** via WebAssembly — no server, no install.
The fitting itself is done by the `rheofit` library (installed from PyPI in the
browser), so every library improvement shows up in the app automatically.

**Use it:** upload a flow curve (TRIOS JSON or Excel), pick the measurement
step, pick a model, preview the curve with the sliders, then hit **Fit**.
A **Compare** tab fits all nine models and ranks them by RedChi2.

## Files

- `fit_app.py` — the whole app: one self-contained marimo notebook (PEP 723
  inline dependencies, no local imports so the WASM export stays simple).

## Run locally

```bash
marimo edit app/fit_app.py   # develop
marimo run app/fit_app.py    # app mode
```

## Deployment

`.github/workflows/deploy-app.yml` exports the notebook with
`marimo export html-wasm … --mode run` and deploys the static output to
GitHub Pages on every push to `master` that touches `app/`.

One-time setup (repo admin): Settings → Pages → Build and deployment →
Source: **GitHub Actions**. The app then lives at
`https://rheopy.github.io/rheofit/`.
