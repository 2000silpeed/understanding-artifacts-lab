#!/usr/bin/env python3
"""플로이드–워셜: 모든 출발점과 도착점 사이의 최단 거리.

사용법:
  python3 floyd_warshall.py graph.txt          # 표·경유지별 변경·경로를 사람이 읽는 글로 출력
  python3 floyd_warshall.py graph.txt --json   # 같은 계산을 JSON으로 출력 (영상 trace.json의 원본)

입력 형식(graph.txt): 첫 줄 "정점수 간선수", 다음 줄마다 "출발 도착 거리". '#' 뒤는 주석.
C++17 예제(floyd_warshall.cpp)는 같은 입력에 글자 하나까지 같은 글 출력을 낸다.
"""
import json
import sys

INF = None  # 무한대(아직 길을 모름). 숫자와 섞어 더하지 않도록 None으로 둔다.


def read_graph(path):
    """(정점 이름 목록, [(u, v, w)]) — 정점 이름은 처음 나온 순서대로."""
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.split('#', 1)[0].strip()
            if line:
                rows.append(line.split())
    n, m = int(rows[0][0]), int(rows[0][1])
    names, edges = [], []
    for u, v, w in rows[1:1 + m]:
        for x in (u, v):
            if x not in names:
                names.append(x)
        edges.append((names.index(u), names.index(v), int(w)))
    if len(names) != n or len(edges) != m:
        raise ValueError(f'정점 {n}개·간선 {m}개라고 했는데 정점 {len(names)}개·간선 {len(edges)}개를 읽었습니다')
    return names, edges


def initial_table(n, edges):
    """자기 자신은 0, 바로 가는 도로는 그 거리, 나머지는 무한대. nxt[i][j] = i에서 j로 갈 때의 첫걸음."""
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    nxt = [[i if i == j else None for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        if dist[u][v] is INF or w < dist[u][v]:
            dist[u][v], nxt[u][v] = w, v
    return dist, nxt


def via(dist, i, k, j):
    """i → k → j 의 거리. 둘 중 하나라도 무한대면 무한대."""
    if dist[i][k] is INF or dist[k][j] is INF:
        return INF
    return dist[i][k] + dist[k][j]


def shorter(a, b):
    """a가 b보다 짧은가 (무한대는 어떤 수보다도 길다)."""
    return a is not INF and (b is INF or a < b)


def floyd_warshall(n, edges):
    """바깥 반복문이 경유지 k. 경유지 k마다 바뀐 칸을 기록한다."""
    dist, nxt = initial_table(n, edges)
    rounds = []
    for k in range(n):                      # 경유지 k를 하나씩 허락한다
        changes = []
        for i in range(n):                  # 출발
            for j in range(n):              # 도착
                d = via(dist, i, k, j)
                if shorter(d, dist[i][j]):
                    route = path(nxt, i, k)[:-1] + path(nxt, k, j)   # 바뀌는 순간의 실제 길 i → … → k → … → j
                    changes.append({'i': i, 'j': j, 'old': dist[i][j], 'new': d, 'ik': dist[i][k], 'kj': dist[k][j], 'route': route})
                    dist[i][j] = d
                    nxt[i][j] = nxt[i][k]   # 첫걸음은 k로 가는 길의 첫걸음
        rounds.append({'k': k, 'changes': changes, 'after': [row[:] for row in dist]})
    return dist, nxt, rounds


def floyd_warshall_wrong_order(n, edges, watch=()):
    """흔한 실수: k 반복문을 맨 안쪽에 둔다. watch의 (i, j)를 계산하는 순간의 dist[i][k], dist[k][j]를 남긴다."""
    dist, _ = initial_table(n, edges)
    seen = {}
    for i in range(n):
        for j in range(n):
            if (i, j) in watch:
                seen[(i, j)] = [{'k': k, 'ik': dist[i][k], 'kj': dist[k][j]} for k in range(n)]
            for k in range(n):
                d = via(dist, i, k, j)
                if shorter(d, dist[i][j]):
                    dist[i][j] = d
    return dist, seen


def path(nxt, i, j):
    """nxt를 따라가며 i에서 j까지의 정점 목록. 길이 없으면 None."""
    if nxt[i][j] is None:
        return None
    out = [i]
    while i != j:
        i = nxt[i][j]
        out.append(i)
    return out


def negative_cycle_vertices(dist):
    """대각선(자기 자신까지의 거리)이 0보다 작은 정점들."""
    return [i for i in range(len(dist)) if dist[i][i] is not INF and dist[i][i] < 0]


def solve(path_txt):
    names, edges = read_graph(path_txt)
    n = len(names)
    init, _ = initial_table(n, edges)
    dist, nxt, rounds = floyd_warshall(n, edges)
    neg = negative_cycle_vertices(dist)
    pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
    # 실수 비교는 음수 사이클이 없을 때만 의미가 있다 (있으면 '정답' 자체가 없다)
    wrong, _ = floyd_warshall_wrong_order(n, edges)
    diff = [] if neg else [(i, j) for i, j in pairs if wrong[i][j] != dist[i][j]]
    _, seen = floyd_warshall_wrong_order(n, edges, watch=set(diff))
    paths = {} if neg else {(i, j): path(nxt, i, j) for i, j in pairs}
    return dict(names=names, edges=edges, initial=init, rounds=rounds, final=dist, next=nxt, negative=neg,
                paths=paths, wrong=wrong, diff=diff, seen=seen)


# ---------- 출력 ----------
def cell(x):
    return '∞' if x is INF else str(x)


def table_lines(names, dist):
    head = '    ' + ''.join(name.rjust(5) for name in names)
    rows = ['  ' + names[i].ljust(2) + ''.join(cell(x).rjust(5) for x in dist[i]) for i in range(len(names))]
    return [head] + rows


def text_report(r):
    N = r['names']
    out = [f"그래프: 정점 {len(N)}개, 간선 {len(r['edges'])}개", '초기 표 (행 = 출발, 열 = 도착)']
    out += table_lines(N, r['initial'])
    for rd in r['rounds']:
        k = N[rd['k']]
        out.append(f'경유지 {k}: 바뀐 칸 {len(rd["changes"])}개')
        for c in rd['changes']:
            i, j = N[c['i']], N[c['j']]
            out.append(f"  {i}→{j}: {cell(c['old'])} → {c['new']}  ({i}→{k} {c['ik']} + {k}→{j} {c['kj']})")
    out.append('최종 표')
    out += table_lines(N, r['final'])
    if r['negative']:
        out.append('음수 사이클: 있음 (대각선이 0보다 작은 정점: ' + ', '.join(f"{N[i]}={r['final'][i][i]}" for i in r['negative']) + ')')
        out.append('경로: 음수 사이클이 있어 최단 경로가 정의되지 않음')
    else:
        out.append('음수 사이클: 없음')
        out.append('모든 경로')
        for (i, j), p in r['paths'].items():
            out.append(f'  {N[i]}→{N[j]}: ' + ('길 없음' if p is None else ' → '.join(N[x] for x in p) + f" (거리 {r['final'][i][j]})"))
    if r['negative']:
        out.append('실수(k 반복문을 맨 안쪽에 둠) 비교: 음수 사이클이 있어 생략')
    elif r['diff']:
        out.append('실수(k 반복문을 맨 안쪽에 둠)와 다른 칸')
        for i, j in r['diff']:
            out.append(f"  {N[i]}→{N[j]}: 정답 {cell(r['final'][i][j])}, 실수한 결과 {cell(r['wrong'][i][j])}")
    else:
        out.append('실수(k 반복문을 맨 안쪽에 둠)와 다른 칸: 없음')
    return '\n'.join(out)


def json_report(r, source):
    N = r['names']
    return {
        'source': source,
        'names': N,
        'edges': [{'from': N[u], 'to': N[v], 'w': w} for u, v, w in r['edges']],
        'initial': r['initial'],
        'rounds': [{'k': N[rd['k']], 'changes': [{'from': N[c['i']], 'to': N[c['j']], 'old': c['old'], 'new': c['new'], 'ik': c['ik'], 'kj': c['kj'],
                                                  'route': [N[x] for x in c['route']]}
                                                 for c in rd['changes']], 'after': rd['after']} for rd in r['rounds']],
        'final': r['final'],
        'next': [[None if x is None else N[x] for x in row] for row in r['next']],
        'negativeCycle': [N[i] for i in r['negative']],
        'paths': {f'{N[i]}{N[j]}': (None if p is None else {'nodes': [N[x] for x in p], 'dist': r['final'][i][j]}) for (i, j), p in r['paths'].items()},
        'wrongOrder': {'final': r['wrong'], 'diff': [{'from': N[i], 'to': N[j], 'right': r['final'][i][j], 'wrong': r['wrong'][i][j],
                                                     'whenComputed': [{'k': N[s['k']], 'ik': s['ik'], 'kj': s['kj']} for s in r['seen'][(i, j)]]}
                                                    for i, j in r['diff']]},
        'inf': 'null = ∞',
    }


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    r = solve(argv[1])
    if '--json' in argv:
        print(json.dumps(json_report(r, argv[1].replace('\\', '/').split('/')[-1]), ensure_ascii=False, indent=1))
    else:
        print(text_report(r))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
