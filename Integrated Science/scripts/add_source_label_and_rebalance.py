# -*- coding: utf-8 -*-
"""
1) 회차1/2/3, 문항은행 시트에 '출처표기'(예: 2026 고2 6월 1번) 열(U) 추가.
   기존 연도/월/학년/원본번호 열은 그대로 유지 — U열은 그 값들을 조합한 표기 전용 열.
2) 회차1의 신설 영역 3문항(과학의 기초 2 + 과학과 미래 사회 1)이 전부 2026-06 고2에
   몰려 있던 것을 2025-06 고1 / 2026-06 고1 / 2026-03 고2 세 자산으로 재배분.
"""
import openpyxl
from copy import copy

SRC = "통합과학_모의고사_3회차_양식.xlsx"
wb = openpyxl.load_workbook(SRC, data_only=False)


def copy_style(src_cell, dst_cell):
    dst_cell.font = copy(src_cell.font)
    dst_cell.fill = copy(src_cell.fill)
    dst_cell.border = copy(src_cell.border)
    dst_cell.alignment = copy(src_cell.alignment)
    dst_cell.number_format = src_cell.number_format


# ---------- 1. 회차1/2/3에 출처표기(U) 열 추가 ----------
for sn in ["회차1", "회차2", "회차3"]:
    ws = wb[sn]
    ws.unmerge_cells("A1:T1")
    ws.merge_cells("A1:U1")
    ws.column_dimensions["U"].width = 18

    u2 = ws["U2"]
    u2.value = "출처표기"
    copy_style(ws["T2"], u2)

    u3 = ws["U3"]
    copy_style(ws["T3"], u3)

    for r in range(3, 28):
        cell = ws[f"U{r}"]
        cell.value = (
            f'=IF(OR($K{r}="",$L{r}="",$M{r}="",$N{r}=""),"",'
            f'$K{r}&" "&IF($M{r}="H1","고1","고2")&" "&$L{r}&"월 "&$N{r}&"번")'
        )
        if r >= 4:
            copy_style(ws[f"T{r}"], cell)

# ---------- 2. 문항은행에 출처표기(U) 열 추가 ----------
ws = wb["문항은행"]
ws.unmerge_cells("A1:T1")
ws.merge_cells("A1:U1")
ws.column_dimensions["U"].width = 18

u3 = ws["U3"]
u3.value = "출처표기"
copy_style(ws["T3"], u3)

u4 = ws["U4"]
copy_style(ws["T4"], u4)

for r in range(4, 305):
    cell = ws[f"U{r}"]
    cell.value = (
        f'=IF(OR($B{r}="",$C{r}="",$D{r}="",$E{r}=""),"",'
        f'$B{r}&" "&IF($D{r}="H1","고1","고2")&" "&$C{r}&"월 "&$E{r}&"번")'
    )
    if r >= 5:
        copy_style(ws[f"T{r}"], cell)

# ---------- 3. 회차1 신설 영역 3문항 재배분 ----------
ws = wb["회차1"]

# row1 = 과학의 기초 #1 (기존 2026-06 고2 #4 -> 2025-06 고1 #6, 소리 신호 디지털 변환)
ws["E3"] = "10통과1-01-04"
ws["H3"] = "소리 신호의 디지털 변환과 센서"
ws["I3"] = 4
ws["J3"] = 2
ws["K3"] = 2025
ws["L3"] = 6
ws["M3"] = "H1"
ws["N3"] = 6
ws["O3"] = "1.5점"
ws["P3"] = "그림"

# row2 = 과학의 기초 #2 (기존 2026-06 고2 #6 -> 2026-06 고1 #1, 산 정상부 기본량)
ws["E4"] = "10통과1-01-02"
ws["H4"] = "산 정상부 자료와 기본량의 단위"
ws["I4"] = 4
ws["J4"] = 2
ws["K4"] = 2026
ws["L4"] = 6
ws["M4"] = "H1"
ws["N4"] = 1
ws["O4"] = "1.5점"
ws["P4"] = "자료 없음"

# row25 = 과학과 미래 사회 (기존 2026-06 고2 #25 -> 2026-03 고2 #11, 자율주행차 SSI)
ws["E27"] = "10통과2-03-03"
ws["H27"] = "자율주행 자동차와 과학기술의 사회적 쟁점(SSI)"
ws["I27"] = 5
ws["J27"] = 2
ws["K27"] = 2026
ws["L27"] = 3
ws["M27"] = "H2"
ws["N27"] = 11
ws["O27"] = "1.5점"
ws["P27"] = "자료 없음"

ws["A29"] = (
    "v3 — 신설 영역(과학의 기초·과학과 미래 사회) 3문항을 2025-06 고1 / 2026-06 고1 / 2026-03 고2로 "
    "재배분(2026-06 고2 한 자산 편중 해소). 나머지 22문항 출처는 v2와 동일(9개 자산 분산, 자산당 최대 5문항). "
    "U열('출처표기')은 K·L·M·N열을 조합한 표기 전용 열이며 별도 입력이 필요 없다(자동 계산). "
    "성취기준(2015)은 B1/GATE-2 canon 부재로 공란 유지. D3 재배열 미적용."
)

wb.save(SRC)
print("saved")
