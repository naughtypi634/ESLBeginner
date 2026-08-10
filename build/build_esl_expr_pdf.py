#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build PDF/ESL-Real Life Expressions Cut Ver.1.pdf using the shared ESLBeginner design.

Pipeline:  Markdown  →  raw-LaTeX blocks (shared macros)  →  pandoc + xelatex  →  PDF
"""

import re
import sys
from pathlib import Path

ROOT = Path(r"F:\AI project\ESLBeginner")
sys.path.insert(0, str(ROOT / "build"))

from build_pdfs import (  # noqa: E402
    GEN_DIR,
    PDF_DIR,
    T_dashitem,
    T_note,
    T_pagebreak,
    T_section,
    l,
    pandoc_pdf,
    raw,
    split_en_cn,
)
import build_pdfs as _bp

_bp.PANDOC = r"C:\Program Files\Pandoc\pandoc.exe"

MD = ROOT / "MD" / "ESL-Real Life Expressions Cut Ver.1.md"


def parse(lines):
    legend = [t[2:].strip() for t in lines if t.strip().startswith("> ")]
    out = []
    out.append(raw(r"\esltitle{ESL Real Life Expressions}"))
    out.append(raw(r"\par{\color{muted}\small 日常口语表达速查表}\par\vspace{16pt}"))
    out.append(raw(r"\clubpenalty=8000 \widowpenalty=8000"))
    if legend:
        out.append(T_note("；".join(legend)))
    out.append(raw(
        r"\newcommand{\eslpairnb}[2]{\noindent"
        r"\begin{minipage}[t]{\linewidth}{\bodyfont #1}"
        r"\if\relax\detokenize{#2}\relax\else\par\vspace{1.5pt}"
        r"{\color{muted}\footnotesize #2}\fi\end{minipage}\par\vspace{5.5pt}}"
    ))
    out.append(raw(
        r"\newcommand{\eslsubhdrnb}[2]{\par\vspace{9pt}\noindent"
        r"\begin{minipage}[t]{\linewidth}{\bfseries\small #1}"
        r"\if\relax\detokenize{#2}\relax\else\hspace{7pt}{\color{muted}\dispspaced\footnotesize #2}\fi"
        r"\par\vspace{4pt}\end{minipage}\par\nopagebreak}"
    ))

    part_count = 0
    for rawline in lines:
        s = rawline.rstrip()
        t = s.strip()
        if not t:
            continue
        if t.startswith("> "):  # already emitted under the title
            continue
        m = re.match(r"^# Part (\d+)\s+(.+)$", t)
        if m:
            part_count += 1
            if part_count > 1:
                out.append(T_pagebreak())
            out.append(T_section(m.group(1), m.group(2)))
            continue
        if not s.startswith(" "):  # top-level group title
            m2 = re.match(r"^(\d+)\.\s+(.+)$", t)
            if m2:
                out.append(raw(f"\\eslsubhdrnb{{{l(m2.group(1))}. {l(m2.group(2))}}}{{}}"))
                continue
            out.append(T_dashitem(t))  # plain filler line (过渡语)
            continue
        # indented item
        m3 = re.match(r"^\s*(\d+)\.\s+(.+)$", t)
        if m3:
            en, cn = split_en_cn(m3.group(2))
            out.append(raw(f"\\eslpairnb{{{l(en)}}}{{{l(cn)}}}"))
            continue
        m4 = re.match(r"^-\s+(.+)$", t)
        if m4:
            out.append(T_dashitem(m4.group(1)))
            continue
        out.append(T_dashitem(t))
    return out


def main():
    lines = MD.read_text(encoding="utf-8").splitlines()
    body = "\n".join(parse(lines))
    GEN_DIR.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)
    md_out = GEN_DIR / f"{MD.stem}.md"
    md_out.write_text(body, encoding="utf-8")
    pdf = PDF_DIR / f"{MD.stem}.pdf"
    ok = pandoc_pdf(md_out, pdf)
    print(f"[{'ok' if ok else 'FAIL'}] {MD.name} -> {pdf}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
