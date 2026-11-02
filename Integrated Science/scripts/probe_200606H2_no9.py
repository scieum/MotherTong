# -*- coding: utf-8 -*-
"""2026-06 고2 통합과학 9번(산·염기) 본문과 해설 정답표 추출."""
import fitz

base = r"inbox\2026년-06월-고2-통합과학-{}.pdf"

doc = fitz.open(base.format("문제"))
print("문제 PDF pages:", len(doc))
for pno in range(len(doc)):
    t = doc[pno].get_text()
    if "\n9." in t or t.startswith("9."):
        print(f"--- page {pno+1} ---")
        print(t[:3000])
        break

sol = fitz.open(base.format("해설"))
print("해설 PDF pages:", len(sol))
print("--- 해설 p1 ---")
print(sol[0].get_text()[:2500])
