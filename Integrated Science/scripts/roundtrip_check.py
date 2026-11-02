# -*- coding: utf-8 -*-
"""워크북에 기입된 내용이 sets_final.json과 일치하는지 검증."""
import json
import openpyxl

sets = json.load(open('scripts/sets_final.json', encoding='utf-8'))
wb = openpyxl.load_workbook("통합과학_모의고사_3회차_양식.xlsx", data_only=False)

errs = 0
for name, items in sets.items():
    ws = wb[name]
    for i in items:
        r = i['pos'] + 2
        checks = [
            ('B', float(i['score']), float(ws[f'B{r}'].value)),
            ('D', i['domain'], ws[f'D{r}'].value),
            ('E', i['standard'], ws[f'E{r}'].value),
            ('I', i['answer'], ws[f'I{r}'].value),
            ('L', i['year'], ws[f'L{r}'].value),
            ('M', i['month'], ws[f'M{r}'].value),
            ('N', i['grade'], ws[f'N{r}'].value),
            ('O', i['orig_no'], ws[f'O{r}'].value),
            ('P', i['orig_score'], ws[f'P{r}'].value),
            ('U', i['subj_code'], ws[f'U{r}'].value),
        ]
        for col, exp, got in checks:
            if exp != got:
                print(f'{name}#{i["pos"]} {col}: 기대 {exp!r} 실제 {got!r}')
                errs += 1

bank = wb['문항은행']
cnt = sum(1 for r in range(4, bank.max_row + 1) if bank[f'B{r}'].value is not None)
used = sum(1 for r in range(4, bank.max_row + 1) if bank[f'Q{r}'].value)
print(f'회차 시트 불일치: {errs}건 / 문항은행 데이터 행: {cnt} / 사용 표기: {used}')
print('ROUNDTRIP OK' if errs == 0 and cnt == 206 and used == 75 else 'ROUNDTRIP 문제 있음')
