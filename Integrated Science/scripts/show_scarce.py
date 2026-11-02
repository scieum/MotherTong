# -*- coding: utf-8 -*-
import json
pool = json.load(open('scripts/pool_existing.json', encoding='utf-8'))
for std in ['10통과1-02-04','10통과1-03-06','10통과2-02-05','10통과2-01-04',
            '10통과1-03-05','10통과1-02-02','10통과2-02-04','10통과1-01-02',
            '10통과1-01-03','10통과1-01-04','10통과2-03-01','10통과2-03-03']:
    print('===', std)
    for i in pool:
        if i['standard'] == std:
            print("  {}#{:02d} {}-{:02d} {} {} no{} orig={} assigned={} diff={} ans={} | {}".format(
                i['from_set'], i['pos'], i['year'], i['month'], i['grade'],
                i['subj_code'], i['orig_no'], i['orig_score'], i['score_assigned'],
                i['difficulty'], i['answer'], i['topic']))
