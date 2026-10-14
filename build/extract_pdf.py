"""Extract text from PDFs given as argv paths. Usage: python -I extract_pdf.py out_dir file1.pdf ..."""
import sys
import os
import pypdfium2 as pdfium

out_dir = sys.argv[1]
os.makedirs(out_dir, exist_ok=True)

for path in sys.argv[2:]:
    doc = pdfium.PdfDocument(path)
    parts = []
    for i, page in enumerate(doc):
        parts.append(f"\n===== PAGE {i + 1} =====\n")
        parts.append(page.get_textpage().get_text_range())
    text = "".join(parts)
    name = os.path.splitext(os.path.basename(path))[0]
    dest = os.path.join(out_dir, name + ".txt")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"{name}: {len(doc)} pages, {len(text)} chars -> {dest}")
