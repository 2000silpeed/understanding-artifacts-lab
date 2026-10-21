#!/usr/bin/env python3
"""Kahn topological sort with a FIFO ready queue and trace-backed snapshots."""
from __future__ import annotations

import json
import sys
from typing import Dict, List, Optional, Tuple

VERTICES = ["A", "B", "C", "D", "E", "F"]
DEFAULT_GRAPH = {
    "A": ["C"],
    "B": ["C", "D"],
    "C": ["E"],
    "D": ["E"],
    "E": [],
    "F": [],
}
TRANSFER_GRAPH = {**{v: list(edges) for v, edges in DEFAULT_GRAPH.items()}, "E": ["B"]}


def validate_graph(graph: Dict[str, List[str]]) -> None:
    vertices = set(graph)
    seen: set[Tuple[str, str]] = set()
    for source, edges in graph.items():
        for dest in edges:
            if dest not in vertices:
                raise ValueError("invalid endpoint")
            edge = (source, dest)
            if edge in seen:
                raise ValueError("duplicate edge rejected")
            seen.add(edge)


def snapshot(queue: List[str], indegree: Dict[str, int], output: List[str], processed: List[str]) -> dict:
    return {
        "queue": list(queue),
        "indegree": dict(indegree),
        "output": list(output),
        "processed": list(processed),
    }


def kahn(graph: Dict[str, List[str]]) -> dict:
    validate_graph(graph)
    vertices = list(graph)
    indegree = {vertex: 0 for vertex in vertices}
    for edges in graph.values():
        for dest in edges:
            indegree[dest] += 1
    queue = [vertex for vertex in vertices if indegree[vertex] == 0]
    output: List[str] = []
    processed: List[str] = []
    events: List[dict] = []

    def event(kind: str, *, vertex: Optional[str] = None, source: Optional[str] = None,
              dest: Optional[str] = None, value: Optional[int] = None) -> None:
        events.append({
            "time": len(events),
            "kind": kind,
            "vertex": vertex,
            "from": source,
            "to": dest,
            "value": value,
            **snapshot(queue, indegree, output, processed),
        })

    event("init")
    while queue:
        vertex = queue.pop(0)
        output.append(vertex)
        processed.append(vertex)
        event("pop", vertex=vertex)
        for dest in graph[vertex]:
            indegree[dest] -= 1
            event("decrement", source=vertex, dest=dest, value=indegree[dest])
            if indegree[dest] == 0:
                queue.append(dest)
                event("enqueue", vertex=dest)
    has_cycle = len(output) != len(vertices)
    event("done", value=len(vertices) - len(output))
    return {
        "vertices": vertices,
        "order": output,
        "has_cycle": has_cycle,
        "remaining": [vertex for vertex in vertices if vertex not in processed],
        "final_indegree": indegree,
        "events": events,
    }


def rejected(graph: Dict[str, List[str]]) -> dict:
    try:
        kahn(graph)
    except ValueError as exc:
        return {"accepted": False, "error": str(exc)}
    raise AssertionError("scenario should be rejected")


def build_trace() -> dict:
    scenarios = {
        "default": kahn(DEFAULT_GRAPH),
        "transfer": kahn(TRANSFER_GRAPH),
        "empty": kahn({}),
        "single": kahn({"X": []}),
        "disconnected": kahn({"A": ["B"], "B": [], "C": [], "D": [], "E": [], "F": []}),
        "self_loop": kahn({"X": ["X"]}),
        "duplicate": rejected({"A": ["B", "B"], "B": []}),
        "invalid_endpoint": rejected({"A": ["Z"], "B": []}),
    }
    return {
        "contract": {
            "algorithm": "topological_sort_kahn",
            "graph_kind": "directed",
            "dependency_meaning": "u -> v means u must be processed before v",
            "queue_policy": "FIFO; initial zero-indegree vertices follow input order",
            "zero_indegree": "indegree counts remaining incoming edges",
            "cycle_rule": "cycle exists when processed output length is smaller than vertex count",
            "complexity": "O(V + E)",
            "instrumentation": "each event stores a full queue, indegree, output, and processed snapshot; this is separate from algorithm cost",
            "duplicate_edges": "rejected before execution",
            "self_loops": "accepted by validation and make a cycle",
            "vertices": VERTICES,
            "default_adjacency": DEFAULT_GRAPH,
            "transfer_adjacency": TRANSFER_GRAPH,
        },
        "scenarios": scenarios,
    }


def compact(value: List[str]) -> str:
    return "->".join(value) if value else "[]"


def summary(trace: dict, names: List[str]) -> str:
    lines = []
    for name in names:
        scenario = trace["scenarios"][name]
        if not scenario.get("accepted", True):
            lines.append(f"{name}: rejected={scenario['error']}")
        else:
            lines.append(
                f"{name}: order={compact(scenario['order'])} cycle={'true' if scenario['has_cycle'] else 'false'}"
            )
            if scenario["has_cycle"]:
                lines.append(f"{name}: remaining={compact(scenario['remaining'])}")
    return "\n".join(lines) + "\n"


def main() -> int:
    trace = build_trace()
    if "--trace" in sys.argv:
        print(json.dumps(trace, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    elif "--edge" in sys.argv:
        print(summary(trace, ["empty", "single", "disconnected", "self_loop", "duplicate", "invalid_endpoint"]), end="")
    elif "--transfer" in sys.argv:
        print(summary(trace, ["transfer"]), end="")
    else:
        print(summary(trace, ["default"]), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
