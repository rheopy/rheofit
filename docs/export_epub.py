#!/usr/bin/env python3
"""Build the EPUB version of the documentation.

The interactive marimo explorers (``docs/_static/interactive/``, ~110 MB of
WebAssembly) must not be bundled into the ebook, and Sphinx's
``epub_exclude_files`` only matches exact file names, so this wrapper
temporarily moves the directory aside (on persistent disk, not /tmp),
builds the EPUB, and moves it back.

The explorer iframes are wrapped in ``{only} builder_html`` in the model
pages, so the EPUB keeps the explanatory text plus the static preview PNGs
instead of dead iframes.

Output: ``docs/_build/epub/rheofit.epub``
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent
WASM_DIR = DOCS / "_static" / "interactive"
ASIDE_DIR = DOCS / "_build" / "wasm_aside"
EPUB_OUT = DOCS / "_build" / "epub"
EPUB_CONF = DOCS / "epub_conf"


def main() -> None:
    if not shutil.which("latex") or not shutil.which("dvipng"):
        raise SystemExit(
            "export_epub.py needs LaTeX + dvipng for math rendering "
            "(e.g. `apt-get install texlive-latex-recommended dvipng`)."
        )
    moved = False
    if WASM_DIR.exists():
        ASIDE_DIR.parent.mkdir(parents=True, exist_ok=True)
        if ASIDE_DIR.exists():
            shutil.rmtree(ASIDE_DIR)
        shutil.move(str(WASM_DIR), str(ASIDE_DIR))
        moved = True
    try:
        subprocess.run(
            [sys.executable, "-m", "sphinx", "-b", "epub",
             "-c", str(EPUB_CONF), str(DOCS), str(EPUB_OUT)],
            check=True,
        )
    finally:
        if moved:
            if WASM_DIR.exists():
                shutil.rmtree(WASM_DIR)
            shutil.move(str(ASIDE_DIR), str(WASM_DIR))
    epub = EPUB_OUT / "rheofit.epub"
    print(f"epub -> {epub} ({epub.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
