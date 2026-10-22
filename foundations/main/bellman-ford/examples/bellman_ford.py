"""Bellman-Ford on a small graph file, with a round-by-round trace — the example of films/bellman-ford-20261022.

usage:
  python3 bellman_ford.py graph.txt                    # prints the Dijkstra comparison and every Bellman-Ford check
  python3 bellman_ford.py graph.txt --trace out.json   # also writes the trace the film draws from
Graph file: 'V <names…>' (the first is the source) and one 'E <from> <to> <weight>' per edge, in scan order.
The lines between 'film:begin' and 'film:end' are shown on screen in the film, unchanged.
"""
import heapq
import json
import sys

INF = float('inf')


# film:begin
def bellman_ford(n, edges, src):
    dist = [INF] * n
    dist[src] = 0
    for _ in range(n - 1):              # V - 1 rounds
        for u, v, w in edges:           # relax every edge
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    for u, v, w in edges:               # one more pass
        if dist[u] + w < dist[v]:
            return None                 # negative cycle
    return dist
# film:end


def read_graph(path):
    names, edges = [], []
    for line in open(path, encoding='utf-8'):
        p = line.split()
        if not p or p[0].startswith('#'):
            continue
        if p[0] == 'V':
            names = p[1:]
        elif p[0] == 'E':
            edges.append((names.index(p[1]), names.index(p[2]), int(p[3])))
    return names, edges


def fmt(x):
    return 'INF' if x == INF else str(x)


def dijkstra_finalize_once(n, edges, src):
    """Textbook Dijkstra: a popped vertex is final and is never updated again. Returns (finalize order, dist)."""
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    dist, done, order, heap = [INF] * n, [False] * n, [], [(0, src)]
    dist[src] = 0
    while heap:
        d, u = heapq.heappop(heap)
        if done[u]:
            continue
        done[u] = True
        order.append((u, d))
        for v, w in adj[u]:
            if not done[v] and d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
    return order, dist


def bellman_ford_trace(n, edges, src):
    """Same algorithm as bellman_ford(), recording every check of every round and the check pass."""
    dist, pred = [INF] * n, [None] * n
    dist[src] = 0
    rounds = []

    def scan():
        checks = []
        for k, (u, v, w) in enumerate(edges):
            du, before = dist[u], dist[v]
            cand = du + w
            updated = cand < before
            if updated:
                dist[v], pred[v] = cand, u
            checks.append({'edge': k, 'u': u, 'v': v, 'w': w, 'du': du, 'before': before, 'cand': cand, 'updated': updated})
        return checks

    for r in range(1, n):
        rounds.append({'round': r, 'checks': scan(), 'dist': dist[:]})
    before_check = dist[:]
    # the check pass only looks; it must not change the answer it reports on
    check = []
    for k, (u, v, w) in enumerate(edges):
        cand = dist[u] + w
        check.append({'edge': k, 'u': u, 'v': v, 'w': w, 'du': dist[u], 'before': dist[v], 'cand': cand, 'updated': cand < dist[v]})
    negative = any(c['updated'] for c in check)
    return {'rounds': rounds, 'check': check, 'negativeCycle': negative, 'dist': before_check, 'pred': pred}


def path_to(pred, src, v):
    out = [v]
    while out[-1] != src and pred[out[-1]] is not None and len(out) <= len(pred):
        out.append(pred[out[-1]])
    return out[::-1] if out[-1] == src else None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    names, edges = read_graph(path)
    n, src = len(names), 0
    E = lambda u, v: f'{names[u]}->{names[v]}'
    row = lambda d: ' '.join(f'{names[i]}={fmt(x)}' for i, x in enumerate(d))
    print('graph:', path.replace('\\', '/').split('/')[-1])
    print('vertices:', ' '.join(names), f'(source {names[src]})')
    print('edges (scan order):', ', '.join(f'{E(u, v)} {w}' for u, v, w in edges))
    print()
    order, ddist = dijkstra_finalize_once(n, edges, src)
    print('[dijkstra, finalize once]')
    for u, d in order:
        print(f'finalize {names[u]} {fmt(d)}')
    print('result:', row(ddist))
    print()
    tr = bellman_ford_trace(n, edges, src)
    print('[bellman-ford]')
    print('start:', row([0 if i == src else INF for i in range(n)]))
    for rd in tr['rounds']:
        print(f"round {rd['round']}")
        for c in rd['checks']:
            if c['du'] == INF and not c['updated']:
                print(f"  {E(c['u'], c['v'])} skip ({names[c['u']]}=INF)")
            elif c['updated']:
                print(f"  {E(c['u'], c['v'])} {names[c['v']]}: {fmt(c['before'])} -> {fmt(c['cand'])}")
            else:
                print(f"  {E(c['u'], c['v'])} keep ({fmt(c['du'])}{c['w']:+d}={fmt(c['cand'])} >= {fmt(c['before'])})")
        print('  dist:', row(rd['dist']))
    upd = [c for c in tr['check'] if c['updated']]
    if upd:
        print('check: ' + ', '.join(f"{E(c['u'], c['v'])} {fmt(c['before'])} -> {fmt(c['cand'])}" for c in upd) + ' -> negative cycle')
    else:
        print('check: no update -> no negative cycle')
    plain = bellman_ford(n, edges, src)
    if tr['negativeCycle']:
        assert plain is None
        print('result: negative cycle (no shortest paths)')
    else:
        assert plain == tr['dist']
        print('result:', row(plain))
        for v in range(n):
            if v != src and plain[v] != INF:
                print(f'path {names[v]}:', ' -> '.join(names[x] for x in path_to(tr['pred'], src, v)))
    if '--trace' in sys.argv:
        out = sys.argv[sys.argv.index('--trace') + 1]
        clean = lambda x: None if x == INF else x
        data = {
            'graph': path.replace('\\', '/').split('/')[-1], 'vertices': names, 'source': src,
            'edges': [{'u': u, 'v': v, 'w': w} for u, v, w in edges],
            'dijkstra': {'order': [[u, clean(d)] for u, d in order], 'dist': [clean(x) for x in ddist]},
            'rounds': [{'round': rd['round'], 'dist': [clean(x) for x in rd['dist']],
                        'checks': [{k: clean(x) if k in ('du', 'before', 'cand') else x for k, x in c.items()} for c in rd['checks']]} for rd in tr['rounds']],
            'check': [{k: clean(x) if k in ('du', 'before', 'cand') else x for k, x in c.items()} for c in tr['check']],
            'negativeCycle': tr['negativeCycle'], 'dist': None if tr['negativeCycle'] else [clean(x) for x in plain],
            'paths': None if tr['negativeCycle'] else {names[v]: [names[x] for x in path_to(tr['pred'], src, v)] for v in range(n) if plain[v] != INF},
        }
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
            f.write('\n')


if __name__ == '__main__':
    main()
