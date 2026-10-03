# caption-v1 최종 독립 검토

- 검토 시각: `2026-10-03T15:29:56+09:00`
- 검토 대상: `.`
- 검토 방식: 현재 파일을 읽기 전용으로 대조·재실행하고, 최종 `video/video-ko.mp4`에서 프레임을 직접 추출해 시각 검토함. 임시 재검증 산출물은 `/tmp/caption-review/`에만 생성함.

## 최종 판정

**원 보고서의 NEEDS WORK 지적(필수 P1 2건, 권장 P2 2건, provenance hash P1)은 현재 artifact 기준으로 닫혔다.**

- 자막/정렬/포장/해시/플레이어/최종 MP4 디코드: **기술적으로 PASS**.
- 25개 English source ↔ Korean subtitle semantic 대조: **25/25 의미상 일치, 차단 번역 결함 없음**.
- 최종 burned-in MP4 직접 프레임 검토: **검토한 25개 cue midpoint에서 가시적 clipping, 한글 깨짐, 다이어그램 overlap 없음**.
- 실제 영어 음성에 대한 `faster-whisper tiny.en` ASR: **기계 proxy로 25개 발화 절이 순서대로 관측됨**. ASR은 사람 청취가 아니며, 이 결과로 audible sync/번역 품질을 인증하지 않음.
- **실제 human listening 인증: NOT RUN.** 사람 청취를 했다고 주장할 근거가 없으므로, 이 한계가 남아 있는 동안 “사람이 청취·동기 확인했다”, “human study 통과” 또는 측정된 학습효과를 주장하면 안 됨.

따라서 좁은 의미의 **caption-v1 기술 릴리스 판정은 PASS**, 사람 청취/사람 학습 연구를 포함한 일반적 publication 인증은 **NOT CERTIFIED**이다.

## 1. 원 보고서 지적사항의 closure 판정

| 원 지적 | 현재 상태 | 독립 판정 |
|---|---|---|
| P1 cue 15: top-p의 prefix/순서 의미 약화 | `top-p는 확률이 큰 후보부터 차례로 남겨요. 누적 확률이 p 이상이 되는 최소 개수만 남겨요.` | **CLOSED.** 높은 확률 순서와 누적 threshold를 모두 명시한다. “prefix”라는 영어 단어는 없지만 의미가 보존된다. |
| P1 cue 16: 83.3%의 질량 주체가 모호함 | `두 후보의 원래 확률 합은 83.3%예요.` | **CLOSED.** mat+floor 두 후보의 원래 확률 질량임을 명시한다. |
| P2 cue 4: `floor token`/illustrative 표현 약화 | `네 후보 토큰의 예시 로짓은 mat 2.0, floor 1.0,` | **CLOSED FOR RELEASE.** 네 후보/토큰/예시용 logits 의미가 보존된다. `floor` 레이블은 화면과 앞뒤 문맥에서 token 후보로 명확하다. 남은 것은 문체 압축이지 의미 차단 결함이 아니다. |
| P2 cue 24: `estimates`가 `확률`로 좁아짐 | `이 추정값은 다음 토큰을 예측해요.` | **CLOSED.** source의 estimates를 직접 반영한다. |
| P1 provenance/media hash 미검증 | final video, master, original의 실제 SHA-256을 alignment binding과 대조; 변조 fixture에서 gate가 실패함 | **CLOSED.** 아래 해시 및 tamper probe 참조. |

## 2. 25개 English source ↔ Korean 번역 대조

대조 기준은 `video/caption-alignment.json`의 25 cues를 source 문장 단위로 읽고, 숫자·조건·부정·caveat·용어·인과관계를 비교한 것이다. 기계 word coverage는 별도로 재검증했다.

| Cue | English source 핵심 | Korean 대조 결과 |
|---:|---|---|
| 1 | context를 읽고 next-token 후보에 점수를 매겨 하나를 선택 | **일치.** `문맥을 읽은 LLM`, 후보 scoring, 하나 선택이 모두 보존됨. |
| 2 | token은 단어/단어 일부/문장부호일 수 있음 | **일치.** 세 가지 가능성을 모두 보존함. |
| 3 | toy context: “The cat sat on the” | **일치.** 예제 문맥과 영어 문자열 보존. |
| 4 | 네 개의 illustrative logits: mat 2.0, floor token 1.0 | **일치.** `네 후보 토큰의 예시 로짓`으로 illustrative/candidate 의미가 유지됨. |
| 5 | sofa 0.3, roof minus 0.4 | **일치.** `sofa 0.3, roof -0.4`와 수치/부호가 일치. |
| 6 | educational values, not measured model output | **일치.** `교육용 수치이며 실제 모델의 측정값이 아니`라고 명시. |
| 7 | logits become probabilities through softmax | **일치.** softmax가 logits를 확률로 바꾼다고 표현. |
| 8 | shifted scores를 exponentiate하고 normalize | **일치.** 점수 이동, 지수값, 합이 1이 되도록 정규화가 모두 반영됨. |
| 9 | temperature 1에서 mat 60.9% | **일치.** 조건과 수치가 그대로 보존됨. |
| 10 | floor 22.4%, sofa 11.1%, roof 5.5% | **일치.** 세 레이블과 수치가 모두 보존됨. |
| 11 | temperature가 distribution shape를 바꿈 | **일치.** 확률 분포 모양을 바꾼다고 표현. |
| 12 | lower temperature sharpens | **일치.** 낮으면 분포가 뾰족해진다고 표현. |
| 13 | higher temperature flattens | **일치.** 높으면 분포가 평평해진다고 표현. |
| 14 | variety를 바꾸며 correctness가 아님 | **일치.** 다양성 변화와 정확성 보장 아님을 모두 보존. |
| 15 | probabilities를 정렬하고 mass에 도달하는 smallest prefix 유지 | **일치.** 확률이 큰 후보부터 차례로, 누적 p 이상이 되는 최소 개수라는 순서·threshold 의미가 보존됨. |
| 16 | p=.80에서 mat/floor가 83.3%를 retain | **일치.** 두 후보의 원래 확률 합이 83.3%라고 명시해 주체가 더 선명함. |
| 17 | 두 후보는 남고 나머지는 제거 | **일치.** `두 후보만 남고, 나머지는 제외`와 일치. |
| 18 | this is a mass rule | **일치.** `기준은 누적 확률 질량`으로 교육적 의미가 보존됨. |
| 19 | cumulative probability 구간에서 uniform number를 draw | **일치.** 누적 확률 구간과 균등 난수 모두 보존. |
| 20 | u=.82이므로 filtered intervals에서 floor 선택 | **일치.** `u=0.82`, 필터링된 구간, floor 선택이 모두 보존됨. |
| 21 | 선택 token을 context에 붙이고 다음 step을 recompute | **일치.** 문맥에 붙임과 다음 단계 score 재계산을 모두 명시. |
| 22 | toy는 한 단계만 보여줌 | **일치.** caveat가 그대로 보존됨. |
| 23 | loop: context → logits → probabilities → filtering → sampling | **일치.** 다섯 단계와 반복 순서가 그대로 표시됨. |
| 24 | estimates predict a next token | **일치.** `이 추정값은 다음 토큰을 예측`으로 수정됨. |
| 25 | real-world truth를 검증하지 않음 | **일치.** 현실의 사실 여부를 검증하지 않는다는 부정/caveat 보존. |

**번역 결론:** 25개 모두 source의 핵심 명제·수치·조건·부정·제한을 보존한다. cue 4의 `floor token`은 한국어 문장에서 레이블로 압축됐지만 `네 후보 토큰`과 화면의 후보 box가 함께 있어 의미상 차단 결함은 아니다.

## 3. 자막·word timing 기술 재검증

실제 실행 결과:

1. `python3 -B skill/understanding-artifacts/scripts/test_audit_captions.py`
   - exit **0**, **31 tests OK**.
2. `python3 -B skill/understanding-artifacts/scripts/test_audit_bundle.py --report /tmp/final-independent-bundle-regression.json`
   - exit **0**, **16 tests OK**.
3. `python3 -B skill/understanding-artifacts/scripts/audit_captions.py . --report /tmp/final-independent-caption-audit.json`
   - exit **0**, `passed=true`.
   - alignment/SRT/VTT **25/25**.
   - timed source words **189/189**, duplicate assignment **0**.
   - max start drift **0 s**, max CPS **15.918**, minimum exposure **1.05 s**.
   - timeline SHA 및 source-word exactness, 순서/비중첩, Hangul, sidecar 일치 PASS.
4. `python3 -B skill/understanding-artifacts/scripts/audit_bundle.py . --report /tmp/final-independent-bundle-audit.json`
   - exit **0**, required subtitle/media/package gate PASS.
5. 임시 출력 경로로 복사한 player verifier를 실제 재실행
   - `node /tmp/caption-review/verify_caption_player.cjs`, exit **0**.
   - HTTP desktop/mobile 및 `file://` offline 모두 track `ko`, 25 cues, 1920×1080, duration 79.333333, playback advancement, 25/25 seek match, keyboard toggle, no overflow, console errors 0, external requests 0.
   - 원본 `caption-player-check.json`은 수정하지 않았고, 재실행 결과는 `/tmp/caption-review/re-run-caption-player-check.json`에만 기록됨.

이 결과는 **final cached ASR/alignment timeline에 대한 기술적 word timing**을 검증한다. 오디오를 사람이 듣고 실제 단어 경계를 판정한 결과는 아니다.

## 4. 최종 MP4 직접 decode 및 vision 검토

최종 `video/video-ko.mp4`에서 각 cue의 midpoint를 직접 `ffmpeg -ss ... -frames:v 1`로 추출했다.

- 25개 1920×1080 PNG: `/tmp/caption-review/frames/cue-01...cue-25...png`
- 25개 contact sheet: `/tmp/caption-review/final-caption-cue-mid-contact-sheet.jpg`
- 전체 MP4 decode: `ffmpeg -v error -i video/video-ko.mp4 -f null -`, exit **0**.
- 확인한 직접 프레임: cue 1, cue 15, cue 16 및 25개 전체 contact sheet.

실제 보이는 결과:

- 25개 midpoint 모두 burned-in 한국어 cue가 표시된다.
- cue 15의 `top-p` 두 줄과 cue 16의 `p=0.80`/`83.3%` 두 줄이 실제로 렌더되고, 숫자/한글이 잘리지 않는다.
- cue 1, 15, 16에서 자막은 하단 전용 band에 있고, 상단 제목/후보 box/확률 도식과 겹치지 않는다.
- contact sheet의 모든 cue에서 한글 glyph 깨짐, 빈 caption, 프레임 전체 검정, 눈에 띄는 clipping은 보이지 않는다.
- 자막은 화면 하단에 가깝지만 관찰한 1920×1080 frame 안에 완전히 들어온다. 이 검토는 390px 실제 player의 CSS overflow도 별도 player test로 통과시켰다.

`blackdetect`를 기본 `pix_th=0.98`로 실행하면 navy dark-theme 배경 전체를 검정으로 오인해 `0–79.3 s`를 검정으로 보고한다. 이는 이 영상에 유효한 blank-frame 판정이 아니다. `pix_th=0.10`에서는 black interval이 없었고, 직접 추출한 실제 frame에는 도식과 자막이 보였다. 따라서 blackdetect 기본값을 근거로 빈 영상이라고 판정하지 않았다.

## 5. audio 및 ASR proxy

실행한 명령:

- `ffmpeg -i video/video-ko.mp4 -vn -ac 1 -ar 16000 -y /tmp/caption-review/final-audio.wav`
- `faster_whisper` `tiny.en`, CPU/int8, 실제 추출 audio에 대해 transcribe, exit **0**, 약 15.51 s.

ASR proxy 결과:

- language `en`, **25 segments**.
- 25개 English clause가 모두 순서대로 관측됐다.
- 작은 모델의 인식 오차는 확인됨: `mat`→`matte`, `top-p`→`top piece`, `next token`→`ex token` 등. 이는 ASR 오인식이며 Korean subtitle 자체의 누락으로 해석하지 않았다.
- ASR segment는 넓은 구간 단위이며 cached word timeline과 동일한 word boundary 인증이 아니다.

오디오 기술 지표:

- final: H.264, yuv420p, 1920×1080, video/container duration `79.333333 s`.
- audio: AAC LC, stereo, 48 kHz, stream duration `79.286000 s`.
- duration 차이 `0.047333 s`; caption 마지막 cue는 `76.925638 s`로 audio/video tail 안에 있다.
- loudnorm proxy: input I `-14.04 LUFS`, true peak `-1.39 dBFS` (기존 `caption-audio-check.json` 및 재실행 결과와 일치).
- master와 final의 audio packet MD5를 `ffmpeg -map 0:a:0 -c copy -f md5 -`로 비교: 양쪽 모두 `MD5=b24bdbb1d393291eb70cb41dd5844777`.

**엄격한 한계:** 위 loudness, full decode, packet hash, ASR는 사람 청취가 아니다. 실제 human listening/audible synchronization review는 수행하지 않았다.

## 6. SHA-256 identity 및 변조 회귀

현재 실제 SHA-256:

```text
video/video-ko.mp4       7b1fae31dd339424ce61dc7887d8fbe574f1ae5e72d06d7aef69e648091a78f6
video/video-master.mp4   e11284adc357033578a70309c58084bbf7aca4a6c5d5e50da84ac95183a29a72
video/video.mp4          ffd24dfe12c596eb797b36d8cfe10274c80f95e7fa340185b75eb9fe11189506
video/timeline.json      adc58c95f42839c79676f0e41fa43db31254dec2133b0fc1890cfa1f25bc8d76
video/caption-alignment.json
dcbea8fa6ae29b8251728283d8ae1912cb326cad8677ca01028f76be93bd7a30
```

alignment에 선언된 media bindings는 final/master/original 세 hash와 실제 값이 모두 일치했다. 또한 임시 복사본에서 다음 변조를 실제로 실행했다.

- final `video-ko.mp4` 한 바이트 변조 → `audit_captions.py` exit **1**, `media_binding_hash_video` 실패.
- 선언된 final hash를 64개 zero로 변조 → `audit_captions.py` exit **1**, `media_binding_hash_video` 실패.
- 동일 fixture에서 bundle gate도 exit **1**.

따라서 원 보고서의 “선언 hash가 실제 파일과 비교되지 않는다”는 현재 버전의 P1은 **닫혔다**.

## 7. 남은 제한과 release wording

남은 항목은 현재 caption-v1 기술 검증의 결함이라기보다 검증 범위의 한계다.

- **Human listening:** not run. ASR/vision/loudness를 human listening으로 표기하지 말 것.
- **Human learning/retention study:** not run. 이해도 향상·학습효과·사람 비교 우위를 주장하지 말 것.
- **Fresh-topic transfer / unrelated-domain four-format study:** not run. 이 단일 next-token case의 기술 검증을 일반적 교육효과로 일반화하지 말 것.
- `contract.json`의 `test_coverage` 일부가 `not_run`으로 보수적으로 남아 있다. 이를 사람 연구 PASS로 덮어쓰지 않았다.

### 결론

**수정 전 독립 보고서의 NEEDS WORK 원인은 현 caption-v1에서 모두 닫혔다.** 현재 남은 blocker는 “기술적 자막 artifact가 작동하지 않는다”가 아니라, 실제 사람 청취/번역·학습 연구를 수행하지 않았다는 명시적 범위 제한이다. 공개 문구는 다음 수준을 넘지 않아야 한다:

> “25개 source-word alignment, SRT/VTT, final burned-in frame, media hash, full decode, player seek/toggle/offline 및 ASR proxy를 검증했다. 사람 청취 인증과 사람 학습 연구는 수행하지 않았다.”

이 보고서 외에는 어떤 workspace 파일도 수정하지 않았다.
