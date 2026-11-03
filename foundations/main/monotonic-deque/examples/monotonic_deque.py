"""Sliding-window maximum with a monotonic deque (단조 덱), plus the naive scan it replaces.

  python3 monotonic_deque.py input.txt            # the film's example: every step, answers, operation counts
  python3 monotonic_deque.py latency-day.txt      # one day of generated latencies (n = 86,400, k = 300): counts only
  python3 monotonic_deque.py input.txt --json     # the trace the film reads (../trace.json)

Input (one case per file, '#' starts a comment):
  k <window size>
  a <v0> <v1> ...                      explicit values (integers), or
  gen latency <n> <seed>               n latencies (ms) from the LCG below — monotonic_deque.cpp makes the same ones

The deque holds indices whose values strictly decrease from front to back. For each new index i:
  1. front: drop the front index if it has left the window (index <= i - k)
  2. back:  drop back indices whose value is <= a[i]  (they leave earlier and are not larger: never a maximum again)
  3. push i
  4. once the window is full (i >= k - 1) the front index holds the window maximum
Every index is pushed once and popped at most once, so the whole pass is O(n); the deque never holds more than k.
"""
import json
import sys
from collections import deque
from pathlib import Path

SMALL = 30  # print every step for arrays up to this length


# ---------- input ----------
def lcg_latency(n, seed):
    """n latencies in ms: 40–69 ms, and about 1 in 200 seconds a spike of +120–399 ms (32-bit LCG, Numerical Recipes)."""
    x, out = seed & 0xFFFFFFFF, []
    for _ in range(n):
        x = (1664525 * x + 1013904223) & 0xFFFFFFFF
        r1 = x
        x = (1664525 * x + 1013904223) & 0xFFFFFFFF
        r2 = x
        v = 40 + (r1 >> 24) % 30
        if (r2 >> 16) % 200 == 0:
            v += 120 + (r2 >> 4) % 280
        out.append(v)
    return out


def read_input(path):
    """(a, k, source) from a case file; source is 'values' or 'gen latency <n> <seed>'."""
    k, a, source = None, None, 'values'
    for raw in Path(path).read_text().splitlines():
        line = raw.split('#', 1)[0].split()
        if not line:
            continue
        if line[0] == 'k':
            k = int(line[1])
        elif line[0] == 'a':
            a = [int(x) for x in line[1:]]
        elif line[:2] == ['gen', 'latency']:
            n, seed = int(line[2]), int(line[3])
            a, source = lcg_latency(n, seed), f'gen latency {n} {seed}'
        else:
            raise ValueError(f'{path}: unknown line {raw!r}')
    if k is None or a is None or not 1 <= k <= len(a):
        raise ValueError(f'{path}: need k and values with 1 <= k <= n')
    return a, k, source


# ---------- the two algorithms ----------
def window_max(a, k):
    dq, ans = deque(), []
    for i, v in enumerate(a):
        if dq and dq[0] <= i - k:
            dq.popleft()
        while dq and a[dq[-1]] <= v:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            ans.append(a[dq[0]])
    return ans


def window_min(a, k):
    """The same deque for minima: only the comparison flips, and the deque keeps increasing values."""
    dq, ans = deque(), []
    for i, v in enumerate(a):
        if dq and dq[0] <= i - k:
            dq.popleft()
        while dq and a[dq[-1]] >= v:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            ans.append(a[dq[0]])
    return ans


def sliding_max(a, k, steps=None):
    """window_max() with counters (the numbers the film and the receipts quote): same answers, plus operation counts.
    steps (a list) receives one record per index: what left the front, what was dropped at the back, the deque after."""
    dq, ans = deque(), []
    stats = {'push': 0, 'popFront': 0, 'popBack': 0, 'compare': 0, 'maxLen': 0}
    for i, v in enumerate(a):
        front_out, back_out = [], []
        if dq and dq[0] <= i - k:                  # 1. the front index has left the window
            front_out.append(dq.popleft())
            stats['popFront'] += 1
        while dq:                                   # 2. drop smaller-or-equal values at the back
            stats['compare'] += 1
            if a[dq[-1]] > v:
                break
            back_out.append(dq.pop())
            stats['popBack'] += 1
        dq.append(i)                                # 3. push the new index
        stats['push'] += 1
        stats['maxLen'] = max(stats['maxLen'], len(dq))
        if i >= k - 1:                              # 4. the front is the maximum of a[i-k+1 .. i]
            ans.append(a[dq[0]])
        if steps is not None:
            steps.append({'i': i, 'v': v, 'frontOut': front_out, 'backOut': back_out[::-1], 'deque': list(dq),
                          'window': [max(0, i - k + 1), i], 'max': a[dq[0]] if i >= k - 1 else None})
    return ans, stats


def naive_max(a, k):
    """Window maxima by scanning all k values of every window, and the number of value comparisons it made."""
    ans, compare = [], 0
    for s in range(len(a) - k + 1):
        best = a[s]
        for j in range(s + 1, s + k):
            compare += 1
            if a[j] > best:
                best = a[j]
        ans.append(best)
    return ans, compare


# ---------- output ----------
def pairs(idx, a):
    return '[' + ' '.join(f'{i}:{a[i]}' for i in idx) + ']' if idx else '-'


def report(a, k, source='values'):
    """The printed lines (the C++ example prints the same bytes)."""
    steps = [] if len(a) <= SMALL else None
    ans, st = sliding_max(a, k, steps)
    nans, ncmp = naive_max(a, k)
    out = [f'n {len(a)} k {k}' + ('' if source == 'values' else f' ({source})')]
    if steps is not None:
        for s in steps:
            out.append(f"step {s['i']} in {s['v']} | front-out {pairs(s['frontOut'], a)} | back-out {pairs(s['backOut'], a)}"
                       f" | deque {pairs(s['deque'], a)} | " + (f"max {s['max']}" if s['max'] is not None else 'filling'))
        out.append('answers ' + ' '.join(map(str, ans)))
    else:
        out.append(f'answers {len(ans)} values, first 5: ' + ' '.join(map(str, ans[:5])) + f', largest {max(ans)}')
    out.append(f"deque push {st['push']} pop-front {st['popFront']} pop-back {st['popBack']} compare {st['compare']} max-length {st['maxLen']}")
    out.append(f'naive compare {ncmp}')
    out.append('check naive == deque: ' + ('yes' if nans == ans == window_max(a, k) else 'NO'))
    return out


def trace(a, k, source, day=None):
    """What the film reads: the example's every step, answers and counts; with day = (a, k, source) the use-case numbers."""
    steps = []
    ans, st = sliding_max(a, k, steps)
    nans, ncmp = naive_max(a, k)
    t = {'source': 'examples/monotonic_deque.py input.txt --json', 'a': a, 'k': k, 'n': len(a), 'answers': ans, 'naiveAnswers': nans,
         'steps': steps, 'stats': st, 'naiveCompare': ncmp, 'naiveLooks': (len(a) - k + 1) * k}
    if day is not None:
        da, dk, dsrc = day
        dans, dst = sliding_max(da, dk)
        _, dncmp = naive_max(da, dk)
        head = 600  # the first ten minutes, drawn in the use-case scene
        t['day'] = {'source': dsrc, 'n': len(da), 'k': dk, 'answers': len(dans), 'stats': dst, 'naiveCompare': dncmp,
                    'head': da[:head], 'headMax': dans[:head - dk + 1], 'dayMax': max(da), 'spikes': sum(v >= 160 for v in da)}
    return t


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[2])
        return 2
    a, k, source = read_input(argv[1])
    if '--json' in argv:
        day = read_input(Path(argv[1]).with_name('latency-day.txt'))
        json.dump(trace(a, k, source, day), sys.stdout, ensure_ascii=False, separators=(',', ':'))
        sys.stdout.write('\n')
    else:
        sys.stdout.write('\n'.join(report(a, k, source)) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
