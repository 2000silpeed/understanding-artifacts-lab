#!/usr/bin/env python3
"""Explicit two-token context concatenation contract, stdlib only."""
import json
import math
import sys

TOKENS = ["a", "b", "c"]
IDS = {token: i for i, token in enumerate(TOKENS)}
E = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
W = [[1.0, 0.0, -1.0], [0.0, 1.0, 0.0], [0.0, -1.0, 1.0], [1.0, 0.0, 0.0]]
SEQUENCE = ["a", "b", "c", "a"]


def stable_softmax(z):
    if not z or not all(math.isfinite(value) for value in z):
        raise ValueError("logits must be finite and non-empty")
    top = max(z)
    weights = [math.exp(value - top) for value in z]
    total = sum(weights)
    return [value / total for value in weights]


def concatenate(first, second):
    return list(first) + list(second)


def dot_products(h):
    """Return every operand, product, and prefix sum used to form hW."""
    if len(h) != len(W):
        raise ValueError("h width must match W rows")
    details = []
    for j in range(len(W[0])):
        terms = []
        partial_sums = []
        total = 0.0
        for i, value in enumerate(h):
            product = value * W[i][j]
            if product == 0:
                product = 0.0
            total += product
            if total == 0:
                total = 0.0
            terms.append({"left": value, "right": W[i][j], "product": product})
            partial_sums.append(total)
        details.append({"output_id": j, "terms": terms, "partial_sums": partial_sums, "result": total})
    return details


def logits(h):
    return [column["result"] for column in dot_products(h)]


def forward(context_ids):
    if len(context_ids) != 2 or any(i < 0 or i >= len(E) for i in context_ids):
        raise ValueError("context must contain two valid ids")
    h = concatenate(E[context_ids[0]], E[context_ids[1]])
    products = dot_products(h)
    z = [column["result"] for column in products]
    p = stable_softmax(z)
    return {"context_ids": list(context_ids), "h": h, "dot_products": products, "z": z, "p": p, "prediction_id": max(range(len(p)), key=p.__getitem__)}


def build_training_pairs(sequence):
    """Fixed window: target is the next item, never a future item beyond it."""
    if len(sequence) < 3:
        raise ValueError("sequence needs two context tokens and one target")
    pairs = []
    for i in range(len(sequence) - 2):
        context = sequence[i:i + 2]
        target = sequence[i + 2]
        pairs.append({"context": context, "context_ids": [IDS[token] for token in context], "target": target, "target_id": IDS[target], "future_tokens_excluded": sequence[i + 3:]})
    return pairs


def vec_text(values):
    return "[" + ",".join(f"{value:.6f}" for value in values) + "]"


def context_text(context_ids):
    return "[" + ",".join(TOKENS[i] for i in context_ids) + "]"


def pair_text(pair):
    return f"{context_text(pair['context_ids'])}->{pair['target']} future_excluded=[{','.join(pair['future_tokens_excluded'])}]"


def display(trace):
    contract = trace["contract"]
    main = trace["main"]
    reverse = trace["reverse"]
    transfer = trace["transfer"]
    average = trace["average"]
    pairs = trace["training_pairs"]
    e_rows = len(contract["E"])
    e_cols = len(contract["E"][0])
    w_rows = len(contract["W"])
    w_cols = len(contract["W"][0])
    lines = [
        f"contract E={e_rows}x{e_cols} h=1x{contract['hidden_width']} W={w_rows}x{w_cols} context_length={contract['context_length']}",
        f"{context_text(main['context_ids'])} -> h={vec_text(main['h'])} z={vec_text(main['z'])}",
        f"{context_text(reverse['context_ids'])} -> h={vec_text(reverse['h'])} z={vec_text(reverse['z'])}",
        f"order_preserved={str(average['same']).lower()} average_ab=average_ba={vec_text(average['ab'])}",
        f"stable_softmax_sum={trace['stable_softmax_sum']:.6f} prediction_ab={contract['tokens'][main['prediction_id']]}",
        f"pair_0={pair_text(pairs[0])}",
        f"pair_1={pair_text(pairs[1])}",
        f"transfer={context_text(transfer['context_ids'])}->h={vec_text(transfer['h'])} z={vec_text(transfer['z'])}",
        f"p_ab={vec_text(main['p'])} p_ba={vec_text(reverse['p'])} p_transfer={vec_text(transfer['p'])}",
    ]
    return "\n".join(lines) + "\n"


def main_trace():
    ab = forward([IDS["a"], IDS["b"]])
    ba = forward([IDS["b"], IDS["a"]])
    ca = forward([IDS["c"], IDS["a"]])
    average_ab = [(E[0][i] + E[1][i]) / 2 for i in range(2)]
    average_ba = [(E[1][i] + E[0][i]) / 2 for i in range(2)]
    return {
        "contract": {"tokens": TOKENS, "E": E, "W": W, "context_length": 2, "embedding_dim": 2, "hidden_width": 4, "vocab_size": 3, "window": 2},
        "main": ab,
        "reverse": ba,
        "transfer": ca,
        "average": {"ab": average_ab, "ba": average_ba, "same": average_ab == average_ba},
        "training_pairs": build_training_pairs(SEQUENCE),
        "stable_softmax_sum": sum(ab["p"]),
    }


if __name__ == "__main__":
    trace = main_trace()
    if "--trace" in sys.argv:
        print(json.dumps(trace, ensure_ascii=False, separators=(",", ":")))
    else:
        sys.stdout.write(display(trace))
