# -*- coding: utf-8 -*-
"""지정한 회차 시트의 25문항을 JSON으로 추출한다."""
import openpyxl
import json
import sys

sheet_name = sys.argv[1]   # 예: 회차1
out_prefix = sys.argv[2]   # 예: set1

wb = openpyxl.load_workbook("통합과학_모의고사_3회차_양식.xlsx", data_only=False)
ws = wb[sheet_name]

items = []
for r in range(3, 28):
    n = ws[f"A{r}"].value
    items.append({
        "n": n, "score": ws[f"B{r}"].value, "domain": ws[f"D{r}"].value,
        "orig_score": ws[f"P{r}"].value, "year": ws[f"L{r}"].value, "month": ws[f"M{r}"].value,
        "grade": ws[f"N{r}"].value, "orig_no": ws[f"O{r}"].value, "subj_code": ws[f"U{r}"].value,
        "answer": ws[f"I{r}"].value, "topic": ws[f"H{r}"].value,
    })

with open(f"scripts/{out_prefix}_items.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)
print("saved", len(items), "items ->", f"scripts/{out_prefix}_items.json")
