# Understanding Artifacts Lab · 다음 토큰 선택

[웹에서 실행](https://2000silpeed.github.io/understanding-artifacts-lab/) · [81.7초 영상](video/video.mp4) · [명료한 글](writing.md) · [인과 도식](diagram.svg) · [검증 보고](test-report.json)

Karpathy의 글 → 도식 → HTML → 맞춤형 설명 영상 제안을 실제 워크플로로 만든 교육용 데모입니다. 같은 질문과 가상 입력을 네 형식으로 설명하고, 사실·수학·동작·미디어 검사를 각각 수행했습니다.

## 직접 조작하기

ZIP을 풀고 `index.html`을 열면 오프라인으로 작동합니다. 로컬 한국어 글꼴도 포함했습니다. 더 엄격한 브라우저나 영상 자막/미디어 정책에서는 `python3 -m http.server 8000` 후 `http://localhost:8000`을 열어 주세요.

온도 T, top-p, seed를 바꾸고 sample/greedy를 비교해 보세요. 필터링 전 확률과 필터링 후 재정규화된 확률을 구분해서 표시합니다. 선택 뒤에는 실제 모델이 문맥을 바탕으로 logits를 다시 계산해야 하며, 이 데모는 실제 모델 추론을 실행하지 않습니다.

## 네 출력의 관계

가상 logits는 `[2, 1, 0.3, -0.4]`입니다. T=1, top-p=.8에서 mat·floor를 보존하고, 다시 정규화하면 73.1%·26.9%입니다. 웹/도식은 기본 seed 42 또는 greedy의 mat를, 영상은 명시적인 u=.82의 floor를 보여 줍니다. 같은 분포에서도 추출값이 다르면 선택은 달라집니다.

영상: 1920×1080, 30 fps, H.264/yuv420p + AAC, 영어 내레이션, 한국어 화면. 로컬 Kokoro 음성·Whisper 전사 검증을 사용했습니다. 추가 유료 음성 API는 사용하지 않았습니다. [`video/script.md`](video/script.md)는 의도한 원고이고, [`video/qa.json`](video/qa.json)은 실제 최종 오디오의 전사 대조입니다. ASR 일치율은 인간의 이해도 점수가 아닙니다.

## 재사용 스킬

[`skill/understanding-artifacts`](skill/understanding-artifacts)에는 주제 계약, 평가 지침, 번들 검사기와 합성 회귀 테스트가 있습니다. 합성 fixture의 통과를 이 데모의 학습효과로 해석하지 않습니다. 계약은 출처의 사실과 설명용 가상 데이터를 구분하도록 요구합니다.

## 검증 다시 실행하기

Python 3.9+, Node 20+, ffmpeg/ffprobe가 필요합니다.

```sh
npm install
npx playwright install chromium
python3 ops/numerical_oracle.py
npm test
npm run verify:parent
npm run audit
python3 skill/understanding-artifacts/scripts/test_audit_bundle.py
```

영상 소스와 생성 음성 캐시는 [`video/source`](video/source)에 있습니다. explainroo 설치 후 해당 폴더를 프로젝트로 `node bin/explainroo.js check <project>`, `render <project>`, `verify <project>`를 실행할 수 있습니다. 원본의 `build/voice` 캐시를 보존했으므로 이미 생성한 음성을 재사용할 수 있습니다. 한국어 렌더에는 Noto Sans CJK가 필요합니다.

## 검증의 한계

- 실제 모델에서 측정한 logits나 tokenizer 경계가 아니라, 계산을 설명하기 위한 가상 4후보 예제입니다.
- 글은 **STE-inspired**입니다. ASD-STE100 준수·인증을 주장하지 않습니다.
- 계산·브라우저 동작·미디어 구조·음성 전사 대조를 검사했습니다. 사람을 대상으로 한 이해도 실험은 수행하지 않았습니다.
- 높은 생성 확률이나 낮은 온도는 현실의 사실성을 보장하지 않습니다.

원문: https://x.com/karpathy/status/2105819303471976479 · 메커니즘 출처는 [`sources.md`](sources.md).

코드/원고는 MIT. Noto 기반 서브셋 글꼴은 SIL OFL 1.1이며 assets의 라이선스·출처를 따릅니다.
