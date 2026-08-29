#!/usr/bin/env python3
"""Build two polished versions of MD/Visa_Q&A_Revised_A1.md.

Version 1: two-page A4 PDF  -> PDF/Visa Q&A A1（两页A4版）.pdf
Version 2: mobile-portrait Q&A cards (2 questions per card)
                                -> MD/Visa Q&A A1（手机卡片版）.html

All wording is parsed from the source markdown; nothing is added or rewritten.
"""

import html
import re
from pathlib import Path

ROOT = Path(r"F:\AIProject\ESLBeginner")
SRC = ROOT / "MD" / "Visa_Q&A_Revised_A1.md"
PDF_OUT = ROOT / "PDF" / "Visa Q&A A1（两页A4版）.pdf"
HTML_OUT = ROOT / "MD" / "Visa Q&A A1（手机卡片版）.html"
PREVIEW = ROOT / "build" / "preview"

NAVY = "#123B5E"
AMBER = "#C08A2D"
INK = "#1F2933"
MUTED = "#66737E"


# ---------------------------------------------------------------- parsing

def parse_md(text: str):
    title = None
    note = None
    sections = []  # [{"heading": str, "rows": [(q, a, s), ...]}]
    tips = []      # raw numbered lines
    cur = None
    for raw in text.splitlines():
        ln = raw.strip()
        if ln.startswith("# ") and not ln.startswith("## "):
            title = ln[2:].strip()
        elif ln.startswith("> "):
            note = ln[2:].strip().replace("**", "")
        elif ln.startswith("## "):
            cur = {"heading": ln[3:].strip(), "rows": []}
            sections.append(cur)
        elif ln.startswith("|") and cur is not None:
            cells = [c.strip().replace("**", "").replace("*", "")
                     for c in ln.strip().strip("|").split("|")]
            if len(cells) >= 3 and cells[0] and not cells[0].startswith(":") \
                    and cells[0] != "问题":
                cur["rows"].append(tuple(cells[:3]))
        elif re.match(r"^\d+\.\s", ln):
            tips.append(ln)
    return title, note, sections, tips


def esc(s: str) -> str:
    return html.escape(s, quote=False)


# ---------------------------------------------------------------- PDF

def build_pdf(title, sections) -> int:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (HRFlowable, KeepTogether, PageBreak,
                                    Paragraph, SimpleDocTemplate, Spacer,
                                    Table, TableStyle)

    pdfmetrics.registerFont(TTFont("MSYH", r"C:\Windows\Fonts\msyh.ttc",
                                   subfontIndex=0))
    pdfmetrics.registerFont(TTFont("MSYH-B", r"C:\Windows\Fonts\msyhbd.ttc",
                                   subfontIndex=0))

    c_navy = colors.HexColor(NAVY)
    c_amber = colors.HexColor(AMBER)
    c_ink = colors.HexColor(INK)
    c_muted = colors.HexColor(MUTED)
    c_line = colors.HexColor("#D9E2EA")

    W, H = A4
    LM = RM = 34
    CW = W - LM - RM

    def st(name, **kw):
        base = dict(fontName="MSYH", fontSize=8.3, leading=10.8, textColor=c_ink)
        base.update(kw)
        return ParagraphStyle(name, **base)

    s_title = st("title", fontName="MSYH-B", fontSize=18, leading=23,
                 textColor=c_navy, wordWrap="CJK")
    s_sec = st("sec", fontName="MSYH-B", fontSize=13.5, leading=17,
               textColor=c_navy, wordWrap="CJK")
    s_th = st("th", fontName="MSYH-B", fontSize=9, leading=11.4,
              textColor=colors.white, wordWrap="CJK")
    s_q = st("q", fontName="MSYH-B", fontSize=9.2, leading=12.2,
             textColor=c_navy)
    s_a = st("a", fontSize=9.2, leading=12.2, textColor=c_ink)
    s_s = st("s", fontSize=8.5, leading=11.3, textColor=c_muted,
             wordWrap="CJK")

    def sec_head(num, heading):
        p = Paragraph(
            f'<font name="MSYH-B" color="{AMBER}">{num}</font>'
            f'<font color="#C9D6E0">　</font>'
            f'<font name="MSYH-B" color="{NAVY}">{esc(heading)}</font>',
            s_sec)
        rule = HRFlowable(width="100%", thickness=0.7, color=c_line,
                          spaceBefore=3, spaceAfter=8)
        return KeepTogether([p, rule])

    def qa_table(rows):
        data = [[Paragraph(esc("问题"), s_th),
                 Paragraph(esc("推荐回答（A1 水平）"), s_th),
                 Paragraph(esc("策略要点"), s_th)]]
        for q, a, s in rows:
            data.append([Paragraph(esc(q), s_q),
                         Paragraph(esc(a), s_a),
                         Paragraph(esc(s), s_s)])
        t = Table(data, colWidths=[136, 221, CW - 136 - 221], repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_navy),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#F7FAFC")]),
            ("GRID", (0, 0), (-1, -1), 0.5, c_line),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.8),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ]))
        return t

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("MSYH", 7.5)
        canvas.setFillColor(c_muted)
        canvas.drawCentredString(W / 2, 18, f"{doc.page} / 2")
        canvas.restoreState()

    story = []
    story.append(Paragraph(esc(title), s_title))
    story.append(Spacer(1, 5))
    story.append(HRFlowable(width=38, thickness=3, color=c_amber,
                            spaceBefore=2, spaceAfter=14))

    s1 = sections[0]
    story.append(Spacer(1, 18))
    story.append(sec_head("01", s1["heading"]))
    story.append(qa_table(s1["rows"]))
    story.append(PageBreak())

    s2 = sections[1]
    story.append(sec_head("02", s2["heading"]))
    story.append(qa_table(s2["rows"]))

    doc = SimpleDocTemplate(str(PDF_OUT), pagesize=A4,
                            leftMargin=LM, rightMargin=RM,
                            topMargin=38, bottomMargin=30,
                            title="美国签证面试问答",
                            author="ESLBeginner")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return PDF_OUT


# ---------------------------------------------------------------- cards HTML

def build_html(title, note, sections) -> Path:
    card_seq = 0
    sections_html = []
    for sec in sections:
        cards = []
        for i in range(0, len(sec["rows"]), 2):
            card_seq += 1
            qas = []
            for q, a, s in sec["rows"][i:i + 2]:
                qas.append(
                    f'<div class="qa">'
                    f'<div class="q"><span class="tag q">Q</span>'
                    f'<p class="qtext">{esc(q)}</p></div>'
                    f'<div class="a"><span class="tag a">A</span>'
                    f'<p class="atext">{esc(a)}</p></div>'
                    f'<div class="strat"><span class="slabel">策略要点</span>'
                    f'<span class="stext">{esc(s)}</span></div>'
                    f'</div>')
            cards.append(
                f'<div class="card">'
                f'<div class="card-head"><span class="sec-tag">'
                f'{esc(sec["heading"])}</span>'
                f'<span class="card-no">{card_seq:02d}</span></div>'
                f'{"".join(qas)}'
                f'</div>')
        sections_html.append(
            f'<section><div class="sec-label">'
            f'{esc(sec["heading"])}</div>{"".join(cards)}</section>')

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>美国签证面试问答 · 卡片版</title>
<style>
:root{{
  --navy:#123B5E; --navy2:#1B4F79; --amber:#C08A2D; --amber-soft:#F7EFDF;
  --ink:#1F2933; --muted:#66737E; --paper:#F4F1EA; --card:#FFFFFF;
  --line:#E5DFD3; --line2:#D8E2EA;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{-webkit-text-size-adjust:100%}}
body{{
  font-family:"Inter","Segoe UI","PingFang SC","Microsoft YaHei",system-ui,sans-serif;
  background:var(--paper); color:var(--ink);
  -webkit-font-smoothing:antialiased; line-height:1.5;
}}
.wrap{{max-width:480px;margin:0 auto;padding:18px 16px 44px}}
header{{background:var(--navy);border-radius:20px;padding:20px 18px 16px;
  box-shadow:0 10px 26px rgba(18,59,94,.18)}}
h1{{font-size:20px;line-height:1.42;color:#fff;font-weight:800}}
.rule{{width:42px;height:4px;background:var(--amber);border-radius:2px;margin:13px 0 12px}}
section{{margin-top:22px}}
.sec-label{{
  position:sticky;top:10px;z-index:5;display:inline-flex;align-items:center;
  background:var(--navy);color:#fff;font-weight:700;font-size:13.5px;
  padding:7px 14px;border-radius:999px;box-shadow:0 5px 12px rgba(18,59,94,.20);
}}
.card{{
  background:var(--card);border:1px solid var(--line);border-radius:18px;
  box-shadow:0 6px 18px rgba(31,41,51,.06);margin:14px 0;
}}
.card-head{{
  display:flex;justify-content:space-between;align-items:center;
  padding:13px 16px 11px;
}}
.sec-tag{{font-size:12px;font-weight:700;color:var(--navy2);letter-spacing:.2px}}
.card-no{{font-size:12.5px;font-weight:800;color:var(--amber);letter-spacing:.5px}}
.qa{{padding:13px 16px;border-top:1px dashed var(--line)}}
.qa:first-of-type{{border-top:none}}
.q,.a{{display:flex;gap:10px}}
.a{{margin-top:11px}}
.tag{{
  flex:0 0 auto;width:26px;height:26px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:800;color:#fff;margin-top:2px;
}}
.tag.q{{background:var(--navy)}}
.tag.a{{background:var(--amber)}}
.qtext{{font-weight:700;font-size:15px;line-height:1.45;color:var(--navy)}}
.atext{{font-size:15px;line-height:1.55}}
.strat{{
  margin:11px 0 2px 36px;background:var(--amber-soft);border-radius:10px;
  padding:8px 11px;font-size:12.5px;line-height:1.55;color:#7A5B1E;
}}
.slabel{{font-weight:700;margin-right:6px}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>{esc(title)}</h1>
    <div class="rule"></div>
  </header>
  {"".join(sections_html)}
</div>
</body>
</html>"""
    HTML_OUT.write_text(page, encoding="utf-8")
    return HTML_OUT


if __name__ == "__main__":
    text = SRC.read_text(encoding="utf-8")
    title, note, sections, tips = parse_md(text)
    # requested content rules for the two versions:
    title = "美国签证面试问答"
    note = None          # drop the 使用说明 blockquote
    tips = []            # drop the 通用面试小贴士 section
    sections = [s for s in sections if s["rows"]]   # drop empty sections
    for sec in sections:
        sec["rows"] = [
            (q.replace("（新增）", "").replace("(新增)", "").strip(), a, s)
            for q, a, s in sec["rows"]]

    # PDF
    build_pdf(title, sections)
    try:
        import pymupdf
        doc = pymupdf.open(PDF_OUT)
        print(f"PDF pages: {doc.page_count} -> {PDF_OUT}")
        PREVIEW.mkdir(parents=True, exist_ok=True)
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(dpi=140)
            pix.save(PREVIEW / f"visa_pdf_p{i}.png")
        doc.close()
    except Exception as exc:
        print("preview failed:", exc)

    # Cards HTML
    build_html(title, note, sections)
    print("HTML cards ->", HTML_OUT)
