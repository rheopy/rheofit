# Sphinx configuration for the rheofit documentation.
#
# Standard Read the Docs setup: Sphinx + MyST (Markdown) + autodoc.
# Build locally with:  sphinx-build -b html docs docs/_build/html
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "rheofit"
copyright = "2026, rheopy"
author = "rheopy"
release = "0.1.0"

extensions = [
    "myst_parser",
    "sphinxcontrib.mermaid",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["print.css"]

# MyST: allow $...$ / $$...$$ math and ::: colon fences.
myst_enable_extensions = [
    "dollarmath",
    "colon_fence",
]

# ```mermaid fences become {mermaid} directives (rendered by
# sphinxcontrib-mermaid on HTML builders). For the EPUB — whose readers do
# not run JavaScript — each diagram is wrapped in {only} blocks with a
# pre-rendered SVG fallback (docs/walkthrough/*.svg).
myst_fence_as_directive = ["mermaid"]

suppress_warnings = ["misc.highlighting_failure"]

# Don't document inherited / private members; keep API pages tight.
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "private-members": False,
    "show-inheritance": False,
}
