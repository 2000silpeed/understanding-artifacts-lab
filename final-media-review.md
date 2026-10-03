# 최종 미디어 독립 검토

## 판정

**VERDICT: PASS — 차단 미디어 문제 없음.**

실제 공개 번들 `video/video.mp4`를 직접 probe하고, 전체 파일을 ffmpeg로 디코드한 뒤 선택 시점의 실제 프레임을 별도로 추출해 시각 검토했다. 기술적 미디어 품질과 공개 번들 계약 자산 관점에서 게시를 막을 결함은 확인되지 않았다.

## 실행한 명령과 실제 결과

번들 루트에서 다음을 실행했다.

```bash
ffprobe -v error -show_format -show_streams -of json video/video.mp4
```

- 종료 코드: `0`
- 컨테이너: MP4, `probe_score=100`
- 비디오: H.264 High, `1920x1080`, progressive, `yuv420p`, `30/1`, `2450` frames, `81.666667 s`
- 오디오: AAC-LC, stereo, `48000 Hz`, `81.666000 s`
- 파일 크기: `7,349,969` bytes

```bash
ffmpeg -hide_banner -loglevel error -i video/video.mp4 -f null -
```

- 종료 코드: `0`
- 전체 파일 디코드 오류 없음.

선택 실제 프레임 추출:

```bash
for t in 0 10 20 30 40 50 60 67.5 68.0 68.5 70 80 81.5; do
  ffmpeg -hide_banner -loglevel error -ss "$t" -i video/video.mp4 \
    -frames:v 1 -q:v 2 "<temporary-frame>"
done
```

- `13/13` 프레임 추출 성공.
- 각 프레임 실제 디코드 크기: `1920x1080`, RGB JPEG 검사 결과.
- `67.5`, `68.0`, `68.5`초를 포함해 샘플 장면을 검사했다.

오디오 기술 검사:

```bash
ffmpeg -hide_banner -nostats -i video/video.mp4 \
  -af astats=metadata=1:reset=0 -f null -
ffmpeg -hide_banner -nostats -i video/video.mp4 \
  -af ebur128=peak=true -f null -
```

- 두 명령 모두 종료 코드 `0`.
- `astats` overall peak: `-1.401840 dB`.
- `ebur128`: integrated `-14.0 LUFS`, LRA `2.2 LU`, true peak `-1.4 dBFS`.
- 디지털 풀스케일 초과/클리핑 증거 없음. 이는 청취 품질이나 사람의 음성 이해도를 인증하는 결과가 아니다.

## 실제 프레임 시각 검토

검토 대상은 실제 MP4에서 ffmpeg로 디코드한 선택 프레임 contact sheet와 `video/poster.png`였다.

- 검은 프레임, 깨진 디코드, 심한 프레임 clipping은 보이지 않았다.
- 주요 도식이 실제 영상에 나타난다: logits 후보/점수, softmax 확률 막대, temperature 변화, top-p 누적 질량/필터, sampling 구간, 최종 loop diagram.
- 한국어 제목·보조 문구·라벨의 glyph가 네모나 대체문자로 깨지지 않았다.
- poster의 한국어와 메인 도식도 화면 경계에 잘리지 않았다.
- 68.0초 프레임에서 `u = 0.82` marker가 `mat 0.731` 뒤의 파란 `floor 0.269` 구간 안에 위치한다.
- 같은 프레임에서 `선택: floor`가 한 줄로 표시되고, `The cat sat on the floor` context 업데이트도 한 줄로 보인다. 해당 라벨의 줄바꿈/겹침/clipping은 보이지 않았다.
- 67.5/68.5초 주변 프레임에서도 샘플 구간과 선택 표시가 안정적으로 유지된다.

이 검토는 픽셀·레이아웃·렌더링 관찰이며, 사람의 학습 이해도나 실제 음성 청취/의미 이해를 주장하지 않는다.

## 기존 QA 및 계약 교차 확인

`video/qa.json` 및 `test-report.json`을 읽었다.

- QA `issues=[]`, `blackSegments=[]`, `silences=[]`.
- QA 미디어 메타데이터는 실제 probe와 일치: `1920x1080`, H.264, AAC 48 kHz stereo, `81.67 s`.
- ASR match rate: `0.991`; 이는 음성-전사 일치에 대한 **proxy**이며 인간 청취/이해도 검사가 아니다.
- `test-report.json`: `passed=true`, parent actual MP4 browser playback `passed=true`, duration `81.666667`, dimensions `1920x1080`.
- `human_comprehension_test: not_performed`로 명시되어 있다. 이 제한은 차단 결함이 아니라 판정 범위의 비고다.

`bundle-audit.json`과 `contract.json`을 교차 확인했다.

- bundle audit `passed=true`.
- 계약 자산 전부 존재: `writing.md`, `diagram.svg`, `index.html`, `video/video.mp4`, `video/script.md`, `sources.md`, `test-report.json`.
- `test-report.json`의 계약/공개 보고서 경로는 상대 경로이며, `/home`, `/tmp`, `/workspace`, `/mnt`, `/Users` 형태의 machine-specific absolute path hit는 `0`.
- `bundle-audit.json`에도 같은 absolute path hit가 `0`.
- audit의 video stream/audio/positive duration/faststart checks 모두 통과.

## Blockers / non-blockers

### Blockers

- 없음.

### Non-blockers / 범위 제한

- 사람 대상 청취·이해도·학습 효과 실험은 수행하지 않았다. 공개 test report도 이를 명시한다.
- ASR `0.991`은 음성-전사 일치 proxy로만 해석한다.
- 시각 검토는 선택된 실제 프레임과 poster 중심이며, 인간의 의미 이해를 대신하지 않는다.

## 최종 결론

실제 공개 MP4는 probe·전체 디코드·선택 프레임 디코드·오디오 peak 검사·시각 검토를 모두 통과했다. 68초 샘플 장면의 `u=.82 -> floor` 위치와 단일행 라벨도 확인되었고, 한국어 glyph 및 주요 도식에 차단 수준의 렌더링 문제는 없다. **미디어 관점에서 게시 진행 가능하다.**
