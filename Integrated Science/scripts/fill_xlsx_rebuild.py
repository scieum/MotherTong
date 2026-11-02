# -*- coding: utf-8 -*-
"""규칙서 v1.2 재구성 결과를 워크북에 기입 (2026-09-03).
- 회차1~3: 25문항 전면 교체 (B,C,D,E,G,H,I,J,L,M,N,O,P,Q,U + A29 노트)
- 문항은행: 마스터 풀 146문항 전체 적재 (사용 회차·eligible·confidence 포함)
- 로그: output/logs/run_20260903_rebuild.jsonl
"""
import json
import datetime

import openpyxl

SRC = "통합과학_모의고사_3회차_양식.xlsx"
sets = json.load(open('scripts/sets_final.json', encoding='utf-8'))
pool = json.load(open('scripts/master_pool.json', encoding='utf-8'))

# 수동 추가 문항(2026-06 고2 9번)을 풀에도 반영
pool.append({
    'year': 2026, 'month': 6, 'grade': 'H2', 'subj_code': 'INTG', 'orig_no': 9,
    'standard': '10통과2-01-04', 'topic': '산·염기 성질 실험(페놀프탈레인 색 변화·탄산 칼슘 기체 발생)',
    'answer': 3, 'difficulty': 2, 'orig_score': '1.5점', 'material': '표',
    'calc': False, 'boki': True, 'origin': 'manual-probe',
    'subject': '통합과학2', 'domain': '변화와 다양성', 'high': False,
})

NEW_DOMAINS = {'과학의 기초', '과학과 미래 사회'}
MEDIUM_CONF = {(2026, 9, 'H2', 8), (2026, 9, 'H2', 11), (2026, 9, 'H2', 13),
               (2026, 9, 'H1', 2), (2026, 9, 'H1', 15), (2026, 9, 'H1', 17), (2026, 9, 'H1', 20),
               (2019, 11, 'H1', 5), (2019, 11, 'H1', 18),
               (2018, 11, 'H1', 1), (2018, 11, 'H1', 17),
               (2019, 9, 'H1', 6), (2019, 9, 'H1', 8)}
EXCLUDED_STD = {'10통과1-01-01', '10통과2-03-04'}

def key(i):
    return (i['year'], i['month'], i['grade'], i['subj_code'], i['orig_no'])

used_in = {}
for name, items in sets.items():
    for i in items:
        used_in[key(i)] = name

wb = openpyxl.load_workbook(SRC, data_only=False)

NOTES = {
    '회차1': ("v4 재배치(2026-09-03): 구자산 태깅 확장(2018-11·2019-09·2019-11 고1) 후 2026년 의존도 축소 — "
              "2026년 6문항(기초·미래 신설, 산염기 저배점, 마지막 장 필수분만). 배점 템플릿=2026-03 관찰 배열. "
              "U-1: 22~25번 2025+ 전용, 25번=2026-09 고2 20번 중화 정량(U-2). U-3: 출처당 ≤3. "
              "2021년 이후 비율 80%(R-305 충족). 성취기준(2015)은 GATE-2 canon 부재로 공란."),
    '회차2': ("v4 재배치(2026-09-03): 2026년 6문항. 배점 템플릿=2026-06 관찰 배열. "
              "구자산 확장분 투입: 2019-09 전기전도성 결합, 2019-11 족 주기성, 2018-11 대멸종 그래프. "
              "22번을 2025-09 자연선택 모의실험(d5)로 교체해 R-408 난이도 곡선 충족(이전 완화 해소). "
              "잔여 소프트 이탈 1건: R-103칸 시스템×2.0=2(판 경계 C를 2.0 배치, 출처 상한 때문) — 로그 기록."),
    '회차3': ("v4 재배치(2026-09-03): 2026년 7문항(빅데이터 E그룹 포함). 배점 템플릿=2026-09 관찰 배열. "
              "구자산 확장분 투입: 2019-09 핵산 단위체·인공막 삼투(2.5), 2018-11 온난화(2.5)·식물 세포, "
              "2019-11 별의 진화(2.5, 물질 2.5점 1문항 구성). 22~25번 전부 2025~26(U-1), "
              "23번 중화 이온 수 계산·25번 수평 투사 계산. scope_risk 문항 미사용."),
}

for name, items in sets.items():
    ws = wb[name]
    for i in sorted(items, key=lambda x: x['pos']):
        r = i['pos'] + 2
        ws[f"B{r}"] = i['score'] if i['score'] != int(i['score']) else int(i['score'])
        ws[f"C{r}"] = i['subject']
        ws[f"D{r}"] = i['domain']
        ws[f"E{r}"] = i['standard']
        ws[f"G{r}"] = '신설(2015 없음)' if i['domain'] in NEW_DOMAINS else '(2015 매핑 대기)'
        ws[f"H{r}"] = i['topic']
        ws[f"I{r}"] = i['answer']
        ws[f"J{r}"] = i['difficulty']
        ws[f"L{r}"] = i['year']
        ws[f"M{r}"] = i['month']
        ws[f"N{r}"] = i['grade']
        ws[f"O{r}"] = i['orig_no']
        ws[f"P{r}"] = i['orig_score']
        ws[f"Q{r}"] = i['material'] or '자료 없음'
        ws[f"U{r}"] = i['subj_code']
    ws['A29'] = NOTES[name]

# ---- 문항은행 적재 ----
bank = wb['문항은행']
pool.sort(key=key)
start = 4
# 기존 데이터/예시 행 정리 (B~Q, S, T만 지우고 A·R·U 수식은 유지)
for r in range(start, bank.max_row + 1):
    for col in 'BCDEFGHIJKLMNOPQST':
        bank[f'{col}{r}'] = None

A_FORMULA = ('=IF(OR($B{r}="",$C{r}="",$D{r}="",$T{r}="",$E{r}=""),"",'
             '$B{r}&TEXT($C{r},"00")&"_"&$D{r}&"_"&$T{r}&"_"&TEXT($E{r},"00"))')
R_FORMULA = '=IF($A{r}="","",$A{r}&".png")'
U_FORMULA = ('=IF(OR($B{r}="",$C{r}="",$D{r}="",$E{r}=""),"",'
             '$B{r}&"년 "&$C{r}&"월 "&IF($D{r}="H1","고1",IF($D{r}="H2","고2",$D{r}))&" 학평 "&$E{r}&"번")')

for n, p in enumerate(pool):
    r = start + n
    k = key(p)
    bank[f'B{r}'] = p['year']
    bank[f'C{r}'] = p['month']
    bank[f'D{r}'] = p['grade']
    bank[f'E{r}'] = p['orig_no']
    bank[f'F{r}'] = p['subject']
    bank[f'G{r}'] = p['domain']
    bank[f'H{r}'] = p['standard']
    bank[f'I{r}'] = '신설(2015 없음)' if p['domain'] in NEW_DOMAINS else '(2015 매핑 대기)'
    bank[f'J{r}'] = p['topic']
    bank[f'K{r}'] = p['orig_score']
    bank[f'L{r}'] = p['answer']
    bank[f'M{r}'] = p['difficulty']
    bank[f'N{r}'] = p['material'] or '자료 없음'
    bank[f'O{r}'] = p['standard'] not in EXCLUDED_STD and not p.get('scope_risk')
    bank[f'P{r}'] = 'medium' if (p['year'], p['month'], p['grade'], p['orig_no']) in MEDIUM_CONF else 'high'
    bank[f'Q{r}'] = used_in.get(k, '')
    if p['standard'] in EXCLUDED_STD:
        bank[f'S{r}'] = 'R-207 세트 제외 성취기준(태깅만 유지)'
    elif p.get('scope_risk'):
        bank[f'S{r}'] = 'scope_risk: 2022 개정 범위 이탈 우려 — 사람 검토 전 선정 금지'
    elif p.get('origin') == 'manual-probe':
        bank[f'S{r}'] = '2026-09-03 해설 PDF 직접 확인으로 추가'
    bank[f'T{r}'] = p['subj_code']
    # A·R·U 수식이 비어 있으면 채움
    if bank[f'A{r}'].value in (None, ''):
        bank[f'A{r}'] = A_FORMULA.format(r=r)
    if bank[f'R{r}'].value in (None, ''):
        bank[f'R{r}'] = R_FORMULA.format(r=r)
    if bank[f'U{r}'].value in (None, ''):
        bank[f'U{r}'] = U_FORMULA.format(r=r)

wb.save(SRC)
print(f'워크북 저장 완료: 회차1~3 교체, 문항은행 {len(pool)}문항 적재')

# ---- 로그 ----
ts = datetime.datetime.now().isoformat(timespec='seconds')
with open('output/logs/run_20260903_rebuild.jsonl', 'a', encoding='utf-8') as f:
    for ev in [
        {'ts': ts, 'phase': 'C1-C3', 'event': 'end',
         'detail': 'v4 문항은행 확장(2026-09-03): 2018-11·2019-09·2019-11 고1 통합과학 60문항 태깅'
                   '(서브에이전트 3개 병렬, 해설 정답표 전건 확보). 총 206문항. scope_risk 3건은 eligible=FALSE'},
        {'ts': ts, 'phase': 'D1-D3', 'event': 'end',
         'detail': 'v4 재배치: 2026년 자산 10/10/10 → 6/6/7. 구자산 3점 고난도(인공막 삼투·온난화·별 진화·'
                   '자연선택 모의실험 등) 투입으로 회차2 R-408 완화 해소. 잔여 소프트 이탈 1건: '
                   '회차2 R-103칸 시스템×2.0=2. validate_rulebook.py HARD FAIL 0'},
        {'ts': ts, 'phase': 'E1', 'event': 'end',
         'detail': 'v4 엑셀 기입 완료(회차1~3 교체, 문항은행 206문항 적재). 크롭·PDF는 사용자 확인 후 재생성'},
    ]:
        f.write(json.dumps(ev, ensure_ascii=False) + '\n')
print('로그 기록 완료')
