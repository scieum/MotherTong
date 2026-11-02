# -*- coding: utf-8 -*-
"""GATE-1·GATE-6 승인 처리(2026-09-03 사용자 '좋아' 응답):
- output/qc/.approved_assets 플래그 생성
- 시험지 PDF 3매를 staging → final로 이동
- 로그 기록
"""
import datetime
import json
import os
import shutil

os.makedirs('output/final', exist_ok=True)

with open('output/qc/.approved_assets', 'w', encoding='utf-8') as f:
    f.write('GATE-1 승인 2026-09-03 (규칙서 v1.2 재구성 세트 컨택트시트 검토)\n')

moved = []
for name in ('set1_1회차_시험지.pdf', 'set2_2회차_시험지.pdf', 'set3_3회차_시험지.pdf'):
    src = os.path.join('output/staging', name)
    dst = os.path.join('output/final', name)
    if os.path.exists(src):
        shutil.move(src, dst)
        moved.append((name, os.path.getsize(dst)))

ts = datetime.datetime.now().isoformat(timespec='seconds')
with open('output/logs/run_20260903_rebuild.jsonl', 'a', encoding='utf-8') as f:
    f.write(json.dumps({'ts': ts, 'phase': 'GATE-1', 'event': 'end',
                        'detail': '사람 승인 — .approved_assets 생성'}, ensure_ascii=False) + '\n')
    f.write(json.dumps({'ts': ts, 'phase': 'GATE-6', 'event': 'end',
                        'detail': '사람 승인 — 시험지 PDF 3매 output/final 이동: ' + ', '.join(n for n, _ in moved)},
                       ensure_ascii=False) + '\n')

for n, s in moved:
    print(f'{n}  {s:,} bytes -> output/final/')
print('GATE-1/GATE-6 처리 완료')
