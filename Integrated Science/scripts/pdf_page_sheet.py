# -*- coding: utf-8 -*-
"""렌더링된 시험지 PDF의 전 페이지를 한 장의 시트로 만들어 QC용으로 저장."""
import sys
import fitz
from PIL import Image

prefix = sys.argv[1]
label = sys.argv[2]
pdf = f"output/staging/{prefix}_{label}_시험지.pdf"
doc = fitz.open(pdf)
zoom = 0.7
pages = []
for p in doc:
    pix = p.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    pages.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
cols = 4
rows = (len(pages) + cols - 1) // cols
w, h = pages[0].width, pages[0].height
sheet = Image.new("RGB", (w * cols + 20 * (cols + 1), h * rows + 20 * (rows + 1)), "gray")
for i, im in enumerate(pages):
    r, c = divmod(i, cols)
    sheet.paste(im, (20 + c * (w + 20), 20 + r * (h + 20)))
out = f"output/qc/pages_{prefix}.png"
sheet.save(out)
print(pdf, "->", len(pages), "pages", out)
