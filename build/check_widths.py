#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Report how much room each table has, before paying for a pandoc run.

build_beginner_pdfs.T_table sizes every table to its own longest cell and steps
the type down until the cells fit on one line. When even 8pt is not enough it
appends to a `too_wide` list that only prints after a full build — and in the
Windows console the Chinese headers of that report come out as mojibake, so the
offending cell is the only readable part. This mirrors the same arithmetic
without invoking pandoc, so a lesson can be checked while it is being written.

Verdicts, matching T_table's branches:
    OK    9pt with >=5% slack — the readable default
    8pt   8pt with >=5% slack — fits, but small
    BAD   no size fits: that cell will wrap

Also reports each file's table-row count, because the series is tuned to land
on exactly two A4 pages and the existing lessons sit between 55 and 74 rows.

Usage:
    python -I build/check_widths.py MD/BeginnerBusiness/01-*.md
    python -I build/check_widths.py --series business
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from series import pick_series  # noqa: E402
import build_beginner_pdfs as B  # noqa: E402

SEP = re.compile(r"^:?-{2,}:?$")

# T_table's thresholds: it takes a size only when it leaves SLACK (5%) of room.
OK_AT = 9.0 / B.SLACK
FITS_AT = 8.0 / B.SLACK


def tables(lines: list[str]):
    """Yield (section heading, header cells, body rows) for every pipe table."""
    section = ""
    i, n = 0, len(lines)
    while i < n:
        s = lines[i].strip()
        if s.startswith("## "):
            section = s[3:].strip()
        if not s.startswith("|"):
            i += 1
            continue
        rows = []
        while i < n and lines[i].strip().startswith("|"):
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if not all(SEP.fullmatch(c) for c in cells):
                rows.append(cells)
            i += 1
        yield section, rows[0], rows[1:]


def report(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    print(f"\n=== {path.name}")
    bad = 0
    nrows = 0
    for section, header, body in tables(lines):
        ncols = len(header)
        widths = [max([B.visual_len(header[c])] + [B.visual_len(r[c]) for r in body])
                  for c in range(ncols)]
        total = sum(widths)
        gap = (3.0 if ncols >= 5 else 5.0) * (ncols - 1) + 2.0
        s_max = B.SLACK * (B.TEXTWIDTH_PT - gap) / (B.EM_PER_UNIT * total) if total else 99.0
        nrows += len(body) + 2
        verdict = "OK " if s_max >= OK_AT else ("8pt" if s_max >= FITS_AT else "BAD")
        if verdict == "BAD":
            bad += 1
        print(f"  [{verdict}] {s_max:5.1f}pt  units={total:5.1f}  {section}")
        if verdict == "BAD":
            for c in range(ncols):
                worst = max([header[c]] + [r[c] for r in body], key=B.visual_len)
                print(f"        col{c} w={widths[c]:5.1f}  {worst}")
    print(f"  rows={nrows} (series target 55-74)")
    return bad


def main() -> int:
    cfg, filters = pick_series(sys.argv[1:])
    files = sorted(cfg["src"].glob("*.md"))
    if filters:
        files = [f for f in files if any(t in f.name for t in filters)]
    bad = sum(report(f) for f in files)
    print(f"\n{len(files)} file(s), {bad} table(s) too wide")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
