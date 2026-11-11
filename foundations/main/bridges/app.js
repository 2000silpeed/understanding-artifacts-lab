(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const state = { data: null, index: 0, selectedAnswer: null, checked: false, revealed: false, completed: new Set() };
  const pos = {
    '본관': [92, 190], '별관': [190, 100], '연구동': [305, 155], '서버실': [438, 73],
    '공장': [255, 315], '창고': [390, 286], '물류': [530, 230], '기숙사': [535, 410], '식당': [680, 410]
  };

  function edgeLabel(edge) {
    return `${state.data.nodes[edge[0]]}–${state.data.nodes[edge[1]]}`;
  }
  function check() { return state.data.checks[state.index]; }
  function isBridge(c) { return state.data.bridges.includes(c.edge); }
  function getChild(c) { return state.data.nodes[c.child]; }
  function getParent(c) { return state.data.nodes[c.parent]; }

  function renderGraph() {
    const edgeLayer = $('#edges');
    const nodeLayer = $('#nodes');
    edgeLayer.replaceChildren(); nodeLayer.replaceChildren();
    state.data.edges.forEach((edge, edgeId) => {
      const [a, b] = edge.map(i => state.data.nodes[i]);
      const [x1, y1] = pos[a], [x2, y2] = pos[b];
      const duplicated = edgeId === 8 || edgeId === 9;
      // Edges 8 and 9 have reversed endpoints: one consistent signed normal
      // produces opposite physical curves, rather than the same curve twice.
      const curve = duplicated ? -28 : 0;
      let d;
      if (curve) {
        const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
        const dx = x2 - x1, dy = y2 - y1, len = Math.max(1, Math.hypot(dx, dy));
        const cx = mx - (dy / len) * curve, cy = my + (dx / len) * curve;
        d = `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`;
      } else d = `M ${x1} ${y1} L ${x2} ${y2}`;
      const visible = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      visible.setAttribute('d', d); visible.classList.add('edge'); visible.dataset.edge = edgeId;
      if (edgeId === check().edge) visible.classList.add('selected');
      if (state.revealed && edgeId === check().edge && isBridge(check())) visible.classList.add('bridge-revealed');
      const hit = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      hit.setAttribute('d', d); hit.classList.add('edge-hit'); hit.dataset.edge = edgeId;
      hit.setAttribute('tabindex', '0'); hit.setAttribute('role', 'button'); hit.setAttribute('aria-label', `${edgeLabel(edge)} 간선 선택`);
      hit.addEventListener('click', () => selectEdge(edgeId));
      hit.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selectEdge(edgeId); } });
      edgeLayer.append(visible, hit);
    });
    state.data.nodes.forEach(name => {
      const [x, y] = pos[name];
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', x); circle.setAttribute('cy', y); circle.setAttribute('r', 28); circle.classList.add('node');
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', x); text.setAttribute('y', y); text.classList.add('node-label'); text.textContent = name;
      nodeLayer.append(circle, text);
    });
  }

  function renderEdgeList() {
    const list = $('#edge-list'); list.replaceChildren();
    state.data.edges.forEach((edge, edgeId) => {
      const button = document.createElement('button'); button.type = 'button'; button.className = 'edge-btn';
      button.dataset.edge = edgeId; button.setAttribute('aria-pressed', String(edgeId === check().edge));
      button.innerHTML = `<small>간선 ${edgeId}</small><strong>${edgeLabel(edge)}</strong>`;
      button.addEventListener('click', () => selectEdge(edgeId)); list.append(button);
    });
  }

  function renderTrace() {
    const body = $('#trace-table'); body.replaceChildren();
    const order = [...state.data.nodes.keys()].sort((a, b) => state.data.tin[a] - state.data.tin[b]);
    order.forEach(index => {
      const row = document.createElement('tr');
      row.innerHTML = `<td>${state.data.nodes[index]}</td><td>${state.data.tin[index]}</td><td>${state.data.low[index]}</td>`;
      body.append(row);
    });
  }

  function renderTask() {
    const c = check();
    $('#task-number').textContent = String(state.index + 1);
    $('#task-total').textContent = String(state.data.checks.length);
    $('#question').innerHTML = `<strong>${edgeLabel(state.data.edges[c.edge])}</strong>를 끊으면 그래프가 나뉠까요?`;
    $('#progress-bar').style.width = `${Math.round((state.completed.size / state.data.checks.length) * 100)}%`;
    $$('.edge-btn').forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.edge) === c.edge)));
    $$('.choice').forEach(button => { button.classList.remove('selected', 'correct'); button.disabled = state.checked; });
    $('#status').className = 'status';
    $('#status').textContent = state.completed.has(state.index) ? '이 과제는 완료했습니다. 이전·다음 과제로 이동할 수 있습니다.' : '선택한 뒤 예측 버튼을 누르면 결과를 확인할 수 있습니다.';
    $('#feedback').className = 'feedback'; $('#feedback').textContent = '';
    $('#reveal').hidden = !state.checked || state.selectedAnswer !== (isBridge(c) ? 'yes' : 'no') || state.revealed;
    $('#reveal-panel').hidden = !state.revealed;
    if (state.revealed) renderReveal();
    $('#previous').disabled = state.index === 0;
    $('#next').disabled = !state.completed.has(state.index) || state.index === state.data.checks.length - 1;
    renderGraph(); renderEdgeList();
    if (state.completed.size === state.data.checks.length) showCompletion();
  }

  function renderReveal() {
    const c = check();
    const bridgeText = isBridge(c) ? '단절선입니다.' : '단절선이 아닙니다.';
    const reason = isBridge(c) ? '크므로, 자식 쪽에서 부모 정점 또는 그 위로 돌아갈 길이 없습니다.' : '크지 않으므로, 아래쪽에서 부모 쪽으로 돌아가는 길이 있습니다.';
    $('#reveal-panel').innerHTML = `<strong>정답: ${bridgeText}</strong><p>트리 간선 <b>${getParent(c)} → ${getChild(c)}</b>에서 <b>low[${getChild(c)}] = ${c.low}</b>, <b>tin[${getParent(c)}] = ${c.tinParent}</b>입니다.</p><p><b>${c.low} &gt; ${c.tinParent}</b>가 ${reason}</p><p class="muted">이 수업의 규칙은 <b>low[v] &gt; tin[u]</b>입니다. 같은 값이면 단절선이 아닙니다. ${c.edge === 8 || c.edge === 9 ? '기숙사–식당의 두 케이블은 간선 번호로 구별합니다.' : ''}</p>`;
  }

  function selectEdge(edgeId) {
    const found = state.data.checks.findIndex(item => item.edge === edgeId);
    if (found < 0) return;
    state.index = found; state.selectedAnswer = null; state.checked = false; state.revealed = false;
    renderTask(); $('#question').scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function choose(answer, button) {
    if (state.checked) return;
    state.selectedAnswer = answer; $$('.choice').forEach(item => item.classList.remove('selected')); button.classList.add('selected');
    const right = answer === (isBridge(check()) ? 'yes' : 'no'); state.checked = true;
    if (right) {
      $('#status').className = 'status good'; $('#status').textContent = '예측이 맞았습니다. 이제 DFS 단계와 정답을 확인하세요.';
      $('#feedback').className = 'feedback good'; $('#feedback').textContent = '좋아요. 정답 보기에서 low와 tin을 비교해 보세요.';
      $('#reveal').hidden = false; $$('.choice').forEach(item => { if (item.dataset.answer === answer) item.classList.add('correct'); });
    } else {
      $('#status').className = 'status bad'; $('#status').textContent = '아직 맞지 않았어요. 정답은 공개하지 않았습니다.';
      $('#feedback').className = 'feedback bad'; $('#feedback').textContent = '다시 생각해 보고, 두 예측 중 하나를 다시 선택하세요.';
      state.checked = false; state.selectedAnswer = null; button.classList.remove('selected');
    }
    $('#next').disabled = true;
  }

  function reveal() {
    if (!state.checked || state.revealed) return;
    state.revealed = true; state.completed.add(state.index); renderTask(); $('#reveal-panel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  function showCompletion() {
    $('#status').className = 'status completion'; $('#status').textContent = '8개 과제를 모두 완료했습니다. 그래프를 다시 보거나 처음부터 다시 풀 수 있습니다.';
  }
  function reset() {
    state.index = 0; state.selectedAnswer = null; state.checked = false; state.revealed = false; state.completed.clear(); renderTask(); $('#task-heading').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function move(delta) {
    const next = state.index + delta; if (next < 0 || next >= state.data.checks.length) return;
    if (delta > 0 && !state.completed.has(state.index)) return;
    state.index = next; state.selectedAnswer = null; state.checked = false; state.revealed = false; renderTask(); $('#task-heading').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  async function init() {
    try {
      const response = await fetch('./data.json', { cache: 'no-store' });
      if (!response.ok) throw new Error(`data.json HTTP ${response.status}`);
      state.data = await response.json();
      $$('.choice').forEach(button => button.addEventListener('click', () => choose(button.dataset.answer, button)));
      $('#reveal').addEventListener('click', reveal); $('#reset').addEventListener('click', reset); $('#previous').addEventListener('click', () => move(-1)); $('#next').addEventListener('click', () => move(1));
      renderTrace(); renderTask();
    } catch (error) {
      $('#status').className = 'status bad'; $('#status').textContent = `실행 자료를 불러오지 못했습니다: ${error.message}`; console.error(error);
    }
  }
  init();
})();
