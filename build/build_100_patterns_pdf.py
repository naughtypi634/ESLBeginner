#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build 100 Common English Phrases and Sentence Patterns (bilingual) -> PDF.

Chain:
    MD/100-Common-Phrases-and-Sentence-Patterns.md (bilingual EN/CN)
        -> build/tex/100-Common-Phrases-and-Sentence-Patterns.md (raw-LaTeX)
        -> pandoc + tectonic (xelatex-compatible) -> PDF/100-Common-Phrases-and-Sentence-Patterns.pdf

Design: ESLBeginner print standard (build/preamble.tex, template.tex).
Usage:
    python build/build_100_patterns_pdf.py
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_IN = ROOT / "MD" / "100-Common-Phrases-and-Sentence-Patterns.md"
GEN_DIR = ROOT / "build" / "tex"
PDF_DIR = ROOT / "PDF"
PANDOC = "pandoc"
TEMPLATE = ROOT / "build" / "template.tex"
PREAMBLE = ROOT / "build" / "preamble.tex"
OUT_NAME = "100-Common-Phrases-and-Sentence-Patterns"
TITLE = "100 Common English Phrases and Sentence Patterns"


def esc(s: str) -> str:
    return (
        s.replace("\u2019", "'")  # curly apostrophe -> narrow straight apostrophe
        .replace("\\", r"\textbackslash{}")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("$", r"\$")
        .replace("&", r"\&")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("%", r"\%")
        .replace("^", r"\textasciicircum{}")
        .replace("~", r"\textasciitilde{}")
    )


def raw(latex: str) -> str:
    return "```{=latex}\n" + latex + "\n```\n\n"


def T_title():
    return raw(f"\\esltitle{{{esc(TITLE)}}}")


def T_section(num: str, title: str):
    return raw(f"\\eslsection{{{esc(num)}}}{{{esc(title)}}}{{}}")


def pair_tex(en: str, cn: str) -> str:
    return (
        f"\\par\\vspace{{5pt}}\\noindent\\begin{{minipage}}[t]{{\\linewidth}}"
        f"{{\\ptnbody {esc(en)}}}\\par\\vspace{{2pt}}"
        f"{{\\color{{muted}}\\footnotesize {esc(cn)}}}"
        f"\\end{{minipage}}\\par\\vspace{{9pt}}"
    )


def T_pair(en: str, cn: str):
    return raw(pair_tex(en, cn))


def T_subheader(text: str):
    return raw(f"\\eslsubheader{{{esc(text)}}}{{}}")


def parse_pairs(lines, start):
    """从 start 行起读取 (EN, CN) 对，直到下一个标记或块结束。"""
    pairs = []
    i = start
    while i + 1 < len(lines):
        if lines[i] == "**Dialogue**":
            break
        if lines[i].startswith("- ") and lines[i + 1].startswith("  - "):
            pairs.append((lines[i][2:].strip(), lines[i + 1][4:].strip()))
            i += 2
            continue
        if lines[i].startswith("> ") and lines[i + 1].startswith("> "):
            en, cn = lines[i][2:].strip(), lines[i + 1][2:].strip()
            if re.search(r"[\u4e00-\u9fff]", cn):
                pairs.append((en, cn))
                i += 2
                continue
        i += 1
    return pairs


def parse_doc():
    """解析重排后的 MD：## 分类页眉 + ### 句型小节。"""
    doc = MD_IN.read_text(encoding="utf-8")
    parts = re.split(r"\n(?=## )", doc)
    categories = []
    for p in parts:
        if not p.startswith("## "):
            continue
        lines = p.split("\n")
        m = re.match(r"^## (\d{2}) (\S+)  (.*)$", lines[0])
        if not m:
            continue
        cat = [m.group(1), m.group(2), m.group(3), []]
        starts = [i for i, l in enumerate(lines) if re.match(r"^### \d{3}", l)]
        for k, start in enumerate(starts):
            end = starts[k + 1] if k + 1 < len(starts) else len(lines)
            block = lines[start:end]
            mm = re.match(r"^### (\d{3})(.*)$", block[0])
            ex_i = next((i for i, l in enumerate(block) if l == "**Examples**"), None)
            dg_i = next((i for i, l in enumerate(block) if l == "**Dialogue**"), None)
            if ex_i is None or dg_i is None:
                continue
            cat[3].append((
                mm.group(1),
                mm.group(2).lstrip(" ."),
                parse_pairs(block, ex_i + 1),
                parse_pairs(block, dg_i + 1),
            ))
        categories.append(cat)
    return categories


def build_content():
    parts = [
        raw("\\newfontfamily\\ptnbody{Noto Sans}[AutoFakeBold=2.5]"),
        T_title(),
    ]
    for cat_num, cat_cn, cat_en, sections in parse_doc():
        parts.append(raw(f"\\eslsection{{{esc(cat_num)}}}{{{esc(cat_cn)}}}{{{esc(cat_en)}}}"))
        for num, title, examples, dialogue in sections:
            parts.append(T_section(num, title))
            parts.append(T_subheader("Examples"))
            for en, cn in examples:
                parts.append(T_pair(en, cn))
            parts.append(T_subheader("Dialogue"))
            for en, cn in dialogue:
                parts.append(T_pair(en, cn))
    return "\n".join(parts)


def build_pdf():
    GEN_DIR.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)
    md_out = GEN_DIR / f"{OUT_NAME}.md"
    md_out.write_text(build_content(), encoding="utf-8")
    pdf = PDF_DIR / f"{OUT_NAME}.pdf"
    cmd = [
        PANDOC, str(md_out),
        "-f", "markdown+raw_attribute",
        "--template", str(TEMPLATE),
        "-H", str(PREAMBLE),
        "--pdf-engine=tectonic",
        "-o", str(pdf),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900)
    if r.returncode != 0:
        print("[FAIL] pandoc/tectonic")
        print(r.stderr[-6000:])
        return False
    print(f"[ok]   {pdf.relative_to(ROOT)}  ({pdf.stat().st_size} bytes)")
    return True


if __name__ == "__main__":
    ok = build_pdf()
    raise SystemExit(0 if ok else 1)
