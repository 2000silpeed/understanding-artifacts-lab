# 프림: 연결된 트리를 한 정점씩 넓혀 최소 신장 트리 만들기

AI 기본기 교육 · 알고리즘 신규 수업 (2026-11-04 저작). **상태: 소스 저작 완료(SOURCE_AUTHORED_NOT_INDEPENDENT)** —
독립 검수 전, 유료 음성·음악 없음, 임시 음성·프리뷰·렌더 없음, 학습 효과 미측정. 상태 영수증: `qa/author-result.json`
(파일별 sha256, 소스 전체 해시, 실행 명령·exit code, 다음 단계).

순서: **핵심 개념 요약 → 구체적인 사용 상황(정원 물탱크) → 본 강의 → 마무리**, 화면과 내레이션 모두.

## 무엇이 어디에

| 경로 | 내용 |
|---|---|
| `scenario.md` | 기획: 요청 순서의 구현, 자율 결정과 이유, 값의 단일 원천, 사실 주장과 근거, 남은 위험 |
| `direction.md` | 디자인·연출: 레시피, 색 의미(토큰 경로), 무대, 움직임=동사 표, 유일한 사치, 소리, 아직 안 만든 것 |
| `SCRIPT.md` | 대본 표: 장면·큐별 자막, TTS 읽기, 화면 동작, 추정 시작 시각 (`script.py --markdown` 생성) |
| `LESSON.md` | 수업 노트: 요약·사용 상황·알고리즘·실행 표·흔한 실수·컷 성질·시간·크루스칼 비교·연습 문제 3개 |
| `script.py` | 대본 원천(49줄: 큐, 자막, trace 사실 키, 화면) + 한글 읽기 변환 + 길이 추정 |
| `tts-lines.json` | TTS 요청 49줄(`python3 script.py` 출력, 2,031자, 추정 길이 포함) |
| `facts.py` | 대본의 사실 키 → `data/trace.json` 값 (관계도 assert) |
| `examples/prim.py`, `examples/prim.cpp` | Python 3 / C++17 예제(표준 라이브러리만). `--start`, `--naive`(흔한 실수), `--dense`(배열 O(n²)) |
| `examples/garden.txt`, `tie.txt`, `disconnected.txt` | 입력 fixture: 영상 속 정원 / 같은 비용(MST 4개) / 두 섬(연결 안 됨) |
| `examples/independent.py` | 독립 확인: 신장 트리 전수 조사 + 크루스칼(코드 공유 없음) |
| `examples/run_examples.py` | 두 언어 실제 실행·바이트 비교·전수 조사·무작위 300개 교차 검사 → `examples/results/`(stdout + `run-receipt.json`) |
| `examples/make_trace.py` | `data/trace.json`(대본·그림·영상이 쓰는 유일한 숫자 출처) 생성·`--check` |
| `make_figures.py` → `figures/` | trace에서 그린 SVG 스토리보드 13장 + `index.json`(그림 ↔ 큐). 영상 렌더 아님 |
| `tokens.local.json`, `data/layout.json` | 이 수업의 의미 색(공유 토큰 경로만) / 지도 좌표 |
| `tests/test_source.py` | 테스트 entrypoint (25개) |
| `author_receipt.py` → `qa/author-result.json` | 아래 명령을 모두 실행하고 영수증을 쓴다 |

## 실행 (worktree 루트에서, python3 ≥ 3.9 + C++17 컴파일러, 외부 패키지 없음)

```sh
python3 -B films/prim-mst-20261103/examples/run_examples.py        # 예제 실행 + 비교 + results/ (exit 0)
python3 -B films/prim-mst-20261103/examples/prim.py films/prim-mst-20261103/examples/garden.txt
python3 -B films/prim-mst-20261103/tests/test_source.py            # 소스 테스트
python3 -B films/prim-mst-20261103/author_receipt.py               # 전부 다시 실행하고 qa/author-result.json 갱신
```

값이 바뀌면 순서: `examples/run_examples.py` → `examples/make_trace.py` → `make_figures.py` → `script.py > tts-lines.json`, `script.py --markdown > SCRIPT.md` → `tests/test_source.py` → `author_receipt.py`.

## 다음 단계 (부모 단계, 이 단계에서는 하지 않음)

1. **독립 검수**: 영수증 해시 확인, `run_examples.py`·테스트 재실행, 대본·수업 노트의 개념 정확성, 읽기 표(`SCRIPT.md` TTS 열) 승인.
2. **내레이션 녹음**(기존 포함 예산 ElevenLabs): `tts-lines.json`의 `text`를 줄마다 한 파일 `voice/<scene>-<cue>.wav`로. `subtitle`은 보내지 않는다. 제공자 글자 정렬을 함께 저장(단어 시각의 원천).
3. **실측 타이밍**: 정렬로 줄·어절 시각 → `shots.json`(모든 장면 `rules.voiceScenes`) → `shotlint.py` → 자막 SRT.
4. **배경 음악**(Suno, 사용자 다운로드): 실측 길이에 맞춰 한 곡을 통째로, 덕킹 12 dB.
5. `film.js`(그래프 지도 도구 여부 결정 포함, `direction.md`) → 스틸 게이트(사람) → `sh pipeline/make.sh prim-mst-20261103 16x9` → `verify.py` → `shotlint --video` → `REVIEW.md` → 사람 청취·미감 승인 → 공개 승인.
