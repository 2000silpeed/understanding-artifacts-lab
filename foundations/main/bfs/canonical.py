#!/usr/bin/env python3
"""Deterministic undirected BFS with event-boundary snapshots.

The algorithm marks a vertex visited when it is enqueued.  Every trace record
shows the unprocessed queue suffix after exactly one enqueue, dequeue, or
neighbor decision.  Snapshot/JSON copying is teaching instrumentation, not
part of the algorithmic O(V+E) bound.
"""
import json
import sys

GRAPH = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D", "E"],
    "D": ["B", "C", "F"],
    "E": ["C", "F"],
    "F": ["D", "E"],
    "G": [],
}


def bfs(start, target=None, graph=GRAPH):
    visited = {start}
    distance = {start: 0}
    parent = {start: None}
    queue = [start]
    head = 0
    order = []
    records = []

    def record(kind, vertex, source=None, action=None):
        records.append({
            "kind": kind,
            "vertex": vertex,
            "from": source,
            "action": action,
            "queue": queue[head:],
            "visited": sorted(visited),
            "distance": dict(distance),
            "parent": dict(parent),
        })

    record("enqueue", start, None, "enqueue")
    while head < len(queue):
        u = queue[head]
        head += 1
        order.append(u)
        record("dequeue", u, None, "dequeue")
        for v in graph.get(u, []):
            if v not in visited:
                visited.add(v)
                distance[v] = distance[u] + 1
                parent[v] = u
                queue.append(v)
                record("enqueue", v, u, "enqueue")
            else:
                record("skip", v, u, "skip")
        if target is not None and u == target:
            break

    path = []
    if target in distance:
        cur = target
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
    return {
        "start": start,
        "target": target,
        "order": queue[:head] + queue[head:],
        "distance": distance,
        "parent": parent,
        "path": path,
        "records": records,
    }


def main():
    result = bfs("A", "F")
    edge = bfs("A", "G")
    if "--trace" in sys.argv:
        print(json.dumps({"graph": GRAPH, "canonical": result, "unreachable": edge}, ensure_ascii=False, separators=(",", ":")))
    else:
        print("graph=undirected stable adjacency")
        print("start=A target=F")
        print("order=" + "->".join(result["order"]))
        print("distance(F)=" + str(result["distance"]["F"]))
        print("path=" + "->".join(result["path"]))
        print("unreachable G=" + str("G" not in edge["distance"]).lower())


if __name__ == "__main__":
    main()
