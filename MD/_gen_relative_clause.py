"""Generate 'Relative Clause' practice PDF from scratch.

Standalone beginner worksheet (4 pages, black & white):
  Part 1  Join the sentences
  Part 2  Choose the correct relative word
  Part 3  Translate into English
  Part 4  Correct the mistakes
  Answer key on the last page.
All English sentences <= 20 words, 2026 China daily-life context.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "PDF"
MD_DIR = ROOT / "MD"


def export_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Render HTML to PDF with Playwright if available; else skip."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    html_content = html_path.read_text(encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        page.wait_for_selector(".page", state="visible", timeout=10000)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        page.pdf(
            path=str(pdf_path),
            width="210mm",
            height="297mm",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
        )
        browser.close()
    return True

# ═══════════════════════════════════════════════════════════════════════
#  CONTENT
# ═══════════════════════════════════════════════════════════════════════

PART1 = [
    (
        "I have a neighbor.",
        "She always waters my plants when I travel.",
        "I have a neighbor who always waters my plants when I travel.",
    ),
    (
        "I bought a milk tea.",
        "It has pearls and extra cheese foam.",
        "I bought a milk tea that has pearls and extra cheese foam.",
    ),
    (
        "We use a parcel locker.",
        "It is at the gate of our community.",
        "We use a parcel locker that is at the gate of our community.",
    ),
    (
        "I found a charger.",
        "Its cable was broken.",
        "I found a charger whose cable was broken.",
    ),
    (
        "The taxi driver was very kind.",
        "He took me to the train station.",
        "The taxi driver who took me to the train station was very kind.",
    ),
    (
        "The concert was amazing.",
        "I bought tickets for it.",
        "The concert that I bought tickets for was amazing.",
    ),
    (
        "This is the wet market.",
        "My mom buys vegetables here.",
        "This is the wet market where my mom buys vegetables.",
    ),
    (
        "I still remember the day.",
        "I got my first job offer on that day.",
        "I still remember the day when I got my first job offer.",
    ),
]

PART2 = [
    ("The man ___ is standing at the door is my uncle.", "who / that"),
    ("The book ___ I borrowed from you is on my desk.", "that / which"),
    ("This is the hotel ___ we stayed last summer.", "where"),
    ("The girl ___ phone was stolen looks very upset.", "whose"),
    ("Do you know the reason ___ he was late this morning?", "why"),
    ("Winter is the season ___ vegetable prices usually go up.", "when"),
    ("The woman ___ you talked to just now is our new manager.", "whom / that"),
    ("I want a phone ___ battery can last two days.", "whose"),
    ("That is the park ___ we fly kites every weekend.", "where"),
    ("The cake ___ my mom made tasted really good.", "that / which"),
    ("This is the moment ___ everything changed.", "when"),
    ("The shoes ___ I bought online are a little too small.", "that / which"),
]

PART3 = [
    ("我喜欢不推销课程的健身教练。", "who", "I like trainers who don't push courses."),
    ("这是我每天跑步的公园。", "where", "This is the park where I run every day."),
    ("我弄丢了开办公室门的那把钥匙。", "that", "I lost the key that opens the office door."),
    ("你还记得我们第一次见面的那家餐厅吗？", "where", "Do you remember the restaurant where we first met?"),
    ("这就是我每天带饭的原因。", "why", "This is the reason why I bring lunch every day."),
    ("昨天帮我搬行李的那个女生是我同学。", "who", "The girl who helped me carry my luggage yesterday is my classmate."),
]

PART4 = [
    (
        "The man which lives next door is a doctor.",
        "The man who lives next door is a doctor.",
        "which → who：先行词是人。",
    ),
    (
        "This is the book who I told you about.",
        "This is the book that / which I told you about.",
        "who → that / which：先行词是物。",
    ),
    (
        "The teacher, that I met yesterday, is very friendly.",
        "The teacher, whom I met yesterday, is very friendly.",
        "非限定性定语从句不用 that。",
    ),
    (
        "I know the girl whose her mother is a singer.",
        "I know the girl whose mother is a singer.",
        "whose 后面不再加 her。",
    ),
    (
        "This is the house where I lived in.",
        "This is the house where I lived. / This is the house that I lived in.",
        "where 和 in 不能重复使用。",
    ),
    (
        "The movie that we saw it last night was great.",
        "The movie that we saw last night was great.",
        "从句里去掉多余的 it。",
    ),
]


# ═══════════════════════════════════════════════════════════════════════
#  HTML / CSS — black & white, clean worksheet style
# ═══════════════════════════════════════════════════════════════════════

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Helvetica Neue', 'Helvetica', 'Arial', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    width: 210mm;
    background: #ffffff;
    color: #1a1a1a;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    line-height: 1.5;
    font-size: 12px;
}

.page {
    width: 210mm;
    height: 297mm;
    padding: 12mm 17mm 11mm 17mm;
    position: relative;
    overflow: hidden;
    background: #ffffff;
}

.page-break { page-break-before: always !important; break-before: always !important; }

/* ── Title ── */
.title-area {
    margin-bottom: 6px;
    padding-bottom: 5px;
    border-bottom: 2.5px solid #000000;
}
.main-title {
    font-size: 25px;
    font-weight: 800;
    color: #000000;
    letter-spacing: -0.3px;
}
.sub-title {
    font-size: 10.5px;
    color: #666666;
    margin-top: 2px;
}

/* ── Grammar reference box ── */
.grammar-box {
    border: 1px dashed #888888;
    background: #f6f6f6;
    padding: 7px 10px;
    font-size: 10.5px;
    line-height: 1.65;
    margin-bottom: 8px;
}
.grammar-box b { font-size: 10.5px; }
.grammar-box .row { display: block; }

/* ── Part header ── */
.part-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 8px 0 2px 0;
}
.part-tag {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    background: #000000;
    color: #ffffff;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.4px;
    flex-shrink: 0;
}
.part-label {
    font-size: 13.5px;
    font-weight: 700;
    color: #000000;
}
.part-desc {
    font-size: 10px;
    color: #666666;
    margin-bottom: 4px;
    padding-left: 3px;
    line-height: 1.4;
}

/* ── Question item ── */
.q-item {
    padding: 2.5px 0 3.5px 4px;
    font-size: 11.5px;
    color: #1a1a1a;
}
.q-num {
    font-weight: 700;
    color: #000000;
    margin-right: 4px;
}
.q-src {
    display: block;
    color: #444444;
    padding-left: 18px;
    line-height: 1.5;
}
.q-hint {
    color: #999999;
    font-size: 10px;
    padding-left: 18px;
}
.blank-line {
    margin: 3px 0 2px 18px;
    width: 78%;
    border-bottom: 1px dotted #aaaaaa;
    height: 9px;
}
.gap { color: #000000; font-weight: 700; letter-spacing: 1px; }

/* ── Answer key ── */
.ans-section { margin-bottom: 6px; }
.ans-header {
    font-size: 11.5px;
    font-weight: 800;
    color: #000000;
    margin: 6px 0 2px 0;
    padding-bottom: 2px;
    border-bottom: 1.5px solid #000000;
}
.ans-item {
    font-size: 10.8px;
    line-height: 1.55;
    padding: 1.5px 0 1.5px 4px;
    color: #1a1a1a;
}
.ans-item .ans-num { font-weight: 700; margin-right: 4px; }
.ans-item .note { color: #777777; font-size: 9.8px; display: block; padding-left: 16px; }
.ans-inline { font-size: 10.8px; line-height: 1.7; padding: 2px 0 2px 4px; }

/* ── Footer ── */
.footer {
    position: absolute;
    bottom: 7mm;
    right: 17mm;
    font-size: 8px;
    color: #999999;
    font-weight: 600;
    letter-spacing: 0.5px;
}
"""


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _page_open(page_num: int, main_title: str, sub_title: str) -> str:
    cls = "page page-break" if page_num > 1 else "page"
    parts = [f'<div class="{cls}">\n']
    parts.append('  <div class="title-area">\n')
    parts.append(f'    <div class="main-title">{_escape_html(main_title)}</div>\n')
    parts.append(f'    <div class="sub-title">{_escape_html(sub_title)}</div>\n')
    parts.append("  </div>\n")
    return "".join(parts)


def _page_close(page_num: int) -> str:
    return f'  <div class="footer">{page_num}/4</div>\n</div>\n'


def _part_header(tag: str, label: str, desc: str) -> str:
    return (
        f'  <div class="part-header"><span class="part-tag">{_escape_html(tag)}</span>'
        f'<span class="part-label">{_escape_html(label)}</span></div>\n'
        f'  <div class="part-desc">{_escape_html(desc)}</div>\n'
    )


def _build_exercise_page(
    page_num: int,
    main_title: str,
    sub_title: str,
    grammar_box: str | None,
    blocks: list[tuple[str, str, str, list]],
) -> str:
    html = _page_open(page_num, main_title, sub_title)
    if grammar_box:
        html += f'  <div class="grammar-box">{grammar_box}</div>\n'
    for tag, label, desc, items in blocks:
        html += _part_header(tag, label, desc)
        for i, item in enumerate(items, 1):
            html += f'  <div class="q-item"><span class="q-num">{i}.</span> {item}</div>\n'
    html += _page_close(page_num)
    return html


def build_html() -> str:
    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="UTF-8">',
        "<title>Relative Clause Practice</title>",
        "<style>",
        CSS,
        "</style>",
        "</head>",
        "<body>",
    ]

    # ── Page 1: Part 1 ──
    grammar = (
        "<b>Relative words at a glance（关系词速查）</b>"
        '<span class="row"><b>who</b> 人·主语　 <b>whom</b> 人·宾语　 <b>whose</b> 谁的·表所属</span>'
        '<span class="row"><b>which / that</b> 物　 <b>where</b> 地点　 <b>when</b> 时间　 <b>why</b> 原因</span>'
    )
    p1_items = []
    for src1, src2, _ans in PART1:
        p1_items.append(
            f'<span>{_escape_html(src1)}</span>'
            f'<span class="q-src">{_escape_html(src2)}</span>'
            '<div class="blank-line"></div>'
        )
    parts.append(
        _build_exercise_page(
            1,
            "Relative Clause",
            "定语从句 · 从零开始练习（Practice from Zero）",
            grammar,
            [
                (
                    "PART 1",
                    "Join the Sentences · 合并句子",
                    "Turn the second sentence into a relative clause. 把第二句变成定语从句，合并成一个句子。",
                    p1_items,
                )
            ],
        )
    )

    # ── Page 2: Part 2 ──
    p2_items = []
    for sentence, _ans in PART2:
        head, _sep, tail = sentence.partition("___")
        rendered = (
            _escape_html(head)
            + '<span class="gap">______</span>'
            + _escape_html(tail)
        )
        p2_items.append(
            f"<span>{rendered}</span>"
            '<div class="blank-line"></div>'
        )
    parts.append(
        _build_exercise_page(
            2,
            "Relative Clause",
            "Part 2 · 选词填空",
            None,
            [
                (
                    "PART 2",
                    "Choose the Correct Word · 选词填空",
                    "Options: who / whom / whose / which / that / where / when / why. Some blanks have more than one correct answer.",
                    p2_items,
                )
            ],
        )
    )

    # ── Page 3: Part 3 + Part 4 ──
    p3_items = [
        f'<span>{_escape_html(cn)}</span>'
        f'<span class="q-hint">hint: use “{_escape_html(hint)}”</span>'
        '<div class="blank-line"></div>'
        for cn, hint, _en in PART3
    ]
    p4_items = [
        f'<span>{_escape_html(wrong)}</span>'
        '<div class="blank-line"></div>'
        for wrong, _correct, _note in PART4
    ]
    parts.append(
        _build_exercise_page(
            3,
            "Relative Clause",
            "Part 3 · 翻译 & Part 4 · 改错",
            None,
            [
                (
                    "PART 3",
                    "Translate into English · 翻译",
                    "Use the relative word in the hint. 必须使用提示中的关系词。",
                    p3_items,
                ),
                (
                    "PART 4",
                    "Correct the Mistakes · 改错",
                    "Each sentence has one mistake. 每句只有一处错误，请改正。",
                    p4_items,
                ),
            ],
        )
    )

    # ── Page 4: Answer key ──
    html = _page_open(4, "Relative Clause", "Answer Key · 参考答案")
    html += '  <div class="ans-section">'
    html += '    <div class="ans-header">PART 1 · Join the Sentences</div>'
    for i, (_s1, _s2, ans) in enumerate(PART1, 1):
        html += f'    <div class="ans-item"><span class="ans-num">{i}.</span>{_escape_html(ans)}</div>'
    html += "  </div>"

    html += '  <div class="ans-section">'
    html += '    <div class="ans-header">PART 2 · Choose the Correct Word</div>'
    inline = "　".join(f"{i}. {_escape_html(ans)}" for i, (_s, ans) in enumerate(PART2, 1))
    html += f'    <div class="ans-inline">{inline}</div>'
    html += "  </div>"

    html += '  <div class="ans-section">'
    html += '    <div class="ans-header">PART 3 · Translate into English</div>'
    for i, (_cn, _hint, en) in enumerate(PART3, 1):
        html += f'    <div class="ans-item"><span class="ans-num">{i}.</span>{_escape_html(en)}</div>'
    html += "  </div>"

    html += '  <div class="ans-section">'
    html += '    <div class="ans-header">PART 4 · Correct the Mistakes</div>'
    for i, (_wrong, correct, note) in enumerate(PART4, 1):
        html += (
            f'    <div class="ans-item"><span class="ans-num">{i}.</span>{_escape_html(correct)}'
            f'<span class="note">{_escape_html(note)}</span></div>'
        )
    html += "  </div>"

    html += _page_close(4)
    parts.append(html)

    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts)


def main():
    pdf_path = PDF_DIR / "09-Relative Clause.pdf"
    html_path = MD_DIR / "_relative_clause.html"

    print("Generating HTML...")
    html_path.write_text(build_html(), encoding="utf-8")
    print(f"  HTML written to {html_path}")

    print("Exporting PDF (this may take a few seconds)...")
    if export_pdf(html_path, pdf_path):
        print(f"  PDF saved to {pdf_path}")
    else:
        print("  Playwright not available: PDF skipped (HTML is ready).")
    print("Done.")


if __name__ == "__main__":
    main()
