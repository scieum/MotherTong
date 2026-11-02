# -*- coding: utf-8 -*-
"""산화·환원 후보를 키워드로 1차 선별한다. 최종 판정은 본문을 읽고 사람이 한다.

'이산화 탄소'·'과산화 수소'처럼 화합물 이름에 들어 있는 '산화'가 최대 오탐원이므로
먼저 가린 뒤 매칭한다.
"""
import json
import re

# '이산화 탄소'의 '산화', '수산화 나트륨'의 '산화'처럼 화합물 이름에 들어 있는
# 글자가 최대 오탐원이므로 먼저 가린 뒤 매칭한다.
MASK = re.compile(r"(이산화|일산화|삼산화|과산화|이 산화|과 산화|수산화|수 산화)")

# 산화·환원 개념을 직접 묻는 표지.
# '산화'·'환원' 단독도 넣는다 — 빈칸(㉠/㉡) 문항은 선택지에만 그 낱말이 나와서
# '산화되다' 같은 활용형으로는 걸리지 않는다(예: 2024년 3월 화학Ⅰ 8번 구리 지붕).
STRONG = ["산화", "환원", "산화 환원", "산화·환원", "산화환원", "산화되", "산화된",
          "환원되", "환원된", "산화제", "환원제", "산화 반응", "환원 반응", "제련",
          "산화수", "전자를 잃", "전자를 얻", "산소를 잃", "산소를 얻"]
# 산화·환원 맥락일 수 있는 주변 표지 (본문 확인 필요)
WEAK = ["연소", "광합성", "세포 호흡", "부식", "녹슨", "녹이 슬", "녹이 스", "녹이 슨",
        "금속의 반응성", "이온화 경향", "석출", "표백", "산화 구리", "산화 철",
        "산화 마그네슘", "산화 칼슘", "산화 알루미늄", "산화 은"]

items = json.load(open("scripts/all_items_text.json", encoding="utf-8"))
hits = []
for it in items:
    t = re.sub(r"\s+", " ", it["text"])
    probe = MASK.sub("◇", t)
    s = [k for k in STRONG if k in probe]
    w = [k for k in WEAK if k in probe]
    if s or w:
        hits.append({**it, "text": t, "strong": s, "weak": w})

hits.sort(key=lambda h: (0 if h["strong"] else 1, h["file"], h["no"]))
json.dump(hits, open("scripts/redox_candidates.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("후보", len(hits), "/ 전체", len(items),
      "| strong", sum(1 for h in hits if h["strong"]),
      "| weak-only", sum(1 for h in hits if not h["strong"]))
