# -*- coding: utf-8 -*-
"""
회차1~3 시트: U열(출처표기)을 K열로 이동.
K..U 11개 열을 한 칸씩 회전(U -> K, 기존 K..T -> L..U)한다.
item_id/검증/출처표기 수식은 새 열 위치를 참조하도록 다시 쓴다.
"""
import openpyxl
from copy import copy

SRC = "통합과학_모의고사_3회차_양식.xlsx"
wb = openpyxl.load_workbook(SRC, data_only=False)

OLD_COLS = ["K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U"]
# 새 위치 i(=K..U)에 들어갈 값은 old_cols[NEW_ORDER[i]] (0-indexed)
# 회전: [U, K, L, M, N, O, P, Q, R, S, T]
NEW_SOURCE_IDX = [10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

HEADERS = ["출처표기", "출처연도", "출처월", "학년", "원본번호", "원본배점",
           "자료유형", "item_id", "이미지파일명", "검증", "출처과목코드"]


def copy_style(src_cell, dst_cell):
    dst_cell.font = copy(src_cell.font)
    dst_cell.fill = copy(src_cell.fill)
    dst_cell.border = copy(src_cell.border)
    dst_cell.alignment = copy(src_cell.alignment)
    dst_cell.number_format = src_cell.number_format


def formulas_for_row(r):
    return {
        "K": (
            f'=IF(OR($L{r}="",$M{r}="",$N{r}="",$O{r}=""),"",'
            f'$L{r}&" "&IF($N{r}="H1","고1","고2")&" "&$M{r}&"월 "&$O{r}&"번")'
        ),
        "R": (
            f'=IF(OR($L{r}="",$M{r}="",$N{r}="",$U{r}="",$O{r}=""),"",'
            f'$L{r}&TEXT($M{r},"00")&"_"&$N{r}&"_"&$U{r}&"_"&TEXT($O{r},"00"))'
        ),
        "S": f'=IF($R{r}="","",$R{r}&".png")',
        "T": (
            f'=IF($B{r}="","(미입력)",'
            f'IF(AND($P{r}="3점",$B{r}<>2.5),"⚠ 원본 3점은 2.5점이어야 함",'
            f'IF(AND($P{r}="2점",$B{r}=2.5),"⚠ 원본 2점은 2.5점 불가",'
            f'IF(AND(OR($D{r}="과학의 기초",$D{r}="과학과 미래 사회"),$L{r}<2025),"⚠ 신설영역은 2025년 이후 문항만 가능",'
            f'IF(COUNTIF($E$3:$E$27,$E{r})>2,"⚠ 동일 성취기준 3개 이상",'
            f'IF(AND($R{r}<>"",COUNTIF($R$3:$R$27,$R{r})>1),"⚠ 회차 내 문항 중복",'
            f'IF(COUNTIFS($L$3:$L$27,$L{r},$M$3:$M$27,$M{r},$N$3:$N$27,$N{r})>3,'
            f'"⚠ 동일 출처 자산 4문항 이상","OK")))))))'
        ),
    }


for sn in ["회차1", "회차2", "회차3"]:
    ws = wb[sn]

    # ---- 1. 기존 K..U 셀(값+스타일) 스냅샷 ----
    snapshot = {}  # {row: {old_col_letter: cell}}
    for r in range(2, 28):
        snapshot[r] = {}
        for col in OLD_COLS:
            c = ws[f"{col}{r}"]
            snapshot[r][col] = {
                "value": c.value,
                "font": copy(c.font), "fill": copy(c.fill),
                "border": copy(c.border), "alignment": copy(c.alignment),
                "number_format": c.number_format,
            }

    # ---- 2. 새 배치로 값+스타일 이식 (헤더 행 제외하고 우선 스타일/값 이동) ----
    for r in range(2, 28):
        for new_i, new_col in enumerate(OLD_COLS):
            src_col = OLD_COLS[NEW_SOURCE_IDX[new_i]]
            src = snapshot[r][src_col]
            cell = ws[f"{new_col}{r}"]
            cell.font = src["font"]
            cell.fill = src["fill"]
            cell.border = src["border"]
            cell.alignment = src["alignment"]
            cell.number_format = src["number_format"]
            if r == 2:
                cell.value = HEADERS[new_i]
            else:
                # 값은 일단 원래 값을 넣고, 아래에서 수식 열만 재계산해 덮어쓴다.
                cell.value = src["value"]

    # ---- 3. 수식 열(K,R,S,T) 재계산 ----
    for r in range(3, 28):
        f = formulas_for_row(r)
        for col, formula in f.items():
            ws[f"{col}{r}"] = formula

    # ---- 4. 데이터 유효성 검사(드롭다운) 이동 ----
    new_dvs_spec = [
        ("N3:N27", '"H1,H2"'),
        ("Q3:Q27", '"표,그래프,그림,실험 장치,자료 없음"'),
        ("U3:U27", '"INTG,PHY1,CHM1,BIO1,ESS1"'),
        ("P3:P27", '"1.5점,2점,2.5점,3점"'),
    ]
    remove_ranges = {"M3:M27", "P3:P27", "T3:T27", "O3:O27"}
    keep_dvs = []
    for dv in ws.data_validations.dataValidation:
        if str(dv.sqref) not in remove_ranges:
            keep_dvs.append(dv)
    ws.data_validations.dataValidation = keep_dvs
    for rng, formula1 in new_dvs_spec:
        dv = openpyxl.worksheet.datavalidation.DataValidation(
            type="list", formula1=formula1, allow_blank=True
        )
        ws.add_data_validation(dv)
        dv.add(rng)

    # ---- 5. 열 너비 이동 ----
    old_widths = {col: ws.column_dimensions[col].width for col in OLD_COLS}
    for new_i, new_col in enumerate(OLD_COLS):
        src_col = OLD_COLS[NEW_SOURCE_IDX[new_i]]
        ws.column_dimensions[new_col].width = old_widths[src_col]

wb.save(SRC)
print("saved")
