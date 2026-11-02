# -*- coding: utf-8 -*-
"""과거 fill 스크립트들에서 문항 메타데이터를 모두 수집해
현재 xlsx 풀(pool_existing.json)에 없는 것만 pool_extras.json으로 저장."""
import ast
import json
import re

pool = json.load(open('scripts/pool_existing.json', encoding='utf-8'))
used = {(i['year'], i['month'], i['grade'], i['subj_code'], i['orig_no']) for i in pool}

extras = {}

def add(year, month, grade, subj_code, orig_no, rec):
    key = (year, month, grade, subj_code, orig_no)
    if key in used or key in extras:
        return
    extras[key] = rec

def parse_rows(path):
    text = open(path, encoding='utf-8').read()
    m = re.search(r'^rows = (\[.*?^\])', text, re.S | re.M)
    if not m:
        return []
    src = m.group(1)
    src = re.sub(r'\b(PENDING|NEW_DOMAIN|NEW_STD)\b', '"x"', src)
    return ast.literal_eval(src)

# fill_set1_sample_v2.py: 15필드 (subj_code 없음 → INTG)
for r in parse_rows('scripts/fill_set1_sample_v2.py'):
    if len(r) == 15:
        (n, score, subj, domain, std, _std15, topic, ans, diff,
         yr, mo, grade, origno, origscore, mtype) = r
        sc = 'INTG'
    else:
        (n, score, subj, domain, std, _std15, topic, ans, diff,
         yr, mo, grade, origno, origscore, mtype, sc) = r
    add(yr, mo, grade, sc, origno, dict(
        subject=subj, domain=domain, standard=std, topic=topic, answer=ans,
        difficulty=diff, year=yr, month=mo, grade=grade, orig_no=origno,
        orig_score=origscore, material=mtype, subj_code=sc, src='fill_set1_v2'))

for f in ['scripts/fill_set2.py', 'scripts/fill_set3.py']:
    for r in parse_rows(f):
        (n, score, subj, domain, std, _std15, topic, ans, diff,
         yr, mo, grade, origno, origscore, mtype, sc) = r
        add(yr, mo, grade, sc, origno, dict(
            subject=subj, domain=domain, standard=std, topic=topic, answer=ans,
            difficulty=diff, year=yr, month=mo, grade=grade, orig_no=origno,
            orig_score=origscore, material=mtype, subj_code=sc, src=f))

out = list(extras.values())
with open('scripts/pool_extras.json', 'w', encoding='utf-8') as fo:
    json.dump(out, fo, ensure_ascii=False, indent=1)

print('extras:', len(out))
for e in out:
    print(" {}-{:02d} {} {} no{} {} {} ans={} diff={} | {}".format(
        e['year'], e['month'], e['grade'], e['subj_code'], e['orig_no'],
        e['standard'], e['orig_score'], e['answer'], e['difficulty'], e['topic']))
