#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build PDF/ESL-Real Life Expressions Cut Ver.1.pdf using the shared ESLBeginner design.

Pipeline:  Markdown  →  raw-LaTeX blocks (shared macros)  →  pandoc + xelatex  →  PDF
"""

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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

# Pandoc / TeX engine: prefer the original Windows paths when present,
# otherwise fall back to whatever is on PATH (macOS/Linux dev machines).
_PANDOC_WIN = Path(r"C:\Program Files\Pandoc\pandoc.exe")
_MIKTEX_BIN = Path(r"C:\Users\ZZC\AppData\Local\Programs\MiKTeX\miktex\bin\x64")
_bp.PANDOC = str(_PANDOC_WIN) if _PANDOC_WIN.exists() else (shutil.which("pandoc") or "pandoc")
_bp.MIKTEX_BIN = str(_MIKTEX_BIN) if _MIKTEX_BIN.exists() else ""
if not _MIKTEX_BIN.exists():
    _bp.PDF_ENGINE = "xelatex" if shutil.which("xelatex") else (
        "tectonic" if shutil.which("tectonic") else "xelatex"
    )

MD = ROOT / "MD" / "ESL-Real Life Expressions Cut Ver.1.md"


def l_plain(s: str) -> str:
    """Like build_pdfs.l(), but **...** emphasis markers are dropped so the
    PDF renders plain text — no bold, no light-gray highlight boxes."""
    return _bp.esc_latex(re.sub(r"\*\*(.+?)\*\*", r"\1", s))


# Route every LaTeX-emitting helper in this document through l_plain().
l = l_plain
_bp.l = l_plain


def _next_example(lines, i):
    """Return the 例： line right below item i (skipping blanks), or ''."""
    j = i + 1
    while j < len(lines):
        nxt = lines[j].strip()
        if not nxt:
            j += 1
            continue
        m6 = re.match(r"^例[：:]\s*(.+)$", nxt)
        return m6.group(1) if m6 else ""
    return ""


def parse(lines):
    out = []
    # 本册要求：字号整体加大（正文 11.5pt / 注释 9.5pt / 备注 10.5pt）
    out.append(raw(
        r"\renewcommand{\esltitle}[1]{\par\vspace{6pt}"
        r"{\fontsize{27pt}{32pt}\selectfont\bfseries #1}\par\vspace{18pt}}"
    ))
    out.append(raw(
        r"\renewcommand{\eslsection}[3]{\par\vspace{16pt}\noindent"
        r"{\dispfont\bfseries\fontsize{17pt}{21pt}\selectfont #1}\hspace{10pt}"
        r"{\fontsize{15pt}{19pt}\selectfont\bfseries #2}"
        r"\if\relax\detokenize{#3}\relax\else\hspace{7pt}{\color{muted}\dispspaced\footnotesize #3}\fi"
        r"\par\vspace{10pt}}"
    ))
    out.append(raw(
        r"\renewcommand{\eslnote}[1]{\par\noindent\begin{minipage}[t]{\linewidth}"
        r"{\fontsize{10.5pt}{15pt}\selectfont #1}\end{minipage}\par\vspace{10pt}}"
    ))
    out.append(raw(
        r"\renewcommand{\esldash}[1]{\par\vspace{3pt}\noindent"
        r"{\dispfont\bfseries\fontsize{11.5pt}{17pt}\selectfont ---}\hspace{8pt}"
        r"\begin{minipage}[t]{\dimexpr\textwidth-26pt\relax}"
        r"{\fontsize{11.5pt}{17pt}\selectfont\bodyfont #1}\end{minipage}\par\vspace{7.5pt}}"
    ))
    # 本册要求：全黑正文，不使用灰色（覆盖共享模板里的 muted / faint）
    out.append(raw(r"\definecolor{muted}{HTML}{000000}"))
    out.append(raw(r"\definecolor{faint}{HTML}{000000}"))
    out.append(raw(r"\clubpenalty=8000 \widowpenalty=8000"))
    out.append(raw(r"\esltitle{Real Life Expressions}"))
    out.append(raw(
        r"\newcommand{\eslpairnb}[3]{\noindent"
        r"\begin{minipage}[t]{\linewidth}{\fontsize{11.5pt}{17pt}\selectfont\bodyfont #1}"
        r"\if\relax\detokenize{#2}\relax\else\par\vspace{2pt}"
        r"{\fontsize{9.5pt}{13.5pt}\selectfont #2}\fi"
        r"\if\relax\detokenize{#3}\relax\else\par\vspace{2.5pt}"
        r"{\fontsize{9.5pt}{13.5pt}\selectfont 例：{\bodyfont #3}}\fi"
        r"\end{minipage}\par\vspace{7pt}}"
    ))
    out.append(raw(
        r"\newcommand{\esldashex}[2]{\par\vspace{2.5pt}\noindent"
        r"{\dispfont\bfseries\fontsize{11.5pt}{17pt}\selectfont ---}\hspace{8pt}"
        r"\begin{minipage}[t]{\dimexpr\textwidth-26pt\relax}"
        r"{\fontsize{11.5pt}{17pt}\selectfont\bodyfont #1}"
        r"\if\relax\detokenize{#2}\relax\else\par\vspace{2pt}"
        r"{\fontsize{9.5pt}{13.5pt}\selectfont 例：{\bodyfont #2}}\fi"
        r"\end{minipage}\par\vspace{7.5pt}}"
    ))
    out.append(raw(
        r"\newcommand{\eslsubhdrnb}[2]{\par\vspace{10.5pt}\noindent"
        r"\begin{minipage}[t]{\linewidth}{\bfseries\fontsize{10.5pt}{14pt}\selectfont #1}"
        r"\if\relax\detokenize{#2}\relax\else\hspace{7pt}{\color{muted}\dispspaced\footnotesize #2}\fi"
        r"\par\vspace{4.5pt}\end{minipage}\par\nopagebreak}"
    ))

    part_count = 0
    i = 0
    while i < len(lines):
        rawline = lines[i]
        s = rawline.rstrip()
        t = s.strip()
        if not t:
            i += 1
            continue
        if t.startswith("> "):  # in-place note block; consecutive lines stay together
            block = [t[2:].strip()]
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("> "):
                block.append(lines[j].strip()[2:].strip())
                j += 1
            out.append(raw("\\eslnote{" + "\\par\\vspace{2pt}".join(l(b) for b in block) + "}"))
            i = j  # skip the consumed note lines
            continue
        m = re.match(r"^# Part (\d+)\s+(.+)$", t)
        if m:
            part_count += 1
            if part_count > 1:
                out.append(T_pagebreak())
            out.append(T_section(m.group(1), m.group(2)))
            i += 1
            continue
        if not s.startswith(" "):  # top-level group title
            m2 = re.match(r"^(\d+)\.\s+(.+)$", t)
            if m2:
                out.append(raw(f"\\eslsubhdrnb{{{l(m2.group(1))}. {l(m2.group(2))}}}{{}}"))
                i += 1
                continue
            out.append(T_dashitem(t))  # plain filler line (过渡语)
            i += 1
            continue
        # indented item
        if re.match(r"^\s*例[：:]\s*(.+)$", t):  # already consumed by item above
            i += 1
            continue
        m3 = re.match(r"^\s*(\d+)\.\s+(.+)$", t)
        if m3:
            en, cn = split_en_cn(m3.group(2))
            ex = _next_example(lines, i)
            out.append(raw(f"\\eslpairnb{{{l(en)}}}{{{l(cn)}}}{{{l(ex)}}}"))
            i += 1
            continue
        m4 = re.match(r"^-\s+(.+)$", t)
        if m4:
            ex = _next_example(lines, i)
            if ex:
                out.append(raw(f"\\esldashex{{{l(m4.group(1))}}}{{{l(ex)}}}"))
            else:
                out.append(T_dashitem(m4.group(1)))
            i += 1
            continue
        out.append(T_dashitem(t))
        i += 1
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
