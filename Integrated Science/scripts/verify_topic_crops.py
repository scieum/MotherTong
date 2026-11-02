# -*- coding: utf-8 -*-
"""크롭 검증: 모든 문항은 선택지 1~5로 끝나므로, 잘라낸 영역에 원문자가
5개 다 들어 있는지로 잘림 여부를 판정한다. 사용법: python scripts/verify_topic_crops.py <주제키>
"""
import importlib
import os
import sys

import fitz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crop_engine import locate_item, item_segments, _slot_x_range

CIRCLED = set("①②③④⑤")

key = sys.argv[1]
sel = importlib.import_module(f"{key}_selection")

bad = []
for it in sel.entries():
    if it["image"]:
        continue
    doc = fitz.open(os.path.join("inbox", it["file"]))
    pno, page, w, _ = locate_item(doc, it["no"])
    segs, _ = item_segments(doc, pno, w, it["no"])
    found = set()
    for p, c, y0, y1 in segs:
        pg = doc[p]
        xr = _slot_x_range(pg, c)
        for x in pg.get_text("words"):
            if xr[0] - 20 <= x[0] <= xr[1] + 20 and y0 - 2 <= x[1] <= y1 + 10:
                found |= set(x[4]) & CIRCLED
    if len(found) < 5:
        bad.append((it["seq"], it["stem"], it["no"], "".join(sorted(found)),
                    [(p + 1, c) for p, c, _, _ in segs]))
    doc.close()

print(f"{key}: 선택지 5개가 모두 들어간 문항 확인 — 미달 {len(bad)}건")
for b in bad:
    print("   ", b)
