# 스택 수업 source package

## 학습 목표

- 스택과 LIFO를 쉬운 말로 정의하고, push, pop, top을 구분해요.
- `[10, 20, 30]`을 차례로 넣은 뒤 top은 30, pop 뒤 상태는 `[10, 20]`, 다음 pop 결과는 20임을 계산해요.
- 빈 스택의 pop/top을 underflow로 다루고, 첫 push와 마지막 pop 경계를 확인해요.
- Python list와 C++17 vector의 마지막 원소 조작을 실제 코드로 비교해요.
- top의 읽기와 논리적인 끝 pop은 O(1)이지만, Python list의 내부 축소/재할당은 한 번에 O(n)일 수 있음을 구별해요. Python 끝 append/pop의 amortized O(1), C++17 vector<int>::pop_back의 O(1), dynamic-array push의 worst-case O(n)을 함께 비교해요.

## 범위와 한계

이 수업의 구현은 동적 배열 기반 스택의 핵심 연산만 다뤄요. 동시성, 디스크 저장, 사용자 정의 예외 타입, 메모리 할당기의 내부 정책은 범위 밖이에요. `canonical.py`와 `canonical.cpp`가 직접 실행해 같은 stdout과 trace를 계산하고, 영상 장면은 그 trace의 상태만 그려요.

## 실행 계약

```bash
python3 canonical.py
python3 canonical.py --trace
g++ -std=c++17 -Wall -Wextra -pedantic canonical.cpp -o /tmp/lesson-2026-10-08-ds-canonical
/tmp/lesson-2026-10-08-ds-canonical
/tmp/lesson-2026-10-08-ds-canonical --trace
node source-test.mjs
```

stdout 계약은 `expected.txt`와 같아야 해요. 빈 스택에서 `pop`과 `top`은 `underflow`를 발생시키고, `trace.json`은 실제 메서드 호출 뒤의 상태를 보존해요.

## 핵심 원리

스택은 입구를 꼭대기 하나로 제한해 가장 최근 값을 먼저 처리해요. 그래서 되돌리기, 괄호 검사, 호출 기록처럼 최근 작업을 먼저 되돌리는 흐름에 잘 맞아요. 먼저 온 작업부터 처리해야 하는 흐름은 큐가 더 자연스러워요.

top 메서드의 읽기와 논리적인 끝 원소 제거는 O(1)이에요. Python list의 끝 append/pop은 여러 호출 전체로 보면 amortized O(1)이지만, 끝 pop이 내부 저장 공간 축소/재할당을 일으키면 구현 수준의 한 번 비용은 worst-case O(n)일 수 있어요. 반면 C++17 vector<int>::pop_back은 int 원소 하나를 끝에서 제거하고 capacity를 줄이지 않으므로 O(1)이에요. 동적 배열 push는 공간이 남으면 O(1), resize 순간에는 O(n), 전체로는 amortized O(1)로 분석해요. amortized 분석은 모든 개별 호출이 O(1)이라는 뜻이 아니고, 전체 연산 묶음에 비용을 분산한다는 뜻이에요.

## 검증 경계

`source-test.mjs`는 실제 renderer의 `parseScript`를 import하고, 실제 scene module을 strict proxy로 실행해 unsupported API, 비유한 좌표, 잘못된 cue/marker, caption-safe y 범위를 검사해요. 또한 Python/C++17 실행, stdout, trace, HTML offline 조건, SVG 크기, artifact SHA-256을 확인해요. TTS, render, browser, publish, human listening, learning effectiveness는 실행하지 않아요.
