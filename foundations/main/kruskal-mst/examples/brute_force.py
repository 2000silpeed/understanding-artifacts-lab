"""크루스칼 결과를 독립적으로 확인하는 두 방법 (작은 그래프 전용, Python 3 표준 라이브러리만).

all_spanning_trees: 간선 n-1개 조합을 전부 만들어, 사이클 없이 모든 정점을 잇는 것만 남긴다(전수 조사).
prim: 정점 하나에서 시작해 트리 밖으로 나가는 가장 싼 간선을 붙여 가는 다른 알고리즘.

usage: python3 brute_force.py graph.txt   # 신장 트리 개수, 최소·최대 비용, 최소인 트리 개수, 프림 비용
"""
import heapq
import itertools
import sys

from kruskal import read_graph


def is_spanning_tree(names, subset):
    """간선 n-1개가 사이클 없이 모든 정점을 잇는가 (작은 union-find, 크루스칼 코드와 독립)."""
    parent = {v: v for v in names}

    def root(v):
        while parent[v] != v:
            v = parent[v]
        return v
    for u, v, _ in subset:
        a, b = root(u), root(v)
        if a == b:
            return False
        parent[a] = b
    return len({root(v) for v in names}) == 1


def all_spanning_trees(names, edges):
    """[(비용 합, 간선 튜플)] — 입력 순서 조합 순서."""
    return [(sum(e[2] for e in c), c) for c in itertools.combinations(edges, len(names) - 1) if is_spanning_tree(names, c)]


def prim(names, edges):
    """프림 알고리즘의 비용 합(연결 그래프만; 아니면 None)."""
    adj = {v: [] for v in names}
    for u, v, w in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))
    seen, total, heap = {names[0]}, 0, list(adj[names[0]])
    heapq.heapify(heap)
    while heap and len(seen) < len(names):
        w, v = heapq.heappop(heap)
        if v in seen:
            continue
        seen.add(v)
        total += w
        for x in adj[v]:
            if x[1] not in seen:
                heapq.heappush(heap, x)
    return total if len(seen) == len(names) else None


def summary(names, edges):
    trees = all_spanning_trees(names, edges)
    costs = [c for c, _ in trees]
    return {'spanningTrees': len(trees), 'minTotal': min(costs) if costs else None, 'maxTotal': max(costs) if costs else None,
            'minCount': costs.count(min(costs)) if costs else 0, 'prim': prim(names, edges)}


if __name__ == '__main__':
    n, e = read_graph(sys.argv[1])
    s = summary(n, e)
    print(' '.join(f'{k}={v}' for k, v in s.items()))
