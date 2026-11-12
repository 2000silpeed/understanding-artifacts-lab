"""실습 — 강의 16: 리프 링크로 범위 안 키 개수 세기.

목표: range_count(tree, lo, hi)를 완성한다.
  - 반환: (개수, 읽은 리프 수)
  - 결과 리스트를 만들지 말고 개수만 센다.
  - 뿌리에서 시작 리프까지 한 번만 내려가고, 그다음은 leaf.next 링크로만 이동한다.
  - 키가 hi를 넘으면 바로 멈춘다(그 리프까지는 읽은 리프로 센다).

트리 구조(../code/python/bplustree.py):
  node.leaf      리프면 True
  node.keys      정렬된 키 목록
  node.children  내부 노드의 자식 목록 (len(keys) + 1개)
  node.next      리프의 오른쪽 이웃 리프 (마지막 리프는 None)
  내부 노드에서 내려갈 자식: children[bisect_right(keys, lo)]

확인: python3 practice/check_practice.py practice/exercise_range_count.py
"""
from bisect import bisect_right  # noqa: F401  (내려갈 자식을 고를 때 쓴다)


def range_count(tree, lo, hi):
    node = tree.root
    # TODO 1) lo로 시작 리프까지 내려가기
    # TODO 2) leaf.next를 따라 걸으며 lo 이상 hi 이하인 키 세기, 읽은 리프 수 세기
    # TODO 3) hi보다 큰 키를 만나면 바로 (개수, 읽은 리프 수) 돌려주기
    raise NotImplementedError('range_count를 완성하세요')
