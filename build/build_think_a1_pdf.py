#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build PDF/to Think in English Naturally A1.pdf from the A1 manuscript.

Pipeline:
    MD/Think in English Naturally A1 英语思维基础版.md   (source of truth)
        ->  build/tex/...md  (raw-LaTeX blocks)
        ->  pandoc + xelatex/tectonic ->  PDF/to Think in English Naturally A1.pdf

A1 版复刻原 Think in English 的设计：全黑正文，加大字号间距，一场一页。
每个英文句按意群切块，句首加粗、句尾加下划线；A1 学习者词汇量小，故在
每句下方用灰色小字给中文对照。

Usage:
    python build/build_think_a1_pdf.py          # build PDF
    python build/build_think_a1_pdf.py --png    # also render page previews
"""

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))

import build_pdfs as _bp  # noqa: E402
from build_pdfs import (  # noqa: E402
    GEN_DIR,
    PDF_DIR,
    PREVIEW,
    T_pagebreak,
    pandoc_pdf,
    raw,
)
import build_think_pdf as think  # 复用意群切分 chunk_sentence / l_plain

# ---- 引擎路径（与原 Think 脚本一致）----
_PANDOC_WIN = Path(r"C:\Program Files\Pandoc\pandoc.exe")
_MIKTEX_BIN = Path(r"C:\Users\ZZC\AppData\Local\Programs\MiKTeX\miktex\bin\x64")
_bp.PANDOC = str(_PANDOC_WIN) if _PANDOC_WIN.exists() else (shutil.which("pandoc") or "pandoc")
_bp.MIKTEX_BIN = str(_MIKTEX_BIN) if _MIKTEX_BIN.exists() else ""
if not _MIKTEX_BIN.exists():
    _bp.PDF_ENGINE = "xelatex" if shutil.which("xelatex") else (
        "tectonic" if shutil.which("tectonic") else "xelatex"
    )

SRC = ROOT / "MD" / "Think in English Naturally A1 英语思维基础版.md"
PDF_OUT = PDF_DIR / "to Think in English Naturally A1.pdf"
SRC_NAME = PDF_OUT.stem
# PDF 第一行固定标题（用户在需求中指定的精确写法）
A1_TITLE = "Think in English Naturally・A1"

_CN_START = re.compile(r"^[\u4e00-\u9fff]")
_HEADER = re.compile(r"^##\s+(.*)$")


def parse(src: Path) -> dict:
    """md -> {title, sections: [{title, pairs: [(en, cn), ...]}]}"""
    lines = [ln for ln in src.read_text(encoding="utf-8").splitlines()]
    doc = {"title": "", "sections": []}
    title_done = False
    cur = None
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        m = _HEADER.match(s)
        if m:
            cur = {"title": m.group(1).strip(), "pairs": []}
            doc["sections"].append(cur)
            continue
        if not title_done and not cur:
            doc["title"] = s
            title_done = True
            continue
        if cur is None:
            raise ValueError(f"内容出现在场景标题之前: {s!r}")
        # 每两行一对：英文 + 中文
        if _CN_START.match(s):
            if not cur["pairs"] or cur["pairs"][-1][1] is not None:
                # 孤立的无英文先行中文：忽略/报错
                raise ValueError(f"中文行缺少前句英文: {s!r}")
            en, _ = cur["pairs"][-1]
            if en is None:
                raise ValueError(f"前句已填中文: {s!r}")
            cur["pairs"][-1] = (en, s)
        else:
            cur["pairs"].append((s, None))
    # 校验每对都有中文
    missing = [(i, p) for s in doc["sections"] for i, p in enumerate(s["pairs"]) if p[1] is None]
    if missing:
        raise ValueError(f"{len(missing)} 句缺少中文对照: {missing[:3]}")
    return doc


def build_markdown(doc: dict) -> str:
    # 本 A1 版视觉：英文一律 Roboto，中文一律微软雅黑(Microsoft YaHei)。
    # 每个「英文句+中文对照」为一个单位：英文句在上，中文紧随其下；
    # 单位与单位之间留出明显间距分隔。
    out = []
    out.append(raw(
        r"\newfontfamily\roboto{Roboto}[AutoFakeBold=2.5]"
    ))
    # 标题：固定显示 "Think in English Naturally・A1"
    out.append(raw(
        r"\renewcommand{\esltitle}[1]{\par\vspace{2pt}\noindent"
        r"{\roboto\CJKfontspec{Microsoft YaHei}\fontsize{26pt}{28pt}\selectfont\bfseries #1}"
        r"\par\vspace{8pt}}"
    ))
    out.append(raw(
        r"\newcommand{\eslthinksec}[1]{\par\vspace{10pt}\noindent"
        r"{\roboto\CJKfontspec{Microsoft YaHei}\fontsize{16.5pt}{19pt}\selectfont\bfseries #1}"
        r"\par\vspace{5.5pt}}"
    ))
    # 英文句（Roboto）。句前留较大的单位分隔间距，让每对清晰分开
    out.append(raw(
        r"\newcommand{\eslengl}[1]{\par\vspace{6.5pt}\noindent"
        r"{\roboto\fontsize{13pt}{20.5pt}\selectfont #1}}"
    ))
    # 中文对照（微软雅黑灰字），紧贴其上英文句
    out.append(raw(
        r"\newcommand{\eslcnex}[1]{\par\vspace{1pt}\noindent"
        r"{\color{cncolor}\CJKfontspec{Microsoft YaHei}\fontsize{10.5pt}{15.5pt}\selectfont #1}}"
    ))
    out.append(raw(r"\definecolor{cncolor}{HTML}{595959}"))
    out.append(raw(r"\definecolor{faint}{HTML}{000000}"))
    out.append(raw(r"\clubpenalty=8000 \widowpenalty=8000"))

    out.append(raw(rf"\esltitle{{{think.l_plain(A1_TITLE)}}}"))
    for i, sec in enumerate(doc["sections"], 1):
        if i > 1:
            out.append(T_pagebreak())
        out.append(raw(f"\\eslthinksec{{{think.l_plain(sec['title'])}}}"))
        for en, cn in sec["pairs"]:
            chunks = think.chunk_sentence(en)
            rendered = []
            for k, c in enumerate(chunks):
                esc = think.l_plain(c)
                if k == 0:
                    rendered.append(r"{\bfseries " + esc + "}")
                elif k == len(chunks) - 1:
                    rendered.append(r"{\esluline{" + esc + "}}")
                else:
                    rendered.append(esc)
            # 英文句 + 句中对照，作为一个紧密单位输出
            out.append(raw(r"\eslengl{" + " ".join(rendered) + "}"))
            out.append(raw(r"\eslcnex{" + think.l_plain(cn) + "}"))
    return "\n".join(out)


def previews() -> bool:
    """Render the first few pages to PNG."""
    PREVIEW.mkdir(exist_ok=True)
    try:
        import fitz
    except ImportError:
        return False
    pdf_doc = fitz.open(PDF_OUT)
    print(f"pages = {pdf_doc.page_count}")
    for i in range(min(3, pdf_doc.page_count)):
        page = pdf_doc[i]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4))
        png = PREVIEW / f"think_a1_{i}.png"
        pix.save(png)
        print(f"[png]  {png}")
    return True


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if not SRC.exists():
        print(f"[FAIL] 缺少源文件 {SRC}")
        return 1
    doc = parse(SRC)
    n_sec = len(doc["sections"])
    n_pairs = sum(len(s["pairs"]) for s in doc["sections"])
    print(f"解析完成：{n_sec} 个场景 / {n_pairs} 句（含中文对照）")
    if n_sec != 19 or any(len(s["pairs"]) != 20 for s in doc["sections"]):
        print(f"[warn] 预期 19 场景、每场 20 句，实际 {n_sec} 场景、"
              f"每场 {[len(s['pairs']) for s in doc['sections']]}", file=sys.stderr)

    body = build_markdown(doc)
    GEN_DIR.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)
    md_out = GEN_DIR / f"{SRC_NAME}.md"
    md_out.write_text(body, encoding="utf-8")
    ok = pandoc_pdf(md_out, PDF_OUT)
    print(f"[{'ok' if ok else 'FAIL'}] {SRC.name} -> {PDF_OUT.name}")
    if ok and "--png" in sys.argv:
        previews()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
