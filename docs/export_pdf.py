#!/usr/bin/env python3
"""Build a PDF of the documentation via headless Chromium print-to-PDF.

Why Chromium instead of Sphinx's LaTeX builder: these pages are full of
Unicode (tau_0, shear-rate dots, emoji headings) and MathJax math. Chromium
renders exactly what a reader sees on the site -- typeset equations, emoji,
code blocks -- and the print stylesheet (``docs/_static/print.css``) hides
the live interactive iframes while keeping their static preview images.

Steps:
  1. ``sphinx-build -b html`` (no WASM export needed; iframes are print-hidden)
  2. serve the built HTML over local HTTP
  3. print each page to PDF with headless Chromium, giving MathJax time to
     typeset via ``--virtual-time-budget``
  4. merge the per-page PDFs with pypdf, adding bookmarks

Output: ``docs/_build/pdf/rheofit.pdf``

Requires: Chromium/Chrome (playwright's ``chromium`` build, ``chromium``,
``chromium-browser`` or ``google-chrome`` on PATH, or ``CHROMIUM_BIN`` env),
plus ``pypdf``.
"""
from __future__ import annotations

import functools
import http.server
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

DOCS = Path(__file__).resolve().parent
HTML_OUT = DOCS / "_build" / "html"
PDF_OUT = DOCS / "_build" / "pdf"
PAGES_DIR = PDF_OUT / "_pages"

# (bookmark title, html path relative to HTML_OUT)
PAGES = [
    ("rheofit documentation", "index.html"),
    ("Case study: Carbopol Ultrez 21", "walkthrough.html"),
    ("Constitutive models", "models/index.html"),
    ("Herschel-Bulkley", "models/herschel_bulkley.html"),
    ("Bingham", "models/bingham.html"),
    ("Three-Component (TC)", "models/tc.html"),
    ("Casson", "models/casson.html"),
    ("API reference", "api.html"),
]


def find_chromium() -> str:
    if os.environ.get("CHROMIUM_BIN"):
        return os.environ["CHROMIUM_BIN"]
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        path = shutil.which(name)
        if path:
            return path
    # playwright's bundled chromium
    candidates = sorted(Path.home().glob(".cache/ms-playwright/chromium-*/chrome-linux/chrome"))
    if candidates:
        return str(candidates[-1])
    raise SystemExit(
        "No Chromium found. Install one (e.g. `python -m playwright install chromium`)"
        " or set CHROMIUM_BIN."
    )


def main() -> None:
    chromium = find_chromium()
    print(f"chromium: {chromium}")

    # NOTE: no -W here. This HTML is a throwaway intermediate used only for
    # printing: the PDF job skips export_interactive.py, so the links to the
    # WebAssembly explorers (../_static/interactive/*/index.html) are
    # intentionally missing and would trip warnings-as-errors.
    subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "html",
         str(DOCS), str(HTML_OUT)],
        check=True,
    )

    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HTML_OUT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for title, rel in PAGES:
            out = PAGES_DIR / (Path(rel).stem + ".pdf")
            url = f"http://127.0.0.1:{port}/{rel}"
            print(f"printing {rel} ...")
            subprocess.run(
                [chromium, "--headless=new", "--no-sandbox",
                 "--disable-dev-shm-usage", "--disable-gpu",
                 "--no-pdf-header-footer",
                 "--virtual-time-budget=25000",
                 f"--print-to-pdf={out}", url],
                check=True, timeout=240,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
    finally:
        server.shutdown()

    from pypdf import PdfReader, PdfWriter

    writer = PdfWriter()
    for title, rel in PAGES:
        pdf = PAGES_DIR / (Path(rel).stem + ".pdf")
        reader = PdfReader(str(pdf))
        start = len(writer.pages)
        for page in reader.pages:
            writer.add_page(page)
        writer.add_outline_item(title, start)
    final = PDF_OUT / "rheofit.pdf"
    with open(final, "wb") as f:
        writer.write(f)
    print(f"pdf -> {final} ({final.stat().st_size / 1e6:.1f} MB, "
          f"{len(writer.pages)} pages)")


if __name__ == "__main__":
    main()
