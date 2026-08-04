"""Generate '07-1 定语从句练习 A1-A2' styled HTML + PDF.

Pure black & white (no gray): every visible color is #000000 on #ffffff.
Only the title keeps a rule (border-bottom); no other lines/borders.
Content source: MD/07-1-定语从句练习(A1-A2).md
Layout: continuous A4 flow — 8 ladders, 20 sentences each, with category labels.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_DIR = ROOT / "MD"
PDF_DIR = ROOT / "PDF"

SOURCE = MD_DIR / "07-1-定语从句练习(A1-A2).md"
HTML_OUT = MD_DIR / "_07-1-定语从句练习(A1-A2).html"
PDF_OUT = PDF_DIR / "07-1-定语从句练习(A1-A2).pdf"


CSS = """
@page {
    size: A4;
    margin: 12mm 15mm 14mm 15mm;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Helvetica Neue', 'Helvetica', 'Arial', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    background: #ffffff;
    color: #000000;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    line-height: 1.4;
    font-size: 11px;
}

/* ── Title (the only rule in the document) ── */
.title-area {
    margin: 0 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 2.5px solid #000000;
}
.main-title {
    font-size: 23px;
    font-weight: 800;
    color: #000000;
    letter-spacing: 0.2px;
}

/* ── Ladder (阶梯) ── */
.ladder {
    margin-bottom: 12px;
    page-break-inside: auto;
}
.ladder-head {
    font-size: 13px;
    font-weight: 800;
    color: #000000;
    letter-spacing: 0.3px;
    margin-top: 8px;
}
.note {
    font-size: 9.8px;
    color: #000000;
    margin: 2px 0 5px 0;
    line-height: 1.5;
}

/* ── Category label (分类) ── */
.cat {
    font-size: 10px;
    font-weight: 800;
    color: #000000;
    letter-spacing: 0.5px;
    margin: 7px 0 2px 0;
}

/* ── Items ── */
.item {
    padding: 1.5px 0 2.5px 0;
    page-break-inside: avoid;
}
.item-cn {
    font-size: 10.8px;
    font-weight: 800;
    color: #000000;
    line-height: 1.45;
}
.item-cn .num {
    margin-right: 5px;
    font-weight: 800;
}
.item-en {
    font-size: 9.9px;
    color: #000000;
    padding-left: 17px;
    line-height: 1.45;
}
.item-en .hl {
    font-weight: 800;
    color: #000000;
}
"""


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def inline(text: str) -> str:
    """**bold** -> <b class=hl> (relative-clause emphasis, bold black only)."""
    return re.sub(r"\*\*(.+?)\*\*", r'<b class="hl">\1</b>', esc(text))


def parse() -> list:
    """Return ladders: list of dict(head, pattern, note, groups).
    groups: list of (category_label, items[(num, cn, en)]).
    """
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    ladders: list = []
    cur = None
    cur_group = None

    i = 0
    while i < len(lines):
        s = lines[i].strip()
        i += 1
        if not s or s.startswith("#"):
            continue
        m = re.match(r"^第(.)阶梯$", s)
        if m:
            cur = {"head": s, "pattern": None, "note": None, "groups": []}
            ladders.append(cur)
            cur_group = None
            continue
        if cur is None:
            continue
        if cur["pattern"] is None:
            cur["pattern"] = s
            continue
        if cur["note"] is None:
            cur["note"] = s
            continue
        m = re.match(r"^【(.+)】$", s)
        if m:
            cur_group = {"label": m.group(1), "items": []}
            cur["groups"].append(cur_group)
            continue
        m = re.match(r"^(\d+)\.\s*(.*)$", s)
        if m:
            num = m.group(1)
            cn = m.group(2)
            en = ""
            if i < len(lines):
                nxt = lines[i].strip()
                mm = re.match(r"^\((.+)\)$", nxt)
                if mm:
                    en = mm.group(1)
                    i += 1
            if cur_group is None:
                cur_group = {"label": "", "items": []}
                cur["groups"].append(cur_group)
            cur_group["items"].append((num, cn, en))
            continue
    return ladders


def build_html(ladders) -> str:
    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="UTF-8">',
        "<title>定语从句练习 A1-A2（07-1）</title>",
        "<style>",
        CSS,
        "</style>",
        "</head>",
        "<body>",
        '  <div class="title-area"><div class="main-title">定语从句练习 A1-A2</div></div>',
    ]

    for idx, lad in enumerate(ladders, 1):
        head = lad["head"]
        if lad["pattern"]:
            head = f'{head} · {lad["pattern"]}'
        parts.append(f'  <div class="ladder">')
        parts.append(f'    <div class="ladder-head">{esc(head)}</div>')
        if lad["note"]:
            parts.append(f'    <div class="note">{esc(lad["note"])}</div>')
        for group in lad["groups"]:
            if group["label"]:
                parts.append(f'    <div class="cat">{esc(group["label"])}</div>')
            for num, cn, en in group["items"]:
                parts.append("    <div class=\"item\">")
                parts.append(f'      <div class="item-cn"><span class="num">{num}.</span>{esc(cn)}</div>')
                if en:
                    parts.append(f'      <div class="item-en">{inline(en)}</div>')
                parts.append("    </div>")
        parts.append("  </div>")

    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts)


FOOTER = (
    '<div style="width:100%; font-size:8px; font-weight:700; '
    'font-family:\'Helvetica Neue\',Helvetica,Arial,sans-serif; color:#000000; '
    'text-align:right; padding-right:15mm;">'
    '07-1 · <span class="pageNumber"></span>/<span class="totalPages"></span>'
    "</div>"
)


def export_pdf(html_path: Path, pdf_path: Path) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Playwright not installed — PDF skipped (HTML ready).")
        return False
    html_content = html_path.read_text(encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=FOOTER,
            margin={"top": "12mm", "bottom": "14mm", "left": "15mm", "right": "15mm"},
        )
        browser.close()
    return True


def main():
    ladders = parse()
    assert len(ladders) == 8, f"expected 8 ladders, got {len(ladders)}"
    total = 0
    for lad in ladders:
        n = sum(len(g["items"]) for g in lad["groups"])
        assert n == 20, f'{lad["head"]}: expected 20 items, got {n}'
        total += n
        print(f'  {lad["head"]}: {n} items, {len(lad["groups"])} groups')
    print(f"  total: {total} sentences")

    html = build_html(ladders)
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"HTML written to {HTML_OUT}")

    if export_pdf(HTML_OUT, PDF_OUT):
        print(f"PDF saved to {PDF_OUT}")


if __name__ == "__main__":
    main()
