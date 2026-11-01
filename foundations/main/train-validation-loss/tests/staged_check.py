#!/usr/bin/env python3
"""Fail-closed staged companion checker; values must match the authored result JSON."""
from __future__ import annotations
import hashlib, json, re, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CANON=ROOT/'canonical'
fail=[]
def check(ok,msg):
    if not ok: fail.append(msg)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

# authored source snapshot is complete and the public copy is byte-identical
expected=['practice/index.html','practice/browser_check.cjs','practice/build_practice.py','lesson.md','film-data.json','script/narration.json']
for rel in expected:
    check((CANON/rel).is_file(),f'missing canonical/{rel}')
    if (CANON/rel).is_file() and rel=='lesson.md': check((ROOT/rel).read_bytes()==(CANON/rel).read_bytes(),'lesson.md parity')
# embedded app data must be the exact canonical DATA object, whose values come from result files
html=(CANON/'practice/index.html').read_text()
m=re.search(r'const DATA = (\{.*?\});\nconst \$',html,re.S)
check(bool(m),'canonical DATA object missing')
if m:
    canonical_data=json.loads(m.group(1)); appjs=(ROOT/'app-data.js').read_text(); am=re.search(r'window\.TRAIN_VALIDATION_DATA=(\{.*\});\n$',appjs,re.S); check(bool(am),'app data export missing')
    if am: check(json.loads(am.group(1))==canonical_data,'app data differs from canonical practice')
    for key,filename in [('small','run-small.json'),('large','run-large.json')]:
        result=json.loads((CANON/'results'/filename).read_text())
        check(canonical_data['runs'][key]['log']==result['log'],f'{key} loss log changed')
        check(canonical_data['runs'][key]['best']==result['best'],f'{key} best changed')
        check(canonical_data['runs'][key]['final']==result['final'],f'{key} final changed')
# offline/document and public UX invariants
for rel in ['index.html','app.js','styles.css','app-data.js']:
    text=(ROOT/rel).read_text()
    check(not re.search(r'(?:src|href)=["\']https?://',text),f'external dependency in {rel}')
check('PretendardVariable.woff2' in (ROOT/'styles.css').read_text(),'local Pretendard missing')
check('이 걸음에서 멈춰 보기' in (ROOT/'index.html').read_text(),'first interaction missing')
check('실험 초기화' in (ROOT/'index.html').read_text() and '직전 위치로 되돌리기' in (ROOT/'index.html').read_text(),'reset/undo missing')
# source ZIP inspection
z=ROOT/'source.zip'; check(z.is_file(),'source.zip missing')
if z.is_file():
    with zipfile.ZipFile(z) as archive:
        names=archive.namelist(); check(names==sorted(names),'ZIP order is not sorted'); check(all(not n.startswith('/') and '..' not in Path(n).parts for n in names),'unsafe ZIP path'); check(not any('__pycache__' in n or n.endswith(('.pyc','.mp4','.wav')) for n in names),'forbidden ZIP member'); check('canonical/lesson.md' in names,'canonical lesson missing')
        for n in names:
            check(hashlib.sha256(archive.read(n)).hexdigest()==sha(ROOT/n) if n.startswith('canonical/') and (ROOT/n).is_file() else True,f'ZIP member mismatch {n}')
print(json.dumps({'status':'PASS' if not fail else 'FAIL','failures':fail,'canonical_files':sum(p.is_file() for p in CANON.rglob('*'))},ensure_ascii=False))
raise SystemExit(1 if fail else 0)
