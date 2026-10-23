"""세그먼트 트리: 한 점 갱신 + 구간 최솟값 질의 (재귀, 노드 번호는 1부터).

입력 (표준 입력):
  n
  a0 a1 ... a(n-1)
  q
  query l r      # a[l..r] (양 끝 포함, 인덱스는 0부터)의 최솟값을 한 줄에 출력
  update i x     # a[i] = x

사용: python3 segment_tree.py < input.txt
"""
import sys

INF = float('inf')


class SegmentTree:
    def __init__(self, a):
        self.n = len(a)
        self.tree = [INF] * (4 * self.n)
        self.build(a, 1, 0, self.n - 1)

    def build(self, a, node, start, end):
        if start == end:
            self.tree[node] = a[start]
            return
        mid = (start + end) // 2
        self.build(a, 2 * node, start, mid)
        self.build(a, 2 * node + 1, mid + 1, end)
        self.tree[node] = min(self.tree[2 * node], self.tree[2 * node + 1])

    def query(self, node, start, end, l, r):
        if r < start or end < l:           # 밖: 겹치지 않음
            return INF
        if l <= start and end <= r:        # 안: 통째로 포함
            return self.tree[node]
        mid = (start + end) // 2           # 걸침: 두 자식으로
        left = self.query(2 * node, start, mid, l, r)
        right = self.query(2 * node + 1, mid + 1, end, l, r)
        return min(left, right)

    def update(self, node, start, end, i, x):
        if start == end:                   # 잎: 값을 바꾼다
            self.tree[node] = x
            return
        mid = (start + end) // 2
        if i <= mid:
            self.update(2 * node, start, mid, i, x)
        else:
            self.update(2 * node + 1, mid + 1, end, i, x)
        self.tree[node] = min(self.tree[2 * node], self.tree[2 * node + 1])


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    a = [int(v) for v in data[1:1 + n]]
    q = int(data[1 + n])
    st = SegmentTree(a)
    pos = 2 + n
    out = []
    for _ in range(q):
        op, u, v = data[pos], int(data[pos + 1]), int(data[pos + 2])
        pos += 3
        if op == 'query':
            out.append(str(st.query(1, 0, n - 1, u, v)))
        elif op == 'update':
            st.update(1, 0, n - 1, u, v)
        else:
            raise SystemExit(f'unknown operation: {op}')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
