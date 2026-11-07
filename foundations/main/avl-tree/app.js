(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory;
  else {
    var api = factory(root.AVL_DATA);
    root.AVLCompanion = api;
    root.addEventListener('DOMContentLoaded', function () { api.mount(root.AVL_DATA); });
  }
})(typeof window === 'undefined' ? globalThis : window, function (data) {
  'use strict';

  function createModel(payload) {
    if (!payload || !Array.isArray(payload.steps)) throw new Error('canonical trace is required');
    var index = 0, revealed = false;
    return {
      current: function () { return payload.steps[index]; },
      index: function () { return index; },
      revealed: function () { return revealed; },
      answer: function () { revealed = true; },
      next: function () { if (revealed && index < payload.steps.length - 1) { index += 1; revealed = false; } },
      previous: function () { if (index > 0) { index -= 1; revealed = false; } },
      reset: function () { index = 0; revealed = false; },
      end: function () { index = payload.steps.length - 1; revealed = false; },
      done: function () { return index === payload.steps.length - 1 && revealed; },
      length: function () { return payload.steps.length; }
    };
  }

  function mount(payload) {
    var $ = function (id) { return document.getElementById(id); };
    var model = createModel(payload), answer = $('answer'), message = $('message'), selected = null;
    var choices = ['균형', 'LL', 'LR', 'RR', 'RL'];
    var colors = { ink: '#123649', muted: '#4f626d', accent: '#a6420a', ok: '#1c6e43', bg: '#fbf5ee', line: '#c9bfb0' };
    function esc(v) { return String(v).replace(/[&<>"']/g, function (c) { return ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' })[c]; }); }
    function nodeList(snapshot) {
      return Object.keys(snapshot.nodes).map(function (k) { var n = snapshot.nodes[k]; return { key: +k, x: 50 + (n.d * 0), y: 0, n: n }; });
    }
    function draw(snapshot, title) {
      var nodes = nodeList(snapshot), ordered = [];
      function walk(key) { if (key === null) return; var n = snapshot.nodes[String(key)]; walk(n.l); ordered.push(key); walk(n.r); }
      walk(snapshot.root);
      var pos = {}, width = 360, maxDepth = 0;
      ordered.forEach(function (key, i) { var n = snapshot.nodes[String(key)]; maxDepth = Math.max(maxDepth, n.d); pos[key] = { x: 26 + i * (308 / Math.max(1, ordered.length - 1)), y: 28 + n.d * 60 }; });
      if (ordered.length === 1) pos[ordered[0]].x = width / 2;
      var lines = '';
      nodes.forEach(function (x) { ['l', 'r'].forEach(function (side) { if (x.n[side] !== null) { var a = pos[x.key], b = pos[x.n[side]]; lines += '<line x1="' + a.x + '" y1="' + a.y + '" x2="' + b.x + '" y2="' + b.y + '" stroke="' + colors.line + '" stroke-width="2"/>'; } }); });
      var circles = nodes.map(function (x) { var p = pos[x.key]; return '<g><circle cx="' + p.x + '" cy="' + p.y + '" r="17" fill="#fff" stroke="' + colors.ink + '" stroke-width="2"/><text x="' + p.x + '" y="' + (p.y + 5) + '" text-anchor="middle" font-size="14" font-weight="800" fill="' + colors.ink + '">' + esc(x.key) + '</text></g>'; }).join('');
      return '<div class="tree-title">' + esc(title) + '</div><svg viewBox="0 0 360 ' + (maxDepth * 60 + 60) + '" role="img" aria-label="' + esc(title) + '">' + lines + circles + '</svg>';
    }
    function rotationText(s) { return s.rotations.length ? s.rotations.map(function (r) { return (r.dir === 'left' ? '왼쪽' : '오른쪽') + ' 회전(' + r.at + ')'; }).join(' → ') : '회전 없음'; }
    function render() {
      var s = model.current(), revealed = model.revealed(), summary = payload.summary;
      $('progress').textContent = (model.index() + 1) + ' / ' + model.length();
      $('key').textContent = s.key;
      $('path').textContent = s.path.length ? s.path.join(' → ') : '—';
      $('balancePath').textContent = s.pathBf.map(function (x) { return x[0] + ' (' + (x[1] > 0 ? '+' : '') + x[1] + ')'; }).join(' · ') || '—';
      $('prompt').textContent = revealed ? (s.case ? '정답: ' + s.case : '정답: 균형') : '삽입 뒤 균형인가요? 경우를 먼저 예측해 보세요.';
      var expected = s.case ? s.case : '균형';
      $('feedback').innerHTML = revealed ? '<b>' + (selected === expected ? '맞았습니다. ' : '정답은 ') + esc(expected) + '</b> · ' + (s.dup ? '이미 있는 키라 무시됩니다.' : (s.case ? '불균형 지점 ' + esc(s.at) + ', 균형 인수 ' + esc(s.atBf) + ' · ' + rotationText(s) : 'AVL 범위 안입니다.')) : '선택한 뒤 정답을 확인하세요.';
      $('before').innerHTML = draw(s.before, '삽입 직후 · 회전 전');
      $('after').innerHTML = revealed ? draw(s.after, '확인된 뒤') : '<div class="hidden-tree">정답을 확인하면 나타납니다.</div>';
      answer.innerHTML = choices.map(function (c) { return '<button data-choice="' + c + '"' + (revealed ? ' disabled' : '') + '>' + c + '</button>'; }).join('');
      Array.prototype.forEach.call(answer.querySelectorAll('button'), function (b) { b.onclick = function () { selected = b.getAttribute('data-choice'); model.answer(); render(); $('feedback').setAttribute('tabindex','-1'); $('feedback').focus(); }; });
      $('prev').disabled = model.index() === 0;
      $('reset').disabled = model.index() === 0 && !revealed;
      $('next').disabled = !revealed || model.index() === model.length() - 1;
      $('end').disabled = model.index() === model.length() - 1 && revealed;
      if (model.done()) message.textContent = '마지막 삽입까지 확인했어요. 회전은 키의 순서를 바꾸지 않고 높이를 고칩니다. 수업 노트에서 다른 입력도 실행해 보세요.';
      else message.textContent = '';
      $('summary').hidden = !model.done();
      $('summary').textContent = '최종 높이 ' + summary.height + ' · 전위 순회 ' + summary.preorder.join(' ') + ' · 중위 순회 ' + summary.inorder.join(' ');
    }
    $('input').textContent = payload.inputText;
    $('keySequence').textContent = '삽입 순서: ' + payload.keys.join(' → ');
    $('lessonLink').href = 'lesson.html';
    $('zipLink').href = 'downloads/avl-source.zip';
    $('prev').onclick = function () { selected = null; model.previous(); render(); };
    $('reset').onclick = function () { selected = null; model.reset(); render(); };
    $('next').onclick = function () { selected = null; model.next(); render(); };
    $('end').onclick = function () { selected = null; model.end(); render(); };
    render();
  }
  return { createModel: createModel, mount: mount };
});
