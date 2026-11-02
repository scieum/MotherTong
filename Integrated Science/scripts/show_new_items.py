# -*- coding: utf-8 -*-
import json

pool = json.load(open('scripts/master_pool.json', encoding='utf-8'))
new = [p for p in pool if (p['year'], p['month']) in [(2019, 11), (2018, 11), (2019, 9)]]
new.sort(key=lambda p: (p['standard'], -p['year']))
for p in new:
    hl = 'H' if p['high'] else 'L'
    risk = ' [scope_risk]' if p.get('scope_risk') else ''
    print("{} [{}] {}-{:02d} no{:<2} {:3s} d{} ans={} calc={} {} | {}{}".format(
        p['standard'], hl, p['year'], p['month'], p['orig_no'], str(p['orig_score']),
        p['difficulty'], p['answer'], p.get('calc'), (p['material'] or '?'), p['topic'], risk))
