# -*- coding: utf-8 -*-
import json
from collections import defaultdict

pool = json.load(open('scripts/master_pool.json', encoding='utf-8'))
by_std = defaultdict(list)
for p in pool:
    by_std[p['standard']].append(p)

for std in sorted(by_std):
    print('===', std)
    for p in sorted(by_std[std], key=lambda x: (-x['year'], -x['month'])):
        hl = 'H' if p['high'] else 'L'
        print("  [{}] {}-{:02d} {} {} no{:<2} {:4s} d{} ans={} {} | {}".format(
            hl, p['year'], p['month'], p['grade'], p['subj_code'], p['orig_no'],
            str(p['orig_score']), p['difficulty'], p['answer'],
            (p['material'] or '?'), p['topic']))
