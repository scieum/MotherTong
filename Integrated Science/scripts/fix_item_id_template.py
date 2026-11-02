# -*- coding: utf-8 -*-
"""
ExamForge xlsx 템플릿 패치: item_id 충돌 방지를 위해 '출처과목코드' 열(T)을 추가하고
item_id 수식이 과목 코드를 포함하도록 변경한다.

대상: 회차1, 회차2, 회차3, 문항은행 시트
근거: CLAUDE.md '매핑 범위 확장' / 'item_id 체계 보강' 항목
"""
import openpyxl
from copy import copy

SRC = "통합과학_모의고사_3회차_양식.xlsx"
CODE_LIST = "INTG,PHY1,CHM1,BIO1,ESS1"

wb = openpyxl.load_workbook(SRC, data_only=False)


def copy_style(src_cell, dst_cell):
    dst_cell.font = copy(src_cell.font)
    dst_cell.fill = copy(src_cell.fill)
    dst_cell.border = copy(src_cell.border)
    dst_cell.alignment = copy(src_cell.alignment)
    dst_cell.number_format = src_cell.number_format


# ---------- 1. 회차1 / 회차2 / 회차3 ----------
for sn in ["회차1", "회차2", "회차3"]:
    ws = wb[sn]

    # 제목 병합 범위를 T열까지 확장
    ws.unmerge_cells("A1:S1")
    ws.merge_cells("A1:T1")

    # T열 폭
    ws.column_dimensions["T"].width = 14

    # 헤더 (T2) — K2 스타일 복제
    t2 = ws["T2"]
    t2.value = "출처과목코드"
    copy_style(ws["K2"], t2)

    # 예시 행 (T3)
    t3 = ws["T3"]
    t3.value = "INTG"
    copy_style(ws["K3"], t3)

    # 입력 행 (T4:T27) — 각 행의 K열 스타일 복제, 값은 비움
    for r in range(4, 28):
        tcell = ws[f"T{r}"]
        tcell.value = None
        copy_style(ws[f"K{r}"], tcell)

    # 드롭다운 검증
    dv = openpyxl.worksheet.datavalidation.DataValidation(
        type="list", formula1=f'"{CODE_LIST}"', allow_blank=True
    )
    ws.add_data_validation(dv)
    dv.add(f"T3:T27")

    # item_id(Q열) 수식 갱신 — 과목코드(T) 포함
    for r in range(3, 28):
        ws[f"Q{r}"] = (
            f'=IF(OR($K{r}="",$L{r}="",$M{r}="",$T{r}="",$N{r}=""),"",'
            f'$K{r}&TEXT($L{r},"00")&"_"&$M{r}&"_"&$T{r}&"_"&TEXT($N{r},"00"))'
        )

# ---------- 2. 문항은행 ----------
ws = wb["문항은행"]
ws.unmerge_cells("A1:S1")
ws.merge_cells("A1:T1")
ws.column_dimensions["T"].width = 14

t3 = ws["T3"]
t3.value = "출처과목코드"
copy_style(ws["S3"], t3)

t4 = ws["T4"]
t4.value = "INTG"
copy_style(ws["S4"], t4)

for r in range(5, 305):
    tcell = ws[f"T{r}"]
    tcell.value = None
    copy_style(ws[f"S{r}"], tcell)

dv = openpyxl.worksheet.datavalidation.DataValidation(
    type="list", formula1=f'"{CODE_LIST}"', allow_blank=True
)
ws.add_data_validation(dv)
dv.add("T4:T304")

for r in range(4, 305):
    ws[f"A{r}"] = (
        f'=IF(OR($B{r}="",$C{r}="",$D{r}="",$T{r}="",$E{r}=""),"",'
        f'$B{r}&TEXT($C{r},"00")&"_"&$D{r}&"_"&$T{r}&"_"&TEXT($E{r},"00"))'
    )

# ---------- 3. 기준 시트 — 출처 과목 코드 legend 추가 ----------
ws = wb["기준"]

title = ws["A89"]
title.value = "6. 출처 과목 코드 (item_id 충돌 방지용)"
copy_style(ws["A72"], title)
ws.merge_cells("A89:G89")

hdr_row = 90
headers = ["코드", "과목명", "교육과정", "비고"]
for i, h in enumerate(headers):
    c = ws.cell(row=hdr_row, column=1 + i, value=h)
    copy_style(ws["A73"], c)

rows = [
    ("INTG", "통합과학", "2015/2022 개정", "학년(H1/H2)으로 2015·2022 시기 구분됨 — 코드 공용"),
    ("PHY1", "물리학Ⅰ", "2015 개정", "고2 선택과목. 통합과학 중복 주제 문항 조달용"),
    ("CHM1", "화학Ⅰ", "2015 개정", "고2 선택과목. 통합과학 중복 주제 문항 조달용"),
    ("BIO1", "생명과학Ⅰ", "2015 개정", "고2 선택과목. 통합과학 중복 주제 문항 조달용"),
    ("ESS1", "지구과학Ⅰ", "2015 개정", "고2 선택과목. 통합과학 중복 주제 문항 조달용"),
]
for i, row in enumerate(rows):
    r = hdr_row + 1 + i
    for j, val in enumerate(row):
        ws.cell(row=r, column=1 + j, value=val)

note = ws.cell(row=hdr_row + 1 + len(rows) + 1, column=1)
note.value = (
    "비고: 동일 연·월·학년에 서로 다른 과목의 원본번호가 겹칠 수 있어 "
    "item_id에 과목코드를 포함시킨다. 예: 201903_H2_PHY1_07"
)

wb.save(SRC)
print("saved")
