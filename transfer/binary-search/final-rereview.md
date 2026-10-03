# 이진 탐색 최종 재검토 — corrected MP4 직접 증거

- 대상: `video/video-ko.mp4`
- 검토일: 2026-10-03
- 범위: 현재 MP4 SHA, caption/bundle 재감사, 실제 decoded frame의 cue 14/15/20 midpoint 및 cue 14 start/end 부근, 27개 midpoint의 한국어 온스크린 제목·자막 글리프·겹침 점검
- 제한: 사람 청취·번역 자연스러움·학습 효과를 인증하지 않음. 아래는 기계 감사와 직접 frame/vision 증거에 한정함.
- 보존 규칙: 기존 `final-review.md`는 수정하지 않음. 재감사 JSON·프레임은 `/tmp`에만 생성함.

## 결론

**이전 NEEDS WORK의 두 핵심 지연은 corrected MP4에서 수정됨.**

- cue 14: midpoint/end에 `23 > 16`, 23·38 제거, `L=4 U=4`가 보임.
- cue 15: midpoint/end에 `찾음: 16, 인덱스 4`, index 4의 16 강조가 보임.
- cue 20: midpoint/end에 `L > U · 목표가 없습니다`, `L=2 U=1`, 8 비교 화살표가 보임.

따라서 기존 보고서의 **“늦은 23 비교 / cue 16에서 found / 8>7이 cue 20 뒤에서야 표시”** 결함은 재현되지 않았다. 다만 각 장면의 애니메이션은 cue 시작 순간 빈/부분 상태에서 완성 상태로 전개되므로, 남은 onset 지연을 아래에 정확히 기록한다. 이는 이전처럼 다음 cue까지 의미 화면이 밀리는 현상은 아니다.

## 현재 MP4 증거

- 파일: `$LAB/transfer/binary-search/video/video-ko.mp4`
- SHA-256: `a20914b1585af246b63e591ca34a9524aa614f7329b557d5ff2f0d5ad171b83d`
- 크기: `7,622,326` bytes
- ffprobe: `87.933333 s`, H.264/yuv420p, 1920×1080, 30 fps, AAC stereo 48 kHz
- caption-alignment의 `media_bindings.video`도 동일 SHA: `a20914b1585af246b63e591ca34a9524aa614f7329b557d5ff2f0d5ad171b83d`

## 재실행한 audit

명령은 모두 `/tmp` 보고서로 출력했다.

```text
python3 $HOME/.hermes/skills/creative/understanding-artifacts/scripts/audit_captions.py \
  $LAB/transfer/binary-search \
  --report /tmp/binary-search-caption-audit-rereview.json

python3 $HOME/.hermes/skills/creative/understanding-artifacts/scripts/audit_bundle.py \
  $LAB/transfer/binary-search \
  --report /tmp/binary-search-bundle-audit-rereview.json
```

결과: **caption audit PASS / bundle audit PASS**

- cue: alignment/SRT/VTT 모두 `27`
- source timed-word coverage: `225/225`
- max CPS: `13.839`
- max start error: `0`
- media/timeline/original binding hash: PASS
- bundle의 `test-report.json` 존재 및 MP4 probe/faststart/audio: PASS

## 직접 decoded frame 증거

생성 위치: `/tmp/binary-search-rereview-frames/`

- `all-midpoints.jpg`: cue 01–27 midpoint sweep
- `requested-boundaries.jpg`: cue 14/15/20의 start·mid·end
- `cue-14-onset.jpg`, `cue-15-onset.jpg`, `cue-20-onset.jpg`: cue 시작 후 전개 확인

| cue | alignment 시간 | midpoint 직접 확인 | start/onset 확인 |
|---:|---:|---|---|
| 14 | `42.031000–45.571000` | `43.801 s`: `23 > 16`, 23·38 cross-out, `L=4 U=4`; `45.541 s`도 동일 | `42.031 s`는 빈 box, `42.350 s`에 `23 >` 전개, `42.600 s`부터 `23 > 16`과 제거 상태가 완성. 완성까지 약 `0.57 s`. |
| 15 | `46.062000–47.442000` | `46.752 s`: `찾음: 16, 인덱스 4`, 16 원형 강조; `47.412 s`도 동일 | `46.062 s`는 빈 found box, `46.200 s`에 텍스트 전개, `46.400 s`에 found 텍스트·원형 강조가 보임. 완성까지 약 `0.34 s`. |
| 20 | `58.102000–61.242000` | `59.672 s`: `L > U · 목표가 없습니다`, `L=2 U=1`, 8 비교 표시; `61.212 s`도 동일 | `58.102 s`는 빈 box, `58.500 s`에 `L > U` 전개, `58.800 s`에 empty/not-found 상태가 완성. 완성까지 약 `0.70 s`. |

이 onset animation은 각 cue 내부 초반에 완료되며, cue 14/15/20의 의미 화면이 다음 cue로 늦게 넘어가는 이전 결함과 다르다. 위 시간은 실제 frame extract 기준이며 사람 청취 동기화 주장이 아니다.

## 한국어 제목·글리프·겹침 점검

27개 midpoint contact sheet와 요청한 경계/onset frame을 직접 확인했다.

- 주요 온스크린 제목은 한국어로 표시됨: `이진 탐색`, `정렬된 배열 하나`, `가운데 값과 비교`, `목표 16: 후보 구간 줄이기`, `목표 7: 빈 구간이면 없습니다`, `경계 찾기는 다른 질문입니다`, `기억할 규칙` 등.
- 알고리즘 고유 표기 `lower_bound`, `upper_bound`는 영어 식별자로 남아 있으나 일반 제목/설명 미번역으로 보지 않음.
- 한국어 burned-in 자막 글리프에서 네모·대체문자·깨진 획은 관찰되지 않음.
- 자막은 하단 safe area 안에 있고 frame 밖으로 잘리지 않음.
- 자막과 주요 도형/상단 제목 사이의 충돌·겹침은 관찰되지 않음.
- 비정상적인 완전 black/blank frame은 확인되지 않음. 일부 cue 시작 frame의 빈 box는 장면 전개 애니메이션 상태임.

## 이전 보고서 보존

- 기존 보고서: `$LAB/transfer/binary-search/final-review.md`
- 본 재검토에서 기존 보고서는 읽기만 했고 수정하지 않음.
- 본 작업의 패키지 내 쓰기 대상은 이 파일 `final-rereview.md` 하나뿐임.

## 판정

- **현재 MP4 SHA·포맷·caption 구조/binding:** PASS
- **27 cue / 225 words:** PASS (`27`, `225/225`)
- **cue 14/15/20의 기존 cross-cue visual delay:** 수정 확인
- **한국어 온스크린 제목 및 자막 글리프/겹침:** 직접 frame 증거상 문제 없음
- **잔여 관찰:** 장면별 onset animation 약 `0.34–0.70 s`; 추가 semantic late transition으로 판정하지 않음
- **사람 인증:** 하지 않음
