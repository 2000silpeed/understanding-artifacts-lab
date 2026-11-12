import {
  CANONICAL,
  buildTree,
  leafChain,
  levels,
  noLinkRangeSearch,
  rangeCount,
  rangeSearch,
} from './model.mjs';

const tree = buildTree(CANONICAL.insertOrder, CANONICAL.maxKeys);
const scenarios = [
  { lo: 20, hi: 40, choices: ['(7, 4)', '(7, 5)', '(0, 2)', '(14, 6)'], answer: 0, title: '강의 예제 범위', reason: 'L2에서 시작해 L2·L3·L4·L5를 읽습니다. L5에서 41이 hi=40보다 크므로 멈춥니다.' },
  { lo: 22, hi: 22, choices: ['(0, 1)', '(1, 1)', '(0, 2)', '(2, 3)'], answer: 2, title: '키 사이에 놓인 범위', reason: '22와 같은 키는 없지만, 시작점인 L2를 읽은 뒤 L3의 24에서 상한을 넘어 멈추므로 두 리프를 읽습니다.' },
  { lo: 0, hi: 100, choices: ['(14, 6)', '(14, 5)', '(13, 6)', '(0, 6)'], answer: 0, title: '전체 범위', reason: '가장 왼쪽 리프 L1부터 마지막 L6까지 링크를 따라가며 14개를 셉니다.' },
  { lo: 33, hi: 33, choices: ['(1, 1)', '(1, 2)', '(0, 2)', '(2, 2)'], answer: 1, title: '경계 키만 포함하기', reason: 'L4에서 33을 세고, 다음 L5에서 36이 상한을 넘는 것을 확인한 뒤 멈춥니다. 끝 경계를 포함하므로 33은 셉니다.' },
];

const state = { index: 0, selected: null, finished: false, completed: new Set() };
const app = document.querySelector('#app');
const fontStatus = document.querySelector('#font-status');

function fmt(values) { return values.length ? values.join(', ') : '없음'; }
function nodeLabel(node) { return `${node.name}[${node.keys.join(',')}]`; }
function resultFor(scenario) {
  return { count: rangeCount(tree, scenario.lo, scenario.hi), search: rangeSearch(tree, scenario.lo, scenario.hi), noLinks: noLinkRangeSearch(tree, scenario.lo, scenario.hi) };
}
function renderTree(walked = []) {
  const treeLevels = levels(tree);
  const levelHtml = treeLevels.map((nodes, depth) => `
    <div class="level-wrap">
      <div class="level-label">${depth === 0 ? '뿌리' : `레벨 ${depth}`}</div>
      <div class="level">${nodes.map((node) => `<div class="node"><span class="node-name">${node.name}${node.children === null ? ' · 리프' : ' · 안내'}</span><span class="node-keys">${node.keys.join(', ') || '비어 있음'}</span></div>`).join('')}</div>
    </div>`).join('');
  const chainHtml = leafChain(tree).map((node, index) => `<span class="chain-node ${walked.includes(node.name) ? 'walked' : ''}"><span>${node.name}: ${node.keys.join(', ')}</span><small>${walked.includes(node.name) ? '읽음 · ' : ''}${index < 5 ? `다음 → L${index + 2}` : '마지막'}</small></span>`).join('');
  return `<div class="tree-board" aria-label="B+ 트리 구조">
    <details class="full-tree"><summary>트리 전체 구조 펼치기</summary>${levelHtml}<p>R의 왼쪽은 I1, 오른쪽은 I2입니다. I1의 자식은 L1·L2·L3, I2의 자식은 L4·L5·L6입니다.</p></details>
    <div class="mini-label">리프 연결(next) · L1부터 L6 순서로 읽어요</div>
    <div class="chain" aria-label="리프 연결 순서">${chainHtml}</div>
  </div>`;
}
function feedback(scenario, result, selected) {
  const correct = selected === scenario.answer;
  const count = result.count;
  const answerText = scenario.choices[scenario.answer];
  return `<div class="feedback ${correct ? 'correct' : 'incorrect'}" role="status" aria-live="polite">
    <h3>${correct ? '정답입니다.' : '아직 수정할 점이 있어요.'}</h3>
    <p class="result-line">실제 결과: (${count.count}, ${count.leavesRead}) · 읽은 리프: ${result.search.walked.join(' → ')}</p>
    <p>${correct ? scenario.reason : `정답은 ${answerText}입니다. ${scenario.reason}`}</p>
    <p>링크를 쓸 때 이동 수는 ${result.search.moves}번이고, 링크가 없다면 ${result.noLinks.moves}번입니다.</p>
  </div>`;
}
function finishHtml() {
  const completedCount = state.completed.size;
  const title = completedCount === scenarios.length ? '실습을 끝까지 완료했습니다.' : '여기서 실습을 종료했습니다.';
  return `<section class="card finish" aria-labelledby="finish-title">
    <p class="eyebrow">학습 결과</p>
    <h2 id="finish-title">${title}</h2>
    <p>정답을 확인한 과제 ${completedCount}개 / ${scenarios.length}개</p>
    <div class="finish-summary">
      <div class="summary-item"><strong>${completedCount}</strong>확인한 과제</div>
      <div class="summary-item"><strong>${scenarios.length}</strong>전체 과제</div>
      <div class="summary-item"><strong>next</strong>리프 이동 방식</div>
    </div>
    <p>핵심은 시작 리프까지 한 번만 내려가고, 이후에는 <code>next</code> 링크로 오른쪽을 걷는 것입니다. hi보다 큰 키를 만나면 그 리프까지 읽은 뒤 즉시 멈춥니다.</p>
    <button class="btn btn-primary" id="restart" type="button">처음부터 다시 하기</button>
  </section>`;
}
function render() {
  if (state.finished) {
    app.innerHTML = finishHtml();
    document.querySelector('#restart').addEventListener('click', () => { state.index = 0; state.selected = null; state.completed.clear(); state.finished = false; render(); focusMain(); });
    focusMain();
    return;
  }
  const scenario = scenarios[state.index];
  const result = resultFor(scenario);
  const answered = state.selected !== null;
  const progress = Math.round(((state.index + (answered ? 1 : 0)) / scenarios.length) * 100);
  const options = scenario.choices.map((choice, i) => `<label class="option"><input type="radio" name="prediction" value="${i}" ${state.selected === i ? 'checked' : ''}><span class="option-text">${choice}</span></label>`).join('');
  app.innerHTML = `<div class="toolbar" aria-label="실습 조작">
      <div class="progress" aria-label="진행률">과제 ${state.index + 1} / ${scenarios.length}<div class="progress-track"><span class="progress-fill" style="width:${progress}%"></span></div></div>
      <button class="btn" id="previous" type="button" ${state.index === 0 ? 'disabled' : ''}>이전</button>
      <button class="btn" id="reset" type="button">처음부터</button>
      <button class="btn btn-danger" id="end" type="button">종료</button>
    </div>
    <section class="card task" aria-labelledby="task-title">
      <div class="lesson-grid">
        <div>
          <p class="eyebrow">${scenario.title}</p>
          <h2 id="task-title">[${scenario.lo}, ${scenario.hi}]에서 무엇을 셀까요?</h2>
          <p>아래 트리는 강의에서 실행한 같은 14개 키의 구조입니다. 먼저 답을 고르고, 그 다음에 노란 리프 이동과 이유를 확인하세요.</p>
          ${renderTree(answered ? result.search.walked : [])}
        </div>
        <div>
          <div class="query-row" aria-label="현재 입력값">
            <div class="query"><span>lo</span><output>${scenario.lo}</output></div>
            <div class="query"><span>hi</span><output>${scenario.hi}</output></div>
            <div class="query"><span>노드당 최대 키 수</span><output>${CANONICAL.maxKeys}</output></div>
          </div>
          <fieldset>
            <legend>예상 결과 (개수, 읽은 리프 수)</legend>
            <div class="options">${options}</div>
          </fieldset>
          ${answered ? feedback(scenario, result, state.selected) : '<p class="status" role="status">아직 정답을 공개하지 않았습니다. 하나를 선택하면 결과와 이유가 바로 나타납니다.</p>'}
          <div class="next-row">
            <p class="next-hint">${answered ? '확인했으면 다음 과제로 가세요.' : '선택 후 결과가 나타납니다.'}</p>
            <button class="btn btn-primary" id="next" type="button" ${answered ? '' : 'disabled'}>${state.index === scenarios.length - 1 ? '완주 화면' : '다음 과제'}</button>
          </div>
        </div>
      </div>
    </section>
    <section class="card note" aria-labelledby="meaning-title">
      <h2 id="meaning-title">이 결과의 의미</h2>
      <p><strong>내부 노드:</strong> 실제 데이터 키는 모두 리프에 있고, 내부 노드에는 길 안내용 구분 키가 있습니다. 구분 키와 같으면 오른쪽 자식으로 갑니다. 예를 들어 20은 R → I1 → L2로 내려갑니다.</p>
      <p><strong>리프 링크:</strong> 범위의 시작점만 찾은 뒤 L2 → L3처럼 오른쪽 링크를 따라가므로, 부모로 되돌아가 다음 자식을 다시 찾지 않습니다.</p>
      <p><strong>포함 범위:</strong> lo와 hi를 모두 포함합니다. 키가 hi보다 커지면 그 키가 있는 리프까지 읽은 것으로 세고 멈춥니다.</p>
      <p><strong>이 예제의 범위:</strong> 중복 키를 넣지 않는 교육용 구현입니다. 이동 수는 노드 사이 이동 횟수이지 실행 시간이나 디스크 읽기 횟수가 아닙니다. 실제 데이터베이스의 페이지 크기·캐시·동시성 처리는 여기서 모델링하지 않습니다.</p>
    </section>`;
  document.querySelectorAll('input[name="prediction"]').forEach((input) => input.addEventListener('change', (event) => {
    state.selected = Number(event.target.value);
    if (!state.completed.has(state.index)) {
      state.completed.add(state.index);
    }
    render();
    document.querySelector(`input[name="prediction"][value="${state.selected}"]`)?.focus({ preventScroll: true });
  }));
  document.querySelector('#next').addEventListener('click', () => {
    if (state.index === scenarios.length - 1) state.finished = true;
    else { state.index += 1; state.selected = null; }
    render();
    focusMain();
  });
  document.querySelector('#previous').addEventListener('click', () => {
    if (state.index > 0) { state.index -= 1; state.selected = null; }
    render();
    focusMain();
  });
  document.querySelector('#reset').addEventListener('click', () => { state.index = 0; state.selected = null; state.completed.clear(); state.finished = false; render(); focusMain(); });
  document.querySelector('#end').addEventListener('click', () => { state.finished = true; render(); focusMain(); });
}
function focusMain() { document.querySelector('#main')?.focus({ preventScroll: true }); }

fontStatus.textContent = document.fonts ? '한글 글꼴을 확인하는 중…' : '브라우저 기본 글꼴을 사용합니다.';
if (document.fonts) {
  document.fonts.ready.then(() => {
    const loaded = [...document.fonts].some((font) => font.status === 'loaded' && font.family.includes('Noto Sans CJK KR Local'));
    fontStatus.textContent = loaded ? '로컬 Noto Sans CJK KR 글꼴이 적용되었습니다.' : '로컬 글꼴을 확인하지 못해 시스템 한글 글꼴을 사용합니다.';
  });
}
render();

export { CANONICAL, scenarios, tree, resultFor };
