# 실행 예제 — 미니배치로 작은 언어 모델 학습하기

영상의 모든 숫자는 이 폴더의 실행 결과에서 나온다. 입력은 `data/corpus.txt`(문장 8개)와 `data/config.txt`(학습률 1.0, 시드 7,
배치 4 등). 세 구현(Python · C++17 · 실습 페이지 JS)이 같은 셔플(32비트 LCG)과 같은 계산 순서를 써서 같은 숫자를 낸다.

```sh
cd films/minibatch-gradient-20261023/examples
python3 minibatch.py data/ --report                          # 읽기 쉬운 추적 (out/python-report.txt)
python3 minibatch.py data/ > out/python-result.json           # 영상·자막이 읽는 JSON
c++ -std=c++17 -O2 -Wall -Wextra -pedantic -o out/minibatch-cpp minibatch.cpp
./out/minibatch-cpp data/ > out/cpp-result.json               # 같은 숫자 (차이 ≤ 1e-12, 실제 최대 4.4e-16)
node ../lab/check.cjs                                         # 실습 엔진도 같은 숫자인지
```

핵심 한 걸음 (`minibatch.py`의 `minibatch_step`, 영상 코드 장면에 그대로 나온다):

```python
def minibatch_step(W, batch, lr):
    G = zeros(len(W))
    for prev, nxt in batch:
        p = softmax(W[prev])
        for j in range(len(p)):
            G[prev][j] += p[j] - (j == nxt)
    mean = 1.0 / len(batch)
    return [[w - lr * (g * mean) for w, g in zip(wr, gr)]
            for wr, gr in zip(W, G)]
```

바꿔 볼 것: `config.txt`의 `learning_rate`(예: 0.3, 3.0), `walkthrough_batch`, `seed`, 또는 `corpus.txt`에 문장 추가.
브라우저에서는 `../lab/index.html`을 열면 같은 계산을 표와 곡선으로 볼 수 있다(외부 네트워크 없음).
`out/minibatch-cpp`는 이 Mac(arm64)에서 만든 실행 파일이라 다른 OS에서는 위 명령으로 다시 빌드한다.
