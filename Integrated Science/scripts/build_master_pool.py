# -*- coding: utf-8 -*-
"""마스터 풀 병합 + R-205 3회차 소요 대비 수급 검산.
high = 원본 3점/2.5점(→2.5점 배정 가능), low = 원본 2점/1.5점(→1.5/2점 배정)."""
import json
from collections import defaultdict

DOMAIN_OF = {
    '10통과1-01': '과학의 기초', '10통과1-02': '물질과 규칙성', '10통과1-03': '시스템과 상호작용',
    '10통과2-01': '변화와 다양성', '10통과2-02': '환경과 에너지', '10통과2-03': '과학과 미래 사회',
}
SUBJ_OF = {'10통과1': '통합과학1', '10통과2': '통합과학2'}

def norm(std):
    return std.strip() if std else std

items = {}

def key_of(i):
    return (i['year'], i['month'], i['grade'], i.get('subj_code', 'INTG'), i['orig_no'])

def put(rec):
    k = key_of(rec)
    if k not in items:
        items[k] = rec

# 1) 기존 xlsx 75문항
for i in json.load(open('scripts/pool_existing.json', encoding='utf-8')):
    put(dict(
        year=i['year'], month=i['month'], grade=i['grade'], subj_code=i['subj_code'],
        orig_no=i['orig_no'], standard=norm(i['standard']), topic=i['topic'],
        answer=i['answer'], difficulty=i['difficulty'], orig_score=i['orig_score'],
        material=i['material'], calc=None, boki=None, origin='xlsx'))

# 2) 과거 스크립트 미사용분
for i in json.load(open('scripts/pool_extras.json', encoding='utf-8')):
    put(dict(
        year=i['year'], month=i['month'], grade=i['grade'], subj_code=i['subj_code'],
        orig_no=i['orig_no'], standard=norm(i['standard']), topic=i['topic'],
        answer=i['answer'], difficulty=i['difficulty'], orig_score=i['orig_score'],
        material=i['material'], calc=None, boki=None, origin='extras'))

# 3) 신규 카탈로그
import os
CATALOGS = [('scripts/catalog_202609_H2.json', 2026, 9, 'H2'),
            ('scripts/catalog_202609_H1.json', 2026, 9, 'H1'),
            ('scripts/catalog_201911_H1.json', 2019, 11, 'H1'),
            ('scripts/catalog_201811_H1.json', 2018, 11, 'H1'),
            ('scripts/catalog_201909_H1.json', 2019, 9, 'H1')]
CATALOGS = [c for c in CATALOGS if os.path.exists(c[0])]
for fname, yr, mo, gr in CATALOGS:
    for i in json.load(open(fname, encoding='utf-8')):
        put(dict(
            year=yr, month=mo, grade=gr, subj_code='INTG',
            orig_no=i['orig_no'], standard=norm(i['standard']), topic=i['topic'],
            answer=i['answer'], difficulty=i['difficulty'], orig_score=i['orig_score'],
            material=i['material'], calc=i.get('calc'), boki=i.get('boki'),
            scope_risk=i.get('scope_risk', False), origin=fname))

pool = list(items.values())
for p in pool:
    p['subject'] = SUBJ_OF[p['standard'][:5]]
    p['domain'] = DOMAIN_OF[p['standard'][:8]]
    p['high'] = p['orig_score'] in ('3점', '2.5점')

json.dump(pool, open('scripts/master_pool.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# 수급 검산 — needed_3sets
NEED = {
    '10통과1-01-02': 3, 'A(01-03/01-04)': 3,
    '10통과1-02-02': 3, '10통과1-02-04': 3, '10통과1-02-05': 3, 'B(02-01/02-03/02-06)': 6,
    '10통과1-03-03': 3, '10통과1-03-04': 3, '10통과1-03-05': 6, '10통과1-03-06': 3, 'C(03-01/03-02)': 3,
    '10통과2-01-01': 3, '10통과2-01-02': 3, '10통과2-01-03': 3, '10통과2-01-04': 6, '10통과2-01-05': 3,
    'D(02-01/02-02)': 3, '10통과2-02-03': 3, '10통과2-02-04': 3, '10통과2-02-05': 3, '10통과2-02-06': 3,
    'E(03-01/02/03)': 3,
}
GROUPS = {
    'A(01-03/01-04)': ['10통과1-01-03', '10통과1-01-04'],
    'B(02-01/02-03/02-06)': ['10통과1-02-01', '10통과1-02-03', '10통과1-02-06'],
    'C(03-01/03-02)': ['10통과1-03-01', '10통과1-03-02'],
    'D(02-01/02-02)': ['10통과2-02-01', '10통과2-02-02'],
    'E(03-01/02/03)': ['10통과2-03-01', '10통과2-03-02', '10통과2-03-03'],
}

by_std = defaultdict(list)
for p in pool:
    by_std[p['standard']].append(p)

print('total pool:', len(pool))
print()
print(f"{'need-key':32s} need  have  high  low")
for k, need in NEED.items():
    stds = GROUPS.get(k, [k])
    have = sum(len(by_std[s]) for s in stds)
    high = sum(1 for s in stds for p in by_std[s] if p['high'])
    flag = '  <-- 부족!' if have < need else ''
    print(f"{k:32s} {need:4d}  {have:4d}  {high:4d}  {have-high:4d}{flag}")

# 신설 영역 R-105 체크
print()
print('신설영역(기초·미래) 2025년 미만 문항(사용 불가):')
for p in pool:
    if p['domain'] in ('과학의 기초', '과학과 미래 사회') and p['year'] < 2025:
        print('  ', key_of(p), p['topic'])

# R-207 제외 대상 보유량
for s in ['10통과1-01-01', '10통과2-03-04']:
    if by_std[s]:
        print(f'R-207 제외 {s}: {len(by_std[s])}개 (선정 금지)')

# 그룹 E 상세
print()
print('그룹 E 상세:')
for s in GROUPS['E(03-01/02/03)']:
    for p in by_std[s]:
        print(f"  {s} {p['year']}-{p['month']:02d} {p['grade']} no{p['orig_no']} {p['orig_score']} | {p['topic']}")
