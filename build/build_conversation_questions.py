#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the ESL Conversation Questions series.

Source:  MD/ESL-Conversation-Questions/<NN-Category-Slug>.md
Output:  PDF/ESL-Conversation-Questions/
             All-Questions.pdf                  every topic, every category
             <NN-Category-Slug>/
                 <NN-MM-Topic-Slug>.pdf         one PDF per topic (10 questions)
                 <NN-Category-Slug>-All.pdf     every topic in the category

Each question line in the source is `N. <English> | <中文>`; a topic is
`## NN <English Title> | <中文标题>` and a category is
`# NN <中文名> <English Name>`.

Usage:
    python build/build_conversation_questions.py            # every category
    python build/build_conversation_questions.py 01         # only category 01
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))

import build_pdfs as build  # noqa: E402
from build_pdfs import l, raw  # noqa: E402

SOURCE_DIR = ROOT / "MD" / "ESL-Conversation-Questions"
OUT_DIR = ROOT / "PDF" / "ESL-Conversation-Questions"
TEX_DIR = ROOT / "build" / "tex"
ADDITIONS = TEX_DIR / "conversation_questions_preamble.tex"
TMP_MD = TEX_DIR / "_cq_tmp.md"

QUESTIONS_PER_TOPIC = 10

CATEGORY_RE = re.compile(r"^#\s+(\d+)\s+(\S+)\s+(.+)$")
TOPIC_RE = re.compile(r"^##\s+(\d+)\s+(.+?)\s*\|\s*(.+)$")
QUESTION_RE = re.compile(r"^(\d+)\.\s+(.+?)\s*\|\s*(.+)$")


# ---------------------------------------------------------------- parsing
def slug(text: str) -> str:
    """`Morning Routines` -> `Morning-Routines` (filename-safe, keeps case)."""
    cleaned = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip()
    return re.sub(r"[\s_]+", "-", cleaned)


def parse_category(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    category = {"num": "", "cn": "", "en": "", "topics": []}
    topic = None
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if (m := CATEGORY_RE.match(line)) and not category["num"]:
            category["num"], category["cn"], category["en"] = m.group(1), m.group(2), m.group(3)
            continue
        if m := TOPIC_RE.match(line):
            topic = {"num": m.group(1), "en": m.group(2), "cn": m.group(3), "questions": []}
            category["topics"].append(topic)
            continue
        if m := QUESTION_RE.match(line):
            if topic is None:
                raise ValueError(f"{path.name}:{lineno}: question before any topic heading")
            topic["questions"].append({"n": m.group(1), "en": m.group(2), "cn": m.group(3)})
            continue
        raise ValueError(f"{path.name}:{lineno}: unrecognized line: {line[:70]}")

    if not category["num"]:
        raise ValueError(f"{path.name}: missing category heading (`# NN 中文 English`)")
    if not category["topics"]:
        raise ValueError(f"{path.name}: no topics found")
    for topic in category["topics"]:
        if len(topic["questions"]) != QUESTIONS_PER_TOPIC:
            raise ValueError(
                f"{path.name}:{topic['en']}: expected {QUESTIONS_PER_TOPIC} questions, "
                f"found {len(topic['questions'])}"
            )
        nums = [int(q["n"]) for q in topic["questions"]]
        if nums != list(range(1, QUESTIONS_PER_TOPIC + 1)):
            raise ValueError(f"{path.name}:{topic['en']}: question numbers are not 1..{QUESTIONS_PER_TOPIC}")
    return category


# ---------------------------------------------------------------- latex emit
PREAMBLE_BODY = r"""\usepackage{longtable}

% ---------- category title (compilation PDFs) ----------
\newcommand{\cqcategory}[3]{%
  \par\vspace{2pt}%
  {\dispspaced\bfseries\footnotesize #1}\par
  \vspace{5pt}%
  {\bfseries\fontsize{26pt}{30pt}\selectfont #3}\par
  \vspace{3pt}%
  {\fontsize{15pt}{18pt}\selectfont\color{muted} #2}\par
  \vspace{9pt}%
  \noindent{\color{ink}\hrule height 2.4pt}\par
  \vspace{16pt}%
}

% ---------- topic title ----------
\newcommand{\cqtopic}[4]{%
  \par\vspace{2pt}%
  {\dispfont\bfseries\fontsize{9pt}{11pt}\selectfont\color{muted} #1}\par
  \vspace{3pt}%
  {\bfseries\fontsize{19pt}{23pt}\selectfont #3}\par
  \vspace{2pt}%
  {\fontsize{12.5pt}{15pt}\selectfont\color{muted} #4}\par
  \vspace{7pt}%
  \noindent{\color{ink}\hrule height 1.8pt}\par
  \vspace{10pt}%
}

% ---------- question list ----------
% English sits above its Chinese, in one full-width column: a beginner reading
% a 13pt English line should not also have to track a second column, and the
% full measure keeps almost every question on a single line.
% Hyphenation is off: `\RaggedRight` alone still breaks words, and a question
% like "morning" rendering as "morn-ing" reads as a spelling error to a
% beginner. Ragged right absorbs the cost without overfull lines.
\newcommand{\cqen}{\fontsize{13pt}{16.5pt}\selectfont}
\newcommand{\cqcn}{\fontsize{11pt}{16.5pt}\selectfont}
\newcommand{\cqnohyph}{\hyphenpenalty=10000 \exhyphenpenalty=10000 \pretolerance=10000 \tolerance=10000}
% One question is one unbreakable block: number gutter, then English with its
% Chinese right underneath. A longtable row is the obvious host, but `\\[dim]`
% is silently ignored inside one, so the pair spacing could not be tuned; two
% side-by-side minipages give exact control and keep each pair together when
% the page breaks.
\newcommand{\cqitem}[3]{%
  \par\vspace{10pt}\noindent
  \begin{minipage}[t]{7.5mm}\dispfont\bfseries\footnotesize #1\end{minipage}%
  \begin{minipage}[t]{\dimexpr\textwidth-7.5mm\relax}%
    \RaggedRight\cqnohyph\cqen #2\par
    \vspace{2pt}%
    \RaggedRight\cqnohyph\cqcn #3\par
  \end{minipage}\par
}

% ---------- page break ----------
\newcommand{\cqnewpage}{\clearpage}
"""


def emit_topic(category: dict, topic: dict) -> str:
    items = "\n".join(
        f"\\cqitem{{{q['n']}}}{{{l(q['en'])}}}{{{l(q['cn'])}}}" for q in topic["questions"]
    )
    label = f"{category['en']} · Topic {topic['num']}"
    return (
        raw(f"\\cqtopic{{{l(label)}}}{{{l(topic['num'])}}}{{{l(topic['en'])}}}{{{l(topic['cn'])}}}")
        + raw(items)
    )


def emit_topic_pdf(category: dict, topic: dict) -> str:
    return emit_topic(category, topic)


def emit_category_pdf(category: dict) -> str:
    parts = [
        raw(f"\\cqcategory{{{l(category['num'])}}}{{{l(category['cn'])}}}{{{l(category['en'])}}}"),
    ]
    for index, topic in enumerate(category["topics"]):
        if index:
            parts.append(raw("\\cqnewpage"))
        parts.append(emit_topic(category, topic))
    return "\n".join(parts)


def emit_all_pdf(categories: list[dict]) -> str:
    parts = [raw("\\cqcategory{}{}{All Conversation Questions}")]
    for category in categories:
        for topic in category["topics"]:
            parts.append(raw("\\cqnewpage"))
            parts.append(emit_topic(category, topic))
    return "\n".join(parts)


# ---------------------------------------------------------------- build
def render(body_md: str, pdf: Path) -> tuple[bool, str]:
    TMP_MD.write_text(body_md, encoding="utf-8")
    env = dict(os.environ)
    env["PATH"] = build.MIKTEX_BIN + os.pathsep + env["PATH"]
    cmd = [
        build.PANDOC, str(TMP_MD),
        "-f", "markdown+raw_attribute",
        "--template", str(build.TEMPLATE),
        "-H", str(build.PREAMBLE),
        "-H", str(ADDITIONS),
        "--pdf-engine=" + build.PDF_ENGINE,
    ]
    if build.PDF_ENGINE == "xelatex" and Path(build.MIKTEX_BIN).exists():
        cmd.append("--pdf-engine-opt=--enable-installer")
    cmd += ["-o", str(pdf)]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=300, env=env,
        )
    except subprocess.TimeoutExpired:
        return False, "pandoc/xelatex timed out"
    if result.returncode != 0:
        return False, result.stderr[-2000:]
    if not (pdf.exists() and pdf.stat().st_size > 2000):
        return False, "output missing or too small"
    return True, ""


def emit_at(pdf: Path, body: str, label: str) -> None:
    ok, err = render(body, pdf)
    print(f"  [{'ok' if ok else 'FAIL'}] {label}", flush=True)
    if not ok:
        print(err)
        raise SystemExit(f"build failed: {label}")


def main() -> None:
    args = sys.argv[1:]
    prefixes = [a for a in args if not a.startswith("--")]
    every_source = sorted(SOURCE_DIR.glob("*.md"))
    # `--global-only` skips the per-category work and rebuilds just the
    # compilation, which is what you want after fixing a few source lines.
    global_only = "--global-only" in args
    sources = (
        [p for p in every_source if any(p.name.startswith(x) for x in prefixes)]
        if prefixes else every_source
    )
    if not sources and not global_only:
        raise SystemExit(f"no source files in {SOURCE_DIR} matching {prefixes}")

    TEX_DIR.mkdir(parents=True, exist_ok=True)
    ADDITIONS.write_text(PREAMBLE_BODY, encoding="utf-8")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    done = 0
    if not global_only:
        categories = [parse_category(path) for path in sources]
        for path, category in zip(sources, categories):
            category_dir = OUT_DIR / path.stem
            category_dir.mkdir(parents=True, exist_ok=True)
            for topic in category["topics"]:
                name = f"{category['num']}-{topic['num']}-{slug(topic['en'])}.pdf"
                emit_at(category_dir / name, emit_topic_pdf(category, topic), f"{category_dir.name}/{name}")
                done += 1
            name = f"{path.stem}-All.pdf"
            emit_at(category_dir / name, emit_category_pdf(category), f"{category_dir.name}/{name}")

    # The compilation always needs every category, not just the ones rebuilt.
    if not prefixes or global_only:
        all_categories = [parse_category(path) for path in every_source]
        emit_at(OUT_DIR / "All-Questions.pdf", emit_all_pdf(all_categories), "All-Questions.pdf")

    print(f"\n[done] {done} topic PDFs -> {OUT_DIR}")


if __name__ == "__main__":
    main()
