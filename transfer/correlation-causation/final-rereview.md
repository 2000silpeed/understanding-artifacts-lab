# 최종 재검토 — 상관관계 ≠ 인과관계 corrected 영상

## 판정

**상태: PASS — 현재 renamed corrected 원본과 KO 합성 MP4의 직접 프레임 재검토 완료.**

이 문서는 이전 `final-review.md`를 대체하지 않는다. 이전 보고서의 `PENDING` 상태/내용은 변경하지 않았고, 이번 결과는 새 corrected 최종 산출물에 대한 별도 재검토다.

`corrected-original.mp4`가 없는 것은 미완료 상태가 아니다. corrected 원본이 `video-original.mp4`로 rename된 현재 패키징을 기준으로 확인했다. 따라서 `corrected-original.mp4` 부재를 blocker 또는 `PENDING`으로 세지 않았다.

## 검토 범위와 직접 근거

- 검토 루트: `$LAB/transfer/correlation-causation`
- 직접 검토한 KO 영상: `video/video-ko.mp4`
- renamed corrected 원본: `video/video-original.mp4`
- master: `video/video-master.mp4`
- 영상 메타데이터: 1920×1080, H.264/AAC, 30 fps, 73.333333초, 2200 frames
- 최근 render provenance는 작업 컨텍스트에 기록된 `rootproc195… exited 0`을 참고했지만, 최종 판정은 process 상태가 아니라 실제 파일 hash·ffprobe·decoded frame·audit 결과에 근거했다.

### SHA-256

| artifact | SHA-256 |
|---|---|
| `video/video-ko.mp4` | `227b12db12caa7c0a098deab0f247d75e07e2e504733492d3c95328d37c04b79` |
| `video/video-original.mp4` (renamed corrected original) | `81a79bd24863b67196ecf9b7752db415d45a75dc93a71b660d820f5a9df67eb7` |
| `video/video-master.mp4` | `a5341c034b1475a5a2fbca120a6a74c74d67712fffed595cedcdfde5b39397e8` |

`caption-alignment.json`의 `original_video_sha256` 및 media bindings가 위 현재 파일 hash와 모두 일치한다. pre-correction baseline `$LAB/baseline-evidence/correlation-pre-correction-original.mp4`의 SHA-256은 `140c23bd08a491d4a6d0ddce9cc38f6d0fdc7b4d4982d62affada5a2b6cc2e5b`로 현재 renamed original과 다르다.

## 1. Canonical source / provenance

- `data-model.js` 실제 SHA-256: `5d5f26a605392c6bc1bc6991769d95f628bdb04d113b48ce81c45c326ed6d2d3`
- `scene-data-provenance.json`의 source SHA와 일치.
- provenance canonical counts: **aggregate 42 / group22 6 / intervention 7**.
- Node 실행 결과:
  - aggregate: `n=42`, `r=0.9672481779111594`
  - T=22°C group: `n=6`, `r=0.20809520526299863`
  - intervention: `n=7`, `r=-0.21468038799135705`
- `scenes.js`의 표시 배열도 aggregate 42, groupAggregate 42, group22 6, intervention 7개로 확인했다.
- `scenes.js` 주석 및 provenance에 따라 표시 좌표는 canonical educational `data-model.js`에서 계산된 값이며 임의로 발명한 값으로 취급하지 않았다.

좌표/레이아웃 확인:

- group 좌측 plot axes `(x=270..810, y=320..700)` 안에 canonical 42점 중심이 모두 위치.
- group 우측 plot axes `(x=1170..1710, y=320..700)` 안에 T=22°C canonical 6점 중심이 모두 위치.
- intervention axes `(x=420..1520, y=610..880)` 안에 7점 중심이 모두 위치.
- intervention y-axis label anchor `x=388`, axis `x=420`; full-resolution frame에서 label과 축/점의 겹침이나 잘림은 보이지 않음.

## 2. Caption / bundle CLI audit

두 CLI report는 요청대로 repository가 아닌 `/tmp`에만 생성했다.

- `audit_captions.py ... --report /tmp/correlation-causation-final-rereview-caption-audit.json`
  - exit `0`, `passed=true`
  - cue `20`, SRT/VTT/alignment `20`
  - 실제 timeline source word count: **158**; unique covered `158/158`
  - 중복 source-word assignment 없음
  - `max_cps=19.298`, `max_start_error=0`
  - SRT/VTT/KO alignment 텍스트 및 timing 일치
- `audit_bundle.py ... --report /tmp/correlation-causation-final-rereview-bundle-audit.json`
  - exit `0`, `passed=true`
  - 현재 `test-report.json` asset 존재 및 video/media metadata 검사 통과
  - H.264/yuv420p, audio stream, positive duration, MP4 faststart 검사 통과

`test-report.json`도 실제 존재하며 `passed=true`, 20 cues, 1920×1080, 73.333333초, errors `[]`를 기록한다.

## 3. 20개 cue midpoint decoded frame 직접 검토

현재 `video-ko.mp4`에서 각 cue의 `(start+end)/2`를 계산해 **20/20 PNG를 실제 추출**했다. 전체 contact sheet와 group/intervention full-resolution still을 vision으로 확인했다.

- contact sheet: `/tmp/correlation-causation-rereview-midpoints/contact-sheet.png`
- 개별 midpoint frames: `/tmp/correlation-causation-rereview-midpoints/cue-01...cue-20...png`
- full-resolution 집중 확인:
  - `/tmp/correlation-causation-rereview-midpoints/cue-11-full.png`
  - `/tmp/correlation-causation-rereview-midpoints/cue-13-full.png`

| cue | scene | midpoint (s) |
|---:|---|---:|
| 1 | hook | 2.550 |
| 2 | hook | 5.805 |
| 3 | pattern | 9.300 |
| 4 | pattern | 13.225 |
| 5 | dag | 17.147 |
| 6 | dag | 20.552 |
| 7 | missing | 24.627 |
| 8 | missing | 27.377 |
| 9 | missing | 29.967 |
| 10 | group | 33.207 |
| 11 | group | 36.417 |
| 12 | intervention | 41.050 |
| 13 | intervention | 43.935 |
| 14 | intervention | 46.445 |
| 15 | questions | 50.933 |
| 16 | questions | 55.963 |
| 17 | questions | 59.668 |
| 18 | outro | 62.677 |
| 19 | outro | 64.942 |
| 20 | outro | 68.612 |

직접 보이는 결과:

- 20개 frame 모두 decode되었고 nonblank이며 해당 scene/cue 의미와 시각적으로 대응한다.
- 제목, 상단 panel label, DAG label, 질문 카드의 눈에 띄는 겹침 또는 화면 밖 잘림을 찾지 못했다.
- cue 3의 두 축 label과 제목/부제는 분리되어 보이며 y-axis label overlap이 없다.
- cue 11 full-resolution에서 좌측은 상승하는 canonical 42-point cloud, 우측은 T=22°C의 6개 yellow point cluster가 보인다. 두 panel title box, plot axes, r label, synthetic-data note 및 KO subtitle 사이에 겹침/잘림이 없다.
- cue 12–14의 intervention sequence에서 chart가 보이며, cue 13 full-resolution에 **7개 teal point**가 모두 표시된다. point centers는 axes 안에 있고, 보이는 marker의 clipping은 없으며 y-axis label은 축/점과 겹치지 않는다.
- KO burned-in subtitle은 cue midpoint에서 화면 하단의 별도 caption-safe 영역에 있고 chart/title을 가리지 않는다.

## 4. 한국어 scope 및 인간 검증 한계

- 이번 작업에서 Source Narration, KO full-text translation, SRT/VTT/alignment 본문은 수정하지 않았다. 새로 만든 파일은 이 `final-rereview.md`뿐이다.
- KO 검토 범위는 현재 burned-in frame의 표시, cue 수/coverage/timing/readability 및 SRT/VTT 기계적 일치다.
- CLI audit와 frame review는 번역의 자연스러움, 실제 청취 sync, 발음/음질, comprehension을 인증하지 않는다.
- 실제 사람의 청취·학습·이해도 연구나 사용자 승인 데이터는 수행하지 않았으므로, 이를 인증하지 않는다.

## 변경 파일

- 생성: `transfer/correlation-causation/final-rereview.md`
- 변경하지 않음: 기존 `transfer/correlation-causation/final-review.md` (`PENDING` 내용 불변)
- `/tmp`에만 생성: caption audit JSON/stdout, bundle audit JSON/stdout, 20 midpoint frames, contact sheet, 집중 확인 stills

**최종 결론:** renamed corrected original과 현재 KO MP4의 실제 hash binding, canonical 42/6/7 provenance, 20/20 midpoint frame decode/vision, group panel 배치, intervention 7-point chart, title/label/y-axis overlap, captions audit 및 bundle audit가 확인되어 이번 corrected 영상 최종 재검토는 **PASS**다. 사람의 실제 청취/학습 인증은 아니다.
