#!/usr/bin/env python3
"""Executable LIFO stack contract for the lesson."""
from __future__ import annotations

import json
import sys


class Stack:
    def __init__(self) -> None:
        self.items: list[int] = []

    def push(self, value: int) -> None:
        self.items.append(value)

    def top(self) -> int:
        if not self.items:
            raise IndexError("underflow")
        return self.items[-1]

    def pop(self) -> int:
        if not self.items:
            raise IndexError("underflow")
        return self.items.pop()

    def state(self) -> list[int]:
        return list(self.items)


def make_trace() -> dict:
    stack = Stack()
    for value in (10, 20, 30):
        stack.push(value)
    after_push = stack.state()
    top_value = stack.top()
    popped = stack.pop()
    after_pop = stack.state()
    second_pop = stack.pop()
    after_second_pop = stack.state()

    empty = Stack()
    empty_pop_error = "missing"
    empty_top_error = "missing"
    try:
        empty.pop()
    except IndexError as error:
        empty_pop_error = str(error)
    try:
        empty.top()
    except IndexError as error:
        empty_top_error = str(error)

    return {
        "after_push": after_push,
        "top": {"value": top_value, "state": after_push},
        "after_pop": {"value": popped, "state": after_pop},
        "second_pop": {"value": second_pop, "state": after_second_pop},
        "empty": {"pop_error": empty_pop_error, "top_error": empty_top_error, "state": empty.state()},
        "costs": {
            "push_amortized": "O(1)",
            "push_worst": "O(n)",
            "pop_logical": "O(1)",
            "python_pop_amortized": "O(1)",
            "python_pop_worst": "O(n) possible shrink/reallocation",
            "cpp_vector_pop_back": "O(1) for int",
            "top": "O(1)",
            "resize_note": "dynamic array relocation",
        },
    }


def list_text(values: list[int]) -> str:
    return "[" + ",".join(str(value) for value in values) + "]"


def emit_stdout(trace: dict) -> str:
    lines = [
        f"STACK after_push={list_text(trace['after_push'])}",
        f"TOP value={trace['top']['value']}",
        f"POP value={trace['after_pop']['value']} remaining={list_text(trace['after_pop']['state'])}",
        f"SECOND_POP value={trace['second_pop']['value']} remaining={list_text(trace['second_pop']['state'])}",
        f"EMPTY pop_error={trace['empty']['pop_error']} top_error={trace['empty']['top_error']}",
        "COST top=O(1) logical_pop=O(1) python_pop_amortized=O(1) python_pop_worst=O(n) cpp_vector_pop_back=O(1)",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    trace = make_trace()
    if "--trace" in sys.argv:
        print(json.dumps(trace, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        sys.stdout.write(emit_stdout(trace))
