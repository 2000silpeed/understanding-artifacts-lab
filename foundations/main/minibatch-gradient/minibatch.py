"""Minibatch training of a tiny bigram language model — the worked example behind the film.

Model: a 4 x 4 score table W. Row = previous word, column = next word. p = softmax(W[prev]).
Loss of one example (prev, next) = -log p[next]. Its gradient is non-zero only in row `prev`: p - onehot(next).
Minibatch step: average the losses and the gradients of B examples, then W <- W - lr * (mean gradient).

Standard library only (Python 3.8+). minibatch.cpp implements the same steps (same shuffle, same order) and must
print the same numbers; test_source.py compares the two.

usage:
  python3 minibatch.py data/            # JSON result on stdout (examples/out/python-result.json)
  python3 minibatch.py data/ --report   # the same run as a readable trace (examples/out/python-report.txt)
"""
import json
import math
import sys
from pathlib import Path


def read_inputs(data_dir):
    data_dir = Path(data_dir)
    sentences = [ln.split() for ln in (data_dir / 'corpus.txt').read_text(encoding='utf-8').splitlines() if ln.strip()]
    cfg = {}
    for ln in (data_dir / 'config.txt').read_text(encoding='utf-8').splitlines():
        ln = ln.split('#', 1)[0].split()
        if ln:
            cfg[ln[0]] = ln[1:]
    vocab = []
    for words in sentences:
        for w in words:
            if w not in vocab:
                vocab.append(w)
    pairs = [(vocab.index(a), vocab.index(b)) for words in sentences for a, b in zip(words, words[1:])]
    config = {
        'learning_rate': float(cfg['learning_rate'][0]),
        'seed': int(cfg['seed'][0]),
        'walkthrough_batch': int(cfg['walkthrough_batch'][0]),
        'walkthrough_steps': int(cfg['walkthrough_steps'][0]),
        'curve_batches': [int(x) for x in cfg['curve_batches']],
        'curve_epochs': int(cfg['curve_epochs'][0]),
        'grad_check_eps': float(cfg['grad_check_eps'][0]),
    }
    return vocab, pairs, config


class Lcg:
    """32-bit linear congruential generator (Numerical Recipes constants); C++ uses the same one."""

    def __init__(self, seed):
        self.state = seed & 0xFFFFFFFF

    def next(self):
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state


def shuffled(n, rng):
    """Fisher-Yates from the back with rng.next() % (i + 1)."""
    order = list(range(n))
    for i in range(n - 1, 0, -1):
        j = rng.next() % (i + 1)
        order[i], order[j] = order[j], order[i]
    return order


def softmax(row):
    m = max(row)
    e = [math.exp(x - m) for x in row]
    s = sum(e)
    return [x / s for x in e]


def example(W, prev, nxt):
    """Probabilities, loss and gradient row of one example."""
    p = softmax(W[prev])
    loss = -math.log(p[nxt])
    grad = [p[j] - (1.0 if j == nxt else 0.0) for j in range(len(p))]
    return p, loss, grad


def batch_loss_grad(W, pairs, idx, reduce='mean'):
    """Loss and gradient matrix of a batch: mean (divide by B) or sum."""
    V = len(W)
    G = [[0.0] * V for _ in range(V)]
    total = 0.0
    per = []
    for k in idx:
        prev, nxt = pairs[k]
        p, loss, grad = example(W, prev, nxt)
        per.append({'index': k, 'prev': prev, 'next': nxt, 'probs': p, 'loss': loss, 'grad': grad})
        total += loss
        for j in range(V):
            G[prev][j] += grad[j]
    scale = 1.0 / len(idx) if reduce == 'mean' else 1.0
    return total * scale, [[g * scale for g in row] for row in G], per


def full_loss(W, pairs):
    return batch_loss_grad(W, pairs, range(len(pairs)))[0]


def step(W, G, lr):
    return [[w - lr * g for w, g in zip(wr, gr)] for wr, gr in zip(W, G)]


def zeros(V):
    return [[0.0] * V for _ in range(V)]


# The update the film shows on screen (code scene), line for line. train() runs it; test_source.py checks it
# against batch_loss_grad + step and against the C++ twin.
def minibatch_step(W, batch, lr):
    G = zeros(len(W))
    for prev, nxt in batch:
        p = softmax(W[prev])
        for j in range(len(p)):
            G[prev][j] += p[j] - (j == nxt)
    mean = 1.0 / len(batch)
    return [[w - lr * (g * mean) for w, g in zip(wr, gr)]
            for wr, gr in zip(W, G)]


def train(pairs, V, B, epochs, lr, seed):
    """Minibatch SGD from W = 0; reshuffle every epoch; batches are consecutive slices of the shuffled order."""
    rng, W = Lcg(seed), zeros(V)
    log = {'batch': B, 'updates': 0, 'examplesSeen': [0], 'fullLoss': [full_loss(W, pairs)], 'batchLoss': [], 'batches': []}
    for _ in range(epochs):
        order = shuffled(len(pairs), rng)
        for s in range(0, len(order), B):
            idx = order[s:s + B]
            loss = batch_loss_grad(W, pairs, idx)[0]
            W = minibatch_step(W, [pairs[k] for k in idx], lr)
            log['updates'] += 1
            log['batches'].append(idx)
            log['batchLoss'].append(loss)
            log['examplesSeen'].append(log['examplesSeen'][-1] + len(idx))
            log['fullLoss'].append(full_loss(W, pairs))
    log['W'] = W
    log['probs'] = [softmax(row) for row in W]
    return log


def run(data_dir):
    vocab, pairs, cfg = read_inputs(data_dir)
    V, N, lr = len(vocab), len(pairs), cfg['learning_rate']

    # walkthrough: the first steps of the B = walkthrough_batch run, every number kept
    rng, W = Lcg(cfg['seed']), zeros(V)
    order = shuffled(N, rng)
    B = cfg['walkthrough_batch']
    steps = []
    for k in range(cfg['walkthrough_steps']):
        idx = order[k * B:(k + 1) * B]
        before = full_loss(W, pairs)
        loss, G, per = batch_loss_grad(W, pairs, idx)
        W2 = step(W, G, lr)
        steps.append({'step': k + 1, 'batch': idx, 'examples': per, 'meanLoss': loss, 'meanGrad': G,
                      'Wbefore': W, 'Wafter': W2, 'probsBefore': [softmax(r) for r in W], 'probsAfter': [softmax(r) for r in W2],
                      'batchLossAfter': batch_loss_grad(W2, pairs, idx)[0], 'fullLossBefore': before, 'fullLossAfter': full_loss(W2, pairs)})
        W = W2

    # analytic gradient (p - y, averaged) against central differences of the mean loss, at the first step
    first = steps[0]
    eps, worst = cfg['grad_check_eps'], 0.0
    for i in range(V):
        for j in range(V):
            Wp, Wm = [r[:] for r in first['Wbefore']], [r[:] for r in first['Wbefore']]
            Wp[i][j] += eps
            Wm[i][j] -= eps
            num = (batch_loss_grad(Wp, pairs, first['batch'])[0] - batch_loss_grad(Wm, pairs, first['batch'])[0]) / (2 * eps)
            worst = max(worst, abs(num - first['meanGrad'][i][j]))

    # mean vs sum: one full-batch step from W = 0 with the same learning rate
    every = list(range(N))
    mean_l, mean_G, _ = batch_loss_grad(zeros(V), pairs, every, 'mean')
    sum_l, sum_G, _ = batch_loss_grad(zeros(V), pairs, every, 'sum')
    Wm_, Ws_ = step(zeros(V), mean_G, lr), step(zeros(V), sum_G, lr)

    curves = {str(b): train(pairs, V, b, cfg['curve_epochs'], lr, cfg['seed']) for b in cfg['curve_batches']}

    # step size against batch size: the first batch of each run (same seed), from W = 0, mean vs sum
    step_scale = []
    for b in cfg['curve_batches']:
        idx = shuffled(N, Lcg(cfg['seed']))[:b]
        big = {k: max(abs(lr * g) for r in batch_loss_grad(zeros(V), pairs, idx, k)[1] for g in r) for k in ('mean', 'sum')}
        step_scale.append({'batch': b, 'firstBatch': idx, 'meanMaxStep': big['mean'], 'sumMaxStep': big['sum']})

    # the best this model can do on this data: each row = the observed next-word frequencies
    best = 0.0
    for prev in range(V):
        nxt = [n for p, n in pairs if p == prev]
        for n in dict.fromkeys(nxt):  # first-appearance order, the summation order minibatch.cpp uses
            q = nxt.count(n) / len(nxt)
            best -= nxt.count(n) * math.log(q)
    best /= N

    return {
        'schema': 'MINIBATCH_EXAMPLE_V1',
        'vocab': vocab, 'pairs': pairs, 'config': cfg,
        'walkthrough': {'batchSize': B, 'learningRate': lr, 'epochOrder': order, 'steps': steps},
        'gradCheck': {'eps': eps, 'maxAbsDiff': worst},
        'meanVsSum': {'batch': N, 'learningRate': lr,
                      'mean': {'loss': mean_l, 'maxAbsStep': max(abs(lr * g) for r in mean_G for g in r), 'fullLossAfter': full_loss(Wm_, pairs), 'probsAfter': [softmax(r) for r in Wm_]},
                      'sum': {'loss': sum_l, 'maxAbsStep': max(abs(lr * g) for r in sum_G for g in r), 'fullLossAfter': full_loss(Ws_, pairs), 'probsAfter': [softmax(r) for r in Ws_]}},
        'stepScale': step_scale,
        'curves': curves,
        'bestPossibleLoss': best,
    }


def report(r):
    v = r['vocab']
    f = lambda x: f'{x:+.4f}'
    out = [f"vocab {v}", f"pairs {[(v[a], v[b]) for a, b in r['pairs']]}", f"config {r['config']}", '']
    wt = r['walkthrough']
    out.append(f"epoch order (seed {r['config']['seed']}): {wt['epochOrder']}")
    for st in wt['steps']:
        out.append(f"\n== step {st['step']}  batch {st['batch']}  (B = {wt['batchSize']}, lr = {wt['learningRate']})")
        for e in st['examples']:
            out.append(f"  #{e['index']} {v[e['prev']]} -> {v[e['next']]}   p = [{', '.join(f'{x:.4f}' for x in e['probs'])}]"
                       f"   loss = {e['loss']:.4f}   grad[{v[e['prev']]}] = [{', '.join(f(x) for x in e['grad'])}]")
        out.append(f"  mean loss = {st['meanLoss']:.4f}")
        for i, row in enumerate(st['meanGrad']):
            if any(row):
                out.append(f"  mean grad[{v[i]}] = [{', '.join(f(x) for x in row)}]")
        for i, row in enumerate(st['Wafter']):
            if any(row):
                out.append(f"  W[{v[i]}] after = [{', '.join(f(x) for x in row)}]   p = [{', '.join(f'{x:.4f}' for x in st['probsAfter'][i])}]")
        out.append(f"  batch loss after = {st['batchLossAfter']:.4f}   full loss {st['fullLossBefore']:.4f} -> {st['fullLossAfter']:.4f}")
    out.append(f"\ngradient check: max |analytic - numeric| = {r['gradCheck']['maxAbsDiff']:.2e} (eps {r['gradCheck']['eps']})")
    ms = r['meanVsSum']
    out.append(f"\none full-batch step (B = {ms['batch']}, lr = {ms['learningRate']}):")
    for k in ('mean', 'sum'):
        out.append(f"  {k:4s}: largest score change {ms[k]['maxAbsStep']:.4f}   full loss -> {ms[k]['fullLossAfter']:.4f}")
    out.append('\nlargest score change of the first batch, by batch size:')
    for s in r['stepScale']:
        out.append(f"  B = {s['batch']:>2}: mean {s['meanMaxStep']:.4f}   sum {s['sumMaxStep']:.4f}")
    out.append('\ncurves (full loss after each update):')
    for b, c in r['curves'].items():
        out.append(f"  B = {b:>2} ({c['updates']:>2} updates): " + ' '.join(f'{x:.3f}' for x in c['fullLoss']))
    out.append(f"\nbest possible loss on this data: {r['bestPossibleLoss']:.4f}")
    return '\n'.join(out)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    result = run(sys.argv[1])
    if '--report' in sys.argv:
        print(report(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=1))
