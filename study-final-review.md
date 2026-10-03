# Study 최종 재검토

## 판정

- **분석기 코드 기준:** 이전 독립 리뷰의 3개 지적은 수정되어 unit 검증을 통과했다.
- **사람 결과 기준:** **측정되지 않음**. 실제 사람 응답은 없으며, 아래 fixture와 core 회귀 검사는 모두 합성 QA다. 합성 fixture를 사람 결과로 해석하지 않는다.
- **배포/최종 study 기준:** **NEEDS WORK**. `study/content.json`에 아직 일부 video fingerprint가 `pending`이고, 실제 사람 응답도 없다.

## 실제로 읽은 범위

- `study/app.js`
- `ops/summarize_human_study.py`
- `ops/test_study_analyzer.py`
- 보존된 이전 보고서 `study-independent-review.md`
- 계약 확인용 `study/question-bank.json`, `study/content.json`

코드, 배포물, 이전 보고서는 수정하지 않았다. 이 최종 보고서만 새로 작성했다.

## 실행한 명령과 실제 결과

1. `python3 ops/test_study_analyzer.py`
   - **21개 테스트, 모두 OK** (`Ran 21 tests ... OK`)
   - 포함된 검증: 24시간 retention 경계, cross-format primary 제외, 충돌 duplicate ID 양방향 파일순서, `human` 필수, synthetic 제외, 답변 재채점, 음수/NaN 시간 거부, missing directory fail-closed.

2. `node --check study/app.js && python3 -m py_compile ops/summarize_human_study.py ops/test_study_analyzer.py`
   - **종료 코드 0**, 문법/컴파일 오류 없음.

3. `node ops/test_study_core.cjs`
   - **12개 PASS**.
   - 출력상 `consent required`, `human self declaration required`, `explicit human declaration accepted, not verified`까지 통과.
   - 범위는 `Synthetic study-tool regression; not human results`.

4. 실제 JSON/API 확인 스크립트
   - 실제 `study/question-bank.json`의 최상위 타입: **list**
   - bank dict 변환 항목 수: **3**
   - 실제 정답 필드: **`answer`** (`score` 키를 사용하지 않음)
   - `summarize(empty_dir, bank_dict, content_dict)` 실제 호출 결과: `evidence_status=not_measured`, `submitted_self_declared_human_sessions=0`.

## 이전 3개 지적의 수정 확인

### 1. retention 24시간 gate — 수정됨

`ops/summarize_human_study.py`는 retention 응답이 있으면 다음을 분석 경계에서 확인한다.

- `retention_completed_at` timestamp 존재 및 파싱
- `retention_completed_at - completed_at >= 24시간`
- retention 완료 시각이 export 시각보다 늦지 않음
- `retention_cross_format_exposure`가 boolean

테스트 결과:

- 정확히 86,400초: `test_retention_rescored` **통과**
- 1초: `test_early_retention_rejected` **통과**
- 86,399초: `test_retention_boundary_below` **통과**
- timestamp 누락: `test_missing_retention_stamp` **통과**

### 2. cross-format 오염의 primary 혼입 — 수정됨

`groups` 계산에서 `primary_sessions`와 pre/post 평균 및 gain 평균은 `cross_format_exposure is False`인 clean 행만 사용한다. 오염 행은 별도의 `cross_format_sessions` 및 `contaminated_mean_gain_correct`로 보고한다. retention도 clean 행만 `retention_submissions`/평균에 포함하고, 오염 retention은 `retention_cross_format_sessions`로 분리한다.

- `test_dirty_learning_not_primary` **통과**
- `test_dirty_retention_not_primary` **통과**

### 3. 충돌 duplicate ID 3 — 수정됨

동일 ID의 `(kind, topic, format)`이 충돌하면 이미 받아들인 행을 삭제하고 ID를 `conflicted`로 표시한다. 따라서 어느 파일이 먼저 정렬되는지와 무관하게 해당 ID의 모든 export가 집계되지 않는다.

- `test_conflicting_duplicate_rejected` **통과**
- `test_duplicate_reverse_file_order` **통과**
- 정상 동일 variant duplicate는 최신 `exported_at`만 유지하는 `test_duplicate_latest_only` **통과**

## 추가 요구사항 확인

- 새 세션 시작 시 `consent`와 `human` checkbox를 모두 요구한다.
- 생성 세션에는 `human: true`, `participant_mode: "self_declared_human"`, `identity_verified: false`가 기록된다.
- 분석기는 `synthetic is not False`를 거부하고, `human is True` 및 `participant_mode == "self_declared_human"`를 요구한다.
- 따라서 `human=true`는 **자기 선언**일 뿐 인증된 사람 신원이나 실제 사람 결과를 뜻하지 않는다.
- 청취 진행률은 `!v.paused && !v.seeking && !v.muted && v.volume > 0`일 때만 `observed`에 누적된다. 음소거 또는 volume 0 구간은 진척 집계에서 제외된다. 제출 시 mute/volume 상태도 별도 기록되지만 `audible_output_verified`는 false다.
- 청취 결과는 learning score와 분리된다.

## 잔여 결함/제약

1. `study/content.json`에서 `binary-search`와 `correlation-causation`의 video fingerprint가 아직 `pending`이다. 따라서 final artifact identity가 확정되기 전에는 해당 자료의 제출 세션을 허용하지 않는 것이 맞고, 현재 결과는 base-only 범위다.
2. 실제 사람 응답, 참가자 신원 검증, 실제 청취 가능 여부, 학습 인과효과를 입증하는 데이터는 없다.
3. timestamp 검사는 일관성 검증이지 시계의 진실성 또는 참가자 신원 인증이 아니다.
4. `summarize`는 세 인자를 positional로 받는 `summarize(input_dir, bank, content)` API이며, 호출 의미는 `summarize(input_dir, bank_dict, content_dict)`와 일치한다. CLI는 실제 JSON 배열을 dict로 변환한 뒤 호출한다.

## 최종 결론

분석 경계의 retention gate, clean primary 분리, 충돌 duplicate 무효화는 이번 재검토에서 모두 실제 unit으로 확인됐다. 코드 수준의 해당 3개 지적은 **해결**이다. 다만 fake fixture는 사람 결과가 아니며, 실제 응답 0건과 pending fingerprint 때문에 study 자체를 사람 연구 결과 또는 최종 배포 완료로 승인할 근거는 없다.
