#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild 造句公式.pdf at a compact fixed page count (target: 10 pages).

Layout-only task: the source of truth is the PDF's own text stream
(PDF/造句公式.pdf, an old Word/Aspose export with huge whitespace).
This script:
  1. extracts the text exactly (per page),
  2. rejoins only the physical line-wraps the OLD export introduced
     (so every logical formula/example stays one logical line),
  3. verifies the reconstruction is lossless (whitespace-insensitive
     equality against the raw page text),
  4. re-typesets the SAME text compactly via tectonic (XeLaTeX engine)
     with the project's Noto Sans / Noto Sans SC print style.

It never adds, removes or rewrites any content character.

Usage:
    python build/build_zaoju_pdf.py            # bilingual 造句公式.pdf (10p)
    python build/build_zaoju_pdf.py --strip-cn # English-only, no Chinese
    python build/build_zaoju_pdf.py --strip-cn --out 造句公式-纯英文
"""

import re
import subprocess
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The pristine source is the original 40-page Word/Aspose export. It is kept
# separate (build/) so it is never overwritten by the rebuilt PDF below.
SRC_PDF = ROOT / "build" / "造句公式源_40页.pdf"
OUT_PDF = ROOT / "PDF" / "造句公式.pdf"
GEN_DIR = ROOT / "build" / "tex"
TEX_OUT = GEN_DIR / "造句公式.tex"

PAGES_TARGET = 10

# ---------------------------------------------------------------------------
# 1. Exact text extraction
# ---------------------------------------------------------------------------
def extract_pages(path):
    import pypdfium2 as pdfium
    d = pdfium.PdfDocument(path)
    return [d[i].get_textpage().get_text_bounded() for i in range(len(d))]


def cjk(ch):
    return ('\u4e00' <= ch <= '\u9fff' or '\u3000' <= ch <= '\u303f'
            or '\uff00' <= ch <= '\uffef')


def reconstruct(pages):
    """physical lines -> logical lines, rejoining only mid-line wraps."""
    phys = []
    for pi, pg in enumerate(pages):
        for ln in pg.split('\n'):
            phys.append((pi, ln.rstrip('\r')))
    logical = []
    i = 0
    while i < len(phys):
        pi, raw = phys[i]
        if raw.strip() == '':
            i += 1
            continue
        buf = raw
        j = i
        while True:
            opens = buf.count('(') + buf.count('（')
            closes = buf.count(')') + buf.count('）')
            if opens <= closes:
                break
            if j + 1 >= len(phys) or phys[j + 1][0] != pi:
                break
            nxt = phys[j + 1][1]
            if nxt.strip() == '':
                break
            buf = buf + _sep(buf, nxt) + nxt.rstrip()
            j += 1
        logical.append(' '.join(buf.split()))
        i = j + 1
    return logical


def _sep(buf, nxt):
    bt = buf.rstrip(' ')
    nxt_l = nxt.lstrip(' ')
    if bt.endswith(' ') or nxt.startswith(' '):
        return ' '
    b = bt[-1] if bt else ''
    c = nxt_l[0] if nxt_l else ''
    if cjk(b) or cjk(c):
        return ''
    return ' '


def norm(s):
    return re.sub(r'\s+', '', s)


# ---------------------------------------------------------------------------
# 2b. Chinese removal (English-only mode) -- removes Chinese, keeps English
# ---------------------------------------------------------------------------
_CJKIDEO = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')
_CHUNK = re.compile(r'[（(][^（）()]*[）)]')


def _has_cjk(s):
    return bool(_CJKIDEO.search(s))


def _fullwidth_ascii(ch):
    o = ord(ch)
    if 0xFF01 <= o <= 0xFF5E:      # full-width forms -> ASCII
        return chr(o - 0xFEE0)
    if o == 0x3000:                # ideographic space
        return ' '
    return ch


def strip_cn_line(line):
    """Remove all Chinese from one logical line.

    - any parenthesised group that contains CJK ideographs is removed whole
      (e.g. "I'm a teacher(我是一名老师)" -> "I'm a teacher");
      English-only parentheticals such as (ASAP) / (could have) are kept;
    - remaining full-width punctuation is mapped to ASCII (? -> ?, （ -> ( );
    - runs of CJK punctuation are dropped.
    """
    out = line
    while True:
        m = None
        for cand in _CHUNK.finditer(out):
            if _has_cjk(cand.group(0)):
                m = cand
                break
        if m is None:
            break
        out = out[:m.start()] + ' ' + out[m.end():]
    out = ''.join(_fullwidth_ascii(c) for c in out)
    out = re.sub(r'[\u3001\u3002\u3008-\u3011\u3014-\u301f]', '', out)
    return ' '.join(out.split())


def strip_cn_lines(lines):
    kept = []
    for ln in lines:
        s = strip_cn_line(ln)
        if _CJKIDEO.search(s):
            continue        # line is still (mostly) Chinese -> drop it
        if re.search(r'[A-Za-z]', s):
            kept.append(s)
    return kept


# ---------------------------------------------------------------------------
# 2. Pattern grouping
# ---------------------------------------------------------------------------
def split_patterns(logical):
    """Group logical lines into patterns by 'N. ...' headers."""
    blocks = []
    cur = None
    for ln in logical:
        m = re.match(r'^(\d+)\.\s', ln)
        if m:
            if cur is not None:
                blocks.append(cur)
            cur = {'num': int(m.group(1)), 'lines': [ln]}
        else:
            if cur is None:
                cur = {'num': None, 'lines': []}
            cur['lines'].append(ln)
    if cur is not None:
        blocks.append(cur)
    return blocks


# ---------------------------------------------------------------------------
# 3. LaTeX emission
# ---------------------------------------------------------------------------
def esc(s):
    return (s
            .replace('\\', r'\textbackslash{}')
            .replace('{', r'\{').replace('}', r'\}')
            .replace('$', r'\$').replace('&', r'\&')
            .replace('#', r'\#').replace('%', r'\%')
            .replace('_', r'\_')
            .replace('^', r'\textasciicircum{}')
            .replace('~', r'\textasciitilde{}'))


P = dict(
    top_mm=13, bottom_mm=12, left_mm=13, right_mm=13,
    col=2, colsep_mm=6.5,        # 2 columns -> 11pt readable type in 10 pages
    pat_pt=11.6, pat_bs=14.2,   # pattern header
    cn_pt=11.2, cn_bs=13.8,     # chinese formula line
    ex_pt=11.0, ex_bs=13.4,     # example lines
    gap_pat=5.0, gap_cn_ex=1.6,
)


def latex_body(blocks, P):
    out = []
    for b in blocks:
        if b['num'] is None:
            # stray pre-header lines (shouldn't happen)
            for ln in b['lines']:
                out.append(_ex(ln, P, first=True))
            continue
        lines = b['lines']
        out.append(_pat(lines[0], P))
        # remaining lines: 2nd is Chinese formula (if CJK, not an example)
        rest = lines[1:]
        for idx, ln in enumerate(rest):
            if idx == 0 and _is_cn_formula(ln):
                out.append(_cn(ln, P))
            elif ln.startswith('举一反三'):
                out.append(_jy(ln, P))
            else:
                out.append(_ex(ln, P))
    return '\n'.join(out)


def _is_cn_formula(ln):
    # Chinese formula line: pure(ish) Chinese + underscores, no half-width latin
    has_cjk = any('\u4e00' <= c <= '\u9fff' for c in ln)
    latin = re.search(r'[A-Za-z]{2,}', ln)
    return has_cjk and latin is None and '（' not in ln and '(' not in ln


def _pat(ln, P):
    # break is allowed in the glue BEFORE a pattern header; header is then
    # kept together with the following chinese formula line (next macro adds
    # the \nopagebreak), so a header is never orphaned at a page bottom.
    return rf"\par\vspace{{{P['gap_pat']}pt}}\noindent\eslpat{{{esc(ln)}}}\par\nopagebreak"


def _cn(ln, P):
    return (rf"\noindent\eslcn{{{esc(ln)}}}\par\nopagebreak"
            rf"\vspace{{{P['gap_cn_ex']}pt}}\nopagebreak")


def _jy(ln, P):
    return (rf"\noindent\esljy{{{esc(ln)}}}\par\nopagebreak"
            rf"\vspace{{{P['gap_cn_ex']}pt}}\nopagebreak")


def _ex(ln, P, first=False):
    # example lines flow normally; only the first example is glued to the
    # chinese formula line above it (that \nopagebreak already emitted).
    # between examples a page break stays allowed, so a long pattern can
    # always break instead of overflowing the page box.
    if first:
        return rf"\noindent\eslex{{{esc(ln)}}}\par\nopagebreak"
    return rf"\noindent\eslex{{{esc(ln)}}}\par"
    # NOTE: first example's \nopagebreak is emitted from _cn/_jy glue above;
    # this _ex(first=True) guard is a no-op kept for clarity.


PREAMBLE = r"""% ESLBeginner · 造句公式 compact rebuild (self-contained, layout-only)
\documentclass[a4paper]{article}
\usepackage[a4paper, top=__TOP__mm, bottom=__BOT__mm, left=__LEFT__mm, right=__RIGHT__mm]{geometry}
\usepackage{fontspec}
\usepackage{xeCJK}
% NOTE: Mapping= (empty) disables XeTeX's default "tex-text" character
% mapping. Without it, straight apostrophes (U+0027, e.g. "didn't") and
% --/--- would silently change to U+2019 / en- / em-dash, altering content.
% Characters must stay byte-identical to the source.
\setmainfont{Noto Sans}[Mapping=]
\setCJKmainfont{Noto Sans SC}
\usepackage{multicol}
\usepackage{xcolor}
\definecolor{ink}{HTML}{1A1A1A}
\definecolor{muted}{HTML}{595959}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\columnsep}{__COLSEP__mm}
% Kernel \raggedright (not ragged2e's \RaggedRight, which breaks xeCJK line
% breaking and causes overfull boxes). It also disables hyphenation entirely,
% so TeX never inserts a '-' glyph that is not in the source text.
\raggedcolumns
\pagestyle{empty}
\newcommand{\eslpat}[1]{{\color{ink}\bfseries\fontsize{__PAT__}{__PATBS__}\selectfont #1}}
\newcommand{\eslcn}[1]{{\color{muted}\fontsize{__CN__}{__CNBS__}\selectfont #1}}
\newcommand{\eslex}[1]{{\color{ink}\fontsize{__EX__}{__EXBS__}\selectfont\raggedright #1}}
\newcommand{\esljy}[1]{{\color{muted}\bfseries\fontsize{__CN__}{__CNBS__}\selectfont #1}}
\begin{document}
\begin{multicols}{__COLSNUM__}
__BODY__
\end{multicols}
\end{document}
"""


def build_tex(blocks, P):
    body = latex_body(blocks, P)
    tex = (PREAMBLE
           .replace('__COLSNUM__', str(P.get('col', 2)))
           .replace('__TOP__', str(P['top_mm'])).replace('__BOT__', str(P['bottom_mm']))
           .replace('__LEFT__', str(P['left_mm'])).replace('__RIGHT__', str(P['right_mm']))
           .replace('__COLSEP__', str(P.get('colsep_mm', 7)))
           .replace('__PAT__', str(P['pat_pt'])).replace('__PATBS__', str(P['pat_bs']))
           .replace('__CN__', str(P['cn_pt'])).replace('__CNBS__', str(P['cn_bs']))
           .replace('__EX__', str(P['ex_pt'])).replace('__EXBS__', str(P['ex_bs']))
           .replace('__BODY__', body))
    GEN_DIR.mkdir(exist_ok=True)
    TEX_OUT.write_text(tex, encoding='utf-8')
    return TEX_OUT


def compile(tex_path):
    cmd = ['tectonic', str(tex_path)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=600)
    if r.returncode != 0:
        print(r.stderr[-4000:])
        return False
    return True


def page_count(pdf_path):
    import pypdfium2 as pdfium
    d = pdfium.PdfDocument(pdf_path)
    n = len(d)
    d.close()
    return n


def _clean(s):
    # pypdfium inserts STX/other control chars (\x00-\x1f) between glyph runs on
    # xelatex/xdvipdfmx output; they are extraction artifacts, not content.
    return re.sub(r'[\x00-\x1f\s]+', '', s)


def verify_content(pdf_path, canonical, logical):
    """Multiset + ordered-sequence content check.

    Single-column output is checked with exact normalized equality. For
    two-column output pypdfium interleaves runs with \x02 markers, so we strip
    controls/whitespace and assert: (a) the multiset of characters is identical
    (nothing added/removed), and (b) every logical source line appears in the
    rendered text in the original order (nothing reordered or lost).
    """
    import pypdfium2 as pdfium
    d = pdfium.PdfDocument(pdf_path)
    txt = ''.join(d[i].get_textpage().get_text_bounded() for i in range(len(d)))
    d.close()
    p = _clean(txt)
    if p == canonical:
        return True  # exact (single column, clean extraction)
    if sorted(p) != sorted(canonical):
        print('    multiset mismatch:', len(p), 'vs', len(canonical))
        return False
    pos = 0
    for ln in logical:
        key = _clean(ln)
        if not key:
            continue
        j = p.find(key, pos)
        if j < 0:
            print('    line not found in order:', repr(key[:50]))
            return False
        pos = j + len(key)
    return True


def main():
    global P, TEX_OUT, OUT_PDF
    pages_arg = PAGES_TARGET
    strip_cn = '--strip-cn' in sys.argv
    out_name = '造句公式-纯英文' if strip_cn else '造句公式'
    if '--out' in sys.argv:
        out_name = sys.argv[sys.argv.index('--out') + 1]
    if '--pages' in sys.argv:
        pages_arg = int(sys.argv[sys.argv.index('--pages') + 1])

    if not SRC_PDF.exists():
        print('[FAIL] source PDF missing:', SRC_PDF)
        return 1

    pages = extract_pages(SRC_PDF)
    logical = reconstruct(pages)
    raw_all = ''.join(pages)
    canonical = norm(raw_all)
    recon = norm(''.join(logical))
    if recon != canonical:
        print('[FAIL] reconstruction not lossless')
        return 1

    content = logical
    if strip_cn:
        content = strip_cn_lines(logical)
        # English-only guard: no CJK ideograph may remain in any kept line
        bad = [s for s in content if _CJKIDEO.search(s)]
        if bad:
            print('[FAIL] Chinese still present after strip:', bad[:3])
            return 1
        print(f'[ok] stripped Chinese: {len(logical)} -> {len(content)} lines')

    blocks = split_patterns(content)
    nums = [b['num'] for b in blocks if b['num'] is not None]
    print(f'[ok] extracted {len(pages)} source pages -> {len(blocks)} patterns '
          f'({min(nums)}..{max(nums)}), {len(content)} lines')

    TEX_OUT = GEN_DIR / f'{out_name}.tex'
    OUT_PDF = ROOT / 'PDF' / f'{out_name}.pdf'
    expected = _clean(''.join(content))
    TEX_OUT.parent.mkdir(exist_ok=True)
    build_tex(blocks, P)
    if not compile(TEX_OUT):
        print('[FAIL] tectonic compile')
        return 1
    produced = TEX_OUT.with_suffix('.pdf')
    if not produced.exists():
        print('[FAIL] no pdf produced:', produced)
        return 1

    n = page_count(produced)
    print(f'[info] produced page count: {n} (target {pages_arg})')
    if not verify_content(produced, expected, content):
        print('[FAIL] rebuilt PDF content does not match source')
        return 1
    print('[ok] content verified lossless (no chars added/removed/reordered)')

    if strip_cn:
        import pypdfium2 as pdfium
        d = pdfium.PdfDocument(produced)
        txt = ''.join(d[i].get_textpage().get_text_bounded() for i in range(len(d)))
        d.close()
        if _CJKIDEO.search(_clean(txt)):
            print('[FAIL] Chinese ideograph found in English-only output')
            return 1
        print('[ok] no Chinese characters remain in output')

    shutil.copy(produced, OUT_PDF)
    print(f'[ok] wrote {OUT_PDF.relative_to(ROOT)}  ({n} pages)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
