import math

# Frozen toy probability vectors. These are hand-set examples, not model output.
PROBABILITIES = [0.1, 0.7, 0.2]
PRIMARY_TARGET_ID = 1
COMPARISON_TARGET_ID = 0


def validate_probability(probability):
    if not math.isfinite(probability) or probability <= 0.0 or probability > 1.0:
        raise ValueError("probability must satisfy 0 < p <= 1; p=0 has mathematical loss +infinity")


def validate_target(target_id, probabilities):
    if not isinstance(target_id, int) or isinstance(target_id, bool):
        raise ValueError("target token ID must be an integer")
    if target_id < 0 or target_id >= len(probabilities):
        raise ValueError("target token ID is outside the probability vector")


def next_token_loss(probabilities, target_id):
    validate_target(target_id, probabilities)
    target_probability = probabilities[target_id]
    validate_probability(target_probability)
    return -math.log(target_probability)


def fixed(value):
    return f"{value:.6f}"


def full(value):
    return f"{value:.15f}"


def main():
    primary_loss = next_token_loss(PROBABILITIES, PRIMARY_TARGET_ID)
    comparison_loss = next_token_loss(PROBABILITIES, COMPARISON_TARGET_ID)
    mean_loss = (primary_loss + comparison_loss) / 2.0

    print("probabilities: [" + ",".join(fixed(value) for value in PROBABILITIES) + "]")
    print("target token ID: 1")
    print("target probability: 0.700000")
    print("loss full: " + full(primary_loss))
    print("loss displayed rounded: " + fixed(primary_loss))
    print("comparison target token ID: 0")
    print("comparison target probability: 0.100000")
    print("comparison loss full: " + full(comparison_loss))
    print("comparison loss displayed rounded: " + fixed(comparison_loss))
    print("mean of two losses full: " + full(mean_loss))
    print("mean of two losses displayed rounded: " + fixed(mean_loss))
    print("validation: p=0 rejected; mathematical loss limit is +infinity")
    print("validation: p=1.2 rejected; target token ID=3 rejected")
    print("boundary: toy probabilities only; no training, gradient, autograd, framework, or Transformer inference")


if __name__ == "__main__":
    main()
