#!/usr/bin/env python3
"""Executable recursion contract for the 2026-10-08 lesson."""
from __future__ import annotations

import json
import sys

MAX_N = 8


def _check(n: int) -> None:
    if n < 0 or n > MAX_N:
        raise ValueError("n must be between 0 and 8")


def sum_to(n: int) -> int:
    _check(n)
    if n == 0:
        return 0
    return n + sum_to(n - 1)


def iterative_sum_to(n: int) -> int:
    _check(n)
    total = 0
    for value in range(n + 1):
        total += value
    return total


def trace_case(n: int) -> dict[str, object]:
    _check(n)
    calls: list[int] = []
    returns: list[dict[str, int]] = []

    def visit(value: int) -> int:
        calls.append(value)
        if value == 0:
            returns.append({"n": 0, "value": 0})
            return 0
        result = value + visit(value - 1)
        returns.append({"n": value, "value": result})
        return result

    result = visit(n)
    return {
        "input": n,
        "calls": calls,
        "returns": returns,
        "result": result,
        "call_count": len(calls),
        "max_depth": len(calls),
        "shrinks": all(calls[i + 1] == calls[i] - 1 for i in range(len(calls) - 1)),
    }


def make_trace() -> dict[str, object]:
    return {"max_n": MAX_N, "cases": {"n0": trace_case(0), "n3": trace_case(3), "n4": trace_case(4)}}


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--trace":
        print(json.dumps(make_trace(), ensure_ascii=False, separators=(",", ":")))
        return
    print("sum_to(4) = 4 + 3 + 2 + 1 + 0 = 10")
    print("sum_to(0) = 0")
    print("iterative_sum_to(4) = 10")
    print("bounded input: 0 <= n <= 8")
    try:
        sum_to(-1)
    except ValueError:
        print("negative input rejected: -1")


if __name__ == "__main__":
    main()
