# 이진 탐색 최종 4형식 독립검토

- 검토 대상: `transfer/binary-search/video/video-ko.mp4`
- 검토 범위: writing / diagram / web / burned-in Korean MP4, 영어 source↔한국어 cue 의미, 실제 MP4 midpoint 프레임, 구조·자막 audit
- 검토 한계: 실제 사람 청취·학습·이해도 인증이 아니다. 오디오를 사람이 청취했다는 주장은 하지 않는다.
- 작업 규칙: 패키지 파일은 이 보고서만 수정. 프레임·contact sheet·audit 재실행 산출물은 `/tmp`에만 생성.

## 최종 판정

**보완 필요(최종 승인 보류).**

MP4는 실제 `87.933333 s`, H.264/yuv420p 1920×1080/30fps, AAC stereo로 재생 가능하고, 27개 자막 cue의 구조·coverage audit은 PASS다. writing/diagram/web의 고정 예시도 `[2, 5, 8, 12, 16, 23, 38]`, target `16 → index 4`, missing target `7`, zero-based/inclusive 범위와 일치한다.

그러나 실제 decoded frame을 cue midpoint와 경계 시점에서 확인한 결과, **found 경로의 cue 14–15와 missing 경로의 cue 20에서 화면 전환이 영어 narration/한국어 자막보다 늦다.** 따라서 구조 PASS만으로 영상 의미 동기화를 최종 PASS할 수 없다.

## 실행한 검증과 실제 결과

### MP4 probe

- `ffprobe ... transfer/binary-search/video/video-ko.mp4`
- duration: `87.933333 s`
- video: H.264 High, `1920×1080`, `30/1`, `yuv420p`, 2638 frames
- audio: AAC LC, `48000 Hz`, stereo
- bundle probe에서 faststart도 PASS

### 실제 프레임 추출 및 vision 검토

각 alignment cue의 실제 midpoint를 MP4에서 `ffmpeg -ss ... -frames:v 1`로 27장 추출했다.

- 개별 프레임: `/tmp/binary-search-review/cue-01-*.png` … `cue-27-*.png`
- 전체 contact sheet: `/tmp/binary-search-review/cue-midpoints-contact-sheet.jpg`
- longest/condition/negative/bounds 선별 sheet: `/tmp/binary-search-review/selected-cue-vision.jpg`
- cue 14와 cue 20 경계 시점 sheet: `/tmp/binary-search-review/cue14-cue20-timing.jpg`

관찰: burned-in 한국어 자막은 27개 midpoint에서 하단 safe area 안에 있고, 잘림·겹침·깨진 글자는 보이지 않았다. 검은/빈 화면으로 오인할 만한 완전한 blank frame은 없었다. 다만 아래 cue 전환 지연은 실제 프레임에서 확인됐다.

### caption 구조 audit 재실행

명령:

```text
python3 skill/understanding-artifacts/scripts/audit_captions.py transfer/binary-search --report /tmp/binary-search-caption-audit-rerun.json
```

결과: **PASS**

- cue 수: alignment/SRT/VTT 모두 `27`
- source timed-word coverage: `225/225`
- max CPS: `13.839`
- max start error: `0`
- timeline/original/media binding hash checks: PASS
- audit 범위 밖: 번역 품질, 실제 audible sync, visual overlap, 사람 학습 효과

### bundle 구조 audit 재실행

명령:

```text
python3 skill/understanding-artifacts/scripts/audit_bundle.py transfer/binary-search --report /tmp/binary-search-bundle-audit-rerun.json
```

결과: **FAIL(한 항목)**

- writing/diagram/web/video/master/transcript/SRT/VTT/alignment/timeline/sources/original MP4 존재: PASS
- HTML static local-link/network literal check: PASS
- MP4 metadata/compatibility/audio/faststart: PASS
- 실패 항목: `asset_tests` — 계약서가 요구하는 `test-report.json`이 패키지에 없음
- audit 보고서 자체는 `/tmp`에만 생성했으며 패키지에 test-report를 만들지 않았다.

## 모든 cue 영어 source ↔ 한국어 의미 검토

| cue | scene | source 의미 ↔ KO 의미 | 실제 midpoint 시각 검토 |
|---:|---|---|---|
| 01 | hook | PASS: 정렬 배열이 매 비교에서 후보 절반을 버린다는 뜻 일치 | PASS. 자막 판독 가능. 초반은 title-only라 시각적 지지는 약함. |
| 02 | hook | PASS: 순서가 지름길을 안전하게 한다는 뜻 일치 | PASS. sorted/target 도식과 일치. |
| 03 | setup | PASS: 일곱 값 | PASS. 배열 첫 값이 등장. |
| 04 | setup | PASS: 첫 값 2, 5 | PASS. 2와 5 표시. |
| 05 | setup | PASS: 다음 값 8, 12 | PASS. 8과 12까지 표시. |
| 06 | setup | PASS: target 16 | PASS. target 16 표시. |
| 07 | setup | PASS: 마지막 값 23, 38 | PASS. 23/38 표시. |
| 08 | setup | PASS: 0-based index로 16 검색 | PASS. 전체 배열과 index 표시. |
| 09 | first | PASS: 현재 범위 0..6 | PASS. 전체 배열/index가 보임. |
| 10 | first | PASS: floor((0+6)/2)=3 | PASS. L=0,U=6 및 mid=3/12가 보임. |
| 11 | first | PASS: middle value 12 | PASS. mid pointer가 12를 가리킴. |
| 12 | found | PASS: 12<16, 왼쪽 절반 불가 | PASS. 12<16와 0..3 제거가 보임. |
| 13 | found | PASS: 4..6 유지 | PASS. keep indexes 4..6와 L=4,U=6이 보임. |
| 14 | found | **KO 번역 자체는 PASS**: 23이 크므로 index 4만 유지 | **FAIL visual sync**. cue 전체와 midpoint(42.10–45.56s)에서 화면은 여전히 `12 < 16`, `keep indexes 4..6`, mid=3이며 23 비교/제거를 보여주지 않음. |
| 15 | found | **KO 번역 자체는 PASS**: index 4에 16 | **FAIL visual sync**. midpoint 46.75s에서는 `23 > 16`/23·38 제거 단계가 보이고, index 4의 found 시각은 뒤 cue 쪽에서 나타남. |
| 16 | found | PASS: 검색 성공 | PASS. `found: 16 at index 4`와 원형 강조가 보임. |
| 17 | missing | PASS: 이제 7 검색 | PASS. target 7 장면으로 전환. |
| 18 | missing | PASS: 12>7, 0..2 유지 | PASS. `12 > 7 → keep 0..2`, L=0,U=2. |
| 19 | missing | PASS: 5<7, index 2 유지 | PASS. `5 < 7 → keep index 2`, L=2,U=2. |
| 20 | missing | **KO 번역 자체는 PASS**: 8>7, 범위 empty | **FAIL visual sync**. midpoint와 cue end 근처까지 화면은 `5 < 7 → keep index 2` 상태다. `8 > 7`/empty 전환은 약 61.85s 이후, 다음 cue 경계 뒤에 나타난다. |
| 21 | missing | PASS: 7은 배열에 없음 | PASS. `L > U · not found`와 8>7/empty 결론이 보임. |
| 22 | bounds | PASS: basic search는 한 match에서 멈춤 | PASS 의미상 일치. midpoint는 제목/자막 중심으로 시각 정보가 sparse. |
| 23 | bounds | PASS: boundary search는 다른 질문 | PASS. lower_bound/upper_bound 두 상자가 보임. |
| 24 | bounds | PASS: lower_bound = target 이상 첫 값 | PASS. lower_bound 설명과 `첫 번째 값 ≥ target`. |
| 25 | bounds | PASS: upper_bound = target보다 큰 첫 값 | PASS. upper_bound 설명과 `첫 번째 값 > target`. |
| 26 | outro | PASS: 순서가 비교를 informative하게 함 | 텍스트 의미 PASS. midpoint는 title-only에 가까워 시각적 보강이 약함. |
| 27 | outro | PASS: discard 전 sorted prerequisite 확인 | PASS. `sorted → compare middle → discard half`, `sorted first`와 자막 일치. |

## 4형식 일치 확인

### Writing

`writing.md`는 다음을 명시한다.

- 배열 `[2, 5, 8, 12, 16, 23, 38]`
- target `16`, 결과 index `4`
- `mid=floor((L+U)/2)`
- found 경로 `0..6 → 4..6 → 4..4`
- missing target `7` 경로 `0..6 → 0..2 → 2..2 → L=3,U=2`
- 정렬 전제 및 lower/upper bound 구분

### Diagram

`diagram.svg`의 정렬 전제, `L=0,U=6`, `mid=3`, `array[3]=12`, 0..3 제거, found/missing 경로가 writing과 일치한다. diagram의 단일 예시 값·index·결론에 불일치는 발견하지 못했다.

### Web

실제 local HTTP 서버에서 `index.html`을 로드했다.

- 한국어 제목/설명, 고정 배열, target 16, 단계 실행 UI 표시: PASS
- video `video-master.mp4` 실제 `readyState=4`, duration `87.933333`: PASS
- 한국어 text track 실제 cue 수 `27`, mode `showing`: PASS
- target 7로 전환 후 4회 step 결과 실제 DOM:
  - `0..6 → mid 3 = 12, greater`
  - `0..2 → mid 1 = 5, less`
  - `2..2 → mid 2 = 8, greater`
  - `없습니다 · L > U (2 > 1)`
  - writing의 not-found 계산과 일치
- 잔여 UI 결함: reset 직후 message가 이미 `12과 target 비교`를 표시하지만 실행 기록은 “아직 비교하지 않았습니다”라고 표시한다. 알고리즘 결과 결함은 아니며 상태 표현의 일관성 문제다.

### Movie

MP4의 27개 midpoint와 selected/timing sheet를 vision 검토했다. 배열·L/U·mid·found/missing·bounds의 숫자와 한국어 자막은 대부분 source 의미와 일치한다. 단, cue 14–15 및 cue 20의 실제 화면 전환 지연은 movie 단독의 최종 승인 결함이다.

## 잔여 결함 및 우선순위

1. **높음 — found 경로 cue 14–15 semantic/visual sync 지연**
   - cue 14(42.031–45.571s) narration은 23 비교와 index 4 유지인데, 실제 화면은 끝까지 12 비교/4..6 유지 단계다.
   - cue 15(46.062–47.442s) narration은 index 4의 16을 말할 때 실제 midpoint 화면은 23>16 제거 단계다.
   - 실제 `found: 16 at index 4` 화면은 cue 16 쪽에서 확인된다.
   - 수정 방향: visual mark/transition을 cue 14 narration에 맞추거나 cue 14–16 caption/audio cue 경계를 최종 화면 전환과 재정렬한 뒤 MP4와 alignment/hash를 함께 재생성해야 한다.

2. **높음 — missing 경로 cue 20 semantic/visual sync 지연**
   - cue 20(58.102–61.242s) narration은 8>7 및 empty인데, midpoint와 61.24s 근처까지 `5<7 → keep index 2`가 남아 있다.
   - `8>7` 및 empty/not-found 상태는 약 61.85s 이후 다음 cue 쪽에서 들어온다.
   - 수정 방향: 8>7/empty transition을 cue 20 안으로 당기거나 cue 20/21 timing을 실제 visual mark에 맞춰 재생성한다.

3. **중간 — bundle 구조 audit가 `test-report.json` 부재로 FAIL**
   - 계약서에는 tests artifact가 선언되어 있으나 패키지에는 없다.
   - 이번 검토에서는 사용자 지시대로 final-review.md 외 패키지 파일을 수정하지 않았다.

4. **낮음 — declared screen language와 movie 내부 label 언어 차이**
   - contract는 screen `ko`로 선언되어 있으나 MP4 내부 주요 title/label은 `Binary search`, `One sorted array`, `Compare the middle`, `Target 16`, `lower_bound` 등 영어다.
   - burned-in 한국어 자막은 읽히므로 자막 접근성/의미 전달의 즉시 blocker로 보지는 않지만, 계약의 screen-language 요구를 엄격히 적용하면 정리 대상이다.

5. **낮음 — 일부 cue의 시각 보강이 늦거나 sparse**
   - cue 01 midpoint는 title-only에 가깝고, cue 26 midpoint도 title-only에 가까우며 구체적인 `sorted → compare middle → discard half` 요약은 cue 27에서 나타난다.
   - 의미상 번역 오류는 아니지만 midpoint 기준 cue별 visual support는 약하다.

6. **낮음 — web 초기 상태 message/trace 불일치**
   - 초기 DOM message는 `12과 16 비교: less`를 표시하는 반면 trace는 아직 비교하지 않았다고 표시한다.
   - 실제 step 계산과 target 7 결과는 정상이다.

## 승인 조건

- cue 14/15와 cue 20의 visual transition을 narration/caption 의미와 일치시키고 final MP4에서 다시 midpoint/경계 프레임을 추출한다.
- caption audit 재실행에서 27 cue, coverage 225/225, media binding hash가 다시 PASS인지 확인한다.
- bundle audit의 `test-report.json` 정책을 별도로 해결하거나, 의도적으로 미제공인 이유를 배포 판정에 명시한다.
- 수정 후 사람이 들었다거나 학습 효과가 검증됐다고 표현하지 않는다.

## 검토 결론

**기술 포맷·재생·자막 구조: PASS.**
**writing/diagram/web 고정 예시 일치: PASS.**
**MP4 전체 cue 의미 동기화: FAIL(2개 핵심 지연 구간).**
**최종 4형식 배포 판정: 보완 필요.**
