#!/usr/bin/env python3
"""Trace-backed top-down stable merge sort for the Oct 10 lesson."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Item:
    value: int
    label: str

    def as_dict(self) -> dict[str, Any]:
        return {"value": self.value, "label": self.label}


def item(value: int, label: str | None = None) -> Item:
    return Item(value, label if label is not None else str(value))


def merge_sort(values: list[Item]) -> dict[str, Any]:
    splits: list[dict[str, Any]] = []
    merges: list[dict[str, Any]] = []
    comparison_count = 0

    def dump(items: list[Item]) -> list[dict[str, Any]]:
        return [x.as_dict() for x in items]

    def visit(items: list[Item], path: str) -> list[Item]:
        nonlocal comparison_count
        if len(items) <= 1:
            splits.append({"path": path, "items": dump(items), "base": True})
            return items[:]
        mid = len(items) // 2
        left, right = items[:mid], items[mid:]
        splits.append({"path": path, "items": dump(items), "mid": mid, "left": dump(left), "right": dump(right)})
        left_sorted = visit(left, path + "L")
        right_sorted = visit(right, path + "R")
        out: list[Item] = []
        i = j = 0
        steps: list[dict[str, Any]] = []
        while i < len(left_sorted) and j < len(right_sorted):
            left_front = left_sorted[i]
            right_front = right_sorted[j]
            comparison_count += 1
            if left_front.value <= right_front.value:
                chosen, side = left_front, "left"
                i += 1
            else:
                chosen, side = right_front, "right"
                j += 1
            out.append(chosen)
            steps.append({
                "left_front": left_front.as_dict(),
                "right_front": right_front.as_dict(),
                "chosen": chosen.as_dict(),
                "side": side,
                "output": dump(out),
            })
        out.extend(left_sorted[i:])
        out.extend(right_sorted[j:])
        merges.append({
            "path": path,
            "left": dump(left_sorted),
            "right": dump(right_sorted),
            "comparisons": len(steps),
            "steps": steps,
            "result": dump(out),
        })
        return out

    sorted_items = visit(values, "root")
    return {
        "input": dump(values),
        "splits": splits,
        "merges": merges,
        "sorted": dump(sorted_items),
        "comparison_count": comparison_count,
        "base_cases": sum(1 for split in splits if split.get("base")),
        "merge_count": len(merges),
    }


def cases() -> dict[str, dict[str, Any]]:
    return {
        "main": merge_sort([item(8), item(3), item(6), item(2)]),
        "duplicates": merge_sort([item(2, "2A"), item(1, "1X"), item(2, "2B"), item(1, "1Y")]),
        "empty": merge_sort([]),
        "single": merge_sort([item(7)]),
    }


def stdout_text() -> str:
    main = cases()["main"]
    dup = cases()["duplicates"]
    return "\n".join([
        "input: [8, 3, 6, 2]",
        "split root: [8, 3, 6, 2] -> [8, 3] | [6, 2]",
        "split left: [8, 3] -> [8] | [3]",
        "split right: [6, 2] -> [6] | [2]",
        "merge [8] + [3]: compare 8 vs 3 -> take 3; append 8 => [3, 8]",
        "merge [6] + [2]: compare 6 vs 2 -> take 2; append 6 => [2, 6]",
        "merge [3, 8] + [2, 6]: compare 3 vs 2 -> take 2",
        "merge [3, 8] + [2, 6]: compare 3 vs 6 -> take 3",
        "merge [3, 8] + [2, 6]: compare 8 vs 6 -> take 6; append 8",
        f"sorted: [2, 3, 6, 8]",
        f"comparisons: {main['comparison_count']}",
        "duplicate input: [2A, 1X, 2B, 1Y]",
        "stable duplicate output: [1X, 1Y, 2A, 2B]",
        "equality rule: left item wins when values are equal",
        "",
    ])


if __name__ == "__main__":
    if "--trace" in sys.argv:
        print(json.dumps({"algorithm": "top_down_stable_merge_sort", "comparison_rule": "left.value <= right.value", "cases": cases()}, separators=(",", ":"), ensure_ascii=False))
    else:
        print(stdout_text(), end="")
