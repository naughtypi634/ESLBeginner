#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registry of the lesson series that share the Beginner layout pipeline.

check_consistency.py, check_orphan_headings.py and fit_pages.py all walk one
series at a time and all need to know the same three things about it: where the
markdown lives, where its PDFs land, and which builder produces them. Keeping
that in one place means adding a series is a single edit rather than three.

Scripts run with `python -I` are NOT given their own directory on sys.path, so
import this as:

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from series import SERIES, pick_series
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SERIES = {
    "beginner": {
        "src": ROOT / "MD" / "Beginner",
        "pdf": ROOT / "PDF" / "Beginner",
        "builder": ROOT / "build" / "build_beginner_pdfs.py",
    },
    "business": {
        "src": ROOT / "MD" / "BeginnerBusiness",
        "pdf": ROOT / "PDF" / "BeginnerBusiness",
        "builder": ROOT / "build" / "build_beginner_business_pdfs.py",
    },
}

DEFAULT = "beginner"


def pick_series(argv: list[str]) -> tuple[dict, list[str]]:
    """Split `--series NAME` out of argv, leaving the positional filters.

    Returns (config, remaining_argv). Defaults to the general Beginner series,
    so every existing invocation of these scripts behaves exactly as before.
    """
    name = DEFAULT
    rest: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--series":
            if i + 1 >= len(argv):
                raise SystemExit("--series needs a value: " + " | ".join(SERIES))
            name = argv[i + 1]
            i += 2
            continue
        if arg.startswith("--series="):
            name = arg.split("=", 1)[1]
            i += 1
            continue
        rest.append(arg)
        i += 1
    if name not in SERIES:
        raise SystemExit(f"unknown series {name!r}: " + " | ".join(SERIES))
    return SERIES[name], rest
