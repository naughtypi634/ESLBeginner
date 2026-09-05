#!/usr/bin/env python3
"""Build the A1 Conversation Starter workbook.

Each story is exactly two pages: vocabulary and story on page one, then
conversation questions on page two.
"""

import re
import shutil
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "MD" / "conversation starter" / "A1"
TEX_DIR = ROOT / "build" / "tex"
PDF_DIR = ROOT / "PDF"
GEN_MD = TEX_DIR / "ConversationStarter.A1.generated.md"
ADDITIONS = TEX_DIR / "conversation_starter_a1_preamble.tex"
PDF = PDF_DIR / "ConversationStarter.A1.pdf"

sys.path.insert(0, str(ROOT / "build"))
import build_pdfs as build  # noqa: E402
from build_pdfs import l, pandoc_pdf, raw  # noqa: E402


def configure_toolchain():
    """Use tools available on this machine without changing shared settings."""
    pandoc = shutil.which("pandoc")
    xelatex = shutil.which("xelatex")
    if not pandoc or not xelatex:
        raise RuntimeError("pandoc and xelatex are required to build this PDF")
    build.PANDOC = pandoc
    build.PDF_ENGINE = xelatex
    build.MIKTEX_BIN = str(Path(xelatex).parent)


def parse_source(path: Path):
    text = path.read_text(encoding="utf-8")
    unit = re.search(r"^## UNIT \d+: (.+)$", text, re.MULTILINE)
    stories = []
    matches = list(re.finditer(r"^### (STORY \d+: .+)$", text, re.MULTILINE))
    for index, match in enumerate(matches):
        block = text[match.start(): matches[index + 1].start() if index + 1 < len(matches) else len(text)]
        heading = match.group(1)
        vocabulary = re.findall(r"^\d+\. (.+)$", block.split("**Story**", 1)[0], re.MULTILINE)
        body_match = re.search(r"\*\*Story\*\*\s*\n\n(.+?)\n\n\*\*Conversation Questions\*\*", block, re.DOTALL)
        questions = re.findall(r"^\d+\. (.+)$", block.split("**Conversation Questions**", 1)[1], re.MULTILINE)
        if not body_match or len(vocabulary) != 10 or len(questions) != 10:
            raise ValueError(f"invalid story structure: {path.name} / {heading}")
        stories.append({"heading": heading, "vocabulary": vocabulary, "body": body_match.group(1), "questions": questions})
    if not unit or len(stories) != 5:
        raise ValueError(f"invalid unit structure: {path.name}")
    return unit.group(1), stories


def emit_story(unit_number, unit_title, story):
    vocab_rows = []
    for index in range(0, 10, 2):
        left = f"{index + 1}. {l(story['vocabulary'][index])}"
        right = f"{index + 2}. {l(story['vocabulary'][index + 1])}"
        vocab_rows.append(f"{left} & {right} \\\\")
    vocab_table = "\\begin{tabularx}{\\textwidth}{@{}X X@{}}\n" + "\n".join(vocab_rows) + "\n\\end{tabularx}"
    body = "\n".join(f"\\cspara{{{l(paragraph)}}}" for paragraph in story["body"].split("\n\n"))
    questions = "\n".join(f"\\csquestion{{{index}}}{{{l(question)}}}" for index, question in enumerate(story["questions"], 1))
    return (
        raw(f"\\csfirstpage{{{l(unit_number)}}}{{{l(unit_title)}}}{{{l(story['heading'])}}}")
        + raw(f"\\csvocabhead{{Key Vocabulary}}\n{vocab_table}")
        + raw(body)
        + raw("\\cssecondpage")
        + raw(f"\\csquestionhead{{Conversation Questions}}\n{questions}")
    )


def emit():
    chunks = []
    for unit in range(1, 11):
        path = SOURCE_DIR / f"ConversationStarter.A1.Unit{unit}.md"
        unit_title, stories = parse_source(path)
        for story in stories:
            chunks.append(emit_story(str(unit), unit_title, story))
    return "\n".join(chunks)


def build_pdf():
    env = dict(os.environ)
    env["PATH"] = build.MIKTEX_BIN + os.pathsep + env["PATH"]
    command = [
        build.PANDOC,
        str(GEN_MD),
        "-f", "markdown+raw_attribute",
        "--template", str(build.TEMPLATE),
        "-H", str(build.PREAMBLE),
        "-H", str(ADDITIONS),
        "--pdf-engine=" + build.PDF_ENGINE,
        "--pdf-engine-opt=--enable-installer",
        "-o", str(PDF),
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300, env=env)
    if result.returncode != 0:
        print(result.stderr[-3000:])
        return False
    return PDF.exists() and PDF.stat().st_size > 2000


def main():
    configure_toolchain()
    ADDITIONS.write_text(
        r"""\usepackage{tabularx}
\newcommand{\csfirstpage}[3]{%
  \clearpage
  {\dispfont\bfseries\fontsize{9pt}{11pt}\selectfont UNIT #1}\hspace{8pt}
  {\fontsize{11pt}{14pt}\selectfont\bfseries #2}\par\vspace{8pt}
  {\dispfont\bfseries\fontsize{15pt}{18pt}\selectfont #3}\par\vspace{10pt}
}
\newcommand{\csvocabhead}[1]{%
  \par\noindent{\bfseries\fontsize{11pt}{14pt}\selectfont #1}\par\vspace{5pt}
}
\newcommand{\cspara}[1]{%
  \par\vspace{4pt}\noindent\bodyfont #1\par
}
\newcommand{\cssecondpage}{\clearpage}
\newcommand{\csquestionhead}[1]{%
  \noindent{\bfseries\fontsize{13pt}{16pt}\selectfont #1}\par\vspace{10pt}
}
\newcommand{\csquestion}[2]{%
  \par\vspace{5pt}\noindent\begin{tabularx}{\textwidth}{@{}l X@{}}
    {\dispfont\bfseries\footnotesize #1.} & \RaggedRight\bodyfont #2
  \end{tabularx}\par
}
""",
        encoding="utf-8",
    )
    GEN_MD.write_text(emit(), encoding="utf-8")
    PDF_DIR.mkdir(exist_ok=True)
    if not build_pdf():
        raise SystemExit("PDF build failed")
    print(f"[ok] {PDF} ({PDF.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()