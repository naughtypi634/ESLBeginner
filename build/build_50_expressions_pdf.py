#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build 50 Common English Expressions (bilingual) -> PDF.

Chain:
    MD/50-Common-Expressions.md (bilingual EN/CN, 50 topics)
        -> build/tex/50-Common-Expressions.md (raw-LaTeX)
        -> pandoc + tectonic -> PDF/50-Common-Expressions.pdf

Design: ESLBeginner print standard (build/preamble.tex, template.tex).
Usage:
    python build/build_50_expressions_pdf.py
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_IN = ROOT / "MD" / "50-Common-Expressions.md"
GEN_DIR = ROOT / "build" / "tex"
PDF_DIR = ROOT / "PDF"
PANDOC = "pandoc"
TEMPLATE = ROOT / "build" / "template.tex"
PREAMBLE = ROOT / "build" / "preamble.tex"
OUT_NAME = "50-Common-Expressions"
TITLE = "50 Common English Expressions"


def esc(s: str) -> str:
    return (
        s.replace("\u2019", "'")
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


def parse_doc():
    doc = MD_IN.read_text(encoding="utf-8")
    topics = []  # (num, cn, en, [(label, [(en, cn), ...]), ...])
    cur = None
    label = None
    for line in doc.split("\n"):
        m = re.match(r"^## (\d{2}) (\S+)  (.*)$", line)
        if m:
            cur = [m.group(1), m.group(2), m.group(3), []]
            topics.append(cur)
            label = None
            continue
        if cur is None:
            continue
        m = re.match(r"^\*\*(.+)\*\*$", line)
        if m:
            label = m.group(1)
            cur[3].append([label, []])
            continue
        m = re.match(r"^- (.+)  ([\u4e00-\u9fff].+)$", line)
        if m:
            if cur[3]:
                cur[3][-1][1].append((m.group(1).strip(), m.group(2).strip()))
            else:
                cur[3].append(["", [(m.group(1).strip(), m.group(2).strip())]])
    return topics


def build_content():
    parts = [
        raw("\\newfontfamily\\ptnbody{Noto Sans}[AutoFakeBold=2.5]"),
        T_title(),
    ]
    for num, cn, en, groups in parse_doc():
        parts.append(raw(f"\\eslsection{{{esc(num)}}}{{{esc(cn)}}}{{{esc(en)}}}"))
        for label, pairs in groups:
            if label:
                parts.append(T_subheader(label))
            for en2, cn2 in pairs:
                parts.append(T_pair(en2, cn2))
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
