#!/usr/bin/env python3
import json
import math
import sys

W = [[-0.1, -0.1, 0.2], [-0.2, -0.2, 0.4]]
E = [[0.0, 1.0], [1.0, 2.0], [-1.0, 1.0]]
INPUT_ID = 1
TARGET_ID = 2
LEARNING_RATE = 0.3
EPSILON = 1e-6


def validate(w, e, input_id, target, lr):
    if len(w) != 2 or any(len(row) != 3 for row in w):
        raise ValueError("W shape")
    if len(e) != 3 or any(len(row) != 2 for row in e):
        raise ValueError("E shape")
    if not all(math.isfinite(x) for row in w for x in row):
        raise ValueError("W finite")
    if not all(math.isfinite(x) for row in e for x in row):
        raise ValueError("E finite")
    if type(input_id) is not int or input_id not in range(3):
        raise ValueError("input_id")
    if type(target) is not int or target not in range(3):
        raise ValueError("target_id")
    if not math.isfinite(lr) or lr < 0:
        raise ValueError("learning_rate")


def vector_for(e, input_id):
    if type(input_id) is not int or input_id not in range(3):
        raise ValueError("input_id")
    return e[input_id][:]


def logits(h, w):
    if len(h) != 2 or len(w) != 2 or any(len(row) != 3 for row in w):
        raise ValueError("shape")
    return [sum(h[i] * w[i][j] for i in range(2)) for j in range(3)]


def softmax(z):
    if len(z) != 3 or not all(math.isfinite(x) for x in z):
        raise ValueError("logits")
    top = max(z)
    exp_values = [math.exp(x - top) for x in z]
    total = sum(exp_values)
    return [x / total for x in exp_values]


def loss_from(z, target):
    p = softmax(z)
    if type(target) is not int or target not in range(3):
        raise ValueError("target_id")
    return -math.log(p[target])


def forward(h, w, target):
    z = logits(h, w)
    p = softmax(z)
    y = [1.0 if j == target else 0.0 for j in range(3)]
    g = [p[j] - y[j] for j in range(3)]
    return {"z": z, "p": p, "loss": -math.log(p[target]), "g": g}


def input_gradient(h, w, g):
    return [sum(w[i][j] * g[j] for j in range(3)) for i in range(2)]


def dE_for(input_id, dh):
    d = [[0.0, 0.0] for _ in range(3)]
    d[input_id] = dh[:]
    return d


def update_embedding(e, input_id, dh, lr):
    updated = [row[:] for row in e]
    updated[input_id] = [e[input_id][i] - lr * dh[i] for i in range(2)]
    return updated


def finite_difference(e, input_id, w, target, eps=EPSILON):
    result = []
    for i in range(2):
        plus = [row[:] for row in e]
        minus = [row[:] for row in e]
        plus[input_id][i] += eps
        minus[input_id][i] -= eps
        lp = loss_from(logits(plus[input_id], w), target)
        lm = loss_from(logits(minus[input_id], w), target)
        result.append((lp - lm) / (2.0 * eps))
    return result


def calculate(w=W, e=E, input_id=INPUT_ID, target=TARGET_ID, lr=LEARNING_RATE):
    validate(w, e, input_id, target, lr)
    h = vector_for(e, input_id)
    initial = forward(h, w, target)
    dh = input_gradient(h, w, initial["g"])
    dE = dE_for(input_id, dh)
    e_prime = update_embedding(e, input_id, dh, lr)
    h_prime = vector_for(e_prime, input_id)
    updated = forward(h_prime, w, target)
    return {
        "w": [row[:] for row in w],
        "e": [row[:] for row in e],
        "input_id": input_id,
        "target_id": target,
        "learning_rate": lr,
        "selected_row": input_id,
        "h": h,
        "initial": initial,
        "dh": dh,
        "dE": dE,
        "finite_difference": finite_difference(e, input_id, w, target),
        "E_prime": e_prime,
        "h_prime": h_prime,
        "updated": updated,
    }


def build_trace():
    main = calculate()
    transfer = calculate(input_id=0)
    zero_w = calculate(w=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    zero_input = calculate(e=[[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]], input_id=1)
    return {
        "contract": {
            "W": main["w"],
            "E": main["e"],
            "input_id": main["input_id"],
            "target_id": main["target_id"],
            "learning_rate": main["learning_rate"],
            "selected_row": main["selected_row"],
            "bias": False,
        },
        "main": main,
        "transfer": transfer,
        "zero_W": {"dh": zero_w["dh"], "dE": zero_w["dE"], "g": zero_w["initial"]["g"]},
        "zero_input": {"dh": zero_input["dh"], "dE": zero_input["dE"]},
    }


def fmt(value):
    return format(value, ".12f")


def vec(values):
    return "[" + ",".join(fmt(x) for x in values) + "]"


def mat(values):
    return "[" + ";".join(",".join(fmt(x) for x in row) for row in values) + "]"


def stdout_lines(trace):
    main = trace["main"]
    updated = main["updated"]
    transfer = trace["transfer"]
    return [
        "EMBEDDING_INPUT_ROW_UPDATE",
        "W=" + mat(main["w"]) + " E=" + mat(main["e"]),
        "input_id=1 h=" + vec(main["h"]) + " target_id=2 lr=" + fmt(main["learning_rate"]),
        "z=" + vec(main["initial"]["z"]) + " p=" + vec(main["initial"]["p"]) + " loss=" + fmt(main["initial"]["loss"]),
        "g=" + vec(main["initial"]["g"]) + " dh=" + vec(main["dh"]) + " dE=" + mat(main["dE"]),
        "finite_difference=" + vec(main["finite_difference"]),
        "E_prime=" + mat(main["E_prime"]) + " h_prime=" + vec(main["h_prime"]),
        "z_prime=" + vec(updated["z"]) + " p_prime=" + vec(updated["p"]) + " loss_prime=" + fmt(updated["loss"]),
        "transfer_input_id=0 h=" + vec(transfer["h"]) + " z=" + vec(transfer["initial"]["z"]) + " dh=" + vec(transfer["dh"]),
        "zero_W_dh=" + vec(trace["zero_W"]["dh"]) + " zero_input_dh=" + vec(trace["zero_input"]["dh"]),
    ]


def main():
    trace = build_trace()
    if "--trace" in sys.argv:
        print(json.dumps(trace, ensure_ascii=False, separators=(",", ":")))
    else:
        print("\n".join(stdout_lines(trace)))


if __name__ == "__main__":
    main()
