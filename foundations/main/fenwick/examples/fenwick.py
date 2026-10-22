"""펜윅 트리(Fenwick tree, Binary Indexed Tree) — 영상 'films/fenwick-20261022'의 실행 예제.

영상에 나오는 숫자는 모두 이 프로그램의 출력에서 나온다(examples/out/python.txt).
같은 출력을 C++17 판(fenwick.cpp)도 글자 하나까지 똑같이 낸다(run_examples.sh가 diff로 확인).

usage: python3 fenwick.py
"""


class Fenwick:
    """1번부터 n번까지. tree[i]는 (i - lowbit(i), i] 구간의 합을 맡는다."""

    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)          # tree[0]은 쓰지 않는다

    def update(self, i, d, path=None):
        """i번 값에 d를 더한다. 맨 오른쪽 1(i & -i)을 더해 가며 위로 올라간다."""
        while i <= self.n:
            if path is not None:
                path.append(i)
            self.tree[i] += d
            i += i & -i

    def prefix(self, i, path=None):
        """1번부터 i번까지의 합. 맨 오른쪽 1을 빼 가며 내려온다."""
        s = 0
        while i > 0:
            if path is not None:
                path.append(i)
            s += self.tree[i]
            i -= i & -i
        return s

    def range_sum(self, l, r):
        """l번부터 r번까지의 합 = prefix(r) - prefix(l - 1)."""
        return self.prefix(r) - self.prefix(l - 1)


def lowbit(i):
    return i & -i


def bits(x, width):
    """x의 하위 width비트(음수는 2의 보수)."""
    return format(x & ((1 << width) - 1), f'0{width}b')


class Lcg:
    """C++ 판과 같은 수열을 내는 작은 난수기(64비트 LCG)."""

    def __init__(self, seed):
        self.x = seed

    def next(self, k):
        self.x = (self.x * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        return (self.x >> 33) % k


def main():
    A = [3, 1, 4, 1, 5, 9, 2, 6]             # 1번..8번 (예시 값)
    n = len(A)
    fw = Fenwick(n)
    for i, v in enumerate(A, 1):
        fw.update(i, v)

    print('== 1. 배열과 펜윅 트리 ==')
    print('A    =', A)
    print('tree =', fw.tree[1:])
    for i in range(1, n + 1):
        lo = i - lowbit(i) + 1
        print(f'tree[{i}] bin={bits(i, 4)} lowbit={lowbit(i)} covers {lo}..{i} = {fw.tree[i]}')

    print('== 2. prefix(7) ==')
    path = []
    s = fw.prefix(7, path)
    print('path =', path, 'values =', [fw.tree[i] for i in path], 'sum =', s)
    print('naive sum(A[1..7]) =', sum(A[:7]), 'cells read =', 7)

    print('== 3. update(3, +5): A[3] 4 -> 9 ==')
    P_before = [sum(A[:i]) for i in range(1, n + 1)]
    A[2] += 5
    P_after = [sum(A[:i]) for i in range(1, n + 1)]
    changed = [i + 1 for i in range(n) if P_before[i] != P_after[i]]
    path = []
    fw.update(3, 5, path)
    print('path =', path, 'next =', path[-1] + lowbit(path[-1]), '> n')
    print('tree =', fw.tree[1:])
    print('prefix table before =', P_before)
    print('prefix table after  =', P_after)
    print('prefix table cells changed =', len(changed), changed)
    print('fenwick cells changed =', len(path), path)

    print('== 4. range_sum(3, 7) ==')
    p7, p2 = fw.prefix(7), fw.prefix(2)
    print(f'prefix(7) = {p7}, prefix(2) = {p2}, range_sum(3, 7) = {p7} - {p2} = {fw.range_sum(3, 7)}')
    print('check sum(A[3..7]) =', sum(A[2:7]))

    print('== 5. lowbit: i & -i (8-bit) ==')
    for i in (6, 7, 8):
        print(f'{i:>2} = {bits(i, 8)}  -{i} = {bits(-i, 8)}  {i} & -{i} = {bits(i & -i, 8)} = {i & -i}')

    print('== 6. steps for n = 1,000,000 ==')
    N = 1_000_000
    max_prefix = max_update = 0
    for i in range(1, N + 1):
        c, j = 0, i
        while j > 0:
            c += 1
            j -= j & -j
        max_prefix = max(max_prefix, c)
        c, j = 0, i
        while j <= N:
            c += 1
            j += j & -j
        max_update = max(max_update, c)
    print('max prefix steps =', max_prefix, 'max update steps =', max_update, 'bit length of n =', N.bit_length())

    print('== 7. random check vs plain array ==')
    rnd, m = Lcg(20261022), 1000
    plain, fw2 = [0] * (m + 1), Fenwick(m)
    ops = 20000
    for _ in range(ops):
        if rnd.next(2):
            i, d = rnd.next(m) + 1, rnd.next(201) - 100
            plain[i] += d
            fw2.update(i, d)
        else:
            l = rnd.next(m) + 1
            r = l + rnd.next(m - l + 1)
            assert fw2.range_sum(l, r) == sum(plain[l:r + 1]), (l, r)
    print(f'{ops} random ops on n = {m}: all range sums match')


if __name__ == '__main__':
    main()
