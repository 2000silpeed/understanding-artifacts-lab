# 수업 노트 — 크루스칼: 사이클을 피하며 최소 신장 트리 만들기

영상 `kruskal-mst-20261024`와 같은 예제를 직접 돌려 보는 노트. 아래 출력 블록과 연습 문제 정답은 `test_source.py`가
실제 실행 결과(`examples/results/`, `examples/brute_force.py`)와 글자 그대로 대조한다.

## 1. 문제

마을 6곳(A–F)을 케이블로 잇는다. 놓을 수 있는 자리는 9곳이고, 숫자는 그 자리의 비용이다(예시 값, `examples/graph.txt`).
모든 마을이 **이어지기만** 하면 될 때 가장 싸게 잇는 방법은?

- **신장 트리**: 모든 정점을 잇고 사이클이 없는 간선 묶음. 정점이 n개면 간선은 언제나 n − 1개(여기서는 5개).
- **최소 신장 트리**: 신장 트리 중 비용 합이 가장 작은 것. 이 그래프의 신장 트리는 55가지, 비용 합은 19–35.

## 2. 크루스칼

1. 간선을 비용 순서로 줄 세운다(같은 비용은 입력 순서).
2. 앞에서부터 하나씩 본다. 두 끝이 **다른 덩어리**면 고르고(두 덩어리가 합쳐진다), **같은 덩어리**면 버린다(이으면 사이클).
3. 간선을 n − 1개 고르면 멈춘다.

실제 출력 (`python3 examples/kruskal.py examples/graph.txt`, C++17 `./kruskal examples/graph.txt`도 같다):

```text
sorted: E-F:1 B-E:2 B-F:3 A-D:4 C-F:5 B-C:6 D-E:7 A-B:8 A-E:9
step 1: E-F w=1 find(E)=E find(F)=F take total=1
step 2: B-E w=2 find(B)=B find(E)=E take total=3
step 3: B-F w=3 find(B)=E find(F)=E skip cycle
step 4: A-D w=4 find(A)=A find(D)=D take total=7
step 5: C-F w=5 find(C)=C find(F)=E take total=12
step 6: B-C w=6 find(B)=E find(C)=E skip cycle
step 7: D-E w=7 find(D)=A find(E)=E take total=19
mst: E-F B-E A-D C-F D-E
total: 19
edges: 5/5 checked: 7/9
connected: yes
```

읽는 법: `find(x)`는 x가 속한 덩어리의 대표. 두 대표가 같으면 `skip cycle`, 다르면 `take`. 비용 8, 9는 보지 않고 끝났다(`checked: 7/9`).

## 3. "같은 덩어리인가?" — 유니온 파인드

- 정점마다 `parent`(대표 쪽을 가리키는 화살표)를 둔다. 처음엔 모두 자기 자신.
- `find(v)`: 화살표를 끝까지 따라가 대표를 찾고, 지나온 정점이 대표를 바로 가리키게 고친다(경로 압축).
- `union(a, b)`: 두 대표가 같으면 거절(False). 다르면 **작은 덩어리의 대표를 큰 덩어리의 대표 아래에** 붙인다.
- 예제의 비용 7: `find(D) = A`, `find(E) = E` → 다르다. A의 덩어리(A, D: 2개)가 E의 덩어리(B, C, E, F: 4개)보다 작아 A가 E 아래로 붙는다.

## 4. 흔한 실수: "두 끝을 이미 방문했으면 버린다"

방문 여부는 "같은 덩어리인가"가 아니다. 이 그래프에서 비용 7(D-E)은 두 끝 모두 방문했지만 서로 다른 덩어리를 잇는 간선이다.

```text
naive rule: skip an edge when both ends are already visited
step 1: E-F w=1 take
step 2: B-E w=2 take
step 3: B-F w=3 skip both-visited
step 4: A-D w=4 take
step 5: C-F w=5 take
step 6: B-C w=6 skip both-visited
step 7: D-E w=7 skip both-visited
step 8: A-B w=8 skip both-visited
step 9: A-E w=9 skip both-visited
edges: 4/5 total: 12 components: 2
```

결과는 간선 4개, 비용 12, 덩어리 2개 — 모든 마을이 이어지지 않는다.

## 5. 왜 최소가 되는가

간선 (u, v)를 고르는 순간, u가 속한 덩어리 밖으로 나가는 간선 중 이 간선이 가장 싸다(더 싼 간선은 이미 다 살펴봤고, 그중 덩어리 밖으로
나가던 것은 그때 골라져 덩어리를 키웠다). **덩어리 밖으로 나가는 가장 싼 간선은 언제나 어떤 최소 신장 트리에 들어간다**(경계 성질).
그래서 고를 때마다 안전하다. 예제의 비용 7 순간: 덩어리 {A, D} 밖으로 나가는 간선은 7·8·9, 가장 싼 것이 7.
`examples/brute_force.py`로 55가지를 모두 따져 봐도 최소는 19 하나뿐이다.

## 6. 시간

간선이 m개면 정렬에 m log m 정도. 유니온 파인드는 경로 압축 + 크기 기준 합치기로 한 번에 상각 α(n)(사실상 상수)라 전체 시간은 정렬이 정한다.
(간선이 이미 정렬되어 있거나 비용이 작은 정수라 계수 정렬을 쓸 수 있으면 그 부분이 줄어든다.)

## 7. 직접 실행

```sh
cd films/kruskal-mst-20261024/examples
python3 kruskal.py graph.txt            # 위 출력
python3 kruskal.py graph.txt --naive    # 흔한 실수
python3 brute_force.py graph.txt        # 전수 조사 + 프림으로 확인
c++ -std=c++17 -O2 -o /tmp/kruskal kruskal.cpp && /tmp/kruskal graph.txt
python3 run_examples.py                 # 두 언어 실행·비교·무작위 300개 교차 검사, results/ 와 영수증 갱신
```

입력 형식: 첫 줄에 정점 이름, 그다음 줄마다 `u v 비용`. `#` 뒤는 주석.

## 8. 연습 문제 (정답은 `test_source.py`가 다시 계산)

1. `examples/tie.txt`(비용 2가 세 개)에서 최소 신장 트리의 비용 합은? 최소 신장 트리는 몇 개인가?
2. `examples/disconnected.txt`는 처음부터 두 섬이다. 크루스칼은 무엇을 돌려주는가?
3. `examples/graph.txt`에서 방문 규칙이 처음으로 크루스칼과 다른 판단을 내리는 간선은?

<details><summary>정답</summary>

1. 비용 합 5. 최소 신장 트리는 3개(같은 비용 세 간선 중 어느 둘을 골라도 된다). 크루스칼은 입력 순서대로 R-S, P-Q, Q-R을 고른다.
2. 섬마다 하나씩 신장 숲: B-C, A-C, D-E, 비용 합 7, `connected: no (components 2)`.
3. D-E(비용 7). 크루스칼은 고르고, 방문 규칙은 버린다.

</details>
