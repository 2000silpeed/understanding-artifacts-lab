"""Runs both examples for real and keeps the evidence.

  python3 films/kruskal-mst-20261024/examples/run_examples.py

1. compiles kruskal.cpp (C++17) into a temporary directory (deleted afterwards; no binary is kept in the source tree),
2. runs Python and C++ on every fixture (graph.txt, graph.txt --naive, tie.txt, disconnected.txt), keeps stdout in
   examples/results/{py,cpp}-<case>.txt and requires the two to be byte-identical,
3. checks the answers independently: brute force over every spanning tree and Prim's algorithm (brute_force.py),
4. cross-checks 300 seeded random graphs in Python (Kruskal = brute-force minimum = Prim) and 60 of them in C++,
5. checks data/trace.json is a fresh run (make_trace.py --check),
6. writes data/runs.json (the stdout the film's terminal shows) and examples/results/run-receipt.json.
Exit 0 only if every command exits 0 and every comparison holds. Needs python3 and a C++17 compiler ($CXX or c++).
"""
import json
import os
import platform
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILM = HERE.parent
sys.path.insert(0, str(HERE))
from brute_force import all_spanning_trees, prim, summary  # noqa: E402
from kruskal import components, kruskal, read_graph  # noqa: E402

CASES = [('graph', ['graph.txt']), ('graph-naive', ['graph.txt', '--naive']), ('tie', ['tie.txt']), ('disconnected', ['disconnected.txt'])]
SEED, RANDOM_N, RANDOM_CPP = 20261024, 300, 60


def run(cmd, cwd=HERE):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def random_graph(rng, k):
    """Connected-or-not small graph: n 2..7 vertices, distinct or tied costs 1..9."""
    n = rng.randint(2, 7)
    names = [f'V{i}' for i in range(n)]
    pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]
    rng.shuffle(pairs)
    m = rng.randint(n - 1, min(len(pairs), 10))
    return names, [(a, b, rng.randint(1, 9)) for a, b in pairs[:m]]


def write_graph(path, names, edges):
    path.write_text(' '.join(names) + '\n' + ''.join(f'{u} {v} {w}\n' for u, v, w in edges), encoding='utf-8')


def main():
    receipt = {'host': {'system': platform.system(), 'machine': platform.machine(), 'python': platform.python_version()},
               'commands': [], 'checks': {}}
    ok = True

    def check(name, cond):
        nonlocal ok
        receipt['checks'][name] = bool(cond)
        ok = ok and bool(cond)

    cxx = os.environ.get('CXX') or shutil.which('c++') or shutil.which('g++') or shutil.which('clang++')
    receipt['cxx'] = {'path': cxx, 'version': run([cxx, '--version'])[1].splitlines()[0] if cxx else None}
    results = HERE / 'results'
    results.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='kruskal-mst-'))
    try:
        exe = tmp / 'kruskal'
        cc = [cxx, '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror', '-o', str(exe), 'kruskal.cpp']
        code, out, err = run(cc)
        receipt['commands'].append({'cmd': ' '.join(['c++'] + cc[1:-3] + ['-o', '<tmp>/kruskal', 'kruskal.cpp']), 'exit': code, 'stderr': err.strip()})
        check('c++17 compiles with -Wall -Wextra -Werror', code == 0)
        if code:
            raise SystemExit(json.dumps(receipt, ensure_ascii=False, indent=1))

        outputs = {}
        for case, args in CASES:
            pc, po, pe = run([sys.executable, 'kruskal.py', *args])
            cc_, co, ce = run([str(exe), *args])
            (results / f'py-{case}.txt').write_text(po, encoding='utf-8')
            (results / f'cpp-{case}.txt').write_text(co, encoding='utf-8')
            receipt['commands'].append({'cmd': 'python3 kruskal.py ' + ' '.join(args), 'exit': pc, 'stdout': f'results/py-{case}.txt', 'stderr': pe.strip()})
            receipt['commands'].append({'cmd': './kruskal ' + ' '.join(args), 'exit': cc_, 'stdout': f'results/cpp-{case}.txt', 'stderr': ce.strip()})
            check(f'{case}: python exit 0', pc == 0)
            check(f'{case}: c++ exit 0', cc_ == 0)
            check(f'{case}: python stdout == c++ stdout', po == co and po != '')
            outputs[case] = po.splitlines()

        # independent answers
        for case, f in (('graph', 'graph.txt'), ('tie', 'tie.txt'), ('disconnected', 'disconnected.txt')):
            names, edges = read_graph(HERE / f)
            s = summary(names, edges)
            tree, total, _ = kruskal(names, edges)
            receipt[f'brute-{case}'] = s
            if s['spanningTrees']:
                check(f'{case}: kruskal total == brute-force minimum == prim', total == s['minTotal'] == s['prim'])
                check(f'{case}: printed total line', f'total: {total}' in outputs[case])
            else:
                check(f'{case}: no spanning tree, kruskal reports a forest', len(components(names, tree)) > 1 and 'connected: no (components 2)' in outputs[case])
        names, edges = read_graph(HERE / 'tie.txt')
        tree, total, _ = kruskal(names, edges)
        mins = [set(c) for cost, c in all_spanning_trees(names, edges) if cost == total]
        check('tie: kruskal tree is one of the minimum trees', set(tree) in mins)

        # seeded random cross-check
        rng = random.Random(SEED)
        bad, cpp_bad, spanning = [], [], 0
        for k in range(RANDOM_N):
            names, edges = random_graph(rng, k)
            tree, total, _ = kruskal(names, edges)
            trees = all_spanning_trees(names, edges)
            if trees:
                spanning += 1
                if not (total == min(c for c, _ in trees) == prim(names, edges) and len(tree) == len(names) - 1):
                    bad.append(k)
            elif len(components(names, tree)) == 1:
                bad.append(k)
            if k < RANDOM_CPP:
                g = tmp / f'r{k}.txt'
                write_graph(g, names, edges)
                pc, po, _ = run([sys.executable, str(HERE / 'kruskal.py'), str(g)])
                cc_, co, _ = run([str(exe), str(g)])
                if pc or cc_ or po != co:
                    cpp_bad.append(k)
        receipt['random'] = {'seed': SEED, 'graphs': RANDOM_N, 'connected': spanning, 'mismatches': bad,
                             'cppGraphs': RANDOM_CPP, 'cppMismatches': cpp_bad}
        check(f'random: {RANDOM_N} graphs, kruskal == brute force == prim', not bad)
        check(f'random: first {RANDOM_CPP} graphs, python stdout == c++ stdout', not cpp_bad)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    receipt['binaryKept'] = False

    code, out, _ = run([sys.executable, 'make_trace.py', '--check'])
    receipt['commands'].append({'cmd': 'python3 make_trace.py --check', 'exit': code, 'stdout': out.strip()})
    check('data/trace.json == fresh run', code == 0)

    runs = {'source': 'examples/run_examples.py (real stdout, Python 3 and C++17)', 'input': (HERE / 'graph.txt').read_text(encoding='utf-8').splitlines(),
            'python': {'cmd': 'python3 kruskal.py graph.txt', 'stdout': outputs['graph']},
            'cpp': {'cmd': './kruskal graph.txt', 'stdout': (results / 'cpp-graph.txt').read_text(encoding='utf-8').splitlines()},
            'naive': {'cmd': 'python3 kruskal.py graph.txt --naive', 'stdout': outputs['graph-naive']}}
    (FILM / 'data' / 'runs.json').write_text(json.dumps(runs, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    receipt['ok'] = ok
    (results / 'run-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({'ok': ok, 'failed': [k for k, v in receipt['checks'].items() if not v], 'checks': len(receipt['checks']),
                      'random': receipt['random']}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
