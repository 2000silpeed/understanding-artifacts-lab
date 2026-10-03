> Release note: this is the pre-render semantic/skill review. Its missing-media findings were subsequently resolved. See final-media-review.md, test-report.json and bundle-audit.json for the completed release.

# 현재 이해-artifacts 스킬 및 next-token 산출물 독립 검토

## 판정 요약

- **현재 `understanding-artifacts` 스킬의 auditor 회귀:** 통과.
- **현재 설명의 수식/확률 의미:** 핵심 계산은 일치한다. 로짓, 안정적 softmax, top-p의 threshold-crossing prefix, 재정규화, 온도 수치, `u = 0.82 -> floor`가 서로 모순되지 않는다.
- **현재 번들의 포장 상태:** 아직 부모가 소유한 최종 MP4/전사/통합 test-report가 없어 auditor 전체는 실패한다. 이는 현재 렌더 진행 상태에서 예상되는 미완료이며, 이 검토는 최종 영상 합격을 인증하지 않는다.
- **최종 권고:** 의미상 차단 결함은 찾지 못했다. 다만 릴리스 전에 부모가 최종 MP4와 전사/test-report를 채우고, 아래의 cross-format 명확성 제안 2건을 반영하면 더 안전하다.

## 범위

읽은 항목:

- `skill/understanding-artifacts/SKILL.md`
- 현재 `audit_bundle.py`, `test_audit_bundle.py`, `references/evaluation.md`
- `output-understanding-lab`의 `contract.json`, `facts.json`, `writing.md`, `diagram.svg`, `index.html`, `sources.md`, `test_web.js`
- `video/source/scenes.js` 및 `script.md`
- 이전 `skill-review.md`는 참고만 하고, 현재 auditor를 다시 실행해 판정했다.

합성 auditor fixture와 실제 next-token demo 결과를 분리했다. 영상은 기다리거나 최종 합격 판정하지 않았다.

## 실제 실행 명령과 결과

| 명령 | 종료 | 결과 |
|---|---:|---|
| `python3 skill/understanding-artifacts/scripts/test_audit_bundle.py --report ./tests/independent-skill-regression.json` | **0** | 15 tests, failures 0, errors 0, skipped 0, passed true |
| `python3 skill/understanding-artifacts/scripts/audit_bundle.py . --report /tmp/understanding-current-audit.json` | **1** | `video/video.mp4`, `video/script.md`, `test-report.json`가 아직 없어 asset/local-link checks 실패. 최종 영상의 유효성 판정으로 사용하지 않음. |
| `node --check scenes.js` (explainroo video project) | **0** | 현재 scenes.js 문법 정상 |
| Python 독립 계산/소스 assertion: T=0.5/1/2, top-p=.8, 좌표, `u=.82` | **0** | top-p keep `[0,1]`, mass `0.8334218875890236`, renormalized `[.7310585786300049,.2689414213699951]`, draw가 floor 구간에 들어감 |

회귀 결과 파일: `tests/independent-skill-regression.json`.

이번 pass에서는 read-only 조건 때문에 `test_web.js`를 재실행하지 않았다. 기존 `tests/web-latest.json`은 부모가 만든 별도 증거로 보고, 이 독립 보고서의 실행 결과로 세지 않았다.

## 스킬 auditor 회귀 확인

이전 `skill-review.md`의 superseded auditor 결함을 현재 소스에서 재검증했다. 현재 15개 합성 테스트가 다음을 모두 통과했다.

- path가 없는 외부 URL과 protocol-relative URL 차단
- CSS `@import`/`url()` 및 정적 JS `fetch()` 외부 literal 차단
- non-object contract(`[]`, `null`, 문자열, 숫자)를 traceback 없이 구조화된 실패로 처리
- invalid UTF-8 web asset을 `web_parse` 실패로 처리
- faststart 없는 MP4 차단
- report 안에 bundle의 machine-specific absolute root가 남지 않는지 확인
- missing/empty/traversal/invalid video/no-audio fixture 차단

따라서 이전 F-01~F-06은 현재 auditor 기준으로 **재현되지 않았다**. 다만 테스트가 주로 `auditor.audit()`를 직접 호출하므로, CLI `--report` 파일 생성과 process exit code까지 subprocess로 고정하는 테스트를 추가하면 회귀 방어가 더 강해진다. 이것은 현재 의미의 차단 결함은 아니다.

## 의미/계산 검토 결과

### 통과한 핵심 항목

- `facts.json`, `contract.json`, `writing.md`, web JavaScript, `scenes.js`의 공통 입력이 모두 `logits = [2.0, 1.0, 0.3, -0.4]`와 네 개의 교육용 후보로 일치한다.
- 안정적 softmax의 식 `exp((z_i - max(z))/T) / sum(...)`이 스킬, facts, web, diagram에 일관되게 반영되어 있다.
- T=1 값은 `[60.9%, 22.4%, 11.1%, 5.5%]`로 맞고, 반올림 합이 99.9%일 수 있다는 caveat도 있다.
- 온도 표시값은 영상에서 `T = 0.5`와 `T = 2.0`으로 명시된다. 표시된 값 `85.0/11.5/2.8/0.7` 및 `42.8/26.0/18.3/12.9`는 같은 로짓에서 계산한 반올림값과 일치한다.
- top-p는 개별 확률 하한이 아니라 내림차순 누적 질량이다. `.609 < .80`, `.609 + .224 = .833 >= .80`이므로 mat와 floor를 보존하는 설명이 정확하다.
- 보존 질량 `0.8334218875890236`을 다시 나누어 `0.7310585786300049`, `0.2689414213699951`을 얻는다. Web의 두 리본도 원래 분포와 재정규화 분포를 구별한다.
- 영상 sample scene의 경계는 `x = 280 + 1360 * .73105858 = 1274.23967`, `u=.82`의 위치는 `x=1395.2`이다. 따라서 u는 floor 구간에 있고, `script.md`의 “selects floor”와 scene의 `선택: floor`가 맞는다.
- greedy는 sampling과 별도 모드로 처리되고, positive temperature에서는 argmax가 변하지 않는다.
- writing/web/영상 모두 전체 vocabulary가 생략된 toy example, tokenizer 경계 미증명, 실제 모델 추론 아님, 확률이 사실성을 보장하지 않음, 선택 뒤 실제 모델이 logits를 다시 계산한다는 caveat를 포함한다.
- `SKILL.md` 자체에는 `$HOME` 또는 demo 전용 경로가 없고, `scripts/`·`templates/` 상대 경로를 사용한다. `sources.md`는 공개 HTTPS source와 retrieval/evidence 경계를 담으며, skill/source portability 측면의 차단 문제는 보이지 않았다.

## 조치가 필요한 항목과 주관적 제안

### 🟠 현재 번들 릴리스 차단: 부모 산출물 미완료

현재 `contract.json`이 요구하는 `video/video.mp4`, `video/script.md`, `test-report.json`이 lab root에 없다. 실제 bundle auditor는 이 때문에 exit 1이다. 부모가 렌더를 끝내면 다음을 다시 실행해야 한다.

1. 최종 MP4를 `contract.json`의 상대 경로에 배치한다.
2. 전사와 통합 test-report를 상대 경로에 배치한다.
3. auditor, 실제 browser test, final MP4 playback/ffprobe 검사를 다시 실행한다.
4. 그 결과만으로 최종 video/media 판정을 한다.

이 항목은 현재 부모가 렌더 중이라는 전제에서는 예상된 blocker이며, 본 보고서는 영상이 완료됐다고 주장하지 않는다.

### 🟡 권장: standalone diagram에서 temperature를 별도 intervention으로 더 명시

`diagram.svg`와 inline SVG의 softmax 상자에는 `exp((z−max)/T)`가 있어 수식상 T는 존재한다. 그러나 causal box가 `CONTEXT → LOGITS → SOFTMAX → FILTER → CHOICE`로만 보이고, `T=0.5`/`T=2.0`의 개입이나 분포 변화가 별도 beat로 보이지 않는다. 요구사항이 temperature를 독립적인 causal stage로 보여주는 것이라면, softmax와 filter 사이에 `TEMPERATURE` callout 또는 “T 낮음/높음” annotation을 추가하는 것이 좋다. **수식 오류는 아니며, cross-format 시각 명확성 개선이다.**

### 🟡 권장: 서로 다른 sample draw를 화면에서 명시

- Web 기본 seed 42의 draw는 mat를 선택한다.
- 영상은 의도적으로 `u=.82`를 써서 floor를 선택한다.
- standalone diagram은 `sample / greedy`와 `mat`만 표시하고 draw/seed를 표시하지 않는다.

서로 다른 독립 예시를 사용하는 것 자체는 오류가 아니다. 다만 diagram의 `mat`에 `illustrative draw` 또는 `seed 42`를 붙이거나, video 쪽에 `explicit u=.82 example`를 더 크게 표시하면 학습자가 cross-format 결과를 불일치로 읽을 가능성이 줄어든다.

### 💭 사소한 제안: normalized percentages의 음성 동기

영상 화면은 sample scene에서 73.1%/26.9%를 보여주지만 `script.md`의 sample narration은 `u=.82`와 floor 선택을 말하고, 73.1%/26.9%를 직접 발화하지 않는다. 화면과 음성이 모순되지는 않는다. 단, 숫자까지 음성으로 확인하려는 설계라면 “After renormalization, mat is 73.1 percent and floor is 26.9 percent”를 sample scene narration에 넣고 cue를 맞추는 편이 낫다.

## 수정/생성 파일

- 생성: `./independent-current-review.md` (이 보고서)
- 생성/갱신: `./tests/independent-skill-regression.json` (사용자가 요구한 auditor 회귀 report)
- understanding-artifacts skill, web, diagram, writing, scenes, script, publishing 대상은 수정하지 않았다.
