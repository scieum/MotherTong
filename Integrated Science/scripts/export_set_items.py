# -*- coding: utf-8 -*-
"""sets_final.json → 크롭·조판 파이프라인용 set{1,2,3}_items.json 재생성."""
import json

sets = json.load(open('scripts/sets_final.json', encoding='utf-8'))
NAME2PREFIX = {'회차1': 'set1', '회차2': 'set2', '회차3': 'set3'}

for name, items in sets.items():
    prefix = NAME2PREFIX[name]
    out = []
    for i in sorted(items, key=lambda x: x['pos']):
        out.append({
            'n': i['pos'],
            'score': i['score'],
            'domain': i['domain'],
            'orig_score': i['orig_score'],
            'year': i['year'],
            'month': i['month'],
            'grade': i['grade'],
            'orig_no': i['orig_no'],
            'subj_code': i['subj_code'],
            'answer': i['answer'],
            'topic': i['topic'],
        })
    with open(f'scripts/{prefix}_items.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(prefix, len(out), '문항 저장')
