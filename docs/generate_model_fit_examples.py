#!/usr/bin/env python3
"""Generate the worked synthetic-data examples for docs/models/<model>.md.

For each of the nine rheofit models this script:
  1. builds a synthetic flow curve from rheomodel with known parameters
     (+ small relative noise, fixed seed),
  2. fits it with rheofit,
  3. saves docs/models/<model>_fit_example.png (data + fit + truth),
  4. rewrites docs/models/<model>.md as: rheomodel pointer, constitutive
     equation, the worked example (code + its ACTUAL output below),
     and the interactive explorer section (kept verbatim).

Run from the repo root:  python docs/generate_model_fit_examples.py
Requires: rheomodel (pip), and this repo importable (run from repo root).
"""
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from rheomodel import get_model
import rheofit

# model -> (true params, (log10 gmin, log10 gmax), noise, effort, note)
CASES = {
    "bingham": (
        {"sigma_y": 20.0, "K": 5.0}, (-2, 2), 0.02, "fast", None),
    "herschel_bulkley": (
        {"sigma_y": 15.0, "K": 8.0, "n": 0.5}, (-2, 2), 0.02, "fast", None),
    "power_law": (
        {"K": 10.0, "n": 0.4}, (-2, 2), 0.02, "fast", None),
    "casson": (
        {"sigma_y": 12.0, "K": 3.0}, (-2, 2), 0.02, "fast", None),
    "carreau": (
        {"eta_0": 50.0, "lambda_val": 2.0, "n": 0.4}, (-3, 3), 0.02, "fast",
        None),
    "carreau_carreau": (
        {"eta_0_1": 12.0, "lambda_val_1": 0.2,
         "eta_0_2": 25.0, "lambda_val_2": 4.0},
        (-3, 3), 0.02, "fast", None),
    "tc": (
        {"sigma_y": 10.0, "gamma_dot_c": 1.0, "eta_bg": 2.0},
        (-2, 3), 0.02, "fast", None),
    "tc_carreau": (
        {"sigma_y": 10.0, "gamma_dot_c": 1.0,
         "eta_0": 30.0, "lambda_val": 1.5},
        (-2, 3), 0.02, "fast", None),
    # six parameters need cleaner data to stay identifiable
    "tccc": (
        {"sigma_y": 8.0, "gamma_dot_c": 0.05, "eta_0_1": 15.0,
         "lambda_val_1": 0.5, "eta_0_2": 20.0, "lambda_val_2": 5.0},
        (-2, 3), 0.005, "fast",
        "Six parameters need cleaner data — 0.5% noise here instead of 2%."),
}

DISPLAY = {
    "bingham": "Bingham plastic",
    "herschel_bulkley": "Herschel\u2013Bulkley",
    "power_law": "power law",
    "casson": "Casson",
    "carreau": "Carreau",
    "carreau_carreau": "Carreau\u2013Carreau",
    "tc": "TC (three-component)",
    "tc_carreau": "TC\u2013Carreau",
    "tccc": "TCCC",
}

EQUATIONS = {
    "bingham": r"\tau = \tau_0 + \mu_p\dot{\gamma}",
    "herschel_bulkley": r"\tau = \tau_0 + K\dot{\gamma}^n",
    "power_law": r"\sigma = K\dot{\gamma}^n",
    "casson": r"\sigma = (\sqrt{\sigma_y} + \sqrt{K\dot{\gamma}})^2",
    "carreau": r"\sigma = \eta_0\dot{\gamma}[1+(\lambda\dot{\gamma})^2]^{(n-1)/2}",
    "carreau_carreau":
        r"\sigma = \sum_{i=1,2} \eta_{0,i}\dot{\gamma}"
        r"[1+(\lambda_i\dot{\gamma})^2]^{-1/4,-1/2}",
    "tc": r"\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2}"
           r" + \eta_{bg}\dot{\gamma}",
    "tc_carreau": r"\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2}"
                  r" + \eta_0\dot{\gamma}[1+(\lambda\dot{\gamma})^2]^{-1/2}",
    "tccc": r"\sigma = \sigma_y + \sigma_y(\dot{\gamma}/\dot{\gamma}_c)^{1/2}"
            r" + \sum_i \eta_{0,i}\dot{\gamma}[1+(\lambda_i\dot{\gamma})^2]^{-1/4,-1/2}",
}

RHEOMODEL_URL = "https://rheomodel.readthedocs.io/en/latest/models/{}.html"

EXAMPLE_TEMPLATE = '''```python
import numpy as np
import pandas as pd
from rheomodel import get_model
import rheofit

# 1. synthetic flow curve from rheomodel: known truth + {noise_pct} noise
model = get_model("{key}")
gamma_dot = np.logspace({lo}, {hi}, {npts})
true = {true_repr}
rng = np.random.default_rng(0)
stress = model.equation(gamma_dot, **true)
stress = stress * (1 + {noise} * rng.standard_normal(gamma_dot.size))

# 2. fit it with rheofit
df = pd.DataFrame({{"Shear rate / 1/s": gamma_dot, "Stress / Pa": stress}})
res = rheofit.fit(df, "{key}", effort="{effort}", seed=0)

for name, p in res["params"].items():
    print(f"{{name:12s}} true={{true[name]:8.3g}}  fit={{p['value']:8.3g}} ± {{p['stderr']:.2g}}")
print(f"RedChi2 = {{res['redchi']:.2e}}")
```

Output:

```
{output}
```

![{display} — fit to synthetic data]({key}_fit_example.png)
'''


def explorer_block(path):
    """Extract the interactive-explorer ## section verbatim."""
    lines = open(path).read().splitlines()
    idx = [i for i, line in enumerate(lines) if line.startswith("## ")]
    start = next(i for i in idx if "Interactive explorer" in lines[i])
    si = idx.index(start)
    end = idx[si + 1] if si + 1 < len(idx) else len(lines)
    block = lines[start:end]
    while block and not block[-1].strip():
        block.pop()
    return block


def main():
    for key, (true, (lo, hi), noise, effort, note) in CASES.items():
        model = get_model(key)
        noise_pct = (f"{noise:.1%}".rstrip("0").rstrip(".")
                     if noise < 0.01 else f"{noise:.0%}")
        gd = np.logspace(lo, hi, 25)
        rng = np.random.default_rng(0)
        clean = model.equation(gd, **true)
        stress = clean * (1 + noise * rng.standard_normal(gd.size))
        df = pd.DataFrame(
            {"Shear rate / 1/s": gd, "Stress / Pa": stress})
        res = rheofit.fit(df, key, effort=effort, seed=0)

        # figure: data + rheofit fit + true curve
        gf = np.logspace(lo, hi, 200)
        fig, ax = plt.subplots(figsize=(6, 4.2))
        ax.loglog(gd, stress, "o", ms=4, label="synthetic data")
        ax.loglog(res["x"], res["y_fit"], "-", lw=2, label="rheofit fit")
        ax.loglog(gf, model.equation(gf, **true), "--", lw=1,
                  alpha=0.6, label="true model")
        ax.set_xlabel("Shear rate / 1/s")
        ax.set_ylabel("Stress / Pa")
        ax.set_title(f"{DISPLAY[key]} — fit to synthetic data")
        ax.legend(frameon=False, fontsize=9)
        fig.tight_layout()
        fig_path = f"docs/models/{key}_fit_example.png"
        fig.savefig(fig_path, dpi=110)
        plt.close(fig)

        # literal output block (exactly what the code above prints)
        out_lines = []
        for name, p in res["params"].items():
            out_lines.append(
                f"{name:12s} true={true[name]:8.3g}  "
                f"fit={p['value']:8.3g} \u00b1 {p['stderr']:.2g}")
        out_lines.append(f"RedChi2 = {res['redchi']:.2e}")
        output = "\n".join(out_lines)

        # sanity: every parameter within 20% of truth
        bad = [name for name, p in res["params"].items()
               if abs(p["value"] - true[name]) / true[name] > 0.20]
        status = "OK " if not bad else f"CHECK {bad}"
        print(f"{status} {key:16s} redchi={res['redchi']:.2e} -> {fig_path}")

        # assemble the page
        page_path = f"docs/models/{key}.md"
        explorer = explorer_block(page_path)
        url = RHEOMODEL_URL.format(key)
        parts = [
            "[← All models](index)",
            "",
            f"# Fitting the {DISPLAY[key]} model",
            "",
            f"> \U0001f9ec **The model itself lives in "
            f"[rheomodel]({url}).** Equations, parameters, history, "
            f"applicability, and references are documented there. In code, "
            f"`rheofit.models.{key}` is a thin adapter over `rheomodel` "
            f"\u2014 same physics, same parameters. This page is about "
            f"*fitting* it to data.",
            "",
            "The constitutive equation, for reference:",
            "",
            "$$",
            EQUATIONS[key],
            "$$",
            "",
            "## Worked example",
            "",
            (f"{note} " if note else "")
            + "Generate a flow curve from `rheomodel` with known parameters, "
            f"add {noise_pct} noise, and fit it with `rheofit`:",
            "",
            EXAMPLE_TEMPLATE.format(
                key=key, display=DISPLAY[key], lo=lo, hi=hi, npts=25,
                true_repr="{" + ", ".join(
                    f'"{k}": {v}' for k, v in true.items()) + "}",
                noise=noise, noise_pct=noise_pct,
                effort=effort, output=output),
        ]
        parts.extend(explorer)
        parts.append("")
        text = "\n".join(parts)
        lines = text.splitlines()
        while lines and (not lines[-1].strip()
                         or lines[-1].strip() == "---"):
            lines.pop()
        open(page_path, "w").write("\n".join(lines) + "\n")

    print("done — pages and figures regenerated from live fits")


if __name__ == "__main__":
    main()
