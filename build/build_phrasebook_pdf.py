#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESLBeginner · Phrasebook MD -> print-ready PDF
==============================================
Pipeline:  MD/Phrasebook-Complete.md
           -> (parsed, re-emitted as raw LaTeX) build/tex/Phrasebook-*.md
           -> pandoc + custom template    -> xelatex (MiKTeX) -> PDF/

Design: black & white only (one ink + two grays), A4, no decorative rules.
Entries sit in a single longtable so
  * a row is never split across a page (no orphan half-line), and
  * `\\*` on the heading rows keeps a heading together with the entry that
    follows it (no stranded heading at the foot of a page), and on the
    second-to-last row of a section it keeps the section from leaving a single
    row alone at the top of the next page. Only those rows are glued: gluing
    more of them would make the keep-block taller than the space left on a
    page and longtable would break early, leaving a conspicuous gap.
All four columns share one baseline, and each row's advance is stated here
(14.2pt, whatever the row contains), so the vertical rhythm stays constant. A
row whose longest cell is wider than its column is emitted at a slightly
smaller size (down to MIN_PT) rather than wrapped, so no entry ever ends with
a short leftover line. Whatever space the pages leave unused is then spread
into the row spacing (never the other way round - the layout is never squeezed
to save a page), which is what keeps the last page from being a near-empty
page and every page ending flush.

Usage:
    python build/build_phrasebook_pdf.py                # full book -> PDF/
    python build/build_phrasebook_pdf.py --demo          # 11-section demo + page PNGs
    python build/build_phrasebook_pdf.py --no-fill       # leave the row spacing alone
"""

import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
GEN = BUILD / "tex"
PDF_DIR = ROOT / "PDF"
PREVIEW = BUILD / "preview"
MD = ROOT / "MD" / "Phrasebook-Complete.md"
TEMPLATE = BUILD / "phrasebook_template.tex"
PREAMBLE = BUILD / "phrasebook_preamble.tex"

DEMO_SECTIONS = ["S01", "S19", "S44", "S45", "S52", "S60",
                 "S89", "F01", "F02", "F47", "F84"]


def _toolchain():
    if sys.platform.startswith("win"):
        pandoc = r"C:\Users\ZZC\AppData\Local\Pandoc\pandoc.exe"
        if not Path(pandoc).exists():
            pandoc = shutil.which("pandoc") or "pandoc"
        return pandoc, "xelatex", r"C:\Users\ZZC\AppData\Local\Programs\MiKTeX\miktex\bin\x64", ROOT / ".venv" / "Scripts" / "python.exe"
    pandoc = shutil.which("pandoc") or "pandoc"
    xelatex = shutil.which("xelatex")
    return pandoc, "xelatex" if xelatex else "tectonic", str(Path(xelatex).parent) if xelatex else "", ROOT / ".venv" / "bin" / "python"


PANDOC, PDF_ENGINE, MIKTEX_BIN, VENV_PY = _toolchain()

SEC_RE = re.compile(r"^([SF]\d+)\s+(.+?)\s+([\u4e00-\u9fff][^\s]*)$")
ENTRY_RE = re.compile(r"^(\d+)\.\s+\*\*(.+?)\*\*\s+(.+?)\s+-\s+\*(.+?)\*$")

ESC = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def esc(s: str) -> str:
    return "".join(ESC.get(c, c) for c in s)


# ---------- row fitting: measure against the real fonts ----------
FONT_DIR = Path(r"C:\Windows\Fonts")
FONTS = {
    "phrase": FONT_DIR / "NotoSans-Bold.ttf",
    "gloss": FONT_DIR / "Noto Sans SC (TrueType).otf",
    "example": FONT_DIR / "NotoSans-Italic.ttf",
}
PT = 9.5                       # normal entry font size
MIN_PT = 8.25                  # a row is never shrunk below this
STEP = 0.25
COL_MM = {"phrase": 58.0, "gloss": 34.0, "example": 89.0}   # must match the preamble
SLACK = 0.97                   # keep 3% headroom; PIL has no kerning
SAFE = 0.98                    # headroom before a row is shrunk or wrapped
ROW_GAP = 2.2                  # row space in pt (the fill pass adjusts this)
GAP_MIN, GAP_MAX = ROW_GAP, 11.0   # the fill pass only ever loosens, never squeezes
FILL_PASSES = 2
MM = 25.4 / 72.0
PT_PER_MM = 72 / 25.4
BOTTOM_MM = 18.0               # bottom margin, the reference for "page is full"
LEFT_MM = 8.0                  # left margin, needed to spot where a row starts
COL_MM_IDX = 5.0               # the index column, i.e. everything up to LEFT+5mm
_fonts: dict = {}


def _font(kind: str):
    if kind not in _fonts:
        _fonts[kind] = ImageFont.truetype(str(FONTS[kind]), 100)
    return _fonts[kind]


def width_mm(kind: str, text: str) -> float:
    return _font(kind).getlength(text) * PT / 100.0 / 72.0 * 25.4


def cell_lines(kind: str, text: str):
    """Greedy line break for one cell, then never leave a single word or a
    single Chinese character stranded on the last line. Returns the lines; the
    caller joins them with a forced break, so a wrap can never dangle."""
    W = COL_MM[kind] * SLACK
    sep = " " if " " in text else ""
    tokens = text.split(" ") if sep else list(text)
    lines, cur = [], []
    for tok in tokens:
        cand = sep.join(cur + [tok])
        if cur and width_mm(kind, cand) > W:
            lines.append(cur)
            cur = [tok]
        else:
            cur.append(tok)
    if cur:
        lines.append(cur)
    if len(lines) > 1 and len(lines[-1]) == 1 and len(lines[-2]) > 1:
        lines[-1] = [lines[-2].pop()] + lines[-1]
    return [sep.join(line) for line in lines]


def row_pt(phrase: str, gloss: str, example: str) -> float:
    """The row's font size. All four cells of a row shrink together so the row
    stays on one line: 9.5pt normally, and only for a row whose longest cell is
    wider than its column a smaller size (never below MIN_PT). This is what
    keeps an entry from wrapping and ending in a short leftover line."""
    need = max(width_mm(kind, text) / (COL_MM[kind] * SAFE)
               for kind, text in (("phrase", phrase), ("gloss", gloss), ("example", example)))
    if need <= 1:
        return PT
    return round(max(MIN_PT, math.floor(PT / need / STEP) * STEP), 2)


def latex_cell(kind: str, text: str) -> str:
    """A cell body, with forced breaks between wrapped lines (escaped per line)."""
    return "\\\\ ".join(esc(line) for line in cell_lines(kind, text))


def parse(md_text: str):
    """-> [(part_title, [(code, en, zh, [(n, phrase, gloss, example)])])]"""
    title = None
    parts = []
    part = None
    sec = None
    skipped = 0
    for line in md_text.split("\n"):
        if line.startswith("## "):
            head = line[3:].strip()
            if head.endswith("目录"):          # scene / function table of contents
                sec = None
                continue
            m = SEC_RE.match(head)
            if not m:
                skipped += 1
                sec = None
                continue
            sec = (m.group(1), m.group(2), m.group(3), [])
            part[1].append(sec)
        elif line.startswith("# "):
            head = line[2:].strip()
            sec = None
            if title is None:
                title = head
            else:
                part = (head, [])
                parts.append(part)
        elif sec is not None:
            m = ENTRY_RE.match(line.strip())
            if m:
                sec[3].append((int(m.group(1)), m.group(2), m.group(3), m.group(4)))
    if skipped:
        print(f"  [warn] {skipped} heading(s) not recognised")
    return title, parts


def build_body(title, parts, only=None, row_gap=ROW_GAP, tail=0, tail_extra=0.0):
    out = ["\\begin{phdoc}", "\\phtitle{" + esc(title) + "}"]
    wrap = 0
    shrunk = []
    seen = 0
    total_rows = sum(len(s[3]) for _, secs in parts for s in secs
                     if only is None or s[0] in only)
    for part_title, sections in parts:
        keep = [s for s in sections if only is None or s[0] in only]
        if not keep:
            continue
        out.append("\\phpart{" + esc(part_title) + "}")
        for code, en, zh, entries in keep:
            out.append("\\phsection{%s}{%s}" % (esc(en), esc(zh)))
            for i, (n, phrase, gloss, example) in enumerate(entries):
                size = row_pt(phrase, gloss, example)
                if size < PT:
                    shrunk.append((code, n, size, max(
                        width_mm(k, t) / (COL_MM[k] * SAFE)
                        for k, t in (("phrase", phrase), ("gloss", gloss), ("example", example)))))
                cells = [esc(phrase), esc(gloss), esc(example)]
                gap = row_gap
                if seen >= total_rows - tail:          # fill the last page out
                    gap += tail_extra
                seen += 1
                # MIN_PT is enough for every row in the book; if a future entry
                # ever needs less, fall back to a balanced two-line cell rather
                # than let the text run into the next column.
                if any(width_mm(k, t) * size / PT > COL_MM[k] * 0.995 for k, t in
                       (("phrase", phrase), ("gloss", gloss), ("example", example))):
                    wrap += 1
                    cells = [latex_cell("phrase", phrase), latex_cell("gloss", gloss),
                             latex_cell("example", example)]
                    rows = max(c.count("\\\\") for c in cells) + 1
                    gap = row_gap + 13.0 * (rows - 1)
                # the second-to-last row is glued to the last one, so a section
                # never leaves a single row alone at the top of a page
                macro = "\\phentrykeep" if i == len(entries) - 2 else "\\phentry"
                out.append("%s{%.2f}{%.1f}{%d}{%s}{%s}{%s}"
                           % (macro, size, gap, n, cells[0], cells[1], cells[2]))
    out.append("\\end{phdoc}")
    n_entries = sum(len(s[3]) for _, secs in parts for s in secs
                    if only is None or s[0] in only)
    print(f"  rows: {n_entries} entries, {len(shrunk)} shrunk, {wrap} wrapped")
    if shrunk:
        worst = min(s[2] for s in shrunk)
        print("  shrunk rows: " + ", ".join(f"{c}/{n}@{s:.2f}pt" for c, n, s, _ in shrunk[:8])
              + (f" ... smallest {worst:.2f}pt" if len(shrunk) > 8 else ""))
    return "\n".join(out) + "\n"


def run_pandoc(md_out: Path, pdf: Path) -> bool:
    env = dict(os.environ)
    if MIKTEX_BIN:
        env["PATH"] = MIKTEX_BIN + os.pathsep + env["PATH"]
    cmd = [PANDOC, str(md_out), "-f", "markdown+raw_attribute",
           "--template", str(TEMPLATE), "-H", str(PREAMBLE),
           "--pdf-engine=" + PDF_ENGINE]
    if PDF_ENGINE == "xelatex" and MIKTEX_BIN and Path(MIKTEX_BIN).exists():
        cmd.append("--pdf-engine-opt=--enable-installer")
    cmd += ["-o", str(pdf)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=900, env=env)
    if r.returncode != 0:
        print(r.stdout[-3000:])
        print(r.stderr[-3000:])
        return False
    over = [l for l in r.stderr.splitlines() if "Overfull" in l or "Underfull" in l]
    if over:
        print(f"  [boxes] {len(over)} over/underfull warning(s); first 5:")
        for l in over[:5]:
            print("   ", l[:150])
    return pdf.exists() and pdf.stat().st_size > 2000


def measure_fill(pdf: Path):
    """(pages, [gap per page in pt], rows on the last page).

    The gap is the unused space under the text on a page. The fill pass spreads
    that space into the row spacing, so the pages end flush instead of leaving a
    nearly empty last page or a hole at the bottom of a page.
    """
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(pdf))
    gaps, last_rows = [], 0
    for page in doc:
        tp = page.get_textpage()
        lows, anchors = [], set()
        for i in range(tp.count_chars()):
            c = tp.get_text_range(i, 1)
            b = tp.get_charbox(i)
            if not b or c in "\r\n ":
                continue
            y = b[1] * MM
            x = b[0] * MM
            if y <= BOTTOM_MM + 1.0:              # that is the page number
                continue
            lows.append(y)
            if c.isdigit() and x < LEFT_MM + COL_MM_IDX:
                anchors.add(round(y, 2))
        if lows:
            gaps.append((min(lows) - BOTTOM_MM) * PT_PER_MM)
            last_rows = len(anchors)
    pages = len(doc)
    del doc
    return pages, gaps, last_rows


def build_pdf(md_out: Path, pdf: Path, title, parts, only, n_rows, fill=True):
    """Render, then stretch the row spacing until the pages are filled.

    Each pass is measured; the pass with the least unused space wins, and if
    that leaves the last page short the rows on it are spread to reach the
    bottom margin.
    """

    def render(gap, tail=0, extra=0.0):
        md_out.write_text(build_body(title, parts, only, gap, tail, extra), encoding="utf-8")
        return run_pandoc(md_out, pdf)

    best = None
    gap = ROW_GAP
    last_rendered = None
    for attempt in range(FILL_PASSES + 1):
        if not render(gap):
            return False
        last_rendered = gap
        pages, gaps, last_rows = measure_fill(pdf)
        total = sum(gaps)
        print(f"  fill pass {attempt + 1}: row space {gap:.2f}pt -> {pages} pages, "
              f"unused {total:.0f}pt, worst page {max(gaps):.0f}pt "
              f"({max(gaps) / PT_PER_MM:.1f}mm), last page {gaps[-1] / PT_PER_MM:.1f}mm")
        if best is None or total < best[0] - 1:
            best = (total, gap, pages, gaps, last_rows)
        if not fill or total < 12 or attempt == FILL_PASSES:
            break
        gap = min(GAP_MAX, max(GAP_MIN, gap + max(0.05, 0.75 * total / max(n_rows, 1))))

    total, gap, pages, gaps, last_rows = best
    if gap != last_rendered and not render(gap):    # the best pass may not be the last
        return False
    if gap != last_rendered:
        pages, gaps, last_rows = measure_fill(pdf)
    # the last page is the only one whose leftover can be absorbed locally,
    # and only in small doses: spreading a handful of rows over a page looks wrong
    if fill:
        last_gap = gaps[-1]
        if 20 < last_gap < 260 and last_rows >= 3:
            extra = min(4.0, 0.9 * (last_gap - 12) / last_rows)
            print(f"  filling the last page: {last_rows} rows +{extra:.2f}pt each")
            if render(gap, last_rows, extra):
                pages, gaps, last_rows = measure_fill(pdf)
    print(f"  final: {pages} pages, row space {gap:.2f}pt, unused {sum(gaps):.0f}pt, "
          f"worst page {max(gaps) / PT_PER_MM:.1f}mm, last page {gaps[-1] / PT_PER_MM:.1f}mm")
    return True


def preview(pdf: Path, stem: str, scale: float = 1.35):
    PREVIEW.mkdir(exist_ok=True)
    for stale in PREVIEW.glob(f"{stem}-*.png"):   # drop PNGs from a previous run
        stale.unlink()
    if not VENV_PY.exists():
        print("  [warn] .venv missing pypdfium2")
        return
    code = (
        "import pypdfium2 as p;"
        f"d=p.PdfDocument(r'{pdf}');"
        f"[d[i].render(scale={scale}).to_pil().save(r'{PREVIEW}/{stem}-%02d.png' % (i+1)) for i in range(len(d))];"
        "print('pages=', len(d))"
    )
    r = subprocess.run([str(VENV_PY), "-c", code], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    print(r.stdout.strip() or r.stderr.strip()[-500:])


def main():
    demo = "--demo" in sys.argv
    title, parts = parse(MD.read_text(encoding="utf-8"))
    total = sum(len(s[3]) for _, secs in parts for s in secs)
    print(f"parsed: title={title!r} parts={len(parts)} sections={sum(len(s) for _, s in parts)} entries={total}")

    only = set(DEMO_SECTIONS) if demo else None
    n_rows = sum(len(s[3]) for _, secs in parts for s in secs
                 if only is None or s[0] in only)
    stem = "Phrasebook-demo" if demo else "Phrasebook-Complete"
    GEN.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)
    md_out = GEN / f"{stem}.md"
    pdf = PDF_DIR / f"{stem}.pdf"
    if not build_pdf(md_out, pdf, title, parts, only, n_rows,
                     fill="--no-fill" not in sys.argv):
        print("[FAIL]")
        return 1
    print(f"[ok]  {pdf}")
    if demo:
        preview(pdf, "pb-demo", scale=1.35)
    return 0


if __name__ == "__main__":
    sys.exit(main())
