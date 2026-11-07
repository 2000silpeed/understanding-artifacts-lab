# AVL 트리: 높이 균형과 회전으로 탐색 성능 유지하기 — 수업 노트

AI 기본기 연구실 · 자료구조. 영상(`film.js`)과 같은 순서로 쓴다: **핵심 요약 → 사용 상황 → 본 강의**.
이 노트의 모든 숫자는 `examples/`의 실제 실행 결과에서 왔고, `test_source.py`가 노트와 실행 결과를 맞춰 본다.
예제 키는 설명용으로 고른 **예시 값**이고, 주문 번호 1만 건은 규칙(1부터 1씩 증가)으로 **만든 예시 데이터**다(실제 서비스 기록이 아니다).

## 1. 핵심 요약

1. **높이 차이는 1까지.** 모든 노드에서 왼쪽 서브트리와 오른쪽 서브트리의 높이 차이(균형 인수)를 −1, 0, +1 가운데 하나로 지킨다.
2. **깨지면 그 자리에서 회전.** 키를 넣다가 어떤 노드의 차이가 2가 되면, 그 노드에서 회전 한 번(곧은 모양) 또는 두 번(꺾인 모양)으로 바로 고친다.
3. **그래서 높이 ∝ log n.** 높이가 늘 노드 수의 로그에 비례하므로 찾기와 넣기가 O(log n)이다.

이름은 만든 두 사람(Adelson-Velsky, Landis)의 머리글자다. AVL 트리는 **이진 탐색 트리**에 "높이 균형" 규칙 하나를 더한 것이다.

## 2. 사용 상황: 주문 번호로 주문 찾기

주문 서버가 주문 번호를 키로 주문을 저장하고, 고객이 주문 번호로 조회한다. 주문 번호는 1번부터 1씩 늘어나며
들어온다(하루 주문 10,000건). 정렬된 순서로 들어오는 키는 보통의 이진 탐색 트리에게 최악이다: 새 번호가 늘 맨
오른쪽에 붙어 트리가 한 줄로 늘어진다. `python3 avl_tree.py orders.txt`의 실제 출력(C++17도 바이트 단위로 같다):

```text
keys 10000 nodes 10000 (gen sequential 10000 first 1)
avl height 14 | max for 10000 nodes 18
rotations LL 0 RR 9986 LR 0 RL 0
avl levels 1 2 4 8 16 32 64 128 256 512 1024 2048 4096 1809
plain height 10000
search 10000 found | visits avl 14 plain 10000 | path 4096 6144 8192 9216 9728 9856 9920 9952 9984 9992 9996 9998 9999 10000
search 1 found | visits avl 13 plain 1 | path 4096 2048 1024 512 256 128 64 32 16 8 4 2 1
search 5000 found | visits avl 10 plain 5000 | path 4096 6144 5120 4608 4864 4992 5056 5024 5008 5000
average visits over 10000 keys | avl 12.36 | plain 5000.50
check inorder sorted: yes
check avl heights and balance: yes
check height <= max height: yes
```

- 보통의 트리는 높이 **10,000**. 가장 최근 주문(10,000번)을 찾으려면 노드를 10,000개 거친다.
- 같은 키를 같은 순서로 넣은 AVL 트리는 높이 **14**. 같은 주문을 노드 14개만 보고 찾는다.
- 모든 주문을 한 번씩 찾을 때 거치는 노드 수의 평균은 5,000.50개 대 12.36개다.
- 주문 10,000건을 넣는 동안 회전 9,986번이 일어났고, 정렬된 입력이라 모두 RR(왼쪽 회전 한 번)이었다. 회전 하나는 상수 시간이다.
- 참고(`random-input.txt`, 같은 키가 섞인 무작위 순서 3,000개): 이때는 보통의 트리도 높이 26으로 버틴다. 문제는 정렬되거나 거의 정렬된 입력이고,
  입력 순서를 고를 수 없을 때 AVL 같은 균형 트리가 높이를 보장한다.

같은 문제 모양: 시간순 ID(주문·로그·메시지)를 키로 한 순서 있는 색인, 증가하는 타임스탬프로 찾는 세션 표, 정렬된 파일을 읽어 만드는 사전.

## 3. 이진 탐색 트리와 높이

이진 탐색 트리는 어느 노드에서나 왼쪽 서브트리에는 더 작은 키, 오른쪽 서브트리에는 더 큰 키가 있는 트리다.
찾을 때는 루트에서 시작해 작으면 왼쪽, 크면 오른쪽으로 내려간다. 그래서 찾는 비용은 **트리의 높이**가 정한다.

- 키 `10 30 70`을 이 순서로 넣으면 셋이 한 줄로 서서 높이가 3이다.
- 같은 세 키라도 30을 위에 두면 높이는 2다. AVL 트리의 목표는 이런 낮은 모양을 계속 지키는 것이다.

## 4. 높이와 균형 인수

- **높이**: 그 노드에서 가장 먼 잎까지 내려가며 세는 노드 수. 잎은 1, 빈 자리는 0이다. `height(n) = 1 + max(height(left), height(right))`.
- **균형 인수** `bf(n) = height(left) − height(right)`. 양수면 왼쪽이, 음수면 오른쪽이 높다.
- 한 줄로 선 `10 → 30 → 70`에서 10은 왼쪽 0, 오른쪽 2라서 균형 인수 −2: 균형이 깨졌다.
- **AVL 규칙**: 모든 노드의 균형 인수가 −1, 0, +1 가운데 하나다.
- 키를 넣으면 높이가 바뀔 수 있는 노드는 넣은 자리에서 루트까지의 경로뿐이다. 그래서 재귀가 돌아오는 길에 그 경로만 아래에서부터 확인한다.

## 5. 회전

회전은 기운 노드를 한 칸 내리고, 높은 쪽 자식을 한 칸 올린다. 왼쪽 회전을 일반형으로 쓰면(A, B, C는 서브트리):

| | 위 | 아래 |
|---|---|---|
| 전 | x | x의 왼쪽 A, x의 오른쪽 y(그 아래 B, C) |
| 후 | y | y의 왼쪽 x(그 아래 A, B), y의 오른쪽 C |

- 키 순서 `A < x < B < y < C`는 그대로다. 위아래만 바뀐다(영상은 노드의 가로 위치를 키 순서로 고정해 이것을 보여 준다).
- 올라가는 y의 안쪽 서브트리 B는 내려가는 x가 넘겨받는다. 바뀌는 연결은 x의 오른쪽, y의 왼쪽, 부모가 가리키는 노드 세 개뿐이라 회전 하나는 O(1)이다.
- 회전 뒤에는 **내려간 노드부터** 높이를 다시 계산한다(내려간 노드가 올라간 노드의 자식이 되었기 때문).

어느 회전을 쓸지는 기운 노드 z와 그 높은 쪽 자식 c가 기운 방향으로 정한다:

| 경우 | 모양 | 처방 |
|---|---|---|
| LL | z도 c도 왼쪽으로 곧게 | z에서 오른쪽 회전 1번 |
| RR | z도 c도 오른쪽으로 곧게 | z에서 왼쪽 회전 1번 |
| LR | z는 왼쪽, c는 오른쪽으로 꺾임 | c에서 왼쪽 회전으로 곧게 편 뒤 z에서 오른쪽 회전 |
| RL | z는 오른쪽, c는 왼쪽으로 꺾임 | c에서 오른쪽 회전으로 곧게 편 뒤 z에서 왼쪽 회전 |

## 6. 예제 따라가기

키 `10 30 70 60 40 50 20`을 차례로 넣는다(예시 값). 네 경우가 한 번씩 생기도록 고른 순서다.
`python3 avl_tree.py input.txt`의 실제 출력(C++17도 바이트 단위로 같다):

```text
keys 7 nodes 7 (keys)
step 1 insert 10 | path - | balanced | height 1
step 2 insert 30 | path 10 | balanced | height 2
step 3 insert 70 | path 10 30 | unbalanced 10 bf -2 | RR left(10) | height 2
step 4 insert 60 | path 30 70 | balanced | height 3
step 5 insert 40 | path 30 70 60 | unbalanced 70 bf +2 | LL right(70) | height 3
step 6 insert 50 | path 30 60 40 | unbalanced 30 bf -2 | RL right(60) left(30) | height 3
step 7 insert 20 | path 40 30 10 | unbalanced 30 bf +2 | LR left(10) right(30) | height 3
preorder 40 20 10 30 60 50 70
inorder 10 20 30 40 50 60 70
avl height 3 | max for 7 nodes 4
rotations LL 1 RR 1 LR 1 RL 1
avl levels 1 2 4
plain height 6
search 50 found | visits avl 3 plain 6 | path 40 60 50
search 35 missing | visits avl 3 plain 5 | path 40 20 30
average visits over 7 keys | avl 2.43 | plain 3.43
check inorder sorted: yes
check avl heights and balance: yes
check height <= max height: yes
```

| 넣는 키 | 무슨 일이 일어나나 |
|---|---|
| 10, 30 | 균형. 10의 균형 인수 −1 |
| 70 | 10이 −2, 오른쪽으로 곧게 기운 **RR** → 10에서 왼쪽 회전, 30이 루트 |
| 60 | 70의 왼쪽에 붙음. 균형 |
| 40 | 70이 +2, 왼쪽으로 곧게 기운 **LL** → 70에서 오른쪽 회전, 60이 올라감 |
| 50 | 40의 오른쪽에 붙음. 경로 40(−1) · 60(+1) · 30(−2), 꺾인 **RL** → 60에서 오른쪽, 30에서 왼쪽, 40이 루트 |
| 20 | 10의 오른쪽에 붙음. 30이 +2, 자식 10이 −1인 **LR** → 10에서 왼쪽, 30에서 오른쪽, 20이 올라감 |

결과는 높이 3인 꽉 찬 트리(전위 순회 `40 20 10 30 60 50 70`)다. 같은 키를 같은 순서로 보통의 트리에 넣으면 높이 6이고,
50을 찾을 때 AVL 트리는 노드 3개(40 → 60 → 50), 보통의 트리는 6개를 거친다.

## 7. 왜 O(log n)인가

높이 h인 AVL 트리가 가질 수 있는 가장 적은 노드 수 N(h)는 한쪽 서브트리가 높이 h − 1, 다른 쪽이 h − 2일 때다:
N(h) = N(h − 1) + N(h − 2) + 1, N(0) = 0, N(1) = 1. 높이 1부터 1 2 4 7 12 20 33 …(피보나치 수 − 1)으로 거의 일정한 비율(약 1.6배)로 커진다.
노드 수가 높이에 대해 지수적으로 늘어나므로, 거꾸로 높이는 노드 수의 로그에 비례한다(대략 1.44 log₂ n 이하).

- 노드 10,000개인 AVL 트리는 아무리 기울어도 높이 **18**을 넘지 못한다(N(18) = 6,764 ≤ 10,000 < N(19) = 10,945). 주문 데이터의 실제 높이는 14였다.
- 넣기: 경로를 한 번 내려갔다 올라오며(O(log n)) 높이와 균형 인수를 고친다. 넣기 한 번에 고쳐야 하는 노드는 많아야 하나이고,
  회전은 거기서 많아야 두 번이다(고친 서브트리의 높이가 넣기 전과 같아지기 때문). 그래서 넣기도 O(log n).
- 메모리: 노드마다 높이(작은 정수) 하나를 더 저장한다.

## 8. 코드

`examples/avl_tree.py`의 회전, 경우 판단(출력용), rebalance, 넣기(그대로 옮김):

```python
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
```

`insert()`는 재귀로 내려가 빈 자리에 새 노드를 만들고, 돌아오는 길에 노드마다 `rebalance()`를 부른다. `case_of()`는 실행 출력에
경우 이름을 적기 위한 보조 함수이고, 균형을 고치는 일은 `rebalance()`만 한다. C++17(`examples/avl_tree.cpp`)의 같은 함수:

```cpp
Ptr rebalance(Ptr n) {
    update(n);
    if (bf(n) > 1) {
        if (bf(n->left) < 0) n->left = rotate_left(std::move(n->left));
        return rotate_right(std::move(n));
    }
    if (bf(n) < -1) {
        if (bf(n->right) > 0) n->right = rotate_right(std::move(n->right));
        return rotate_left(std::move(n));
    }
    return n;
}
```

## 9. 흔한 실수

- **회전 뒤 높이를 다시 계산하지 않기.** 저장된 높이가 틀리면 다음 넣기의 균형 인수가 틀려 고쳐야 할 곳을 놓친다.
  키 1~7을 차례로 넣으며 높이를 고치지 않는 왼쪽 회전을 쓰면 결과 트리가 AVL 규칙을 어긴다(`test_source.py`가 확인).
- **높이 갱신 순서를 거꾸로 하기.** 내려간 노드(새 자식)를 먼저, 올라간 노드(새 부모)를 나중에 계산해야 한다.
- **꺾인 모양에 회전 한 번만 하기.** 30, 10, 20처럼 LR 모양(30이 +2, 10이 −1)에서 30에서 오른쪽으로 한 번만 돌리면 10이 루트가 되고 균형 인수가 −2로 여전히 깨져 있다.
  먼저 10에서 왼쪽으로 돌려 곧게 편 뒤 30에서 오른쪽으로 돌려야 20이 루트가 된다.
- **루트만 확인하기.** 균형이 깨지는 곳은 경로 중간일 수 있다(예제에서 40을 넣을 때의 70). 경로를 아래에서부터 모두 확인한다.

## 10. 연습 문제

입력 `examples/practice.txt`: `insert 55 35 65 25 15 45 25`, 다 넣은 뒤 45와 50을 찾는다.

1. 회전이 일어나는 키는 몇 번째 무엇이고, 어떤 경우이며 어디서 돌리는가?
2. 다 넣은 뒤 트리를 전위 순회로 적어라.
3. 마지막 25는 어떻게 되는가?
4. 같은 키를 같은 순서로 보통의 이진 탐색 트리에 넣으면 높이는? AVL 트리는?

답(`python3 avl_tree.py practice.txt`의 실제 출력에서):

- 1번: 5번째 키 15에서 LL(35의 균형 인수 +2, 35에서 오른쪽 회전), 6번째 키 45에서 LR(55의 균형 인수 +2, 25에서 왼쪽 → 55에서 오른쪽)
- 2번: 전위 순회 35 25 15 55 45 65
- 3번: 25는 이미 있는 키라 무시된다(노드 6개)
- 4번: 보통의 트리 높이 4, AVL 트리 높이 3

## 11. 한계와 선택

- **삭제**도 같은 회전으로 균형을 되찾지만, 삭제는 서브트리 높이를 줄이므로 루트까지 올라가며 여러 번 돌 수 있다(많아야 경로 길이만큼, O(log n)). 이 예제는 넣기와 찾기만 구현했다.
- **AVL 대 레드블랙 트리**: AVL은 균형 조건이 엄격해 높이가 더 낮고 찾기가 많은 곳에 잘 맞는다. 넣고 지우기가 아주 잦으면
  조건이 느슨해 회전이 적은 레드블랙 트리도 많이 쓴다(널리 쓰이는 C++ `std::map`, Java `TreeMap` 구현이 레드블랙 트리다).
- **해시 테이블 대 균형 트리**: 키 순서가 필요 없고 같은 키만 찾는다면 해시 테이블이 더 단순할 수 있다.
  키 순서대로 읽기(중위 순회), 범위 찾기, 가장 가까운 키 찾기가 필요할 때 균형 트리를 고른다.

## 실행 (worktree 루트에서)

```sh
python3 films/avl-tree-20261107/examples/run_examples.py   # Python·C++17 실행, 결과 저장, 대조
python3 films/avl-tree-20261107/examples/avl_tree.py films/avl-tree-20261107/examples/input.txt
python3 films/avl-tree-20261107/test_source.py             # 테스트 진입점
```
