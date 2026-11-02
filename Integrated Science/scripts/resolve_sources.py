# -*- coding: utf-8 -*-
import json, os

SUBJ = {"INTG": "통합과학", "PHY1": "물리학1", "CHM1": "화학1", "BIO1": "생명과학1", "ESS1": "지구과학1"}
GRADE = {"H1": "고1", "H2": "고2"}

with open("scripts/set1_items.json", encoding="utf-8") as f:
    items = json.load(f)

out = []
for it in items:
    fname = f"{it['year']}년-{it['month']:02d}월-{GRADE[it['grade']]}-{SUBJ[it['subj_code']]}-문제.pdf"
    path = os.path.join("inbox", fname)
    exists = os.path.exists(path)
    out.append((it["n"], fname, exists, it["orig_no"]))

for n, fname, exists, orig_no in out:
    print(n, fname, "OK" if exists else "MISSING!!", "#" + str(orig_no))
