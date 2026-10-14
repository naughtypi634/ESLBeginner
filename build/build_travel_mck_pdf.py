#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESLBeginner · 旅游英语实用手册 (2026 麦肯锡场景版) PDF builder
=============================================================
Source:   build/src/旅游英语实用手册-2026麦肯锡场景版.md  (LaTeX-in-markdown)
Output:   PDF/旅游英语实用手册-2026麦肯锡场景版.pdf

Pipeline: markdown w/ raw LaTeX  →  pandoc  →  xelatex  →  PDF
Design:   build/preamble_mck.tex  (McKinsey blue system)

Usage:
    python build/build_travel_mck_pdf.py           # build PDF
    python build/build_travel_mck_pdf.py --png     # also render page previews
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "build" / "src" / "旅游英语实用手册-2026麦肯锡场景版.md"
GEN_DIR = ROOT / "build" / "tex"
PDF_DIR = ROOT / "PDF"
PREVIEW = ROOT / "build" / "preview" / "mck"
TEMPLATE = ROOT / "build" / "template.tex"
PREAMBLE = ROOT / "build" / "preamble_mck.tex"
OUT_NAME = "旅游英语实用手册-2026麦肯锡场景版"

MIKTEX_BIN = r"C:\Users\ZZC\AppData\Local\Programs\MiKTeX\miktex\bin\x64"


def _toolchain():
    """Resolve pandoc / xelatex per platform, mirroring build_pdfs.py."""
    if sys.platform.startswith("win"):
        pandoc = r"C:\Users\ZZC\AppData\Local\Pandoc\pandoc.exe"
        if not Path(pandoc).exists():
            pandoc = shutil.which("pandoc") or "pandoc"
        return pandoc, "xelatex", MIKTEX_BIN, ROOT / ".venv" / "Scripts" / "python.exe"
    pandoc = shutil.which("pandoc") or "pandoc"
    engine = shutil.which("xelatex") or "tectonic"
    xelatex = shutil.which("xelatex")
    miktex_bin = str(Path(xelatex).parent) if xelatex else ""
    return pandoc, engine, miktex_bin, ROOT / ".venv" / "bin" / "python"


PANDOC, PDF_ENGINE, MIKTEX_BIN, VENV_PY = _toolchain()


def pandoc_pdf(md: Path, pdf: Path) -> bool:
    env = dict(os.environ)
    if MIKTEX_BIN:
        env["PATH"] = MIKTEX_BIN + os.pathsep + env["PATH"]
    cmd = [
        PANDOC, str(md),
        "-f", "markdown+raw_attribute",
        "--template", str(TEMPLATE),
        "-H", str(PREAMBLE),
        "--pdf-engine=" + PDF_ENGINE,
    ]
    if PDF_ENGINE == "xelatex" and Path(MIKTEX_BIN).exists():
        cmd.append("--pdf-engine-opt=--enable-installer")
    cmd += ["-o", str(pdf)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=300, env=env)
    except subprocess.TimeoutExpired:
        print("  [warn] pandoc/xelatex timed out")
        return False
    if r.returncode != 0:
        print(f"  [fail] {r.stderr[-3000:]}")
        return False
    return pdf.exists() and pdf.stat().st_size > 2000


def preview(pdf: Path) -> None:
    """Render every page to build/preview/mck/pNN.png via project-local pypdfium2."""
    if not VENV_PY.exists():
        print("  [warn] .venv missing (pypdfium2)")
        return
    PREVIEW.mkdir(parents=True, exist_ok=True)
    code = (
        "import pypdfium2 as p;"
        f"pdf=p.PdfDocument(r'{pdf}');"
        f"[pdf[i].render(scale=1.4).to_pil().save(r'{PREVIEW}/p%02d.png' % (i+1))"
        " for i in range(len(pdf))];"
        "print('pages=', len(pdf))"
    )
    r = subprocess.run([str(VENV_PY), "-c", code], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180)
    print(("  " + r.stdout.strip()) if r.returncode == 0 else f"  [png-fail] {r.stderr.strip()}")


def main() -> int:
    if not SRC.is_file():
        raise SystemExit(f"source not found: {SRC}")
    GEN_DIR.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)

    md_out = GEN_DIR / f"{OUT_NAME}.md"
    shutil.copyfile(SRC, md_out)

    pdf = PDF_DIR / f"{OUT_NAME}.pdf"
    if not pandoc_pdf(md_out, pdf):
        print(f"[FAIL] {OUT_NAME}")
        return 1
    print(f"[ok]   ->  {pdf}")
    if "--png" in sys.argv:
        preview(pdf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
