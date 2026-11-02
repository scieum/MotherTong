# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import glob
import os
import sys

prefix = sys.argv[1]

paths = sorted(glob.glob(f"output/items/{prefix}/{prefix}_*.png"))
thumbs = []
TW = 500
for p in paths:
    im = Image.open(p)
    ratio = TW / im.width
    th = im.resize((TW, int(im.height * ratio)))
    thumbs.append((os.path.basename(p), th))

cols = 5
rows = (len(thumbs) + cols - 1) // cols
cell_h = max(t[1].height for t in thumbs) + 30
cell_w = TW + 10
sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), "white")
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 20)
for i, (name, th) in enumerate(thumbs):
    r, c = divmod(i, cols)
    x, y = c * cell_w, r * cell_h
    draw.text((x + 5, y + 2), name, fill="red", font=font)
    sheet.paste(th, (x + 5, y + 26))

os.makedirs("output/qc", exist_ok=True)
out_path = f"output/qc/contact_sheet_{prefix}.png"
sheet.save(out_path)
print("saved", out_path, sheet.size)
