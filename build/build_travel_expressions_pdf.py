#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build an Apple-style A4 PDF from MD/Essential Expressions for travel.md
=======================================================================
Design language (Apple):
  - white canvas, #1d1d1f ink, #424245 secondary text
  - SF Pro Display headings with negative tracking, SF Pro Text body
  - hairline separators (#d2d2d7 / #ececf0), generous whitespace
  - minimal chrome: title rule + quiet page number only

Pipeline: markdown -> HTML (pandoc) -> print CSS -> PDF (Playwright/Chromium)
Output:   PDF/Essential Expressions for travel.pdf

Usage (run with the project venv):
    .venv/bin/python build/build_travel_expressions_pdf.py
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_SRC = ROOT / "MD" / "Essential Expressions for travel.md"
PDF_OUT = ROOT / "PDF" / "Essential Expressions for travel.pdf"


CSS = """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #ffffff; }
body {
  font-family: "SF Pro Text", -apple-system, "Helvetica Neue",
               "PingFang SC", "Microsoft YaHei", sans-serif;
  color: #1d1d1f;
  font-size: 9.8pt;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

.doc-title {
  font-family: "SF Pro Display", -apple-system, "Helvetica Neue", sans-serif;
  font-size: 20pt;
  font-weight: 600;
  letter-spacing: -0.4px;
  line-height: 1.2;
  color: #1d1d1f;
  margin: 0 0 4pt;
}
.title-rule {
  height: 1pt;
  background: #d2d2d7;
  margin: 0 0 14pt;
}

.topic { break-inside: avoid; }

h2 {
  font-family: "SF Pro Display", -apple-system, "Helvetica Neue", sans-serif;
  font-size: 12pt;
  font-weight: 600;
  letter-spacing: -0.2px;
  color: #1d1d1f;
  margin: 15pt 0 5pt;
  break-after: avoid;
}
.topic:first-of-type h2 { margin-top: 0; }

table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 2pt;
}
thead th {
  text-align: left;
  font-size: 7pt;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.9px;
  color: #86868b;
  padding: 0 0 3pt;
  border-bottom: 1pt solid #d2d2d7;
}
td {
  padding: 5pt 10pt 5pt 0;
  vertical-align: top;
  border-bottom: 1pt solid #ececf0;
}
tr:last-child td { border-bottom: none; }
td:first-child {
  width: 43%;
  font-weight: 600;
  color: #1d1d1f;
}
td:last-child { color: #424245; }
"""


def pandoc_html(src: Path) -> str:
    """Convert the travel markdown to HTML with pandoc."""
    proc = subprocess.run(
        ["pandoc", str(src), "-f", "markdown", "-t", "html", "--no-highlight"],
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


def decorate(html: str) -> str:
    """Turn pandoc output into Apple-style document structure."""
    # The document's first plain paragraph is its title.
    html = re.sub(
        r"<p>(Essential Expressions for travel)</p>",
        r'<div class="doc-title">\1</div><div class="title-rule"></div>',
        html,
        count=1,
    )
    # Section titles: bold-only paragraphs -> <h2>.
    html = re.sub(
        r"<p><strong>(.*?)</strong></p>",
        r"<h2>\1</h2>",
        html,
        flags=re.S,
    )
    # Group each heading with its table so a section never splits across pages.
    html = re.sub(
        r"(<h2>.*?</h2>\s*<table[^>]*>.*?</table>)",
        r'<section class="topic">\1</section>',
        html,
        flags=re.S,
    )
    return html


def render_pdf(body_html: str) -> None:
    """Render the styled HTML to A4 PDF via Playwright headless Chromium."""
    from playwright.sync_api import sync_playwright

    page_html = (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<style>" + CSS + "</style></head><body>" + body_html + "</body></html>"
    )
    footer = (
        "<div style=\"width:100%;text-align:right;"
        "font-family:'SF Pro Text','Helvetica Neue',sans-serif;"
        "font-size:8px;color:#86868b;\">"
        "<span class=\"pageNumber\"></span></div>"
    )
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(page_html, wait_until="load")
        page.pdf(
            path=str(PDF_OUT),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=footer,
            margin={"top": "15mm", "right": "15mm", "bottom": "16mm", "left": "15mm"},
        )
        browser.close()


def main() -> None:
    if not MD_SRC.is_file():
        raise SystemExit(f"source not found: {MD_SRC}")
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    body = decorate(pandoc_html(MD_SRC))
    render_pdf(body)
    print(f"OK -> {PDF_OUT}")


if __name__ == "__main__":
    main()
