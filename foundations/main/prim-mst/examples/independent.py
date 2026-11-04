"""Independent answers for the Prim examples: every spanning tree (brute force) and Kruskal.

Shares no code with prim.py (own parser, own union-find), so a bug in prim.py cannot hide here.

  python3 independent.py garden.txt
"""
import itertools
import json
import sys


def read_graph(path):
    with open(path, encoding='utf-8') as f:
        rows = [ln.split('#', 1)[0].split() for ln in f]
    rows = [r for r in rows if r]
    names = rows[0]
    pos = {nm: i for i, nm in enumerate(names)}
    return names, [(pos[a], pos[b], int(w)) for a, b, w in rows[1:]]


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        self.p[b] = a
        return True


def spanning_trees(n, edges, vertices=None):
    """All spanning trees of the sub-graph on `vertices` (default: all): list of (total, edge-index tuple)."""
    vs = set(range(n)) if vertices is None else set(vertices)
    idx = [i for i, (u, v, _) in enumerate(edges) if u in vs and v in vs]
    out = []
    for combo in itertools.combinations(idx, len(vs) - 1):
        d = DSU(n)
        if all(d.union(edges[i][0], edges[i][1]) for i in combo):
            out.append((sum(edges[i][2] for i in combo), combo))
    if len(vs) == 1:
        out = [(0, ())]
    return out


def component(n, edges, start):
    d = DSU(n)
    for u, v, _ in edges:
        d.union(u, v)
    return [v for v in range(n) if d.find(v) == d.find(start)]


def kruskal(n, edges):
    """Stable sort by cost; returns accepted/rejected log and the forest total."""
    d = DSU(n)
    log = []
    for i in sorted(range(len(edges)), key=lambda i: edges[i][2]):
        u, v, w = edges[i]
        log.append({'edge': i, 'cost': w, 'take': d.union(u, v)})
    return {'log': log, 'total': sum(e['cost'] for e in log if e['take']),
            'taken': [e['edge'] for e in log if e['take']]}


def summary(path):
    names, edges = read_graph(path)
    n = len(names)
    comp = component(n, edges, 0)
    trees = spanning_trees(n, edges, comp)
    best = min(t for t, _ in trees)
    return {'graph': path, 'vertices': n, 'edges': len(edges), 'componentOfFirst': len(comp),
            'spanningTrees': len(trees), 'minTotal': best, 'minTrees': sum(1 for t, _ in trees if t == best),
            'maxTotal': max(t for t, _ in trees), 'kruskalTotal': kruskal(n, edges)['total']}


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(json.dumps(summary(p), ensure_ascii=False))
