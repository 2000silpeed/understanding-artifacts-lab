# 큐 수업 source package

## 학습자와 prerequisites

- 파이썬에서 리스트와 숫자 값을 다뤄 본 초급 학습자를 대상으로 해요.
- 값이 순서를 가진 모음으로 표현될 수 있고, 함수 호출이 상태를 바꿀 수 있다는 정도를 전제로 해요.
- C++ 문법은 이 수업에서 필요한 `std::queue<int>` 선언과 메서드 호출을 코드로 함께 읽어요.
- 메모리의 실제 주소나 컨테이너의 내부 칸 배치는 prerequisite가 아니며, 이 수업에서 약속하지 않아요.

## 학습 목표

- 큐를 먼저 들어온 값이 먼저 나오는 자료구조로 정의하고 FIFO를 설명해요.
- enqueue는 뒤에 추가하고, front는 확인만 하며, dequeue는 앞에서 제거한다는 차이를 말해요.
- `[12, 35, 8]`에 47을 enqueue한 뒤 front가 12이고, dequeue 12 뒤 `[35, 8, 47]`이 되는 과정을 예측해요.
- 이어서 19를 enqueue하고 35를 dequeue하면 `[8, 47, 19]`임을 실제 Python/C++ 실행으로 확인해요.
- 빈 큐의 front/dequeue를 정상 숫자로 바꾸지 않고 empty guard로 처리해요.
- Python `collections.deque`와 C++17 `std::queue`의 논리 순서를 비교하고, `list.pop(0)`과 `deque.popleft`의 비용 차이를 설명해요.
- 화면의 가로 배치는 설명용이며, 큐의 논리 순서가 특정 물리 레이아웃을 보장하지 않는다는 점을 구분해요.

## 핵심 용어

- **큐(queue)**: 먼저 들어온 값을 먼저 처리하는 순서 구조예요.
- **FIFO**: First In, First Out. 먼저 들어온 값이 먼저 나간다는 규칙이에요.
- **enqueue**: 뒤(rear)에 값을 추가해요.
- **front**: 앞의 값을 읽고 상태는 바꾸지 않아요.
- **dequeue**: 앞의 값을 반환하고 제거해요.
- **empty guard**: 값이 없을 때 반환할 숫자를 꾸며내지 않고 빈 상태를 명시적으로 처리하는 경계예요.
- **논리 순서**: 앞에서 뒤로 어떤 값이 먼저 처리되는지에 대한 계약이에요. 컨테이너가 메모리에 실제로 일렬 배치된다는 주장과 달라요.

## 실행 예시

초기 큐는 `[12, 35, 8]`이에요. `enqueue(47)` 뒤에는 `[12, 35, 8, 47]`이고, `front()`는 12를 반환하지만 상태를 바꾸지 않아요. 이어서 `dequeue()`는 12를 반환하고 `[35, 8, 47]`을 남겨요.

연습에서는 이 상태에 `enqueue(19)`를 한 뒤 `dequeue()`를 실행해요. 35가 반환되고 최종 상태는 `[8, 47, 19]`이에요. 두 상태와 반환값은 `canonical.py`와 `canonical.cpp`의 실제 실행에서 생성돼요.

## 구현과 비용

Python 구현은 `collections.deque`의 `append`와 `popleft`를 사용해요. `deque.append`와 `deque.popleft`는 양 끝 작업을 위한 O(1) 연산으로 설명해요. 일반 Python 리스트의 `pop(0)`은 앞 원소 뒤의 값들을 이동시킬 수 있어서 O(n)이 될 수 있어요.

C++ 구현은 `std::queue<int>`의 `push`, `front`, `pop` 인터페이스를 사용해요. 표준 `std::queue`의 기본 컨테이너는 `std::deque`예요. 따라서 이 수업의 기본 설정에서 push/front/pop의 비용은 O(1)로 적어요. 다만 `std::queue`는 컨테이너 어댑터이므로 다른 적합한 컨테이너를 선택하면 비용 조건이 달라질 수 있어요. 이 수업은 특정 물리 메모리 배치나 주소를 약속하지 않아요.

## 범위와 한계

동시성, 블로킹 작업 큐, 우선순위 큐, 사용자 정의 allocator, 표준 라이브러리의 모든 대체 컨테이너는 범위 밖이에요. `std::queue`의 내부를 순회하는 대신, 논리적 front/pop 결과를 관찰해요. empty guard는 이 수업의 코드에서 `IndexError("empty")`와 `std::out_of_range("empty")`를 잡아 같은 의미로 표현해요.

## 실행 계약

```bash
python3 canonical.py
python3 canonical.py --trace
g++ -std=c++17 -Wall -Wextra -pedantic canonical.cpp -o /tmp/lesson-2026-10-10-ds-canonical
/tmp/lesson-2026-10-10-ds-canonical
/tmp/lesson-2026-10-10-ds-canonical --trace
node source-test.mjs
```

`expected.txt`는 두 실행의 표준 출력과 같아야 하고, `trace.json`은 실제 상태와 비용 계약을 보존해요. `source-test.mjs`는 현재 renderer parser와 실제 `Stage` 메서드의 cue/lifetime 경로를 사용해요. TTS, 렌더, 브라우저, 네트워크, 게시, 사람의 전체 듣기와 학습 효과 측정은 이 source package 검증 범위가 아니에요.

## transfer 질문

먼저 도착한 작업부터 처리해야 하는가요, 아니면 최근 작업부터 되돌려야 하는가요? 전자면 큐와 FIFO를, 후자면 스택과 LIFO를 선택해요. 답을 외우기보다 다음 입력에서 앞과 뒤 중 어느 쪽이 바뀌는지 설명해 보세요.


C++ std::queue::pop()의 반환형은 void예요. 먼저 front() 값을 저장하고 pop()으로 제거한 뒤 저장한 값을 반환해요.
