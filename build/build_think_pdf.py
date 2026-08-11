#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build PDF/to Think in English Naturally 英语思维.pdf from the source docx.

Pipeline:  MD/to Think in English Naturally 英语思维.docx
        ->  build/tex/to Think in English Naturally 英语思维.md (raw-LaTeX blocks)
        ->  pandoc + xelatex/tectonic  ->  PDF/to Think in English Naturally 英语思维.pdf

Design follows the current ESLBeginner print standard (Real Life Expressions):
all-black body, larger type, generous spacing, one scene per page. Every
sentence is split into >= 3 sense-group chunks: the first chunk is bold,
the last chunk is underlined, and the middle stays regular.

Usage:
    python build/build_think_pdf.py            # build PDF
    python build/build_think_pdf.py --png      # also render page previews
"""

import re
import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))

import build_pdfs as _bp  # noqa: E402
from build_pdfs import (  # noqa: E402
    GEN_DIR,
    PDF_DIR,
    PREVIEW,
    T_pagebreak,
    pandoc_pdf,
    raw,
)

# Pandoc / TeX engine: prefer the original Windows paths when present,
# otherwise prefer xelatex (TeX Live) and fall back to tectonic.
_PANDOC_WIN = Path(r"C:\Program Files\Pandoc\pandoc.exe")
_MIKTEX_BIN = Path(r"C:\Users\ZZC\AppData\Local\Programs\MiKTeX\miktex\bin\x64")
_bp.PANDOC = str(_PANDOC_WIN) if _PANDOC_WIN.exists() else (shutil.which("pandoc") or "pandoc")
_bp.MIKTEX_BIN = str(_MIKTEX_BIN) if _MIKTEX_BIN.exists() else ""
if not _MIKTEX_BIN.exists():
    _bp.PDF_ENGINE = "xelatex" if shutil.which("xelatex") else (
        "tectonic" if shutil.which("tectonic") else "xelatex"
    )

DOCX = ROOT / "MD" / "to Think in English Naturally 英语思维.docx"
PDF_OUT = PDF_DIR / "to Think in English Naturally 英语思维.pdf"

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


# ---------------------------------------------------------------- docx -> text
def docx_paragraphs(path: Path) -> list[str]:
    """Extract one plain-text string per body paragraph from a .docx file."""
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    paras = []
    for p in root.iter(f"{W_NS}p"):
        parts = []
        for node in p.iter():
            if node.tag == f"{W_NS}t":
                parts.append(node.text or "")
            elif node.tag == f"{W_NS}tab":
                parts.append(" ")
            elif node.tag == f"{W_NS}br":
                parts.append(" ")
        paras.append("".join(parts).strip())
    return paras


_SENT_END = re.compile(r"[.!?]([\u2019'\"]?)$")


def parse(lines: list[str]) -> dict:
    """Turn docx paragraphs into {title, sections: [{title, items: [...]}]}."""
    clean = [s for s in (ln.strip() for ln in lines) if s]
    doc = {"title": clean[0], "sections": []}
    cur = None
    for line in clean[1:]:
        if _SENT_END.search(line):
            if cur is None:
                raise ValueError(f"句子出现在任何场景标题之前: {line!r}")
            cur["items"].append(line)
        else:
            cur = {"title": line, "items": []}
            doc["sections"].append(cur)
    return doc


# ---------------------------------------------------------------- chunking
# "Think in English" 每句按意群切成 >= 3 个 chunk，视觉上首块加粗、末块下划线。
# 规则：短语动词不拆（PHRASAL），状语/介词短语从尾部切（ANCHOR_RX），
# 主语+助动词框架从头部切（FRAMES / NP_START），兜底按 copula/限定词切分。

PHRASAL = {
    "put on", "putting on", "turn off", "turning off", "turn on", "get off",
    "take off", "throw away", "throwing away", "write down", "writing down",
    "back up", "backing up", "scroll through", "scrolling through", "look for",
    "looking for", "wait for", "waiting for", "listen to", "listening to",
    "get to", "set up", "setting up", "clean up", "cleaning up", "hang up",
    "hanging up", "fold up", "folding up", "check in", "work out", "go out",
    "wake up", "grow up", "show up", "give up", "pick up", "find out",
    "point out", "try on", "go on", "come back", "go back", "get back",
    "go over", "look at", "looking at", "talk about", "talking about",
    "think about", "thinking about", "think of", "care about", "hear about",
    "know about", "agree with", "deal with", "meet up with", "catch up with",
    "get along with", "make up", "work on", "focus on", "rely on", "depend on",
    "pay for", "paying for", "ask for", "asking for", "apply for", "search for",
    "check for", "prepare for", "preparing for", "talk to", "speak to",
    "belong to", "move to", "return to", "reply to", "responding to",
    "apologize to", "lead to", "add to", "refer to", "going to", "need to",
    "want to", "have to", "used to", "supposed to", "try to", "trying to",
    "start to", "begin to", "learn to", "remember to", "forget to", "forgot to",
    "decide to", "plan to", "hope to", "like to", "love to", "hate to",
    "stop to", "continue to", "manage to", "afford to", "choose to",
    "offer to", "refuse to", "agree to", "seem to", "happen to", "tend to",
    "about to", "in order to", "so as to", "up to", "down to", "close to",
    "next to", "due to", "similar to", "different from", "away from", "far from",
    "out of", "in front of", "instead of", "because of", "a lot of",
    "lots of", "plenty of", "kind of", "sort of", "type of", "pair of",
    "cup of", "glass of", "bottle of", "piece of", "bit of", "little bit of",
    "sure about", "nervous about", "worried about", "excited about",
    "curious about", "anxious about", "happy about", "frustrated with",
    "stressed with", "tired of", "proud of", "grateful for", "thanks for",
    "good at", "bad at", "late for", "ready for", "feel like", "look like",
    "sound like", "smell like", "taste like", "seem like", "go for",
    "come for", "run for", "sign up for", "stop for", "leave for", "head for",
    "aim for", "try for", "study for", "work for", "hold on", "hang on",
    "come on", "carry on", "keep on", "move on", "turn down", "turn up",
    "calm down", "slow down", "settle down", "sit down", "stand up", "get up",
    "get out of", "get out", "head out", "step out", "eat out", "dine out",
    "stay focused", "set my alarm", "do the laundry", "wash the dishes",
    "start cleaning", "finish this report", "finish this task",
    "clean the house", "clean my desk", "prepare my outfit",
    "set realistic goals", "make my bed", "pack my bag", "take a shower",
    "take a walk", "take a break", "take a nap", "take a photo", "take notes",
    "take small steps", "grab a", "grab some", "grab my", "grab the",
    "check my", "check the", "check if", "check on", "check out",
    "check my progress", "check my schedule", "check today", "study English",
    "practice speaking", "practice yoga", "speak English", "write a",
    "write in", "write down", "let me check", "let me know", "let me think",
    "I can find", "just in", "in case", "eating together", "for a while",
}

_ANCHOR_TEXTS = [
    "just in case", "this morning", "this evening", "this weekend", "every day",
    "right now", "at the moment", "on the way", "next time", "for a while",
    "for a minute", "for a moment", "for a few minutes", "for fifteen minutes",
    "for 30 minutes", "in 10 minutes", "for a short walk", "for a short nap",
    "for a short rest", "for some fresh air", "for a walk", "for a change",
    "for fun", "for help", "for lunch", "for dinner", "for tea", "for breakfast",
    "for the party", "for the occasion", "for the event", "for tomorrow",
    "for today", "for everyone", "for coming", "for my health",
    "for my mind and body", "for my friend", "for my friends", "for my family",
    "for clarification", "rather than", "instead of", "out of", "because",
    "while", "when", "until", "before", "after", "if", "that", "what", "and",
    "or", "but", "so", "too", "than", "like", "with", "about", "at", "on",
    "in", "for", "by", "from", "during", "through", "around", "under", "over",
    "without", "into", "near", "next to", "across", "against", "to", "again",
    "yet", "now", "today", "tonight", "tomorrow", "later", "soon", "already",
    "outside", "inside", "early", "quickly", "slowly", "carefully", "together",
    "faster", "first", "more", "alone", "here", "well",
]
# 词边界锚点：锚点本身必须独立成词（前面是行首或空格，后面不是单词字符）
ANCHOR_RX = [
    (t, re.compile(rf"(?:^|\s){re.escape(t)}(?![\w’])"))
    for t in sorted(_ANCHOR_TEXTS, key=len, reverse=True)
]

COPULA = {
    "is", "are", "was", "were", "looks", "look", "feels", "feel", "seems",
    "seem", "smells", "smell", "tastes", "taste", "sounds", "sound", "makes",
    "make", "has", "have", "went", "goes", "go", "does", "did", "changes",
    "took", "becomes", "become", "gets", "get", "turns", "turn", "isn’t",
    "aren’t", "wasn’t", "weren’t", "looks like", "feels like",
}

FRAMES = [
    "That movie I watched", "I’m looking for", "I’m thinking about",
    "I’m going to", "I’m feeling", "I’m not", "I’m just", "I’m really",
    "I’m a bit", "I’m a little", "I’m so", "I’m too", "I’m proud",
    "I’m worried", "I’m grateful", "I’m excited", "I’m nervous",
    "I’m curious", "I’m anxious", "I’m frustrated", "I’m happy", "I’m tired",
    "I’m hungry", "I’m lonely", "I’m calm", "I’m motivated", "I’m relaxed",
    "I’m sleepy", "I’m confident", "I’m stressed", "I’m", "I’ll just", "I’ll",
    "I’d better", "I’d", "I’ve", "I can’t", "I don’t", "I can", "I could",
    "I should", "I need to", "I want to", "I have to", "I think", "I hope",
    "I wonder", "I wish", "I love", "I feel", "I need", "I want", "I miss",
    "I almost", "I learned", "I forgot", "I spilled", "I’m enjoying",
    "I’m decorating", "I’m writing", "I’m planning", "I’m preparing",
    "I’m baking", "I’m buying", "I’m inviting", "I’m helping", "I’m closing",
    "I’m calling", "I’m replying", "I’m sharing", "I’m watching",
    "I’m listening", "I’m reading", "I’m dancing", "I’m doing", "I’m tracking",
    "I’m practicing", "I’m resting", "I’m eating", "I’m drinking", "I’m having",
    "I’m checking", "I’m sending", "I’m joining", "I’m learning",
    "I’m updating", "I’m downloading", "I’m scrolling", "I’m taking",
    "I’m making", "I’m washing", "I’m cleaning", "I’m folding",
    "I’m organizing", "I’m opening", "I’m boiling", "I’m brushing",
    "I’m putting", "I’m waiting", "I’m jogging", "I’m exercising", "I’m going",
    "I’m getting", "I’m keeping", "I’m saying", "I’m preparing", "I’m setting",
    "I’m cooking", "I’m baking", "I’m trying", "I’m looking", "I’m about",
    "I’m done", "I’m out", "I’m reading", "Let’s", "Let me", "Time to",
    "It’s", "It feels", "It looks", "It’s too", "It’s so", "Did I", "Did she",
    "Do I", "Should I", "Where did I", "What should I", "What time",
    "What song", "What a", "Where’s", "How", "What", "Where", "Why", "When",
    "Wow,", "Okay,", "Oops,", "Finally,", "Goodnight,", "Lunch break", "Home",
    "Communication", "Relaxing", "Staying active", "Eating together", "Today",
    "tomorrow", "I’m thinking", "I’m waiting", "I’m checking", "I’m putting",
    "I hope the bus", "I hope it", "I wish the ride", "I think this brand",
    "I think I", "I feel lucky", "I feel sleepy", "I’m grateful",
    "I’m a little",
]

DET = re.compile(
    r"\b(my|your|his|her|its|our|their|the|a|an|some|another|this|that|"
    r"these|those|something|anything|everything|nothing|it|them|him|me|us|"
    r"more|ten|fifteen|thirty|one|two|few)\b"
)
NP_START = re.compile(r"^(The|This|That|These|My|Our|Your|A)\b", re.I)


def _anchor_protected(pos: int, s: str, anchor_text: str) -> bool:
    """True if the anchor directly continues a protected phrasal verb."""
    aw = anchor_text.split()[0]
    words = s[:pos].rstrip().split()
    for n in (2, 3):
        if len(words) >= n - 1:
            cand = " ".join(words[-(n - 1):] + [aw])
            if cand in PHRASAL:
                return True
    return False


def split_tail(s: str):
    """Split off the rightmost adverb/prepositional/clause tail."""
    best = None  # (end, len, head, tail) — rightmost wins, then longest
    for text, rx in ANCHOR_RX:
        m = rx.search(s)
        if not m:
            continue
        pos = m.start()
        head = s[:pos].rstrip()
        tail = s[pos:].strip()
        if not head or not tail or _anchor_protected(pos, s, text):
            continue
        cand = (m.end(), len(text), head, tail)
        if best is None or cand > best:
            best = cand
    if best is None:
        return None
    return best[2], best[3]


def split_frame(s: str):
    """Split off the leading subject/auxiliary frame."""
    for f in sorted(FRAMES, key=len, reverse=True):
        if s == f or s.startswith(f + " "):
            return f, s[len(f):].strip()
    m = NP_START.match(s)
    if m:
        words = s.split()
        frame = [words[0]]
        for w in words[1:]:
            if w.rstrip(".,!?").lower() in COPULA:
                break
            frame.append(w)
            if len(frame) >= 4:
                break
        rest = s[len(" ".join(frame)):].strip()
        if rest:
            return " ".join(frame), rest
    return None, s


def fallback_split(chunks: list[str]) -> list[str] | None:
    """Split the longest chunk (ties prefer the later, verb-phrase side)."""
    idx = max(range(len(chunks)), key=lambda i: (len(chunks[i].split()), i))
    c = chunks[idx]
    words = c.split()
    if len(words) < 2:
        return None
    for i in range(1, len(words)):  # before a copula
        if words[i].rstrip(".,!?").lower() in COPULA:
            chunks[idx:idx + 1] = [" ".join(words[:i]), " ".join(words[i:])]
            return chunks
    for i in range(1, len(words)):  # before a determiner
        if DET.match(words[i]):
            chunks[idx:idx + 1] = [" ".join(words[:i]), " ".join(words[i:])]
            return chunks
    if NP_START.match(words[0]):  # noun phrase at chunk start
        cut = min(2, len(words) - 1)
        chunks[idx:idx + 1] = [" ".join(words[:cut]), " ".join(words[cut:])]
        return chunks
    if len(words) >= 3:  # after the first word
        chunks[idx:idx + 1] = [words[0], " ".join(words[1:])]
        return chunks
    if len(words) == 2:  # last resort
        chunks[idx:idx + 1] = [words[0], words[1]]
        return chunks
    return None


def chunk_sentence(s: str) -> list[str]:
    """Split one sentence into >= 3 sense-group chunks."""
    # 逗号/破折号保留在前一个 chunk 上（"Okay," / "pushed me —"）
    pieces = re.split(r"(\s*[,—]\s*)", s)
    segs = []
    i = 0
    while i < len(pieces):
        text = pieces[i]
        if i + 1 < len(pieces) and pieces[i + 1].strip():
            sep = pieces[i + 1].strip()
            if sep == "—":  # 英文破折号两侧有空格
                text = text.rstrip() + " " + sep
            else:
                text = text.rstrip() + sep
            i += 2
        else:
            i += 1
        if text:
            segs.append(text)
    chunks = []
    for seg in segs:
        cur = seg
        tails = []
        for _ in range(6):
            r = split_tail(cur)
            if r is None:
                break
            tails.insert(0, r[1])
            cur = r[0]
        parts = [cur] + tails
        if parts:
            fr, rest = split_frame(parts[0])
            if fr and rest:
                parts = [fr, rest] + parts[1:]
        chunks.extend(parts)
    guard = 0
    while len(chunks) < 3 and guard < 12:
        r = fallback_split(chunks)
        if r is None:
            break
        chunks = r
        guard += 1
    return chunks


# ---------------------------------------------------------------- latex emit
def l_plain(s: str) -> str:
    """Escaped plain text — no markdown emphasis in this handbook.

    Em dashes are emitted as TeX ligatures (---) so they render in the Latin
    font with proper spacing instead of being routed through xeCJK as CJK
    punctuation (which would swallow the following space). The curly
    apostrophe (U+2019) is also a CJK-class punctuation in xeCJK and renders
    with too much internal spacing in "I'm" — replacing it with the ASCII
    apostrophe keeps it in the Latin font (xelatex prints it as a proper
    right single quotation mark).
    """
    return _bp.esc_latex(s.replace("\u2014", "---").replace("\u2019", "'"))


def build_markdown(doc: dict) -> str:
    out = []
    # 本册要求：全黑正文、加大字号间距（对齐 Real Life Expressions 标准）
    out.append(raw(
        r"\renewcommand{\esltitle}[1]{\par\vspace{4pt}"
        r"{\fontsize{27pt}{32pt}\selectfont\bfseries #1}\par\vspace{14pt}}"
    ))
    out.append(raw(
        r"\newcommand{\eslthinksec}[1]{\par\vspace{14pt}\noindent"
        r"{\fontsize{16pt}{20pt}\selectfont\bfseries #1}\par\vspace{10pt}}"
    ))
    out.append(raw(
        r"\newcommand{\eslthinkitem}[1]{\par\vspace{10pt}\noindent"
        r"{\bodyfont\fontsize{13pt}{20pt}\selectfont #1}\par}"
    ))
    # 全黑正文，不使用灰色
    out.append(raw(r"\definecolor{muted}{HTML}{000000}"))
    out.append(raw(r"\definecolor{faint}{HTML}{000000}"))
    out.append(raw(r"\clubpenalty=8000 \widowpenalty=8000"))

    out.append(raw(rf"\esltitle{{{l_plain(doc['title'])}}}"))
    for i, sec in enumerate(doc["sections"], 1):
        if i > 1:
            out.append(T_pagebreak())
        out.append(raw(f"\\eslthinksec{{{l_plain(sec['title'])}}}"))
        for item in sec["items"]:
            chunks = chunk_sentence(item)
            rendered = []
            for k, c in enumerate(chunks):
                esc = l_plain(c)
                if k == 0:
                    rendered.append(r"{\bfseries " + esc + "}")
                elif k == len(chunks) - 1:
                    rendered.append(r"{\esluline{" + esc + "}}")
                else:
                    rendered.append(esc)
            out.append(raw(r"\eslthinkitem{" + " ".join(rendered) + "}"))
    return "\n".join(out)


# ---------------------------------------------------------------- preview
def previews() -> bool:
    """Render the first few pages to PNG (pymupdf, present in the local venv)."""
    PREVIEW.mkdir(exist_ok=True)
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return False
    pdf_doc = fitz.open(PDF_OUT)
    print(f"pages = {pdf_doc.page_count}")
    for i in range(min(3, pdf_doc.page_count)):
        page = pdf_doc[i]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4))
        png = PREVIEW / f"think_en_{i}.png"
        pix.save(png)
        print(f"[png]  {png}")
    return True


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if not DOCX.exists():
        print(f"[FAIL] 缺少源文件 {DOCX}")
        return 1

    paras = docx_paragraphs(DOCX)
    doc = parse(paras)
    n_sec = len(doc["sections"])
    n_items = sum(len(s["items"]) for s in doc["sections"])
    print(f"解析完成：{n_sec} 个场景 / {n_items} 句")
    if n_sec != 19 or any(len(s["items"]) != 20 for s in doc["sections"]):
        print(f"[warn] 预期 19 场景、每场 20 句，实际 {n_sec} 场景、每场 "
              f"{[len(s['items']) for s in doc['sections']]}", file=sys.stderr)

    body = build_markdown(doc)
    GEN_DIR.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)
    md_out = GEN_DIR / f"{DOCX.stem}.md"
    md_out.write_text(body, encoding="utf-8")

    ok = pandoc_pdf(md_out, PDF_OUT)
    print(f"[{'ok' if ok else 'FAIL'}] {DOCX.name} -> {PDF_OUT.name}")
    if ok and "--png" in sys.argv:
        previews()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
