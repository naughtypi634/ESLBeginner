"""Shared helper: after a numbered course PDF is built, also emit a
student-facing copy whose filename drops the leading number prefix.

e.g.  PDF/12-Feelings And Emotions.pdf  ->  PDF/Feelings And Emotions.pdf
"""

import re
from pathlib import Path

_NUM_PREFIX = re.compile(r"^(\d+-)+")


def student_stem(stem: str) -> str:
    """Strip leading number segments (e.g. 12-, 07-1-)."""
    return _NUM_PREFIX.sub("", stem, count=1)


def make_student_copy(pdf_path: Path) -> Path | None:
    """Create the title-only copy next to the numbered PDF; no-op if none needed."""
    student = pdf_path.with_name(student_stem(pdf_path.stem) + pdf_path.suffix)
    if student == pdf_path:
        return None
    student.write_bytes(pdf_path.read_bytes())
    return student
