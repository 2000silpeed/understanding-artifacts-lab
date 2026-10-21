#!/usr/bin/env python3
"""Stdlib-only hidden tanh forward contract for lesson-2026-10-21-llm."""
import json
import math
import sys

TOKENS = ["a", "b", "c"]
IDS = {token: i for i, token in enumerate(TOKENS)}
E = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
W1 = [[1.0, 0.0], [0.0, 1.0], [1.0, -1.0], [-1.0, 1.0]]
B1 = [0.0, 0.0]
W2 = [[1.0, 0.0, -1.0], [0.0, 1.0, 0.0]]
B2 = [0.0, 0.0, 0.0]


def validate_matrix(matrix, rows, cols, name):
    if len(matrix) != rows or any(len(row) != cols for row in matrix):
        raise ValueError(f"{name} shape must be {rows}x{cols}")
    if not all(math.isfinite(v) for row in matrix for v in row):
        raise ValueError(f"{name} must be finite")


def stable_softmax(z):
    if not z or not all(math.isfinite(v) for v in z):
        raise ValueError("logits must be finite and non-empty")
    peak = max(z)
    weights = [math.exp(v - peak) for v in z]
    total = sum(weights)
    return [v / total for v in weights]


def linear_details(values, weights, bias):
    if len(values) != len(weights) or not weights or any(len(row) != len(bias) for row in weights):
        raise ValueError("linear shape mismatch")
    details = []
    for j in range(len(bias)):
        terms = []
        partial = []
        total = bias[j]
        for i, value in enumerate(values):
            product = value * weights[i][j]
            if product == 0:
                product = 0.0
            total += product
            if total == 0:
                total = 0.0
            terms.append({"left": value, "right": weights[i][j], "product": product})
            partial.append(total)
        details.append({"output_id": j, "bias": bias[j], "terms": terms, "partial_sums": partial, "result": total})
    return details


def forward(context_ids, b1=None):
    if len(context_ids) != 2 or any(not isinstance(i, int) or i < 0 or i >= len(E) for i in context_ids):
        raise ValueError("context must contain two valid ids")
    validate_matrix(E, 3, 2, "E")
    validate_matrix(W1, 4, 2, "W1")
    validate_matrix(W2, 2, 3, "W2")
    first_bias = list(B1 if b1 is None else b1)
    if len(first_bias) != 2 or not all(math.isfinite(v) for v in first_bias):
        raise ValueError("b1 must have two finite values")
    x = list(E[context_ids[0]]) + list(E[context_ids[1]])
    linear1 = linear_details(x, W1, first_bias)
    u = [item["result"] for item in linear1]
    h = [math.tanh(v) for v in u]
    linear2 = linear_details(h, W2, B2)
    z = [item["result"] for item in linear2]
    p = stable_softmax(z)
    return {
        "context_ids": list(context_ids), "x": x, "b1": first_bias, "linear1": linear1,
        "u": u, "h": h, "linear2": linear2, "z": z, "p": p,
        "prediction_id": max(range(len(p)), key=p.__getitem__),
    }


def vec(values):
    return "[" + ",".join(f"{value:.6f}" for value in values) + "]"


def context(ids):
    return "[" + ",".join(TOKENS[i] for i in ids) + "]"


def display(trace, mode="default"):
    if mode == "transfer":
        item = trace["transfer"]
        return f"transfer={context(item['context_ids'])} x={vec(item['x'])} u={vec(item['u'])} h={vec(item['h'])} z={vec(item['z'])} p={vec(item['p'])}\n"
    if mode == "edge":
        edge = trace["edge_cases"]
        return "edge=" + ";".join(f"{k}:{v}" for k, v in edge.items()) + "\n"
    if mode == "shape":
        s = trace["shape_case"]
        return f"shape=input{tuple(s['input_shape'])} hidden{tuple(s['hidden_shape'])} output{tuple(s['output_shape'])}\n"
    main = trace["main"]
    reverse = trace["reverse"]
    bias = trace["bias_case"]
    return "\n".join([
        "contract tokens=3 ids=0,1,2 E=3x2 W1=4x2 W2=2x3",
        f"[a,b] x={vec(main['x'])} u={vec(main['u'])} h={vec(main['h'])} z={vec(main['z'])}",
        f"[b,a] x={vec(reverse['x'])} u={vec(reverse['u'])} h={vec(reverse['h'])} z={vec(reverse['z'])}",
        f"bias_b1=[1,-1] [a,b] u={vec(bias['u'])}",
        f"transfer [c,a] x={vec(trace['transfer']['x'])} u={vec(trace['transfer']['u'])} h={vec(trace['transfer']['h'])} z={vec(trace['transfer']['z'])}",
        f"softmax_sum_ab={sum(main['p']):.6f} prediction_ab={TOKENS[main['prediction_id']]}",
        f"p_ab={vec(main['p'])} p_ba={vec(reverse['p'])} p_transfer={vec(trace['transfer']['p'])}",
    ]) + "\n"


def main_trace():
    main = forward([IDS["a"], IDS["b"]])
    reverse = forward([IDS["b"], IDS["a"]])
    bias = forward([IDS["a"], IDS["b"]], [1.0, -1.0])
    transfer = forward([IDS["c"], IDS["a"]])
    edge_cases = {
        "invalid_id": "reject",
        "wrong_context_width": "reject",
        "empty_context": "reject",
        "single_context": "reject",
        "finite_probabilities": "true",
    }
    return {
        "contract": {"tokens": TOKENS, "ids": IDS, "E": E, "W1": W1, "B1": B1, "W2": W2, "B2": B2,
                      "shapes": {"x": [1, 4], "u": [1, 2], "h": [1, 2], "z": [1, 3], "p": [1, 3]},
                      "provenance": "toy hand-chosen weights; not learned"},
        "main": main, "reverse": reverse, "bias_case": bias, "transfer": transfer,
        "shape_case": {"input_shape": [1, 4], "hidden_shape": [1, 2], "output_shape": [1, 3]},
        "edge_cases": edge_cases,
        "stable_softmax_sum": sum(main["p"]),
    }


if __name__ == "__main__":
    trace = main_trace()
    if "--trace" in sys.argv:
        print(json.dumps(trace, ensure_ascii=False, separators=(",", ":")))
    elif "--transfer" in sys.argv:
        sys.stdout.write(display(trace, "transfer"))
    elif "--edge" in sys.argv:
        sys.stdout.write(display(trace, "edge"))
    elif "--shape" in sys.argv:
        sys.stdout.write(display(trace, "shape"))
    else:
        sys.stdout.write(display(trace))
