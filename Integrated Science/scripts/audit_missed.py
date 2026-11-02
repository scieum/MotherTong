# -*- coding: utf-8 -*-
"""누락 감사: 훨씬 넓은 그물로 다시 훑어, 앞선 1차 선별에 걸리지 않은 문항만 뽑는다."""
import json
import re

BROAD = [
    # 산화·환원 쪽
    "산화", "환원", "연소", "부식", "녹", "제련", "철광석", "용광로", "전자를", "전자가",
    "광합성", "세포 호흡", "호흡", "표백", "살균", "이온화 경향", "반응성", "석출",
    # 산·염기 쪽
    "산성", "염기성", "액성", "지시약", "리트머스", "BTB", "페놀프탈레인", "메틸",
    "pH", "수소 이온", "수산화 이온", "염산", "황산", "질산", "아세트산", "탄산",
    "수산화", "암모니아", "식초", "비눗물", "제산제", "위산", "레몬", "전해질",
    "이온화", "중화", "산과 염기", "산 수용액", "염기 수용액",
]

items = json.load(open("scripts/all_items_text.json", encoding="utf-8"))
seen = set()
for f in ("scripts/redox_candidates.json", "scripts/acidbase_candidates.json"):
    for x in json.load(open(f, encoding="utf-8")):
        seen.add((x["file"], x["no"]))

hits = []
for it in items:
    t = re.sub(r"\s+", " ", it["text"])
    kw = [k for k in BROAD if k in t]
    if kw and (it["file"], it["no"]) not in seen:
        hits.append({**it, "text": t, "kw": kw})

json.dump(hits, open("scripts/audit_missed.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("넓은 그물에 걸린 문항", sum(1 for it in items
      if any(k in re.sub(r'\s+', ' ', it['text']) for k in BROAD)),
      "| 1차 선별에 없던 것", len(hits))
