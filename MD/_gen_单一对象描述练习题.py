#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单一对象描述练习题 · 专属渲染器

MD/单一对象描述练习题.md  →  HTML 预览（MD/_单一对象描述练习题.html）  →  A4 PDF（PDF/单一对象描述练习题.pdf）

设计要点（对应本项目 2026-08 标准）：
  1. 每种用法（形容词/名词/动名词/表语从句/介词短语/不定式）的例句
     都用「加粗 + 下划线」突出用法对应的词或词组；
  2. 例句省墨：无灰色填充，黑白打印友好；
  3. 层级清晰：标题 → 场景（日常生活/商务场景版）→ 用法分类 → 编号例句；
  4. 字号保证打印清晰，中文例句左侧竖条与句型核心呼应。

用法:
  .venv/bin/python MD/_gen_单一对象描述练习题.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_DIR = ROOT / "MD"
PDF_DIR = ROOT / "PDF"
SOURCE = MD_DIR / "单一对象描述练习题.md"
HTML_OUT = MD_DIR / "_单一对象描述练习题.html"
PDF_OUT = PDF_DIR / "单一对象描述练习题.pdf"

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
    font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    color: #111; background: #fff;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
.sheet { width: 210mm; padding: 0; }

/* ---------- 封面头 ---------- */
.title { border-bottom: 3px solid #111; padding: 1mm 0 3.2mm; margin-bottom: 4.5mm; }
.title h1 { font-size: 24px; font-weight: 800; letter-spacing: 1px; }

/* ---------- 场景（日常生活 / 商务场景版） ---------- */
.part { break-inside: auto; page-break-inside: auto; }
.parthead {
    break-inside: avoid; page-break-inside: avoid;
    border-bottom: 2px solid #111; padding-bottom: 2.4mm; margin-bottom: 2.8mm;
    margin-top: 5mm;
}
.partnum { font-size: 10px; font-weight: 800; letter-spacing: 2.5px; color: #666; }
.parttitle { font-size: 17px; font-weight: 800; margin-top: 1mm; }

/* ---------- 用法分类 ---------- */
.catwrap { break-inside: auto; page-break-inside: auto; }
.cat {
    break-inside: avoid; page-break-inside: avoid;
    break-after: avoid; page-break-after: avoid;
    font-size: 13.5px; font-weight: 800; border-left: 1.2mm solid #111;
    padding-left: 2.5mm; margin: 3.8mm 0 1.8mm;
}

/* ---------- 编号例句：中文 + 英文 ---------- */
.item { break-inside: avoid; page-break-inside: avoid; margin-bottom: 1.5mm; }
.itemline {
    display: table; width: 100%; table-layout: fixed;
}
.num {
    display: table-cell; width: 9mm; font-size: 10px; font-weight: 800;
    color: #666; padding-top: 0.8mm; vertical-align: top;
}
.zh {
    display: table-cell; font-size: 12px; font-weight: 500;
    border-left: 0.8mm solid #111; padding-left: 2.5mm;
    vertical-align: top; padding-top: 0.5mm;
}
.en {
    font-size: 10.5px; color: #555; margin: 0.8mm 0 0 11.5mm; line-height: 1.35;
}
.hl { font-weight: 800; text-decoration: underline; }
"""


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(text: str) -> str:
    """**bold** -> <span class='hl'>, 其余做 HTML 转义。"""
    return re.sub(r"\*\*(.+?)\*\*", r"<span class='hl'>\1</span>", esc(text))


def parse_md(text: str) -> dict:
    doc = {"title": "单一对象描述练习题", "parts": []}
    cur_part = None
    cur_cat = None
    for raw in text.splitlines():
        s = raw.strip()
        if s.startswith("# "):
            doc["title"] = s[2:].strip()
        elif s.startswith("## "):
            cur_part = {"title": s[3:].strip(), "cats": []}
            doc["parts"].append(cur_part)
            cur_cat = None
        elif s.startswith("### "):
            cur_cat = {"title": s[4:].strip(), "items": []}
            cur_part["cats"].append(cur_cat)
        elif re.match(r"^\d+\.\s", s):
            num, zh = re.match(r"^(\d+)\.\s*(.*)$", s).groups()
            en = ""
            cur_cat["items"].append({"num": num, "zh": zh, "en": en})
        elif s and cur_cat and cur_cat["items"] and cur_cat["items"][-1]["en"] == "":
            cur_cat["items"][-1]["en"] = s
    return doc


def build_html(doc: dict) -> str:
    parts = [
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>",
        f"<title>{esc(doc['title'])}</title><style>",
        CSS,
        "</style></head><body><div class='sheet'>",
        f"<div class='title'><h1>{inline(doc['title'])}</h1></div>",
    ]
    for pi, part in enumerate(doc["parts"], 1):
        parts.append("<div class='part'>")
        parts.append("<div class='parthead'>")
        parts.append(f"<div class='partnum'>PART {pi} / {len(doc['parts'])}</div>")
        parts.append(f"<div class='parttitle'>{inline(part['title'])}</div>")
        parts.append("</div>")
        for cat in part["cats"]:
            parts.append("<div class='catwrap'>")
            parts.append(f"<div class='cat'>{inline(cat['title'])}</div>")
            for it in cat["items"]:
                parts.append("<div class='item'>")
                parts.append("<div class='itemline'>")
                parts.append(f"<div class='num'>{it['num']}</div>")
                parts.append(f"<div class='zh'>{inline(it['zh'])}</div>")
                parts.append("</div>")
                parts.append(f"<div class='en'>{inline(it['en'])}</div>")
                parts.append("</div>")
            parts.append("</div>")
        parts.append("</div>")
    parts.append("</div></body></html>")
    return "\n".join(parts)


def export_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Playwright 导出 A4 PDF（页面底部居中页码）。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.set_content(html_path.read_text(encoding="utf-8"), wait_until="networkidle")
        page.pdf(
            path=str(pdf_path),
            width="210mm",
            height="297mm",
            print_background=True,
            margin={"top": "12mm", "bottom": "15mm", "left": "15mm", "right": "15mm"},
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=(
                "<div style='font-family:PingFang SC,sans-serif;font-size:8px;color:#999;"
                "width:100%;text-align:center;'><span class='pageNumber'></span></div>"
            ),
        )
        browser.close()
    return True


def main():
    text = SOURCE.read_text(encoding="utf-8")
    doc = parse_md(text)
    n_items = sum(len(c["items"]) for p in doc["parts"] for c in p["cats"])
    n_hl = sum(
        it["zh"].count("**") // 2 + it["en"].count("**") // 2
        for p in doc["parts"] for c in p["cats"] for it in c["items"]
    )
    print(f"解析完成：{len(doc['parts'])} 个场景 / {n_items} 条例句 / {n_hl} 处强调")
    if n_items != 600 or len(doc["parts"]) != 2:
        print("[warn] 结构与预期不符，请检查 MD 结构", file=sys.stderr)
    HTML_OUT.write_text(build_html(doc), encoding="utf-8")
    if export_pdf(HTML_OUT, PDF_OUT):
        print("PDF OK →", PDF_OUT.name)
    else:
        print("PDF 导出失败（缺少 playwright？请用 .venv/bin/python 运行）", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
