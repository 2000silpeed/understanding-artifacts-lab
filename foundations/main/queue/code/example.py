#!/usr/bin/env python3
"""Executable FIFO queue contract for the lesson."""
from __future__ import annotations

import json
import sys
from collections import deque


class Queue:
    def __init__(self) -> None:
        self.items: deque[int] = deque()

    def enqueue(self, value: int) -> None:
        self.items.append(value)

    def front(self) -> int:
        if not self.items:
            raise IndexError("empty")
        return self.items[0]

    def dequeue(self) -> int:
        if not self.items:
            raise IndexError("empty")
        return self.items.popleft()

    def state(self) -> list[int]:
        return list(self.items)


def make_trace() -> dict:
    queue = Queue()
    for value in (12, 35, 8):
        queue.enqueue(value)
    initial = queue.state()

    queue.enqueue(47)
    after_enqueue = {"value": 47, "state": queue.state()}
    front_value = queue.front()
    front = {"value": front_value, "state": queue.state()}
    dequeued = queue.dequeue()
    after_dequeue = {"value": dequeued, "state": queue.state()}

    queue.enqueue(19)
    exercise_after_enqueue = {"value": 19, "state": queue.state()}
    exercise_dequeued = queue.dequeue()
    exercise_after_dequeue = {"value": exercise_dequeued, "state": queue.state()}

    empty = Queue()
    empty_front_guard = "missing"
    empty_dequeue_guard = "missing"
    try:
        empty.front()
    except IndexError as error:
        empty_front_guard = str(error)
    try:
        empty.dequeue()
    except IndexError as error:
        empty_dequeue_guard = str(error)

    return {
        "initial": initial,
        "after_enqueue": after_enqueue,
        "front": front,
        "after_dequeue": after_dequeue,
        "exercise": {
            "after_enqueue": exercise_after_enqueue,
            "after_dequeue": exercise_after_dequeue,
        },
        "empty": {
            "front_guard": empty_front_guard,
            "dequeue_guard": empty_dequeue_guard,
            "state": empty.state(),
        },
        "costs": {
            "cpp_std_queue_default_deque_front": "O(1)",
            "cpp_std_queue_default_deque_pop": "O(1)",
            "cpp_std_queue_default_deque_push": "O(1)",
            "python_deque_popleft": "O(1)",
            "python_deque_append": "O(1)",
            "python_list_pop_zero": "O(n)",
            "order_note": "logical order only; physical layout unspecified",
        },
    }


def list_text(values: list[int]) -> str:
    return "[" + ",".join(str(value) for value in values) + "]"


def emit_stdout(trace: dict) -> str:
    lines = [
        f"QUEUE initial={list_text(trace['initial'])}",
        f"ENQUEUE value={trace['after_enqueue']['value']} state={list_text(trace['after_enqueue']['state'])}",
        f"FRONT value={trace['front']['value']} state={list_text(trace['front']['state'])}",
        f"DEQUEUE value={trace['after_dequeue']['value']} remaining={list_text(trace['after_dequeue']['state'])}",
        f"EXERCISE enqueue={trace['exercise']['after_enqueue']['value']} state={list_text(trace['exercise']['after_enqueue']['state'])}",
        f"EXERCISE dequeue={trace['exercise']['after_dequeue']['value']} remaining={list_text(trace['exercise']['after_dequeue']['state'])}",
        f"EMPTY front_guard={trace['empty']['front_guard']} dequeue_guard={trace['empty']['dequeue_guard']}",
        "COST deque_append=O(1) deque_popleft=O(1) list_pop_zero=O(n) std_queue_default_deque=O(1)",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    trace = make_trace()
    if "--trace" in sys.argv:
        print(json.dumps(trace, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        sys.stdout.write(emit_stdout(trace))
