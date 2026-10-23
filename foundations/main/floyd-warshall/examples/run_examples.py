#!/usr/bin/env python3
"""예제 실행 영수증: Python·C++17·실습 JS(fw.js)를 같은 입력으로 실제 실행하고 결과를 보존한다.

  python3 films/floyd-warshall-20261023/examples/run_examples.py

- C++는 $CXX(없으면 c++)로 -std=c++17 컴파일, 실행 파일은 scratch/floyd-warshall-20261023/build/ (임시).
- 결과: examples/results/{py,cpp}-<입력>.txt, py-graph.json, js-graph.json, run-receipt.json
- 영상 데이터: trace.json = py-graph.json, trace-negative.json = py-negative_cycle.json (영상의 표·숫자는 이 둘만 읽는다)
- Python 글 출력과 C++ 글 출력이 글자 하나까지 같고, fw.js 보고서가 Python JSON과 같아야 exit 0.
"""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILM = HERE.parent
ROOT = FILM.parent.parent
RES = HERE / 'results'
BUILD = ROOT / 'scratch' / FILM.name / 'build'
INPUTS = ['graph.txt', 'negative_cycle.txt']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    return str(Path(p).resolve().relative_to(ROOT))


def run(cmd, out=None):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if out is not None:
        Path(out).write_text(r.stdout, encoding='utf-8')
    return {'cmd': ' '.join(str(c) for c in cmd), 'exit': r.returncode, 'stderr': r.stderr.strip()[-2000:],
            **({'stdout': rel(out), 'stdoutSha256': sha(out)} if out is not None else {})}


def screen_excerpt(out, neg):
    """Lines of the real program output that the film shows verbatim (same in Python and C++ when the receipt is ok)."""
    L, N = out.splitlines(), neg.splitlines()
    i = L.index('최종 표')
    return {
        'command': 'python3 floyd_warshall.py graph.txt',
        'final': L[i:i + 6],
        'pathBA': next(x.strip() for x in L if x.strip().startswith('B→A: B →')),
        'wrongHead': next(x for x in L if x.startswith('실수(')),
        'wrongBA': next(x.strip() for x in L if x.strip().startswith('B→A: 정답')),
        'negativeCommand': 'python3 floyd_warshall.py negative_cycle.txt',
        'negative': next(x for x in N if x.startswith('음수 사이클:')),
        'source': 'examples/results/py-graph.txt, examples/results/py-negative_cycle.txt (= cpp-*.txt)',
    }


def main():
    RES.mkdir(exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    cxx = os.environ.get('CXX') or shutil.which('c++') or shutil.which('g++') or shutil.which('clang++')
    exe = BUILD / 'floyd_warshall'
    steps = [run([cxx, '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic', rel(HERE / 'floyd_warshall.cpp'), '-o', rel(exe)])]
    steps[-1]['what'] = 'compile C++17'
    cxx_version = subprocess.run([cxx, '--version'], capture_output=True, text=True).stdout.splitlines()[:1]
    same = {}
    for name in INPUTS:
        stem = name.rsplit('.', 1)[0]
        py, cpp = RES / f'py-{stem}.txt', RES / f'cpp-{stem}.txt'
        steps.append({'what': f'Python text {name}', **run([sys.executable, rel(HERE / 'floyd_warshall.py'), rel(HERE / name)], py)})
        steps.append({'what': f'C++ text {name}', **run([rel(exe), rel(HERE / name)], cpp)})
        same[name] = py.read_text(encoding='utf-8') == cpp.read_text(encoding='utf-8') and py.stat().st_size > 0
    pj, jj = RES / 'py-graph.json', RES / 'js-graph.json'
    steps.append({'what': 'Python JSON graph.txt', **run([sys.executable, rel(HERE / 'floyd_warshall.py'), rel(HERE / 'graph.txt'), '--json'], pj)})
    pn = RES / 'py-negative_cycle.json'
    steps.append({'what': 'Python JSON negative_cycle.txt', **run([sys.executable, rel(HERE / 'floyd_warshall.py'), rel(HERE / 'negative_cycle.txt'), '--json'], pn)})
    steps.append({'what': 'practice fw.js report graph.txt', **run(['node', rel(FILM / 'practice' / 'check.cjs'), 'report', rel(HERE / 'graph.txt')], jj)})
    steps.append({'what': 'practice exercises answers', **run(['node', rel(FILM / 'practice' / 'check.cjs'), 'exercises'], RES / 'js-exercises.json')})
    py_json, js_json = json.loads(pj.read_text()), json.loads(jj.read_text())
    # fw.js 보고서에는 wrongOrder.diff[].whenComputed가 없다 (Python만 기록) — 그 키만 빼고 비교
    py_cmp = json.loads(json.dumps(py_json))
    for d in py_cmp['wrongOrder']['diff']:
        d.pop('whenComputed', None)
    py_cmp.pop('inf', None)
    js_same = py_cmp == js_json
    shutil.copyfile(pj, FILM / 'trace.json')
    shutil.copyfile(pn, FILM / 'trace-negative.json')
    excerpt = screen_excerpt((RES / 'py-graph.txt').read_text(encoding='utf-8'), (RES / 'py-negative_cycle.txt').read_text(encoding='utf-8'))
    (FILM / 'screen-excerpt.json').write_text(json.dumps(excerpt, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    ok = all(s['exit'] == 0 for s in steps) and all(same.values()) and js_same
    receipt = {
        'what': 'Floyd–Warshall example execution receipt (real runs, this host)',
        'host': {'system': platform.system(), 'machine': platform.machine(), 'python': platform.python_version(), 'cxx': cxx, 'cxxVersion': cxx_version,
                 'node': subprocess.run(['node', '--version'], capture_output=True, text=True).stdout.strip()},
        'inputs': {rel(HERE / n): sha(HERE / n) for n in INPUTS},
        'sources': {rel(p): sha(p) for p in [HERE / 'floyd_warshall.py', HERE / 'floyd_warshall.cpp', FILM / 'practice' / 'fw.js', FILM / 'practice' / 'exercises.js', FILM / 'practice' / 'check.cjs']},
        'steps': steps,
        'pythonEqualsCpp': same,
        'fwJsEqualsPythonJson': js_same,
        'trace': {'path': rel(FILM / 'trace.json'), 'sha256': sha(FILM / 'trace.json'), 'copiedFrom': rel(pj)},
        'screenExcerpt': {'path': rel(FILM / 'screen-excerpt.json'), 'sha256': sha(FILM / 'screen-excerpt.json')},
        'traceNegative': {'path': rel(FILM / 'trace-negative.json'), 'sha256': sha(FILM / 'trace-negative.json'), 'copiedFrom': rel(pn)},
        'ok': ok,
    }
    (RES / 'run-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({'ok': ok, 'pythonEqualsCpp': same, 'fwJsEqualsPythonJson': js_same, 'exits': [s['exit'] for s in steps]}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
