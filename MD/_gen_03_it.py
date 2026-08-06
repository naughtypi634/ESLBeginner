#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03-it-句型 · 专属渲染器

MD/03-it-句型.md  →  HTML 预览（MD/_03-it-句型.html）  →  A4 PDF（PDF/03-it-句型.pdf）

设计要点（对应 2026-08 修改需求）：
  1. 例句只占一行：例句列足够宽 + nowrap，并用浏览器实测防止溢出；
  2. 例句显眼：浅灰底 + 左侧深色竖条 + 句型核心加粗；
  3. 每种用法例句更多：直接扩充 MD 内容；
  4. 例句全部按 2026 · 中国 · 成年人场景重新审查。

用法:
  .venv/bin/python MD/_gen_03_it.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_DIR = ROOT / "MD"
PDF_DIR = ROOT / "PDF"
SOURCE = MD_DIR / "03-it-句型.md"
HTML_OUT = MD_DIR / "_03-it-句型.html"
PDF_OUT = PDF_DIR / "03-it-句型.pdf"

FORMULA_RE = re.compile(r"\+ (?:to do|doing|that 从句)")
CAT_RE = re.compile(r"^([\u2e80-\u9fff].*?)\s+([A-Za-z].*)$")

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
    font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    color: #1a1a1a; background: #fff;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
.sheet { width: 210mm; padding: 0; }

/* ---------- 封面头 ---------- */
.title { border-bottom: 3px solid #111; padding: 1mm 0 3.2mm; margin-bottom: 4.5mm; }
.title h1 { font-size: 21px; font-weight: 800; letter-spacing: 1px; }
.title .sub { font-size: 9.5px; color: #666; margin-top: 1.8mm; letter-spacing: 1.5px; }
.title .tip { font-size: 9px; color: #888; margin-top: 1.5mm; }

/* ---------- 句型区块：自然分页，标题与首行不拆开 ---------- */
.pat { break-inside: auto; }
.pathead, .cat { break-after: avoid; page-break-after: avoid; }
.pathead { border-bottom: 2px solid #111; padding-bottom: 2.4mm; margin-bottom: 2.8mm; }
.patnum { font-size: 8.5px; font-weight: 800; letter-spacing: 2.5px; color: #8b8b8b; }
.formula { font-size: 14px; font-weight: 800; margin-top: 1mm; }
.note { font-size: 9.5px; color: #666; font-style: italic; margin-top: 1.8mm; }

/* ---------- 用法分类 ---------- */
.cat {
    font-size: 11.5px; font-weight: 800; border-left: 1.1mm solid #111;
    padding-left: 2.5mm; margin: 3.4mm 0 1.6mm;
}
.cat .en { font-weight: 400; color: #7a7a7a; font-size: 8.5px; letter-spacing: 1.2px; margin-left: 2mm; }

/* ---------- 例句行：词义 | 词汇 | 高亮例句 ---------- */
table { width: 100%; table-layout: fixed; border-collapse: separate; border-spacing: 0 1.4mm; }
tr { break-inside: avoid; page-break-inside: avoid; }
td { padding: 1.5mm 2mm; vertical-align: middle; }
td.cn { width: 17mm; font-size: 10px; font-weight: 600; color: #555; white-space: nowrap; overflow: hidden; }
td.en { width: 36mm; font-size: 10.5px; font-weight: 700; white-space: nowrap; overflow: hidden; }
td.ex {
    font-size: 11px; font-weight: 500; background: #f2f2f2;
    border-left: 1mm solid #111; white-space: nowrap; overflow: hidden;
}
td.ex b { font-weight: 800; }
"""


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(text: str) -> str:
    """**bold** -> <b>, 其余做 HTML 转义。"""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(text))


def parse_md(text: str) -> list[dict]:
    """解析 MD：句型（公式+示例）→ 分类 → (中文词, 英文词, 例句) 三元组。"""
    patterns: list[dict] = []
    cur: dict | None = None
    rows_buf: list[str] = []

    def flush_rows() -> list[tuple[str, str, str]]:
        nonlocal rows_buf
        out = []
        for j in range(0, len(rows_buf) - 2, 3):
            out.append((rows_buf[j], rows_buf[j + 1], rows_buf[j + 2]))
        if len(rows_buf) % 3:
            print(f"[warn] 丢弃不完整行: {rows_buf[len(rows_buf) - len(rows_buf) % 3:]!r}",
                  file=sys.stderr)
        rows_buf = []
        return out

    def close_cat():
        nonlocal cur
        if cur is not None and cur["cats"]:
            cur["cats"][-1]["rows"].extend(flush_rows())
        else:
            flush_rows()

    def close_pattern():
        nonlocal cur
        close_cat()
        if cur is not None:
            patterns.append(cur)
        cur = None

    for raw in text.splitlines():
        s = raw.strip()
        if not s or s in ("# it-句型", "It 常用句型"):
            continue
        if s == "---":
            close_pattern()
            continue
        if FORMULA_RE.search(s):
            close_pattern()
            m = FORMULA_RE.search(s)
            formula = s[: m.end()].strip()
            note = s[m.end():].strip()
            cur = {"formula": formula, "note": note, "cats": []}
            continue
        m = CAT_RE.match(s)
        if m and "**" not in s:
            close_cat()
            cat = {"cn": m.group(1).strip(), "en": m.group(2).strip(), "rows": []}
            cur["cats"].append(cat)
            continue
        rows_buf.append(s)
    close_pattern()
    return patterns


def build_html(patterns: list[dict]) -> str:
    parts = [
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>",
        "<title>It 句型</title><style>",
        CSS,
        "</style></head><body><div class='sheet'>",
        "<div class='title'><h1>It 句型</h1>"
        "<div class='sub'>2026 · 中国成年人版 · 9 种 It 常用句型</div>"
        "<div class='tip'>例句中加粗部分是句型核心：先模仿例句，再把句型套用到自己的生活。</div></div>",
    ]
    for i, pat in enumerate(patterns, 1):
        parts.append("<div class='pat'>")
        parts.append("<div class='pathead'>")
        parts.append(f"<div class='patnum'>PATTERN {i} / 9</div>")
        parts.append(f"<div class='formula'>{inline(pat['formula'])}</div>")
        if pat["note"]:
            parts.append(f"<div class='note'>{inline(pat['note'])}</div>")
        parts.append("</div>")
        for cat in pat["cats"]:
            parts.append(
                f"<div class='cat'>{inline(cat['cn'])}<span class='en'>{inline(cat['en'])}</span></div>"
            )
            parts.append("<table><tbody>")
            for cn, en, ex in cat["rows"]:
                parts.append(
                    f"<tr><td class='cn'>{inline(cn)}</td>"
                    f"<td class='en'>{inline(en)}</td>"
                    f"<td class='ex'>{inline(ex)}</td></tr>"
                )
            parts.append("</tbody></table>")
        parts.append("</div>")
    parts.append("</div></body></html>")
    return "\n".join(parts)


def export_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Playwright 导出 A4 PDF；导出前实测每个例句列是否溢出。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.set_content(html_path.read_text(encoding="utf-8"), wait_until="networkidle")
        overflow = page.evaluate(
            """() => {
                const bad = [];
                document.querySelectorAll('td.ex').forEach((el) => {
                    if (el.scrollWidth > el.clientWidth + 1) bad.push(el.textContent.trim());
                });
                return bad;
            }"""
        )
        if overflow:
            print(f"[warn] {len(overflow)} 条例句超出单行宽度，已按原样导出：", file=sys.stderr)
            for t in overflow:
                print("  -", t, file=sys.stderr)
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
    patterns = parse_md(text)
    n_rows = sum(len(c["rows"]) for p in patterns for c in p["cats"])
    print(f"解析完成：{len(patterns)} 个句型 / {n_rows} 条例句")
    if len(patterns) != 9:
        print("[warn] 句型数量不是 9，请检查 MD 结构", file=sys.stderr)
    HTML_OUT.write_text(build_html(patterns), encoding="utf-8")
    if export_pdf(HTML_OUT, PDF_OUT):
        print("PDF OK →", PDF_OUT.name)
    else:
        print("PDF 导出失败（缺少 playwright？请用 .venv/bin/python 运行）", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
