#!/usr/bin/env python3
"""Direct, instrumented binary-search-tree implementation for the lesson."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Optional

MAIN_INPUT = [8, 3, 10, 1, 6, 14, 4, 7, 13]
TRANSFER_INPUT = [5, 2, 8, 1, 3]

@dataclass
class Node:
    value: int
    left: Optional['Node'] = None
    right: Optional['Node'] = None


def level_snapshot(root: Optional[Node]):
    if root is None:
        return []
    queue: list[tuple[Optional[Node], int]] = [(root, 0)]
    positions: dict[int, int] = {}
    max_index = 0
    while queue:
        node, index = queue.pop(0)
        max_index = max(max_index, index)
        if node is None:
            continue
        positions[index] = node.value
        queue.append((node.left, index * 2 + 1))
        queue.append((node.right, index * 2 + 2))
    out: list[Optional[int]] = [None] * (max_index + 1)
    for index, value in positions.items():
        out[index] = value
    while out and out[-1] is None:
        out.pop()
    return out


def inorder(root: Optional[Node]):
    if root is None:
        return []
    return inorder(root.left) + [root.value] + inorder(root.right)


def height(root: Optional[Node]):
    if root is None:
        return 0
    return 1 + max(height(root.left), height(root.right))


def event(operation, value, current, direction, path, root, result, changed):
    return {
        "operation": operation,
        "value": value,
        "current": current,
        "direction": direction,
        "path": path[:],
        "snapshot": level_snapshot(root),
        "result": result,
        "changed": changed,
    }


def insert(root: Optional[Node], value: int, events: list[dict]):
    if root is None:
        root = Node(value)
        events.append(event("insert", value, None, "root", [], root, "inserted", True))
        return root, [value], True
    node = root
    path = []
    while True:
        path.append(node.value)
        if value == node.value:
            events.append(event("insert", value, node.value, "equal", path, root, "duplicate", False))
            return root, path, False
        if value < node.value:
            direction = "left"
            if node.left is None:
                node.left = Node(value)
                path2 = path + [value]
                events.append(event("insert", value, node.value, direction, path2, root, "inserted", True))
                return root, path2, True
            node = node.left
        else:
            direction = "right"
            if node.right is None:
                node.right = Node(value)
                path2 = path + [value]
                events.append(event("insert", value, node.value, direction, path2, root, "inserted", True))
                return root, path2, True
            node = node.right


def search(root: Optional[Node], value: int, events: list[dict]):
    node = root
    path = []
    while node is not None:
        path.append(node.value)
        if value == node.value:
            events.append(event("search", value, node.value, "equal", path, root, "found", False))
            return node, path
        if value < node.value:
            direction = "left"
            if node.left is None:
                events.append(event("search", value, node.value, direction, path, root, "missing", False))
                return None, path
            node = node.left
        else:
            direction = "right"
            if node.right is None:
                events.append(event("search", value, node.value, direction, path, root, "missing", False))
                return None, path
            node = node.right
    events.append(event("search", value, None, "empty", path, root, "missing", False))
    return None, path


def build(values):
    root = None
    events = []
    for value in values:
        root, _, _ = insert(root, value, events)
    return root, events


def run_main():
    root, events = build(MAIN_INPUT)
    _, path7 = search(root, 7, events)
    _, path5_missing = search(root, 5, events)
    root, path5_insert, inserted5 = insert(root, 5, events)
    _, path5_found = search(root, 5, events)
    root, path5_duplicate, duplicate5 = insert(root, 5, events)
    return {
        "input": MAIN_INPUT,
        "events": events,
        "search_7_path": path7,
        "search_5_missing_path": path5_missing,
        "insert_5_path": path5_insert,
        "search_5_found_path": path5_found,
        "duplicate_5_path": path5_duplicate,
        "duplicate_5_ignored": duplicate5 is False,
        "insert_5_changed": inserted5,
        "final_tree": level_snapshot(root),
        "inorder": inorder(root),
        "height": height(root),
    }


def run_edge():
    root = None
    events = []
    _, empty_search = search(root, 42, events)
    root, empty_insert_path, inserted = insert(root, 42, events)
    _, one_search = search(root, 42, events)
    return {
        "input": [],
        "events": events,
        "empty_search_path": empty_search,
        "insert_path": empty_insert_path,
        "one_node_search_path": one_search,
        "inserted": inserted,
        "final_tree": level_snapshot(root),
        "inorder": inorder(root),
        "height": height(root),
    }


def run_transfer():
    root, events = build(TRANSFER_INPUT)
    root, path, inserted = insert(root, 4, events)
    return {
        "input": TRANSFER_INPUT,
        "events": events,
        "insert_4_path": path,
        "inserted": inserted,
        "final_tree": level_snapshot(root),
        "inorder": inorder(root),
        "height": height(root),
    }


def trace():
    return {"canonical": run_main(), "edge": run_edge(), "transfer": run_transfer()}


def fmt(values):
    return json.dumps(values, ensure_ascii=False, separators=(",", ":"))


def main():
    args = set(sys.argv[1:])
    if "--trace" in args:
        print(json.dumps(trace(), ensure_ascii=False, separators=(",", ":")))
        return
    if "--edge" in args:
        e = run_edge()
        print(f"edge input: {fmt(e['input'])}")
        print(f"empty search(42) path: {fmt(e['empty_search_path'])}, found: false")
        print(f"insert(42) path: {fmt(e['insert_path'])}, inserted: {str(e['inserted']).lower()}")
        print(f"one-node search(42) path: {fmt(e['one_node_search_path'])}, found: true")
        print(f"edge final inorder: {fmt(e['inorder'])}")
        print(f"edge trace events: {len(e['events'])}")
        return
    if "--transfer" in args:
        t = run_transfer()
        print(f"transfer input: {fmt(t['input'])}")
        print(f"insert(4) path: {fmt(t['insert_4_path'])}, inserted: {str(t['inserted']).lower()}")
        print(f"transfer final tree: {fmt(t['final_tree'])}")
        print(f"transfer inorder: {fmt(t['inorder'])}")
        print(f"transfer height: {t['height']}")
        print(f"transfer trace events: {len(t['events'])}")
        return
    c = run_main()
    print(f"BST input: {fmt(c['input'])}")
    print(f"inorder before search: {fmt([1,3,4,6,7,8,10,13,14])}")
    print(f"search(7) path: {fmt(c['search_7_path'])}, found: true")
    print(f"search(5) path: {fmt(c['search_5_missing_path'])}, found: false")
    print(f"insert(5) path: {fmt(c['insert_5_path'])}, inserted: true")
    print(f"search(5) path: {fmt(c['search_5_found_path'])}, found: true")
    print(f"insert(5) path: {fmt(c['duplicate_5_path'])}, duplicate ignored: true")
    print(f"inorder after: {fmt(c['inorder'])}")
    print(f"final tree: {fmt(c['final_tree'])}")
    print(f"height: {c['height']}")
    print(f"trace events: {len(c['events'])}")


if __name__ == "__main__":
    main()
