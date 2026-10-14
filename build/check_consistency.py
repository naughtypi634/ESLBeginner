#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Structural checks for the Beginner series (MD/Beginner/*.md).

The builder (build_beginner_pdfs.py) is line-oriented and silent: it drops any
line that does not start with "# ", "## ", "### " or "|", and a table row whose
cell count differs from its header crashes the whole run with IndexError.
Nothing in the toolchain checks section numbering or the section contract, so
this script does.

The series carries NO exercises: a lesson is teaching tables plus a closing
`## N. Discussion 讨论`. Exercise-shaped tables (fill-in, error correction,
sentence building, answer keys) are reported as errors, because their presence
means practice content crept back in.

Usage:
    python -I build/check_consistency.py                 # every lesson
    python -I build/check_consistency.py 13 14           # filename substrings
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "MD" / "Beginner"

SEP = re.compile(r"^:?-{2,}:?$")
CJK = re.compile(r"[㐀-䶿一-鿿]")
DISCUSSION = "Discussion 讨论"

# Exercise shapes that must never appear in a handout.
EXERCISE = {
    ("序号", "句子"), ("序号", "答案"), ("序号", "答案", "序号", "答案"),
    ("提示", "例句", "中文对照"), ("序号", "原形", "过去式"),
    ("序号", "原形", "过去式", "序号", "原形", "过去式"),
    ("序号", "动词", "-ing 形式"), ("序号", "陈述句", "tag"),
    ("序号", "一般疑问句", "反义疑问句"), ("序号", "问句", "事实", "回答"),
    ("序号", "直接说法", "更客气的说法"), ("序号", "原句", "改写"),
}

# Headers the series is allowed to use. An unlisted one is a warning, not an
# error: the point is to notice drift, not to freeze the vocabulary of tables.
KNOWN = {
    ("结构", "例句", "中文对照"), ("句型", "例句", "中文对照"),
    ("English", "中文", "English", "中文"), ("例句", "中文对照"),
    ("Question", "中文对照"), ("说法", "例句", "中文对照"),
    ("说法", "中文对照"), ("规则", "例句"), ("规则", "变化", "例句"),
    ("规则", "动词 → 第三人称", "例句"), ("规则", "动词 → -ing", "例子"),
    ("规则", "动词 → 过去式", "例子"),
    ("常见错误", "正确说法", "说明"), ("正确说法", "常见错误"),
    ("主格", "形容词性物主", "宾格", "名词性物主"),
    ("提问", "回答", "中文对照"), ("提问", "回答"),
    ("连接词", "作用", "例句", "中文对照"), ("频率", "例句", "中文对照"),
    ("用法", "例句", "中文对照"), ("时态", "用法", "例句"),
    ("位置", "规则", "例句"), ("意思", "例句", "中文对照"),
    ("区别", "说明", "例子"), ("想表达", "用哪个", "例句"),
    ("陈述句类型", "陈述句", "tag", "中文对照"),
    ("问句", "事实", "回答", "中文对照"), ("A", "B"),
    ("中文", "English", "例子"), ("中文", "English", "例句"), ("中文", "English"),
    ("写法", "读法", "例句"), ("搭配", "例句", "中文对照"),
    ("序数词", "中文", "序数词", "中文"), ("时间", "例句", "中文对照"),
    ("原形", "过去式", "中文", "原形", "过去式", "中文"),
    ("场合", "用哪个", "例句"), ("中文", "English", "中文", "English"),
}


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def check(path: Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    err: list[str] = []
    warn: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    h1 = [ln for ln in lines if ln.startswith("# ")]
    if len(h1) != 1:
        err.append(f"H1 count = {len(h1)}, want exactly 1")
    elif not CJK.search(h1[0]):
        err.append("H1 has no Chinese gloss")

    headings = [ln[3:].strip() for ln in lines if ln.startswith("## ")]
    nums, titles = [], []
    for s in headings:
        m = re.match(r"^(\d+)\.\s*(.*)$", s)
        if not m:
            err.append(f"section without a number: {s!r}")
        else:
            nums.append(int(m.group(1)))
            titles.append(m.group(2))
    if nums and nums != list(range(1, len(nums) + 1)):
        err.append(f"section numbers not contiguous 1..{len(nums)}: {nums}")
    if not titles or titles[-1] != DISCUSSION:
        err.append(f"last section is {titles[-1:]}, want {[DISCUSSION]} (no exercises)")

    i, n = 0, len(lines)
    while i < n:
        if lines[i].strip().startswith("|"):
            header = cells(lines[i])
            j = i + 1
            if j < n and lines[j].strip().startswith("|") and all(SEP.fullmatch(c) for c in cells(lines[j])):
                j += 1
            else:
                err.append(f"line {i + 1}: table has no |---| separator row")
            body = []
            while j < n and lines[j].strip().startswith("|"):
                body.append(cells(lines[j]))
                j += 1
            for k, r in enumerate(body):
                if len(r) != len(header):
                    err.append(f"line {i + 2 + k}: row has {len(r)} cells, header has {len(header)}")
                if any("|" in c for c in r):
                    err.append(f"line {i + 2 + k}: stray pipe inside a cell")
            key = tuple(header)
            if key in EXERCISE:
                err.append(f"line {i + 1}: exercise table {header} — handouts carry no practice")
            elif key not in KNOWN:
                warn.append(f"line {i + 1}: header {header} not in the known set")
            i = j
            continue
        i += 1

    return err, warn


def main() -> None:
    filters = sys.argv[1:]
    files = sorted(SRC.glob("*.md"))
    if filters:
        files = [f for f in files if any(t in f.name for t in filters)]

    titles: dict[str, str] = {}
    bad = 0
    for path in files:
        err, warn = check(path)
        first = next((ln[2:].strip() for ln in path.read_text(encoding="utf-8").splitlines()
                      if ln.startswith("# ")), "")
        if first in titles:
            err.append(f"H1 duplicates {titles[first]}")
        titles.setdefault(first, path.name)
        if err:
            bad += 1
            print(f"[BAD ] {path.name}")
            for e in err:
                print(f"         {e}")
        else:
            print(f"[OK  ] {path.name}")
        for w in warn:
            print(f"         warn: {w}")

    print(f"\n{len(files) - bad}/{len(files)} clean")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
