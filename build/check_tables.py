"""Validate markdown tables: each table block must keep a consistent column count.

Usage: python -I check_tables.py file1.md ...
"""
import re
import sys
from pathlib import Path

for raw in sys.argv[1:]:
    path = Path(raw)
    lines = path.read_text(encoding="utf-8").splitlines()
    block: list[tuple[int, str]] = []
    problems = []
    maxcols = 0

    def flush() -> None:
        global block, maxcols
        if not block:
            return
        counts = {len(re.split(r"(?<!\\)\|", ln.strip().strip("|"))) for _, ln in block}
        if len(counts) > 1:
            problems.append(
                f"  L{block[0][0]}-{block[-1][0]}: mixed column counts {sorted(counts)}"
            )
        # separator row must exist as row 2
        if len(block) < 2 or not re.fullmatch(r"[\s|:-]+", block[1][1].strip()):
            problems.append(f"  L{block[0][0]}: missing |---|---| separator row")
        maxcols = max(maxcols, max(counts))
        block = []

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("|"):
            block.append((i, line))
        else:
            flush()
            continue
    flush()

    status = "OK " if not problems else "BAD"
    print(f"[{status}] {path.name}  (max {maxcols} cols)")
    for p in problems:
        print(p)
