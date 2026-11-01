"""Toy Korean corpus for the lesson: five independent slots, four words each.

Every sentence is  WHO WHEN WHERE WHAT VERB.  The slots are chosen independently
and uniformly, so the true next-character distribution is known exactly:
inside a word the next syllable is fixed, and at the first syllable of each slot
there are four equally likely choices.  That gives an exact lower bound (the
"floor") for the cross-entropy any model can reach on fresh sentences.

Usage:  python -B src/corpus.py fixtures/grammar.json fixtures/
        writes all.txt, train_small.txt, train_large.txt, val.txt, test.txt
        (val = 멈출 시점을 고르는 데 쓰는 검증 세트, test = 마지막에 한 번만 재는 시험 세트)
"""
import json
import math
import random
import sys
from pathlib import Path

BOS, EOS = "^", "$"


def all_sentences(grammar):
    out = [""]
    for slot in grammar["slots"]:
        out = [(p + " " + w).strip() for p in out for w in slot["words"]]
    return [s + grammar["end"] for s in out]


def split(grammar):
    sents = all_sentences(grammar)
    order = list(range(len(sents)))
    random.Random(grammar["split_seed"]).shuffle(order)
    sz = grammar["sizes"]
    val = [sents[i] for i in order[: sz["val"]]]
    test = [sents[i] for i in order[sz["val"]: sz["val"] + sz["test"]]]
    rest = [sents[i] for i in order[sz["val"] + sz["test"]:]]
    large = rest[: sz["train_large"]]
    small = large[: sz["train_small"]]  # the small set is a prefix of the large one
    return {"all": sents, "val": val, "test": test, "train_small": small, "train_large": large}


def floor_nats_per_char(sentences, grammar):
    """Exact expected loss of the true distribution on these sentences.

    Only the first character of each slot is uncertain (ln K nats); every other
    character, the space, the full stop and the end marker are certain.
    """
    choice_points = 0
    for slot in grammar["slots"]:
        firsts = {w[0] for w in slot["words"]}
        assert len(firsts) == len(slot["words"]), "slot words must differ at the first syllable"
        choice_points += 1
    k = len(grammar["slots"][0]["words"])
    assert all(len(s["words"]) == k for s in grammar["slots"])
    targets = sum(len(s) + 1 for s in sentences)  # every character plus the end marker
    return choice_points * len(sentences) * math.log(k) / targets


def main(grammar_path, out_dir):
    grammar = json.loads(Path(grammar_path).read_text(encoding="utf-8"))
    parts = split(grammar)
    out = Path(out_dir)
    for name, rows in parts.items():
        (out / f"{name}.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(json.dumps({k: len(v) for k, v in parts.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main(*sys.argv[1:3])
