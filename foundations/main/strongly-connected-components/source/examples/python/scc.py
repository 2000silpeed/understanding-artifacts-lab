"""강한 연결 요소(SCC): Kosaraju(DFS 두 번)와 Tarjan(DFS 한 번).

수업 예제. DFS는 모두 반복문(명시적 스택)으로 짜서 정점이 수십만 개여도
재귀 한도에 걸리지 않는다. 방문 순서는 재귀 DFS와 똑같다
(정점 번호 순으로 시작, 간선은 입력 순서대로).

usage:
  python3 scc.py <graph file>          수업 화면에 쓰는 실행 기록(텍스트)
  python3 scc.py <graph file> --json   같은 내용을 JSON으로
"""
import json
import sys


def read_graph(path):
    """'nodes a b c' 한 줄 + 'a -> b' 간선 줄. '#'으로 시작하는 줄은 주석."""
    names, edges = None, []
    with open(path, encoding='utf-8') as f:
        for no, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if parts[0] == 'nodes':
                names = parts[1:]
                continue
            if names is None or len(parts) != 3 or parts[1] != '->':
                raise ValueError(f'{path}:{no}: "{line}"')
            idx = {n: i for i, n in enumerate(names)}
            if parts[0] not in idx or parts[2] not in idx:
                raise ValueError(f'{path}:{no}: 모르는 정점 "{line}"')
            edges.append((idx[parts[0]], idx[parts[2]]))
    if names is None:
        raise ValueError(f'{path}: nodes 줄이 없다')
    return names, edges


def adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    return adj


def reverse(n, edges):
    """간선 방향을 모두 뒤집은 인접 리스트."""
    return adjacency(n, [(v, u) for u, v in edges])


def finish_order(n, adj):
    """1단계: DFS가 정점을 '끝낸'(더 갈 곳이 없어 되돌아간) 순서."""
    seen, order = [False] * n, []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [(s, 0)]
        while stack:
            v, i = stack[-1]
            if i < len(adj[v]):
                stack[-1] = (v, i + 1)
                w = adj[v][i]
                if not seen[w]:
                    seen[w] = True
                    stack.append((w, 0))
            else:
                stack.pop()
                order.append(v)
    return order


def kosaraju(n, edges):
    """2단계: 끝난 순서의 역순으로, 뒤집은 그래프에서 DFS. 한 번의 DFS가 닿는 곳이 한 묶음.
    묶음은 '응축 그래프의 위상 순서'로 나온다(들어오는 쪽 묶음이 먼저)."""
    adj = adjacency(n, edges)
    order = finish_order(n, adj)
    radj = reverse(n, edges)
    seen, comps = [False] * n, []
    for s in reversed(order):
        if seen[s]:
            continue
        seen[s] = True
        comp, stack = [s], [(s, 0)]
        while stack:
            v, i = stack[-1]
            if i < len(radj[v]):
                stack[-1] = (v, i + 1)
                w = radj[v][i]
                if not seen[w]:
                    seen[w] = True
                    comp.append(w)
                    stack.append((w, 0))
            else:
                stack.pop()
        comps.append(comp)
    return order, comps


def tarjan(n, edges):
    """DFS 한 번. low[v] = v의 DFS 서브트리에서 스택에 남은 정점으로 닿는 가장 작은 방문 번호.
    low[v] == index[v]이면 v가 묶음의 뿌리: 스택에서 v까지 꺼낸 것이 한 묶음.
    묶음은 '역위상 순서'로 나온다(나가는 쪽 묶음이 먼저)."""
    adj = adjacency(n, edges)
    index, low, on = [-1] * n, [0] * n, [False] * n
    st, comps, t = [], [], 0
    for s in range(n):
        if index[s] != -1:
            continue
        index[s] = low[s] = t
        t += 1
        st.append(s)
        on[s] = True
        call = [(s, 0)]
        while call:
            v, i = call[-1]
            if i < len(adj[v]):
                call[-1] = (v, i + 1)
                w = adj[v][i]
                if index[w] == -1:
                    index[w] = low[w] = t
                    t += 1
                    st.append(w)
                    on[w] = True
                    call.append((w, 0))
                elif on[w]:
                    low[v] = min(low[v], index[w])
            else:
                call.pop()
                if call:
                    u = call[-1][0]
                    low[u] = min(low[u], low[v])
                if low[v] == index[v]:
                    comp = []
                    while True:
                        w = st.pop()
                        on[w] = False
                        comp.append(w)
                        if w == v:
                            break
                    comps.append(comp)
    return comps


def condense(n, edges, comps):
    """묶음 하나를 점 하나로 줄인 그래프(응축 그래프)의 간선. 중복·자기 간선은 뺀다."""
    cid = [0] * n
    for k, comp in enumerate(comps):
        for v in comp:
            cid[v] = k
    out, seen = [], set()
    for u, v in edges:
        e = (cid[u], cid[v])
        if e[0] != e[1] and e not in seen:
            seen.add(e)
            out.append(e)
    return cid, out


def analyse(names, edges):
    n = len(names)
    order, comps = kosaraju(n, edges)
    _, cedges = condense(n, edges, comps)
    tj = tarjan(n, edges)
    same = sorted(sorted(c) for c in comps) == sorted(sorted(c) for c in tj)
    return {
        'nodes': n,
        'edges': len(edges),
        'finishOrder': [names[v] for v in order],
        'pass2Order': [names[v] for v in reversed(order)],
        'pass2Starts': [names[c[0]] for c in comps],
        'components': [[names[v] for v in c] for c in comps],
        'condensationEdges': [[a + 1, b + 1] for a, b in cedges],
        'topoOrder': [k + 1 for k in range(len(comps))],
        'deployOrder': [k + 1 for k in reversed(range(len(comps)))],
        'tarjanComponents': [[names[v] for v in c] for c in tj],
        'tarjanSamePartition': same,
    }


def report(r):
    """수업 화면과 같은 줄을 찍는다. C++ 예제(main.cpp)와 글자 하나까지 같아야 한다."""
    comp = lambda k: '{' + ' '.join(r['components'][k - 1]) + '}'
    L = [f"그래프: 정점 {r['nodes']}개, 간선 {r['edges']}개",
         '1단계 끝난 순서: ' + ' '.join(r['finishOrder']),
         '2단계 살펴볼 순서(끝난 순서의 역순): ' + ' '.join(r['pass2Order']),
         '2단계 실제 출발점: ' + ' '.join(r['pass2Starts'])]
    L += [f'묶음 {k}: {comp(k)}' for k in range(1, len(r['components']) + 1)]
    L.append('응축 간선: ' + ', '.join(f'{a}->{b}' for a, b in r['condensationEdges']))
    L.append('위상 순서(호출하는 쪽 먼저):' + ''.join(f' {k}' for k in r['topoOrder']))
    L.append('배포 순서(호출받는 쪽 먼저):' + ''.join(f' {k}' for k in r['deployOrder']))
    L.append('Tarjan 묶음 순서:' + ''.join(' {' + ' '.join(c) + '}' for c in r['tarjanComponents']))
    L.append('Tarjan과 같은 분할: ' + ('예' if r['tarjanSamePartition'] else '아니오'))
    return '\n'.join(L) + '\n'


def main(argv):
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    names, edges = read_graph(argv[1])
    r = analyse(names, edges)
    if '--json' in argv[2:]:
        sys.stdout.write(json.dumps(r, ensure_ascii=False, indent=1) + '\n')
    else:
        sys.stdout.write(report(r))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
