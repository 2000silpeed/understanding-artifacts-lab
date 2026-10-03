# 독립 검토 지적 사항의 부모 수정·재검증

원 보고서 `subtitle-independent-review.md`는 수정 전 자막/검증기의 NEEDS WORK 판정이다. 원 보고서는 보존하고 수정 사실·새 기술 검사 결과는 따로 기록한다. 아래는 부모의 후속 검증이며, 독립 검토자가 최종 영상을 인증했다고 주장하지 않는다.

- P1 cue15: `최소 집합` 대신 `확률이 큰 후보부터 차례로` + `누적 확률이 p 이상이 되는 최소 개수`로 정렬된 최소 접두 집합을 명시했다.
- P1 cue16: `필터 전 확률의 합` 대신 `두 후보의 원래 확률 합`으로 mat/floor만의 유지 질량 83.3%임을 명시했다.
- P2 cue4: `네 후보 토큰의 예시 로짓`으로 토큰/설명용 입력이라는 의미를 명시했다.
- P2 cue24: `이 확률`을 원문의 `estimates`에 대응하는 `이 추정값`으로 고쳤다.
- P1 provenance: 선언된 timeline/original SHA를 실제 파일과 비교한다. final burned-in/master/original 아티팩트를 SHA에 연결하고 final/master binding이 빠지면 실패시킨다. 변조/누락/올바른 binding 회귀를 추가했다. 영상은 번역 수정 후 재렌더하고, 렌더 후 다시 봉인하여 새 최종 해시와 비교한다.
- 자막 구조 PASS ≠ 번역/사람 청취/사람 학습 인증이라는 한계를 유지한다. 새 HTML은 실제 TextTrack 25개, seek, 재생 시간 진행, 키보드 토글, file:// 및 데스크톱/390px 모바일에서 검사한다. HTTP 테스트 서버는 Range 206을 지원한다.

최종 실행 결과는 `test-report.json`, `caption-audit.json`, `caption-player-check.json`, `bundle-audit.json`으로 확인한다. 이 문서만으로 실행 완료/독립 재인증을 주장하지 않는다.
