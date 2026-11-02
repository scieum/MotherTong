# -*- coding: utf-8 -*-
"""
D3 배열 보정: 각 회차의 25번(마지막 문항)이 그 회차 최고난도가 되도록 재배치.
- 회차1: 22 <-> 25 교환 (25번 난이도 4 -> 5, 자연선택 모의실험)
- 회차2: 변경 없음 (25번이 이미 난이도 5)
- 회차3: 22 <-> 25 교환 (25번 난이도 4 -> 5, DNA 염기 결합 규칙성)
교환 문항이 모두 2.5점이라 배점 패턴(22~25번 2.5점) 불변, R1(연속 동일영역 <=2)
사전 시뮬레이션 통과 확인 후 적용. 문항 내용은 그대로, 위치만 교환한다.
"""
import openpyxl
from copy import copy

SRC = "통합과학_모의고사_3회차_양식.xlsx"
wb = openpyxl.load_workbook(SRC, data_only=False)

FIELDS = ["B", "C", "D", "E", "G", "H", "I", "J", "L", "M", "N", "O", "P", "Q", "U"]


def swap(sheet_name, pos_a, pos_b):
    ws = wb[sheet_name]
    ra, rb = pos_a + 2, pos_b + 2
    for col in FIELDS:
        ca, cb = ws[f"{col}{ra}"], ws[f"{col}{rb}"]
        a = {"value": ca.value, "font": copy(ca.font), "fill": copy(ca.fill),
             "border": copy(ca.border), "alignment": copy(ca.alignment),
             "number_format": ca.number_format}
        ca.value = cb.value
        ca.font = copy(cb.font); ca.fill = copy(cb.fill)
        ca.border = copy(cb.border); ca.alignment = copy(cb.alignment)
        ca.number_format = cb.number_format
        cb.value = a["value"]
        cb.font = a["font"]; cb.fill = a["fill"]
        cb.border = a["border"]; cb.alignment = a["alignment"]
        cb.number_format = a["number_format"]


swap("회차1", 22, 25)
swap("회차3", 22, 25)

wb["회차1"]["A29"] = (
    "v8 — 마지막 문항 최고난도 규칙 적용(2026-09-02): 22<->25 교환으로 25번을 난이도 5"
    "(자연선택 모의실험)로 배치. 내용·정답·출처는 v7과 동일, 위치만 교환."
)
wb["회차3"]["A29"] = (
    "마지막 문항 최고난도 규칙 적용(2026-09-02): 22<->25 교환으로 25번을 난이도 5"
    "(DNA 염기 결합 규칙성과 조합의 경우의 수)로 배치. 내용·정답·출처는 이전과 동일, 위치만 교환. "
    "회차2는 25번이 이미 난이도 5라 변경 없음."
)

wb.save(SRC)
print("saved: 회차1 22<->25, 회차3 22<->25 (회차2 변경 없음)")
