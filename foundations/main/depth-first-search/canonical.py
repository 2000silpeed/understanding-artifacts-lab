#!/usr/bin/env python3
"""Canonical explicit-stack DFS contract for the Korean lesson.

Stack arrays are serialized bottom -> top, so the rightmost item is popped.
Neighbors are scanned in reverse adjacency order, and visited is marked when
an item is pushed. A target succeeds on its pop boundary.
"""
from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from typing import Dict, Iterable, List, Optional

MAIN: Dict[str, List[str]] = OrderedDict([
    ("A", ["B", "C"]),
    ("B", ["A", "D", "E"]),
    ("C", ["A", "F"]),
    ("D", ["B"]),
    ("E", ["B", "F"]),
    ("F", ["C", "E"]),
])
ALTERNATE: Dict[str, List[str]] = OrderedDict([
    ("P", ["Q", "R"]),
    ("Q", ["P", "S"]),
    ("R", ["P"]),
    ("S", ["Q"]),
])


def snapshot(stack: List[str], visited: Iterable[str], parent: Dict[str, Optional[str]]) -> dict:
    return {
        "stack": list(stack),
        "visited": list(visited),
        "parent": dict(parent),
    }


def dfs(graph: Dict[str, List[str]], start: str, target: Optional[str] = None) -> dict:
    stack: List[str] = []
    visited: List[str] = []
    visited_set = set()
    parent: Dict[str, Optional[str]] = OrderedDict()
    order: List[str] = []
    events: List[dict] = []

    def add_event(kind: str, **fields: object) -> None:
        event: dict = {"kind": kind}
        event.update(fields)
        event.update(snapshot(stack, visited, parent))
        events.append(event)

    if start not in graph:
        return {
            "start": start,
            "target": target,
            "order": order,
            "found": False,
            "parent": parent,
            "events": events,
        }

    visited_set.add(start)
    visited.append(start)
    parent[start] = None
    stack.append(start)
    add_event("push", vertex=start, from_vertex=None, reason="start")

    while stack:
        vertex = stack.pop()
        order.append(vertex)
        add_event("pop", vertex=vertex, target=(vertex == target))
        if target is not None and vertex == target:
            add_event("target_found", vertex=vertex)
            break
        for neighbor in reversed(graph.get(vertex, [])):
            if neighbor in visited_set:
                add_event("skip", from_vertex=vertex, to=neighbor, reason="visited")
                continue
            visited_set.add(neighbor)
            visited.append(neighbor)
            parent[neighbor] = vertex
            stack.append(neighbor)
            add_event("push", vertex=neighbor, from_vertex=vertex, reason="new")

    return {
        "start": start,
        "target": target,
        "order": order,
        "found": target is not None and bool(order) and order[-1] == target,
        "parent": parent,
        "events": events,
    }


def build_trace() -> dict:
    scenarios = OrderedDict([
        ("full", dfs(MAIN, "A")),
        ("early_target", dfs(MAIN, "A", "F")),
        ("unreachable", dfs(MAIN, "A", "Z")),
        ("cycle", dfs(MAIN, "E")),
        ("alternate", dfs(ALTERNATE, "P", "S")),
    ])
    return {
        "contract": {
            "graph": "fixed adjacency list",
            "adjacency": MAIN,
            "alternate_adjacency": ALTERNATE,
            "stack_orientation": "bottom_to_top_left_to_right",
            "stack_top": "rightmost_item",
            "neighbor_scan": "reverse_listed_order",
            "visited_mark": "at_push",
            "target_boundary": "success_on_pop",
            "duplicate_push": False,
        },
        "scenarios": scenarios,
    }


def display_order(order: List[str]) -> str:
    return ",".join(order) if order else "(empty)"


def main() -> None:
    parser = argparse.ArgumentParser(description="run the lesson DFS contract")
    parser.add_argument("--trace", action="store_true", help="print machine-readable trace JSON")
    args = parser.parse_args()
    trace = build_trace()
    if args.trace:
        print(json.dumps(trace, ensure_ascii=False, separators=(",", ":")))
        return
    scenarios = trace["scenarios"]
    print("DFS explicit-stack contract")
    print("full order: " + display_order(scenarios["full"]["order"]))
    print("early target F order: " + display_order(scenarios["early_target"]["order"]))
    print("unreachable Z order: " + display_order(scenarios["unreachable"]["order"]))
    print("cycle from E order: " + display_order(scenarios["cycle"]["order"]))
    print("alternate target S order: " + display_order(scenarios["alternate"]["order"]))
    print("full events: " + str(len(scenarios["full"]["events"])))


if __name__ == "__main__":
    main()
