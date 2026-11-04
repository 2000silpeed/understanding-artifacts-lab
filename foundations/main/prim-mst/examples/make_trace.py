"""Write data/trace.json — the only source of numbers for the script, figures and the film.

Everything comes from calling the real functions in prim.py / independent.py on garden.txt, plus the real
stdout files that run_examples.py saved (results/*.txt). Run run_examples.py first.

  python3 films/prim-mst-20261103/examples/make_trace.py          # write
  python3 films/prim-mst-20261103/examples/make_trace.py --check  # exit 1 if data/trace.json is stale
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILM = HERE.parent
sys.path.insert(0, str(HERE))
import independent  # noqa: E402
import prim  # noqa: E402

OUT = FILM / 'data' / 'trace.json'


def code_excerpt():
    """prim() from prim.py with its real line numbers (what the code scene shows)."""
    lines = (HERE / 'prim.py').read_text(encoding='utf-8').splitlines()
    a = next(i for i, l in enumerate(lines) if l.startswith('def prim('))
    b = next(i for i in range(a, len(lines)) if lines[i].strip().startswith("return {'start'"))
    return [{'line': i + 1, 'text': lines[i]} for i in range(a, b + 1)]


def build():
    names, edges = prim.read_graph(HERE / 'garden.txt')
    n = len(names)
    E = lambda x, y, w: {'a': names[x], 'b': names[y], 'w': w}  # noqa: E731
    cand = lambda c, tree: {'w': c[0], 'seq': c[1], 'a': names[c[2]], 'b': names[c[3]],  # noqa: E731
                            'stale': names[c[3]] in tree}

    res = prim.prim(names, edges, 0)
    tree = [names[0]]
    steps = []
    for e in res['events'][1:]:
        x, y, w = e['edge']
        inside = set(tree)
        cut = sorted((ww, names[u], names[v]) for u, v, ww in edges if (names[u] in inside) != (names[v] in inside))
        step = {'kind': e['kind'], 'edge': E(x, y, w), 'candidatesBefore': [cand(c, inside) for c in e['heapBefore']],
                'treeBefore': list(tree)}
        if e['kind'] == 'take':
            assert cut[0][0] == w, 'cut property: chosen edge must be the cheapest crossing edge'
            step['cut'] = [{'w': ww, 'a': a if a in inside else b, 'b': b if a in inside else a} for ww, a, b in cut]
            tree.append(names[y])
            step['pushed'] = [E(c[2], c[3], c[0]) for c in e['pushed']]
            step['treeAfter'] = list(tree)
            step['bedsWatered'] = len(tree) - 1
            step['fromLastAdded'] = names[x] == step['treeBefore'][-1]
        else:
            step['reason'] = 'both ends already in tree'
        steps.append(step)
    takes = [s for s in steps if s['kind'] == 'take']
    skips = [s for s in steps if s['kind'] == 'skip']

    naive = prim.prim_naive(names, edges, 0)
    diverge = next(k for k, (a, b) in enumerate(zip(naive['taken'], res['taken'])) if a != b)
    last = names[naive['taken'][diverge][0]]
    nv_options = sorted((w, names[x if names[y] == last else y]) for x, y, w in edges
                        if last in (names[x], names[y]) and names[x if names[y] == last else y] not in takes[diverge]['treeBefore'])

    kr = independent.kruskal(n, edges)
    dsu = independent.DSU(n)
    klog = []
    for entry in kr['log']:
        u, v, w = edges[entry['edge']]
        if entry['take']:
            dsu.union(u, v)
        tank_beds = sum(1 for z in range(1, n) if dsu.find(z) == dsu.find(0))
        klog.append({**E(u, v, w), 'take': entry['take'], 'tankBedsAfter': tank_beds,
                     'pieces': len({dsu.find(z) for z in range(n)})})

    trees = independent.spanning_trees(n, edges)
    best = min(t for t, _ in trees)
    starts = {}
    for s in range(n):
        r = prim.prim(names, edges, s)
        starts[names[s]] = {'order': [names[s]] + [names[y] for _, y, _ in r['taken']], 'total': r['total'],
                            'edges': sorted(sorted([names[x], names[y]]) + [w] for x, y, w in r['taken']),
                            'skips': sum(1 for e in r['events'] if e['kind'] == 'skip')}
    dense = prim.prim_dense(names, edges, 0)

    runs = {}
    for case in ['garden-lazy', 'garden-naive', 'garden-dense', 'garden-start-동백', 'tie-lazy', 'disconnected-lazy']:
        out = (HERE / 'results' / f'{case}.txt').read_text(encoding='utf-8').splitlines()
        runs[case] = out
    assert runs['garden-lazy'] == prim.format_run(names, res, 'lazy'), 'results/ is stale: run run_examples.py'

    return {
        'source': 'examples/make_trace.py: prim.py + independent.py on examples/garden.txt, stdout from examples/results/',
        'graph': {'file': 'examples/garden.txt', 'names': names, 'start': names[0], 'beds': n - 1,
                  'edges': [{'id': i, **E(u, v, w)} for i, (u, v, w) in enumerate(edges)],
                  'distinctCosts': len({w for *_, w in edges}) == len(edges)},
        'prim': {'steps': steps, 'takeOrder': [s['edge'] for s in takes], 'skipCount': len(skips),
                 'skipped': [s['edge'] for s in skips], 'total': res['total'], 'treeEdges': len(res['taken']),
                 'connected': res['connected'], 'heapLeftAtStop': [cand(c, set(tree)) for c in res['heapLeft']],
                 'maxCandidates': max(len(s['candidatesBefore']) for s in steps),
                 'notFromLastAdded': [k + 1 for k, s in enumerate(takes) if not s['fromLastAdded']]},
        'naive': {'taken': [E(*t) for t in naive['taken']], 'total': naive['total'], 'connected': naive['connected'],
                  'divergeStep': diverge + 1, 'lastAdded': last,
                  'lastAddedOptions': [{'w': w, 'to': b} for w, b in nv_options],
                  'missed': takes[diverge]['edge'], 'extra': naive['total'] - res['total']},
        'kruskal': {'log': klog, 'total': kr['total'],
                    'sameTree': sorted(kr['taken']) == sorted(next(i for i, (u, v, w) in enumerate(edges)
                                                                   if {u, v} == {x, y} and w == ww)
                                                              for x, y, ww in res['taken'])},
        'brute': {'spanningTrees': len(trees), 'min': best, 'minTrees': sum(1 for t, _ in trees if t == best),
                  'max': max(t for t, _ in trees)},
        'starts': starts,
        'dense': {'total': dense['total'], 'sameOrder': [t[:2] for t in dense['taken']] == [t[:2] for t in res['taken']]},
        'fixtures': {f: independent.summary(str(HERE / f'{f}.txt')) | {'file': f'examples/{f}.txt'}
                     for f in ['tie', 'disconnected']},
        'runs': runs,
        'code': code_excerpt(),
    }


def main():
    data = build()
    for f in data['fixtures'].values():
        f['graph'] = f.pop('file')
    text = json.dumps(data, ensure_ascii=False, indent=1) + '\n'
    if '--check' in sys.argv:
        ok = OUT.exists() and OUT.read_text(encoding='utf-8') == text
        print(json.dumps({'trace': 'data/trace.json', 'upToDate': ok}))
        return 0 if ok else 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text, encoding='utf-8')
    print(json.dumps({'trace': 'data/trace.json', 'written': True}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
