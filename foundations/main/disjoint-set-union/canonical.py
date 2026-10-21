#!/usr/bin/env python3
"""Canonical disjoint-set union contract for the 2026-10-21 DS lesson."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass


@dataclass
class DSU:
    n: int

    def __post_init__(self) -> None:
        self.parent = list(range(self.n))
        self.size = [1] * self.n
        self.events: list[dict] = []

    def snapshot(self) -> dict:
        return {"parent": self.parent[:], "size": self.size[:]}

    def path_to_root(self, x: int) -> list[int]:
        path = [x]
        while path[-1] != self.parent[path[-1]]:
            path.append(self.parent[path[-1]])
        return path

    def valid(self, x: int) -> str | None:
        if x < 0:
            return "negative_id"
        if x >= self.n:
            return "out_of_range"
        return None

    def record(self, operation: str, a: int, b: int | None, result: str,
               roots: list[int], changed: bool,
               path_before: list | None = None,
               path_after: list | None = None) -> None:
        self.events.append({
            "operation": operation,
            "a": a,
            "b": b,
            "result": result,
            "roots": roots,
            "changed": changed,
            "path_before": path_before if path_before is not None else [],
            "path_after": path_after if path_after is not None else [],
            "snapshot": self.snapshot(),
        })

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != x:
            nxt = self.parent[x]
            self.parent[x] = root
            x = nxt
        return root

    def find_observed(self, x: int) -> int | None:
        reason = self.valid(x)
        if reason:
            self.record("find", x, None, reason, [], False)
            return None
        before = self.path_to_root(x)
        root = self.find(x)
        after = self.path_to_root(x)
        self.record("find", x, None, "root", [root], before != after, [before], [after])
        return root

    def union(self, a: int, b: int) -> dict:
        reason_a = self.valid(a)
        reason_b = self.valid(b)
        if reason_a or reason_b:
            reason = reason_a or reason_b or "invalid_id"
            self.record("union", a, b, reason, [], False)
            return {"accepted": False, "reason": reason, "changed": False}
        before = [self.path_to_root(a), self.path_to_root(b)]
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            after = [self.path_to_root(a), self.path_to_root(b)]
            self.record("union", a, b, "already_same", [ra, rb], False, before, after)
            return {"accepted": True, "changed": False, "root": ra}
        if self.size[ra] < self.size[rb] or (self.size[ra] == self.size[rb] and rb < ra):
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        after = [self.path_to_root(a), self.path_to_root(b)]
        self.record("union", a, b, "merged", [ra, rb], True, before, after)
        return {"accepted": True, "changed": True, "root": ra}

    def same(self, a: int, b: int) -> dict:
        reason_a = self.valid(a)
        reason_b = self.valid(b)
        if reason_a or reason_b:
            reason = reason_a or reason_b or "invalid_id"
            self.record("same", a, b, reason, [], False)
            return {"accepted": False, "reason": reason, "result": False}
        before = [self.path_to_root(a), self.path_to_root(b)]
        ra = self.find(a)
        rb = self.find(b)
        result = ra == rb
        after = [self.path_to_root(a), self.path_to_root(b)]
        self.record("same", a, b, "true" if result else "false", [ra, rb], before != after, before, after)
        return {"accepted": True, "result": result}


def run_canonical() -> dict:
    dsu = DSU(6)
    initial = dsu.snapshot()
    unions = [dsu.union(0, 1), dsu.union(2, 3), dsu.union(1, 2)]
    path_before = dsu.path_to_root(3)
    dsu.find_observed(3)
    path_after = dsu.path_to_root(3)
    same_03 = dsu.same(0, 3)
    same_04 = dsu.same(0, 4)
    duplicate = dsu.union(0, 3)
    return {
        "input": list(range(6)),
        "initial": initial,
        "unions": unions,
        "find_3_path_before": path_before,
        "find_3_path_after": path_after,
        "queries": {"same_0_3": same_03, "same_0_4": same_04},
        "duplicate_union_0_3": duplicate,
        "events": dsu.events,
        "final": dsu.snapshot(),
    }


def run_edge() -> dict:
    empty = DSU(0)
    single = DSU(1)
    return {
        "n_zero": {
            "union_0_0": empty.union(0, 0),
            "same_0_0": empty.same(0, 0),
            "negative_find": empty.find_observed(-1),
            "events": empty.events,
            "final": empty.snapshot(),
        },
        "n_one": {
            "union_0_0": single.union(0, 0),
            "same_0_0": single.same(0, 0),
            "out_of_range_union": single.union(0, 1),
            "events": single.events,
            "final": single.snapshot(),
        },
    }


def run_transfer() -> dict:
    dsu = DSU(6)
    for pair in [(0, 1), (2, 3), (1, 2)]:
        dsu.union(*pair)
    dsu.union(4, 5)
    before = dsu.same(0, 5)
    join = dsu.union(3, 5)
    after = dsu.same(0, 5)
    return {
        "after_union_4_5_same_0_5": before,
        "union_3_5": join,
        "after_union_3_5_same_0_5": after,
        "final": dsu.snapshot(),
        "events": dsu.events,
    }


def trace() -> dict:
    return {"canonical": run_canonical(), "edge": run_edge(), "transfer": run_transfer()}


def compact(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def main() -> None:
    args = set(sys.argv[1:])
    if "--trace" in args:
        print(compact(trace()))
        return
    if "--edge" in args:
        edge = run_edge()
        print("edge n=0 union(0,0) accepted: false, reason: out_of_range")
        print("edge n=0 negative find accepted: false, reason: negative_id")
        print("edge n=1 self union changed: false")
        print("edge n=1 same(0,0): true")
        print("edge n=1 union(0,1) accepted: false, reason: out_of_range")
        print(f"edge trace events: {len(edge['n_zero']['events']) + len(edge['n_one']['events'])}")
        return
    if "--transfer" in args:
        transfer = run_transfer()
        print(f"transfer after union(4,5) same(0,5): {str(transfer['after_union_4_5_same_0_5']['result']).lower()}")
        print(f"transfer union(3,5) changed: {str(transfer['union_3_5']['changed']).lower()}")
        print(f"transfer after union(3,5) same(0,5): {str(transfer['after_union_3_5_same_0_5']['result']).lower()}")
        print(f"transfer final root size: {transfer['final']['size'][0]}")
        print(f"transfer trace events: {len(transfer['events'])}")
        return
    canonical = run_canonical()
    print("dsu input: [0,1,2,3,4,5]")
    print(f"union (0,1) changed: {str(canonical['unions'][0]['changed']).lower()}")
    print(f"union (2,3) changed: {str(canonical['unions'][1]['changed']).lower()}")
    print(f"union (1,2) changed: {str(canonical['unions'][2]['changed']).lower()}")
    print("find 3 before path: 3->2->0")
    print("find 3 after path: 3->0")
    print(f"same (0,3): {str(canonical['queries']['same_0_3']['result']).lower()}")
    print(f"same (0,4): {str(canonical['queries']['same_0_4']['result']).lower()}")
    print(f"duplicate union (0,3) changed: {str(canonical['duplicate_union_0_3']['changed']).lower()}")
    print(f"final parent: {canonical['final']['parent']}")
    print(f"final root size: {canonical['final']['size'][0]}")
    print(f"trace events: {len(canonical['events'])}")


if __name__ == "__main__":
    main()
