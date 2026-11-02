# -*- coding: utf-8 -*-
"""산·염기 후보를 키워드로 1차 선별한다(중화 반응 문항은 별도 표시).

'산화'가 '산'을 포함하므로 산화·환원 표지를 먼저 가려낸다.
"""
import json
import re

MASK = re.compile(r"(이산화|일산화|삼산화|과산화|산화|환원)")

ACID_BASE = ["산성", "염기성", "액성", "페놀프탈레인", "리트머스", "BTB", "메틸 오렌지",
             "지시약", "pH", "염산", "HCl", "황산", "아세트산", "탄산", "구연산", "레몬",
             "수산화 나트륨", "NaOH", "수산화 칼륨", "KOH", "암모니아", "제산제", "석회 가루",
             "묽은 염산", "수용액의 액성", "H", "OH"]
# 실제로 쓸 표지 (H·OH 단독은 오탐이 심해 이온 표기로만)
ACID_BASE = ["산성", "염기성", "액성", "페놀프탈레인", "리트머스", "BTB", "메틸 오렌지",
             "지시약", "pH", "염산", "HCl", "황산", "아세트산", "탄산 칼슘", "구연산",
             "수산화 나트륨", "NaOH", "수산화 칼륨", "KOH", "암모니아", "제산제", "석회 가루"]
NEUTRAL = ["중화", "알짜 이온", "혼합 용액", "혼합한 용액", "중화점", "중화열"]

items = json.load(open("scripts/all_items_text.json", encoding="utf-8"))
hits = []
for it in items:
    t = re.sub(r"\s+", " ", it["text"])
    probe = MASK.sub("◇", t)
    k = [w for w in ACID_BASE if w in probe]
    n = [w for w in NEUTRAL if w in probe]
    if k:
        hits.append({**it, "text": t, "kw": k, "neutral": n})

hits.sort(key=lambda h: (h["file"], h["no"]))
json.dump(hits, open("scripts/acidbase_candidates.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("후보", len(hits), "/ 전체", len(items),
      "| 중화 표지 있음", sum(1 for h in hits if h["neutral"]))
