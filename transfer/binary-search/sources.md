# 출처와 근거 기록

## S1. Python 공식 문서: `bisect`

- URL: https://docs.python.org/3/library/bisect.html
- 조회: 2026-10-03, HTTP 200, 49,902 bytes, 최종 URL 동일.
- 관련 구절: `bisect` 모듈은 정렬된 순서를 유지하기 위한 삽입 위치를 찾으며, `bisect_left`는 정렬을 유지하는 `x`의 삽입 위치를 찾고 이미 같은 값이 있으면 그 값들보다 왼쪽을 반환한다. `bisect_right`는 같은 값들 뒤의 삽입 위치를 반환한다.
- 사용한 주장: 정렬 전제가 필요하다는 점, `lower`/`upper` 경계를 삽입 위치로 해석하는 점.
- 주의: Python 문서의 API는 일반적으로 반열린 구간과 삽입 위치를 설명한다. 이 자료의 애니메이션은 학습을 위해 `L..U` 양끝을 모두 포함하는 구간과 `mid=floor((L+U)/2)`를 사용한다.

## S2. cppreference: `std::lower_bound`

- URL: https://en.cppreference.com/w/cpp/algorithm/lower_bound
- 조회: 2026-10-03, HTTP 200, 194,403 bytes, 최종 URL 동일.
- 관련 구절: `lower_bound`는 정렬된 범위에서 값보다 앞서지 않는 첫 원소를 찾고, 범위가 해당 비교식에 대해 분할되어 있지 않으면 동작이 정의되지 않는다.
- 사용한 주장: `lower_bound`는 “첫 번째 not less” 경계라는 점과 정렬/분할 전제.

## S3. cppreference: `std::upper_bound`

- URL: https://en.cppreference.com/w/cpp/algorithm/upper_bound
- 조회: 2026-10-03, HTTP 200, 194,649 bytes, 최종 URL 동일.
- 관련 구절: `upper_bound`는 값보다 뒤에 정렬된 첫 원소, 즉 값보다 큰 첫 원소를 찾는다.
- 사용한 주장: `upper_bound`는 “첫 번째 greater” 경계라는 점.

## 자체 계산 및 실행 근거

- 예시 배열 `[2, 5, 8, 12, 16, 23, 38]`와 목표 `16`, `7`은 사용자 요청의 교육용 고정 입력이다.
- 범위 변화, `mid` 값, found/not-found 결과는 `index.html`의 순수 `binarySearch` 함수와 `tests/test-binary-search.js`에서 재계산한다.
- `O(log n)`은 매 반복마다 포함 후보 구간이 절반 이하로 줄어드는 이 구현의 알고리즘적 분석이다. 사람의 학습 효과나 이해도 측정 결과를 뜻하지 않는다.

## 출처의 한계

이 묶음은 알고리즘 정의와 구현 검증을 위한 출처 기록이다. 사람을 대상으로 한 학습 실험, 번역 품질에 대한 독립적인 언어 평가, 실제 사용 환경에서의 성능 측정은 수행하지 않았다.
