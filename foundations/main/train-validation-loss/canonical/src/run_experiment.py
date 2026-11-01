"""Run the lesson's experiments and write every number the film uses.

Usage (from the film folder):
    python -B src/run_experiment.py fixtures results
Reads  fixtures/config.json, grammar.json, all.txt, train_*.txt, val.txt
Writes results/run-<id>.json (full loss log + probes) and results/summary.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpus import BOS, EOS, floor_nats_per_char  # noqa: E402
import tinylm  # noqa: E402

N_SAMPLES = 200
SAMPLE_SEED = 11


def read_lines(path):
    return [s for s in Path(path).read_text(encoding="utf-8").splitlines() if s]


def r(x, n=4):
    return round(float(x), n)


def row4(row):
    return {k: (v if k == "step" else r(v)) for k, v in row.items()}


def sample(params, stoi, itos, context, rng, max_len=40):
    ids = [stoi[BOS]] * context
    out = []
    for _ in range(max_len):
        _, _, logp = tinylm.forward(params, np.array([ids[-context:]]))
        nxt = int(rng.choice(len(itos), p=np.exp(logp[0]) / np.exp(logp[0]).sum()))
        if nxt == stoi[EOS]:
            break
        out.append(itos[nxt])
        ids.append(nxt)
    return "".join(out)


def generation_stats(params, stoi, itos, context, train, allset):
    rng = np.random.default_rng(SAMPLE_SEED)
    texts = [sample(params, stoi, itos, context, rng) for _ in range(N_SAMPLES)]
    tr, al = set(train), set(allset)
    copies = sum(t in tr for t in texts)
    valid = sum(t in al for t in texts)
    return {"n": N_SAMPLES, "seed": SAMPLE_SEED, "copies_of_train": copies,
            "copies_expected_if_true": r(N_SAMPLES * len(tr) / len(al), 2),
            "grammatical": valid, "new_grammatical": valid - copies,
            "distinct": len(set(texts)), "first5": texts[:5]}


def sentence_losses(params, sentences, stoi, context):
    """Mean loss per sentence (nats per character)."""
    out = []
    for sent in sentences:
        X, Y = tinylm.windows([sent], stoi, context)
        out.append(float(-tinylm.per_char_logp(params, X, Y).mean()))
    return np.array(out)


def pick_bias_word(train, grammar):
    """Disclosed selection rule: the 누가 word whose 언제 counts in the given
    training set are farthest from even (total variation; ties -> grammar order)."""
    who, when = grammar["slots"][0]["words"], grammar["slots"][1]["words"]
    best = None
    for w in who:
        rows = [t.split(" ")[1] for t in train if t.split(" ")[0] == w]
        tv = 0.5 * sum(abs(rows.count(x) / len(rows) - 1 / len(when)) for x in when)
        if best is None or tv > best[1] + 1e-12:
            best = (w, tv)
    return best[0]


def next_word_probs(params, prefix, options, stoi, context):
    """P(first syllable of each option | the prefix), the slot's choice point."""
    ids = [stoi[BOS]] * context + [stoi[c] for c in prefix]
    _, _, logp = tinylm.forward(params, np.array([ids[-context:]]))
    return {w: r(math.exp(logp[0][stoi[w[0]]])) for w in options}


def probe(res, train, val, stoi, grammar, context, who):
    """What the model believes comes after `who`, against the training counts and the truth."""
    when = grammar["slots"][1]["words"]
    counts = {x: sum(1 for t in train if t.split(" ")[:2] == [who, x]) for x in when}
    unseen = [x for x in when if counts[x] == 0]
    lb = sentence_losses(res["best_params"], val, stoi, context)
    lf = sentence_losses(res["final_params"], val, stoi, context)
    rise = lf - lb
    hit = [i for i, v in enumerate(val) if v.split(" ")[0] == who and v.split(" ")[1] in unseen]
    return {
        "who_rule": "첫 실험의 훈련 세트에서 '언제' 분포가 균등에서 가장 먼 '누가' 단어 (총변동거리)",
        "who": who, "prefix": who + " ", "true_p": r(1 / len(when)),
        "train_count_with_who": sum(counts.values()), "train_counts": counts,
        "unseen_after_who": unseen,
        "best": next_word_probs(res["best_params"], who + " ", when, stoi, context),
        "final": next_word_probs(res["final_params"], who + " ", when, stoi, context),
        "val_with_unseen_pair": len(hit),
        "val_with_unseen_pair_loss": {
            "best": r(float(lb[hit].mean())) if hit else None,
            "final": r(float(lf[hit].mean())) if hit else None},
        "val_sentences_worse": int((rise > 0).sum()),
        "val_rise_median": r(float(np.median(rise))),
    }


def run_one(run, cfg, grammar, fixtures, stoi, itos, allset, who):
    train = read_lines(fixtures / run["train"])
    val = read_lines(fixtures / run["val"])
    model = dict(cfg["model"], **cfg["train"])
    res = tinylm.train(train, val, stoi, model, cfg["init_seed"])
    log, best = res["log"], res["best"]
    assert all(math.isfinite(row["train"]) and math.isfinite(row["val"]) for row in log), "non-finite loss"
    final = log[-1]
    min_train = min(log, key=lambda row: row["train"])
    floor_val = floor_nats_per_char(val, grammar)
    floor_train = floor_nats_per_char(train, grammar)
    ctx = model["context"]
    test = read_lines(fixtures / run["test"])
    Xte, Yte = tinylm.windows(test, stoi, ctx)
    test_loss = {"best": r(tinylm.loss(res["best_params"], Xte, Yte)),
                 "final": r(tinylm.loss(res["final_params"], Xte, Yte)),
                 "floor": r(floor_nats_per_char(test, grammar)), "n_sentences": len(test)}
    out = {
        "id": run["id"], "label": run["label"],
        "n_train_sentences": len(train), "n_val_sentences": len(val),
        "n_train_targets": res["n_train_targets"], "n_val_targets": res["n_val_targets"],
        "n_params": tinylm.n_params(res["final_params"]),
        "floor_val": r(floor_val), "floor_train": r(floor_train),
        "start": row4(log[0]),
        "best": row4(best),
        "final": row4(final),
        "min_train": row4(min_train),
        "gap_best": r(best["val"] - best["train"]),
        "gap_final": r(final["val"] - final["train"]),
        "val_rise_after_best": r(final["val"] - best["val"]),
        "ppl": {"best_val": r(math.exp(best["val"]), 2), "final_val": r(math.exp(final["val"]), 2),
                "final_train": r(math.exp(final["train"]), 2), "floor_val": r(math.exp(floor_val), 2)},
        "test": test_loss,
        "probe": probe(res, train, val, stoi, grammar, ctx, who),
        "generation": {
            "best": generation_stats(res["best_params"], stoi, itos, ctx, train, allset),
            "final": generation_stats(res["final_params"], stoi, itos, ctx, train, allset),
        },
        "log": [{k: (v if k == "step" else r(v, 6)) for k, v in row.items()} for row in log],
    }
    return out


def main(fixtures_dir, results_dir):
    # macOS Accelerate BLAS sets spurious FP flags even in finite matmuls (seen with
    # numpy 2.0.2); silence them and check finiteness of every loss explicitly instead.
    np.seterr(all="ignore")
    fixtures, results = Path(fixtures_dir), Path(results_dir)
    results.mkdir(exist_ok=True)
    cfg = json.loads((fixtures / "config.json").read_text(encoding="utf-8"))
    grammar = json.loads((fixtures / "grammar.json").read_text(encoding="utf-8"))
    allset = read_lines(fixtures / "all.txt")
    stoi, itos = tinylm.build_vocab(allset)
    who = pick_bias_word(read_lines(fixtures / cfg["runs"][0]["train"]), grammar)
    summary = {"vocab": len(itos), "chance_loss": r(math.log(len(itos))),
               "numpy": np.__version__, "probe_who": who, "runs": {}}
    for run in cfg["runs"]:
        out = run_one(run, cfg, grammar, fixtures, stoi, itos, allset, who)
        (results / f"run-{run['id']}.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        summary["runs"][run["id"]] = {k: v for k, v in out.items() if k != "log"}
        print(run["id"], json.dumps({k: out[k] for k in ("start", "best", "final", "floor_val", "gap_final")},
                                    ensure_ascii=False))
    (results / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:3])
