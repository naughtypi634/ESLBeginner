#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESLBeginner · Beginner series MD -> PDF builder.

The MD/Beginner/ handouts share one regular shape (level-1 title, numbered
level-2 sections, optional level-3 sub-headings, pipe tables, nothing else),
so unlike build_pdfs.py they need no per-file parser: one reader covers all.

Usage:
    python build/build_beginner_pdfs.py            # build every lesson
    python build/build_beginner_pdfs.py 07         # only files matching "07"
    python build/build_beginner_pdfs.py --png      # also render page-1 previews
"""

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))

import build_pdfs as B  # noqa: E402  (reuses toolchain resolution + esc_latex)
from student_copy import make_student_copy  # noqa: E402

SRC_DIR = ROOT / "MD" / "Beginner"
GEN_DIR = ROOT / "build" / "tex" / "beginner"
PDF_DIR = ROOT / "PDF" / "Beginner"
PREVIEW = ROOT / "build" / "preview"
BEGINNER_PREAMBLE = ROOT / "build" / "preamble_beginner.tex"

CJK = B.CJK_RE
SEPARATOR = re.compile(r"^:?-{2,}:?$")

# A4 (595.3pt) minus the Beginner series' 14mm side margins (preamble_beginner)
# -> the line actually available to a table.
TEXTWIDTH_PT = 595.3 - 2 * (14 / 25.4 * 72)
# One visual_len() unit is a single Latin character. Measured off the rendered
# text layer of these very PDFs, a Latin char advances ~0.42em in this
# preamble's Noto Sans; a CJK char is two units and measures ~1.0em. 0.45
# carries a little margin over the measurement.
EM_PER_UNIT = 0.45
# Slack required when choosing a table's type size (see T_table).
SLACK = 0.95

# Tables whose widest cell cannot fit on one line even at the smallest body
# size — reported at the end of a run so the wording can be shortened.
too_wide: list[tuple[str, float, list[str], int, str]] = []
CURRENT_FILE = ""


# ---------------------------------------------------------------- text
def l(s: str) -> str:
    """LaTeX-safe cell text; **bold** becomes wrappable \\textbf (not the
    shared preamble's \\eslmark colorbox, which cannot break across lines and
    would overflow the narrower Beginner table columns)."""
    bold = []

    def _save(m):
        bold.append(m.group(1))
        return f"\x00{len(bold) - 1}\x00"

    s = re.sub(r"\*\*(.+?)\*\*", _save, s)
    s = B.esc_latex(s)
    for i, b in enumerate(bold):
        s = s.replace(f"\x00{i}\x00", r"\textbf{" + B.esc_latex(b) + "}")
    # A literal em dash followed by a space loses that space under xeCJK
    # ("can't —I'm"); \textemdash\ keeps it. Done last, after esc_latex, so the
    # backslash survives. Only the spaced Latin form is rewritten, leaving a
    # Chinese —— to the CJK font.
    return s.replace(" — ", " \\textemdash\\ ")


def raw(latex: str) -> str:
    return "```{=latex}\n" + latex + "\n```\n\n"


def _plain_len(t: str) -> float:
    return sum(2.0 if CJK.search(ch) else 1.0 for ch in t)


def visual_len(s: str) -> float:
    """Rough display width: CJK counts double, markdown markers don't count,
    and bold runs count 10% wider (bold Noto Sans is wider than regular, and a
    column sized to exactly its widest cell would otherwise wrap that cell)."""
    total = 0.0
    pos = 0
    for m in re.finditer(r"\*\*(.+?)\*\*", s):
        total += _plain_len(s[pos:m.start()])
        total += _plain_len(m.group(1)) * 1.10
        pos = m.end()
    return total + _plain_len(s[pos:])


# ---------------------------------------------------------------- components
def T_title(text: str) -> str:
    return raw(f"\\eslbtitle{{{l(text)}}}")


def T_section(num: str, text: str) -> str:
    return raw(f"\\eslbsec{{{num}}}{{{l(text)}}}")


def T_sub(text: str) -> str:
    return raw(f"\\eslbsub{{{l(text)}}}")


def T_table(header: list[str], rows: list[list[str]]) -> str:
    """Column widths are proportional to each column's longest cell.

    \textwidth is ~520pt on A4 with 20mm side margins. The rule of thumb for
    "does the longest cell still fit on one line" is the cell's width in em,
    which visual_len() already approximates (CJK counts double); a table whose
    widest cell needs more than a column can hold steps down to \footnotesize.
    """
    ncols = len(header)
    widths = [
        max([visual_len(header[c])] + [visual_len(r[c]) for r in rows]) for c in range(ncols)
    ]
    weights = [max(w, 5) for w in widths]
    total = sum(weights)
    tabcolsep = 3.0 if ncols >= 5 else 5.0
    # One @{\hspace{...}} per inter-column boundary, i.e. ncols-1 of them. The
    # extra 2pt keeps the assembled box just inside \textwidth — at exactly
    # \textwidth XeTeX reports an overfull hbox of ~1.5pt.
    gap = tabcolsep * (ncols - 1) + 2.0
    fracs = [max(TEXTWIDTH_PT - gap, 1.0) / TEXTWIDTH_PT * w / total for w in weights]

    # Plain tabular with explicit p{} widths, like the preamble's \esltriple.
    colspec = "".join(
        ("@{\\hspace{" + f"{tabcolsep:.0f}" + "pt}}" if c else "@{}")
        + r">{\RaggedRight\arraybackslash}p{" + f"{fracs[c]:.4f}" + r"\textwidth}"
        for c in range(ncols)
    ) + "@{}"

    # Largest type size at which every row still fits on one line. A row is
    # only as wide as the cells it actually holds, so the binding row is the
    # one with the largest total — not every column's maximum at once.
    # Each column is sized to its own longest cell, so the binding constraint is
    # the SUM of the column maxima, not any single row: a table can have every
    # row short yet still need more width than it has, if two different columns
    # hold their long cell in two different rows.
    rows_all = [header] + rows
    total_units = sum(widths)
    s_max = SLACK * (TEXTWIDTH_PT - gap) / (EM_PER_UNIT * total_units) if total_units else 99.0

    # Sizing a row to exactly the available width wraps its widest cell as soon
    # as the estimate is off by a percent, so only take a size that leaves 5%
    # slack. LaTeX names on a 10pt base document: \small is 9pt, \footnotesize 8pt.
    if s_max >= 9.0 / SLACK:
        size, stretch = "\\small", "1.05"
    elif s_max >= 8.0 / SLACK:
        size, stretch = "\\footnotesize", "1.0"
    else:
        size, stretch = "\\footnotesize", "0.96"
        worst = max(rows_all, key=lambda r: sum(visual_len(c) for c in r))
        too_wide.append((CURRENT_FILE, s_max, header, total_units, max(worst, key=visual_len)))
    hdr = " & ".join(l(c) for c in header)
    body = " \\\\\n  \\hline\n  ".join(" & ".join(l(c) for c in r) for r in rows)

    return raw("\n".join([
        # A plain tabular is a single unbreakable box, so starting one at the
        # foot of a page would push it whole to the next one and leave a gap.
        "\\needspace{4\\baselineskip}",
        "\\par\\vspace{4pt}",
        "\\noindent{" + size + "\\setlength{\\tabcolsep}{0pt}"
        "\\renewcommand{\\arraystretch}{" + stretch + "}",
        "\\begin{tabular}{" + colspec + "}",
        "  \\rowcolor{filllight}\\bfseries " + hdr + "\\\\",
        "  \\hline",
        "  " + body + " \\\\",
        "  \\hline",
        "\\end{tabular}}",
        "\\par\\vspace{5pt}",
    ]))


# ---------------------------------------------------------------- parser
def read_table(lines: list[str], i: int):
    rows = []
    n = len(lines)
    while i < n and lines[i].strip().startswith("|"):
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if not all(SEPARATOR.fullmatch(c) for c in cells):
            rows.append(cells)
        i += 1
    return rows[0], rows[1:], i


def parse(md: Path) -> str:
    lines = md.read_text(encoding="utf-8").splitlines()
    out = []
    i, n = 0, len(lines)
    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("### "):
            out.append(T_sub(s[4:].strip()))
        elif s.startswith("## "):
            heading = s[3:].strip()
            m = re.match(r"^(\d+)\.\s*(.*)$", heading)
            if m:
                out.append(T_section(m.group(1), m.group(2)))
            else:
                out.append(T_section("", heading))
        elif s.startswith("# "):
            out.append(T_title(s[2:].strip()))
        elif s.startswith("|"):
            header, rows, i = read_table(lines, i)
            out.append(T_table(header, rows))
            continue
        i += 1
    return "\n".join(out)


# ---------------------------------------------------------------- build
def pandoc_pdf(md: Path, pdf: Path) -> bool:
    env = dict(os.environ)
    cmd = [
        B.PANDOC, str(md),
        "-f", "markdown+raw_attribute",
        "--template", str(B.TEMPLATE),
        "-H", str(B.PREAMBLE),
        "-H", str(BEGINNER_PREAMBLE),
        "--pdf-engine=" + B.PDF_ENGINE,
        "-o", str(pdf),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300, env=env)
    except subprocess.TimeoutExpired:
        print("  [warn] pandoc timed out")
        return False
    if r.returncode != 0:
        print(f"  [fail] {r.stderr[-3000:]}")
        return False
    return pdf.exists() and pdf.stat().st_size > 2000


def build_one(md: Path, render_png: bool) -> bool:
    global CURRENT_FILE
    CURRENT_FILE = md.name
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    gen = GEN_DIR / md.name
    gen.write_text(parse(md), encoding="utf-8")
    pdf = PDF_DIR / (md.stem + ".pdf")
    if not pandoc_pdf(gen, pdf):
        print(f"[FAIL] {md.name}")
        return False
    print(f"[ok]   {md.name}  ->  {pdf.name}")
    sp = make_student_copy(pdf)
    if sp:
        print(f"[student] {sp.name}")
    if render_png:
        PREVIEW.mkdir(exist_ok=True)
        B.pdf_preview(pdf, PREVIEW / (md.stem + ".png"))
    return True


def main() -> None:
    render_png = "--png" in sys.argv
    targets = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = sorted(SRC_DIR.glob("*.md"))
    if targets:
        files = [f for f in files if any(t in f.name for t in targets)]
    ok = 0
    for md in files:
        if build_one(md, render_png):
            ok += 1
    print(f"\n{ok}/{len(files)} built  ->  {PDF_DIR}")
    if too_wide:
        print(f"\n{len(too_wide)} table(s) too wide to keep cells on one line at 8pt:")
        for fname, s_max, header, widest, cell in too_wide:
            print(f"  {fname}  [{s_max:.1f}pt]  {' | '.join(h[:12] for h in header)}")
            print(f"      widest cell: {cell[:110]}")


if __name__ == "__main__":
    main()
