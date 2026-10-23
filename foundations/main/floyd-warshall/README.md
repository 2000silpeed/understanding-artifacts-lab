# 플로이드–워셜: 모든 출발점과 도착점 사이의 최단 경로

와이스튜디오 · AI 기본기 연구실 알고리즘 편. **상태: 소스 저작 완료(SOURCE_AUTHORED_NOT_INDEPENDENT)** — 유료 음성·음악 입력 전, 최종 영상 아님.
상태 영수증: `qa/author-result.json` (파일 해시, 실행 명령·exit, 남은 단계).

## 무엇이 어디에

| 경로 | 내용 |
|---|---|
| `scenario.md` | 기획: 시청자, 한 문장, 예제 선택 이유, 장면표, 색·움직임 결정 |
| `research.md` | 실제로 본 출처와 범위(Wikipedia, prompt-motion.com, 승인된 배열 영상) |
| `script.py` | 대본 43줄(발화 = TTS 텍스트) + 자막 `SUB` + `reading()` + 표 변경과 대사 연결 `NARRATED` |
| `tts-lines.json` | parent가 TTS에 보낼 줄 목록(`python3 script.py` 출력, 1,289자) |
| `examples/floyd_warshall.py` | Python 예제 (표·경유지별 변경·경로·실수 비교·음수 사이클, `--json`) |
| `examples/floyd_warshall.cpp` | C++17 예제, Python과 글자 하나까지 같은 출력 |
| `examples/graph.txt`, `examples/negative_cycle.txt` | 실행 입력(영상 속 지도, 음수 사이클 예) |
| `examples/run_examples.py` | 세 구현을 실제 실행하고 `examples/results/`에 보존 + 영수증 |
| `examples/results/` | `py-*.txt`, `cpp-*.txt`, `py-*.json`, `js-graph.json`, `js-exercises.json`, `run-receipt.json` |
| `trace.json`, `trace-negative.json`, `screen-excerpt.json` | 영상이 읽는 유일한 숫자 출처(= Python 실행 결과) |
| `practice/index.html` | 실습: 한 칸씩 비교, 경유지 단위 진행, 경로 보기, 실수 토글, 그래프 직접 입력, 연습 문제 6개 |
| `practice/fw.js`, `practice/exercises.js` | 실습 계산 모듈(Python과 같은 JSON) / 연습 문제(정답은 다시 계산해 확인) |
| `practice/check.cjs`, `practice/smoke.cjs` | Node 확인 / headless Chrome 실습 확인 |
| `plan.py` | 제공자 글자 정렬 → `shots.json`(장면·샷·말 단위 큐). `--check`, `--preview` |
| `film.js` | 영상(16:9, Canvas). 지도+표 무대, 13장면 |
| `film-tokens.json`, `check_palette.py` | 영상 전용 추가 색(공유 tokens `paper` 위) + 대비 검사 |
| `subtitles.py` | 실제 정렬 시각으로 한글 자막 SRT/VTT (추정 시각은 거부) |
| `INPUTS.md` | 외부 공급 입력 형식과 다음 실행 명령 |
| `test_source.py` | 소스 테스트 24개 |
| `qa/preview/` | **PREVIEW(추정 타이밍, 무음)**: 스틸 23장·시트, 미리보기 shots/shotlist/shotlint, 미리보기 자막, 실습 스크린샷 |
| `qa/authoring/` | 예제 그래프 탐색 스크립트, 발화 속도 실측 스크립트·출력 |

## 실행 (worktree 루트에서)

```sh
python3 films/floyd-warshall-20261023/examples/run_examples.py         # 예제 실행 + 영수증 (exit 0)
.venv/bin/python films/floyd-warshall-20261023/test_source.py          # 소스 테스트
node films/floyd-warshall-20261023/practice/smoke.cjs                   # 실습 HTML 브라우저 확인
open films/floyd-warshall-20261023/practice/index.html                  # 실습 직접 열기 (서버 불필요)
.venv/bin/python films/floyd-warshall-20261023/plan.py --check         # 입력 상태 (지금은 3 = 입력 없음)
```

다음 단계(유료 음성·음악 입력 이후)는 `INPUTS.md` 끝의 명령 순서를 따른다.
