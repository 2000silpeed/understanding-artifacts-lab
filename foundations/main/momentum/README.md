# 모멘텀 실습 companion

1. `index.html`을 열어 먼저 세 걸음의 속도를 예측합니다.
2. β 비교 막대에서 실행 결과를 확인합니다.
3. `lesson.html`은 원본 `lesson.md`를 읽기 문서로 렌더링한 수업 노트입니다.
4. `downloads/momentum-code.zip`을 내려받으면 표준 라이브러리 Python과 C++17 예제를 실행할 수 있습니다.

실행 예:

```sh
python3 examples/python/momentum.py --fixtures examples/fixtures --out /tmp/momentum-python.json
c++ -std=c++17 -Wall -Wextra -pedantic examples/cpp/momentum.cpp -o /tmp/momentum
/tmp/momentum examples/fixtures > /tmp/momentum-cpp.json
```

데이터는 수업용으로 직접 만든 아파트 8채 예제이며 실제 거래 자료가 아닙니다.
