# tanh 은닉층 역전파 companion

`index.html`은 입력 2 → tanh 은닉 2 → 출력 1의 순전파·역전파와 학습 흐름을 조작하는 실습 페이지입니다. 원본 lab의 계산 블록과 숫자는 source-v2를 그대로 사용하고, 배포용 글꼴·모바일 래퍼·학습자 다운로드 링크만 덧붙였습니다. 영상 embed는 포함하지 않습니다.

## 독립 실행

```sh
python3 examples/tanh_backprop.py
c++ -std=c++17 -O2 -Wall -Wextra -pedantic -o /tmp/tanh_backprop examples/tanh_backprop.cpp
/tmp/tanh_backprop
```

Python/C++17 출력은 byte-for-byte로 비교할 수 있고, 첫 실행의 핵심 값은 `dL/dw = -0.290642...`, 한 걸음 뒤 `w = 0.645321...`, `loss = 0.0223149...`입니다.
