"""Render ESLBeginner numbered-series MD files into styled A4 PDFs.

Usage:
  python _gen_beginner_series.py [04-Frequency.md 06-How to describe a person.md ...]
Default: renders 04, 06, 10-20 (the merged/new documents).

Names are resolved relative to MD/. Subfolders are supported and mirrored into
PDF/, e.g. "Travel2Daily/26-01-Is There Nearby.md"
   -> MD/Travel2Daily/_26-01-Is There Nearby.html
   -> PDF/Travel2Daily/26-01-Is There Nearby.pdf
   -> PDF/Travel2Daily/Is There Nearby.pdf   (student copy, number prefix stripped)
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_DIR = ROOT / "MD"
PDF_DIR = ROOT / "PDF"
sys.path.insert(0, str(ROOT))
from build.student_copy import make_student_copy

# Per-lesson spacing profiles, keyed by MD file name -> body class.
LESSON_CLASS = {
    "16-Present Continuous.md": "present-continuous",
    "18-Skills I Can Do.md": "skills",
    "19-Time Clauses.md": "time-clauses",
    "21-Modal Verbs.md": "modal-verbs",
    "21-2-Modal Verbs Complete.md": "modal-verbs",
    "28-Personality Growth.md": "personality",
}

# Per-lesson tables that are plain word lists: keyed by MD file name, the value
# lists the lowercased `### ` headings whose tables render a regular-weight
# first column instead of the default highlighted one.
PLAIN_FIRST_COL = {
    "11-Describing Things Objects.md": ("words", "evaluation"),
}

# Lessons whose tables should all share one fixed column grid, so every table
# lines up on the same vertical edges instead of sizing columns to content.
# Keyed by MD file name -> column widths (applied to every table of that width).
UNIFORM_WIDTHS: dict[str, tuple[int, ...]] = {
    "28-Personality Growth.md": (35, 39, 26),
}

# Per-lesson table column widths, keyed by MD file name and then by the table's
# header cells. Tables sharing a header shape get identical column edges, so
# every table in the handouts lines up column for column.
TABLE_WIDTHS: dict[str, dict[tuple[str, ...], tuple[int, ...]]] = {
    "28-Personality Growth.md": {
        # Story Frame: the frame column is sized to its longest pattern
        # ("Little by little, I became more ______ .").
        ("步骤", "框架", "例"): (11, 41, 48),
        # Words: three equal scenario columns.
        ("和人相处 With people", "内心 Inner self", "做事 At work"): (35, 32, 33),
        # Phrases / Change: the example carries the phrase in context, so it
        # takes half the table.
        ("说法", "Example", "中文"): (29, 49, 22),
        ("Question", "Answer tags", "中文"): (40, 34, 26),
    },
    "21-Modal Verbs.md": {
        ("English", "Chinese"): (60, 40),
        ("推测词", "确定程度", "例句"): (20, 30, 50),
        ("English", "Chinese", "Answer tags"): (42, 24, 34),
    },
    "21-2-Modal Verbs Complete.md": {
        ("English", "Chinese"): (60, 40),
        ("规则", "说明", "例句"): (20, 30, 50),
        ("情态动词", "主要含义", "例句"): (20, 30, 50),
        ("对比", "区别", "例句"): (20, 30, 50),
        ("情态动词", "否定", "常见缩略"): (20, 30, 50),
        ("问句", "肯定回答", "否定回答"): (20, 30, 50),
        ("情态动词", "更多用法", "例句", "翻译"): (20, 20, 34, 26),
        ("结构", "含义", "例句", "翻译"): (20, 20, 34, 26),
        ("确定程度", "现在 / 将来", "对过去", "例句"): (20, 20, 34, 26),
        ("English", "Chinese", "Answer tags"): (42, 24, 34),
    },
}

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
    "21-2-Modal Verbs Complete.md",
]

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'IBM Plex Sans', 'Segoe UI', 'Helvetica Neue', Arial,
        'Microsoft YaHei', 'PingFang SC', sans-serif;
    width: 210mm; background: #ffffff; color: #000000;
    -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;
    font-size: 12px; line-height: 1.45;
}
.page { width: 210mm; padding: 0; }
.page-break { page-break-before: always !important; break-before: always !important; }
.lesson-section {
    break-inside: avoid; page-break-inside: avoid;
}
body.present-continuous {
    font-size: 11px;
}
body.present-continuous h1 {
    margin-bottom: 7px;
}
body.present-continuous h2 {
    margin-top: 10px; margin-bottom: 4px;
}
body.present-continuous p {
    margin: 2px 0; line-height: 1.3;
}
body.present-continuous table {
    font-size: 11.5px; line-height: 1.35; margin-top: 3px; margin-bottom: 8px;
}
body.present-continuous th,
body.present-continuous td {
    padding: 4px 8px;
}
/* Skills I Can Do: 7 stacked sections of short rows. The default spacing leaves
   the practice section alone on a third page, so tighten to 2 pages. */
body.skills {
    font-size: 11px;
}
body.skills h1 {
    margin-bottom: 7px;
}
body.skills h2 {
    margin-top: 10px; margin-bottom: 4px;
}
body.skills h3 {
    margin: 8px 0 3px 0;
}
body.skills p {
    margin: 2px 0; line-height: 1.3;
}
body.skills .dq {
    margin: 10px 0 3px 0;
}
body.skills table {
    font-size: 11.5px; line-height: 1.35; margin-top: 3px; margin-bottom: 8px;
}
body.skills th,
body.skills td {
    padding: 4px 8px;
}
/* Black text throughout — no gray secondary columns. */
body.skills h3,
body.skills td:nth-child(2),
body.skills td:last-child,
body.skills td.cont {
    color: #000000;
}
/* Time Clauses: 22 structure entries stacked in section 1, so the default
   48px display-line gap would push it to 3 pages. Tighter gap keeps the whole
   handout at 4 pages (sec1 x2, sec2 x1, sec3 x1) without shrinking the text. */
body.time-clauses {
    line-height: 1.38;
}
body.time-clauses .dq {
    margin: 8px 0 2px 0;
}
body.time-clauses h3 {
    margin: 8px 0 2px 0;
}
body.time-clauses p {
    margin: 1px 0;
}
/* Modal Verbs: the sections flow across pages so every page fills up, while
   tables and their headings still refuse to split — that keeps each rendered
   page free of orphan rows and orphan headings. */
body.modal-verbs .lesson-section {
    break-inside: auto; page-break-inside: auto;
}
body.modal-verbs table {
    margin: 3px 0 6px 0;
    font-size: 11px;
    line-height: 1.25;
}
body.modal-verbs th,
body.modal-verbs td {
    padding: 3px 8px;
}
body.modal-verbs h3 {
    margin: 8px 0 3px 0;
}
body.modal-verbs h2 {
    margin: 10px 0 4px 0;
}
body.modal-verbs table.aligned {
    table-layout: fixed;
}
body.modal-verbs table.dqt {
    font-size: 10px;
}
/* Personality Growth: a two-page reference sheet. Pure black on white (no
   gray fills, no colored accents), uniform weight (nothing bold), and roomier
   rows than the series default so the tables do not read as one block. */
body.personality { font-size: 12.5px; }
body.personality h1 {
    font-size: 25px; border-bottom-color: #000000;
    padding-bottom: 10px; margin-bottom: 14px;
}
body.personality h2 {
    font-size: 16px; border-left-color: #000000; margin: 13px 0 6px 0;
}
body.personality h3 { font-size: 13px; margin: 12px 0 5px 0; }
body.personality table {
    font-size: 12.5px; line-height: 1.38; margin: 5px 0 11px 0;
    border: none; border-radius: 0;
}
body.personality table.aligned { table-layout: fixed; }
body.personality th,
body.personality td { padding: 5px 10px; border-bottom: none; }
body.personality th {
    background: transparent; font-size: 12.5px; font-weight: 600;
}
body.personality td:first-child,
body.personality b { font-weight: 400; }
body.personality p { margin: 6px 0; line-height: 1.5; }
/* Model story: each English sentence with its Chinese line directly beneath.
   No gap inside a pair, a clear gap between pairs. */
body.personality .bilingual { margin: 6px 0 12px 0; }
body.personality .bilingual p { margin: 0; line-height: 1.4; }
body.personality .bilingual p.zh { margin-bottom: 1px; }
body.personality .bilingual p.en { margin-top: 9px; }
body.personality .bilingual p.en:first-child { margin-top: 0; }
h1 {
    font-size: 24px; font-weight: 600; color: #000000;
    border-bottom: 3px solid #0f62fe; padding-bottom: 8px; margin: 0 0 10px 0;
    break-after: avoid; page-break-after: avoid;
}
h2 {
    font-size: 14px; font-weight: 600; color: #000000;
    border-left: 3px solid #0f62fe; padding-left: 8px; margin: 16px 0 6px 0;
    break-after: avoid; page-break-after: avoid;
}
h3 {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.04em; color: #000000; margin: 12px 0 4px 0;
    break-after: avoid; page-break-after: avoid;
}
p { margin: 3px 0; color: #000000; }
hr { border: none; border-top: 1px solid #e0e0e0; margin: 8px 0; }
table {
    width: 100%; border-collapse: separate; border-spacing: 0; margin: 4px 0 10px 0;
    font-size: 11px; line-height: 1.4; border: 1px solid #e0e0e0; border-radius: 6px;
    overflow: hidden;
    break-inside: avoid; page-break-inside: avoid;
}
table.matrix { table-layout: fixed; }
th, td { border-bottom: 1px solid #e0e0e0; padding: 5px 9px; text-align: left; vertical-align: middle; white-space: nowrap; }
tr:last-child th, tr:last-child td { border-bottom: none; }
th {
    font-weight: 600; font-size: 10.5px; color: #000000; background: #f4f4f4;
    text-align: left; letter-spacing: 0.02em;
}
td:first-child { font-weight: 600; color: #000000; }
/* Merged-column tables: the first cell of a `^` continuation row is the row's
   own first column, not the shared label, so keep it regular weight. */
td.cont { font-weight: 400; color: #000000; }
/* 11-Describing Things Objects: the "words" / "evaluation" tables are pure
   vocabulary lists, so their first column is not highlighted (regular weight). */
table.plainfirst td:first-child { font-weight: 400; color: #000000; }
td:nth-child(2) { color: #000000; }
td:last-child { color: #000000; }
b { color: #000000; font-weight: 600; }
.dq { font-weight: 600; font-size: 14px; color: #000000; margin: 48px 0 4px 0; }
h2 + .dq { margin-top: 10px; }
.dt { margin: 0 0 4px 0; }
.tag {
    display: inline-block; border: 1px solid #e0e0e0; border-radius: 4px;
    padding: 3px 10px; margin: 0 6px 6px 0; color: #000000; font-size: 10.5px;
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
    color: #000000; text-transform: uppercase; letter-spacing: 0.04em;
}
.w6h1-en { flex: 1; color: #000000; font-size: 12px; }
.w6h1-zh { flex: 0 0 auto; color: #000000; font-size: 10.5px; margin-left: 6px; }
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
    """Single inline pipeline: all markdown/source syntax is converted here.

    Handles every inline marker used by the MD sources so no raw syntax
    (backticks, underscores) can ever leak into the rendered PDF:
      **bold**  -> <b>
      `code`    -> plain text (backticks stripped, kept for authoring clarity)
      ______    -> underlined blank span
    """
    text = esc(text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"_{4,}", "<span class='blank'></span>", text)
    return text


def md_to_html(md_text: str, plain_first_col: tuple[str, ...] = (),
               widths_map: dict[tuple[str, ...], tuple[int, ...]] | None = None,
               uniform_widths: tuple[int, ...] | None = None) -> str:
    """plain_first_col: lowercased `### ` headings whose tables should render
    without a bold/emphasized first column.
    widths_map: header row -> column widths, for tables that must line up.
    uniform_widths: one grid applied to every table of matching width."""
    widths_map = widths_map or {}
    lines = md_text.splitlines()
    out: list[str] = []
    i = 0
    section_open = False
    last_h3 = ""
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.strip() == "## 课程介绍":
            # The intro is course metadata kept in the MD for sync_intro.py and
            # is never printed in the handout, matching build/build_pdfs.py.
            i += 1
            while i < len(lines) and not lines[i].startswith("#"):
                i += 1
            continue
        if line.strip() == "<!-- bilingual -->":
            # Sentence-by-sentence translation: consecutive non-blank lines are
            # paired English / Chinese and rendered as a stacked unit, so the
            # translation sits directly under the sentence it belongs to.
            i += 1
            src: list[str] = []
            while i < len(lines) and lines[i].strip() != "<!-- /bilingual -->":
                if lines[i].strip():
                    src.append(lines[i].strip())
                i += 1
            i += 1
            rows = []
            for k in range(0, len(src) - 1, 2):
                rows.append(f"<p class='en'>{inline(src[k])}</p>"
                            f"<p class='zh'>{inline(src[k + 1])}</p>")
            if len(src) % 2:
                rows.append(f"<p class='en'>{inline(src[-1])}</p>")
            out.append("<div class='bilingual'>" + "".join(rows) + "</div>")
            continue
        if line.strip() == "<!-- pagebreak -->":
            if section_open:
                out.append("</div>")
                section_open = False
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
                       ["Positive 积极", "Negative 消极", "Neutral 中性"],
                       ["Color 颜色", "Shape 形状", "Size 大小", "Material 材质"],
                       ["Positive 积极", "Negative 消极", "Positive 积极", "Negative 消极"],
                       # Chinese-header reference tables (modal verbs handouts).
                       ["推测词", "确定程度", "例句"],
                       ["规则", "说明", "例句"],
                       ["情态动词", "主要含义", "例句"],
                       ["情态动词", "更多用法", "例句", "翻译"],
                       ["结构", "含义", "例句", "翻译"],
                       ["确定程度", "现在 / 将来", "对过去", "例句"],
                       ["对比", "区别", "例句"],
                       ["情态动词", "否定", "常见缩略"],
                       ["问句", "肯定回答", "否定回答"],
                       # Personality Growth: reference tables whose first row is
                       # a real header and must read as a level above the rows.
                       ["步骤", "框架", "例"],
                       ["和人相处 With people", "内心 Inner self", "做事 At work"],
                       ["说法", "Example", "中文"],
                       ["Phrase", "Example", "中文"],
                       ["Pattern", "Example", "中文"],
                       ["Connector", "Example", "中文"],
                       ["Topic", "Starter", "中文"],
                       ["Step", "Pattern", "中文"],
                       ["Question", "Answer tags", "中文"])
            is_head = bool(cells) and cells[0] in HEADERS
            classes = []
            if last_h3 in plain_first_col:
                classes.append("plainfirst")
            if cells and cells[0] == ["Positive 积极", "Negative 消极", "Neutral 中性"]:
                classes.append("matrix")
            if cells and cells[0] == ["English", "Chinese", "Answer tags"]:
                # Discussion rows carry a question plus two or three model
                # answers, so they run at a slightly smaller size.
                classes.append("dqt")
            cls = f" class='{' '.join(classes)}'" if classes else ""
            colgroup = ""
            widths = widths_map.get(tuple(cells[0]))
            if widths is None and uniform_widths and len(uniform_widths) == len(cells[0]):
                widths = uniform_widths
            if widths and len(widths) == len(cells[0]):
                classes.append("aligned")
                cls = f" class='{' '.join(classes)}'"
                total = sum(widths)
                colgroup = "<colgroup>" + "".join(
                    f"<col style='width:{w / total * 100:.2f}%'>" for w in widths
                ) + "</colgroup>"
            # Column 0: a `^` cell continues the cell above (rowspan), so a label
            # shared by several rows is written once in the MD source.
            rowspans: dict[int, int] = {}
            merged: set[tuple[int, int]] = set()
            for ri in range(1, len(cells)):
                if not cells[ri] or cells[ri][0].strip() != "^":
                    continue
                lead = ri - 1
                while lead > 0 and cells[lead] and cells[lead][0].strip() in ("", "^"):
                    lead -= 1
                if lead == 0 or not cells[lead] or not cells[lead][0].strip():
                    continue
                rowspans[lead] = rowspans.get(lead, 1) + 1
                merged.add((ri, 0))
            html = f"<table{cls}>{colgroup}"
            for ri, row in enumerate(cells):
                tag = "th" if ri == 0 and is_head else "td"
                merged_first = (ri, 0) in merged
                row_html = []
                first_emitted = True
                for ci, c in enumerate(row):
                    if (ri, ci) in merged:
                        continue
                    span = rowspans.get(ri, 1) if ci == 0 else 1
                    attr = f" rowspan='{span}'" if span > 1 else ""
                    extra = " class='cont'" if merged_first and first_emitted else ""
                    row_html.append(f"<{tag}{extra}{attr}>{inline(c)}</{tag}>")
                    first_emitted = False
                html += "<tr>" + "".join(row_html) + "</tr>"
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
            last_h3 = line[4:].strip().lower()
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            if section_open:
                out.append("</div>")
            out.append("<div class='lesson-section'>")
            section_open = True
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.strip() == "---":
            out.append("<hr>")
        else:
            out.append(f"<p>{inline(line)}</p>")
        i += 1
    if section_open:
        out.append("</div>")
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
    name = Path(md_name).name
    body = md_to_html(md_text, PLAIN_FIRST_COL.get(name, ()), TABLE_WIDTHS.get(name, {}),
                      UNIFORM_WIDTHS.get(name))
    body_class = LESSON_CLASS.get(name, "")
    return (
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>"
        f"<title>{esc(md_name)}</title><style>{CSS}</style></head>"
        f"<body class='{body_class}'><div class='page'>{body}</div></body>"
        "</html>"
    )


def main():
    targets = sys.argv[1:] or DEFAULT
    for name in targets:
        rel = Path(name)
        md_path = MD_DIR / rel
        html_path = md_path.with_name(f"_{md_path.stem}.html")
        pdf_path = PDF_DIR / rel.parent / f"{rel.stem}.pdf"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(build_html(name), encoding="utf-8")
        if export_pdf(html_path, pdf_path):
            print("OK ", pdf_path.relative_to(PDF_DIR))
            sp = make_student_copy(pdf_path)
            if sp:
                print("    student:", sp.relative_to(PDF_DIR))
        else:
            print("HTML only (no playwright):", html_path.relative_to(MD_DIR))


if __name__ == "__main__":
    main()
