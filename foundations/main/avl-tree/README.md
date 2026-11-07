# AVL 삽입 실습

`index.html`은 인터넷 없이도 열 수 있습니다. 글꼴이 제한되는 브라우저에서는 이 폴더에서 `python3 -m http.server 8000`을 실행하고 `http://localhost:8000/`을 여세요.

1. 이번에 넣을 키와 회전 전 그림을 보세요.
2. 균형, LL, LR, RR, RL 중 하나를 고르면 이유와 회전 후 그림이 나타납니다.
3. 다음 버튼으로 다음 삽입을 확인하세요. 이전과 처음으로 버튼으로 다시 풀 수 있습니다.

## 코드 실행

```sh
python3 canonical/examples/avl_tree.py canonical/examples/input.txt
python3 canonical/examples/avl_tree.py canonical/examples/practice.txt
c++ -std=c++17 -O2 canonical/examples/avl_tree.cpp -o avl_tree
./avl_tree canonical/examples/input.txt
```

`canonical/lesson.md`, 입력 파일, Python/C++ 코드는 강의 원본과 동일합니다. `lesson.html`은 원본 노트를 HTML로 표시한 문서입니다. 실습은 삽입과 탐색을 다루며 삭제 구현이나 실제 서비스 성능을 보증하지 않습니다.
