# -*- coding: utf-8 -*-
import json
import os
import sys

sys.path.insert(0, "scripts")
from crop_engine import crop_item

SUBJ = {"INTG": "통합과학", "PHY1": "물리학1", "CHM1": "화학1", "BIO1": "생명과학1", "ESS1": "지구과학1"}
GRADE = {"H1": "고1", "H2": "고2"}


def score_label(v):
    # 1.5 -> "1.5점", 2 -> "2점", 2.5 -> "2.5점"
    if float(v) == int(v):
        return f"{int(v)}점"
    return f"{v}점"


with open("scripts/set1_items.json", encoding="utf-8") as f:
    items = json.load(f)

os.makedirs("output/items", exist_ok=True)

results = []
for it in items:
    fname = f"{it['year']}년-{it['month']:02d}월-{GRADE[it['grade']]}-{SUBJ[it['subj_code']]}-문제.pdf"
    path = os.path.join("inbox", fname)
    out_path = f"output/items/set1_{it['n']:02d}.png"
    ok, info = crop_item(path, it["orig_no"], it["n"], score_label(it["score"]), out_path)
    results.append((it["n"], ok, info if not ok else info.get("score_badge_needed")))
    print(it["n"], "OK" if ok else "FAIL", info if not ok else f"badge={info.get('score_badge_needed')}")

failed = [r for r in results if not r[1]]
print("\n총", len(results), "개 중 실패", len(failed), "개")
