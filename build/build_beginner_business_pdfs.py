#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESLBeginner · Beginner Business English MD -> PDF builder.

The business series has exactly the same shape as the general Beginner series —
level-1 title, numbered level-2 sections, pipe tables, nothing else — so it
reuses build_beginner_pdfs.py's reader, table sizing and preamble wholesale and
only redirects where the files are read from and written to.

build_beginner_pdfs.py resolves its directory globals inside its functions and
never captures them in a default argument, so rebinding the module attributes
here is all that is needed. CJK and SEPARATOR are the only globals bound at
import time, and both are shared constants.

Usage:
    python build/build_beginner_business_pdfs.py            # build every lesson
    python build/build_beginner_business_pdfs.py 07         # only files matching "07"
    python build/build_beginner_business_pdfs.py --png      # also render page-1 previews
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))

import build_beginner_pdfs as B  # noqa: E402

# GEN_DIR and PREVIEW default into build/tex/ and build/preview/, which the
# general series already fills with same-stemmed files (01-…, 02-…); a shared
# directory would silently overwrite them. Give this series its own.
B.SRC_DIR = ROOT / "MD" / "BeginnerBusiness"
B.GEN_DIR = ROOT / "build" / "tex" / "beginner_business"
B.PDF_DIR = ROOT / "PDF" / "BeginnerBusiness"
B.PREVIEW = ROOT / "build" / "preview" / "beginner_business"


if __name__ == "__main__":
    B.main()
