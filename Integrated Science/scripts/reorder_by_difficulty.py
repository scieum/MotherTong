# -*- coding: utf-8 -*-
"""
D3 배열: 2026-03/2026-06 고2 통합과학 실제 기준 시험지의 '번호별 배점' 패턴을
템플릿으로 뽑아(1~9번은 2.5점 없음, 22~25번은 전부 2.5점, 전반 저난도->후반 고난도)
회차1·회차2의 25문항을 그 자리에 재배치한다. 문항 내용(성취기준·정답·출처 등)은
그대로 두고 '번호(위치)'만 재배정한다.

old_pos -> new_pos 매핑은 각 회차의 실제 배점/난이도/영역 데이터를 바탕으로
R1(연속 동일영역 <=2) R2(1~5번 평균난이도<=2.5) R3(21~25번에 난이도4~5 3개 이상)
R4(2.5점 3개 연속 금지, 단 마지막 22~25번 4연속은 실제 기준 시험지 패턴을 따라 예외)
를 만족하도록 배정했다.
"""
import openpyxl
from copy import copy

SRC = "통합과학_모의고사_3회차_양식.xlsx"
wb = openpyxl.load_workbook(SRC, data_only=False)

FIELDS = ["B", "C", "D", "E", "G", "H", "I", "J", "L", "M", "N", "O", "P", "Q", "U"]

# old_pos(1~25) -> new_pos(1~25)
MAP_SET1 = {
    1: 5, 2: 6, 3: 1, 4: 8, 5: 18, 6: 10, 7: 15, 8: 4, 9: 2, 10: 21,
    11: 3, 12: 7, 13: 14, 14: 17, 15: 12, 16: 22, 17: 13, 18: 24, 19: 25, 20: 19,
    21: 11, 22: 16, 23: 23, 24: 20, 25: 9,
}
MAP_SET2 = {
    1: 6, 2: 7, 3: 14, 4: 1, 5: 15, 6: 5, 7: 19, 8: 2, 9: 17, 10: 8,
    11: 4, 12: 22, 13: 23, 14: 16, 15: 24, 16: 11, 17: 18, 18: 3, 19: 25, 20: 20,
    21: 10, 22: 13, 23: 12, 24: 9, 25: 21,
}


def reorder(sheet_name, mapping):
    ws = wb[sheet_name]
    snapshot = {}
    for old_pos in range(1, 26):
        r = old_pos + 2
        snapshot[old_pos] = {}
        for col in FIELDS:
            c = ws[f"{col}{r}"]
            snapshot[old_pos][col] = {
                "value": c.value,
                "font": copy(c.font), "fill": copy(c.fill),
                "border": copy(c.border), "alignment": copy(c.alignment),
                "number_format": c.number_format,
            }
    for old_pos, new_pos in mapping.items():
        r = new_pos + 2
        for col in FIELDS:
            src = snapshot[old_pos][col]
            cell = ws[f"{col}{r}"]
            cell.value = src["value"]
            cell.font = src["font"]
            cell.fill = src["fill"]
            cell.border = src["border"]
            cell.alignment = src["alignment"]
            cell.number_format = src["number_format"]


reorder("회차1", MAP_SET1)
reorder("회차2", MAP_SET2)

for sn, note in [
    ("회차1", "v7 — D3 배열 적용(2026-03/06 고2 기준 시험지의 번호별 배점 패턴을 템플릿으로 재배치). "
              "내용·정답·출처는 v6과 동일, 번호(위치)만 재배정."),
    ("회차2", "D3 배열 적용(회차1과 동일 템플릿 원리로 재배치). 내용·정답·출처는 이전과 동일, 번호만 재배정."),
]:
    wb[sn]["A29"] = note

wb.save(SRC)
print("saved")
