#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync course intros from 课程介绍总览.md (repo root) into each lesson MD.

The index stores every course as two plain lines:

    <course title>          # must match the lesson MD's H1
    <intro sentence>

Usage:
    python build/sync_intro.py            # sync every lesson in the index
    python build/sync_intro.py 14         # sync lessons whose filename contains "14"
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


def sync_one(path: Path, intro: str) -> str:
    original = path.read_text(encoding="utf-8")
    lines = original.split("\n")
    intro_idx = next((i for i, ln in enumerate(lines) if ln.strip() == HEADER), None)
    block = [HEADER, "", intro]

    if intro_idx is None:
        # Insert right after the H1 title (and any blank lines that follow it).
        title_idx = next((i for i, ln in enumerate(lines) if ln.startswith("# ")), 0)
        insert_at = title_idx + 1
        while insert_at < len(lines) and not lines[insert_at].strip():
            insert_at += 1
        lines[insert_at:insert_at] = block + [""]
    else:
        # Replace the existing intro block (header + blank + paragraph).
        end = intro_idx + 1
        while end < len(lines) and not lines[end].strip():
            end += 1
        while end < len(lines) and lines[end].strip() and not lines[end].startswith("#"):
            end += 1
        lines[intro_idx:end] = block

    out = "\n".join(lines)
    if not out.endswith("\n"):
        out += "\n"
    if out == original or out + "\n" == original:
        return "unchanged"
    path.write_text(out, encoding="utf-8", newline="")
    return "updated" if intro_idx is not None else "added"


def main() -> None:
    if not INDEX.exists():
        sys.exit(f"missing index: {INDEX}")
    entries = parse_index(INDEX.read_text(encoding="utf-8"))
    filters = sys.argv[1:]

    files = sorted(p for p in MD_DIR.glob("*.md") if not p.name.startswith("_"))
    titles: dict[str, Path] = {}
    for p in files:
        first = next((ln for ln in p.read_text(encoding="utf-8").splitlines() if ln.startswith("# ")), "")
        titles[first[2:].strip()] = p
    title_to_name = {t: p.name for t, p in titles.items()}

    results: dict[str, list[str]] = {"added": [], "updated": [], "unchanged": [], "no-intro-in-index": []}
    for title, path in titles.items():
        if filters and not any(f in path.name for f in filters):
            continue
        intro = entries.get(title)
        if intro is None:
            results["no-intro-in-index"].append(path.name)
            continue
        results[sync_one(path, intro)].append(path.name)

    index_only = [t for t in entries if t not in titles]
    if filters:
        index_only = [t for t in index_only if any(f in title_to_name.get(t, t) for f in filters)]

    for key, names in results.items():
        if names:
            print(f"[{key}] {len(names)}: {', '.join(names)}")
    if index_only:
        print(f"[index-only] {len(index_only)}: {', '.join(index_only)}")


if __name__ == "__main__":
    main()
