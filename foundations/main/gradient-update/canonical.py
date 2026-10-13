import math

LOGITS = [1.0, 0.0, -0.5]
TARGET_ID = 1
EPSILON = 1e-5
LEARNING_RATE = 0.4
LARGE_LEARNING_RATE = 20.0


def stable_softmax(logits):
    if not logits or not all(math.isfinite(x) for x in logits):
        raise ValueError("logits must be finite and non-empty")
    shift = max(logits)
    weights = [math.exp(x - shift) for x in logits]
    denominator = sum(weights)
    probabilities = [w / denominator for w in weights]
    if not all(math.isfinite(p) and p >= 0.0 for p in probabilities):
        raise ValueError("softmax produced invalid probability")
    return probabilities


def loss(logits, target_id):
    if not isinstance(target_id, int) or isinstance(target_id, bool) or not 0 <= target_id < len(logits):
        raise ValueError("target ID out of range")
    stable_softmax(logits)  # validate finite, nonempty logits
    shift = max(logits)
    value = (shift - logits[target_id]) + math.log(sum(math.exp(z - shift) for z in logits))
    if not math.isfinite(value):
        raise ValueError("loss outside finite numeric range")
    return value


def analytic_gradient(logits, target_id):
    if not isinstance(target_id, int) or isinstance(target_id, bool) or not 0 <= target_id < len(logits):
        raise ValueError("target ID out of range")
    probabilities = stable_softmax(logits)
    gradient = probabilities[:]
    gradient[target_id] -= 1.0
    return gradient


def finite_difference(logits, target_id, epsilon):
    values = []
    for i in range(len(logits)):
        plus = logits[:]
        minus = logits[:]
        plus[i] += epsilon
        minus[i] -= epsilon
        values.append((loss(plus, target_id) - loss(minus, target_id)) / (2.0 * epsilon))
    return values


def update(logits, gradient, learning_rate):
    return [z - learning_rate * g for z, g in zip(logits, gradient)]


def fmt(values):
    return "[" + ", ".join(f"{x:.6f}" for x in values) + "]"


def main():
    p = stable_softmax(LOGITS)
    y = [0.0, 1.0, 0.0]
    g = analytic_gradient(LOGITS, TARGET_ID)
    fd = finite_difference(LOGITS, TARGET_ID, EPSILON)
    new_logits = update(LOGITS, g, LEARNING_RATE)
    new_p = stable_softmax(new_logits)
    large_logits = update(LOGITS, g, LARGE_LEARNING_RATE)
    large_p = stable_softmax(large_logits)
    print("initial logits: " + fmt(LOGITS))
    print("initial probabilities: " + fmt(p))
    print("target probability: " + f"{p[TARGET_ID]:.15f}")
    print("initial loss: " + f"{loss(LOGITS, TARGET_ID):.15f}")
    print("finite difference gradient: " + fmt(fd))
    print("p-minus-y gradient: " + fmt(g))
    print("gradient sum: " + f"{sum(g):.15f}")
    print("small learning rate: 0.400000")
    print("updated logits: " + fmt(new_logits))
    print("updated probabilities: " + fmt(new_p))
    print("updated target probability: " + f"{new_p[TARGET_ID]:.15f}")
    print("updated loss: " + f"{loss(new_logits, TARGET_ID):.15f}")
    print("large learning rate: 20.000000")
    print("large-step target probability: " + f"{large_p[TARGET_ID]:.15f}")
    print("large-step loss: " + f"{loss(large_logits, TARGET_ID):.15f}")
    print("boundary: stable softmax; toy logits only; no transformer training")


if __name__ == "__main__":
    main()
