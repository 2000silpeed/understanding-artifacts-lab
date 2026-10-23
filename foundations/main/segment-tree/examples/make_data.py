"""Writes the data every other part of the film reads, from the real example program (segment_tree.py).

  data/trace.json            the tree, every visited node of each query (call order, kind, return value), the update
                             path (bottom-up, before/after) and the derived numbers the narration and picture use.
                             film.js draws only these values; plan.py and test_source.py check script/subtitles against them.
  examples/random-input.txt  a larger seeded input (cross-check of Python, C++ and the practice page)
  examples/random-expected.txt  its answers from a brute-force scan (independent of the tree code)

usage: python3 films/segment-tree-20261023/examples/make_data.py [--check]
  --check: regenerate in memory and exit 1 if any written file differs (nothing written).
"""
import hashlib
import json
import random
import sys
from pathlib import Path

EX = Path(__file__).resolve().parent
FILM = EX.parent
sys.path.insert(0, str(EX))
from segment_tree import INF, SegmentTree  # noqa: E402

SEED, RN, RQ, RMAX = 20261023, 200, 2000, 1000
SCALE_N = 1_000_000


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Traced(SegmentTree):
    """SegmentTree that records each call of query/update (same code path: every call goes through super())."""

    def __init__(self, a):
        self.events = None
        super().__init__(a)

    def query(self, node, start, end, l, r):
        kind = 'outside' if r < start or end < l else 'inside' if l <= start and end <= r else 'partial'
        rec = {'node': node, 'start': start, 'end': end, 'kind': kind}
        if self.events is not None:
            self.events.append(rec)
        ret = super().query(node, start, end, l, r)
        rec['ret'] = None if ret == INF else ret
        return ret

    def update(self, node, start, end, i, x):
        before = self.tree[node]
        super().update(node, start, end, i, x)
        if self.events is not None:     # appended after the children: bottom-up order
            self.events.append({'node': node, 'start': start, 'end': end, 'before': before, 'after': self.tree[node]})


def nodes_of(st):
    out = []

    def walk(node, start, end, depth):
        out.append({'node': node, 'start': start, 'end': end, 'depth': depth, 'value': st.tree[node]})
        if start != end:
            mid = (start + end) // 2
            walk(2 * node, start, mid, depth + 1)
            walk(2 * node + 1, mid + 1, end, depth + 1)
    walk(1, 0, st.n - 1, 0)
    return sorted(out, key=lambda d: d['node'])


def parse(text):
    data = text.split()
    n = int(data[0])
    a = [int(v) for v in data[1:1 + n]]
    q = int(data[1 + n])
    ops = [(data[2 + n + 3 * k], int(data[3 + n + 3 * k]), int(data[4 + n + 3 * k])) for k in range(q)]
    return a, ops


def height(n):
    """Depth of the deepest leaf of the recursive split of n leaves (root = depth 0)."""
    d = 0
    while n > 1:
        n = (n + 1) // 2
        d += 1
    return d


def visited_count(n, l, r):
    """Number of query calls (visited nodes) for [l, r] on n leaves; same branching as SegmentTree.query."""
    cnt, stack = 0, [(0, n - 1)]
    while stack:
        s, e = stack.pop()
        cnt += 1
        if r < s or e < l or (l <= s and e <= r):
            continue
        m = (s + e) // 2
        stack += [(s, m), (m + 1, e)]
    return cnt


def excerpt(name):
    """Lines of SegmentTree.<name> exactly as in segment_tree.py (class indent removed) and their 1-based line span."""
    src = (EX / 'segment_tree.py').read_text().splitlines()
    i = next(k for k, ln in enumerate(src) if ln.startswith(f'    def {name}('))
    j = i
    while j + 1 < len(src) and src[j + 1].strip():
        j += 1
    return {'lines': [ln[4:] for ln in src[i:j + 1]], 'span': [i + 1, j + 1]}


def trace():
    text = (EX / 'input.txt').read_text()
    a, ops = parse(text)
    st = Traced(a)
    n = len(a)
    out = {'source': {'program': 'examples/segment_tree.py', 'programSha256': sha(EX / 'segment_tree.py'),
                      'input': 'examples/input.txt', 'inputSha256': sha(EX / 'input.txt'), 'writer': 'examples/make_data.py'},
           'n': n, 'array': a, 'nodes': nodes_of(st), 'ops': [], 'outputs': [],
           'code': {'source': 'examples/segment_tree.py', 'query': excerpt('query'), 'update': excerpt('update')}}
    arr = list(a)
    for op, u, v in ops:
        st.events = []
        if op == 'query':
            ans = st.query(1, 0, n - 1, u, v)
            out['ops'].append({'op': 'query', 'l': u, 'r': v, 'answer': ans, 'visits': st.events,
                               'chosen': [e['node'] for e in st.events if e['kind'] == 'inside'],
                               'scanned': v - u + 1, 'bruteForce': min(arr[u:v + 1])})
            out['outputs'].append(str(ans))
        else:
            old = arr[u]
            st.update(1, 0, n - 1, u, v)
            arr[u] = v
            out['ops'].append({'op': 'update', 'i': u, 'x': v, 'old': old, 'path': st.events, 'arrayAfter': list(arr),
                               'nodesAfter': nodes_of(st)})
        st.events = None
    upd = next(o for o in out['ops'] if o['op'] == 'update')
    containing = sum(1 for i in range(n) for j in range(i, n) if i <= upd['i'] <= j)
    rnd = random.Random(SEED)
    samples = [sorted((rnd.randrange(SCALE_N), rnd.randrange(SCALE_N))) for _ in range(300)]
    out['derived'] = {
        'allIntervals': n * (n + 1) // 2,
        'intervalsContainingUpdate': containing,
        'height': height(n),
        'updatePathNodes': len(upd['path']),
        'scale': {'n': SCALE_N, 'height': height(SCALE_N), 'updatePathNodes': height(SCALE_N) + 1,
                  'queryVisitedMaxOver300SeededQueries': max(visited_count(SCALE_N, l, r) for l, r in samples),
                  'queryVisitedBound': 4 * (height(SCALE_N) + 1)},
    }
    return out


def random_files():
    rnd = random.Random(SEED)
    a = [rnd.randint(-RMAX, RMAX) for _ in range(RN)]
    lines, expect = [], []
    for _ in range(RQ):
        if rnd.random() < 0.5:
            i, x = rnd.randrange(RN), rnd.randint(-RMAX, RMAX)
            lines.append(f'update {i} {x}')
            a[i] = x
        else:
            l, r = sorted((rnd.randrange(RN), rnd.randrange(RN)))
            lines.append(f'query {l} {r}')
            expect.append(str(min(a[l:r + 1])))
    # the initial array must be the one before the updates: rebuild it from the same seed
    rnd = random.Random(SEED)
    a0 = [rnd.randint(-RMAX, RMAX) for _ in range(RN)]
    text = f'{RN}\n' + ' '.join(map(str, a0)) + f'\n{RQ}\n' + '\n'.join(lines) + '\n'
    return text, '\n'.join(expect) + '\n'


def main():
    t = trace()
    rin, rexp = random_files()
    files = {FILM / 'data' / 'trace.json': json.dumps(t, ensure_ascii=False, indent=1) + '\n',
             EX / 'random-input.txt': rin, EX / 'random-expected.txt': rexp}
    if '--check' in sys.argv:
        stale = [str(p.relative_to(FILM)) for p, s in files.items() if not p.exists() or p.read_text() != s]
        print(json.dumps({'stale': stale}))
        sys.exit(1 if stale else 0)
    for p, s in files.items():
        p.parent.mkdir(exist_ok=True)
        p.write_text(s)
        print('wrote', p.relative_to(FILM), sha(p))


if __name__ == '__main__':
    main()
