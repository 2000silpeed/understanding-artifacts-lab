// 플로이드–워셜 실습용 계산 모듈. 브라우저(index.html)에서는 window.FW, Node에서는 require로 쓴다.
// examples/floyd_warshall.py 와 같은 규칙: 무한대는 null, 엄격히 더 짧을 때만 바꾸고, 바꿀 때 첫걸음 nxt[i][j] = nxt[i][k].
(function (root) {
  'use strict';

  /** "정점수 간선수" + "출발 도착 거리" 줄들 → { names, edges:[{u,v,w}] }. '#' 뒤는 주석. */
  function parseGraph(text) {
    const rows = text.split('\n').map(l => l.split('#')[0].trim()).filter(Boolean).map(l => l.split(/\s+/));
    if (!rows.length || rows[0].length < 2) throw new Error('첫 줄은 "정점수 간선수" 여야 합니다');
    const n = parseInt(rows[0][0], 10), m = parseInt(rows[0][1], 10);
    const names = [], edges = [];
    const id = x => { let i = names.indexOf(x); if (i < 0) { names.push(x); i = names.length - 1; } return i; };
    for (let e = 1; e <= m; e++) {
      const r = rows[e];
      if (!r || r.length < 3 || !/^-?\d+$/.test(r[2])) throw new Error(`${e + 1}번째 줄은 "출발 도착 거리(정수)" 여야 합니다`);
      edges.push({ u: id(r[0]), v: id(r[1]), w: parseInt(r[2], 10) });
    }
    if (names.length !== n || edges.length !== m) throw new Error(`정점 ${n}개·간선 ${m}개라고 했는데 정점 ${names.length}개·간선 ${edges.length}개를 읽었습니다`);
    return { names, edges };
  }

  const via = (d, i, k, j) => (d[i][k] === null || d[k][j] === null ? null : d[i][k] + d[k][j]);
  const shorter = (a, b) => a !== null && (b === null || a < b);
  const copy = t => t.map(r => r.slice());

  function initialTable(n, edges) {
    const dist = [], nxt = [];
    for (let i = 0; i < n; i++) { dist.push([]); nxt.push([]); for (let j = 0; j < n; j++) { dist[i].push(i === j ? 0 : null); nxt[i].push(i === j ? i : null); } }
    for (const { u, v, w } of edges) if (shorter(w, dist[u][v])) { dist[u][v] = w; nxt[u][v] = v; }
    return { dist, nxt };
  }

  /** 전체 실행: 경유지별 바뀐 칸, 최종 표, 첫걸음 표. */
  function run(g) {
    const n = g.names.length, { dist, nxt } = initialTable(n, g.edges), initial = copy(dist), rounds = [];
    for (let k = 0; k < n; k++) {
      const changes = [];
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
        const d = via(dist, i, k, j);
        if (shorter(d, dist[i][j])) {
          const route = path(nxt, i, k).slice(0, -1).concat(path(nxt, k, j)); // 바뀌는 순간의 실제 길
          changes.push({ i, j, old: dist[i][j], new: d, ik: dist[i][k], kj: dist[k][j], route });
          dist[i][j] = d; nxt[i][j] = nxt[i][k];
        }
      }
      rounds.push({ k, changes, after: copy(dist) });
    }
    const negative = [];
    for (let i = 0; i < n; i++) if (dist[i][i] !== null && dist[i][i] < 0) negative.push(i);
    return { n, initial, rounds, final: dist, nxt };
  }

  /** k 반복문을 맨 안쪽에 둔 (틀린) 순서의 최종 표. */
  function runWrongOrder(g) {
    const n = g.names.length, { dist } = initialTable(n, g.edges);
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) for (let k = 0; k < n; k++) {
      const d = via(dist, i, k, j);
      if (shorter(d, dist[i][j])) dist[i][j] = d;
    }
    return dist;
  }

  /** 한 칸씩 비교하는 실습용: step 번째 비교(0 ≤ step < n³) 직전의 표와 그 비교 내용. */
  function stepState(g, step) {
    const n = g.names.length, { dist, nxt } = initialTable(n, g.edges);
    let s = 0, last = null;
    for (let k = 0; k < n; k++) for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      if (s === step) {
        const d = via(dist, i, k, j);
        return { done: false, k, i, j, cur: dist[i][j], ik: dist[i][k], kj: dist[k][j], cand: d, better: shorter(d, dist[i][j]), dist: copy(dist), last };
      }
      const d = via(dist, i, k, j);
      if (shorter(d, dist[i][j])) { dist[i][j] = d; nxt[i][j] = nxt[i][k]; last = { k, i, j }; }
      s++;
    }
    return { done: true, dist: copy(dist), last };
  }

  function negativeCycle(dist) {
    const out = [];
    dist.forEach((r, i) => { if (r[i] !== null && r[i] < 0) out.push(i); });
    return out;
  }

  function path(nxt, i, j) {
    if (nxt[i][j] === null) return null;
    const out = [i];
    while (i !== j) { i = nxt[i][j]; out.push(i); }
    return out;
  }

  /** examples/floyd_warshall.py --json 과 같은 모양의 보고서 (테스트가 두 출력을 비교한다). */
  function report(g, source) {
    const N = g.names, r = run(g), neg = negativeCycle(r.final), wrong = runWrongOrder(g), paths = {}, diff = [];
    for (let i = 0; i < r.n; i++) for (let j = 0; j < r.n; j++) {
      if (i === j) continue;
      if (!neg.length) {
        const p = path(r.nxt, i, j);
        paths[N[i] + N[j]] = p === null ? null : { nodes: p.map(x => N[x]), dist: r.final[i][j] };
        if (wrong[i][j] !== r.final[i][j]) diff.push({ from: N[i], to: N[j], right: r.final[i][j], wrong: wrong[i][j] });
      }
    }
    return {
      source, names: N,
      edges: g.edges.map(e => ({ from: N[e.u], to: N[e.v], w: e.w })),
      initial: r.initial,
      rounds: r.rounds.map(rd => ({ k: N[rd.k], changes: rd.changes.map(c => ({ from: N[c.i], to: N[c.j], old: c.old, new: c.new, ik: c.ik, kj: c.kj, route: c.route.map(x => N[x]) })), after: rd.after })),
      final: r.final,
      next: r.nxt.map(row => row.map(x => (x === null ? null : N[x]))),
      negativeCycle: neg.map(i => N[i]),
      paths,
      wrongOrder: { final: wrong, diff },
    };
  }

  const api = { parseGraph, run, runWrongOrder, stepState, negativeCycle, path, report };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FW = api;
})(typeof window !== 'undefined' ? window : this);
