"""Prim's minimum spanning tree — the example the film runs (Python 3, standard library only).

The tree starts from one vertex and grows one vertex at a time: every edge that leaves the tree waits in a
candidate heap (cost, push order); the cheapest one is popped, and if its far end is already in the tree it is
dropped ("lazy" Prim), otherwise that end joins the tree and its own edges join the heap.

  python3 prim.py garden.txt                 # Prim from the first vertex (탱크)
  python3 prim.py garden.txt --start 동백     # another start: same tree when all costs differ
  python3 prim.py garden.txt --naive         # common mistake: look only at the vertex added last
  python3 prim.py garden.txt --dense         # array version, O(n^2), no heap and nothing to drop

prim.cpp (C++17) prints the same text, byte for byte, for every input and flag (run_examples.py checks it).
"""
import argparse
import heapq
import sys


def read_graph(path):
    """Return (names, edges). First non-comment line = vertex names; then 'u v cost' per line, in input order."""
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.split('#', 1)[0].strip()
            if line:
                rows.append(line.split())
    names = rows[0]
    index = {name: i for i, name in enumerate(names)}
    if len(index) != len(names):
        raise ValueError('duplicate vertex name')
    edges = []
    for row in rows[1:]:
        if len(row) != 3:
            raise ValueError(f'bad edge line: {row}')
        u, v, w = index[row[0]], index[row[1]], int(row[2])
        if u == v:
            raise ValueError('self loop')
        edges.append((u, v, w))
    return names, edges


def adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:            # neighbours keep input order (both languages)
        adj[u].append((v, w))
        adj[v].append((u, w))
    return adj


def prim(names, edges, start=0):
    """Lazy Prim with a binary heap. Returns the full event log the film draws from."""
    n = len(names)
    adj = adjacency(n, edges)
    in_tree = [False] * n
    heap, seq = [], 0
    events, taken = [], []

    def add(x):
        nonlocal seq
        in_tree[x] = True
        pushed = []
        for y, w in adj[x]:
            if not in_tree[y]:           # an edge back into the tree is never a candidate
                heapq.heappush(heap, (w, seq, x, y))
                pushed.append((w, seq, x, y))
                seq += 1
        return pushed

    pushed = add(start)
    events.append({'kind': 'start', 'v': start, 'pushed': pushed, 'heapAfter': sorted(heap)})
    while heap and len(taken) < n - 1:
        before = sorted(heap)
        w, s, x, y = heapq.heappop(heap)
        if in_tree[y]:                   # both ends already in the tree: would close a cycle
            events.append({'kind': 'skip', 'edge': (x, y, w), 'seq': s, 'heapBefore': before, 'heapAfter': sorted(heap)})
            continue
        taken.append((x, y, w))
        pushed = add(y)
        events.append({'kind': 'take', 'edge': (x, y, w), 'seq': s, 'heapBefore': before,
                       'pushed': pushed, 'heapAfter': sorted(heap), 'tree': sum(in_tree)})
    return {'start': start, 'events': events, 'taken': taken, 'total': sum(w for _, _, w in taken),
            'reached': sum(in_tree), 'n': n, 'connected': sum(in_tree) == n, 'heapLeft': sorted(heap)}


def prim_naive(names, edges, start=0):
    """Common mistake: choose only among edges of the vertex added last (a walk, not a growing tree)."""
    n = len(names)
    adj = adjacency(n, edges)
    in_tree = [False] * n
    in_tree[start] = True
    last, taken, stuck = start, [], None
    while len(taken) < n - 1:
        options = [(w, i, y) for i, (y, w) in enumerate(adj[last]) if not in_tree[y]]
        if not options:
            stuck = last
            break
        w, _, y = min(options)
        taken.append((last, y, w))
        in_tree[y] = True
        last = y
    return {'start': start, 'taken': taken, 'total': sum(w for _, _, w in taken), 'reached': sum(in_tree),
            'n': n, 'connected': sum(in_tree) == n, 'stuck': stuck}


def prim_dense(names, edges, start=0):
    """Array version for dense graphs: best[v] = cheapest known edge from the tree to v. O(n^2), no heap."""
    n = len(names)
    INF = float('inf')
    cost = [[INF] * n for _ in range(n)]
    for u, v, w in edges:
        if w < cost[u][v]:
            cost[u][v] = cost[v][u] = w
    in_tree = [False] * n
    best = [INF] * n
    via = [-1] * n
    best[start] = 0
    taken = []
    for _ in range(n):
        x = -1
        for v in range(n):               # the smallest best[] outside the tree; ties -> smaller index
            if not in_tree[v] and best[v] < INF and (x < 0 or best[v] < best[x]):
                x = v
        if x < 0:
            break
        in_tree[x] = True
        if via[x] >= 0:
            taken.append((via[x], x, best[x]))
        for v in range(n):
            if not in_tree[v] and cost[x][v] < best[v]:
                best[v], via[v] = cost[x][v], x
    return {'start': start, 'taken': taken, 'total': sum(w for _, _, w in taken), 'reached': sum(in_tree),
            'n': n, 'connected': sum(in_tree) == n}


def summary_line(res):
    return f"합계 {res['total']} | 간선 {len(res['taken'])}개 | " + (
        '연결됨' if res['connected'] else f"연결 안 됨 (트리 {res['reached']}/{res['n']})")


def format_run(names, res, mode='lazy'):
    """The exact text both languages print."""
    head = {'lazy': '', 'naive': ' (실수: 방금 붙인 정점만 봄)', 'dense': ' (배열 버전)'}[mode]
    out = [f"시작 {names[res['start']]}{head}"]
    if mode == 'lazy':
        for e in res['events'][1:]:
            x, y, w = e['edge']
            if e['kind'] == 'take':
                out.append(f"고름 {names[x]}-{names[y]} {w} | 트리 {e['tree']}/{res['n']}")
            else:
                out.append(f"버림 {names[x]}-{names[y]} {w} | 두 끝이 이미 트리 안")
    else:
        for k, (x, y, w) in enumerate(res['taken']):
            out.append(f"고름 {names[x]}-{names[y]} {w} | 트리 {k + 2}/{res['n']}")
        if mode == 'naive' and res['stuck'] is not None:
            out.append(f"막힘 {names[res['stuck']]} | 이 정점에서 트리 밖으로 나가는 간선 없음")
    out.append(summary_line(res))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('graph')
    ap.add_argument('--start', help='start vertex name (default: first vertex)')
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--naive', action='store_true')
    mode.add_argument('--dense', action='store_true')
    a = ap.parse_args(argv)
    names, edges = read_graph(a.graph)
    start = names.index(a.start) if a.start else 0
    if a.naive:
        lines = format_run(names, prim_naive(names, edges, start), 'naive')
    elif a.dense:
        lines = format_run(names, prim_dense(names, edges, start), 'dense')
    else:
        lines = format_run(names, prim(names, edges, start), 'lazy')
    sys.stdout.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
