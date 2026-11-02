# -*- coding: utf-8 -*-
"""2026-09 고1 문제 PDF에서 23번 문항의 레이아웃 확인."""
import fitz
import sys
sys.path.insert(0, 'scripts')
from crop_engine import find_number_word, find_column_divider

doc = fitz.open(r"inbox\2026년-09월-고1-통합과학-문제.pdf")
print('pages:', doc.page_count)
for pno in range(doc.page_count):
    page = doc[pno]
    mid = find_column_divider(page)
    for num in (22, 23, 24, 25):
        w = find_number_word(page, num)
        if w:
            col = 'L' if w[0] < mid else 'R'
            print(f'p{pno+1} #{num}: x0={w[0]:.0f} y0={w[1]:.0f} col={col} (mid={mid:.0f}, pageH={page.rect.height:.0f})')
