import math

# Source-only toy contract: public embedding lookup [0, 2] and hand-chosen W.
EMBEDDING = [0.0, 2.0]
W = [[1.0, 0.0, -1.0], [0.0, 1.0, 2.0]]


def matmul_row(x, matrix):
    return [sum(x[r] * matrix[r][c] for r in range(len(x))) for c in range(len(matrix[0]))]


def stable_softmax(logits):
    peak = max(logits)
    shifted = [z - peak for z in logits]
    weights = [math.exp(z) for z in shifted]
    denominator = sum(weights)
    probabilities = [w / denominator for w in weights]
    return peak, shifted, weights, denominator, probabilities


def fixed(value):
    return f'{value:.6f}'


def fixed_values(values):
    return ','.join(fixed(value) for value in values)


def main():
    logits = matmul_row(EMBEDDING, W)
    peak, shifted, weights, denominator, probabilities = stable_softmax(logits)
    displayed_probabilities = [float(fixed(value)) for value in probabilities]
    print('embedding: [' + fixed_values(EMBEDDING) + ']')
    print('W shape: [2, 3]')
    print('logits: [' + fixed_values(logits) + ']')
    print('max(logits): ' + fixed(peak))
    print('shifted: [' + fixed_values(shifted) + ']')
    print('positive weights exp(shifted): [' + fixed_values(weights) + ']')
    print('denominator: ' + fixed(denominator))
    print('probabilities: [' + fixed_values(probabilities) + ']')
    print('prediction: class 2')
    print('displayed probability sum: ' + fixed(sum(displayed_probabilities)))
    print('floating normalization sum: ' + fixed(sum(probabilities)) + ' (before display rounding)')
    print('equal logits transfer: each probability = 1/3 (exact)')


if __name__ == '__main__':
    main()
