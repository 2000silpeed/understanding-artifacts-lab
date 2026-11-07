# 강한 연결 요소 — visual1 (실행 가능한 film + 최종 음성 입력 계약)

방향 그래프에서 서로 오갈 수 있는 정점 묶기. 한국어 AI 기본기 교육, 트랙 algorithms(공개 번호 13).
원본 source package(`films/strongly-connected-components-20261107/`, 대본·예제 독립 콘텐츠 검수 SOURCE_PASS)의 형제 폴더다.
원본의 기획·디자인·예제·학습 순서(핵심 요약 → 사용 상황 → 본 강의)를 그대로 두고, 그 direction을 구현한 `film.js`와
최종 음성의 실제 제공자 글자 시각을 읽는 plan / caption / audio 입력 계약을 더했다.

상태: **SOURCE_AUTHORED_NOT_INDEPENDENT** — 작성자 자체 검사만 했다. 입력(음성 94개·매니페스트·Mac Aside 곡)은 **PENDING**.
녹음·음악·렌더·스틸·업로드는 하지 않았다. 기록: `qa/author-result.json`.

## 흐름

```
script/lesson.json ─ lines.py ─▶ tts-lines.json (94줄, 읽기 적용)          ← 원본 그대로
                                     │  (외부) ElevenLabs eleven_v4 / Aria-KR, with-timestamps, atempo 1.06
                                     ▼
voice/*.wav + voice/manifest.json + audio-src/suno-bed.wav (Mac Aside Suno)  ← PENDING
                                     │  plan.py (제공자 글자 정렬, 추정 없음)
                                     ▼
shots.json (shots.source.json 내용 + 어절 시각) · subs/*.ko.srt · music/score.wav
                                     │  film.js (examples/output/screen-data.json = 실제 실행 값)
                                     ▼
pipeline/build.cjs → render.cjs → audio.py → verify.py
```

## 들어 있는 것

| 경로 | 내용 |
|---|---|
| `film.js` | 장면 13개(제목·요약·사용 상황·정의·단순한 방법·응축·1단계·이유·2단계·결과·코드·비용·정리), 16:9 + 9:16 |
| `plan.py` | 입력 검사(`--check`), 추정 프리뷰(`--preview`, stdout만), 최종 `shots.json`·자막·배경음 작성 |
| `lines.py` → `tts-lines.json` | 문장 단위 TTS 요청(텍스트=읽기, subtitle=원문) |
| `INPUTS.md` | 외부 입력 형식(음성·매니페스트·곡)과 다음 명령 |
| `shots.source.json` | 원본 `shots.json`과 바이트 단위로 같은 기획(샷 40개). `plan.py`는 여기서 내용을 읽고 시각만 다시 정한다 |
| `shots.json` | 지금은 원본 기획 그대로(입력 전). 최종은 `plan.py`가 덮어쓴다 |
| `examples/screen_data.py` → `examples/output/screen-data.json` | 화면용 실행 기록: 1·2단계 순회 사건, 도달 표, Tarjan index/low, 코드 12줄, 터미널 줄 — `scc.py`와 실제 출력에서만 |
| `smoke_film.cjs` | 브라우저 없는 draw-call 검사(입력 전 로드 거부 확인 포함). 결과 `qa/smoke-film.json` |
| `test_source.py` | 보존·줄·화면 데이터·계획·PENDING·계약 테스트 73항목 |
| `qa/write_author_result.py` → `qa/author-result.json` | 실제 명령을 다시 돌려 exit code·해시·상태를 기록 |
| 나머지(`script/`, `examples/` 원본 파일, `direction.md`, `scenario.md`) | 원본과 같음(`test_source.py`가 바이트 비교) |

## 원본 대비 바뀐 것 (경로·consumer binding)

| 변경 | 이유 |
|---|---|
| `shots.json` → `shots.source.json` 사본 추가(바이트 동일), `shots.json`은 최종 때 `plan.py`가 씀 | 최종 shots.json은 실제 음성 시각에서만 나온다. `check_lesson_sync.py`는 계속 `shots.json`을 읽고 내용(카피·move)은 바뀌지 않는다 |
| `film` id = 폴더 이름 `strongly-connected-components-20261107-visual1` (`plan.py`·`film.js`) | 빌드·렌더가 `films/<id>/`로 찾는다. `script/lesson.json`의 `film` 필드(원본 id)는 원문 보존을 위해 그대로 둔다 |
| `examples/run_all.sh`: usage 경로 주석, 7단계 `screen-data` 추가 | film.js 입력을 실행 때마다 실제 코드에서 다시 만든다 |
| 음악: 90 BPM 32마디 생성 루프 → 기존 Mac Aside Suno 연주곡(`audio-src/suno-bed.wav`) | 요청. 곡 박은 측정하지 않고, 원본의 2/3초(90/분) 격자는 화면 단위로만 남긴다 |
| 녹음 단위: 장면별 → 문장별 94개(`tts-lines.json`) | 제공자 글자 정렬을 문장마다 받아 샷을 어절에 맞춘다. 문장별 읽기를 이으면 `script/tts/*.txt`와 같다(테스트) |
| `qa/write_author_result.py` 다시 씀, 원본 기록은 `qa/inherited-original-author-result.json` | visual1의 실제 명령·상태를 기록 |

## 연출 결정 (direction.md §6을 이 폴더에서 정함)

- **고정폭 글꼴**: 공유 토큰에 mono 역할이 없고 공유 설정 수정·글꼴 내려받기가 금지라, 코드·터미널은 `text` 역할(Pretendard)로 쓰고 들여쓰기는 공백 폭으로 맞춘다(정렬 손해는 스틸에서 확인).
- **hull(묶음 테두리)**: `film.js` 안의 helper(`hullRect`·`drawHull`)로 구현했다. 공유 `engine/components`에 넣는 것은 이 작업 범위 밖이라 후보로만 남긴다.
- **장면 전환**: 하드 컷(GPU 전환 없음). 하드·와이프 컷 첫 프레임에 요소가 이미 보인다.
- **효과음**: direction §5대로 절차 합성(정점 방문·끝 번호 `tick`, 묶음 확정 `thump`, 화살표 뒤집기 `swish`, 네 묶음 완성 `hit` 한 번).
- **자막**: 화면에 굽지 않고 SRT 사이드카로 낸다(화면 카피와 겹치지 않게, 한 프레임 accent 하나 규칙).
- 9:16 정점 좌표는 direction 표 그대로이며, 간선이 정점을 지나지 않게 `주문→회원`, `결제→알림`만 휘었다.

## 알려진 한계

- 렌더·스틸·청취를 하지 않았다. 글자 폭은 smoke에서 추정값(한글 0.94em)으로만 검사했다.
- 공유 `pipeline/audio.py`는 `music/score.*`가 있으면 `audio-events.json`의 출처를 "ElevenLabs Music"으로 적는다(공유 코드, sunzi-trailer도 같음). 이 영화의 곡은 Mac Aside Suno 연주곡이다 — REVIEW에서 바로잡아 적을 것.
- Kosaraju 순회 시각 중 말하지 않는 'seen' 간선(인증→회원 등)은 화면에서 따로 강조하지 않는다.
