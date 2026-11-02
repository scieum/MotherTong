# -*- coding: utf-8 -*-
"""화학 반응에서의 열 출입(발열·흡열) 후보를 키워드로 1차 선별한다.

'수산화 나트륨'의 '산화'처럼 화합물 이름에 들어 있는 글자는 먼저 가린다.
'열 출입'이라는 말 없이 실생활 사례(손난로·냉각 팩·제설제)만 제시하는 문항이
많아 그물을 넓게 친다.
"""
import json
import re

MASK = re.compile(r"(이산화|일산화|삼산화|과산화|수산화|이 산화|과 산화|수 산화)")

STRONG = ["발열 반응", "흡열 반응", "발열", "흡열", "열을 방출", "열을 흡수",
          "열 출입", "열의 출입", "에너지를 방출", "에너지를 흡수",
          "주위로 열", "주위의 열", "주위로부터 열"]
WEAK = ["손난로", "냉각 팩", "냉찜질", "발열 도시락", "제설제", "온도가 높아",
        "온도가 낮아", "온도 변화", "최고 온도", "질산 암모늄", "염화 칼슘",
        "산화 칼슘", "연소", "중화", "에너지 출입", "반응물의 에너지", "생성물의 에너지"]

items = json.load(open("scripts/all_items_text.json", encoding="utf-8"))
hits = []
for it in items:
    t = re.sub(r"\s+", " ", it["text"])
    probe = MASK.sub("◇", t)
    s = [k for k in STRONG if k in probe]
    w = [k for k in WEAK if k in probe]
    if s or len(w) >= 2:
        hits.append({**it, "text": t, "strong": s, "weak": w})

hits.sort(key=lambda h: (0 if h["strong"] else 1, h["file"], h["no"]))
json.dump(hits, open("scripts/heat_candidates.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("후보", len(hits), "/ 전체", len(items),
      "| strong", sum(1 for h in hits if h["strong"]),
      "| weak만", sum(1 for h in hits if not h["strong"]))
