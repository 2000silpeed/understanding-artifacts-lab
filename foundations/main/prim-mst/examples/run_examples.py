"""Run the Prim examples for real and check them.

1. Compile prim.cpp (C++17) into a temporary folder (deleted afterwards).
2. Run Python and C++ on every fixture and flag; save each stdout to results/<case>.txt (one file: both
   languages must print the same bytes, otherwise the case fails and both outputs are saved).
3. Check against independent.py: Prim total = brute-force minimum, on every start vertex of garden.txt;
   the naive rule is worse on garden.txt; dense = lazy.
4. 300 seeded random graphs (ties and islands allowed): Python Prim = brute-force minimum of the start's
   component; 60 of them also through the C++ binary, all three modes byte for byte.
5. Write results/run-receipt.json. Exit 0 only if every check passed.

  python3 films/prim-mst-20261103/examples/run_examples.py
"""
import json
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent  # noqa: E402
import prim  # noqa: E402

FIXTURES = ['garden', 'tie', 'disconnected']
MODES = {'lazy': [], 'naive': ['--naive'], 'dense': ['--dense']}
SEED, GRAPHS, CPP_GRAPHS = 20261103, 300, 60
CXX = ['c++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic', '-Werror']


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return p.returncode, p.stdout, p.stderr


def random_graph(rnd, k):
    n = rnd.randint(2, 7)
    names = [f'V{i}' for i in range(n)]
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
    rnd.shuffle(pairs)
    m = rnd.randint(0 if k % 10 == 0 else n - 1, min(len(pairs), 11))
    edges = [(a, b, rnd.randint(1, 9)) for a, b in pairs[:m]]
    text = ' '.join(names) + '\n' + ''.join(f'{names[a]} {names[b]} {w}\n' for a, b, w in edges)
    return names, edges, text


def main():
    results = HERE / 'results'
    results.mkdir(exist_ok=True)
    failed, checks = [], 0
    build = Path(tempfile.mkdtemp(prefix='prim-build-'))
    try:
        exe = build / 'prim'
        code, _, err = run(CXX + ['-o', str(exe), str(HERE / 'prim.cpp')])
        compiler = run(['c++', '--version'])[1].splitlines()[0]
        if code != 0:
            print(err, file=sys.stderr)
            raise SystemExit('C++ build failed')

        cases = [(f, mode, MODES[mode]) for f in FIXTURES for mode in MODES]
        names, _ = prim.read_graph(HERE / 'garden.txt')
        cases += [('garden', f'start-{s}', ['--start', s]) for s in names[1:]]
        runs = {}
        for f, label, flags in cases:
            g = str(HERE / f'{f}.txt')
            py = run([sys.executable, '-B', str(HERE / 'prim.py'), g] + flags)
            cc = run([str(exe), g] + flags)
            case = f'{f}-{label}'
            checks += 1
            ok = py[0] == 0 and cc[0] == 0 and py[1] == cc[1]
            (results / f'{case}.txt').write_text(py[1], encoding='utf-8')
            if not ok:
                failed.append(case)
                (results / f'{case}.cpp-DIFF.txt').write_text(cc[1] + cc[2], encoding='utf-8')
            runs[case] = {'cmd': ' '.join(['prim.py|prim', f'{f}.txt'] + flags), 'exitPy': py[0], 'exitCpp': cc[0],
                          'sameBytes': py[1] == cc[1], 'lastLine': py[1].strip().splitlines()[-1]}

        # independent answers on the fixtures
        indep = {f: independent.summary(str(HERE / f'{f}.txt')) | {'graph': f'examples/{f}.txt'} for f in FIXTURES}
        for f in FIXTURES:
            nm, ed = prim.read_graph(HERE / f'{f}.txt')
            for mode, fn in (('lazy', prim.prim), ('dense', prim.prim_dense)):
                checks += 1
                if fn(nm, ed, 0)['total'] != indep[f]['minTotal']:
                    failed.append(f'{f}-{mode}-vs-bruteforce')
        nm, ed = prim.read_graph(HERE / 'garden.txt')
        trees = independent.spanning_trees(len(nm), ed)
        best = min(t for t, _ in trees)
        want = {frozenset(frozenset(ed[i][:2]) for i in combo) for t, combo in trees if t == best}
        for s in range(len(nm)):
            checks += 1
            got = frozenset(frozenset((x, y)) for x, y, _ in prim.prim(nm, ed, s)['taken'])
            if got not in want:
                failed.append(f'garden-start-{nm[s]}-tree')
        checks += 1
        if not prim.prim_naive(nm, ed, 0)['total'] > best:
            failed.append('garden-naive-not-worse')

        # random cross-check
        rnd = random.Random(SEED)
        mism, cpp_mism, connected, cpp_graphs = [], [], 0, 0
        for k in range(GRAPHS):
            gnames, gedges, text = random_graph(rnd, k)
            n = len(gnames)
            start = rnd.randrange(n)
            comp = independent.component(n, gedges, start)
            rmin = min(t for t, _ in independent.spanning_trees(n, gedges, comp))
            lazy, dense, naive = (prim.prim(gnames, gedges, start), prim.prim_dense(gnames, gedges, start),
                                  prim.prim_naive(gnames, gedges, start))
            connected += len(comp) == n
            if not (lazy['total'] == dense['total'] == rmin and lazy['reached'] == dense['reached'] == len(comp)
                    and naive['reached'] <= len(comp) and (naive['reached'] < len(comp) or naive['total'] >= rmin)):
                mism.append(k)
            if k < CPP_GRAPHS:
                cpp_graphs += 1
                gp = build / f'r{k}.txt'
                gp.write_text(text, encoding='utf-8')
                for flags in MODES.values():
                    args = [str(gp), '--start', gnames[start]] + flags
                    a = run([sys.executable, '-B', str(HERE / 'prim.py')] + args)
                    b = run([str(exe)] + args)
                    if a != b:
                        cpp_mism.append([k, flags])
        checks += 1
        if mism or cpp_mism:
            failed.append('random')
    finally:
        shutil.rmtree(build, ignore_errors=True)

    receipt = {
        'ok': not failed, 'failed': failed, 'checks': checks,
        'compiler': compiler, 'cxxFlags': CXX[1:], 'python': sys.version.split()[0],
        'runs': runs, 'independent': indep,
        'garden': {'spanningTrees': len(trees), 'min': best, 'minTrees': len(want)},
        'random': {'seed': SEED, 'graphs': GRAPHS, 'connected': connected, 'mismatches': mism,
                   'cppGraphs': cpp_graphs, 'cppMismatches': cpp_mism},
        'note': 'Temporary C++ build and random-graph files lived in a system temp folder and were deleted.',
    }
    (results / 'run-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({'ok': receipt['ok'], 'failed': failed, 'checks': checks, 'random': receipt['random']},
                     ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
