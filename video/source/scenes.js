const C = {
  bg: '#172038',
  mint: '#66e3c4',
  blue: '#6faaff',
  amber: '#ffc66b',
  violet: '#bc9cff',
  white: '#f4f7ff',
  muted: '#9aa9c7',
  red: '#ff7385',
};

const tokenColors = [C.mint, C.blue, C.amber, C.violet];
const tokens = [' mat', ' floor', ' sofa', ' roof'];
const logits = ['2.0', '1.0', '0.3', '-0.4'];
const probs = ['60.9%', '22.4%', '11.1%', '5.5%'];

function label(s, text, x, y, opts = {}) {
  return s.text(text, { x, y, font: 'body', size: 38, color: C.white, ...opts });
}
function small(s, text, x, y, opts = {}) {
  return s.text(text, { x, y, font: 'body', size: 30, color: C.muted, ...opts });
}
function tokenBox(s, id, x, y, text, color, opts = {}) {
  return s.box(text, {
    id, x, y, w: 240, h: 126, size: 40, font: 'mono', color,
    fill: '#121c35', stroke: color, width: 3, at: 0, sfx: false, ...opts,
  });
}
function header(s, text, sub, at = 0) {
  s.text(text, { x: 120, y: 120, align: 'left', font: 'display', size: 72, color: C.white, at, enter: 'none' });
  if (sub) s.text(sub, { x: 120, y: 188, align: 'left', font: 'body', size: 30, color: C.muted, at, enter: 'fade' });
}
function contextStrip(s, at = 0, y = 500) {
  const xs = [230, 465, 700, 935, 1170];
  ['The', 'cat', 'sat', 'on', 'the'].forEach((t, i) => {
    s.box(t, { id: `ctx${i}`, x: xs[i], y, w: 190, h: 112, size: 38, color: i === 4 ? C.mint : C.blue, fill: '#121c35', stroke: i === 4 ? C.mint : C.blue, at, sfx: false });
  });
}
function candidateRow(s, y, at, values, opts = {}) {
  values.forEach((t, i) => tokenBox(s, `${opts.prefix || 't'}${i}`, 280 + i * 350, y, t, tokenColors[i], { at: Array.isArray(at) ? at[i] : at, ...opts }));
}

export default {
  hook(s) {
    s.bg(C.bg);
    header(s, '다음 토큰은 어떻게 정할까?', '한 번의 선택을 수식과 움직임으로 따라가기', 0);
    contextStrip(s, -1, 350);
    s.icon('brain', { id: 'brain', x: 960, y: 650, size: 190, color: C.violet, at: 0.2, bg: '#151b38', sfx: false });
    s.arrow('ctx4', 'brain', { at: s.mark('context') + 0.5, color: C.mint, width: 5, label: '문맥 읽기', labelColor: C.mint, labelSize: 30, bend: -0.15 });
    s.box('다음 후보', { id: 'next', x: 1450, y: 650, w: 300, h: 128, size: 42, color: C.amber, fill: '#211d2c', stroke: C.amber, at: s.cue('scores') - 0.3, sfx: false });
    s.arrow('brain', 'next', { at: s.cue('scores') - 0.1, color: C.amber, width: 5, label: '점수 → 선택', labelColor: C.amber, labelSize: 30 });
    s.text('토큰은 단어 · 단어 조각 · 문장부호일 수 있다', { x: 960, y: 970, align: 'center', font: 'body', size: 32, color: C.muted, at: s.cue('word', 2) });
  },

  logits(s) {
    s.bg(C.bg);
    header(s, '1. 로짓: 후보마다 점수', '로짓은 교육용으로 고른 값이며 실제 모델 출력이 아님', 0);
    contextStrip(s, -1, 300);
    s.arrow('ctx4', [960, 560], { at: s.mark('prompt'), color: C.mint, width: 5, label: '입력 문맥', labelColor: C.mint, labelSize: 30, bend: -0.08 });
    s.box('모델', { id: 'model', x: 960, y: 560, w: 240, h: 128, size: 44, color: C.violet, fill: '#151b38', stroke: C.violet, at: '#prompt', sfx: false });
    s.arrow('model', [1490, 560], { at: s.mark('scores'), color: C.blue, width: 5, label: '후보 점수', labelColor: C.blue, labelSize: 30 });
    const scoreCues = ['mat', 'floor', 'sofa', 'roof'].map(t => s.cue(t));
    candidateRow(s, 760, scoreCues, logits, { prefix: 'logit' });
    tokens.forEach((t, i) => small(s, t, 280 + i * 350, 700, { color: C.white, align: 'center', at: scoreCues[i] }));
    s.annotate('logit0', { type: 'highlight', color: C.mint, at: s.mark('scores') + 1.0 });
    s.text('가장 큰 로짓을 고르는 방식 = greedy', { x: 960, y: 955, font: 'body', size: 34, color: C.amber, align: 'center', at: s.cue('output') });
    s.text('illustrative values, not measured model output', { x: 960, y: 900, font: 'mono', size: 28, color: C.muted, align: 'center', at: s.cue('educational') });
  },

  softmax(s) {
    s.bg(C.bg);
    header(s, '2. 소프트맥스: 점수 → 확률', '네 후보를 같은 색으로 계속 추적한다', 0);
    s.text('pᵢ = exp((zᵢ − max z) / T) / Σⱼ exp((zⱼ − max z) / T)', { id: 'formula', x: 960, y: 300, font: 'mono', size: 40, color: C.mint, align: 'center', at: '#formula', bg: true, border: C.mint, padding: 24 });
    s.arrow([960, 390], [960, 520], { at: s.mark('formula') + 0.8, color: C.mint, width: 4, label: '정규화', labelColor: C.mint, labelSize: 30 });
    s.bars([
      { label: 'mat', value: 60.9, color: C.mint, at: s.cue('mat') },
      { label: 'floor', value: 22.4, color: C.blue, at: s.cue('floor') },
      { label: 'sofa', value: 11.1, color: C.amber, at: s.cue('sofa') },
      { label: 'roof', value: 5.5, color: C.violet, at: s.cue('roof') },
    ], { x: 960, y: 680, w: 1120, h: 190, max: 65, values: true, suffix: '%', labelSize: 34, valueSize: 34, at: s.cue('mat'), growDur: 0.8 });
    small(s, 'T = 1', 1560, 660, { color: C.mint, at: s.cue('mat') });

    s.text('합계 ≈ 99.9%  ·  반올림 표시', { x: 960, y: 1000, font: 'body', size: 30, color: C.muted, align: 'center', at: s.cue('roof') });
    s.text('확률은 이 네 후보 안에서 정규화한 교육용 예시', { x: 960, y: 900, font: 'body', size: 27, color: C.muted, align: 'center', at: s.cue('normalizes') });
  },

  temperature(s) {
    s.bg(C.bg);
    header(s, '3. 온도 T: 분포의 모양', '낮으면 뾰족하게, 높으면 평평하게', 0);
    s.text('T = 0.5', { x: 540, y: 315, font: 'display', size: 52, color: C.mint, align: 'center', at: '#sharp' });
    s.text('T = 2.0', { x: 1380, y: 315, font: 'display', size: 52, color: C.amber, align: 'center', at: '#flat' });
    s.bars([
      { label: 'mat', value: 85.0, color: C.mint, at: '#sharp' },
      { label: 'floor', value: 11.5, color: C.blue, at: '#sharp' },
      { label: 'sofa', value: 2.8, color: C.amber, at: '#sharp' },
      { label: 'roof', value: 0.7, color: C.violet, at: '#sharp' },
    ], { x: 540, y: 520, w: 700, h: 300, max: 100, values: true, suffix: '%', labelSize: 30, valueSize: 30, at: '#sharp', growDur: 0.7 });
    s.bars([
      { label: 'mat', value: 42.8, color: C.mint, at: '#flat' },
      { label: 'floor', value: 26.0, color: C.blue, at: '#flat' },
      { label: 'sofa', value: 18.3, color: C.amber, at: '#flat' },
      { label: 'roof', value: 12.9, color: C.violet, at: '#flat' },
    ], { x: 1380, y: 520, w: 700, h: 300, max: 100, values: true, suffix: '%', labelSize: 30, valueSize: 30, at: '#flat', growDur: 0.7 });
    s.arrow([900, 660], [1020, 660], { at: s.cue('higher') - 0.2, color: C.amber, width: 5, label: 'T 증가', labelColor: C.amber, labelSize: 32 });
    s.text('선택의 다양성', { x: 960, y: 925, font: 'body', size: 38, color: C.white, align: 'center', at: '#flat' });

    s.text('낮은 T는 상위 후보에 질량을 모은다', { x: 540, y: 900, font: 'body', size: 28, color: C.mint, align: 'center', at: s.cue('lower') });
    s.text('T는 분포의 모양을 바꾸지만 사실성을 보장하지 않는다', { x: 960, y: 995, font: 'body', size: 30, color: C.red, align: 'center', at: s.cue('correctness') });
  },

  topp(s) {
    s.bg(C.bg);
    header(s, '4. Top-p: 확률 질량으로 자르기', '토큰 하나의 고정 컷오프가 아니다', 0);
    s.text('내림차순 정렬', { x: 960, y: 290, font: 'body', size: 36, color: C.blue, align: 'center', at: s.cue('sorts') });
    const xs = [300, 650, 1000, 1350];
    ['mat 60.9%', 'floor 22.4%', 'sofa 11.1%', 'roof 5.5%'].forEach((t, i) => {
      s.box(t, { id: `p${i}`, x: xs[i], y: 470, w: 270, h: 122, size: 34, font: 'mono', color: tokenColors[i], fill: '#121c35', stroke: tokenColors[i], at: s.cue('probabilities') + i * 0.15, sfx: false });
    });
    s.arrow('p0', 'p1', { at: '#sort', color: C.muted, width: 3, head: 'end' });
    s.arrow('p1', 'p2', { at: '#sort', color: C.muted, width: 3, head: 'end' });
    s.arrow('p2', 'p3', { at: '#sort', color: C.muted, width: 3, head: 'end' });
    s.line([[165, 690], [785, 690]], { color: C.mint, width: 6, at: '#keep' });
    s.text('누적 질량', { x: 215, y: 745, font: 'body', size: 32, color: C.mint, at: '#keep' });
    s.text('0.609', { x: 420, y: 650, font: 'mono', size: 30, color: C.mint, at: '#keep' });
    s.text('0.833 ≥ 0.80', { x: 650, y: 650, font: 'mono', size: 36, color: C.amber, at: '#keep' });
    s.annotate('p1', { type: 'box', color: C.amber, at: '#keep', padding: 14 });
    s.box('유지: mat + floor', { x: 475, y: 855, w: 520, h: 120, size: 42, color: C.mint, fill: '#12322f', stroke: C.mint, at: '#keep', sfx: false });
    s.text('mat + floor  =  83.3%', { x: 960, y: 1005, font: 'mono', size: 34, color: C.white, align: 'center', at: '#keep' });
    s.annotate('p2', { type: 'cross', color: C.red, at: s.mark('keep') + 0.8 });
    s.annotate('p3', { type: 'cross', color: C.red, at: s.mark('keep') + 1.0 });
  },

  sample(s) {
    s.bg(C.bg);
    header(s, '5. 샘플링: 누적 구간에서 뽑기', '예시는 필터링 뒤 mat 73.1%, floor 26.9%', 0);
    s.text('0', { x: 240, y: 370, font: 'mono', size: 32, color: C.muted, at: -1 });
    s.text('1', { x: 1680, y: 370, font: 'mono', size: 32, color: C.muted, at: -1 });
    s.line([[280, 390], [1640, 390]], { color: C.muted, width: 6, at: -1 });
    s.line([[280, 390], [1274.23967, 390]], { color: C.mint, width: 12, at: 0.2 });
    s.line([[1274.23967, 390], [1640, 390]], { color: C.blue, width: 12, at: 0.3 });
    s.text('mat  0.731', { x: 760, y: 330, font: 'mono', size: 34, color: C.mint, align: 'center', at: 0.2 });
    s.text('floor  0.269', { x: 1550, y: 330, font: 'mono', size: 34, color: C.blue, align: 'center', at: 0.3 });
    s.circle({ id: 'u', x: 1395.2, y: 390, r: 25, color: C.amber, at: '#draw', sfx: false });
    s.text('u = 0.82', { x: 1395.2, y: 265, font: 'mono', size: 38, align: 'center', color: C.amber, at: '#draw' });
    s.arrow('u', [1395.2, 560], { at: s.mark('draw') + 0.7, color: C.amber, width: 5, label: '균등 추출', labelColor: C.amber, labelSize: 30 });
    s.box('선택: floor', { id: 'chosen', x: 1120, y: 680, w: 430, h: 120, size: 44, color: C.blue, fill: '#12243a', stroke: C.blue, at: s.mark('draw') + 1.1, sfx: false });
    s.arrow('chosen', [960, 850], { at: '#feedback', color: C.mint, width: 5, label: '문맥에 추가', labelColor: C.mint, labelSize: 30, bend: 0.2 });
    s.box('The cat sat on the floor', { x: 960, y: 900, w: 720, h: 112, size: 34, font: 'mono', color: C.mint, fill: '#122a31', stroke: C.mint, at: '#feedback', sfx: false });
    s.text('다음 단계에서는 모델이 점수를 다시 계산한다', { x: 960, y: 1020, font: 'body', size: 28, color: C.muted, align: 'center', at: '#feedback' });
  },

  outro(s) {
    s.bg(C.bg);
    header(s, '한 토큰의 루프', '문맥은 매 선택 뒤 다시 바뀐다', 0);
    const xs = [190, 530, 870, 1210, 1550];
    const chain = [
      ['문맥', 'layers', C.blue],
      ['로짓', 'chart-bar', C.violet],
      ['확률', 'percent', C.mint],
      ['필터', 'funnel', C.amber],
      ['샘플', 'shuffle', C.blue],
    ];
    chain.forEach(([t, icon, color], i) => {
      s.box(t, { id: `o${i}`, x: xs[i], y: 520, w: 250, h: 150, icon, iconSize: 56, size: 38, color, fill: '#121c35', stroke: color, at: i === 0 ? 0.1 : ['logits', 'probabilities', 'filtering', 'sampling'][i - 1], sfx: false });
    });
    for (let i = 0; i < chain.length - 1; i++) {
      s.arrow(`o${i}`, `o${i + 1}`, { at: i === 0 ? s.cue('logits') : [s.cue('probabilities'), s.cue('filtering'), s.cue('sampling')][i - 1], color: C.muted, width: 4, gap: 22 });
    }
    s.arrow('o4', 'o0', { at: s.cue('sampling') + 0.4, color: C.mint, width: 5, bend: 0.35, label: '다시 계산', labelColor: C.mint, labelSize: 30 });
    s.text('이 예시는 한 단계의 선택 규칙을 설명한다', { x: 960, y: 855, font: 'body', size: 38, color: C.white, align: 'center', at: '#caveat' });
    s.text('예측 확률 ≠ 현실의 진실', { x: 960, y: 930, font: 'display', size: 50, color: C.red, align: 'center', at: s.cue('verify') });
    s.text('illustrative toy values', { x: 960, y: 1000, font: 'mono', size: 28, color: C.muted, align: 'center', at: s.cue('truth') });

  },
};
