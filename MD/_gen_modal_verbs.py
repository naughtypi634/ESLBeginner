"""Generate 2-page spacious, minimalist black-and-white A4 PDF for How to use MODAL VERBS with strict single-line items."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "MD" / "How to use MODAL VERBS.md"
HTML_PATH = ROOT / "MD" / "_How to use MODAL VERBS.html"
PDF_PATH = ROOT / "PDF" / "How to use MODAL VERBS.pdf"

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
@page {
    size: A4 portrait;
    margin: 10mm 11mm 10mm 11mm;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
    color: #111111;
    background: #ffffff;
    font-size: 9.3pt;
    line-height: 1.35;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}

.page {
    width: 100%;
    height: 100%;
    page-break-after: always;
    break-after: page;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.page:last-child {
    page-break-after: avoid;
    break-after: avoid;
}

.section-container {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
}

.section-block {
    margin-bottom: 2px;
}

h1 {
    font-size: 16.5pt;
    font-weight: 800;
    letter-spacing: -0.01em;
    color: #000000;
    text-transform: uppercase;
    border-bottom: 2.2px solid #000000;
    padding-bottom: 3px;
    margin-bottom: 6px;
    white-space: nowrap;
}

h2 {
    font-size: 11.5pt;
    font-weight: 700;
    color: #000000;
    border-left: 3.5px solid #000000;
    padding-left: 7px;
    margin: 4px 0 3px 0;
    white-space: nowrap;
}

h3 {
    font-size: 9.2pt;
    font-weight: 700;
    color: #1a1a1a;
    background: #f4f4f4;
    padding: 2.5px 7px;
    border-left: 2.5px solid #444444;
    margin: 6px 0 3px 0;
    letter-spacing: 0.01em;
    white-space: nowrap;
}

.dq-title {
    font-size: 9.2pt;
    font-weight: 700;
    color: #000000;
    border-left: 2.5px solid #000000;
    padding-left: 7px;
    background: #eaeaea;
    margin: 6px 0 3px 0;
    text-transform: uppercase;
    white-space: nowrap;
}

p {
    margin: 2px 0 3px 0;
    color: #222222;
    font-size: 9.2pt;
    white-space: nowrap;
}

.form-badge {
    margin: 2px 0 3px 0;
    font-size: 8.8pt;
    white-space: nowrap;
}

code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 8.5pt;
    background: #f0f0f0;
    padding: 1px 4px;
    border-radius: 2px;
    border: 1px solid #d5d5d5;
    color: #000000;
}

strong, b {
    font-weight: 700;
    color: #000000;
}

ul {
    margin: 2px 0 3px 14px;
    padding: 0;
}

li {
    margin-bottom: 2.5px;
    font-size: 8.9pt;
    color: #222222;
    line-height: 1.32;
    white-space: nowrap;
}

.dq-list li {
    margin-bottom: 2.5px;
    color: #111111;
    font-size: 8.9pt;
    white-space: nowrap;
}

.zh-note {
    color: #555555;
    font-size: 8.4pt;
    margin-left: 4px;
}

hr {
    border: none;
    border-top: 1.2px dashed #cccccc;
    margin: 8px 0 6px 0;
}
"""

def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def inline(text: str) -> str:
    text = esc(text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Highlight Chinese translation in parentheses
    text = re.sub(r"\(（?([^\(\)]*[\u4e00-\u9fa5]+[^\(\)]*)）?\)", r"<span class='zh-note'>(\1)</span>", text)
    return text

def md_to_pages_html(md_text: str) -> str:
    raw_pages = md_text.split("<!-- pagebreak -->")
    pages_html = []
    
    for page_idx, raw_page in enumerate(raw_pages):
        lines = raw_page.splitlines()
        out = []
        i = 0
        in_ul = False
        is_dq = False
        
        while i < len(lines):
            line = lines[i].rstrip()
            if not line.strip():
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                i += 1
                continue
            
            if line.startswith("- "):
                if not in_ul:
                    cls = " class='dq-list'" if is_dq else ""
                    out.append(f"<ul{cls}>")
                    in_ul = True
                out.append(f"<li>{inline(line[2:].strip())}</li>")
                i += 1
                continue
            else:
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
            
            if line.startswith("# "):
                out.append(f"<h1>{inline(line[2:])}</h1>")
            elif line.startswith("## "):
                is_dq = False
                out.append(f"<h2>{inline(line[3:])}</h2>")
            elif line.startswith("### Discussion Questions"):
                is_dq = True
                out.append(f"<div class='dq-title'>{inline(line[4:])}</div>")
            elif line.startswith("### "):
                is_dq = False
                out.append(f"<h3>{inline(line[4:])}</h3>")
            elif line.strip() == "---":
                out.append("<hr>")
            elif "**Form:**" in line:
                out.append(f"<p class='form-badge'>{inline(line)}</p>")
            else:
                out.append(f"<p>{inline(line)}</p>")
            i += 1
            
        if in_ul:
            out.append("</ul>")
            
        pages_html.append(f"<div class='page page-{page_idx+1}'>\n" + "\n".join(out) + "\n</div>")
        
    return "\n".join(pages_html)

def build_html() -> str:
    md_text = MD_PATH.read_text(encoding="utf-8")
    body = md_to_pages_html(md_text)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>How to Use MODAL VERBS</title>
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>"""

def export_pdf():
    html_content = build_html()
    HTML_PATH.write_text(html_content, encoding="utf-8")
    
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
        page.pdf(
            path=str(PDF_PATH),
            format="A4",
            print_background=True,
            margin={"top": "9mm", "bottom": "9mm", "left": "11mm", "right": "11mm"},
        )
        browser.close()
    print("PDF generated successfully at:", PDF_PATH)

if __name__ == "__main__":
    export_pdf()
