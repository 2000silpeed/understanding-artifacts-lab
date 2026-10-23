// 실습 HTML의 예제 그래프와 연습 문제. 적힌 정답(answer)은 check.cjs가 fw.js로 다시 계산해 맞는지 확인한다.
// BASE는 examples/graph.txt 와 글자 하나까지 같아야 한다 (test_source.py가 확인).
(function (root) {
  'use strict';
  const BASE = `# 영상 속 지도: 도시 4곳, 일방통행 도로 6개 (출발 도착 거리)
# 정점 이름은 공백 없이 한 단어. '#' 뒤는 주석.
4 6
A B 4
B C 7
C B 6
C D 3
D A 7
D C 3
`;
  const NEGATIVE = `# 음수 사이클 예: A -> B -> C -> A 를 한 바퀴 돌면 1 + (-1) + (-1) = -1
3 3
A B 1
B C -1
C A -1
`;
  const exercises = [
    {
      id: 'ex1', q: '경유지 C 차례에 D→B가 11에서 9로 바뀝니다. 바뀐 길을 정점 순서로 쓰면?',
      graph: BASE, ask: { type: 'path', from: 'D', to: 'B' }, answer: 'D → C → B (거리 9)',
    },
    {
      id: 'ex2', q: 'C→B 도로를 6에서 1로 바꾸면, D→B의 최단 거리와 길은?',
      graph: BASE.replace('C B 6', 'C B 1'), ask: { type: 'path', from: 'D', to: 'B' }, answer: 'D → C → B (거리 4)',
    },
    {
      id: 'ex3', q: '도로 A→D(거리 5)를 새로 놓으면(간선 7개), B→A의 최단 거리와 길은 바뀔까요?',
      graph: BASE.replace('4 6\n', '4 7\n') + 'A D 5\n', ask: { type: 'path', from: 'B', to: 'A' }, answer: 'B → C → D → A (거리 17)',
    },
    {
      id: 'ex4', q: '같은 A→D(거리 5)를 놓았을 때, A→D의 최단 거리와 길은?',
      graph: BASE.replace('4 6\n', '4 7\n') + 'A D 5\n', ask: { type: 'path', from: 'A', to: 'D' }, answer: 'A → D (거리 5)',
    },
    {
      id: 'ex5', q: 'D→A 도로를 7에서 -15로 바꾸면, 대각선에 무엇이 보일까요?',
      graph: BASE.replace('D A 7', 'D A -15'), ask: { type: 'neg' }, answer: '음수 사이클: A=-1, B=-1, C=-1, D=-2',
      note: '한 바퀴(A→B→C→D→A)는 4 + 7 + 3 - 15 = -1. 음수 사이클이 있으면 칸에 적힌 값 자체는 "최단 거리"가 아니고, 대각선이 0보다 작다는 사실만 믿을 수 있습니다.',
    },
    {
      id: 'ex6', q: '반복문 순서를 틀리게(k를 맨 안쪽에) 두면, 원래 지도에서 틀리는 칸은?',
      graph: BASE, ask: { type: 'wrong' }, answer: 'B→A: 정답 17, 실수한 결과 ∞',
    },
  ];

  /** 문제의 정답 문자열을 fw.js로 직접 계산한다. */
  function answer(FW, e) {
    const g = FW.parseGraph(e.graph), r = FW.report(g, e.id), cell = x => (x === null ? '∞' : String(x));
    if (e.ask.type === 'path') {
      const p = r.paths[e.ask.from + e.ask.to];
      return p === null ? '길 없음' : `${p.nodes.join(' → ')} (거리 ${p.dist})`;
    }
    if (e.ask.type === 'neg') {
      return r.negativeCycle.length ? '음수 사이클: ' + r.negativeCycle.map(v => `${v}=${r.final[g.names.indexOf(v)][g.names.indexOf(v)]}`).join(', ') : '음수 사이클 없음';
    }
    if (e.ask.type === 'wrong') {
      return r.wrongOrder.diff.length ? r.wrongOrder.diff.map(d => `${d.from}→${d.to}: 정답 ${cell(d.right)}, 실수한 결과 ${cell(d.wrong)}`).join(' / ') : '다른 칸 없음';
    }
    throw new Error('unknown ask ' + e.ask.type);
  }

  const api = { BASE, NEGATIVE, exercises, answer };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FW_EXERCISES = api;
})(typeof window !== 'undefined' ? window : this);
