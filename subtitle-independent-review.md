# 자막 독립 검토 보고서

- 검토 범위: `caption-v1`의 English source ↔ 한국어 25 cues, SRT/VTT, timeline/alignment, contract, 원문 네 형식 범위, v1.1 스킬 및 auditor/gate.
- 검토 방식: 읽기/실행 전용. 최종 MP4 렌더를 기다리지 않았고, 최종 영상 PASS를 판정하지 않는다.
- 최종 판정: **NEEDS WORK (조건부 기술 검증 PASS, 번역·청취·최종 영상 인증은 미완료)**.

## 실행 증거

실행한 명령과 실제 종료 코드:

1. `python3 -B skill/understanding-artifacts/scripts/test_audit_captions.py`
   - exit **0**; **25 tests, OK**.
2. `python3 -B skill/understanding-artifacts/scripts/audit_captions.py . --report /tmp/installed-caption-audit.json`
   - exit **0**; `passed=true`.
   - 25 cues, SRT 25, VTT 25; timed source words **189/189**; duplicate 0; 최대 start drift **0 s**; 최대 CPS **15.918**; ffprobe duration **79.333333 s**.
   - timeline SHA-256, source-word exactness, cue 순서/겹침/최소 노출, Hangul, SRT/VTT 일치 모두 PASS.
3. `python3 -B skill/understanding-artifacts/scripts/test_audit_bundle.py --report /tmp/installed-bundle-regression.json`
   - exit **0**; **16 tests, OK**.
4. `python3 -B skill/understanding-artifacts/scripts/audit_bundle.py . --report /tmp/installed-bundle-audit.json`
   - exit **0**; required subtitle gate PASS.
   - 현재 파일에 대해 H.264/yuv420p, 1920x1080, duration 79.333333, AAC stream, faststart 및 subtitle audit가 PASS로 보고됨.
5. 독립 교차검사 `python3 -B /tmp/independent_caption_check.py`
   - exit **0**; alignment source 재구성 불일치 0, 중복 0, coverage 189, start error 0.
   - 임시 복사본에서 `original_video_sha256`를 64개 0으로 변조해도 auditor가 **True/pass**를 반환하는 false-pass probe를 확인.
6. `sha256sum .../video/video-master.mp4 .../video/video-ko.mp4 .../video/timeline.json .../video/caption-alignment.json`
   - exit **0**; timeline hash는 alignment의 `timeline_sha256`와 일치.

## 25개 번역 대조 결과

### 보존된 요소

- **수치/조건**: `2.0, 1.0, 0.3, -0.4`, `60.9%, 22.4%, 11.1%, 5.5%`, `temperature=1`, `p=0.80`, `83.3%`, `u=0.82`가 모두 cues에 보존됨.
- **부정/caveat**: “not measured model output” (cue 6), “not correctness” (cue 14), “do not verify real-world truth” (cue 25)가 의미상 보존됨. toy가 한 단계만 보인다는 제한(cue 22)도 보존됨.
- **용어/라벨**: `mat`, `floor`, `sofa`, `roof`, `top-p`, `logits`, `softmax`, `token`의 핵심 라벨은 대체로 유지됨.
- **coverage**: 25 cue가 timeline의 189 timed words를 빠짐없이 한 번씩 할당함.

### 수정이 필요한 항목

1. **P1 — cue 16 (수치 의미가 모호해질 수 있음)**
   - English: “At p equal to 0.80, mat and floor retain 83.3 percent.”
   - 현재: `p=0.80이면 mat과 floor가 남고, 필터 전 확률의 합은 83.3%예요.`
   - 문제: `필터 전 확률의 합`은 전체 후보의 필터 전 합이 83.3%라는 뜻으로 읽힐 수 있다. 실제 의미는 **남은 mat+floor가 필터 전 확률 질량 83.3%를 차지한다**는 것.
   - 최소 수정 제안: `p=0.80이면 mat과 floor가 남고, 두 후보가 필터 전에 차지한 확률 질량의 합은 83.3%예요.`

2. **P1 — cue 15 (top-p의 prefix 의미가 약화됨)**
   - English: “keeps the smallest prefix reaching its mass.”
   - 현재: `누적 질량이 p에 도달하는 최소 집합을 남겨요.`
   - 문제: `prefix`를 `집합`으로만 옮겨 순서가 있는 “높은 확률 순의 앞부분”이라는 핵심 조건이 사라진다. top-p를 임의의 최소 집합으로 오해할 위험이 있다.
   - 최소 수정 제안: `누적 질량이 p 이상이 되도록 높은 확률 순으로 앞에서부터 고른 최소 접두 집합을 남겨요.`

3. **P2 — cue 4 용어 누락/표현 약화**
   - `the floor token 1.0`이 `floor 1.0`으로 축약됨. chart label만으로는 동작하지만 “token” 용어가 한 번 누락된다.
   - 제안: `mat 2.0, floor 토큰 1.0,` 또는 `mat 2.0, floor라는 토큰 1.0,`.
   - `illustrative` → `가상`은 큰 오역은 아니나 `예시용/설명용`이 원문의 교육용 caveat에 더 충실하다.

4. **P2 — cue 24 용어 drift**
   - English: “These estimates predict a next token.”
   - 현재: `이 확률은 다음 토큰을 예측해요.`
   - `estimates`를 `확률`로 좁혀 번역했다. 앞 문맥상 이해 가능하지만 source의 일반적 “추정값”보다 범위가 좁다.
   - 제안: `이 추정값은 다음 토큰을 예측해요.`

나머지 cues(1–3, 5–14, 17–23, 25)는 수치·조건·부정·교육용 caveat 및 의미가 실질적으로 일치한다. 위 P1 두 건은 machine auditor가 검출할 수 없는 semantic translation finding이므로 번역본을 고치고 SRT/VTT/alignment를 함께 재생성·재검증해야 한다.

## auditor/gate 추가 취약점

- **P1 — `original_video_sha256` provenance가 검증되지 않음.** `caption-alignment.json`에 이 필드가 있지만 `audit_captions.py`는 읽거나 실제 파일과 비교하지 않는다. 임시 bundle 복사본에서 해당 값을 전부 0으로 바꿔도 `audit()`가 `passed=True`였다. 현재 선언값은 `video/video.mp4`의 hash와 일치하지만 감사 대상 contract video인 `video/video-ko.mp4` 또는 master와의 binding이 없다.
  - 영향: 동일 duration/timeline 구조의 다른 영상에도 captions가 기술적으로 PASS할 수 있다.
  - 제안: contract에 provenance 대상 상대경로를 명시하고 그 파일의 SHA-256을 실제 계산해 비교하거나, 최종 mux video hash를 alignment에 기록하고 gate에서 강제. 변조 hash 회귀 fixture도 추가.
- auditor 출력의 명시적 scope처럼, 구조 PASS는 **번역 정확성·실제 audible sync·시각적 overlap·WCAG·학습효과를 증명하지 않는다**. 이는 버그가 아니라 올바른 limitation이며, required gate PASS를 translation/listening 인증으로 표시하면 안 된다.
- 현재 `audit_bundle`의 media probe/메타데이터 PASS도 최종 렌더의 사람 청취, decoded frame review, 실제 플레이어 TextTrack toggle/offline 동작을 대신하지 않는다.

## 원문 네 형식 및 v1.1 충실성

- `ops/karpathy-source.json`의 원문이 말하는 네 형식 **Writing; Diagrams / images; Web pages; Explainer videos** 범위를 계약의 `writing`, `diagram`, `web`, `video` artifact와 스킬 v1.1의 절차/검증 항목이 유지한다.
- 원문이 video를 선호한다고 한 것을 “보편적으로 학습효과가 더 좋다”로 과장하지 않았고, contract도 human learning을 미검증으로 둔다.
- v1.1의 중요한 자막 요구(한국어 narration subtitle, source-word alignment, final audio timeline, SRT/VTT, burned-in MP4/master 구분, human listening/translation 분리, four-format/human-learning limitation)가 현재 자료에 반영되어 있다.
- 다만 현재 `contract.json`의 `test_coverage`는 video/captions를 `not_run`으로 표시하고 있으므로, 이번 기술 gate 결과만으로 이를 `run/pass`로 바꾸어 해석해서는 안 된다.

## 최종 판정 및 다음 조치

- **기술 구조/required gate:** PASS (위 명령 exit 0 근거).
- **번역 semantic review:** NEEDS WORK — cue 15/16은 수정 후 재검토 필요; cue 4/24는 권장 수정.
- **사람 청취/번역 인증:** NOT RUN. ASR/alignment 및 기계 audit는 사람 청취 인증이 아니다.
- **최종 MP4:** 이 독립 검토에서 PASS하지 않음. 부모 렌더 완료 후 최종 decoded frame, caption-safe 위치, actual player track/toggle, audio/caption sync를 별도로 검사해야 한다.
- auditor provenance hash gate를 보강하고, 번역 수정 후 `test_audit_captions.py`, `audit_captions.py`, required bundle gate를 재실행할 것.
