# 🔧 API reference

The full public API. Everything below is also reachable from an AI agent through the
bundled `flow-curve-analysis` skill, which calls these same functions.

## Top-level package

```{eval-rst}
.. automodule:: rheofit
   :members: analyze, fit, print_steps, discover_steps, load_step, load_steps,
             list_models, model_info, get_model, plot, list_plots, plot_info,
             install_skill
```

## Models

Nine registered models, from Newtonian to triple-mode. `list_models()` prints the
names; `model_info(name)` describes parameters, units, and nesting.

```{eval-rst}
.. automodule:: rheofit.models
   :members:
```

## Analysis

```{eval-rst}
.. automodule:: rheofit.analysis
   :members: Analysis, analyze, fit, list_models, model_info, get_model, print_steps
```

## Data loading

Reads TA Instruments TRIOS JSON directly (no tadatakit).

```{eval-rst}
.. automodule:: rheofit.io
   :members: discover_steps, load_step, load_steps, detect_test_type, demo_source
```

## Visualization

```{eval-rst}
.. automodule:: rheofit.visualization
   :members: plot, list_plots, plot_info, get_plot
```

## Reports

```{eval-rst}
.. automodule:: rheofit.report
   :members:
```

## Command line

```{eval-rst}
.. automodule:: rheofit.cli
   :members: main, install_skill
```
