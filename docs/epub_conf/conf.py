# Sphinx configuration for the EPUB build of the rheofit documentation.
#
# Same as docs/conf.py, except math is rendered to PNG images with
# sphinx.ext.imgmath (via LaTeX + dvipng) instead of client-side MathJax:
# ebook readers do not run JavaScript, so MathJax equations would show up
# as raw LaTeX source. Image math works in every reader.
#
# Used as:  sphinx-build -b epub -c docs/epub_conf docs docs/_build/epub
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

exec(open(os.path.join(os.path.dirname(__file__), "..", "conf.py")).read())  # noqa: S102

extensions = [e for e in extensions if e != "sphinx.ext.mathjax"]  # noqa: F821
extensions.append("sphinx.ext.imgmath")  # noqa: F821

# Crisp math on high-DPI readers.
imgmath_image_format = "png"
imgmath_dvipng_args = ["-gamma", "1.5", "-D", "220", "-bg", "Transparent"]
