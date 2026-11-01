훈련 손실과 검증 손실 · 실습 소스

이 폴더는 설치·로그인·네트워크 없이 읽고 실행하는 companion입니다.

웹 실습
  python3 -m http.server 8000
  브라우저에서 http://127.0.0.1:8000/ 열기
  (index.html을 file://로 열어도 화면은 보이지만, 로컬 HTTP가 다운로드·폰트 확인에 더 안전합니다.)

실험 환경
  Python 3.11 이상
  numpy
  CPU만 사용하며 GPU와 네트워크는 필요하지 않습니다.
  저장된 results는 이 강의의 한 번 실행 결과이며, 임의로 다시 실행하면 결과 파일이 달라질 수 있습니다.

실행 예시 (복사본에서 실행)
  cp -R examples /tmp/train-validation-loss-examples
  cd /tmp/train-validation-loss-examples
  python3 -m pip install numpy   # 이미 설치되어 있으면 생략
  python3 -B src/corpus.py fixtures/grammar.json fixtures
  python3 -B src/run_experiment.py fixtures results
  python3 -B src/make_table.py

원본 보존
  canonical/ 아래는 Claude가 작성한 source snapshot을 보존한 영역입니다.
  source.zip에는 canonical/ 전체와 README.txt를 deterministic ZIP으로 담았습니다.
  ZIP을 받은 뒤에는 압축을 풀고 `cd canonical`한 다음 아래의 src/fixtures/results 명령을 실행하세요.
  lesson.md는 같은 수업 노트를 바로 읽을 수 있게 복사한 파일입니다.

주의
  이 페이지는 results/run-small.json과 results/run-large.json의 실제 기록을 읽어 표시합니다.
  이 companion은 실험을 다시 실행하거나 결과 값을 수정하지 않습니다.
  영상·오디오·로그인 정보·외부 CDN은 포함하지 않습니다.
