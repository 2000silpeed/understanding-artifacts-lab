# 독립 최종 검토 — 상관관계 ≠ 인과관계

- 검토 범위: `model / writing / diagram / English script / KO cues` 우선 검토.
- 검토 매체: 현재 저장된 `video/video-original.mp4`의 20개 KO cue 중간 프레임을 직접 추출한 참고 contact sheet와, 현재 산출물의 소스·메타데이터.
- **중요한 경계:** `corrected-original.mp4` 또는 그에 준하는 corrected 최종 MP4가 현재 디렉터리에서 확인되지 않았다. 따라서 아래 영상 프레임 관찰은 **구버전 참고 검토**이며 corrected 영상의 최종 인증이 아니다. corrected render 완료 후 전체 cue 프레임을 다시 추출해야 한다.
- 사람의 실제 청취, 번역의 자연스러움에 대한 사용자 평가, 학습효과/이해도 인증은 수행하지 않았다.

## 현재 판정

**상태: PENDING — corrected MP4 프레임 재검토 대기**

소스·모델·스크립트·다이어그램·자막 구조는 대체로 일관된다. 다만 corrected 렌더의 실제 프레임, corrected media hash, corrected master/KO 합성본 및 후속 caption audit을 확인하지 못했으므로 최종 영상 승인으로 올릴 수 없다.

## 1. 모델 및 수치 검토

`data-model.js`를 Node로 직접 실행해 확인했다.

- 기본 교란 모드: `7개 기온 그룹 × 6개 반복 = 42점`
- `T=22°C` 그룹: `6점`
- 온도 고정 개입 연습: `7점`
- 전체 교란 모드 Pearson `r = 0.9672481779111594`
- `T=22°C` 그룹 Pearson `r = 0.20809520526299863`
- 온도 고정 개입 연습 Pearson `r = -0.21468038799135705`
- `scene-data-provenance.json`의 수량 `(42, 6, 7)`과 일치한다.
- 생성식은 `T → X`, `T → Y`만 포함하고 `X → Y` 항을 포함하지 않는다.
- 실제 관측·실제 사고확률·실제 모집단 추정이 아니라는 경계가 `contract.json`, `writing.md`, `sources.md`, 웹 화면 문구에 반복되어 있다.

**판정: PASS (합성 교육용 모델 및 표시 수치의 소스 일치).**

## 2. Writing 검토

`writing.md`는 다음 핵심을 일관되게 설명한다.

- 상관관계만으로 인과관계를 단정할 수 없음.
- 공통 원인 `T`가 `X`와 `Y`를 함께 움직일 수 있음.
- 관찰 질문과 개입 질문을 분리함.
- 온도 고정 및 X 변경은 실제 실험이나 실제 인과효과 추정이 아님.
- 확인 질문의 기대 답이 생성 규칙과 일치함.

과장된 실제 사례·실제 효과 주장은 확인되지 않았다. 문서 자체의 의미상 차단 이슈는 찾지 못했다.

**판정: PASS (내용·제한 고지 일관성).**

## 3. Diagram 검토

`diagram.svg`를 브라우저에서 전체 화면으로 직접 확인했다.

- 제목/부제는 잘리지 않는다.
- `T → X`, `T → Y` 방향성이 명확하다.
- `X → Y를 선언하지 않음`이 구조 영역 아래에 분명히 표시된다.
- 관찰 질문과 개입 질문이 좌우 카드로 분리되어 있다.
- 카드, 화살표, 설명 문구 사이에 눈에 띄는 겹침이나 잘림은 보이지 않는다.
- 합성 모델이라는 부제가 있어 실제 DAG 증명으로 오해할 위험을 줄인다.

**판정: PASS (직접 시각 검토 기준).**

## 4. English script ↔ KO cue 검토

`video/script.md`, `video/timeline.json`, `video/caption-alignment.json`을 대조했다.

- KO cue 수: `20`; SRT: `20`; VTT: `20`.
- 모든 cue가 English source word 범위와 연결되어 있다.
- source word 중복 배정이 없다.
- SRT/VTT와 alignment의 KO 텍스트 및 밀리초가 일치한다.
- 자동 caption audit의 결과는 `passed: true`이며, 모든 cue의 구조·시간·가독성 검사도 통과했다.
- 최고 KO CPS는 cue 16의 약 `19.30`으로 계약 상한 `20` 이내지만 여유가 작다. corrected 합성본에서 실제 표시 가독성을 재확인해야 한다.
- 의미상 주요 대응은 적절하다: synthetic data → 합성 데이터, common cause → 공통 원인, no arrow → 화살표 없음, intervention → 개입, simulation/not real people → 시뮬레이션/실제 사람이 아님.

**판정: PASS (텍스트·구조·기계적 timing); 자연스러운 번역 및 실제 청취 sync는 미인증.**

## 5. 기존 영상 프레임 참고 검토

현재 `video/video-original.mp4`에서 20개 cue의 중간 시점을 직접 추출해 검토했다. 이는 corrected 영상이 아니다.

- hook, 상승 산점도, DAG, X→Y 미선언, 그룹 비교, 개입, 관찰/개입 대비, outro의 장면 순서가 English narration 및 KO cue 의미와 대체로 맞는다.
- 중간 프레임 contact sheet에서 주제별 시각 요소가 표시되고, 주요 문구의 명백한 화면 밖 잘림은 확인하지 못했다.
- 다만 부모 작업에서 보고된 플롯 범위/제목 겹침 수정이 진행 중이므로, 기존 프레임 관찰을 corrected 결과에 전이하지 않는다.
- cue 중간 프레임만 검사했으므로 cue 시작/종료 전환, 애니메이션 중간 상태, 모든 프레임의 겹침을 인증하지 않는다.

**판정: 참고 PASS; corrected 최종 영상 판정은 PENDING.**

## 미해결 및 후속 필수 확인

1. **[BLOCKER / PENDING] corrected MP4 부재:** `video/corrected-original.mp4`가 현재 확인되지 않았다. corrected render 완료 여부와 실제 파일을 먼저 확인해야 한다.
2. **[BLOCKER / PENDING] corrected 전체 프레임:** corrected MP4에서 20개 KO cue 각각의 시작·중간·끝에 가까운 프레임을 직접 추출하고, 부모가 수정 중인 플롯 범위·제목 겹침을 확인해야 한다.
3. **[HIGH] corrected media binding 재생성:** corrected original 교체 후 `video-master.mp4`, `video-ko.mp4`, SRT/VTT/alignment의 hash와 caption audit을 corrected 매체 기준으로 다시 확인해야 한다. 현재 `caption-audit.json`은 기존 media hash를 기준으로 `passed`인 기록이다.
4. **[MEDIUM] 패키징 감사:** 현재 `bundle-audit.json`은 `passed: false`이며 `test-report.json` asset/link가 누락된 것으로 기록되어 있다. 이것은 영상 의미 검토와 별도의 패키징 미해결 사항이다.
5. **[LIMIT] 실제 청취·학습:** 이 검토는 human listening 또는 learning effectiveness 인증이 아니다.

## 검토에 사용한 직접 근거

- `./transfer/correlation-causation/data-model.js`
- `contract.json`, `scene-data-provenance.json`, `writing.md`, `sources.md`
- `video/script.md`, `video/timeline.json`, `video/caption-alignment.json`
- `video/video-ko.srt`, `video/video-ko.vtt`
- `diagram.svg` 브라우저 전체 화면
- 현재 `video/video-original.mp4`의 20개 cue 중간 프레임 직접 추출 참고 검토
- `caption-audit.json`, `bundle-audit.json`

**최종 의견:** 소스·수치·설명·다이어그램·KO cue의 내부 정합성은 양호하다. 그러나 corrected 렌더와 corrected 전체 프레임 증거가 없으므로 지금은 최종 승인하지 않고 **PENDING**으로 유지한다.
