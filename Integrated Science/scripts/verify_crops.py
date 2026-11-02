# -*- coding: utf-8 -*-
"""전 문항 크롭 완전성 검사: 크롭 영역(clip) 안에 마지막 선택지(⑤)가 들어오는지 확인.
⑤ 워드가 텍스트로 추출되지 않는 원본은 'no-choice-text'로 표시(육안 확인 대상)."""
import json
import os
import sys

import fitz

sys.path.insert(0, 'scripts')
from crop_engine import (detect_columns, find_column_divider, find_number_word,
                         find_page_number_cutoff, locate_item)

SUBJ = {"INTG": "통합과학", "PHY1": "물리학1", "CHM1": "화학1", "BIO1": "생명과학1", "ESS1": "지구과학1"}
GRADE = {"H1": "고1", "H2": "고2"}

problems = []
for prefix in ('set1', 'set2', 'set3'):
    items = json.load(open(f'scripts/{prefix}_items.json', encoding='utf-8'))
    for it in items:
        fname = f"{it['year']}년-{it['month']:02d}월-{GRADE[it['grade']]}-{SUBJ[it['subj_code']]}-문제.pdf"
        doc = fitz.open(os.path.join('inbox', fname))
        pno, page, w, w_next = locate_item(doc, it['orig_no'])
        if w is None:
            problems.append((prefix, it['n'], 'NOT FOUND'))
            doc.close()
            continue
        cols = detect_columns(page)
        col = 'L' if w[0] < find_column_divider(page) else 'R'
        cx0, cx1 = cols[col]
        top = w[1] - 6
        if w_next is not None and abs(w_next[0] - w[0]) < 30:
            bottom = w_next[1] - 6
        else:
            bottom = page.rect.height * 0.92
            pn_y = find_page_number_cutoff(page, (cx0, cx1))
            if pn_y is not None and pn_y - 10 > top:
                bottom = min(bottom, pn_y - 10)
        circ = [x for x in page.get_text('words')
                if any(c in x[4] for c in '①②③④⑤')
                and cx0 - 20 <= x[0] <= cx1 + 20
                and top < x[1] < bottom + 8 and x[3] > bottom]
        if circ:
            bottom = max(x[3] for x in circ) + 3
        # 해당 컬럼·문항 y구간의 ⑤ 워드
        fives = [x for x in page.get_text('words')
                 if '⑤' in x[4] and cx0 - 20 <= x[0] <= cx1 + 20 and x[1] > top]
        fives_in = [x for x in fives if x[3] <= bottom + 2]
        fives_below = [x for x in fives if x[3] > bottom + 2 and (w_next is None or x[1] < (w_next[1] if abs(w_next[0]-w[0]) < 30 else 1e9))]
        if not fives:
            problems.append((prefix, it['n'], f'no-choice-text ({fname} #{it["orig_no"]})'))
        elif not fives_in and fives_below:
            problems.append((prefix, it['n'], f'TRUNCATED? bottom={bottom:.0f} first⑤y={fives_below[0][1]:.0f} ({fname} #{it["orig_no"]})'))
        doc.close()

if problems:
    for p in problems:
        print(p)
else:
    print('전 75문항 ⑤ 선택지 포함 확인')
print('검사 종료:', len(problems), '건 표시')
