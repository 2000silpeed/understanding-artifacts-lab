const dataPromise = fetch('./data.json').then((r) => { if (!r.ok) throw new Error(`data.json ${r.status}`); return r.json(); });
const state = { simulated: false, reason: false, sgd: false };
const $ = (id) => document.getElementById(id);
const fmt = (x) => Number(x).toFixed(6);

function dataGradient(scale, t) { return t % 2 === 1 ? scale : -scale; }

// 독립적인 브라우저 계산: canonical Python/C++ 구현을 읽거나 호출하지 않는다.
function simulate(algorithm, lambda, steps, fixture) {
  const w = fixture.w0.slice();
  const m = [0, 0]; const v = [0, 0];
  const lr = 0.001; const b1 = 0.9; const b2 = 0.999; const eps = 1e-8;
  for (let t = 1; t <= steps; t += 1) {
    for (let i = 0; i < w.length; i += 1) {
      const gd = dataGradient(fixture.gradScale[i], t);
      const g = algorithm === 'l2' ? gd + lambda * w[i] : gd;
      if (algorithm === 'adamw') w[i] = w[i] * (1 - lr * lambda);
      m[i] = b1 * m[i] + (1 - b1) * g;
      v[i] = b2 * v[i] + (1 - b2) * g * g;
      const mh = m[i] / (1 - (b1 ** t));
      const vh = v[i] / (1 - (b2 ** t));
      if (algorithm === 'none' || algorithm === 'l2' || algorithm === 'adamw') {
        w[i] = w[i] - lr * mh / (Math.sqrt(vh) + eps);
      }
    }
  }
  return w;
}

function simulateSgd(kind, lambda, fixture, steps = 1000) {
  const w = fixture.w0.slice(); const lr = 0.001;
  for (let t = 1; t <= steps; t += 1) {
    for (let i = 0; i < w.length; i += 1) {
      const before = w[i];
      if (kind === 'decoupled') w[i] = before * (1 - lr * lambda);
      const g = dataGradient(fixture.gradScale[i], t) + (kind === 'l2' ? lambda * before : 0);
      w[i] -= lr * g;
    }
  }
  return w;
}

function selectedKey(algorithm, lambda) {
  if (algorithm === 'none') return `adam_${lambda}`;
  if (algorithm === 'l2') return `adam_l2_${lambda}`;
  return `adamw_${lambda}`;
}

function setProgress() {
  $('step1').className = `step ${state.simulated ? 'done' : 'active'}`;
  $('step2').className = `step ${state.reason ? 'done' : (state.simulated ? 'active' : '')}`;
  $('step3').className = `step ${state.sgd ? 'done' : (state.reason ? 'active' : '')}`;
  $('step4').className = `step ${state.simulated && state.reason && state.sgd ? 'done' : ''}`;
  $('completion').hidden = !(state.simulated && state.reason && state.sgd);
}

function showLab(d) {
  const algorithm = $('algorithm').value; const lambda = Number($('lambda').value); const steps = Number($('steps').value);
  const got = simulate(algorithm, lambda, steps, d.fixture); const key = selectedKey(algorithm, lambda);
  const reference = d.realOutputs[key]; const refStep = reference.trace[String(steps)] || reference.python;
  const py = steps === 1000 ? reference.python : refStep;
  const cpp = steps === 1000 ? reference.cpp : (reference.trace[String(steps)] || reference.cpp);
  const maxDiff = Math.max(...got.map((x, i) => Math.abs(x - py[i])));
  $('weightA').textContent = fmt(got[0]); $('weightB').textContent = fmt(got[1]);
  $('barA').style.width = `${Math.max(0, Math.min(100, got[0] * 100))}%`;
  $('barB').style.width = `${Math.max(0, Math.min(100, got[1] * 100))}%`;
  $('resultBody').innerHTML = `<tr><td>브라우저 계산</td><td>${fmt(got[0])}</td><td>${fmt(got[1])}</td></tr><tr><td>Python 기준값</td><td>${fmt(py[0])}</td><td>${fmt(py[1])}</td></tr><tr><td>C++ 기준값</td><td>${fmt(cpp[0])}</td><td>${fmt(cpp[1])}</td></tr>`;
  const label = algorithm === 'none' ? '감쇠 없음' : (algorithm === 'l2' ? 'Adam + L2' : 'AdamW');
  $('labFeedback').hidden = false; $('labFeedback').className = `feedback ${maxDiff < 1e-9 ? 'good' : 'warn'}`;
  $('labFeedback').innerHTML = `<span class="answer">${label}, λ ${lambda}, ${steps}걸음</span><br>브라우저 계산과 실제 Python/C++ 결과의 최대 차이: <strong>${maxDiff.toExponential(2)}</strong>.<br>${algorithm === 'adamw' ? 'AdamW는 먼저 w를 같은 비율로 줄여서 A와 B의 decay 비율이 같습니다.' : algorithm === 'l2' ? 'L2에서는 λw가 g에 합쳐집니다. B처럼 데이터 기울기가 작은 곳에서는 이 항의 상대적 영향이 커집니다.' : '감쇠 없음은 두 감쇠 방법을 비교할 기준선입니다.'}`;
  state.simulated = true; setProgress(); $('reasonQuiz').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function quiz(button, feedback, kind) {
  const correct = button.dataset.answer === 'correct';
  [...button.parentElement.querySelectorAll('.choice')].forEach((b) => { b.disabled = correct; b.classList.remove('wrong', 'correct'); });
  button.classList.add(correct ? 'correct' : 'wrong');
  feedback.hidden = false; feedback.className = `feedback ${correct ? 'good' : 'warn'}`;
  feedback.textContent = correct ? (kind === 'reason' ? '맞아요. Adam + L2에서는 λw가 데이터 기울기와 함께 Adam의 m, v를 통과합니다. B의 작은 데이터 기울기에서는 같은 λ가 상대적으로 크게 작용합니다.' : '맞아요. SGD에서는 L2의 g = g_data + λw를 그대로 빼는 식을 정리하면 감쇠와 같은 형태가 됩니다. Adam의 정규화가 끼면 이 등가가 깨집니다.') : '아직 아니에요. 식에서 감쇠가 들어가는 위치와 A/B의 grad_scale을 다시 보세요.';
  if (correct) { if (kind === 'reason') state.reason = true; else { state.sgd = true; $('sgdCheck').hidden = false; } setProgress(); if (kind === 'reason') $('sgdQuiz').scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
}

async function boot() {
  const d = await dataPromise;
  $('simulate').addEventListener('click', () => showLab(d));
  $('reset').addEventListener('click', () => { state.simulated = false; state.reason = false; state.sgd = false; $('sgdCheck').hidden = true; $('labFeedback').hidden = true; $('reasonFeedback').hidden = true; $('sgdFeedback').hidden = true; $('weightA').textContent = '—'; $('weightB').textContent = '—'; $('barA').style.width = '0%'; $('barB').style.width = '0%'; $('resultBody').innerHTML = '<tr><td>브라우저 계산</td><td>—</td><td>—</td></tr><tr><td>Python 기준값</td><td>—</td><td>—</td></tr><tr><td>C++ 기준값</td><td>—</td><td>—</td></tr>'; [...document.querySelectorAll('.choice')].forEach((b) => { b.disabled = false; b.classList.remove('correct', 'wrong'); }); setProgress(); $('simulate').focus(); });
  $('reasonQuiz').querySelectorAll('.choice').forEach((b) => b.addEventListener('click', () => quiz(b, $('reasonFeedback'), 'reason')));
  $('sgdQuiz').querySelectorAll('.choice').forEach((b) => b.addEventListener('click', () => quiz(b, $('sgdFeedback'), 'sgd')));
  $('sgdCheck').addEventListener('click', () => { const a = simulateSgd('l2', .1, d.fixture); const b = simulateSgd('decoupled', .1, d.fixture); $('sgdFeedback').hidden = false; $('sgdFeedback').className = 'feedback good'; $('sgdFeedback').textContent = `계산 완료: 1000걸음 뒤 L2 [${fmt(a[0])}, ${fmt(a[1])}], 분리 감쇠 [${fmt(b[0])}, ${fmt(b[1])}]. 최대 차이는 ${Math.max(...a.map((x, i) => Math.abs(x - b[i]))).toExponential(2)}로 반올림 오차 수준입니다.`; });
  setProgress();
}
boot().catch((err) => { $('labFeedback').hidden = false; $('labFeedback').className = 'feedback warn'; $('labFeedback').textContent = `데이터를 불러오지 못했습니다: ${err.message}`; });
