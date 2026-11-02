# -*- coding: utf-8 -*-
"""중화 반응 후보를 키워드로 1차 선별한다.

'수산화 나트륨'의 '산화'처럼 화합물 이름에 들어 있는 글자가 오탐원이므로 먼저 가린다.
중화는 '중화'라는 낱말 없이 혼합 용액 계산만 묻는 문항이 많아 그물을 넓게 친다.
"""
import json
import re

MASK = re.compile(r"(이산화|일산화|삼산화|과산화|수산화|이 산화|과 산화|수 산화)")

STRONG = ["중화", "중화점", "중화열", "알짜 이온"]
WEAK = ["혼합 용액", "혼합한 용액", "혼합하", "혼합 전", "최고 온도", "제산제", "위산",
        "석회 가루", "비린내", "벌에 쏘", "암모니아수", "생성된 물", "물 분자",
        "액성", "산성", "중성", "염기성", "HCl", "NaOH", "KOH", "염산", "지시약",
        "BTB", "페놀프탈레인", "리트머스"]

items = json.load(open("scripts/all_items_text.json", encoding="utf-8"))
hits = []
for it in items:
    t = re.sub(r"\s+", " ", it["text"])
    probe = MASK.sub("◇", t)
    s = [k for k in STRONG if k in probe]
    w = [k for k in WEAK if k in probe]
    if s or len(w) >= 2:          # 약한 표지는 2개 이상 겹칠 때만 후보로 본다
        hits.append({**it, "text": t, "strong": s, "weak": w})

hits.sort(key=lambda h: (0 if h["strong"] else 1, h["file"], h["no"]))
json.dump(hits, open("scripts/neutral_candidates.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("후보", len(hits), "/ 전체", len(items),
      "| strong", sum(1 for h in hits if h["strong"]),
      "| weak만", sum(1 for h in hits if not h["strong"]))
