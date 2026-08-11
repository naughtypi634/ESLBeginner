#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESLBeginner · MD → styled PDF builder
=====================================
Pipeline:  Markdown  →  (pandoc + custom LaTeX template)  →  xelatex (MiKTeX)  →  PDF

Design system lives in build/preamble.tex (colors, fonts, component macros).
Parsers emit Markdown with raw LaTeX blocks that map to those macros.

Usage:
    python build/build_pdfs.py            # build all PDFs
    python build/build_pdfs.py --png      # also render page-1 previews to build/preview/
    python build/build_pdfs.py 03         # build only file 03
"""

import html as htmllib  # noqa: F401  (kept for parity; unused here)
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from student_copy import make_student_copy
MD_DIR = ROOT / "MD"
GEN_DIR = ROOT / "build" / "tex"
PDF_DIR = ROOT / "PDF"
PREVIEW = ROOT / "build" / "preview"
PANDOC = r"C:\Users\ZZC\AppData\Local\Pandoc\pandoc.exe"
PDF_ENGINE = "xelatex"  # engine passed to pandoc --pdf-engine (override per script)
TEMPLATE = ROOT / "build" / "template.tex"
PREAMBLE = ROOT / "build" / "preamble.tex"
MIKTEX_BIN = r"C:\Users\ZZC\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"

CJK_RE = re.compile(
    r"[\u2e80-\u2eff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef\u3000-\u303f]"
)

META = {
    "01-Be 动词的用法.md": dict(title="Be 动词的用法"),
    "02-There be 句型.md": dict(title="There be 句型"),
    "03-it-句型.md": dict(title="It 句型"),
    "04-Frequency.md": dict(title="频率副词与表达"),
    "05-Comparative And Superlative.md": dict(title="比较级与最高级"),
    "06-How to describe a person.md": dict(title="How to describe a person"),
    "07-定语从句练习.md": dict(title="定语从句练习"),
}

ORDER = [
    "01-Be 动词的用法.md",
    "02-There be 句型.md",
    "03-it-句型.md",
    "04-Frequency.md",
    "05-Comparative And Superlative.md",
    "06-How to describe a person.md",
    "07-定语从句练习.md",
]


# ---------------------------------------------------------------- helpers
def has_cjk(s: str) -> bool:
    return bool(CJK_RE.search(s))


def split_en_cn(line: str):
    m = CJK_RE.search(line)
    if not m:
        return line.strip(), ""
    return line[: m.start()].strip(), line[m.start():].strip()


def esc_latex(s: str) -> str:
    return (
        s.replace("\\", r"\textbackslash{}")
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


def l(s: str) -> str:  # latex-safe text, **bold** -> \textbf{}
    bold = []

    def _save(m):
        bold.append(m.group(1))
        return f"\x00{len(bold) - 1}\x00"

    s = re.sub(r"\*\*(.+?)\*\*", _save, s)
    s = esc_latex(s)
    for i, b in enumerate(bold):
        s = s.replace(f"\x00{i}\x00", r"\eslmark{" + esc_latex(b) + "}")
    return s


def l_underline(s: str) -> str:
    """Like l(), but **bold** markers render as underlines (workbook 07 only)."""
    return l(s).replace(r"\eslmark{", r"\esluline{")


def raw(latex: str) -> str:
    return "```{=latex}\n" + latex + "\n```\n\n"


# ---------------------------------------------------------------- latex emit
def T_title(meta):
    return raw(f"\\esltitle{{{l(meta['title'])}}}")


def T_section(num, cn, en="", lfun=l):
    return raw(f"\\eslsection{{{lfun(num)}}}{{{lfun(cn)}}}{{{lfun(en)}}}")


def T_formula(body, ex=None, label="PATTERN"):
    if ex is not None:
        return raw(f"\\eslformula{{{l(body)}}}{{{l(ex)}}}")
    return raw(f"\\eslformulasimple{{{l(body)}}}")


def T_note(body, lfun=l):
    return raw(f"\\eslnote{{{lfun(body)}}}")


def T_subheader(cn, en="", lfun=l):
    return raw(f"\\eslsubheader{{{lfun(cn)}}}{{{lfun(en)}}}")


def T_pair(en, cn):
    return raw(f"\\eslpair{{{l(en)}}}{{{l(cn)}}}")


def T_triple(cn, en, ex):
    return raw(f"\\esltriple{{{l(cn)}}}{{{l(en)}}}{{{l(ex)}}}")


def T_exitem(n, cn, en):
    return raw(f"\\eslexitem{{{l(n)}}}{{{l(cn)}}}{{{l(en)}}}")


def T_citem(n, cn, en, lfun=l):
    """Compact numbered exercise item — used by 07 (4-page workbook)."""
    return raw(f"\\eslcompactitem{{{lfun(n)}}}{{{lfun(cn)}}}{{{lfun(en)}}}")


def T_qitem(n, body):
    return raw(f"\\eslqitem{{{l(n)}}}{{{l(body)}}}")


def T_dashitem(body):
    return raw(f"\\esldash{{{l(body)}}}")


def T_pattag(body, lfun=l):
    return raw(f"\\eslpattag{{{lfun(body)}}}")


def T_pagebreak():
    return raw("\\eslpagebreak")


def T_tabular(cols, header_cells, rows):
    """Full tabularx — rows may contain \\ and \\hline (not via macro args)."""
    colspec = f"*{{{cols}}}{{>{{\\RaggedRight}}X}}"
    lines = [
        "\\par\\vspace{6pt}",
        "\\noindent\\begin{tabularx}{\\textwidth}{@{}" + colspec + "@{}}",
        "  \\rowcolor{filllight}\\bfseries " + header_cells + "\\\\",
        "  \\hline",
    ]
    for r in rows:
        lines.append("  " + r + " \\\\")
        lines.append("  \\hline")
    lines.append("\\end{tabularx}\\par\\vspace{8pt}")
    return raw("\n".join(lines))


def T_rule(num, title, items):
    rows = [" & ".join(l(c) for c in it) for it in items]
    return (
        raw(f"\\eslrulehead{{{l(num)}}}{{{l(title)}}}")
        + T_tabular(3, "BASE & COMPARATIVE & SUPERLATIVE", rows)
    )


def T_mdtable(header, rows):
    cols = len(header)
    hdr = " & ".join(l(c) for c in header)
    body = [" & ".join(l(c) for c in r) for r in rows]
    return T_tabular(cols, hdr, body)


# ---------------------------------------------------------------- parsers
def parse_01(lines):
    out = []
    title = lines[0][2:].strip()
    sn = 0
    expect_formula = False
    expect_note = False
    for rawline in lines[1:]:
        s = rawline.strip()
        if not s or s == title:
            continue
        if s == "---":
            out.append(T_pagebreak())
            expect_formula = expect_note = False
            continue
        if "\u00b7" in s and has_cjk(s):  # section header — one usage per page
            sn += 1
            if sn > 1:
                out.append(T_pagebreak())
            parts = s.split("\u00b7", 1)
            out.append(T_section(f"{sn}", parts[0].strip(), parts[1].strip()))
            expect_formula = True
            expect_note = False
            continue
        if expect_formula:  # first line after section = pattern formula
            out.append(T_formula(s))
            expect_formula = False
            expect_note = True
            continue
        if expect_note:  # second line after section = explanation note
            out.append(T_note(s))
            expect_note = False
            continue
        if s in ("肯定句", "否定句", "一般疑问句", "特殊疑问句"):
            out.append(T_subheader(s))
            continue
        en, cn = split_en_cn(s)
        if cn:
            out.append(T_pair(en, cn))
        else:
            out.append(T_note(s))
    return out


def parse_02(lines):
    out = []
    title = lines[0][2:].strip()
    expect_formula = False
    i, n = 1, len(lines)
    while i < n:
        s = lines[i].strip()
        i += 1
        if not s or s == title:
            continue
        if s == "---":
            out.append(T_pagebreak())
            expect_formula = False
            continue
        m = re.match(r"^(\d{1,2})\s+(\S.*)$", s)
        if m:
            out.append(T_section(str(int(m.group(1))), m.group(2)))
            expect_formula = True
            continue
        if expect_formula:
            out.append(T_formula(s))
            expect_formula = False
            continue
        m2 = re.match(r"^([A-Za-z][A-Za-z &/]*?)\s+([\u2e80-\u9fff].*)$", s)
        if m2:
            out.append(T_subheader(m2.group(1), m2.group(2)))
            continue
        if not has_cjk(s) and s and s[-1] in ".?!":  # EN sentence → pair
            en = s
            cn = ""
            if i < n:
                nxt = lines[i].strip()
                if has_cjk(nxt) and not re.match(r"^\d", nxt):
                    cn = nxt
                    i += 1
            out.append(T_pair(en, cn))
            continue
        if has_cjk(s):
            out.append(T_note(s))
    return out


def parse_03(lines):
    out = []
    title = lines[0][2:].strip()
    subtitle = "It 常用句型"
    buffer = []

    def flush():
        nonlocal buffer
        for j in range(0, len(buffer) - 2, 3):
            cn, en, ex = buffer[j], buffer[j + 1], buffer[j + 2]
            out.append(T_triple(cn, en, ex))
        buffer = []

    for rawline in lines[1:]:
        s = rawline.strip()
        if not s or s == subtitle or s == title:
            continue
        if s == "---":
            flush()
            out.append(T_pagebreak())
            continue
        if "+" in s:  # formula, possibly with inline example
            flush()
            m = re.search(r"\+ (?:to do|doing|that 从句)", s)
            if m:
                formula = s[: m.end()].strip()
                ex = s[m.end():].strip()
                out.append(T_formula(formula, ex))
            else:
                out.append(T_formula(s))
            continue
        m = re.match(r"^([\u2e80-\u9fff].*?)\s+([A-Za-z].*)$", s)
        if m:  # category subheader
            flush()
            out.append(T_subheader(m.group(1), m.group(2)))
            continue
        buffer.append(s)
    flush()
    return out


def parse_md_table(lines, i):
    header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
    i += 1
    if i < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i]):
        i += 1
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        rows.append(row)
        i += 1
    return header, rows, i


def parse_04(lines):
    out = []
    title_line = lines[0][2:].strip()
    if "\u00b7" in title_line:
        en_part, cn_part = title_line.split("\u00b7", 1)
        title, subtitle = cn_part.strip(), en_part.strip()
    else:
        title, subtitle = title_line, ""
    meta = dict(META["04-Frequency.md"], title=title, subtitle=subtitle)
    out.append(T_title(meta))
    sn = 0
    i, n = 1, len(lines)
    while i < n:
        s = lines[i].strip()
        if not s or s == "---":
            i += 1
            continue
        if s.startswith("## "):
            sn += 1
            h = s[3:].strip()
            m = re.match(r"^(\d+)\.\s*(.*)$", h)
            num = m.group(1) if m else f"{sn:02d}"
            cn = m.group(2) if m else h
            out.append(T_section(num, cn))
            i += 1
            continue
        if s.startswith("### "):
            h = s[4:].strip()
            out.append(T_subheader(h))
            i += 1
            continue
        if s.startswith("Patterns:"):
            out.append(T_formula(s, label="PATTERNS"))
            i += 1
            continue
        if s.startswith("|"):
            header, rows, i = parse_md_table(lines, i)
            out.append(T_mdtable(header, rows))
            continue
        i += 1
    return out, meta


def parse_05(lines):
    out = []
    meta = META["05-Comparative And Superlative.md"]
    out.append(T_title(meta))
    sn = 0
    cur_rule = None
    rule_items = []
    irregular = []
    mode = None

    def flush_rule():
        nonlocal cur_rule, rule_items
        if cur_rule is not None:
            out.append(T_rule(cur_rule[0], cur_rule[1], rule_items))
            cur_rule = None
            rule_items = []

    def flush_irregular():
        nonlocal irregular
        if irregular:
            rows = [
                " & ".join(l(c) for c in irregular[j:j + 3])
                for j in range(0, len(irregular) - 2, 3)
            ]
            out.append(T_tabular(3, "BASE & COMPARATIVE & SUPERLATIVE", rows))
            irregular = []

    for rawline in lines[1:]:
        s = rawline.strip()
        if not s:
            continue
        if re.match(r"^—\s*\d+\s*—", s):
            flush_rule()
            flush_irregular()
            out.append(T_pagebreak())
            continue
        if s == "COMPARATIVE & SUPERLATIVE":
            continue
        if s == "SPEAKING PRACTICE":
            flush_rule()
            flush_irregular()
            sn += 1
            out.append(T_section(f"{sn:02d}", "SPEAKING PRACTICE"))
            mode = "questions"
            continue
        if s == "IRREGULAR FORMS":
            flush_rule()
            sn += 1
            out.append(T_section(f"{sn:02d}", "IRREGULAR FORMS"))
            mode = "irregular"
            continue
        if s == "COMMON COLLOCATIONS":
            flush_irregular()
            sn += 1
            out.append(T_section(f"{sn:02d}", "COMMON COLLOCATIONS"))
            mode = "collocations"
            continue
        if s in ("COMPARE", "SUPERLATIVE"):
            out.append(T_subheader(s))
            continue
        m = re.match(r"^Rule\s+(\d+)\s*(.*)$", s)
        if m:
            flush_rule()
            cur_rule = (m.group(1), m.group(2))
            rule_items = []
            mode = "rules"
            continue
        if "\u2192" in s and mode == "rules" and cur_rule is not None:
            rule_items.append([p.strip() for p in s.split("\u2192")])
            continue
        if mode == "irregular":
            if s in ("Base", "Comparative", "Superlative"):
                continue
            irregular.append(s)
            continue
        if mode == "collocations":
            if s.startswith("—"):
                out.append(T_dashitem(s.lstrip("— ").strip()))
            elif "+" in s or "determiner" in s or "ordinal" in s:
                out.append(T_pattag(s))
            continue
        if mode == "questions":
            mq = re.match(r"^(\d+)\.\s*(.*)$", s)
            if mq:
                out.append(T_qitem(mq.group(1), mq.group(2)))
            continue
    flush_rule()
    flush_irregular()
    return out, meta


def parse_06(lines):
    out = []
    meta = META["06-How to describe a person.md"]
    out.append(T_title(meta))
    sn = 0
    buffer = []
    skip = {"WORD / PHRASE", "中文", "EXAMPLE"}

    def flush():
        nonlocal buffer
        for j in range(0, len(buffer) - 2, 3):
            en, cn, ex = buffer[j], buffer[j + 1], buffer[j + 2]
            out.append(T_triple(cn, en, ex))
        buffer = []

    for rawline in lines[1:]:
        s = rawline.strip()
        if not s or "ESLassistant" in s:
            continue
        if s == "---":
            flush()
            out.append(T_pagebreak())
            continue
        if s in skip:
            continue
        if "+" in s:  # formula
            flush()
            out.append(T_formula(s))
            continue
        m = re.match(r"^([A-Za-z][A-Za-z &/'-]*?)\s{2,}([\u2e80-\u9fff].*)$", s)
        if m:  # section
            flush()
            sn += 1
            en = (m.group(1).strip()
                  .replace("APPE ARANCE", "APPEARANCE")
                  .replace("PERSONALIT Y", "PERSONALITY"))
            out.append(T_section(f"{sn}", en, m.group(2)))
            continue
        m2 = re.match(r"^([A-Z][A-Z ]*?)\s+([\u2e80-\u9fff].*)$", s)
        if m2 and " " not in m2.group(1).strip():  # subheader
            flush()
            out.append(T_subheader(m2.group(1), m2.group(2)))
            continue
        buffer.append(s)
    flush()
    return out, meta


def parse_07(lines):
    out = []
    meta = META["07-定语从句练习.md"]
    out.append(T_title(meta))
    L = l_underline  # workbook 07: emphasis is underlined, not bolded
    chapter_num = 0
    expect_pattern = False
    expect_note = False
    i, n = 1, len(lines)
    while i < n:
        s = lines[i].strip()
        i += 1
        if not s:
            continue
        if s == "---":
            out.append(T_pagebreak())
            expect_pattern = expect_note = False
            continue
        if re.match(r"^定语从句渐进练习（.）$", s):
            chapter_num += 1
            out.append(T_section(f"{chapter_num}", s, lfun=L))
            expect_pattern = expect_note = False
            continue
        if re.match(r"^第.阶梯$", s):
            out.append(T_subheader(s, lfun=L))
            expect_pattern = True
            expect_note = False
            continue
        if expect_pattern:
            out.append(T_pattag(s, lfun=L))
            expect_pattern = False
            expect_note = True
            continue
        if expect_note:
            out.append(T_note(s, lfun=L))
            expect_note = False
            continue
        m = re.match(r"^(\d+)\.\s*(.*)$", s)
        if m:
            n_, cn = m.group(1), m.group(2)
            en = ""
            if i < n:
                nxt = lines[i].strip()
                mm = re.match(r"^\((.+)\)$", nxt)
                if mm:
                    en = mm.group(1)
                    i += 1
            out.append(T_citem(n_, cn, en, lfun=L))
            continue
    return out, meta


PARSERS = {
    "01-Be 动词的用法.md": parse_01,
    "02-There be 句型.md": parse_02,
    "03-it-句型.md": parse_03,
    "04-Frequency.md": parse_04,
    "05-Comparative And Superlative.md": parse_05,
    "06-How to describe a person.md": parse_06,
    "07-定语从句练习.md": parse_07,
}


# ---------------------------------------------------------------- render
def pandoc_pdf(md: Path, pdf: Path) -> bool:
    env = dict(os.environ)
    env["PATH"] = MIKTEX_BIN + os.pathsep + env["PATH"]
    cmd = [
        PANDOC, str(md),
        "-f", "markdown+raw_attribute",
        "--template", str(TEMPLATE),
        "-H", str(PREAMBLE),
        "--pdf-engine=" + PDF_ENGINE,
    ]
    if PDF_ENGINE == "xelatex" and Path(MIKTEX_BIN).exists():
        # MiKTeX-specific: auto-install missing packages (not valid for
        # TeX Live's xelatex on Linux/macOS).
        cmd.append("--pdf-engine-opt=--enable-installer")
    cmd += ["-o", str(pdf)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300, env=env)
    except subprocess.TimeoutExpired:
        print("  [warn] pandoc/xelatex timed out")
        return False
    if r.returncode != 0:
        print(f"  [fail] {r.stderr[-2000:]}")
        return False
    return pdf.exists() and pdf.stat().st_size > 2000


def pdf_preview(pdf: Path, png: Path) -> bool:
    """Render the first page of a PDF to PNG using project-local pypdfium2."""
    if not VENV_PY.exists():
        print("  [warn] .venv missing (pypdfium2) — run: python -m venv .venv && .venv\\Scripts\\pip install pypdfium2 pillow")
        return False
    code = (
        "import pypdfium2 as p;"
        f"pdf=p.PdfDocument(r'{pdf}');"
        "page=pdf[0];"
        f"page.render(scale=1.5).to_pil().save(r'{png}');"
        "print('pages=', len(pdf))"
    )
    try:
        r = subprocess.run([str(VENV_PY), "-c", code],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except subprocess.TimeoutExpired:
        return False
    if r.returncode != 0:
        print(f"  [png-fail] {r.stderr.strip()}")
        return False
    print(f"[png]  {png}")
    return True


def build_one(fname: str, render_png: bool):
    md = MD_DIR / fname
    if not md.exists():
        print(f"[skip] missing {fname}")
        return False
    lines = md.read_text(encoding="utf-8").splitlines()
    if fname == "04-Frequency.md":
        body, meta = parse_04(lines)
    else:
        res = PARSERS[fname](lines)
        if isinstance(res, tuple):
            body, meta = res
        else:
            body, meta = res, META[fname]
    if isinstance(body, list):
        body = "\n".join(body)
    if fname in ("01-Be 动词的用法.md", "02-There be 句型.md", "03-it-句型.md"):
        meta = META[fname]
        body = T_title(meta) + "\n" + body

    stem = md.stem
    GEN_DIR.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)
    md_out = GEN_DIR / f"{stem}.md"
    md_out.write_text(body, encoding="utf-8")

    pdf = PDF_DIR / f"{stem}.pdf"
    if not pandoc_pdf(md_out, pdf):
        print(f"[FAIL] {fname}")
        return False
    print(f"[ok]   {fname}  ->  {pdf.name}")
    sp = make_student_copy(pdf)
    if sp:
        print(f"[student] {sp.name}")

    if render_png:
        PREVIEW.mkdir(exist_ok=True)
        png = PREVIEW / f"{stem}.png"
        pdf_preview(pdf, png)
    return True


def main():
    render_png = "--png" in sys.argv
    targets = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = [o for o in ORDER if not targets or any(t in o for t in targets)]
    ok = 0
    for fname in names:
        if build_one(fname, render_png):
            ok += 1
    print(f"\n{ok}/{len(names)} built  ->  {PDF_DIR}")


if __name__ == "__main__":
    main()
