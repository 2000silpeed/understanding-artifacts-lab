#!/usr/bin/env python3
"""Independent numeric oracle for the shipped loss values and quiz semantics."""
import json, math, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
canonical=json.loads((ROOT/'canonical/practice/index.html').read_text().split('const DATA = ',1)[1].split(';\nconst $',1)[0])
small=canonical['runs']['small']; large=canonical['runs']['large']; failures=[]
def check(ok,msg):
    if not ok: failures.append(msg)
def close(a,b): return abs(a-b)<1e-9
check(round(-math.log(.5),2)==.69,'loss(.5) display oracle')
check(round(-math.log(.25),2)==1.39,'loss(.25) display oracle')
check(small['best']['step']==550 and close(small['best']['val'],.5045),'small best oracle')
check(small['final']['train']==.2028 and small['final']['val']==.7469,'small final oracle')
check(large['final']['train']==.3056 and large['final']['val']==.3235,'large final oracle')
check(small['probe']['train_counts']=={'아침에':3,'점심에':4,'저녁에':0,'밤에':1},'probe counts oracle')
for name,a,b,truth in [('learn',100,500,'배우는 중'),('overfit',600,3000,'외우는 중'),('large',600,3000,'배우는 중')]:
    r=small if name!='large' else large; start=next(x for x in r['log'] if x['step']==a); end=next(x for x in r['log'] if x['step']==b)
    actual='외우는 중' if end['train']<start['train'] and end['val']>start['val'] else '배우는 중' if end['train']<start['train'] and end['val']<=start['val'] else '기타'
    check(actual==truth,f'quiz oracle {name}')
print(json.dumps({'status':'PASS' if not failures else 'FAIL','failures':failures,'computed_loss_half':round(-math.log(.5),2),'computed_loss_quarter':round(-math.log(.25),2),'quiz_truth':['배우는 중','외우는 중','배우는 중']},ensure_ascii=False))
raise SystemExit(1 if failures else 0)
