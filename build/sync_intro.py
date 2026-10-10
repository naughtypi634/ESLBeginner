#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strip course intros from lesson MDs; the intro text lives in 课程介绍总览.md.

Handouts must not carry a course intro (see AGENTS.md), so the index at the repo
root is the single place for that text and this script removes any
`## 课程介绍` block that reappears in a lesson MD.

Usage:
    python build/sync_intro.py            # check/strip every lesson
    python build/sync_intro.py 14         # only lessons whose filename contains "14"
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_DIR = ROOT / "MD"
INDEX = ROOT / "课程介绍总览.md"

SECTION = "## 各课课程介绍"
HEADER = "## 课程介绍"


def parse_index(text: str) -> dict[str, str]:
    """Parse title/intro pairs listed after the entries section heading."""
    entries: dict[str, str] = {}
    pending: list[str] = []
    in_section = False
    for line in text.splitlines():
        s = line.strip()
        if s == SECTION:
            in_section = True
            continue
        if not in_section or not s or s.startswith(">"):
            continue
        pending.append(s)
        if len(pending) == 2:
            entries[pending[0]] = pending[1]
            pending = []
    return entries


def strip_one(path: Path) -> str:
    """Delete the `## 课程介绍` block; returns "stripped" or "clean"."""
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i, found = 0, False
    while i < len(lines):
        if lines[i].strip() == HEADER:
            found = True
            i += 1
            while i < len(lines) and not lines[i].startswith("#"):
                i += 1
            while out and not out[-1].strip():
                out.pop()
            out.append("")
            continue
        out.append(lines[i])
        i += 1
    if not found:
        return "clean"
    while len(out) > 1 and not out[-2].strip() and not out[-1].strip():
        out.pop()
    text = "\n".join(out)
    if not text.endswith("\n"):
        text += "\n"
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))
    return "stripped"


def main() -> None:
    if not INDEX.exists():
        sys.exit(f"missing index: {INDEX}")
    entries = parse_index(INDEX.read_text(encoding="utf-8"))
    filters = sys.argv[1:]

    files = sorted(p for p in MD_DIR.rglob("*.md") if not p.name.startswith("_"))
    results: dict[str, list[str]] = {"stripped": [], "clean": []}
    titles: dict[str, str] = {}
    for p in files:
        first = next((ln for ln in p.read_text(encoding="utf-8").splitlines() if ln.startswith("# ")), "")
        titles.setdefault(first[2:].strip(), str(p.relative_to(MD_DIR)))

    for path in files:
        if filters and not any(f in path.name for f in filters):
            continue
        results[strip_one(path)].append(str(path.relative_to(MD_DIR)))

    index_only = [t for t in entries if t not in titles]
    if filters:
        index_only = [t for t in index_only if any(f in titles.get(t, t) for f in filters)]

    for key, names in results.items():
        if names:
            print(f"[{key}] {len(names)}: {', '.join(names)}")
    if index_only:
        print(f"[index-only] {len(index_only)}: {', '.join(index_only)}")


if __name__ == "__main__":
    main()
