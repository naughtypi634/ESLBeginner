#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Report section/sub headings stranded at the foot of a page.

A heading whose table starts on the next page reads as a broken section. The
builder guards headings with \\needspace, but a heading can still land at the
bottom of a page when the table that follows is pushed over — so this checks
the rendered PDFs rather than the source.

A page is flagged when its LAST text line is one of the lesson's `## ` or
`### ` headings.

Usage:
    python -I build/check_orphan_headings.py
"""

import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "MD" / "Beginner"
PDF = ROOT / "PDF" / "Beginner"

H = re.compile(r"^#{2,3}\s+(.*)$")


def norm(s: str) -> str:
    """Drop the section number: the PDF renders it as part of the same line."""
    return re.sub(r"^\d+\.?\s*", "", s.strip())


def headings(md: Path) -> set[str]:
    out = set()
    for line in md.read_text(encoding="utf-8").splitlines():
        m = H.match(line.strip())
        if m:
            out.add(norm(m.group(1)))
    return out


def main() -> None:
    filters = sys.argv[1:]
    files = sorted(SRC.glob("*.md"))
    if filters:
        files = [f for f in files if any(t in f.name for t in filters)]

    bad = 0
    for md in files:
        pdf = PDF / f"{md.stem}.pdf"
        if not pdf.exists():
            print(f"[????] {md.name}: no PDF")
            continue
        heads = headings(md)
        doc = pymupdf.open(pdf)
        hits = []
        for page in doc:
            lines = [ln.strip() for ln in page.get_text().splitlines() if ln.strip()]
            lines = [ln for ln in lines if not ln.isdigit()]      # drop the page number
            if not lines:
                continue
            last = norm(lines[-1])
            if last in heads:
                hits.append(page.number + 1)
        if hits:
            bad += 1
            print(f"[ORPHAN] {md.name}  heading stranded at foot of page {hits}")
        else:
            print(f"[ok    ] {md.name}")

    print(f"\n{len(files) - bad}/{len(files)} clean")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
