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
sys.path.insert(0, str(ROOT))
from build.student_copy import make_student_copy

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
    font-family: 'IBM Plex Sans', 'Segoe UI', 'Helvetica Neue', Arial,
        'Microsoft YaHei', 'PingFang SC', sans-serif;
    width: 210mm; background: #ffffff; color: #161616;
    -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
    font-size: 12px; line-height: 1.45;
}
.page { width: 210mm; padding: 0; }
.page-break { page-break-before: always !important; break-before: always !important; }
h1 {
    font-size: 24px; font-weight: 600; color: #161616;
    border-bottom: 3px solid #0f62fe; padding-bottom: 8px; margin: 0 0 10px 0;
    break-after: avoid; page-break-after: avoid;
}
h2 {
    font-size: 14px; font-weight: 600; color: #161616;
    border-left: 3px solid #0f62fe; padding-left: 8px; margin: 16px 0 6px 0;
    break-after: avoid; page-break-after: avoid;
}
h3 {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.04em; color: #525252; margin: 12px 0 4px 0;
    break-after: avoid; page-break-after: avoid;
}
p { margin: 3px 0; color: #161616; }
hr { border: none; border-top: 1px solid #e0e0e0; margin: 8px 0; }
table {
    width: 100%; border-collapse: separate; border-spacing: 0; margin: 4px 0 10px 0;
    font-size: 11px; line-height: 1.4; border: 1px solid #e0e0e0; border-radius: 6px;
    overflow: hidden;
    break-inside: avoid; page-break-inside: avoid;
}
table.matrix { table-layout: fixed; }
th, td { border-bottom: 1px solid #e0e0e0; padding: 5px 9px; text-align: left; vertical-align: middle; }
tr:last-child th, tr:last-child td { border-bottom: none; }
th {
    font-weight: 600; font-size: 10.5px; color: #161616; background: #f4f4f4;
    text-align: left; letter-spacing: 0.02em;
}
td:first-child { font-weight: 600; color: #161616; }
td:nth-child(2) { color: #525252; }
td:last-child { color: #525252; }
b { color: #161616; font-weight: 600; }
.dq { font-weight: 600; font-size: 14px; color: #161616; margin: 48px 0 4px 0; }
h2 + .dq { margin-top: 10px; }
.dt { margin: 0 0 4px 0; }
.tag {
    display: inline-block; border: 1px solid #e0e0e0; border-radius: 4px;
    padding: 3px 10px; margin: 0 6px 6px 0; color: #525252; font-size: 10.5px;
}
.w6h1-card {
    border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden;
    margin: 6px 0 12px 0; background: #ffffff;
    break-inside: avoid; page-break-inside: avoid;
}
.w6h1-row {
    display: flex; align-items: baseline; gap: 10px;
    padding: 7px 10px; border-bottom: 1px solid #e0e0e0;
}
.w6h1-row:last-child { border-bottom: none; }
.w6h1-tag {
    flex: 0 0 44px; font-size: 10px; font-weight: 600;
    color: #0f62fe; text-transform: uppercase; letter-spacing: 0.04em;
}
.w6h1-en { flex: 1; color: #161616; font-size: 12px; }
.w6h1-zh { flex: 0 0 auto; color: #525252; font-size: 10.5px; margin-left: 6px; }
.blank {
    display: inline-block; min-width: 68px; height: 1.05em;
    border-bottom: 1px solid #161616; margin: 0 2px; vertical-align: baseline;
}
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
        if line.strip() == "<!-- pagebreak -->":
            out.append("</div><div class='page page-break'>")
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
            if cells and cells[0] and cells[0][0].strip().lower().startswith("6w1h"):
                rows_html = []
                for row in cells[1:]:
                    tag = inline(row[0].strip()) if row and row[0].strip() else ""
                    sentence = inline(row[1].strip()) if len(row) > 1 and row[1].strip() else ""
                    gloss = inline(row[2].strip()) if len(row) > 2 and row[2].strip() else ""
                    sentence = sentence.replace("______", "<span class='blank'></span>")
                    row_html = (f"<div class='w6h1-row'><span class='w6h1-tag'>{tag}</span>"
                                f"<span class='w6h1-en'>{sentence}</span>")
                    if gloss:
                        row_html += f"<span class='w6h1-zh'>{gloss}</span>"
                    row_html += "</div>"
                    rows_html.append(row_html)
                out.append("<div class='w6h1-card'>" + "".join(rows_html) + "</div>")
                continue
            HEADERS = (["English", "Chinese"], ["English", "Chinese", "Example"],
                       ["English", "Chinese", "Answer tags"], ["English", "Chinese", "Keywords"],
                       ["Positive 积极", "Negative 消极", "Neutral 中性"])
            is_head = bool(cells) and cells[0] in HEADERS
            cls = ""
            if cells and cells[0] == ["Positive 积极", "Negative 消极", "Neutral 中性"]:
                cls = " class='matrix'"
            html = f"<table{cls}>"
            for ri, row in enumerate(cells):
                tag = "th" if ri == 0 and is_head else "td"
                html += "<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in row) + "</tr>"
            out.append(html + "</table>")
            continue
        m_bold = re.fullmatch(r"\*\*(.+?)\*\*", line.strip())
        if m_bold:
            out.append(f"<p class='dq'>{inline(m_bold.group(1))}</p>")
            i += 1
            continue
        if line.startswith(">"):
            tags = [t.strip() for t in line.lstrip(">").strip().split("/") if t.strip()]
            boxes = "".join(f"<span class='tag'>{inline(t)}</span>" for t in tags)
            out.append(f"<p class='dt'>{boxes}</p>")
            i += 1
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
            margin={"top": "12mm", "bottom": "12mm", "left": "14mm", "right": "14mm"},
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
            sp = make_student_copy(pdf_path)
            if sp:
                print("    student:", sp.name)
        else:
            print("HTML only (no playwright):", html_path.name)


if __name__ == "__main__":
    main()
