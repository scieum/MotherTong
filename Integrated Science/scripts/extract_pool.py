# -*- coding: utf-8 -*-
"""기존 회차1~3 시트의 75문항을 pool_existing.json으로 추출."""
import json
import openpyxl

wb = openpyxl.load_workbook("통합과학_모의고사_3회차_양식.xlsx", data_only=False)

pool = []
for sheet in ["회차1", "회차2", "회차3"]:
    ws = wb[sheet]
    for r in range(3, 28):
        n = ws[f"A{r}"].value
        if n is None:
            continue
        item = {
            "from_set": sheet,
            "pos": n,
            "score_assigned": ws[f"B{r}"].value,
            "subject": ws[f"C{r}"].value,
            "domain": ws[f"D{r}"].value,
            "standard": ws[f"E{r}"].value,
            "topic": ws[f"H{r}"].value,
            "answer": ws[f"I{r}"].value,
            "difficulty": ws[f"J{r}"].value,
            "year": ws[f"L{r}"].value,
            "month": ws[f"M{r}"].value,
            "grade": ws[f"N{r}"].value,
            "orig_no": ws[f"O{r}"].value,
            "orig_score": ws[f"P{r}"].value,
            "material": ws[f"Q{r}"].value,
            "subj_code": ws[f"U{r}"].value,
        }
        pool.append(item)

with open("scripts/pool_existing.json", "w", encoding="utf-8") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)

# 요약 출력
from collections import Counter
print("total:", len(pool))
print("by standard:")
c = Counter(i["standard"] for i in pool)
for k in sorted(c):
    print(" ", k, c[k])
print("by source exam:")
c2 = Counter(f'{i["year"]}-{i["month"]:02d}-{i["grade"]}-{i["subj_code"]}' for i in pool)
for k in sorted(c2):
    print(" ", k, c2[k])
print("orig_score:", Counter(i["orig_score"] for i in pool))
