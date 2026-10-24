"""data/trace.json — the only source of numbers the film draws, written by running examples/kruskal.py on examples/graph.txt.

usage:
  python3 make_trace.py           # (re)write ../data/trace.json
  python3 make_trace.py --check   # exit 1 if the file on disk differs from a fresh run (writes nothing)
"""
import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from brute_force import all_spanning_trees, prim  # noqa: E402
from kruskal import UnionFind, components, kruskal, naive_visited, read_graph  # noqa: E402

OUT = HERE.parent / 'data' / 'trace.json'
EXCERPTS = [('find', 'UnionFind.find'), ('union', 'UnionFind.union'), ('kruskal', 'kruskal')]


def ed(e, names_order=None):
    return {'u': e[0], 'v': e[1], 'w': e[2], 'id': f'{e[0]}-{e[1]}'}


def code_excerpts(path):
    """Line spans and exact source lines of the functions the film shows (1-based, inclusive)."""
    src = path.read_text(encoding='utf-8')
    lines = src.split('\n')
    tree = ast.parse(src)
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for f in node.body:
                if isinstance(f, ast.FunctionDef):
                    found[f'{node.name}.{f.name}'] = f
        elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
            found[node.name] = node
    out = {}
    for key, name in EXCERPTS:
        f = found[name]
        a, b = f.lineno, f.end_lineno
        # the screen leaves out a docstring and the trace-only `if log is not None:` block; rows keep their real line numbers
        skip = set()
        if f.body and isinstance(f.body[0], ast.Expr) and isinstance(getattr(f.body[0], 'value', None), ast.Constant):
            skip.update(range(f.body[0].lineno, f.body[0].end_lineno + 1))
        for node in ast.walk(f):
            if isinstance(node, ast.If) and ast.unparse(node.test) == 'log is not None':
                skip.update(range(node.lineno, node.end_lineno + 1))
        body = [(i, lines[i - 1]) for i in range(a, b + 1) if i not in skip]
        indent = min(len(x) - len(x.lstrip()) for _, x in body if x.strip())
        out[key] = {'file': 'examples/kruskal.py', 'name': name, 'span': [a, b], 'omitted': sorted(skip),
                    'rows': [[i, x[indent:]] for i, x in body]}
    return out


def build():
    names, edges = read_graph(HERE / 'graph.txt')
    order = sorted(edges, key=lambda e: e[2])
    log = []
    tree, total, checked = kruskal(names, edges, log)
    steps, chosen = [], []
    for k, s in enumerate(log, 1):
        e = (s['u'], s['v'], s['w'])
        before = components(names, chosen)
        comp_u = next(g for g in before if s['u'] in g)
        crossing = sorted((x for x in edges if (x[0] in comp_u) != (x[1] in comp_u)), key=lambda x: x[2])
        if s['take']:
            chosen.append(e)
        steps.append({'k': k, **ed(e), 'findU': s['findU'], 'findV': s['findV'], 'take': s['take'], 'total': s['total'],
                      'treeEdges': len(chosen), 'groupsBefore': before, 'groupsAfter': components(names, chosen),
                      'parentAfter': s['parent'],
                      'cut': {'side': comp_u, 'crossing': [ed(x) for x in crossing]} if s['take'] else None})
    ntree, nsteps = naive_visited(names, edges)
    ngroups = components(names, ntree)
    trees = all_spanning_trees(names, edges)
    costs = [c for c, _ in trees]
    first = trees[0]
    worst = max(trees, key=lambda t: t[0])
    hist = {c: costs.count(c) for c in range(min(costs), max(costs) + 1)}
    # path compression shown in the code scene: call find() on the deepest vertex of the final union-find state
    final = dict(log[-1]['parent'])
    depth = lambda v: 0 if final[v] == v else 1 + depth(final[v])
    deep = max(names, key=depth)
    path = [deep]
    while final[path[-1]] != path[-1]:
        path.append(final[path[-1]])
    uf = UnionFind(names)
    uf.parent = dict(final)
    root = uf.find(deep)
    return {
     'source': 'examples/make_trace.py ← examples/kruskal.py on examples/graph.txt',
     'graph': {'file': 'examples/graph.txt', 'vertices': names, 'edges': [ed(e) for e in edges]},
     'n': len(names), 'm': len(edges), 'allEdgesTotal': sum(e[2] for e in edges),
     'sorted': [ed(e) for e in order],
     'steps': steps,
     'result': {'mst': [ed(e) for e in tree], 'total': total, 'checked': checked, 'edges': len(tree),
                'unchecked': [ed(e) for e in order[checked:]], 'components': len(components(names, tree))},
     'naive': {'rule': 'skip an edge when both ends are already visited',
               'steps': [{'k': k, **ed((s['u'], s['v'], s['w'])), 'take': s['take']} for k, s in enumerate(nsteps, 1)],
               'tree': [ed(e) for e in ntree], 'total': sum(e[2] for e in ntree), 'edges': len(ntree), 'groups': ngroups,
               'firstWrongSkip': next(ed((s['u'], s['v'], s['w'])) for s, lg in zip(nsteps, log) if s['take'] != lg['take'])},
     'brute': {'spanningTrees': len(trees), 'minTotal': min(costs), 'minCount': costs.count(min(costs)), 'maxTotal': max(costs),
               'prim': prim(names, edges),
               'exampleTree': {'edges': [ed(e) for e in first[1]], 'total': first[0], 'note': 'first spanning tree in input-order enumeration'},
               'worstTree': {'edges': [ed(e) for e in worst[1]], 'total': worst[0]},
               'histogram': [{'total': c, 'trees': n} for c, n in hist.items()]},
     'compress': {'v': deep, 'path': path, 'root': root, 'before': final, 'after': uf.parent,
                  'note': 'find() on the deepest vertex of the final union-find state (examples/kruskal.py UnionFind.find)'},
     'code': code_excerpts(HERE / 'kruskal.py'),
    }


def dump(d):
    return json.dumps(d, ensure_ascii=False, indent=1) + '\n'


if __name__ == '__main__':
    text = dump(build())
    if '--check' in sys.argv:
        ok = OUT.exists() and OUT.read_text(encoding='utf-8') == text
        print(json.dumps({'trace': str(OUT.relative_to(HERE.parent)), 'upToDate': ok}))
        sys.exit(0 if ok else 1)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text, encoding='utf-8')
    print('wrote', OUT.relative_to(HERE.parent))
