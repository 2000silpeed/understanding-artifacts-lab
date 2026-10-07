#!/usr/bin/env python3
"""Insertion sort source of truth for the lesson.

Counts are logical events, not wall-clock measurements:
- comparisons: each value comparison a[j].value > key.value is evaluated.
- shifts: each existing item copied one cell to the right.
- inserts: one key placement per outer-loop pass, including a no-shift pass.
- writes: shifts + inserts.
The strict `>` keeps equal tagged items stable.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import sys
from typing import Iterable


@dataclass(frozen=True)
class Item:
    value: int
    label: str = ""

    def short(self) -> str:
        return f"{self.value}{self.label}"


def item_json(item: Item) -> dict[str, object]:
    return {"value": item.value, "label": item.label}


def sort_items(source: Iterable[Item]) -> tuple[list[Item], dict[str, object]]:
    arr = list(source)
    comparisons = 0
    shifts = 0
    inserts = 0
    steps: list[dict[str, object]] = []

    for i in range(1, len(arr)):
        before = list(arr)
        key = arr[i]
        j = i - 1
        step_shifts: list[dict[str, object]] = []
        # The saved key leaves one conceptual hole.  Each shift moves that
        # single hole one cell to the left; it never creates one hole per
        # shifted item.
        hole_path = [i]
        while j >= 0:
            comparisons += 1
            if arr[j].value <= key.value:
                break
            moved = arr[j]
            arr[j + 1] = moved
            step_shifts.append({"from": j, "to": j + 1, "item": item_json(moved)})
            shifts += 1
            hole_path.append(j)
            j -= 1
        insert_index = j + 1
        arr[insert_index] = key
        inserts += 1
        steps.append(
            {
                "i": i,
                "key": item_json(key),
                "before": [item_json(x) for x in before],
                "shifts": step_shifts,
                "insert_index": insert_index,
                "after": [item_json(x) for x in arr],
                "comparisons": len(step_shifts) + (1 if j >= 0 else 0),
                "shift_count": len(step_shifts),
                "hole_count": 1,
                "hole_index": insert_index,
                "hole_path": hole_path,
                "prefix_length": i + 1,
            }
        )

    counts = {
        "comparisons": comparisons,
        "shifts": shifts,
        "inserts": inserts,
        "writes": shifts + inserts,
    }
    return arr, {"steps": steps, "counts": counts}


def int_items(values: list[int]) -> list[Item]:
    return [Item(v) for v in values]


CASES: list[tuple[str, list[Item]]] = [
    ("main", int_items([8, 3, 5, 2])),
    ("practice", int_items([6, 1, 4, 2, 5])),
    ("best", int_items([1, 2, 3, 4])),
    ("worst", int_items([4, 3, 2, 1])),
    ("empty", []),
    ("single", int_items([7])),
    ("duplicates_tagged", [Item(2, "A"), Item(1, "X"), Item(2, "B"), Item(1, "Y")]),
]


def render_list(items: Iterable[Item]) -> str:
    return "[" + ", ".join(item.short() for item in items) + "]"


def expected_text() -> str:
    lines: list[str] = []
    for name, source in CASES:
        result, detail = sort_items(source)
        c = detail["counts"]
        if not isinstance(c, dict):
            raise TypeError("trace counts must be a dictionary")
        lines.extend(
            [
                f"CASE {name}",
                f"input: {render_list(source)}",
                f"sorted: {render_list(result)}",
                f"comparisons: {c['comparisons']}",
                f"shifts: {c['shifts']}",
                f"inserts: {c['inserts']}",
                f"writes: {c['writes']}",
            ]
        )
    return "\n".join(lines) + "\n"


def trace_document() -> dict[str, object]:
    cases: dict[str, object] = {}
    for name, source in CASES:
        result, detail = sort_items(source)
        cases[name] = {
            "input": [item_json(x) for x in source],
            "sorted": [item_json(x) for x in result],
            **detail,
        }
    return {
        "schema": "insertion-sort-trace-v1",
        "definitions": {
            "invariant": "after pass i, positions 0..i are sorted",
            "comparison": "one evaluation of a[j].value > key.value",
            "shift": "one existing item copied from j to j+1",
            "insert": "one placement of the saved key into j+1",
            "hole": "the saved key leaves exactly one conceptual hole; each shift moves it left",
            "writes": "shifts + inserts",
            "stability": "strict > leaves equal values in original order",
            "timing": "counts are logical events, never walltime",
        },
        "cases": cases,
    }


def main() -> int:
    if "--trace" in sys.argv[1:]:
        print(json.dumps(trace_document(), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        sys.stdout.write(expected_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
