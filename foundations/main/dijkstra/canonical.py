#!/usr/bin/env python3
"""다익스트라의 교육용 단순 array-scan canonical implementation.

Contract: directed graph, integer edge weights >= 0, strict improvement only,
lexicographic vertex tie-break for the array scan, and stop only after target
is settled. Every event stores one post-action snapshot.
"""
from __future__ import annotations
import json
import sys
from typing import Dict, List, Optional, Tuple

INF = None
VERTICES = ["A", "B", "C", "D", "E"]
DEFAULT_GRAPH = {
    "A": [("B", 4), ("C", 1)],
    "B": [("D", 1)],
    "C": [("B", 2), ("D", 5)],
    "D": [],
    "E": [],
}
TRANSFER_GRAPH = {
    "A": [("B", 4), ("C", 1)],
    "B": [("D", 1)],
    "C": [("B", 2), ("D", 1)],
    "D": [],
    "E": [],
}
EDGE_SCENARIOS = {
    "unreachable": (DEFAULT_GRAPH, "A", "E"),
    "start_target": (DEFAULT_GRAPH, "A", "A"),
    "zero_weight": ({"A": [("B", 0), ("C", 2)], "B": [("C", 0)], "C": []}, "A", "C"),
    "tie": ({"A": [("B", 1), ("C", 1)], "B": [("D", 1)], "C": [("D", 1)], "D": []}, "A", "D"),
}


def _snapshot(dist: Dict[str, Optional[int]], parent: Dict[str, Optional[str]], settled: List[str]) -> dict:
    return {
        "distances": {v: dist[v] for v in VERTICES if v in dist},
        "parents": {v: parent[v] for v in VERTICES if v in parent},
        "settled": list(settled),
    }


def dijkstra(graph: Dict[str, List[Tuple[str, int]]], start: str, target: Optional[str] = None) -> dict:
    vertices = list(graph)
    if start not in graph:
        raise ValueError("unknown start")
    for source, edges in graph.items():
        for dest, weight in edges:
            if dest not in graph:
                raise ValueError("unknown destination")
            if not isinstance(weight, int) or weight < 0:
                raise ValueError("negative weight rejected")
    dist: Dict[str, Optional[int]] = {v: INF for v in vertices}
    parent: Dict[str, Optional[str]] = {v: None for v in vertices}
    settled: List[str] = []
    dist[start] = 0
    events: List[dict] = []

    def add_event(kind: str, *, vertex=None, source=None, dest=None,
                  old_candidate=None, new_candidate=None,
                  old_parent=None, new_parent=None, improved=False,
                  reason=None, stop=False):
        event = {
            "kind": kind,
            "vertex": vertex,
            "from": source,
            "to": dest,
            "old_candidate": old_candidate,
            "new_candidate": new_candidate,
            "old_parent": old_parent,
            "new_parent": new_parent,
            "improved": improved,
            "reason": reason,
            "stop": stop,
        }
        event.update(_snapshot(dist, parent, settled))
        events.append(event)

    while True:
        candidates = [v for v in vertices if v not in settled and dist[v] is not None]
        if not candidates:
            add_event("done", reason="no reachable unsettled vertex")
            break
        u = min(candidates, key=lambda v: (dist[v], v))
        old = dist[u]
        settled.append(u)
        stopping = target is not None and u == target
        add_event("settle", vertex=u, old_candidate=old, new_candidate=old,
                  reason="target settled" if stopping else "minimum unsettled distance",
                  stop=stopping)
        if stopping:
            break
        for v, weight in graph[u]:
            if v in settled:
                add_event("consider", source=u, dest=v, old_candidate=dist[v],
                          new_candidate=dist[v], old_parent=parent[v], new_parent=parent[v],
                          reason="destination already settled")
                continue
            old_candidate = dist[v]
            assert dist[u] is not None
            candidate = dist[u] + weight
            improved = old_candidate is None or candidate < old_candidate
            old_parent = parent[v]
            if improved:
                dist[v] = candidate
                parent[v] = u
            add_event("relax", source=u, dest=v, old_candidate=old_candidate,
                      new_candidate=candidate if improved else old_candidate,
                      old_parent=old_parent, new_parent=parent[v], improved=improved,
                      reason="strictly smaller candidate" if improved else "tie or larger candidate")

    found = target is not None and dist.get(target) is not None
    path: List[str] = []
    if found:
        current: Optional[str] = target
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
    return {
        "start": start,
        "target": target,
        "found": found,
        "distance": dist.get(target) if target is not None else None,
        "path": path,
        "distances": dist,
        "parents": parent,
        "events": events,
    }


def build_trace() -> dict:
    scenarios = {"default": dijkstra(DEFAULT_GRAPH, "A", "D")}
    for name, (graph, start, target) in EDGE_SCENARIOS.items():
        scenarios[name] = dijkstra(graph, start, target)
    scenarios["transfer"] = dijkstra(TRANSFER_GRAPH, "A", "D")
    negative_error = None
    try:
        dijkstra({"A": [("B", -1)], "B": []}, "A", "B")
    except ValueError as exc:
        negative_error = str(exc)
    scenarios["negative"] = {"accepted": False, "error": negative_error}
    return {
        "contract": {
            "algorithm": "dijkstra_nonnegative",
            "graph_kind": "directed",
            "selection": "minimum unsettled distance by array scan; ties use lexicographic vertex order",
            "tie_policy": "strict improvement only; equal candidates keep the existing parent",
            "early_stop": "stop only after target is settled",
            "complexity": "O(V^2 + E)",
            "instrumentation": "event snapshots copy distances, parents, and settled; this is separate from algorithm cost",
            "infinity": "null in JSON, distinct from numeric zero",
            "negative_weights": "rejected before execution; nonnegative proof is out of scope",
            "vertices": VERTICES,
            "default_adjacency": DEFAULT_GRAPH,
            "transfer_adjacency": TRANSFER_GRAPH,
        },
        "scenarios": scenarios,
    }


def summary(trace: dict) -> str:
    lines = []
    for name in ["default", "unreachable", "start_target", "zero_weight", "tie", "transfer"]:
        s = trace["scenarios"][name]
        if s["found"]:
            suffix = " parent=D:B" if name == "tie" else ""
            lines.append(f"{name}: path={'->'.join(s['path'])} distance={s['distance']}{suffix}")
        else:
            lines.append(f"{name}: found=false")
    lines.append(f"negative: rejected={trace['scenarios']['negative']['error']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    trace = build_trace()
    if "--negative" in sys.argv:
        try:
            dijkstra({"A": [("B", -1)], "B": []}, "A", "B")
        except ValueError as exc:
            print(f"rejected: {exc}")
            return 0
        return 1
    if "--trace" in sys.argv:
        print(json.dumps(trace, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        print(summary(trace), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
