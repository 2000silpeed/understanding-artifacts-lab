"""B+ 트리: 리프 연결과 범위 탐색 (강의 16, data_structures).

키는 모두 리프에 있고, 내부 노드는 길 안내용 구분 키만 가진다. 리프는 next 링크로 키 순서대로 이어진다.
range_search는 시작 키가 있을 리프까지 한 번 내려간 뒤, 리프 링크를 따라 오른쪽으로 걷는다.
range_search_without_links는 비교용이다. 리프 링크를 쓰지 않고, 리프를 다 읽을 때마다 부모로 올라갔다가
다음 자식으로 다시 내려간다(링크 없는 트리의 순회).

이동 수(moves)는 노드에서 노드로 옮겨 간 횟수다. 내려가기, 올라가기, 리프 링크 한 칸이 모두 1이다.
표준 라이브러리만 쓴다. C++17 판은 ../cpp/bplustree.cpp 이며 같은 입력에 같은 출력을 낸다.
"""
from bisect import bisect_right, insort


class Node:
    __slots__ = ('keys', 'children', 'next', 'name')

    def __init__(self, leaf):
        self.keys = []
        self.children = None if leaf else []
        self.next = None  # 리프만 쓴다: 오른쪽 이웃 리프
        self.name = ''

    @property
    def leaf(self):
        return self.children is None


class BPlusTree:
    def __init__(self, max_keys=3):
        if max_keys < 3:
            raise ValueError('max_keys must be at least 3')
        self.max_keys = max_keys
        self.root = Node(leaf=True)

    # ---------- 삽입 ----------
    def insert(self, key):
        """키를 넣는다. 이미 있으면 False. 넘친 노드는 둘로 나누고 구분 키를 부모로 올린다."""
        split = self._insert(self.root, key)
        if split is False:
            return False
        if split is not None:
            sep, right = split
            root = Node(leaf=False)
            root.keys = [sep]
            root.children = [self.root, right]
            self.root = root
        return True

    def _insert(self, node, key):
        if node.leaf:
            i = bisect_right(node.keys, key)
            if i > 0 and node.keys[i - 1] == key:
                return False
            insort(node.keys, key)
            if len(node.keys) <= self.max_keys:
                return None
            mid = len(node.keys) // 2
            right = Node(leaf=True)
            right.keys = node.keys[mid:]
            node.keys = node.keys[:mid]
            right.next, node.next = node.next, right
            return right.keys[0], right  # 리프 분할: 오른쪽 첫 키를 복사해서 올린다
        i = bisect_right(node.keys, key)
        split = self._insert(node.children[i], key)
        if split is None or split is False:
            return split
        sep, right_child = split
        node.keys.insert(i, sep)
        node.children.insert(i + 1, right_child)
        if len(node.keys) <= self.max_keys:
            return None
        mid = len(node.keys) // 2
        right = Node(leaf=False)
        up = node.keys[mid]  # 내부 분할: 가운데 키는 옮겨서 올린다(복사하지 않는다)
        right.keys = node.keys[mid + 1:]
        right.children = node.children[mid + 1:]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        return up, right

    # ---------- 구조 ----------
    def levels(self):
        """뿌리부터 층별 노드 목록. 이름을 붙인다: 뿌리 R, 내부 I1.., 리프 L1.. (왼쪽부터)."""
        out, level = [], [self.root]
        while level:
            out.append(level)
            level = [c for n in level if not n.leaf for c in n.children]
        inner = 0
        for depth, lv in enumerate(out):
            for j, n in enumerate(lv):
                if depth == 0:
                    n.name = 'R'
                elif n.leaf:
                    n.name = f'L{j + 1}'
                else:
                    inner += 1
                    n.name = f'I{inner}'
        return out

    def height(self):
        h, n = 1, self.root
        while not n.leaf:
            n, h = n.children[0], h + 1
        return h

    def leaf_chain(self):
        """가장 왼쪽 리프에서 next 링크를 따라간 리프 목록."""
        n = self.root
        while not n.leaf:
            n = n.children[0]
        chain = []
        while n is not None:
            chain.append(n)
            n = n.next
        return chain

    def check(self):
        """불변식: 리프 깊이가 모두 같고, 키가 정렬돼 있고, 링크 순서 = 키 순서, 노드 크기 제한."""
        depths = set()

        def walk(n, depth, lo, hi):
            assert n.keys == sorted(n.keys) and len(n.keys) <= self.max_keys
            assert all((lo is None or k >= lo) and (hi is None or k < hi) for k in n.keys)
            if n.leaf:
                depths.add(depth)
                return
            assert len(n.children) == len(n.keys) + 1
            bounds = [lo] + n.keys + [hi]
            for i, c in enumerate(n.children):
                walk(c, depth + 1, bounds[i], bounds[i + 1])

        walk(self.root, 1, None, None)
        assert len(depths) == 1
        keys = [k for leaf in self.leaf_chain() for k in leaf.keys]
        assert keys == sorted(keys) and len(keys) == len(set(keys))
        return True

    # ---------- 탐색 ----------
    def search(self, key):
        """키 하나 찾기: 뿌리에서 리프까지 내려간다. (찾았는가, 지나간 노드 이름)"""
        path, n = [], self.root
        while True:
            path.append(n.name)
            if n.leaf:
                return key in n.keys, path
            n = n.children[bisect_right(n.keys, key)]

    # [excerpt:range_search]
    def range_search(self, lo, hi):
        node = self.root
        descent = []
        while not node.leaf:                 # 1) 한 번만 내려간다
            descent.append(node.name)
            node = node.children[bisect_right(node.keys, lo)]
        found, walked = [], []
        while node is not None:              # 2) 리프 링크를 따라 걷는다
            walked.append(node.name)
            for k in node.keys:
                if k > hi:                   # 3) hi를 넘으면 멈춘다
                    return found, descent, walked
                if k >= lo:
                    found.append(k)
            node = node.next
        return found, descent, walked
    # [/excerpt]

    def range_search_without_links(self, lo, hi):
        """비교용: next 링크를 쓰지 않는다. 리프를 다 읽으면 부모로 올라가 다음 자식으로 내려간다.
        반환: (찾은 키, 밟은 노드 이름 순서). 올라가며 지나간 노드도 다시 적는다. 이동 수 = len(route) - 1."""
        route, stack, node = [], [], self.root
        while not node.leaf:
            route.append(node.name)
            i = bisect_right(node.keys, lo)
            stack.append([node, i])
            node = node.children[i]
        found = []
        while True:
            route.append(node.name)
            for k in node.keys:
                if k > hi:
                    return found, route
                if k >= lo:
                    found.append(k)
            while stack and stack[-1][1] == len(stack[-1][0].children) - 1:
                route.append(stack.pop()[0].name)  # 마지막 자식까지 읽은 부모: 지나서 한 층 더 올라간다
            if not stack:
                return found, route
            parent = stack[-1]
            route.append(parent[0].name)  # 부모로 올라가 다음 자식을 고른다
            parent[1] += 1
            node = parent[0].children[parent[1]]
            while not node.leaf:
                route.append(node.name)
                stack.append([node, 0])
                node = node.children[0]

def build(keys, max_keys):
    t = BPlusTree(max_keys)
    for k in keys:
        t.insert(k)
    t.levels()
    t.check()
    return t
