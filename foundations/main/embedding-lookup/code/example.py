#!/usr/bin/env python3
"""Dependency-free one-hot to embedding lookup contract."""

E = [[1, 0], [0, 2], [-1, 1]]
IDS = [0, 1, 0, 2]


def check_id(index):
    if index < 0 or index >= len(E):
        raise IndexError("id must satisfy 0 <= id < vocab_size")


def one_hot(index):
    check_id(index)
    result = [0] * len(E)
    result[index] = 1
    return result


def matmul_one_hot(weights, matrix):
    if len(weights) != len(matrix):
        raise ValueError("shape mismatch")
    return [sum(weights[row] * matrix[row][col] for row in range(len(matrix)))
            for col in range(len(matrix[0]))]


def lookup(index):
    weights = one_hot(index)
    weighted_rows = [[weights[row] * value for value in E[row]] for row in range(len(E))]
    output = matmul_one_hot(weights, E)
    return weights, weighted_rows, output


def main():
    assert (len(E), len(E[0])) == (3, 2)
    weights, weighted_rows, output = lookup(1)
    sequence = [lookup(index)[2] for index in IDS]
    assert output == E[1] == [0, 2]
    assert sequence == [[1, 0], [0, 2], [1, 0], [-1, 1]]
    assert sequence[0] == sequence[2]
    for bad in (3, -1):
        try:
            lookup(bad)
        except IndexError:
            pass
        else:
            raise AssertionError("invalid id accepted")
    print("lesson: one-hot-to-embedding lookup")
    print("vocab: a=0,b=1,c=2")
    print("E shape: 3x2")
    print("E rows: [1,0] [0,2] [-1,1]")
    print("id=1 onehot: [0,1,0]")
    print("id=1 weighted_rows: [0,0] [0,2] [0,0]")
    print("id=1 output: [0,2]")
    print("id=1 equals E[1]: true")
    print("sequence ids: [0,1,0,2]")
    print("sequence output shape: 4x2")
    print("sequence outputs: [1,0] [0,2] [1,0] [-1,1]")
    print("repeat id=0: true")
    print("invalid id=3: rejected")
    print("invalid id=-1: rejected")
    print("tests: shape=pass, lookup=pass, sequence=pass, bounds=pass")


if __name__ == "__main__":
    main()
