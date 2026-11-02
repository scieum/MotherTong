# -*- coding: utf-8 -*-
import json
import os
import sys

sys.path.insert(0, "scripts")
from crop_engine import crop_item

prefix = sys.argv[1]  # 예: set1

SUBJ = {"INTG": "통합과학", "PHY1": "물리학1", "CHM1": "화학1", "BIO1": "생명과학1", "ESS1": "지구과학1"}
GRADE = {"H1": "고1", "H2": "고2"}


def score_label(v):
    if float(v) == int(v):
        return f"{int(v)}점"
    return f"{v}점"


with open(f"scripts/{prefix}_items.json", encoding="utf-8") as f:
    items = json.load(f)

os.makedirs(f"output/items/{prefix}", exist_ok=True)

fails = []
for it in items:
    fname = f"{it['year']}년-{it['month']:02d}월-{GRADE[it['grade']]}-{SUBJ[it['subj_code']]}-문제.pdf"
    path = os.path.join("inbox", fname)
    out_path = f"output/items/{prefix}/{prefix}_{it['n']:02d}.png"
    ok, info = crop_item(path, it["orig_no"], it["n"], score_label(it["score"]), out_path)
    print(it["n"], "OK" if ok else "FAIL", info if not ok else f"badge={info.get('score_badge_needed')}")
    if not ok:
        fails.append((it["n"], info))

print("\n총", len(items), "개 중 실패", len(fails), "개")
