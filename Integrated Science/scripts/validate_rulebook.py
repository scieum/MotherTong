# -*- coding: utf-8 -*-
"""규칙서 v1.2 전 조항 검증 (솔버와 독립된 코드, §7.3 검증 이중화).
입력: scripts/sets_final.json
출력: 규칙 ID별 PASS/FAIL/WARN + 위반 문항.
"""
import json
from collections import Counter, defaultdict

sets = json.load(open('scripts/sets_final.json', encoding='utf-8'))
FAIL, WARN, INFO = [], [], []

def fail(rule, msg): FAIL.append(f'[{rule}] {msg}')
def warn(rule, msg): WARN.append(f'[{rule}] {msg}')
def info(rule, msg): INFO.append(f'[{rule}] {msg}')

DOMS = ['과학의 기초', '물질과 규칙성', '시스템과 상호작용', '변화와 다양성', '환경과 에너지', '과학과 미래 사회']
DOM_TARGET = {'과학의 기초': (2, 1), '물질과 규칙성': (5, 1), '시스템과 상호작용': (6, 0),
              '변화와 다양성': (6, 1), '환경과 에너지': (5, 0), '과학과 미래 사회': (1, 1)}
# R-103 교차 쿼터: {영역: {배점: (target, lo, hi)}}
MATRIX = {
    '과학의 기초':   {1.5: (1, 0, 2), 2.0: (1, 0, 1), 2.5: (0, 0, 0)},
    '물질과 규칙성':  {1.5: (2, 1, 2), 2.0: (3, 3, 3), 2.5: (0, 0, 1)},
    '시스템과 상호작용': {1.5: (1, 0, 2), 2.0: (1, 1, 1), 2.5: (4, 3, 5)},
    '변화와 다양성':  {1.5: (2, 1, 3), 2.0: (2, 1, 3), 2.5: (2, 1, 2)},
    '환경과 에너지':  {1.5: (2, 1, 3), 2.0: (1, 0, 2), 2.5: (2, 2, 2)},
    '과학과 미래 사회': {1.5: (0, 0, 1), 2.0: (1, 0, 1), 2.5: (0, 0, 1)},
}
QUOTA = {  # R-205: std -> (target, lo, hi)  * 로테이션 그룹은 별도
    '10통과1-01-02': (1, 1, 1), '10통과1-02-02': (1, 1, 1), '10통과1-02-04': (1, 0, 2),
    '10통과1-02-05': (1, 0, 2), '10통과1-03-03': (1, 1, 1), '10통과1-03-04': (1, 1, 1),
    '10통과1-03-05': (2, 1, 2), '10통과1-03-06': (1, 1, 1), '10통과2-01-01': (1, 0, 1),
    '10통과2-01-02': (1, 1, 2), '10통과2-01-03': (1, 1, 1), '10통과2-01-04': (2, 2, 2),
    '10통과2-01-05': (1, 0, 1), '10통과2-02-03': (1, 1, 2), '10통과2-02-04': (1, 1, 1),
    '10통과2-02-05': (1, 1, 1), '10통과2-02-06': (1, 1, 1),
}
GROUPS = {
    'A': (['10통과1-01-03', '10통과1-01-04'], 1),
    'B': (['10통과1-02-01', '10통과1-02-03', '10통과1-02-06'], 2),
    'C': (['10통과1-03-01', '10통과1-03-02'], 1),
    'D': (['10통과2-02-01', '10통과2-02-02'], 1),
    'E': (['10통과2-03-01', '10통과2-03-02', '10통과2-03-03'], 1),
}
EXCLUDED = {'10통과1-01-01', '10통과2-03-04'}  # R-207
NEW_DOMAINS = {'과학의 기초', '과학과 미래 사회'}
FIXED_25 = {'10통과1-03-04', '10통과1-03-06', '10통과2-02-05'}  # R-504
FIXED_20 = {'10통과2-01-03'}
FIXED_15 = {'10통과1-02-05'}
EXPECTED = {  # R-505 기대 배점
    '10통과1-01-02': {1.5, 2.0}, '10통과1-01-03': {2.0, 1.5}, '10통과1-01-04': {1.5},
    '10통과1-02-01': {2.0, 1.5}, '10통과1-02-02': {1.5, 2.0, 2.5}, '10통과1-02-03': {2.0, 2.5},
    '10통과1-02-04': {2.0, 2.5}, '10통과1-02-05': {1.5}, '10통과1-02-06': {1.5, 2.0},
    '10통과1-03-01': {1.5, 2.0, 2.5}, '10통과1-03-02': {1.5, 2.0}, '10통과1-03-03': {2.0, 2.5},
    '10통과1-03-04': {2.5}, '10통과1-03-05': {2.0, 2.5, 1.5}, '10통과1-03-06': {2.5},
    '10통과2-01-01': {1.5, 2.0, 2.5}, '10통과2-01-02': {1.5, 2.0, 2.5}, '10통과2-01-03': {2.0},
    '10통과2-01-04': {1.5, 2.0, 2.5}, '10통과2-01-05': {1.5, 2.0},
    '10통과2-02-01': {1.5, 2.0}, '10통과2-02-02': {2.0, 1.5}, '10통과2-02-03': {2.0, 2.5},
    '10통과2-02-04': {1.5, 2.0}, '10통과2-02-05': {2.5}, '10통과2-02-06': {1.5, 2.0, 2.5},
    '10통과2-03-01': {2.0}, '10통과2-03-02': {1.5, 2.0, 2.5}, '10통과2-03-03': {1.5, 2.0},
}

def kid(it):
    return f"{it['year']}{it['month']:02d}_{it['grade']}_{it['subj_code']}_{it['orig_no']:02d}"

all_ids = []
std_3sets = Counter()
group_used = {g: defaultdict(list) for g in GROUPS}

for name, items in sets.items():
    items = sorted(items, key=lambda x: x['pos'])
    n = len(items)
    scores = [i['score'] for i in items]
    doms = [i['domain'] for i in items]
    diffs = [i['difficulty'] for i in items]

    # R-101
    if n != 25 or abs(sum(scores) - 50.0) > 1e-9:
        fail('R-101', f'{name}: {n}문항 / {sum(scores)}점')
    # R-102
    sc = Counter(scores)
    if not (sc[2.5] == 8 and sc[2.0] == 9 and sc[1.5] == 8):
        fail('R-102', f'{name}: 배점 구조 {dict(sc)}')
    # R-103 / R-104 행·열 합계
    dc = Counter(doms)
    if sum(dc.values()) != 25:
        fail('R-104', f'{name}: 영역 합계 {sum(dc.values())}')
    for d in DOMS:
        t, tol = DOM_TARGET[d]
        if abs(dc.get(d, 0) - t) > tol:
            fail('R-103행', f'{name}: {d} {dc.get(d,0)}개 (기준 {t}±{tol})')
    # R-103 교차 쿼터 칸
    for d in DOMS:
        for s_ in (1.5, 2.0, 2.5):
            cnt = sum(1 for i in items if i['domain'] == d and i['score'] == s_)
            tgt, lo, hi = MATRIX[d][s_]
            if d == '과학의 기초' and s_ == 2.5 and cnt > 0:
                fail('R-103a', f'{name}: 과학의 기초에 2.5점 {cnt}개')
            elif not (lo <= cnt <= hi):
                warn('R-103칸', f'{name}: {d}×{s_} = {cnt} (관찰범위 {lo}~{hi})')
    # R-105
    for i in items:
        if i['domain'] in NEW_DOMAINS and i['year'] < 2025:
            fail('R-105', f"{name}#{i['pos']} {kid(i)} 신설영역인데 {i['year']}년")
    # R-201 / R-205
    stc = Counter(i['standard'] for i in items)
    for s_, c in stc.items():
        if c > 2:
            fail('R-201', f'{name}: {s_} {c}문항')
        std_3sets[s_] += c
    for s_, (t, lo, hi) in QUOTA.items():
        if not (lo <= stc.get(s_, 0) <= hi):
            warn('R-205', f'{name}: {s_} {stc.get(s_,0)}개 (범위 {lo}~{hi})')
    for g, (members, per) in GROUPS.items():
        cnt = sum(stc.get(m, 0) for m in members)
        if cnt != per:
            warn('R-205그룹', f'{name}: 그룹{g} {cnt}개 (기준 {per})')
        for m in members:
            if stc.get(m, 0):
                group_used[g][m].append(name)
    # R-202
    pair = [i for i in items if i['standard'] == '10통과2-01-04']
    ps = sorted(i['score'] for i in pair)
    if len(pair) != 2 or ps[0] not in (1.5, 2.0) or ps[1] != 2.5:
        warn('R-202', f'{name}: 산염기 구성 {ps}')
    # R-203/207
    for i in items:
        if i['standard'] in EXCLUDED:
            fail('R-207', f"{name}#{i['pos']} {i['standard']}")
    # R-302
    for i in items:
        if i['answer'] not in (1, 2, 3, 4, 5):
            fail('R-302', f"{name}#{i['pos']} 정답 없음")
    # R-303
    for i in items:
        if i['grade'] == 'H1' and i['month'] == 3:
            fail('R-303', f"{name}#{i['pos']} 고1 3월 자산")
    # R-304 + U-3 (사용자 지정 2026-09-03: 회차당 동일 출처 시험지 최대 3문항)
    src = Counter(f"{i['year']}-{i['month']:02d}-{i['grade']}-{i['subj_code']}" for i in items)
    for s_, c in src.items():
        if c > 3:
            fail('U-3', f'{name}: {s_} {c}문항 (사용자 지정 한도 3)')
    # 연도 분산 요약
    y2026 = sum(1 for i in items if i['year'] == 2026)
    sel = sum(1 for i in items if i['subj_code'] != 'INTG')
    info('U-3', f'{name}: 2026년 {y2026}개 / 2015개정(~2024) {sum(1 for i in items if i["year"] <= 2024)}개 / 고2 3월 선택과목 {sel}개')
    # R-305
    recent = sum(1 for i in items if i['year'] >= 2021)
    if recent / 25 < 0.7:
        warn('R-305', f'{name}: 2021+ 비율 {recent}/25')
    # R-401 / R-402
    if items[0]['score'] != 1.5:
        warn('R-401', f'{name}: 1번 {items[0]["score"]}점')
    if items[24]['score'] != 2.5:
        warn('R-402', f'{name}: 25번 {items[24]["score"]}점')
    # R-403 연속 동일 영역
    run, runs3 = 1, 0
    for a in range(1, 25):
        run = run + 1 if doms[a] == doms[a-1] else 1
        if run == 3:
            runs3 += 1
        if run >= 4:
            fail('R-403', f'{name}: {a-2}~{a+1}번 4연속 {doms[a]}')
    if runs3 > 1:
        warn('R-403', f'{name}: 3연속 {runs3}회')
    # R-404 2.5 연속
    run = 0
    for a in range(25):
        run = run + 1 if scores[a] == 2.5 else 0
        limit = 4 if a + 1 >= 22 else 2
        if run > limit:
            fail('R-404', f'{name}: {a+1}번에서 2.5점 {run}연속')
    # R-405
    for a in range(5):
        if scores[a] == 2.5:
            fail('R-405', f'{name}: {a+1}번 2.5점')
    # R-406
    s1, s2, s3 = sum(scores[:5]), sum(scores[5:18]), sum(scores[18:])
    if not (8.0 <= s1 <= 8.5):
        warn('R-406', f'{name}: 1~5번 합 {s1}')
    if abs(s2 - 25.5) > 1e-9:
        warn('R-406', f'{name}: 6~18번 합 {s2}')
    if not (16.0 <= s3 <= 16.5):
        warn('R-406', f'{name}: 19~25번 합 {s3}')
    # R-407
    for i in items:
        if i['domain'] == '과학의 기초' and i['pos'] > 6:
            warn('R-407', f"{name}#{i['pos']} 과학의 기초")
    # R-408
    if sum(diffs[:5]) / 5 > 2.5 or any(d >= 4 for d in diffs[:5]):
        warn('R-408', f'{name}: 1~5번 난이도 {diffs[:5]}')
    if sum(1 for d in diffs[5:18] if d == 5) > 1:
        warn('R-408', f'{name}: 6~18번 난이도5 {diffs[5:18]}')
    if sum(1 for d in diffs[18:] if d >= 4) < 4:
        warn('R-408', f'{name}: 19~25번 난이도4+ {sum(1 for d in diffs[18:] if d>=4)}개')
    # R-410
    nb = sum(1 for i in items if i.get('boki') is False)
    info('R-410', f'{name}: 비합답형(확인분) {nb}개 (목표 0~4)')
    if nb > 4:
        warn('R-410', f'{name}: 비합답형 {nb}개')
    # R-411
    for i in items:
        if i['pos'] >= 19 and i['score'] == 1.5:
            fail('R-411', f"{name}#{i['pos']} 1.5점")
    # R-412
    calc_late = [i for i in items if i['pos'] >= 22 and i.get('calc')]
    if not (2 <= len(calc_late) <= 3):
        warn('R-412', f'{name}: 22~25번 정량계산형 {len(calc_late)}개')
    # R-501/502/503 원본 배점
    high = [i for i in items if i['orig_score'] in ('3점', '2.5점')]
    low = [i for i in items if i['orig_score'] in ('2점', '1.5점')]
    if len(high) != 8 or len(low) != 17:
        fail('R-501', f'{name}: 고배점 원본 {len(high)} / 저배점 원본 {len(low)}')
    for i in high:
        if i['score'] != 2.5:
            fail('R-502', f"{name}#{i['pos']} 원본 {i['orig_score']} → {i['score']}")
    for i in low:
        if i['score'] == 2.5:
            fail('R-503', f"{name}#{i['pos']} 원본 {i['orig_score']} → 2.5")
    # R-503 난이도 하위 8개 상대순위 (엄격 역전: 차이 2 이상만 FAIL, 1은 경계 → R-506 검토)
    d15 = [i['difficulty'] for i in low if i['score'] == 1.5]
    d20 = [i['difficulty'] for i in low if i['score'] == 2.0]
    if d15 and d20 and max(d15) - min(d20) >= 2:
        fail('R-503순위', f'{name}: 1.5점 최고난도 {max(d15)} vs 2.0점 최저난도 {min(d20)}')
    elif d15 and d20 and max(d15) - min(d20) == 1:
        info('R-506', f'{name}: 난이도 경계선(1.5점 d{max(d15)} vs 2.0점 d{min(d20)}) — 사람 검토 대상')
    # R-504
    for i in items:
        if i['standard'] in FIXED_25 and i['score'] != 2.5:
            fail('R-504', f"{name}#{i['pos']} {i['standard']} → {i['score']}")
        if i['standard'] in FIXED_20 and i['score'] != 2.0:
            fail('R-504', f"{name}#{i['pos']} {i['standard']} → {i['score']}")
        if i['standard'] in FIXED_15 and i['score'] != 1.5:
            fail('R-504', f"{name}#{i['pos']} {i['standard']} → {i['score']}")
    # R-505
    for i in items:
        exp = EXPECTED.get(i['standard'])
        if exp and i['score'] not in exp:
            warn('R-505', f"{name}#{i['pos']} {i['standard']} {i['score']}점 (기대 {sorted(exp)})")

    # U-1 (사용자 지정 2026-09-03, HARD): 22~25번(마지막 장)은 2022 개정(2025+) 출제분만
    for i in items:
        if i['pos'] >= 22 and i['year'] < 2025:
            fail('U-1', f"{name}#{i['pos']} {kid(i)} — 마지막 장에 {i['year']}년(2015 개정) 자산")

    all_ids.extend(kid(i) for i in items)

# U-2 (사용자 지정): 2026-09 고2 20번 중화 문항이 마지막 장(22~25)에 포함되어야 함
found = [
    (name, i['pos']) for name, items in sets.items() for i in items
    if (i['year'], i['month'], i['grade'], i['orig_no']) == (2026, 9, 'H2', 20)
]
if not found:
    fail('U-2', '2026-09 고2 20번(중화 정량) 미포함')
elif not any(p >= 22 for _, p in found):
    warn('U-2', f'2026-09 고2 20번이 마지막 장 밖에 배치됨: {found}')
else:
    info('U-2', f'2026-09 고2 20번(중화 정량) 배치: {found}')

# R-301 회차 간 재사용
dup = [k for k, c in Counter(all_ids).items() if c > 1]
if dup:
    fail('R-301', f'중복: {dup}')

# R-204 3회차 분산
NEED3 = {'10통과1-01-02': 3, '10통과1-02-02': 3, '10통과1-02-04': 3, '10통과1-02-05': 3,
         '10통과1-03-03': 3, '10통과1-03-04': 3, '10통과1-03-05': 6, '10통과1-03-06': 3,
         '10통과2-01-01': 3, '10통과2-01-02': 3, '10통과2-01-03': 3, '10통과2-01-04': 6,
         '10통과2-01-05': 3, '10통과2-02-03': 3, '10통과2-02-04': 3, '10통과2-02-05': 3,
         '10통과2-02-06': 3}
for s_, c in std_3sets.items():
    base = NEED3.get(s_, 3)
    if c > base + 2:
        warn('R-204', f'{s_}: 3회차 합 {c} (기준 {base}+2)')

# R-206 로테이션
for g, used in group_used.items():
    per_std = {m: v for m, v in used.items()}
    over = [m for m, v in per_std.items() if len(v) > 2]
    if over:
        warn('R-206', f'그룹{g}: {over} 3회 사용')
    info('R-206', f'그룹{g}: ' + ', '.join(f'{m.split("-")[-2]}-{m.split("-")[-1]}×{len(v)}' for m, v in per_std.items()))

print('===== FAIL (%d) =====' % len(FAIL))
for f in FAIL: print(' ', f)
print('===== WARN (%d) =====' % len(WARN))
for w in WARN: print(' ', w)
print('===== INFO =====')
for i_ in INFO: print(' ', i_)
print()
print('결과:', 'ALL HARD PASS' if not FAIL else 'HARD FAIL 있음')
