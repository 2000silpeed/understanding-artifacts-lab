// Minibatch training of a tiny bigram language model — the lab's engine (browser and node).
// Same steps, shuffle and arithmetic order as examples/minibatch.py and examples/minibatch.cpp;
// lab/check.cjs runs it on examples/data and compares every number with examples/out/python-result.json.
(function (root) {
  'use strict';

  function parseCorpus(text) {
    const sentences = text.split(/\r?\n/).map(l => l.trim().split(/\s+/).filter(Boolean)).filter(w => w.length);
    const vocab = [];
    for (const ws of sentences) for (const w of ws) if (!vocab.includes(w)) vocab.push(w);
    const pairs = [];
    for (const ws of sentences) for (let i = 0; i + 1 < ws.length; i++) pairs.push([vocab.indexOf(ws[i]), vocab.indexOf(ws[i + 1])]);
    return { vocab, pairs };
  }

  function parseConfig(text) {
    const kv = {};
    for (let l of text.split(/\r?\n/)) {
      l = l.split('#')[0].trim();
      if (!l) continue;
      const [k, ...v] = l.split(/\s+/);
      kv[k] = v;
    }
    return {
      learning_rate: parseFloat(kv.learning_rate[0]), seed: parseInt(kv.seed[0], 10),
      walkthrough_batch: parseInt(kv.walkthrough_batch[0], 10), walkthrough_steps: parseInt(kv.walkthrough_steps[0], 10),
      curve_batches: kv.curve_batches.map(x => parseInt(x, 10)), curve_epochs: parseInt(kv.curve_epochs[0], 10),
      grad_check_eps: parseFloat(kv.grad_check_eps[0]),
    };
  }

  /** 32-bit LCG (Numerical Recipes constants), as in the Python and C++ examples. */
  function Lcg(seed) {
    let state = seed >>> 0;
    return { next() { state = (Math.imul(1664525, state) + 1013904223) >>> 0; return state; } };
  }
  function shuffled(n, rng) {
    const order = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) { const j = rng.next() % (i + 1); [order[i], order[j]] = [order[j], order[i]]; }
    return order;
  }
  function softmax(row) {
    const m = Math.max(...row), e = row.map(x => Math.exp(x - m));
    let s = 0; for (const x of e) s += x;
    return e.map(x => x / s);
  }
  const zeros = V => Array.from({ length: V }, () => new Array(V).fill(0));

  /** Loss and gradient of a batch, reduce 'mean' (÷ B) or 'sum'; per-example details kept. */
  function batchLossGrad(W, pairs, idx, reduce = 'mean') {
    const V = W.length, G = zeros(V), per = [];
    let total = 0;
    for (const k of idx) {
      const [prev, nxt] = pairs[k], p = softmax(W[prev]), loss = -Math.log(p[nxt]);
      const grad = p.map((x, j) => x - (j === nxt ? 1 : 0));
      per.push({ index: k, prev, next: nxt, probs: p, loss, grad });
      total += loss;
      for (let j = 0; j < V; j++) G[prev][j] += grad[j];
    }
    const scale = reduce === 'mean' ? 1 / idx.length : 1;
    return { loss: total * scale, G: G.map(r => r.map(g => g * scale)), per };
  }
  const fullLoss = (W, pairs) => batchLossGrad(W, pairs, pairs.map((_, i) => i)).loss;
  const step = (W, G, lr) => W.map((r, i) => r.map((w, j) => w - lr * G[i][j]));

  function train(pairs, V, B, epochs, lr, seed) {
    const rng = Lcg(seed);
    let W = zeros(V);
    const log = { batch: B, updates: 0, examplesSeen: [0], fullLoss: [fullLoss(W, pairs)], batchLoss: [], batches: [] };
    for (let e = 0; e < epochs; e++) {
      const order = shuffled(pairs.length, rng);
      for (let s = 0; s < order.length; s += B) {
        const idx = order.slice(s, s + B), b = batchLossGrad(W, pairs, idx);
        W = step(W, b.G, lr);
        log.updates++; log.batches.push(idx); log.batchLoss.push(b.loss);
        log.examplesSeen.push(log.examplesSeen[log.examplesSeen.length - 1] + idx.length);
        log.fullLoss.push(fullLoss(W, pairs));
      }
    }
    log.W = W; log.probs = W.map(softmax);
    return log;
  }

  /** The whole example run, same shape as examples/out/python-result.json. */
  function run(corpusText, cfg) {
    const { vocab, pairs } = parseCorpus(corpusText), V = vocab.length, N = pairs.length, lr = cfg.learning_rate;
    let W = zeros(V);
    const order = shuffled(N, Lcg(cfg.seed)), B = cfg.walkthrough_batch, steps = [];
    for (let k = 0; k < cfg.walkthrough_steps && k * B < N; k++) {
      const idx = order.slice(k * B, (k + 1) * B), before = fullLoss(W, pairs), b = batchLossGrad(W, pairs, idx), W2 = step(W, b.G, lr);
      steps.push({ step: k + 1, batch: idx, examples: b.per, meanLoss: b.loss, meanGrad: b.G, Wbefore: W, Wafter: W2, probsBefore: W.map(softmax), probsAfter: W2.map(softmax),
        batchLossAfter: batchLossGrad(W2, pairs, idx).loss, fullLossBefore: before, fullLossAfter: fullLoss(W2, pairs) });
      W = W2;
    }
    const all = pairs.map((_, i) => i), m = batchLossGrad(zeros(V), pairs, all, 'mean'), su = batchLossGrad(zeros(V), pairs, all, 'sum');
    const big = G => Math.max(...G.flat().map(g => Math.abs(lr * g)));
    const curves = {};
    for (const b of cfg.curve_batches) curves[String(b)] = train(pairs, V, b, cfg.curve_epochs, lr, cfg.seed);
    const stepScale = cfg.curve_batches.map(b => {
      const idx = shuffled(N, Lcg(cfg.seed)).slice(0, b);
      return { batch: b, firstBatch: idx, meanMaxStep: big(batchLossGrad(zeros(V), pairs, idx, 'mean').G), sumMaxStep: big(batchLossGrad(zeros(V), pairs, idx, 'sum').G) };
    });
    let best = 0;
    for (let prev = 0; prev < V; prev++) {
      const nx = pairs.filter(p => p[0] === prev).map(p => p[1]);
      for (const n of [...new Set(nx)]) { const c = nx.filter(x => x === n).length; best -= c * Math.log(c / nx.length); }
    }
    best /= N;
    return {
      vocab, pairs, walkthrough: { batchSize: B, learningRate: lr, epochOrder: order, steps },
      meanVsSum: { batch: N, learningRate: lr,
        mean: { loss: m.loss, maxAbsStep: big(m.G), fullLossAfter: fullLoss(step(zeros(V), m.G, lr), pairs) },
        sum: { loss: su.loss, maxAbsStep: big(su.G), fullLossAfter: fullLoss(step(zeros(V), su.G, lr), pairs) } },
      stepScale, curves, bestPossibleLoss: best,
    };
  }

  const MB = { parseCorpus, parseConfig, Lcg, shuffled, softmax, batchLossGrad, fullLoss, step, train, run, zeros };
  if (typeof module !== 'undefined' && module.exports) module.exports = MB; else root.MB = MB;
})(typeof window !== 'undefined' ? window : globalThis);
