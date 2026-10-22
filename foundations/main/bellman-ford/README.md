# 벨만–포드 companion

`index.html`은 모바일/데스크톱에서 한 칸씩 완화하는 실습 페이지입니다. 원본 실습 엔진과 수학 흐름은 source-v2를 그대로 사용하고, 배포용 글꼴·모바일 래퍼·학습자 다운로드 링크만 덧붙였습니다. 영상 embed는 포함하지 않습니다.

## 독립 실행

```sh
python3 examples/bellman_ford.py examples/graph.txt
python3 examples/bellman_ford.py examples/graph-negative-cycle.txt
c++ -std=c++17 -O2 -Wall -Wextra -pedantic -o /tmp/bellman_ford examples/bellman_ford.cpp
/tmp/bellman_ford examples/graph.txt
python3 examples/run_examples.py
```

`run_examples.py`는 정상 그래프와 음수 사이클 fixture 모두에 대해 Python/C++17 stdout parity를 검사합니다.
