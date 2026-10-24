스파스 테이블 · 실습 코드

압축을 푼 폴더에서 다음 명령을 실행하세요.
Python 3:
  python3 examples/sparse_table.py examples/input.txt
  python3 examples/sparse_table.py examples/practice.txt
C++17:
  c++ -std=c++17 -O2 examples/sparse_table.cpp -o sparse_table
  ./sparse_table examples/input.txt

웹 실습은 python3 -m http.server 8000 으로 폴더를 연 뒤
브라우저의 http://localhost:8000/ 에서 보세요.
입력 배열은 정적이고, 인덱스는 0부터, 질의 양 끝을 포함합니다.
전체 설명은 lesson.md, 예제 계산 기록은 trace.json에 있습니다.
영상·오디오·개인 파일은 포함하지 않습니다.
