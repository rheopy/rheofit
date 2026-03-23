# rheofit
[![Documentation Status](https://readthedocs.org/projects/rheofit/badge/?version=latest)](https://rheofit.readthedocs.io/en/latest/?badge=latest)

Library for fitting rheology data flow curves.

Documentation at https://rheofit.readthedocs.io

## Install

### With uv (recommended)

```bash
uv pip install git+https://github.com/rheopy/rheofit.git
```

### With pip

```bash
pip install git+https://github.com/rheopy/rheofit.git
```

### Uninstall

```bash
uv pip uninstall rheofit
# or
pip uninstall rheofit
```

## Development

Clone the repository and install in editable mode with dev dependencies:

```bash
git clone https://github.com/rheopy/rheofit.git
cd rheofit
uv venv
uv pip install -e ".[dev]"
```

To also build the docs:

```bash
uv pip install -e ".[docs]"
```