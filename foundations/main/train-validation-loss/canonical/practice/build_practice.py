"""Builds practice/index.html: the companion practice page for the lesson (offline, one file, no network).

usage: python3 -B films/train-validation-loss-20261029/practice/build_practice.py
Every number on the page is read from results/*.json at build time and embedded as JSON; nothing is typed by hand.
tests/test_practice.py checks that the embedded data equals the results and that the page loads nothing external.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILM = HERE.parent
R = FILM / 'results'
small = json.loads((R / 'run-small.json').read_text())
large = json.loads((R / 'run-large.json').read_text())
summary = json.loads((R / 'summary.json').read_text())
narr = json.loads((FILM / 'script' / 'narration.json').read_text())
DATA = {
    'runs': {k: {'label': r['label'], 'n_train': r['n_train_sentences'], 'floor_val': r['floor_val'], 'best': r['best'], 'final': r['final'],
                 'test': r['test'], 'probe': {'who': r['probe']['who'], 'true_p': r['probe']['true_p'], 'train_counts': r['probe']['train_counts'], 'final': r['probe']['final']},
                 'generation': r['generation'], 'log': r['log']} for k, r in (('small', small), ('large', large))},
    'source': 'results/run-small.json, results/run-large.json (built by practice/build_practice.py)',
}

HTML = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>실습 — __TITLE__</title>
<style>
:root{--ground:#FBF5EE;--ink:#123649;--accent:#2952BE;--muted:#4F626D;--panel:#F4EDE3;--line:#DCD3C4}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font:17px/1.6 "Pretendard","Apple SD Gothic Neo","Noto Sans KR",system-ui,sans-serif}
main{max-width:980px;margin:0 auto;padding:40px 24px 80px}
h1{font-size:34px;line-height:1.2;margin:0 0 6px}
h2{font-size:23px;margin:44px 0 8px}
.sub{color:var(--muted);margin:0 0 24px}
section{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:22px 24px;margin:18px 0}
.row{display:flex;gap:18px;align-items:center;flex-wrap:wrap}
input[type=range]{width:min(520px,100%);accent-color:var(--accent)}
.big{font-size:30px;font-weight:800;font-variant-numeric:tabular-nums}
.val{color:var(--accent)} .train{color:var(--ink)} .muted{color:var(--muted)}
button{font:inherit;border:1.5px solid var(--ink);background:transparent;color:var(--ink);border-radius:999px;padding:6px 16px;cursor:pointer}
button[aria-pressed=true],button.on{background:var(--ink);color:var(--ground)}
canvas{width:100%;height:auto;background:var(--ground);border-radius:12px;border:1px solid var(--line)}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left}
code,pre{font-family:ui-monospace,Menlo,monospace;font-size:14px}
pre{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px;overflow:auto}
details{margin:10px 0} summary{cursor:pointer;font-weight:700}
.note{font-size:14px;color:var(--muted)}
.ok{color:#1e7a46;font-weight:700} .no{color:#a33a2a;font-weight:700}
</style>
</head>
<body>
<main>
<h1>__TITLE__ — 실습</h1>
<p class="sub">__SUBTITLE__. 영상과 같은 실험의 실제 기록으로 직접 확인한다. 이 페이지의 수치는 모두 <code>results/*.json</code>에서 왔다(실측 · 이 실험의 한 번 실행).</p>

<h2>1. 손실 = −ln(정답 확률)</h2>
<section>
  <div class="row"><label for="p">정답 글자에 준 확률 p</label><input id="p" type="range" min="0.001" max="1" step="0.001" value="0.5"></div>
  <p class="big">p = <span id="pv"></span> → 손실 <span id="lv" class="val"></span></p>
  <p class="note">p = 1이면 0, 2분의 1이면 0.69, 4분의 1이면 1.39. 확률이 0에 가까울수록 손실은 끝없이 커진다(저녁 0.04%를 준 모델이 처음 보는 '강아지가 저녁에' 문장에서 비싼 값을 치르는 이유).</p>
</section>

<h2>2. 두 곡선을 직접 읽기</h2>
<section>
  <div class="row" role="group" aria-label="실험 선택">
    <button id="b-small" class="on">훈련 32문장</button><button id="b-large">훈련 512문장</button>
  </div>
  <canvas id="chart" width="1200" height="560" aria-label="훈련 손실과 검증 손실 곡선"></canvas>
  <div class="row"><label for="step">걸음</label><input id="step" type="range" min="0" max="3000" step="10" value="550"><span class="big" id="sv"></span></div>
  <p>훈련 손실 <b class="train big" id="tv"></b> · 검증 손실 <b class="val big" id="vv"></b> · 차이 <b id="gv" class="big"></b></p>
  <p class="note">점선은 이론상 바닥 <span id="fv"></span>. y축은 1.0에서 자른다(0걸음 근처는 약 4).</p>
  <p><button id="stop">여기서 멈추기</button> <span id="verdict"></span></p>
</section>

<h2>3. 진단: 배우는 중? 외우는 중?</h2>
<section>
  <p>구간을 고르고 판정해 보자. 판정은 기록에서 계산한다: 그 구간에서 훈련 손실과 검증 손실이 각각 내려갔는지.</p>
  <table id="quiz"><thead><tr><th>실험</th><th>구간</th><th>내 판정</th><th>기록</th></tr></thead><tbody></tbody></table>
</section>

<h2>4. '강아지가' 다음 말</h2>
<section>
  <table id="probe"><thead><tr><th>다음 말</th><th>32문장 훈련 횟수</th><th>32문장 모델 확률</th><th>512문장 모델 확률</th><th>진짜</th></tr></thead><tbody></tbody></table>
  <p class="note">32문장 모델은 훈련에서 본 횟수 비율(3/8, 4/8, 0/8, 1/8)을 거의 그대로 따른다. 512문장 모델은 진짜 25% 근처다.</p>
</section>

<h2>5. 직접 돌려 보기</h2>
<section>
  <p>필요한 것: Python 3.12 + numpy. 네트워크·GPU 불필요. 결과 파일을 덮어쓰므로 <b>폴더를 복사한 뒤</b> 실행한다.</p>
<pre>cp -R films/train-validation-loss-20261029 /tmp/tvl-practice
cd /tmp/tvl-practice
python3 -B src/corpus.py fixtures/grammar.json fixtures
python3 -B src/run_experiment.py fixtures results     # 약 70초
python3 -B src/make_table.py                         # results/table.md</pre>
  <details><summary>연습 1 — 은닉층을 128에서 32로 줄이면?</summary>
    <p>복사본의 <code>fixtures/config.json</code>에서 <code>"hidden": 32</code>로 바꾸고 위 명령을 다시 실행한다. 실행 전에 예측을 적어 두자: 검증 최저 걸음, 마지막 훈련·검증 손실. 이 실험에서는 돌리지 않았으므로 답은 여러분의 실행 결과다.</p></details>
  <details><summary>연습 2 — 검증으로 멈춘 모델의 시험 손실(0.48)이 검증 손실(0.50)보다 낮을 수 있는 이유</summary>
    <p>시험 128문장도 검증 128문장도 1,024문장 중 일부를 뽑은 표본이다. 표본마다 우연히 쉬운 문장이 더 들어갈 수 있다. 차이 0.02는 이 표본 크기에서 생길 수 있는 흔들림이다. 그래서 멈출 시점을 고른 세트(검증)가 아니라 한 번도 쓰지 않은 세트(시험)로 성적을 잰다.</p></details>
  <details><summary>연습 3 — 훈련 손실이 이론상 바닥보다 낮아지면 왜 "외웠다"인가</summary>
    <p>바닥은 진짜 규칙을 완벽히 아는 모델의 손실이다. 그보다 낮다는 것은 규칙이 허락하는 것보다 훈련 문장을 더 확신한다는 뜻이다. 예: 훈련에 '강아지가 저녁에'가 없었다는 우연을 믿고 저녁에 0.04%를 준다. 그 확신은 처음 보는 문장에서 손실로 돌아온다.</p></details>
</section>
<p class="note">데이터: <span id="src"></span></p>
</main>
<script>
const DATA = __DATA__;
const $ = id => document.getElementById(id);
const f2 = v => v.toFixed(2);
// 1. loss calculator
const p = $('p');
const upd1 = () => { const v = +p.value; $('pv').textContent = v.toFixed(3); $('lv').textContent = f2(-Math.log(v)); };
p.oninput = upd1; upd1();
// 2. chart
let run = 'small';
const cv = $('chart'), g = cv.getContext('2d');
const box = { x: 70, y: 30, w: 1090, h: 470 };
const X = s => box.x + (s / 3000) * box.w, Y = v => box.y + box.h - (v / 1.0) * box.h;
function draw(step) {
  const r = DATA.runs[run];
  g.clearRect(0, 0, cv.width, cv.height);
  g.font = '16px sans-serif'; g.fillStyle = '#4F626D'; g.strokeStyle = '#DCD3C4'; g.lineWidth = 1;
  [0, 0.25, 0.5, 0.75, 1].forEach(v => { g.beginPath(); g.moveTo(box.x, Y(v)); g.lineTo(box.x + box.w, Y(v)); g.stroke(); g.fillText(v.toFixed(2), 14, Y(v) + 5); });
  [0, 1000, 2000, 3000].forEach(s => g.fillText(s.toLocaleString('en-US'), X(s) - 16, box.y + box.h + 24));
  g.save(); g.beginPath(); g.rect(box.x, box.y, box.w, box.h); g.clip();
  g.setLineDash([10, 8]); g.strokeStyle = '#4F626D'; g.lineWidth = 2; g.beginPath(); g.moveTo(box.x, Y(r.floor_val)); g.lineTo(box.x + box.w, Y(r.floor_val)); g.stroke(); g.setLineDash([]);
  for (const [k, col, w] of [['train', '#123649', 2], ['val', '#2952BE', 4]]) {
    g.strokeStyle = col; g.lineWidth = w; g.beginPath();
    r.log.forEach((q, i) => (i ? g.lineTo(X(q.step), Y(q[k])) : g.moveTo(X(q.step), Y(q[k])))); g.stroke();
  }
  g.restore();
  g.strokeStyle = '#2952BE'; g.lineWidth = 1.5; g.beginPath(); g.moveTo(X(step), box.y); g.lineTo(X(step), box.y + box.h); g.stroke();
  const q = r.log.find(x => x.step === step);
  $('sv').textContent = step.toLocaleString('en-US') + '걸음';
  $('tv').textContent = f2(q.train); $('vv').textContent = f2(q.val); $('gv').textContent = f2(q.val - q.train);
  $('fv').textContent = f2(r.floor_val);
}
const st = $('step');
st.oninput = () => { $('verdict').textContent = ''; draw(+st.value); };
for (const k of ['small', 'large']) $('b-' + k).onclick = () => { run = k; $('b-small').classList.toggle('on', k === 'small'); $('b-large').classList.toggle('on', k === 'large'); $('verdict').textContent = ''; draw(+st.value); };
$('stop').onclick = () => {
  const r = DATA.runs[run], s = +st.value, q = r.log.find(x => x.step === s);
  const best = r.log.reduce((a, b) => (b.val < a.val ? b : a));
  $('verdict').innerHTML = `검증 손실 ${f2(q.val)} — 기록상 최저는 ${best.step.toLocaleString('en-US')}걸음의 ${f2(best.val)}. ` + (s === best.step ? '<span class="ok">최저점에서 멈췄다.</span>' : `최저점보다 ${f2(q.val - best.val)} 높다.`);
};
draw(+st.value);
// 3. quiz: verdict from the log (both fall → learning; train falls and val rises → memorising)
const SEG = [['small', 100, 500], ['small', 600, 3000], ['large', 600, 3000]];
const tb = document.querySelector('#quiz tbody');
SEG.forEach(([k, a, b]) => {
  const r = DATA.runs[k], A = r.log.find(x => x.step === a), Bq = r.log.find(x => x.step === b);
  const truth = Bq.train < A.train && Bq.val > A.val ? '외우는 중' : Bq.train < A.train && Bq.val <= A.val ? '배우는 중' : '기타';
  const tr = document.createElement('tr');
  tr.innerHTML = `<td>${r.label}</td><td>${a.toLocaleString('en-US')}→${b.toLocaleString('en-US')}걸음</td><td><button>배우는 중</button> <button>외우는 중</button></td><td class="muted">?</td>`;
  const out = tr.lastChild;
  tr.querySelectorAll('button').forEach(btn => btn.onclick = () => {
    out.innerHTML = `훈련 ${f2(A.train)}→${f2(Bq.train)}, 검증 ${f2(A.val)}→${f2(Bq.val)}: <b>${truth}</b> ` + (btn.textContent === truth ? '<span class="ok">맞음</span>' : '<span class="no">다시</span>');
  });
  tb.append(tr);
});
// 4. probe
const pb = document.querySelector('#probe tbody'), S = DATA.runs.small.probe, L = DATA.runs.large.probe;
const pct = v => (v < 0.01 ? (v * 100).toFixed(2) : (v * 100).toFixed(0)) + '%';
Object.keys(S.final).forEach(w => {
  const tr = document.createElement('tr');
  tr.innerHTML = `<td>${w}</td><td>${S.train_counts[w]}</td><td class="val">${pct(S.final[w])}</td><td>${pct(L.final[w])}</td><td class="muted">${pct(S.true_p)}</td>`;
  pb.append(tr);
});
$('src').textContent = DATA.source;
</script>
</body>
</html>
'''
out = HTML.replace('__DATA__', json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))).replace('__TITLE__', narr['title']).replace('__SUBTITLE__', narr['subtitle'])
(HERE / 'index.html').write_text(out)
print('practice/index.html', len(out), 'bytes')
