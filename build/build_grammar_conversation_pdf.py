#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build PDF/ESL-500 Grammar Based Conversation.pdf from the revised markdown.

Layout (per user requirements):
  - Two separated parts: Part 1 语法讲解 (minimal Chinese explanation +
    exactly 5 English examples per topic), Part 2 讨论问题 (two-column
    numbered question lists per topic).
  - Pure black & white: no grays, no color accents.
  - Topics flow in Part 1; each topic starts a fresh page in Part 2.
  - Real LaTeX table of contents (parts + topics).

Pipeline: Markdown(raw-LaTeX blocks) → pandoc + xelatex (MiKTeX) → PDF
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))

from build_pdfs import (  # noqa: E402
    GEN_DIR,
    PDF_DIR,
    PREAMBLE,
    TEMPLATE,
    T_pagebreak,
    l,
    raw,
)
import build_pdfs as _bp  # noqa: E402

_PANDOC = Path(r"C:\Program Files\Pandoc\pandoc.exe")
_MIKTEX = Path(r"C:\Users\ZZC\AppData\Local\Programs\MiKTeX\miktex\bin\x64")
_bp.PANDOC = str(_PANDOC) if _PANDOC.exists() else (shutil.which("pandoc") or "pandoc")
_bp.MIKTEX_BIN = str(_MIKTEX) if _MIKTEX.exists() else ""
if not _MIKTEX.exists():
    _bp.PDF_ENGINE = shutil.which("xelatex") or "xelatex"

MD = ROOT / "MD" / "ESL-500 Grammar Based Conversation - Pitts, Larry.md"
GEN_MD = GEN_DIR / "ESL-500 Grammar Based Conversation.md"
PDF = PDF_DIR / "ESL-500 Grammar Based Conversation.pdf"
PREAMBLE_ADD = GEN_DIR / "preamble_grammar.tex"
PREVIEW = ROOT / "build" / "preview"

APPENDIX_H2S = {
    "USING CONVERSATION QUESTIONS IN THE CLASSROOM",
    "EXTRAS",
    "ENJOY THE BOOK?",
    "Index",
}

INS_NOTES = (
    "Fill in the parentheses with your own idea.",
    "For the following questions, talk about how certain you are of your opinion using modals.",
)

# topic title -> ultra-short Chinese explanation
CH = {
    "ADVERBS OF FREQUENCY":
        "频率副词表示动作多久发生一次。放在 be 动词后、一般动词前。",
    "AS … AS (EQUATIVES)":
        "as…as 表示“和……一样”；not as…as 表示“不如……”。",
    "BE GOING TO":
        "be going to 表示打算做某事，或根据迹象推测将发生。",
    "COMPARATIVES":
        "比较级用于两者比较：短词加 -er，长词用 more。",
    "CONDITIONALS REAL WITH THE FUTURE (FIRST CONDITIONAL)":
        "真实条件句（将来）：if + 一般现在时，主句用 will。",
    "CONDITIONALS REAL WITH THE PRESENT (ZERO CONDITIONAL)":
        "真实条件句（现在）：if + 一般现在时，主句也用一般现在时。",
    "CONDITIONALS UNREAL WITH THE PAST (THIRD CONDITIONAL)":
        "虚拟条件句（过去）：if + 过去完成时，主句用 would have + 过去分词。",
    "CONDITIONALS UNREAL WITH THE PRESENT (SECOND CONDITIONAL)":
        "虚拟条件句（现在/将来）：if + 一般过去时，主句用 would + 动词。",
    "FOR, SINCE":
        "for + 时间段（持续多久）；since + 时间点（从何时开始）。",
    "GERUNDS VS. INFINITIVES":
        "动名词（-ing）和不定式（to do）用哪个，由前面动词决定。",
    "IMPERATIVES":
        "祈使句直接用动词原形，表命令、建议或指示。",
    "MODALS OF ADVICE":
        "should / ought to / had better 都表建议，语气递增。",
    "MODALS OF NECESSITY":
        "must / have to / have got to 都表“必须”。",
    "MODALS OF POSSIBILITY AND PROBABILITY":
        "may / might / could 表可能；must 表一定；can’t 表不可能。",
    "NOUNS (COUNT / NONCOUNT)":
        "可数名词有复数，不可数名词没有。",
    "PASSIVE VOICE IN THE PRESENT (PRESENT PASSIVE VOICE)":
        "被动语态（现在）：am / is / are + 过去分词。",
    "PASSIVE VOICE WITH THE PAST":
        "被动语态（过去）：was / were + 过去分词。",
    "PAST CONTINUOUS":
        "过去进行时：was / were + doing，表过去某时正在做。",
    "PRESENT PERFECT":
        "现在完成时：have / has + 过去分词，表已发生或影响现在。",
    "PRESENT PERFECT CONTINUOUS":
        "现在完成进行时：have / has been + doing，强调持续到现在。",
    "QUANTIFIERS":
        "量词表数量：many / few + 可数名词；much / little + 不可数名词。",
    "REPORTED SPEECH / INDIRECT SPEECH":
        "间接引语：转述别人说的话，时态、代词要相应变化。",
    "SIMPLE PAST":
        "一般过去时：动词用过去式，表过去发生。",
    "SIMPLE PRESENT":
        "一般现在时：动词原形（第三人称加 -s），表习惯和事实。",
    "SUPERLATIVES":
        "最高级用于三者以上比较：the + -est 或 the most。",
    "TAG QUESTIONS":
        "反义疑问句：前肯定后否定，前否定后肯定。",
    "USED TO, WOULD":
        "used to / would 表过去经常做、现在不再做的事。",
    "WILL":
        "will + 动词原形表将来：预测、承诺、临时决定。",
    "WOULD RATHER, PREFER":
        "would rather / prefer 表更喜欢：prefer + doing / to do；would rather + 动词原形。",
}

# topic title -> exactly 5 curated examples (from the revised markdown, plus
# a few authored fill-ins where the topic had fewer than five).
EXAMPLES = {'ADVERBS OF FREQUENCY': ['He is always sleepy on Monday morning.', 'She sometimes walks in the park after dinner.', 'Sometimes they watch movies at home on Friday night.', 'Usually he gets up early and takes the subway.', 'I never drink coffee at night — I can’t sleep.'], 'AS … AS (EQUATIVES)': ['This apartment is not as big as the one downtown.', 'My brother eats as fast as me.', 'Our shop doesn’t have as many people as the shop next door.', 'My phone looks as good as new now.', 'She speaks English as well as her teacher.'], 'BE GOING TO': ['My sister is going to look for a job next month.', 'The city is going to build a new subway near my home.', 'Don’t worry. It’s not going to rain today.', 'He’s going to win the game — look how fast he runs.', 'I’m going to order food online tonight.'], 'COMPARATIVES': ['He is taller than his brother, so he buys bigger clothes.', 'This phone is more expensive than that one, but the camera is better.', 'She is funnier than her friends — everyone laughs at her.', 'Which is more important, money or health? I think health is more important.', 'He works harder than everyone in his office.'], 'CONDITIONALS REAL WITH THE FUTURE (FIRST CONDITIONAL)': ['If I finish my work before 6pm, my boss will be happy.', 'If you take the stairs instead of the elevator, you’ll be healthier.', 'If he doesn’t practice, he’ll never pass the test.', 'My boss will be happy if I finish my work on time.', 'If it rains this weekend, we’ll stay home and watch TV.'], 'CONDITIONALS REAL WITH THE PRESENT (ZERO CONDITIONAL)': ['If I forget my keys, my roommate gets angry.', 'If I’m bored on the subway, I look at my phone.', 'If my dad forgets where his keys are, he asks my mom.', 'My roommate gets angry if I forget my keys.', 'If I drink coffee at night, I can’t sleep.'], 'CONDITIONALS UNREAL WITH THE PAST (THIRD CONDITIONAL)': ['If I had missed the last subway, I would have taken a taxi home.', 'If you had called me earlier, I would have saved you a seat.', 'I would have taken a taxi home if I had missed the subway.', 'If I had bought that house two years ago, I would be rich now.', 'If I had studied English in school, my life would be different now.'], 'CONDITIONALS UNREAL WITH THE PRESENT (SECOND CONDITIONAL)': ['If I had more money, I would buy a car.', 'If I had a long vacation, I would visit my parents.', 'If I were a cat, I could sleep all day.', 'I would buy a car if I had more money.', 'If I had more free time, I would learn to cook.'], 'FOR, SINCE': ['They have waited in line for 20 minutes.', 'They have waited in line since 3pm.', 'He has worked at this restaurant for 5 weeks.', 'He has worked at this restaurant since November.', 'He has worked since 7pm today.'], 'GERUNDS VS. INFINITIVES': ['Running is fun — I listen to music when I run.', 'I love running in the morning.', 'I never thought about running before.', 'My friend invited me to her wedding in Shanghai.', 'My brother helped me finish my work.'], 'IMPERATIVES': ['Add two cups of flour, then mix the eggs.', 'Don’t sit on the couch all day — go for a walk.', 'Click the green button to order in the app.', 'Find a job near your home.', 'First, cut the vegetables. Then, put them in the pot.'], 'MODALS OF ADVICE': ['Where should I park my car?', 'You shouldn’t drink that milk — it’s old.', 'You should bring an umbrella — it will rain.', 'She had better not be late again — the boss was angry yesterday.', 'He ought to start walking every day.'], 'MODALS OF NECESSITY': ['You must not smoke here — this is a hospital.', 'He has to go to work on Saturday.', 'She doesn’t have to work today.', 'We have to buy a new rice cooker — ours is old.', 'He had to work all night last night.'], 'MODALS OF POSSIBILITY AND PROBABILITY': ['You are really hot — it must be hot outside.', 'We can’t give him the job — he has no experience.', 'After I finish school, I may work in Shanghai.', 'Your phone might be old now.', 'They might not go on vacation this year.'], 'NOUNS (COUNT / NONCOUNT)': ['Do you have a pen? Mine is broken.', 'He doesn’t have much money this month, so he cooks at home.', 'Would you like some fruit?', 'This house is made of wood.', 'Can you get me three bottles of water?'], 'PASSIVE VOICE IN THE PRESENT (PRESENT PASSIVE VOICE)': ['The best phones are made in China.', 'Tea is grown in China.', 'English is spoken in many countries.', 'This food is made by my mother.', 'The room is cleaned every day.'], 'PASSIVE VOICE WITH THE PAST': ['My phone was stolen on the crowded subway!', 'This house was built ten years ago.', 'This food was made by my grandmother.', 'My lunch was taken by a cat in the park.', 'The window was opened by the wind.'], 'PAST CONTINUOUS': ['The workers were fixing the road last week.', 'My stomach was hurting after I ate too much.', 'My friend was talking on the phone while I was watching TV.', 'She was taking the subway home at 9pm.', 'They were having a meeting at 3pm yesterday.'], 'PRESENT PERFECT': ['I have eaten at this restaurant many times.', 'We have lived in this apartment for two years.', 'My mother loves this show. She has watched it many times.', 'My parents have never been to Beijing.', 'Have you ever been to Shanghai?'], 'PRESENT PERFECT CONTINUOUS': ['This company has been making tea since 1998.', 'She has been working all week, but she finished her work today.', 'I have been watching TV for three hours — I need a break.', 'He has been waiting for the bus for 30 minutes.', 'We have been playing basketball every Saturday for two years.'], 'QUANTIFIERS': ['Most restaurants in this street are clean.', 'Many people eat lunch at work.', 'Most of the students in my class are young.', 'Many of my friends live near me.', 'I have enough time to finish my work.'], 'REPORTED SPEECH / INDIRECT SPEECH': ['“I like tea.” → He said he liked tea.', '“I’m working on my homework.” → He said he was working on his homework.', '“Li Wei ate noodles for lunch.” → She said Li Wei had eaten noodles.', '“Can you help me?” → He asked me to help him.', '“Where are you from?” → She asked me where I was from.'], 'SIMPLE PAST': ['He talked to his boss about his work yesterday.', 'She walked to the subway every day last month.', 'They ate noodles. Did they drink tea? Yes, they drank tea.', 'We worked together in the same office.', 'I was tired after work yesterday.'], 'SIMPLE PRESENT': ['I work at a small company.', 'He takes the subway to work every day.', 'The meeting starts at nine.', 'He doesn’t like coffee. I don’t drink tea.', 'The earth goes around the sun.'], 'SUPERLATIVES': ['He is the tallest boy in his class.', 'This house is the most expensive in the street.', 'She is the funniest girl in our office.', 'This phone is the least expensive one in the store.', 'This hotpot is the spiciest food I have ever eaten.'], 'TAG QUESTIONS': ['You’re hungry, aren’t you? Let’s eat.', 'Your boss called you, didn’t he?', 'The bus is late, isn’t it?', 'We shouldn’t go in there, should we?', 'He walks to work, doesn’t he?'], 'USED TO, WOULD': ['I didn’t use to live alone.', 'He used to take the bus to work.', 'He would take the bus to work.', 'My friends would bring lunch to school.', 'Did she use to play games in the afternoon?'], 'WILL': ['People will go to the moon again one day.', 'I’ll help you carry the boxes.', 'We’ll help you move to your new house.', 'Do your homework, or you’ll get a bad grade.', 'Oh no, my phone is dead. I’ll charge it at the coffee shop.'], 'WOULD RATHER, PREFER': ['I prefer walking in the park.', 'I would rather read than watch TV.', 'I prefer tea to coffee.', 'I would rather take the bus than walk.', 'I prefer to eat at home rather than at a restaurant.']}

ADDITIONS = r"""% ESL-500 Grammar Based Conversation · additions on top of build/preamble.tex
% Pure black & white: every color is black.
\usepackage{multicol}
\usepackage{framed}
\usepackage{tocloft}
\definecolor{accent}{HTML}{000000}
\definecolor{exbar}{HTML}{000000}
\definecolor{muted}{HTML}{000000}
\definecolor{faint}{HTML}{000000}
\definecolor{filllight}{HTML}{FFFFFF}

% ---------- footer (black); headers left empty to avoid repeating titles ----------
\fancyfoot[L]{\footnotesize\dispfont ESL-500}

% ---------- compact table of contents (topics + appendix) ----------
\renewcommand{\contentsname}{Contents}
\setlength{\cftbeforesecskip}{9pt}
\renewcommand{\cftsecfont}{\dispfont\bfseries\fontsize{10.5pt}{13pt}\selectfont}
\renewcommand{\cftsecpagefont}{\dispfont\fontsize{10.5pt}{13pt}\selectfont}
\setlength{\cftsecindent}{0pt}

% ---------- title block ----------
\newcommand{\eslbooktitle}{%
  \thispagestyle{empty}%
  \par\vspace{42pt}\noindent
  {\dispfont\bfseries\fontsize{46pt}{50pt}\selectfont 500}\par
  \vspace{10pt}
  {\fontsize{21pt}{25pt}\selectfont\bfseries Grammar Based Conversation}\par
}

% ---------- part 1 topic opener ----------
\newcommand{\esltopic}[3]{%
  \par\vspace{14pt}\noindent
  {\dispfont\bfseries\fontsize{16pt}{20pt}\selectfont #1}\hspace{8pt}%
  {\fontsize{13pt}{17pt}\selectfont\bfseries #2}\par
  \vspace{5pt}
  {\fontsize{11.5pt}{16.5pt}\selectfont #3}\par
  \vspace{6pt}\markboth{#1 #2}{#1 #2}\nopagebreak
  \addcontentsline{toc}{section}{#1 #2}
}

% ---------- separator between explanation and questions ----------
\newcommand{\eslsep}{%
  \par\vspace{6pt}\noindent\rule{\textwidth}{0.4pt}\par\vspace{8pt}
}

% ---------- questions sub-header (###) ----------
\newcommand{\eslqheader}[1]{%
  \par\vspace{10pt}\noindent
  {\dispfont\bfseries\fontsize{12.5pt}{15pt}\selectfont #1}\par
  \vspace{5pt}\nopagebreak
}

% ---------- appendix headers ----------
\newcommand{\eslappheader}[1]{%
  \par\vspace{12pt}\noindent
  {\dispfont\bfseries\fontsize{16pt}{20pt}\selectfont #1}\par
  \vspace{6pt}\markboth{#1}{#1}\nopagebreak
  \addcontentsline{toc}{section}{#1}
}
\newcommand{\eslsub}[1]{%
  \par\vspace{8pt}\noindent{\bfseries\fontsize{11.5pt}{14.5pt}\selectfont #1}\par
  \vspace{3pt}\nopagebreak
}
\newcommand{\esllabel}[1]{%
  \par\vspace{4pt}\noindent{\bfseries\fontsize{11pt}{14pt}\selectfont #1}\par
  \vspace{2pt}\nopagebreak
}

% ---------- body / notes / appendix items ----------
\newcommand{\eslbody}[1]{%
  \par\vspace{2pt}\noindent
  {\bodyfont\fontsize{11pt}{16pt}\selectfont #1}\par\vspace{5pt}
}
\newcommand{\eslqnote}[1]{%
  \par\vspace{3pt}\noindent{\itshape\footnotesize #1}\par\vspace{5pt}
}
\newcommand{\eslitem}[1]{%
  \par\vspace{2pt}\noindent\hspace{14pt}{\bodyfont\fontsize{10.5pt}{14.5pt}\selectfont #1}\par\vspace{2pt}
}

% ---------- part 1 examples: compact numbered list ----------
\newenvironment{eslexamples}{%
  \begin{enumerate}%
  \setlength{\itemsep}{3pt}\setlength{\parsep}{0pt}\setlength{\parskip}{0pt}%
  \renewcommand{\labelenumi}{\dispfont\bfseries\arabic{enumi}.}%
  \bodyfont\fontsize{10.5pt}{14.5pt}\selectfont
}{\end{enumerate}}

% ---------- part 2 questions: two-column numbered list ----------
\newenvironment{eslquestions}{%
  \begin{multicols}{2}%
  \begin{enumerate}%
  \setlength{\itemsep}{3pt}\setlength{\parsep}{0pt}\setlength{\parskip}{0pt}%
  \renewcommand{\labelenumi}{\dispfont\bfseries\arabic{enumi}.}%
  \bodyfont\fontsize{10.5pt}{14pt}\selectfont
}{\end{enumerate}\end{multicols}}
"""


def parse(lines):
    """Return (topics, appendix, q_total) where topics is a list of
    dict(title=..., qsections=[(header, [('q'|'note', text), ...])]) and
    appendix is a list of dict(title=..., blocks=[(kind, text), ...])."""
    topics = []
    appendix = []
    cur_topic = None
    cur_qsec = None
    cur_app = None
    q_total = 0

    def flush_qsec():
        nonlocal cur_qsec
        if cur_qsec is not None:
            cur_topic["qsections"].append(cur_qsec)
            cur_qsec = None

    for rawline in lines:
        s = rawline.strip()
        if not s or s.startswith("![") or s.startswith("# "):
            continue
        if s == "## Table of Contents":
            continue
        if s.startswith("## "):
            flush_qsec()
            title = s[3:].strip()
            if title in APPENDIX_H2S:
                cur_topic = None
                cur_app = {"title": title, "blocks": []}
                appendix.append(cur_app)
                continue
            if title != "Table of Contents":
                cur_topic = {"title": title, "qsections": []}
                topics.append(cur_topic)
                cur_app = None
                continue
            # "## Table of Contents" front matter: skip
            continue
        if s.startswith("### "):
            if cur_topic is not None:
                flush_qsec()
                cur_qsec = {"header": s[4:].strip(), "items": []}
            elif cur_app is not None:
                cur_app["blocks"].append(("h3", s[4:].strip()))
            continue
        if s.startswith("#### "):
            if cur_app is not None:
                cur_app["blocks"].append(("h4", s[5:].strip()))
            continue
        if s.startswith("- "):
            item = s[2:].strip()
            if cur_topic is not None and cur_qsec is not None:
                if item in INS_NOTES:
                    cur_qsec["items"].append(("note", item))
                else:
                    cur_qsec["items"].append(("q", item))
                    q_total += 1
            elif cur_app is not None:
                cur_app["blocks"].append(("item", item))
            continue
        # plain paragraph
        if cur_app is not None:
            cur_app["blocks"].append(("body", s))
    flush_qsec()
    return topics, appendix, q_total


def emit(topics, appendix, q_total):
    out = []
    out.append(raw(r"\eslbooktitle"))
    out.append(T_pagebreak())
    out.append(raw(r"\setcounter{tocdepth}{1}"))
    out.append(raw(r"\tableofcontents"))
    out.append(T_pagebreak())

    # ---- topics: explanation + questions per topic ----
    for i, tp in enumerate(topics, 1):
        title = tp["title"]
        exs = EXAMPLES.get(title)
        if exs is None:
            raise SystemExit("missing examples for " + title)
        if len(exs) != 5:
            raise SystemExit(f"{title}: expected 5 examples, got {len(exs)}")
        out.append(T_pagebreak())
        out.append(raw(f"\\esltopic{{{i:02d}}}{{{l(title)}}}{{{CH[title]}}}"))
        body = "\n".join("\\item " + l(e) for e in exs)
        out.append(raw("\\begin{eslexamples}\n" + body + "\n\\end{eslexamples}"))
        out.append(raw(r"\eslsep"))
        for qsec in tp["qsections"]:
            qh, items = qsec["header"], qsec["items"]
            out.append(raw(f"\\eslqheader{{{l(qh)}}}"))
            qbody = []
            for kind, text in items:
                if kind == "note":
                    if qbody:
                        out.append(raw("\\begin{eslquestions}\n"
                                       + "\n".join("\\item " + x for x in qbody)
                                       + "\n\\end{eslquestions}"))
                        qbody = []
                    out.append(raw(f"\\eslqnote{{{l(text)}}}"))
                else:
                    qbody.append(text)
            if qbody:
                out.append(raw("\\begin{eslquestions}\n"
                               + "\n".join("\\item " + l(x) for x in qbody)
                               + "\n\\end{eslquestions}"))

    # ---- appendix ----
    if appendix:
        out.append(T_pagebreak())
        for sec in appendix:
            out.append(raw(f"\\eslappheader{{{l(sec['title'])}}}"))
            for kind, text in sec["blocks"]:
                if kind == "h3":
                    out.append(raw(f"\\eslsub{{{l(text)}}}"))
                elif kind == "h4":
                    out.append(raw(f"\\esllabel{{{l(text)}}}"))
                elif kind == "item":
                    out.append(raw(f"\\eslitem{{{l(text)}}}"))
                else:
                    out.append(raw(f"\\eslbody{{{l(text)}}}"))
    return out


def build_pdf(gen_md: Path, pdf: Path) -> bool:
    env = dict(os.environ)
    env["PATH"] = _bp.MIKTEX_BIN + os.pathsep + env["PATH"]
    cmd = [
        _bp.PANDOC, str(gen_md),
        "-f", "markdown+raw_attribute",
        "--template", str(TEMPLATE),
        "-H", str(PREAMBLE),
        "-H", str(PREAMBLE_ADD),
        "--pdf-engine=" + _bp.PDF_ENGINE,
        "--pdf-engine-opt=--enable-installer",
        "-o", str(pdf),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300, env=env)
    except subprocess.TimeoutExpired:
        print("  [fail] pandoc/xelatex timed out")
        return False
    if r.returncode != 0:
        print(f"  [fail] {r.stderr[-3000:]}")
        return False
    return pdf.exists() and pdf.stat().st_size > 2000


def main():
    if not MD.exists():
        raise SystemExit(f"missing {MD}")
    PREAMBLE_ADD.write_text(ADDITIONS, encoding="utf-8")
    lines = MD.read_text(encoding="utf-8").split("\n")
    topics, appendix, q_total = parse(lines)
    missing = [t for t in topics if t["title"] not in CH]
    if missing:
        raise SystemExit("missing Chinese explanation for: " + ", ".join(missing))
    print(f"[parse] topics={len(topics)} questions={q_total} appendix={len(appendix)}")
    out = emit(topics, appendix, q_total)
    GEN_MD.write_text("\n\n".join(out) + "\n", encoding="utf-8")
    print(f"[build] {PDF.name}")
    if not build_pdf(GEN_MD, PDF):
        raise SystemExit("build failed")
    print(f"[ok]   {PDF} ({PDF.stat().st_size / 1024:.0f} KB)")

    PREVIEW.mkdir(exist_ok=True)
    prefix = str(PREVIEW / "grammar-conversation")
    r = subprocess.run(["pdftoppm", "-png", "-r", "96", "-f", "1", "-l", "6",
                        str(PDF), prefix], capture_output=True, text=True, encoding="utf-8")
    if r.returncode == 0:
        print(f"[png]  {prefix}-*.png (pages 1-6)")
    else:
        print(f"[warn] preview render failed: {r.stderr[-500:]}")


if __name__ == "__main__":
    main()
