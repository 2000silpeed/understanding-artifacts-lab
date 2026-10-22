// Bellman-Ford step engine for the practice page (practice/index.html) — films/bellman-ford-20261022.
// Same graph format and same trace as examples/bellman_ford.py (test_source.py runs this file in node and compares).
(function (root) {
  'use strict';

  /** 'V S A B …' + 'E from to weight' lines → { names, edges: [{u, v, w}] }. Throws with a Korean message. */
  function parseGraph(text) {
    let names = [];
    const edges = [];
    text.split(/\r?\n/).forEach((line, i) => {
      const p = line.trim().split(/\s+/);
      if (!p[0] || p[0].startsWith('#')) return;
      if (p[0] === 'V') names = p.slice(1);
      else if (p[0] === 'E') {
        const u = names.indexOf(p[1]), v = names.indexOf(p[2]), w = Number(p[3]);
        if (u < 0 || v < 0 || !Number.isInteger(w)) throw new Error(`${i + 1}번째 줄: 'E 출발 도착 정수가중치' 형식이고, 정점은 V 줄에 있어야 합니다`);
        edges.push({ u, v, w });
      } else throw new Error(`${i + 1}번째 줄: V 또는 E로 시작해야 합니다`);
    });
    if (names.length < 2) throw new Error('V 줄에 정점이 두 개 이상 있어야 합니다');
    return { names, edges };
  }

  const clean = x => (x === Infinity ? null : x);

  /** Every check of V - 1 rounds, then the check pass (which only looks). Source = vertex 0.
   *  negativeCycle means a negative cycle REACHABLE FROM THE SOURCE: an unreached vertex keeps Infinity and
   *  Infinity + w is still Infinity, so edges out of it never relax (same as bellman_ford.py / .cpp). */
  function trace(names, edges) {
    const n = names.length, dist = Array(n).fill(Infinity);
    dist[0] = 0;
    const rounds = [];
    for (let r = 1; r < n; r++) {
      const checks = edges.map(({ u, v, w }, k) => {
        const du = dist[u], before = dist[v], cand = du + w, updated = cand < before;
        if (updated) dist[v] = cand;
        return { edge: k, u, v, w, du: clean(du), before: clean(before), cand: clean(cand), updated };
      });
      rounds.push({ round: r, dist: dist.map(clean), checks });
    }
    const check = edges.map(({ u, v, w }, k) => {
      const cand = dist[u] + w;
      return { edge: k, u, v, w, du: clean(dist[u]), before: clean(dist[v]), cand: clean(cand), updated: cand < dist[v] };
    });
    const negativeCycle = check.some(c => c.updated);
    return { rounds, check, negativeCycle, dist: negativeCycle ? null : dist.map(clean) };
  }

  /** Flat list of steps for the page: every check of every round, then every check of the check pass. */
  function steps(t) {
    const out = [];
    t.rounds.forEach(r => r.checks.forEach(c => out.push({ phase: 'round', round: r.round, ...c })));
    t.check.forEach(c => out.push({ phase: 'check', round: t.rounds.length + 1, ...c }));
    return out;
  }

  const api = { parseGraph, trace, steps };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.BF = api;
})(this);
