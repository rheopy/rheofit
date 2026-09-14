"""
Flow-curve fitting — thin wrapper around the `rheofit` library.

The skill and the library share one implementation: everything below simply
forwards to `rheofit.cli`. These two commands are equivalent:

    python .github/skills/flow-curve-analysis/scripts/flow_curve_fit.py <args>
    python -m rheofit <args>

If `rheofit` is not installed, this script falls back to the repository root that
ships this skill.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "numpy",
#   "scipy",
#   "matplotlib",
#   "pandas",
#   "python-pptx",
# ]
# ///

import sys
from pathlib import Path

try:
    from rheofit.cli import main
except ModuleNotFoundError:
    # repo layout: <repo>/.github/skills/<skill>/scripts/this_file.py  ->  <repo>
    repo_root = Path(__file__).resolve().parents[4]
    if not (repo_root / "rheofit").is_dir():
        raise
    sys.path.insert(0, str(repo_root))
    from rheofit.cli import main

if __name__ == "__main__":
    sys.exit(main())
