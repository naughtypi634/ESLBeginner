#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drop the `## N. Practice 练习` section from a Beginner handout and renumber.

The Beginner handouts no longer carry exercises, error correction or answer
keys: the last section of a lesson is `## N. Discussion 讨论`. This removes the
trailing Practice block (heading, every `###` sub-table under it, and the
answer grid) and then renumbers the surviving `## N.` headings 1..K so the
Discussion ends up as the final numbered section.

Knowledge tables are untouched — in particular the `常见错误 | 正确说法 | 说明`
tables that live inside teaching sections are content, not exercises.

Usage:
    python -I build/strip_practice.py            # every lesson
    python -I build/strip_practice.py 27 30      # filename substrings
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "MD" / "Beginner"

H2 = re.compile(r"^##\s+(\d+)\.\s*(.*)$")
PRACTICE = re.compile(r"^Practice\s*练习$")


def strip(path: Path) -> str:
    """Return "stripped", "clean" (no Practice section) or "no-discussion"."""
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")

    out: list[str] = []
    dropped = False
    for line in lines:
        m = H2.match(line)
        if m and PRACTICE.match(m.group(2).strip()):
            dropped = True
            break                      # everything from here down is Practice
        out.append(line)

    if not dropped:
        return "clean"

    # Trim the blank tail the Practice heading left behind.
    while out and not out[-1].strip():
        out.pop()

    # Renumber the surviving ## sections so Discussion is the last one.
    n, numbered = 0, []
    for line in out:
        m = H2.match(line)
        if m:
            n += 1
            numbered.append(f"## {n}. {m.group(2).strip()}")
        else:
            numbered.append(line)

    text = "\n".join(numbered)
    if not text.endswith("\n"):
        text += "\n"
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))
    return "stripped"


def main() -> None:
    filters = sys.argv[1:]
    files = sorted(SRC.glob("*.md"))
    if filters:
        files = [f for f in files if any(t in f.name for t in filters)]

    counts = {"stripped": 0, "clean": 0}
    for path in files:
        res = strip(path)
        counts[res] = counts.get(res, 0) + 1
        if res != "stripped":
            print(f"[{res:8}] {path.name}")

    print(f"\nstripped {counts['stripped']}, already clean {counts['clean']}")


if __name__ == "__main__":
    main()
