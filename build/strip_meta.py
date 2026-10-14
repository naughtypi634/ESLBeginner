#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strip meta content from the Beginner handouts:

  1. drop the "#" row-number header (replaced by 序号),
  2. drop answer-key columns (答案 / 参考答案 / Answer tags),
  3. drop commentary columns (语气 / 用途) and commentary tables (要点 / 说明),
  4. turn the remaining answer columns into blank worksheet fields.

Exercises keep their task; only the answer key and usage commentary go.

Usage: python -I build/strip_meta.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "MD" / "Beginner"

SEP = re.compile(r"^:?-{2,}:?$")

# Header -> new header. The final column is kept but emptied: the exercise
# ("write the -ing form") is meaningless without somewhere to write.
BLANK_FIELD = {
    ("序号", "动词", "答案"): ("序号", "动词", "-ing 形式"),
    ("序号", "原形", "答案", "序号", "原形", "答案"):
        ("序号", "原形", "过去式", "序号", "原形", "过去式"),
    ("序号", "陈述句", "答案"): ("序号", "陈述句", "tag"),
    ("序号", "一般疑问句", "答案"): ("序号", "一般疑问句", "反义疑问句"),
    ("序号", "问句", "事实", "答案"): ("序号", "问句", "事实", "回答"),
    ("序号", "直接说法", "参考答案"): ("序号", "直接说法", "更客气的说法"),
    ("序号", "原句", "参考答案"): ("序号", "原句", "改写"),
}

# Header -> new header, columns dropped (the answer is already in the sentence).
DROP_ANSWER = {
    ("序号", "句子", "答案"): ("序号", "句子"),
}

# Commentary columns to remove outright.
DROP_COLS_OF = {"Answer tags", "语气", "用途"}

# Whole tables that are pure usage commentary, removed.
DELETE_HEADERS = {("要点", "说明")}


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def row(cs: list[str]) -> str:
    return "| " + " | ".join(cs) + " |"


def transform(header: list[str], body: list[list[str]]):
    """Return (header, body) or None to delete the table."""
    header = ["序号" if c == "#" else c for c in header]

    if tuple(header) in DELETE_HEADERS:
        return None

    if tuple(header) in BLANK_FIELD:
        new = list(BLANK_FIELD[tuple(header)])
        # Blank every cell in the columns whose header changed.
        changed = [i for i, (a, b) in enumerate(zip(header, new)) if a != b]
        body = [[("" if i in changed else c) for i, c in enumerate(r)] for r in body]
        return new, body

    if tuple(header) in DROP_ANSWER:
        # Drop the answer column from the body too, not just the header.
        i = header.index("答案")
        return list(DROP_ANSWER[tuple(header)]), [r[:i] + r[i + 1:] for r in body]

    for col in DROP_COLS_OF:
        if col in header:
            i = header.index(col)
            header = header[:i] + header[i + 1:]
            body = [r[:i] + r[i + 1:] for r in body]

    # can / can't 形式: the 要点 column only restates the rule as prose.
    if header == ["要点", "正确", "常见错误"]:
        header = ["正确说法", "常见错误"]
        body = [r[1:] for r in body]

    if "答案" in header:
        i = header.index("答案")
        header = header[:i] + header[i + 1:]
        body = [r[:i] + r[i + 1:] for r in body]

    return header, body


def process(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    out, i, n, changed = [], 0, len(lines), 0
    while i < n:
        s = lines[i].strip()
        is_sep = (
            i + 1 < n
            and lines[i + 1].strip().startswith("|")
            and all(SEP.fullmatch(c) for c in cells(lines[i + 1]))
        )
        if s.startswith("|") and is_sep:
            header = cells(lines[i])
            body, j = [], i + 2
            while j < n and lines[j].strip().startswith("|"):
                body.append(cells(lines[j]))
                j += 1
            res = transform(header, body)
            if res is None:
                while out and not out[-1].strip():
                    out.pop()
                changed += 1
            else:
                new_h, new_b = res
                changed += (new_h != header)
                out.append(row(new_h))
                out.append("|" + "---|" * len(new_h))
                out.extend(row(r) for r in new_b)
            i = j
            continue
        out.append(lines[i])
        i += 1
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return changed


def main() -> None:
    total = 0
    for md in sorted(SRC.glob("*.md")):
        c = process(md)
        total += c
        print(f"{md.name}: {c} table(s) changed")
    print(f"\n{total} table(s) changed")


if __name__ == "__main__":
    main()
