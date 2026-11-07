# 강한 연결 요소 — 시나리오

- 출처: 자체 작성 대본 `script/lesson.json`(화면 줄·내레이션의 단일 원천). 화면·자막은 그 원문 그대로 쓰고, TTS 입력만 `script/pronunciation.json`으로 한글 읽기로 바꾼다.
- 형식: 내레이션 강의(한국어 AI 기본기 교육, 트랙 algorithms · 공개 번호 13). 목적: 설명.
- 순서(요청): **핵심 개념 요약 → 구체적인 사용 상황 → 본 강의**. 제목 카드(약 15초)는 요약 앞에서 주제 문장 하나만 말한다.
- 길이: 추정 약 8분 14초(`script/timing-estimate.json`, 음절 기반) → 샷리스트는 90 BPM 마디로 올림해 768박 = 8분 32초. **녹음 후 실측으로 다시 정한다.** 30fps. 마스터 16:9, 재배치 9:16.
- 지속 액터: 서비스 8개 호출 그래프(`examples/fixtures/services.graph`). 사용 상황에서 세우고, 정의·응축·1단계·2단계·결과에서 같은 좌표로 다시 쓴다.
- 예제 값: 모두 실제 실행 결과(`examples/output/services.python.txt` = `services.cpp.txt`)에서 온다. 측정값이 아니라 예제 그래프의 결정적 계산이므로 `예시 값` 표기 대상이 아니다. 단, 사용 상황의 '서비스 호출 그래프'는 가상의 시스템이라는 점을 화면 구석에 `예시 그래프`로 표시한다.

## 예제 그래프(실행 결과 요약)

| 항목 | 값 |
|---|---|
| 정점·간선 | 8개 · 11개 (주문 결제 포인트 회원 인증 알림 검색 추천) |
| 1단계 끝난 순서 | 포인트 인증 회원 알림 결제 주문 추천 검색 |
| 2단계 살펴볼 순서 | 검색 추천 주문 결제 알림 회원 인증 포인트 (실제 출발점: 검색 주문 알림 회원) |
| 묶음 | 1 {검색 추천} · 2 {주문 포인트 결제} · 3 {알림} · 4 {회원 인증} |
| 응축 간선 | 1→2 · 2→3 · 2→4 · 3→4 (위상 순서 1 2 3 4) |
| 배포 순서(호출받는 쪽 먼저) | 4 3 2 1 = 회원·인증 → 알림 → 주문·결제·포인트 → 검색·추천 |
| Tarjan | {인증 회원} {알림} {포인트 결제 주문} {추천 검색} — 같은 분할, 역위상 순서 |

## 비트 시트

시간은 추정(녹음 전). 동사는 `tokens.motion.verbs`.

| # | 장면 id | 구간 | 핵심 화면 | 추정 길이 | 레시피 | 내용 동사 |
|---|---|---|---|---|---|---|
| 0 | title | 열기 | 제목 + 부제, 그래프 실루엣 | 15s | cerulean | reveal |
| 1 | summary | 핵심 개념 요약 | 카드 4장: 최대 묶음 / 딱 한 묶음 / 점으로 줄이면 사이클 없음 / DFS 두 번 O(V+E) | 35s | orange | reveal, split, transform |
| 2 | usage | 사용 상황 | 서비스 그래프 → 순환 고리 → 덩어리 4개 → 배포 순서 띠 → 다른 쓰임 칩 | 61s | cerulean | connect, loop, contain, split, append |
| 3 | define | 본 강의 1 | u·v 정의 → 회원·인증(같은 묶음) vs 알림·회원(다른 묶음) → 세 성질 → 분할 | 47s | orange | connect, conceal, split |
| 4 | naive | 본 강의 2 | 정점마다 탐색 → 8×8 도달 표 → V × (V+E) → 목표: 두 번 | 28s | cerulean | advance, reveal |
| 5 | condense | 본 강의 3 | 묶음 → 점 4개(응축) → 사이클 없음·출구 → 회원에서 DFS 멈춤 vs 주문에서 샘 | 46s | orange | transform, contain, overflow |
| 6 | pass1 | 본 강의 4 | '끝남' 정의 → DFS 추적, 번호 배지 1–8, 아래 띠 | 44s | cerulean | connect, append, select |
| 7 | why | 본 강의 5 | 묶음별 마지막 끝 8·6·4·3 → 입구 {검색 추천} → 화살표 전부 뒤집기 | 36s | orange | compare, select, transform |
| 8 | pass2 | 본 강의 6 | 뒤집힌 그래프 + 뒤집힌 띠 → 묶음 1·2·3·4가 차례로 | 58s | cerulean | transform, connect, contain |
| 9 | result | 본 강의 7 | 응축 점 1→4 정렬 → 거꾸로 읽어 배포 띠 | 26s | orange | transform, append |
| 10 | code | 본 강의 8 | Python 코드 카드(줄 하이라이트) → Python·C++17 터미널 나란히, diff 없음 | 39s | cerulean | select, reveal, compare |
| 11 | cost | 본 강의 9 | O(V+E) → Tarjan low/index → 결과 순서 반대 | 35s | orange | mix, split, compare |
| 12 | recap | 정리 | 정리 4줄 + 예제 실행 명령, 읽기 홀드 ≥ 3s | 27s | cerulean | reveal |

샷 단위 계획은 [`shots.json`](shots.json)(→ [`shotlist.md`](shotlist.md), shotlint PASS). 연출·레이아웃은 [`direction.md`](direction.md).

## 체크

- [x] 순서: 요약 → 사용 상황 → 본 강의 (화면과 내레이션 모두)
- [x] 화면 숫자·순서·묶음이 실제 실행 결과와 같다 (`examples/check_lesson_sync.py` PASS)
- [x] 레시피 교대 (cerulean ↔ orange)
- [x] 마지막 홀드 ≥ 3초 (C13-02, 16박 ≈ 10.7초 중 홀드)
- [ ] 화면 줄 2줄 이내 — 스틸 게이트에서 확인(렌더 전 단계라 미확인). 넘치면 카피를 줄인다
- [ ] 녹음 후 장면 길이·샷 시작을 단어 시각으로 다시 맞춘다
