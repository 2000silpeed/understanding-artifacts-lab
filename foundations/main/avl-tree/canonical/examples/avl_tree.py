"""AVL tree: keep every node's left/right height difference within 1 by rotating on the way back up an insertion.

  python3 avl_tree.py <input.txt>            # the report (same bytes as the C++17 build of avl_tree.cpp)
  python3 avl_tree.py <input.txt> --json     # the film's number source (trace.json): every insert with tree snapshots

Input (one directive per line, '#' starts a comment):
  insert 50 40 30 ...                 keys in arrival order (a key that is already in the tree is ignored)
  gen sequential <n> first <k>        n keys k, k+1, …, k+n-1 in increasing order (order numbers that only go up)
  gen random <n> seed <s> max <m>     n keys from a 32-bit LCG (seed s) in 1..m, duplicates possible
  search 65 35                        keys to look up after all inserts

Height: an empty tree has height 0, one node height 1, height(node) = 1 + max(height(left), height(right)).
Balance factor bf(node) = height(left) - height(right); the AVL rule is -1 <= bf <= 1 at every node.
Visits: how many nodes a search looks at (one 3-way key comparison per node).
The plain binary search tree (no rotations) is built from the same keys for comparison; it is iterative, because a
sorted arrival order makes it a chain as deep as the number of keys.
"""
import json
import sys
from pathlib import Path

SMALL = 32          # inputs with at most this many keys print every insert step


class Node:
    __slots__ = ('key', 'left', 'right', 'height')

    def __init__(self, key):
        self.key, self.left, self.right, self.height = key, None, None, 1


def height(n):
    return n.height if n else 0


def bf(n):
    return height(n.left) - height(n.right)


def update(n):
    n.height = 1 + max(height(n.left), height(n.right))


def rotate_right(y):
    x = y.left
    y.left = x.right
    x.right = y
    update(y)
    update(x)
    return x


def rotate_left(x):
    y = x.right
    x.right = y.left
    y.left = x
    update(x)
    update(y)
    return y


def case_of(n):
    """'LL', 'LR', 'RR' or 'RL' when n is out of balance (|bf| = 2), else None. Used for the report only."""
    if bf(n) > 1:
        return 'LR' if bf(n.left) < 0 else 'LL'
    if bf(n) < -1:
        return 'RL' if bf(n.right) > 0 else 'RR'
    return None


def rebalance(n):
    update(n)
    if bf(n) > 1:
        if bf(n.left) < 0:
            n.left = rotate_left(n.left)
        return rotate_right(n)
    if bf(n) < -1:
        if bf(n.right) > 0:
            n.right = rotate_right(n.right)
        return rotate_left(n)
    return n


def insert(n, key, log):
    if n is None:
        return Node(key)
    if key < n.key:
        n.left = insert(n.left, key, log)
    elif key > n.key:
        n.right = insert(n.right, key, log)
    else:
        return n                       # already in the tree
    update(n)
    if case_of(n):                     # for the report: (case, node, its bf, the child on the tall side)
        log.append((case_of(n), n.key, bf(n), (n.left if bf(n) > 0 else n.right).key))
    return rebalance(n)


def search(n, key):
    """(found, path of visited keys)."""
    path = []
    while n:
        path.append(n.key)
        if key == n.key:
            return True, path
        n = n.left if key < n.key else n.right
    return False, path


# ---------- the plain binary search tree (no balancing), iterative ----------
class Plain:
    def __init__(self):
        self.key, self.left, self.right = [], [], []

    def insert(self, key):
        if not self.key:
            self.key.append(key); self.left.append(-1); self.right.append(-1)
            return
        i = 0
        while True:
            k = self.key[i]
            if key == k:
                return
            side = self.left if key < k else self.right
            if side[i] < 0:
                side[i] = len(self.key)
                self.key.append(key); self.left.append(-1); self.right.append(-1)
                return
            i = side[i]

    def search(self, key):
        path, i = [], 0 if self.key else -1
        while i >= 0:
            path.append(self.key[i])
            if key == self.key[i]:
                return True, path
            i = self.left[i] if key < self.key[i] else self.right[i]
        return False, path

    def depths(self):
        """Depth (root = 1) of every node, iteratively."""
        out, stack = [], [(0, 1)] if self.key else []
        while stack:
            i, d = stack.pop()
            out.append(d)
            for c in (self.left[i], self.right[i]):
                if c >= 0:
                    stack.append((c, d + 1))
        return out


# ---------- reading, walking, checking ----------
def lcg(n, seed, top):
    """n keys in 1..top from the 32-bit LCG x = (1664525 x + 1013904223) mod 2^32 (same in avl_tree.cpp)."""
    x, out = seed & 0xFFFFFFFF, []
    for _ in range(n):
        x = (1664525 * x + 1013904223) & 0xFFFFFFFF
        out.append(1 + (x >> 8) % top)
    return out


def read_input(path):
    """(keys, searches, source) from an input file."""
    keys, searches, src = [], [], 'keys'
    for raw in Path(path).read_text().splitlines():
        line = raw.split('#', 1)[0].split()
        if not line:
            continue
        if line[0] == 'insert':
            keys += [int(x) for x in line[1:]]
        elif line[0] == 'search':
            searches += [int(x) for x in line[1:]]
        elif line[0] == 'gen' and line[1] == 'sequential':
            n, first = int(line[2]), int(line[4])
            keys += list(range(first, first + n))
            src = ' '.join(line)
        elif line[0] == 'gen' and line[1] == 'random':
            keys += lcg(int(line[2]), int(line[4]), int(line[6]))
            src = ' '.join(line)
        else:
            raise ValueError(f'{path}: unknown directive {raw!r}')
    return keys, searches, src


def preorder(n):
    out, stack = [], [n] if n else []
    while stack:
        x = stack.pop()
        out.append(x.key)
        if x.right:
            stack.append(x.right)
        if x.left:
            stack.append(x.left)
    return out


def inorder(n):
    out, stack = [], []
    while stack or n:
        while n:
            stack.append(n)
            n = n.left
        n = stack.pop()
        out.append(n.key)
        n = n.right
    return out


def nodes(n):
    out, stack = [], [n] if n else []
    while stack:
        x = stack.pop()
        out.append(x)
        stack += [c for c in (x.left, x.right) if c]
    return out


def depth_counts(n):
    """How many nodes sit on each level (root level first)."""
    out, level = [], [n] if n else []
    while level:
        out.append(len(level))
        level = [c for x in level for c in (x.left, x.right) if c]
    return out


def avl_ok(n):
    """Every stored height is right and every balance factor is in -1..1."""
    for x in nodes(n):
        if x.height != 1 + max(height(x.left), height(x.right)) or abs(bf(x)) > 1:
            return False
    return True


def min_nodes(h):
    """Fewest nodes an AVL tree of height h can have: N(0) = 0, N(1) = 1, N(h) = N(h-1) + N(h-2) + 1."""
    a, b = 0, 1
    if h == 0:
        return 0
    for _ in range(h - 1):
        a, b = b, a + b + 1
    return b


def max_height(n):
    """The tallest an AVL tree with n nodes can be: the largest h with min_nodes(h) <= n."""
    h = 0
    while min_nodes(h + 1) <= n:
        h += 1
    return h


def sgn(b):
    return f'{b:+d}' if b else '0'


def run(keys):
    """Insert every key; returns (root, per-key events [(key, path, log, duplicate, height after)], plain tree)."""
    root, plain, events, seen = None, Plain(), [], set()
    for k in keys:
        path = search(root, k)[1]
        log = []
        root = insert(root, k, log)
        plain.insert(k)
        events.append((k, path, log, k in seen, height(root)))
        seen.add(k)
    return root, events, plain


def report(keys, searches, src):
    """The printed report: identical bytes in avl_tree.cpp."""
    root, events, plain = run(keys)
    n = len(nodes(root))
    out = [f'keys {len(keys)} nodes {n} ({src})']
    count = {'LL': 0, 'RR': 0, 'LR': 0, 'RL': 0}
    for step, (k, path, log, dup, h) in enumerate(events, 1):
        for kind, *_ in log:
            count[kind] += 1
        if len(keys) <= SMALL:
            if dup:
                fix = 'already in tree'
            elif log:
                kind, at, b, ch = log[0]
                rot = {'LL': f'right({at})', 'RR': f'left({at})', 'LR': f'left({ch}) right({at})', 'RL': f'right({ch}) left({at})'}[kind]
                fix = f'unbalanced {at} bf {sgn(b)} | {kind} {rot}'
            else:
                fix = 'balanced'
            out.append(f"step {step} insert {k} | path {' '.join(map(str, path)) or '-'} | {fix} | height {h}")
    if len(keys) <= SMALL:
        out.append('preorder ' + ' '.join(map(str, preorder(root))))
        out.append('inorder ' + ' '.join(map(str, inorder(root))))
    out.append(f'avl height {height(root)} | max for {n} nodes {max_height(n)}')
    out.append(f"rotations LL {count['LL']} RR {count['RR']} LR {count['LR']} RL {count['RL']}")
    out.append('avl levels ' + ' '.join(map(str, depth_counts(root))))
    pd = plain.depths()
    out.append(f'plain height {max(pd) if pd else 0}')
    for q in searches:
        fa, pa = search(root, q)
        fp, pp = plain.search(q)
        assert fa == fp
        shown = ' '.join(map(str, pa)) if len(pa) <= 20 else f'{len(pa)} nodes'
        out.append(f"search {q} {'found' if fa else 'missing'} | visits avl {len(pa)} plain {len(pp)} | path {shown}")
    if n:
        ta = sum(len(search(root, k)[1]) for k in inorder(root))
        tp = sum(pd)
        out.append(f'average visits over {n} keys | avl {avg(ta, n)} | plain {avg(tp, n)}')
    keys_sorted = inorder(root)
    out.append('check inorder sorted: ' + ('yes' if all(a < b for a, b in zip(keys_sorted, keys_sorted[1:])) and keys_sorted == sorted(set(keys)) else 'NO'))
    out.append('check avl heights and balance: ' + ('yes' if avl_ok(root) else 'NO'))
    out.append('check height <= max height: ' + ('yes' if height(root) <= max_height(n) else 'NO'))
    return out


def avg(total, n):
    """total / n with two decimals, rounded half up, in integers (no float formatting differences with C++)."""
    c = (total * 100 * 2 + n) // (2 * n)
    return f'{c // 100}.{c % 100:02d}'


# ---------- trace for the film (snapshots of every insert) ----------
class _Copy:
    """A detached copy of the tree for the trace: plain attach, then the same rotations one at a time."""

    def __init__(self, root):
        self.root = self._cp(root)

    @staticmethod
    def _cp(n):
        if n is None:
            return None
        c = Node(n.key)
        c.left, c.right, c.height = _Copy._cp(n.left), _Copy._cp(n.right), n.height
        return c

    def attach(self, key):
        """Plain BST attach + height update on the path; returns the path nodes, root first."""
        if self.root is None:
            self.root = Node(key)
            return [self.root]
        path, n = [], self.root
        while True:
            path.append(n)
            side = 'left' if key < n.key else 'right'
            nxt = getattr(n, side)
            if nxt is None:
                setattr(n, side, Node(key))
                path.append(getattr(n, side))
                break
            n = nxt
        for x in reversed(path):
            update(x)
        return path

    def replace(self, parent, old, new):
        if parent is None:
            self.root = new
        elif parent.left is old:
            parent.left = new
        else:
            parent.right = new


def snap(root):
    """{'root': key, 'nodes': {key: {l, r, h, bf, d}}} with depth d (root = 0)."""
    out, stack = {}, [(root, 0)] if root else []
    while stack:
        n, d = stack.pop()
        out[str(n.key)] = {'l': n.left.key if n.left else None, 'r': n.right.key if n.right else None,
                           'h': n.height, 'bf': bf(n), 'd': d}
        stack += [(c, d + 1) for c in (n.left, n.right) if c]
    return {'root': root.key if root else None, 'nodes': out}


def trace(keys, searches, src, usecase=None):
    """The film's number source: every insert with the tree after the plain attach (pre-rotation), after the first
    rotation of a double rotation, and after the fix (= the real AVL tree, asserted)."""
    root, steps = None, []
    for k in keys:
        cp = _Copy(root)
        found = search(cp.root, k)[0]
        log = []
        root = insert(root, k, log)
        if found:
            steps.append({'key': k, 'dup': True})
            continue
        path = cp.attach(k)
        before = snap(cp.root)
        pathbf = [[x.key, bf(x)] for x in reversed(path)]          # from the new node up to the root
        st = {'key': k, 'dup': False, 'path': [x.key for x in path[:-1]], 'pathBf': pathbf, 'before': before,
              'case': None, 'at': None, 'atBf': None, 'child': None, 'rotations': [], 'mid': None}
        bad = next((i for i in range(len(path) - 1, -1, -1) if abs(bf(path[i])) > 1), None)
        if bad is not None:
            z = path[bad]
            parent = path[bad - 1] if bad > 0 else None
            b = bf(z)
            child = z.left if b > 1 else z.right
            case = ('LL' if bf(child) >= 0 else 'LR') if b > 1 else ('RR' if bf(child) <= 0 else 'RL')
            st.update(case=case, at=z.key, atBf=b, child=child.key)
            if case == 'LR':
                z.left = rotate_left(child)
                st['rotations'].append({'dir': 'left', 'at': child.key})
                st['mid'] = snap(cp.root)
            elif case == 'RL':
                z.right = rotate_right(child)
                st['rotations'].append({'dir': 'right', 'at': child.key})
                st['mid'] = snap(cp.root)
            new = rotate_right(z) if b > 1 else rotate_left(z)
            st['rotations'].append({'dir': 'right' if b > 1 else 'left', 'at': z.key})
            cp.replace(parent, z, new)
            for x in reversed(path[:bad]):
                update(x)
            assert log and log[0] == (case, z.key, b, child.key), (log, case, z.key)
        else:
            assert not log
        st['after'] = snap(root)
        assert st['after'] == snap(cp.root), f'trace copy differs from the AVL tree after inserting {k}'
        steps.append(st)
    plain = Plain()
    for k in keys:
        plain.insert(k)
    out = {
        'source': 'examples/avl_tree.py input.txt --json',
        'keys': keys, 'n': len(nodes(root)), 'height': height(root), 'steps': steps,
        'preorder': preorder(root), 'inorder': inorder(root),
        'plainHeight': max(plain.depths()) if keys else 0, 'plain': plain_snap(plain),
        'cases': [s['case'] for s in steps if s.get('case')],
        'searches': [{'key': q, 'found': search(root, q)[0], 'path': search(root, q)[1], 'plainPath': plain.search(q)[1]} for q in searches],
        'minNodes': [min_nodes(h) for h in range(0, 21)],
    }
    if usecase:
        out['usecase'] = usecase_summary(*usecase)
    return out


def usecase_summary(keys, searches, src):
    root, events, plain = run(keys)
    n = len(nodes(root))
    count = {'LL': 0, 'RR': 0, 'LR': 0, 'RL': 0}
    for _, _, log, _, _ in events:
        for kind, *_ in log:
            count[kind] += 1
    pd = plain.depths()
    return {
        'source': src, 'n': n, 'first': keys[0], 'last': keys[-1],
        'avlHeight': height(root), 'plainHeight': max(pd), 'maxHeight': max_height(n),
        'levels': depth_counts(root), 'rotations': count,
        'searches': [{'key': q, 'avl': len(search(root, q)[1]), 'plain': len(plain.search(q)[1]), 'path': search(root, q)[1]} for q in searches],
        'visitTotal': {'avl': sum(len(search(root, k)[1]) for k in inorder(root)), 'plain': sum(pd)},
        'depth': [len(search(root, k)[1]) - 1 for k in inorder(root)],     # AVL depth (root = 0) of every key, in key order
    }


def plain_snap(plain):
    """The plain tree in the snapshot format of snap() (bf omitted): {'root', 'nodes': {key: {l, r, h, d}}}."""
    if not plain.key:
        return {'root': None, 'nodes': {}}
    order, stack = [], [(0, 0)]
    while stack:
        i, d = stack.pop()
        order.append((i, d))
        stack += [(c, d + 1) for c in (plain.left[i], plain.right[i]) if c >= 0]
    hs = {}
    for i, _ in reversed(order):           # children come after their parent in `order`
        hs[i] = 1 + max([hs[c] for c in (plain.left[i], plain.right[i]) if c >= 0], default=0)
    key = lambda c: plain.key[c] if c >= 0 else None
    return {'root': plain.key[0], 'nodes': {str(plain.key[i]): {'l': key(plain.left[i]), 'r': key(plain.right[i]), 'h': hs[i], 'd': d} for i, d in order}}


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    keys, searches, src = read_input(argv[1])
    if '--json' in argv:
        here = Path(argv[1]).resolve().parent
        uc = read_input(here / 'orders.txt')
        json.dump(trace(keys, searches, src, uc), sys.stdout, ensure_ascii=False, separators=(',', ':'))
        sys.stdout.write('\n')
        return 0
    sys.stdout.write('\n'.join(report(keys, searches, src)) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
