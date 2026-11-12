(() => {
  "use strict";

  function buildAdj(n, edges) {
    const adj = Array.from({ length: n }, () => []);
    edges.forEach(([a, b], edge) => {
      adj[a].push([b, edge]);
      if (a !== b) adj[b].push([a, edge]);
    });
    adj.forEach((row) => row.sort((x, y) => x[0] - y[0] || x[1] - y[1]));
    return adj;
  }

  function componentsWithout(n, edges, removed) {
    const adj = buildAdj(n, edges);
    const seen = Array(n).fill(false);
    const groups = [];
    for (let start = 0; start < n; start += 1) {
      if (start === removed || seen[start]) continue;
      seen[start] = true;
      const stack = [start];
      const group = [];
      while (stack.length) {
        const u = stack.pop();
        group.push(u);
        for (const [v] of adj[u]) {
          if (v !== removed && !seen[v]) {
            seen[v] = true;
            stack.push(v);
          }
        }
      }
      groups.push(group.sort((a, b) => a - b));
    }
    return groups.sort((a, b) => a[0] - b[0]);
  }

  // Same deterministic disc/low semantics as canonical code/articulation.py.
  function computeGraph(n, edges) {
    const adj = buildAdj(n, edges);
    const disc = Array(n).fill(-1);
    const low = Array(n).fill(0);
    const parent = Array(n).fill(-1);
    const cut = new Set();
    const bridges = [];
    const tree = [];
    const back = [];
    const checks = [];
    const roots = [];
    let timer = 0;

    for (let root = 0; root < n; root += 1) {
      if (disc[root] !== -1) continue;
      const rootRecord = { root, children: 0 };
      roots.push(rootRecord);
      disc[root] = low[root] = timer;
      timer += 1;
      const stack = [[root, -1, 0]];
      while (stack.length) {
        const top = stack[stack.length - 1];
        const [u, parentEdge] = top;
        if (top[2] < adj[u].length) {
          const [v, edge] = adj[u][top[2]];
          top[2] += 1;
          if (edge === parentEdge) continue;
          if (disc[v] !== -1) {
            if (disc[v] < disc[u]) back.push({ from: u, to: v, edge });
            low[u] = Math.min(low[u], disc[v]);
          } else {
            if (u === root) rootRecord.children += 1;
            parent[v] = u;
            disc[v] = low[v] = timer;
            timer += 1;
            tree.push({ from: u, to: v, edge });
            stack.push([v, edge, 0]);
          }
        } else {
          stack.pop();
          if (stack.length) {
            const p = stack[stack.length - 1][0];
            low[p] = Math.min(low[p], low[u]);
            const parentOfP = parent[p];
            const isRoot = parentOfP === -1;
            const check = { parent: p, child: u, lowChild: low[u], discParent: disc[p], cut: false };
            if (!isRoot) {
              check.cut = low[u] >= disc[p];
              if (check.cut) cut.add(p);
            }
            checks.push(check);
            if (low[u] > disc[p]) bridges.push([Math.min(p, u), Math.max(p, u)]);
          }
        }
      }
      if (rootRecord.children >= 2) cut.add(root);
    }
    return {
      disc,
      low,
      parent,
      points: Array.from(cut).sort((a, b) => a - b),
      bridges: bridges.sort((a, b) => a[0] - b[0] || a[1] - b[1]),
      tree,
      back,
      checks,
      roots,
    };
  }

  function sameJson(a, b) {
    return JSON.stringify(a) === JSON.stringify(b);
  }

  const api = { buildAdj, componentsWithout, computeGraph, sameJson };
  globalThis.ArticulationCompanion = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;

  if (typeof document === "undefined") return;

  const $ = (id) => document.getElementById(id);
  const state = { data: null, fixture: null, vertex: 0, prediction: null, revealed: false };
  const els = {
    fixture: $("fixture"), vertex: $("vertex"), graph: $("graph-summary"), edges: $("edges"),
    discLow: $("disc-low"), removal: $("removal"), answer: $("answer"), feedback: $("feedback"),
    explain: $("explain"), reset: $("reset"), predictYes: $("predict-yes"), predictNo: $("predict-no"),
    status: $("status"), complexity: $("complexity"), sourceLink: $("source-link"),
  };

  function list(values) { return values.length ? values.join(", ") : "없음"; }
  function edgeLabel(edge) { return `${edge[0]}–${edge[1]}`; }
  function fixtureName() { return state.fixture ? state.fixture.name : ""; }

  function renderGraph() {
    const f = state.fixture;
    els.graph.textContent = `${f.name} · 정점 ${f.n}개 · 간선 ${f.edges.length}개`;
    els.edges.innerHTML = f.edges.map((edge, i) => `<span class="edge" data-edge="${i}">${edgeLabel(edge)}</span>`).join("");
    els.vertex.innerHTML = Array.from({ length: f.n }, (_, i) => `<option value="${i}">정점 ${i}</option>`).join("");
    els.vertex.value = String(state.vertex);
    els.complexity.textContent = state.data.filmData.cost
      ? `실행 기록: 본편 네트워크의 완전 탐색 ${state.data.filmData.cost.network.brute}회 · DFS ${state.data.filmData.cost.network.dfs}회 인접 간선 확인`
      : "비용 수치는 제공된 실행 기록을 사용합니다.";
  }

  function renderHidden() {
    els.discLow.textContent = "정점을 예측한 뒤 설명 보기를 누르면 disc·low가 나타납니다.";
    els.removal.textContent = "정답은 아직 숨겨져 있습니다.";
    els.answer.textContent = "";
    els.feedback.textContent = "";
    els.feedback.className = "feedback";
    els.status.textContent = `현재 그래프: ${fixtureName()} · 정점 ${state.vertex}`;
    els.explain.disabled = false;
    els.predictYes.disabled = false;
    els.predictNo.disabled = false;
  }

  function renderRevealed() {
    const f = state.fixture;
    const result = computeGraph(f.n, f.edges);
    const groups = componentsWithout(f.n, f.edges, state.vertex);
    const isPoint = result.points.includes(state.vertex);
    els.discLow.innerHTML = `<b>disc</b>: ${result.disc.join(" ")}<br><b>low</b>: ${result.low.join(" ")}`;
    els.removal.innerHTML = `정점 ${state.vertex} 제거 후 <b>${groups.length}개</b> 그룹: ${groups.map((g) => `[${g.join(", ")}]`).join(" · ")}`;
    els.answer.innerHTML = `<b>${state.vertex}</b>은(는) ${isPoint ? "단절점입니다" : "단절점이 아닙니다"}. · 전체 단절점: [${list(result.points)}]<br>다리: ${result.bridges.length ? result.bridges.map(edgeLabel).join(", ") : "없음"}`;
    const matches = state.prediction !== null && state.prediction === isPoint;
    els.feedback.textContent = state.prediction === null ? "설명을 확인했습니다. 다음에는 먼저 예측해 보세요." : (matches ? "예측이 맞았습니다." : "예측과 달랐습니다. low와 제거 결과를 다시 비교해 보세요.");
    els.feedback.className = `feedback ${state.prediction === null ? "neutral" : (matches ? "good" : "retry")}`;
    els.status.textContent = `확인 완료: ${fixtureName()} · 정점 ${state.vertex}`;
  }

  function reset() {
    state.prediction = null;
    state.revealed = false;
    renderHidden();
  }

  function setPrediction(value) {
    state.prediction = value;
    els.feedback.textContent = `예측: 정점 ${state.vertex}은(는) ${value ? "단절점이다" : "단절점이 아니다"}. 이제 설명 보기를 눌러 확인하세요.`;
    els.feedback.className = "feedback neutral";
  }

  function selectFixture(name) {
    state.fixture = state.data.fixtures.find((f) => f.name === name) || state.data.fixtures[0];
    state.vertex = Math.min(state.vertex, state.fixture.n - 1);
    renderGraph();
    reset();
  }

  els.predictYes.addEventListener("click", () => setPrediction(true));
  els.predictNo.addEventListener("click", () => setPrediction(false));
  els.explain.addEventListener("click", () => { state.revealed = true; renderRevealed(); });
  els.reset.addEventListener("click", reset);
  els.fixture.addEventListener("change", (event) => selectFixture(event.target.value));
  els.vertex.addEventListener("change", (event) => { state.vertex = Number(event.target.value); reset(); });

  fetch("data/companion-data.json")
    .then((response) => { if (!response.ok) throw new Error(`data ${response.status}`); return response.json(); })
    .then((data) => {
      state.data = data;
      els.fixture.innerHTML = data.fixtures.map((f) => `<option value="${f.name}">${f.name}</option>`).join("");
      state.fixture = data.fixtures[0];
      renderGraph();
      reset();
      els.sourceLink.href = "source/articulation-points-15-source.zip";
    })
    .catch((error) => {
      els.status.textContent = `데이터를 불러오지 못했습니다: ${error.message}`;
      els.status.className = "status error";
    });
})();
