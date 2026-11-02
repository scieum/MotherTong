# -*- coding: utf-8 -*-
"""확정된 산화·환원 문항을 원본 PDF에서 크롭하고 manifest를 만든다.

일반 학평 PDF는 crop_engine(문항 번호 워드 기준)으로, 텍스트 레이어가 없는
수능 예시문항 PDF는 눈으로 맞춘 좌표로 잘라낸다.
"""
import json
import os
import sys

import fitz
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crop_engine import crop_item, ZOOM, FONT_BOLD
from redox_selection import entries

OUT = "output/items/redox"
os.makedirs(OUT, exist_ok=True)


def crop_by_clip(job, out_path):
    """이미지 PDF용: 좌표로 자르고 위쪽에 새 번호 띠를 덧붙인다(원본 번호는 유지)."""
    doc = fitz.open(os.path.join("inbox", job["file"]))
    page = doc[job["page"]]
    pix = page.get_pixmap(clip=fitz.Rect(*job["clip"]),
                          matrix=fitz.Matrix(ZOOM, ZOOM), alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    band = int(img.height * 0.05)
    canvas = Image.new("RGB", (img.width, img.height + band), "white")
    canvas.paste(img, (0, band))
    draw = ImageDraw.Draw(canvas)
    draw.text((4, 2), f"{job['seq']}.", fill="black",
              font=ImageFont.truetype(FONT_BOLD, int(band * 0.85)))
    canvas.save(out_path)
    doc.close()


keys = json.load(open("scripts/answer_keys.json", encoding="utf-8"))
manifest, fails = [], []

for it in entries():
    out_path = f"{OUT}/redox_{it['seq']:02d}.png"
    if it["image"]:
        crop_by_clip(it, out_path)
        answer = it["answer"]
    else:
        ok, info = crop_item(os.path.join("inbox", it["file"]), it["no"], it["seq"], "",
                             out_path, keep_score=True)
        if not ok:
            fails.append((it["stem"], it["no"], info))
            continue
        answer = keys.get(it["stem"], {}).get(str(it["no"]))
    manifest.append({"seq": it["seq"], "png": out_path, "stem": it["stem"],
                     "orig_no": it["no"], "label": it.get("label"),
                     "topic": it["topic"], "tier": it["tier"], "answer": answer})

json.dump(manifest, open("scripts/redox_manifest.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"크롭 {len(manifest)}개 (A {sum(1 for m in manifest if m['tier']=='A')}, "
      f"B {sum(1 for m in manifest if m['tier']=='B')})")
noans = [m for m in manifest if m["answer"] is None]
if noans:
    print("정답 미확보:", [(m["seq"], m["stem"], m["orig_no"]) for m in noans])
if fails:
    print("크롭 실패:", fails)
