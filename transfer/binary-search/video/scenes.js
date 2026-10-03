const A = [2, 5, 8, 12, 16, 23, 38];
const X = [280, 510, 740, 970, 1200, 1430, 1660];
const Y = 560;

function title(s, text, o = {}) {
  return s.text(text, { x: s.safe.left, y: s.safe.top + 20, size: 62, align: 'left', ...o });
}
function arrayRow(s, states = {}, at = 0, out) {
  A.forEach((v, i) => {
    const state = states[i] || 'muted';
    const when = Array.isArray(at) ? at[i] : at;
    s.box(String(v), { id: `n${i}`, x: X[i], y: Y, w: 160, h: 110, size: 44, color: state, at: when, out, border: true });
    s.note(String(i), { x: X[i], y: Y + 100, size: 28, color: 'muted', at: when, out });
  });
}
function rangeLabel(s, left, right, at, color = 'accent', out) {
  s.text(`L=${left}   U=${right}`, { x: 960, y: 330, size: 46, font: 'mono', bg: true, border: color, at, out, color: 'ink' });
}
function pointer(s, id, label, at, color = 'accent', out) {
  s.arrow([X[id], 385], [X[id], 500], { label, labelColor: color, color, width: 5, at, out: typeof out === 'number' ? out - 0.6 : out, head: 'end' });
}
function footer(s, text, at) {
  s.note(text, { x: 960, y: 910, size: 34, color: 'muted', at });
}

export default {
  hook(s) {
    title(s, '이진 탐색', { at: 0, enter: 'none' });
    s.box('정렬됨', { x: 960, y: 600, w: 380, h: 120, icon: 'list-ordered', color: 'green', at: '#sorted', size: 48 });
    s.arrow([780, 600], [520, 600], { label: '정렬이면 절반 제외 가능', labelSize: 32, color: 'green', at: s.cue('order') });
    s.box('목표', { x: 1280, y: 600, w: 300, h: 120, icon: 'crosshair', color: 'yellow', at: 'comparison', size: 48 });
  },

  setup(s) {
    title(s, '정렬된 배열 하나', { at: 0, enter: 'none' });
    arrayRow(s, {0:'blue',1:'blue',2:'blue',3:'blue',4:'blue',5:'blue',6:'blue'}, [0, s.cue('two'), s.cue('eight', 1), s.cue('twelve'), s.cue('sixteen', 1), s.cue('twenty'), s.cue('thirty')]);
    s.text('목표 = 16', { x: 960, y: 250, size: 52, font: 'mono', bg: true, border: 'yellow', at: '#target' });
    footer(s, '값 7개 · 인덱스는 0부터', '#target');
  },

  first(s) {
    title(s, '가운데 값과 비교', { at: 0, enter: 'none' });
    arrayRow(s, {0:'blue',1:'blue',2:'blue',3:'yellow',4:'blue',5:'blue',6:'blue'}, 0);
    rangeLabel(s, 0, 6, '#range');
    pointer(s, 3, 'mid = 3', '#mid', 'yellow');
    s.text('array[mid] = 12', { x: 960, y: 240, size: 52, font: 'mono', bg: true, border: 'yellow', at: '#mid' });
    footer(s, 'mid = floor((L + U) / 2)', '#mid');
  },

  found(s) {
    title(s, '목표 16: 후보 구간 줄이기', { at: 0, enter: 'none' });
    arrayRow(s, {0:'red',1:'red',2:'red',3:'red',4:'blue',5:'blue',6:'blue'}, 0);
    rangeLabel(s, 0, 6, 0, 'accent', s.mark('discard-left') - 0.6);
    pointer(s, 3, 'mid = 3', 0, 'yellow', 7.464333333333336);
    s.text('12 < 16', { x: 960, y: 240, size: 52, font: 'mono', bg: true, border: 'green', at: s.cue('smaller'), out: 6.864333333333336 });
    s.text('인덱스 4..6 유지', { x: 960, y: 180, size: 42, font: 'mono', bg: true, border: 'accent', at: s.cue('keep', 1), out: 6.864333333333336 });
    s.note('다음 비교에서 구간을 다시 줄여요', { x: 960, y: 870, size: 34, color: 'accent', at: 7.0 });
    s.annotate('n0', { type: 'cross', color: 'red', at: '#discard-left' });
    s.annotate('n1', { type: 'cross', color: 'red', at: '#discard-left' });
    s.annotate('n2', { type: 'cross', color: 'red', at: '#discard-left' });
    s.annotate('n3', { type: 'cross', color: 'red', at: '#discard-left' });
    rangeLabel(s, 4, 6, '#discard-left', 'accent', 7.464333333333336);
    pointer(s, 5, 'mid = 5', 7.464333333333336, 'yellow', 11.495333333333335);
    s.text('23 > 16', { x: 960, y: 240, size: 52, font: 'mono', bg: true, border: 'red', at: 7.464333333333336, out: 10.895333333333335 });
    s.annotate('n5', { type: 'cross', color: 'red', at: 7.464333333333336 });
    s.annotate('n6', { type: 'cross', color: 'red', at: 7.464333333333336 });
    pointer(s,4,'mid = 4',11.495333333333335,'green');
    rangeLabel(s, 4, 4, 8.464333333333336);
    s.annotate('n4', { type: 'circle', color: 'green', at: 11.495333333333335 });
    s.text('찾음: 16, 인덱스 4', { x: 960, y: 240, size: 52, font: 'mono', bg: true, border: 'green', at: 11.495333333333335 });
    footer(s, '작으면 왼쪽 제외 · 크면 오른쪽 제외', 0);
  },

  missing(s) {
    title(s, '목표 7: 빈 구간이면 없습니다', { at: 0, enter: 'none' });
    arrayRow(s, {0:'blue',1:'blue',2:'blue',3:'red',4:'red',5:'red',6:'red'}, 0);
    rangeLabel(s, 0, 6, 0, 'accent', s.mark('missing') + 0.5);
    pointer(s, 3, '12 > 7', '#missing', 'red',s.cue('Five'));
    s.text('12 > 7  →  0..2 유지', { x: 960, y: 240, size: 48, font: 'mono', bg: true, border: 'red', at: '#missing', out: s.cue('Five') - 0.3 });
    s.annotate('n3', { type: 'cross', color: 'red', at: '#missing' });
    s.annotate('n4', { type: 'cross', color: 'red', at: '#missing' });
    s.annotate('n5', { type: 'cross', color: 'red', at: '#missing' });
    s.annotate('n6', { type: 'cross', color: 'red', at: '#missing' });
    rangeLabel(s, 0, 2, s.mark('missing') + 1.0, 'accent', s.cue('Five') + 0.5);
    pointer(s, 1, '5 < 7', s.cue('Five'), 'green',8.235333333333337);
    s.text('5 < 7  →  인덱스 2 유지', { x: 960, y: 240, size: 48, font: 'mono', bg: true, border: 'green', at: s.cue('Five'), out: 7.635333333333337 });
    s.annotate('n0', { type: 'cross', color: 'red', at: s.cue('Five') + 0.5 });
    s.annotate('n1', { type: 'cross', color: 'red', at: s.cue('Five') + 0.5 });
    rangeLabel(s, 2, 2, s.cue('Five') + 0.8,'accent',7.635333333333337);
    rangeLabel(s,2,1,8.235333333333337,'red');
    pointer(s, 2, '8 > 7', 8.235333333333337, 'red');
    s.text('L > U  ·  목표가 없습니다', { x: 960, y: 240, size: 52, font: 'mono', bg: true, border: 'red', at: 8.235333333333337 });
    footer(s, '0..6 → 0..2 → 2..2 → 빈 구간', 8.235333333333337);
  },

  bounds(s) {
    title(s, '경계 찾기는 다른 질문입니다', { at: 0, enter: 'none' });
    s.box('lower_bound', { x: 620, y: 480, w: 500, h: 150, icon: 'arrow-down-to-line', color: 'blue', at: '#bounds', size: 40 });
    s.text('첫 번째 값 ≥ target', { x: 620, y: 680, size: 42, at: '#bounds' });
    s.box('upper_bound', { x: 1300, y: 480, w: 500, h: 150, icon: 'arrow-up-to-line', color: 'purple', at: '#bounds', size: 40 });
    s.text('첫 번째 값 > target', { x: 1300, y: 680, size: 42, at: '#bounds' });
    s.arrow([900, 480], [1050, 480], { label: '서로 다른 경계', color: 'accent', at: s.cue('different') });
    s.text('같은 정렬 데이터, 다른 종료 조건', { x: 960, y: 820, size: 38, align: 'center', at: s.cue('different') });
    s.note('upper는 목표보다 큰 첫 번째 값을 찾아요', { x: 960, y: 870, size: 30, color: 'accent', at: 8.0 });
    footer(s, '한 번의 일치와 경계 위치는 같은 질문이 아니다', '#bounds');
  },

  outro(s) {
    title(s, '기억할 규칙', { at: 0, enter: 'none' });
    s.text('정렬 → 가운데 비교 → 절반 제외', { x: 960, y: 430, size: 62, font: 'mono', align: 'center', bg: true, border: 'green', at: '#summary' });
    s.icon('check-circle', { x: 960, y: 650, size: 150, color: 'green', at: '#summary', enter: 'pop' });
    s.note('먼저 정렬 확인', { x: 960, y: 820, size: 38, color: 'accent', at: s.cue('Check') });
    s.icon('list-ordered', { x: 960, y: 820, size: 90, color: 'accent', at: 6.5 });
    footer(s, '이진 탐색 전에 정렬 전제를 확인하세요.', '#summary');
  },
};
