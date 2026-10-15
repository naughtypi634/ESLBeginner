# Bundled fonts

These four faces are checked in so every machine renders the handouts identically.
`build/preamble.tex` references them by filename, not by installed family name.

## Why they are here

Asking XeTeX for `Noto Sans` / `Montserrat` by name defers the choice to the host:

- macOS ships **variable** cuts (`~/Library/Fonts/Montserrat[wght].ttf`,
  `NotoSansSC[wght].ttf`) whose `wght` axis **defaults to 100**. XeTeX draws only the
  default instance, so every heading came out Thin while a Linux or Windows box with
  static cuts drew them bold — same source, different documents.
- The installed families also differ in coverage: `NotoSans-Regular.ttf` on macOS
  has no U+2192 (→), which is why `esc_latex()` routes symbols through `\eslsym`.

Bundling removes both variables.

## What each file is

| File | Instanced from | Axis pinned |
|---|---|---|
| `NotoSans-Regular.ttf` | `NotoSans[wdth,wght].ttf` | `wdth=100`, `wght=400` |
| `NotoSansSC-Regular.ttf` | `NotoSansSC[wght].ttf` | `wght=400` |
| `Montserrat-Regular.ttf` | `Montserrat[wght].ttf` | `wght=400` |
| `Montserrat-ExtraBold.ttf` | `Montserrat[wght].ttf` | `wght=800` |

Bold Latin and bold CJK are still synthesised at build time (`AutoFakeBold=2.5` in the
preamble), so only the Regular cut of each Noto family is needed. Montserrat's bold is
a real face, wired up as `BoldFont=Montserrat-ExtraBold.ttf`.

## Regenerating

```bash
.venv/bin/python - <<'PY'
import os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

SRC = os.path.expanduser("~/Library/Fonts")
for src, loc, dst in [
    ("Montserrat[wght].ttf",    {"wght": 400},              "Montserrat-Regular.ttf"),
    ("Montserrat[wght].ttf",    {"wght": 800},              "Montserrat-ExtraBold.ttf"),
    ("NotoSans[wdth,wght].ttf", {"wdth": 100, "wght": 400}, "NotoSans-Regular.ttf"),
    ("NotoSansSC[wght].ttf",    {"wght": 400},              "NotoSansSC-Regular.ttf"),
]:
    f = TTFont(os.path.join(SRC, src))
    instancer.instantiateVariableFont(f, loc, updateFontNames=True).save("build/fonts/" + dst)
PY
```

Requires `fonttools` in the venv (`pip install fonttools`).

## Licence

Both families are **SIL Open Font License 1.1**, which permits redistribution —
including bundled with a document toolchain — provided the licence accompanies the
files. Noto Sans and Noto Sans SC © Google. Montserrat © Julieta Ulanovsky
(Direction Générale), released under the OFL.

The upstream `OFL.txt` for each family is not yet in this directory; add it from
<https://github.com/google/fonts/tree/main/ofl/notosans>,
<https://github.com/google/fonts/tree/main/ofl/notosanssc> and
<https://github.com/google/fonts/tree/main/ofl/montserrat> if the handouts are ever
published or redistributed outside this repo.
