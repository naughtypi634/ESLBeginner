"""Render ESLBeginner numbered-series MD files into styled A4 PDFs.

Usage:
  python _gen_beginner_series.py [04-Frequency.md 06-How to describe a person.md ...]
Default: renders 04, 06, 10-20 (the merged/new documents).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_DIR = ROOT / "MD"
PDF_DIR = ROOT / "PDF"

DEFAULT = [
    "04-Frequency.md",
    "06-How to describe a person.md",
    "10-Basic Question Forms.md",
    "11-Describing Things Objects.md",
    "12-Feelings And Emotions.md",
    "13-Hobbies.md",
    "14-Passive Voice.md",
    "15-Past Simple Present Perfect.md",
    "16-Present Continuous.md",
    "17-Short Stories Narrative.md",
    "18-Skills I Can Do.md",
    "19-Time Clauses.md",
    "20-Zero First Conditional.md",
    "21-Modal Verbs.md",
]

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    width: 210mm; background: #ffffff; color: #1a1a1a;
    -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
    font-size: 11px; line-height: 1.5;
}
.page { width: 210mm; padding: 0; }
.page-break { page-break-before: always !important; break-before: always !important; }
h1 { font-size: 20px; font-weight: 800; color: #000; border-bottom: 2px solid #000; padding-bottom: 4px; margin-bottom: 8px; }
h2 { font-size: 13px; font-weight: 800; color: #000; margin: 10px 0 4px 0; }
h3 { font-size: 11.5px; font-weight: 700; color: #333; margin: 7px 0 3px 0; }
p { margin: 3px 0; }
hr { border: none; border-top: 1px solid #d0d0d0; margin: 6px 0; }
table { width: 100%; border-collapse: collapse; margin: 3px 0 6px 0; font-size: 10px; }
th, td { border: 1px solid #cccccc; padding: 3px 6px; text-align: left; vertical-align: top; }
th { background: #f0f0f0; font-weight: 800; }
b { color: #000; }
"""


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def inline(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(text))


def md_to_html(md_text: str) -> str:
    lines = md_text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            cells = [r.strip("|").split("|") for r in rows]
            cells = [[c.strip() for c in row] for row in cells if row]
            if len(cells) > 1 and re.fullmatch(r"[\s:\-|]+", "|".join(cells[1])):
                del cells[1]
            html = "<table>"
            for ri, row in enumerate(cells):
                tag = "th" if ri == 0 else "td"
                html += "<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in row) + "</tr>"
            out.append(html + "</table>")
            continue
        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.strip() == "---":
            out.append("<hr>")
        else:
            out.append(f"<p>{inline(line)}</p>")
        i += 1
    return "\n".join(out)


def export_pdf(html_path: Path, pdf_path: Path) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.set_content(html_path.read_text(encoding="utf-8"), wait_until="networkidle")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        page.pdf(
            path=str(pdf_path),
            width="210mm",
            height="297mm",
            print_background=True,
            margin={"top": "13mm", "bottom": "13mm", "left": "16mm", "right": "16mm"},
        )
        browser.close()
    return True


def build_html(md_name: str) -> str:
    md_text = (MD_DIR / md_name).read_text(encoding="utf-8")
    body = md_to_html(md_text)
    return (
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>"
        f"<title>{esc(md_name)}</title><style>{CSS}</style></head><body>"
        f"<div class='page'>{body}</div>"
        "</body></html>"
    )


def main():
    targets = sys.argv[1:] or DEFAULT
    for name in targets:
        html_path = MD_DIR / f"_{Path(name).stem}.html"
        pdf_path = PDF_DIR / name.replace(".md", ".pdf")
        html_path.write_text(build_html(name), encoding="utf-8")
        if export_pdf(html_path, pdf_path):
            print("OK ", pdf_path.name)
        else:
            print("HTML only (no playwright):", html_path.name)


if __name__ == "__main__":
    main()
