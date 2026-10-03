# Understanding Artifacts Lab — v1.1.0

하나의 개념을 **글 · 도식(SVG) · 인터랙티브 웹 · 설명 영상**으로 표현한, 오프라인에서도 실행할 수 있는 교육용 실험실입니다. Karpathy의 [원문](https://x.com/karpathy/status/2105819303471976479)에서 출발했습니다.

## 세 가지 사례

- [LLM의 다음 토큰 선택](index.html): 같은 가상 logits에서 온도, top-k, top-p가 후보 분포를 어떻게 바꾸는가.
- [이진 탐색](transfer/binary-search/index.html): 정렬 전제, 0 기반 인덱스, 성공·실패 경로, 일반 검색과 경계 검색의 차이.
- [상관관계와 인과관계](transfer/correlation-causation/index.html): 같은 합성 생성 규칙으로 공통 원인, 조건부 관찰, 가상 개입을 구분.

각 사례에는 `writing.md`, `diagram.svg`, `index.html`, `video/video-ko.mp4`가 있습니다. 영상은 **영어 음성 + 전체 한국어 동기 자막**입니다. 브라우저용 무자막 master와 soft captions, 다운로드용 burned-in MP4, SRT·WebVTT·word alignment도 포함합니다.

## 실제 사람용 평가 도구

[평가 참여 화면](study/index.html)은 동의·자기 선언 뒤 사전 질문 → 한 형식의 설명 → 사후 질문 → 하루 뒤 회상 질문으로 진행합니다. 자막·청취 평가도 별도 흐름으로 제공합니다.

- 답변은 이 기기의 localStorage에만 저장합니다. 자동 업로드·분석 서비스·계정 로그인이 없습니다.
- 참여자가 JSON을 직접 내보내고 공유해야 분석할 수 있습니다. 기기 내 답변 삭제가 가능합니다.
- 다른 형식 노출을 기록하며, primary 집계와 오염 집계를 분리합니다.
- 문항·산출물 SHA-256을 기록하고, 합성 QA는 실제 응답 집계에서 제외합니다.
- 청취 진행량은 음소거/volume 0 구간을 제외한 미디어 진척일 뿐, 장치의 실제 소리 출력을 인증하지 않습니다.
- **실제 사람 청취·학습 효과: NOT_MEASURED.** 도구 구현, AI 검토, 회귀 통과는 사람 연구 결과가 아닙니다. 세션 자기 선언은 신원 인증이 아닙니다.

내보낸 JSON을 새 디렉터리에 보관하고 아래 명령으로 재채점합니다. 입력 디렉터리가 없으면 실패하며, QA 파일을 사람 결과로 세지 않습니다.

```bash
python3 ops/summarize_human_study.py /path/to/submitted-json --report human-summary.json
```

## 실행과 기술 검사

ZIP을 풀고 `index.html`을 열면 됩니다. `file://`에서 inline WebVTT를 지원합니다. 로컬 HTTP 실행은:

```bash
node ops/serve_public.cjs . 4184
# http://127.0.0.1:4184/
python3 ops/verify_manifest.py
npm ci --ignore-scripts
npx playwright install chromium
npm run test:web
node ops/run_study_check.cjs
python3 -B ops/test_study_analyzer.py
```

검사는 실제 MP4 decode·파일 해시·자막 전체 word coverage·desktop/mobile/offline 재생, 이진 탐색 5,000개 property case, 합성 평가 UI 흐름을 대상으로 합니다. `.github/workflows/artifact-quality.yml`의 이름도 `technical-not-human-efficacy`입니다. **생성·기술·지각·학습 증거를 혼동하지 않습니다.**

## 제작·한계

- 영상: [explainroo](https://github.com/vincentsch/explainroo), 로컬 Kokoro 음성 합성 및 word timing, FFmpeg, Noto Sans CJK 글꼴.
- `skill/understanding-artifacts/`: 재사용 가능한 제작·감사 스킬과 사람 평가 지침.
- STE-inspired 글쓰기이며 정식 STE 인증이 아닙니다. LLM logits 및 상관/인과 수치는 합성 예제입니다.
- 기존 NEEDS WORK/PENDING 독립 보고서는 보존합니다. 이후 수정·재검토/부모 검증은 별도 보고서로 구분합니다.
- `baseline-evidence/` 및 이전 릴리스 문서는 과거 버전의 증거입니다. 현재 미디어는 각 `contract.json`, `caption-audit.json`, `MANIFEST.json`으로 식별합니다.
- 기존 SNS 게시 영상은 자막 개선 이전 버전일 수 있습니다. 이 릴리스의 `video/video-ko.mp4`가 현재 배포본입니다.

[전체 형식 대응표](FORMAT_COVERAGE.md) · [사람 평가 프로토콜](study/protocol.md)
