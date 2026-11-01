"""A small character-level language model in plain numpy.

Model (Bengio-style MLP):  the previous `context` characters -> embeddings ->
one tanh hidden layer -> softmax over the next character.  Loss is the mean
cross-entropy in nats per predicted character.  Trained full-batch with Adam,
no regularisation, so that it can memorise a small training set.
"""
import numpy as np

from corpus import BOS, EOS


def build_vocab(sentences):
    chars = sorted({c for s in sentences for c in s})
    itos = [BOS, EOS] + chars
    return {c: i for i, c in enumerate(itos)}, itos


def windows(sentences, stoi, context):
    """Every (previous `context` characters, next character) pair."""
    xs, ys = [], []
    for s in sentences:
        ids = [stoi[BOS]] * context + [stoi[c] for c in s] + [stoi[EOS]]
        for i in range(context, len(ids)):
            xs.append(ids[i - context:i])
            ys.append(ids[i])
    return np.array(xs, dtype=np.int64), np.array(ys, dtype=np.int64)


def init_params(vocab, cfg, seed):
    rng = np.random.default_rng(seed)
    d, h, n = cfg["embed"], cfg["hidden"], cfg["context"]
    return {
        "E": rng.normal(0, 1.0, (vocab, d)),
        "W1": rng.normal(0, 1.0 / np.sqrt(n * d), (n * d, h)),
        "b1": np.zeros(h),
        "W2": rng.normal(0, 1.0 / np.sqrt(h), (h, vocab)),
        "b2": np.zeros(vocab),
    }


def n_params(p):
    return int(sum(v.size for v in p.values()))


def forward(p, X):
    emb = p["E"][X].reshape(len(X), -1)
    hid = np.tanh(emb @ p["W1"] + p["b1"])
    logits = hid @ p["W2"] + p["b2"]
    logits = logits - logits.max(axis=1, keepdims=True)
    logp = logits - np.log(np.exp(logits).sum(axis=1, keepdims=True))
    return emb, hid, logp


def loss(p, X, Y):
    return float(-forward(p, X)[2][np.arange(len(Y)), Y].mean())


def per_char_logp(p, X, Y):
    return forward(p, X)[2][np.arange(len(Y)), Y]


def loss_and_grads(p, X, Y):
    emb, hid, logp = forward(p, X)
    m = len(Y)
    L = float(-logp[np.arange(m), Y].mean())
    d_logits = np.exp(logp)
    d_logits[np.arange(m), Y] -= 1.0
    d_logits /= m
    g = {"W2": hid.T @ d_logits, "b2": d_logits.sum(0)}
    d_hid = (d_logits @ p["W2"].T) * (1.0 - hid ** 2)
    g["W1"] = emb.T @ d_hid
    g["b1"] = d_hid.sum(0)
    d_emb = (d_hid @ p["W1"].T).reshape(m, X.shape[1], -1)
    gE = np.zeros_like(p["E"])
    np.add.at(gE, X, d_emb)
    g["E"] = gE
    return L, g


class Adam:
    def __init__(self, params, lr, b1=0.9, b2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps, self.t = lr, b1, b2, eps, 0
        self.m = {k: np.zeros_like(v) for k, v in params.items()}
        self.v = {k: np.zeros_like(v) for k, v in params.items()}

    def step(self, params, grads):
        self.t += 1
        for k in params:
            self.m[k] = self.b1 * self.m[k] + (1 - self.b1) * grads[k]
            self.v[k] = self.b2 * self.v[k] + (1 - self.b2) * grads[k] ** 2
            mh = self.m[k] / (1 - self.b1 ** self.t)
            vh = self.v[k] / (1 - self.b2 ** self.t)
            params[k] -= self.lr * mh / (np.sqrt(vh) + self.eps)


def train(train_sents, val_sents, stoi, cfg, seed, on_eval=None):
    """Returns the loss log and the parameters at the best validation step."""
    Xtr, Ytr = windows(train_sents, stoi, cfg["context"])
    Xva, Yva = windows(val_sents, stoi, cfg["context"])
    p = init_params(len(stoi), cfg, seed)
    opt = Adam(p, cfg["lr"])
    log = []
    best = None
    for step in range(cfg["steps"] + 1):
        if step % cfg["eval_every"] == 0:
            row = {"step": step, "train": loss(p, Xtr, Ytr), "val": loss(p, Xva, Yva)}
            log.append(row)
            if best is None or row["val"] < best["val"]:
                best = dict(row)
                best_params = {k: v.copy() for k, v in p.items()}
            if on_eval:
                on_eval(row)
        if step == cfg["steps"]:
            break
        _, g = loss_and_grads(p, Xtr, Ytr)
        opt.step(p, g)
    return {"log": log, "best": best, "best_params": best_params, "final_params": p,
            "n_train_targets": int(len(Ytr)), "n_val_targets": int(len(Yva))}
