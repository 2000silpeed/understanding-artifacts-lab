# 세그먼트 트리 companion

원본 authored practice HTML/JS와 Python/C++ 예제, 입력·정답 fixture를 보존한 learner-source입니다. `practice/index.html`은 원본 실습 페이지이며, 공개 `index.html`에는 공유 한글 글꼴·모바일 overflow 래퍼·다운로드 링크만 추가했습니다. 영상 embed는 포함하지 않습니다.

## 실행

```sh
python3 examples/segment_tree.py < examples/input.txt
c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic examples/segment_tree.cpp -o /tmp/segment_tree
/tmp/segment_tree < examples/input.txt
node practice/check_core.cjs
```
