"""크루스칼 알고리즘: 사이클을 피하며 최소 신장 트리 만들기 (Python 3, 표준 라이브러리만).

usage:
  python3 kruskal.py graph.txt            # 비용 순서대로 간선을 보며 고르기/버리기, 최소 신장 트리와 비용 합
  python3 kruskal.py graph.txt --naive    # 흔한 실수: "두 끝을 이미 방문했으면 버린다" 규칙

입력: 첫 줄 정점 이름, 그다음 줄마다 `u v 비용`. `#` 뒤는 주석.
출력은 kruskal.cpp(C++17)와 글자 하나까지 같다(run_examples.py가 확인).
"""
import sys


def read_graph(path):
    """(정점 이름 목록, [(u, v, w), ...]) — 간선은 입력 순서 그대로."""
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.split('#')[0].split()
            if line:
                rows.append(line)
    names = rows[0]
    edges = [(u, v, int(w)) for u, v, w in rows[1:]]
    for u, v, _ in edges:
        if u not in names or v not in names:
            raise ValueError(f'unknown vertex in edge {u}-{v}')
    return names, edges


class UnionFind:
    def __init__(self, names):
        self.parent = {v: v for v in names}   # 처음엔 모두 자기 자신이 대표
        self.size = {v: 1 for v in names}

    def find(self, v):
        root = v
        while self.parent[root] != root:      # 대표까지 따라 올라간다
            root = self.parent[root]
        while v != root:                      # 지나온 정점은 대표를 바로 가리키게(경로 압축)
            nxt = self.parent[v]
            self.parent[v] = root
            v = nxt
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                      # 같은 덩어리: 이으면 사이클
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra                  # 작은 덩어리를 큰 덩어리 아래에
        self.size[ra] += self.size[rb]
        return True


def kruskal(names, edges, log=None):
    """최소 신장 트리(연결이 아니면 신장 숲). 반환: (고른 간선, 비용 합, 살펴본 간선 수)."""
    uf = UnionFind(names)
    tree, total, checked = [], 0, 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):   # 비용 순서(같으면 입력 순서)
        if len(tree) == len(names) - 1:
            break                                       # 간선 n-1개면 끝
        checked += 1
        ru, rv = uf.find(u), uf.find(v)                 # 두 끝의 대표
        take = uf.union(u, v)                           # 대표가 다르면 잇는다
        if take:
            tree.append((u, v, w))
            total += w
        if log is not None:
            log.append(dict(u=u, v=v, w=w, findU=ru, findV=rv, take=take, total=total,
                            parent=dict(uf.parent)))
    return tree, total, checked


def naive_visited(names, edges):
    """흔한 실수: 두 끝이 모두 이미 방문한 정점이면 버린다. 다른 덩어리끼리 잇는 간선까지 버린다."""
    seen, tree, steps = set(), [], []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        take = not (u in seen and v in seen)
        if take:
            tree.append((u, v, w))
            seen.update((u, v))
        steps.append(dict(u=u, v=v, w=w, take=take))
    return tree, steps


def components(names, tree):
    """고른 간선으로 이어진 덩어리들(각 덩어리는 이름 순서, 덩어리는 첫 정점 순서)."""
    uf = UnionFind(names)
    for u, v, _ in tree:
        uf.union(u, v)
    groups = {}
    for v in names:
        groups.setdefault(uf.find(v), []).append(v)
    return list(groups.values())


def edge_name(e):
    return f'{e[0]}-{e[1]}'


def report(names, edges):
    log = []
    tree, total, checked = kruskal(names, edges, log)
    out = ['sorted: ' + ' '.join(f'{edge_name(e)}:{e[2]}' for e in sorted(edges, key=lambda e: e[2]))]
    for k, s in enumerate(log, 1):
        head = f"step {k}: {s['u']}-{s['v']} w={s['w']} find({s['u']})={s['findU']} find({s['v']})={s['findV']}"
        out.append(head + (f" take total={s['total']}" if s['take'] else ' skip cycle'))
    out.append('mst: ' + ' '.join(edge_name(e) for e in tree))
    out.append(f'total: {total}')
    out.append(f'edges: {len(tree)}/{len(names) - 1} checked: {checked}/{len(edges)}')
    groups = components(names, tree)
    out.append('connected: yes' if len(groups) == 1 else f'connected: no (components {len(groups)})')
    return out


def report_naive(names, edges):
    tree, steps = naive_visited(names, edges)
    out = ['naive rule: skip an edge when both ends are already visited']
    for k, s in enumerate(steps, 1):
        out.append(f"step {k}: {s['u']}-{s['v']} w={s['w']} " + ('take' if s['take'] else 'skip both-visited'))
    groups = components(names, tree)
    out.append(f'edges: {len(tree)}/{len(names) - 1} total: {sum(e[2] for e in tree)} components: {len(groups)}')
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    names, edges = read_graph(argv[1])
    lines = report_naive(names, edges) if '--naive' in argv[2:] else report(names, edges)
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
