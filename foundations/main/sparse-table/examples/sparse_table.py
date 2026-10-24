"""Sparse table: range minimum queries on an array that never changes.

Build once, in O(n log n): row k of the table holds, for every start index i, the minimum of the block
a[i .. i + 2^k - 1]. Row 0 is the array itself; row k is made from two neighbouring blocks of row k - 1.
Answer each query [l, r] in O(1): with k = floor(log2(r - l + 1)), the block starting at l and the block ending at r
(both of length 2^k) cover [l, r] together. They may overlap, which is harmless for min (min(x, x) = x) but not for
sum: the overlap would be counted twice (sum_trap() shows it on the same blocks).

usage:
  python3 sparse_table.py input.txt            # the text report (identical to the C++17 example's output)
  python3 sparse_table.py input.txt --json     # the same facts as JSON (the film's trace.json)
input.txt:  n / n integers / q / q lines "l r" (0-based, inclusive). Lines starting with # are ignored.
"""
import json
import sys


def build_log(n):
    """lg[x] = floor(log2 x) for 1 <= x <= n (lg[0] is unused)."""
    lg = [0] * (n + 1)
    for x in range(2, n + 1):
        lg[x] = lg[x // 2] + 1
    return lg


def build(a):
    """table[k][i] = min(a[i : i + 2^k]) for every k with 2^k <= n."""
    n = len(a)
    table = [list(a)]
    k = 1
    while (1 << k) <= n:
        prev, half = table[k - 1], 1 << (k - 1)
        row = []
        for i in range(n - (1 << k) + 1):
            row.append(min(prev[i], prev[i + half]))
        table.append(row)
        k += 1
    return table


def query(table, lg, l, r):
    """Minimum of a[l..r] (inclusive) from two blocks of length 2^k."""
    k = lg[r - l + 1]
    left = table[k][l]
    right = table[k][r - (1 << k) + 1]
    return min(left, right)


def explain(table, lg, l, r):
    """The steps of query(): length, row k, both blocks (start, end, value) and the answer."""
    length = r - l + 1
    k = lg[length]
    s2 = r - (1 << k) + 1
    first = (l, l + (1 << k) - 1, table[k][l])
    second = (s2, r, table[k][s2])
    return {'l': l, 'r': r, 'len': length, 'k': k, 'size': 1 << k, 'first': first, 'second': second,
            'min': min(first[2], second[2]), 'overlap': [max(l, s2), min(first[1], r)] if s2 <= first[1] else None}


def sum_trap(a, ex):
    """What goes wrong if the same two blocks are used for a sum: the overlap is counted twice."""
    blk = lambda s, e: sum(a[s:e + 1])
    b1, b2 = blk(ex['first'][0], ex['first'][1]), blk(ex['second'][0], ex['second'][1])
    ov = blk(*ex['overlap']) if ex['overlap'] else 0
    return {'first': b1, 'second': b2, 'blocks': b1 + b2, 'true': blk(ex['l'], ex['r']), 'overlapSum': ov}


def covering(n, idx):
    """Table cells (k, i) whose block contains index idx: what an update of a[idx] would have to rebuild."""
    out = []
    k = 0
    while (1 << k) <= n:
        for i in range(max(0, idx - (1 << k) + 1), min(idx, n - (1 << k)) + 1):
            out.append((k, i))
        k += 1
    return out


def cells_for(n):
    """Number of table cells for an array of n elements: sum over k of (n - 2^k + 1)."""
    total, k = 0, 0
    while (1 << k) <= n:
        total += n - (1 << k) + 1
        k += 1
    return total, k


def read_input(path):
    nums = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.split('#', 1)[0]
            nums.extend(int(x) for x in line.split())
    n = nums[0]
    a = nums[1:1 + n]
    q = nums[1 + n]
    qs = [(nums[2 + n + 2 * j], nums[3 + n + 2 * j]) for j in range(q)]
    if len(a) != n or len(nums) != 2 + n + 2 * q:
        raise ValueError(f'{path}: expected n, n values, q and q pairs')
    for l, r in qs:
        if not 0 <= l <= r < n:
            raise ValueError(f'{path}: query {l} {r} outside 0..{n - 1}')
    return a, qs


def report(a, qs):
    """The text report, line by line (the C++ example prints the same lines)."""
    table, lg = build(a), build_log(len(a))
    out = [f'n = {len(a)}', 'a     = ' + ' '.join(map(str, a))]
    for k, row in enumerate(table):
        out.append(f'len {1 << k:<2}= ' + ' '.join(map(str, row)))
    out.append(f'cells = {sum(len(r) for r in table)}')
    for l, r in qs:
        ex = explain(table, lg, l, r)
        (s1, e1, v1), (s2, e2, v2) = ex['first'], ex['second']
        out.append(f'query {l} {r}: len {ex["len"]}, k {ex["k"]}, [{s1},{e1}] -> {v1}, [{s2},{e2}] -> {v2}, min {ex["min"]}')
    for l, r in qs:
        ex = explain(table, lg, l, r)
        st = sum_trap(a, ex)
        out.append(f'sum {l} {r}: blocks {st["first"]} + {st["second"]} = {st["blocks"]}, true {st["true"]}')
    return out


def trace(a, qs, big=1_000_000):
    """Everything the film shows, from the same functions as the report."""
    table, lg = build(a), build_log(len(a))
    n = len(a)
    exs = [explain(table, lg, l, r) for l, r in qs]
    big_cells, big_rows = cells_for(big)
    return {
        'source': 'examples/sparse_table.py --json',
        'a': a, 'n': n,
        'table': table,
        'rowLengths': [len(r) for r in table],
        'cells': sum(len(r) for r in table),
        'comparisons': sum(len(r) for r in table[1:]),
        'allIntervals': n * (n + 1) // 2,
        'log': lg,
        'queries': [{**ex, 'first': list(ex['first']), 'second': list(ex['second']), 'sumTrap': sum_trap(a, ex),
                     'scan': a[ex['l']:ex['r'] + 1]} for ex in exs],
        'big': {'n': big, 'rows': big_rows, 'cells': big_cells, 'allIntervals': big * (big + 1) // 2, 'scanWorst': big},
        'update': {'index': 5, 'cells': [list(c) for c in covering(n, 5)]},
    }


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().split('\n\n')[-1], file=sys.stderr)
        return 2
    a, qs = read_input(argv[1])
    if '--json' in argv:
        json.dump(trace(a, qs), sys.stdout, ensure_ascii=False, indent=1)
        sys.stdout.write('\n')
    else:
        print('\n'.join(report(a, qs)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
