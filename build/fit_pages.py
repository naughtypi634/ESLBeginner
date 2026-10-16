#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trim a Beginner lesson until it renders on exactly two A4 pages.

The series has no page-break primitive, so a lesson that runs slightly long
spills onto a third page whenever the last table cannot fit at the foot of
page 2. The fix is always "delete rows", never "add a page break".

Rows are removed in this order, cheapest content first:
  1. Discussion questions, down to a floor of 5;
  2. rows from the tail of the last teaching table before the Discussion,
     down to a floor of 3, skipping `常见错误 | 正确说法 | 说明` tables
     (those are explanations, the last thing to sacrifice).

Usage:
    python -I build/fit_pages.py            # every lesson that renders long
    python -I build/fit_pages.py 20 28      # filename substrings
    python -I build/fit_pages.py --series business
"""

import re
import subprocess
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from series import pick_series  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "Scripts" / "python.exe"

CFG = None
SRC = None
PDF = None

SEP = re.compile(r"^:?-{2,}:?$")
H2 = re.compile(r"^##\s+\d+\.\s*(.*)$")
KEEP_TABLE = "常见错误"
DISCUSSION_FLOOR = 5
TABLE_FLOOR = 3


def tables(lines: list[str]) -> list[tuple[int, int, list[str]]]:
    """(start, end_exclusive, header) for every pipe table."""
    out, i, n = [], 0, len(lines)
    while i < n:
        if lines[i].strip().startswith("|"):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            j = i
            while j < n and lines[j].strip().startswith("|"):
                j += 1
            out.append((i, j, header))
            i = j
            continue
        i += 1
    return out


def data_rows(start: int, end: int, lines: list[str]) -> list[int]:
    """Line indexes of body rows (header and separator excluded)."""
    rows, hdr = [], True
    for k in range(start, end):
        cells = [c.strip() for c in lines[k].strip().strip("|").split("|")]
        if hdr:
            hdr = False
            continue
        if all(SEP.fullmatch(c) for c in cells):
            continue
        rows.append(k)
    return rows


def drop(lines: list[str]) -> bool:
    """Delete one low-value row. Return False when nothing is left to drop."""
    ts = tables(lines)
    if not ts:
        return False
    # The Discussion table is the last one in the file.
    last_start, last_end, last_hdr = ts[-1]
    is_discussion = any(
        (m := H2.match(lines[k])) and "Discussion" in m.group(1)
        for k in range(max(0, last_start - 3), last_start)
    )
    if is_discussion:
        rows = data_rows(last_start, last_end, lines)
        if len(rows) > DISCUSSION_FLOOR:
            del lines[rows[-1]]
            return True
    # Otherwise walk the teaching tables backwards for a droppable tail row.
    for start, end, header in reversed(ts[:-1]):
        if KEEP_TABLE in " ".join(header):
            continue
        rows = data_rows(start, end, lines)
        if len(rows) > TABLE_FLOOR:
            del lines[rows[-1]]
            return True
    return False


def pages(stem: str) -> int:
    builder = CFG["builder"].relative_to(ROOT).as_posix()
    subprocess.run([str(PY), builder, stem],
                   cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    pdf = PDF / f"{stem}.pdf"
    if not pdf.exists():
        return 99
    return len(pymupdf.open(pdf))


def main() -> None:
    global CFG, SRC, PDF
    CFG, filters = pick_series(sys.argv[1:])
    SRC, PDF = CFG["src"], CFG["pdf"]
    files = sorted(SRC.glob("*.md"))
    if filters:
        files = [f for f in files if any(t in f.name for t in filters)]

    for md in files:
        n = pages(md.stem)
        if n <= 2:
            print(f"[ok   ] {md.name}  ({n} page{'s' if n != 2 else ''})")
            continue
        raw = md.read_bytes()
        newline = "\r\n" if b"\r\n" in raw else "\n"
        lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")
        cuts = 0
        while n > 2:
            if not drop(lines):
                print(f"[STUCK] {md.name} still {n} pages, nothing left to trim safely")
                break
            md.write_bytes("\n".join(lines).replace("\n", newline).encode("utf-8"))
            cuts += 1
            n = pages(md.stem)
        else:
            print(f"[FIXED] {md.name}  {n} pages after cutting {cuts} row(s)")
            continue


if __name__ == "__main__":
    main()
