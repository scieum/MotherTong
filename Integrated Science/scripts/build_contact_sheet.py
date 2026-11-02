# -*- coding: utf-8 -*-
from PIL import Image
import glob
import os

paths = sorted(glob.glob("output/items/set1_*.png"))
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
from PIL import ImageDraw, ImageFont
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 20)
for i, (name, th) in enumerate(thumbs):
    r, c = divmod(i, cols)
    x, y = c * cell_w, r * cell_h
    draw.text((x + 5, y + 2), name, fill="red", font=font)
    sheet.paste(th, (x + 5, y + 26))

sheet.save("output/qc/contact_sheet_set1.png")
print("saved", sheet.size)
