#!/usr/bin/env python3
"""Executable linked-list contract for the lesson.

The trace is produced by the same pointer operations that produce the stdout.
It deliberately counts logical link writes, not allocator or object-destruction work.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import sys
from typing import Optional


@dataclass
class Node:
    value: int
    next: Optional["Node"] = None


class SinglyLinkedList:
    def __init__(self, values: list[int] | None = None) -> None:
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        for value in values or []:
            self.append(value)

    def append(self, value: int) -> int:
        node = Node(value)
        if self.head is None:
            self.head = self.tail = node
            return 0
        assert self.tail is not None
        self.tail.next = node
        self.tail = node
        return 1

    def values(self) -> list[int]:
        result: list[int] = []
        node = self.head
        while node is not None:
            result.append(node.value)
            node = node.next
        return result

    def index_at(self, index: int) -> tuple[int, int]:
        if index < 0:
            raise IndexError("negative index")
        node = self.head
        steps = 0
        while node is not None and steps < index:
            node = node.next
            steps += 1
        if node is None:
            raise IndexError("index out of range")
        return node.value, steps

    def find(self, value: int) -> tuple[int, int]:
        node = self.head
        position = 0
        while node is not None:
            if node.value == value:
                return position, position
            node = node.next
            position += 1
        return -1, position

    def node_at(self, index: int) -> Node:
        node = self.head
        for _ in range(index):
            if node is None:
                raise IndexError("index out of range")
            node = node.next
        if node is None:
            raise IndexError("index out of range")
        return node

    def insert_after(self, predecessor: Node, value: int) -> int:
        new_node = Node(value, predecessor.next)
        predecessor.next = new_node
        if self.tail is predecessor:
            self.tail = new_node
        return 2

    def delete_after(self, predecessor: Node) -> tuple[int, int]:
        target = predecessor.next
        if target is None:
            raise IndexError("no node after predecessor")
        predecessor.next = target.next
        if self.tail is target:
            self.tail = predecessor
        return target.value, 1


def arrow(values: list[int]) -> str:
    return " -> ".join(map(str, values)) + " -> null"


def make_trace() -> dict:
    linked = SinglyLinkedList([10, 20, 30, 40])
    index_value, index_steps = linked.index_at(2)
    found_position, lookup_steps = linked.find(40)
    predecessor = linked.node_at(1)
    before_insert = linked.values()
    insert_links = linked.insert_after(predecessor, 25)
    after_insert = linked.values()
    inserted_position, inserted_steps = linked.find(25)
    removed, delete_links = linked.delete_after(predecessor)
    after_delete = linked.values()
    empty = SinglyLinkedList()
    empty_state = empty.values()
    append_links = empty.append(50)
    return {
        "initial": before_insert,
        "index_access": {"index": 2, "value": index_value, "visited": [10, 20, 30], "steps": index_steps},
        "lookup": {"value": 40, "position": found_position, "visited": [10, 20, 30, 40], "steps": lookup_steps},
        "insert_after": {"predecessor": 20, "value": 25, "link_updates": insert_links, "state": after_insert},
        "lookup_after_insert": {"value": 25, "position": inserted_position, "steps": inserted_steps},
        "delete_after": {"predecessor": 20, "removed": removed, "link_updates": delete_links, "state": after_delete},
        "boundaries": {"empty_head": None, "empty_length": len(empty_state), "append_value": 50, "append_link_updates": append_links, "tail": 50, "state": empty.values()},
        "costs": {"index_access": "O(n)", "known_predecessor_insert": "O(1)", "position_search": "O(n)", "delete_requires_predecessor": True},
    }


def emit_stdout(trace: dict) -> str:
    lines = [
        f"LIST initial={arrow(trace['initial'])}",
        f"INDEX index=2 value={trace['index_access']['value']} visited={len(trace['index_access']['visited'])} steps={trace['index_access']['steps']}",
        f"LOOKUP value=40 position={trace['lookup']['position']} visited={len(trace['lookup']['visited'])} steps={trace['lookup']['steps']}",
        f"INSERT_AFTER predecessor=20 value=25 link_updates={trace['insert_after']['link_updates']} state={arrow(trace['insert_after']['state'])}",
        f"LOOKUP_AFTER value=25 position={trace['lookup_after_insert']['position']} steps={trace['lookup_after_insert']['steps']}",
        f"DELETE_AFTER predecessor=20 removed={trace['delete_after']['removed']} link_updates={trace['delete_after']['link_updates']} state={arrow(trace['delete_after']['state'])}",
        f"EMPTY head=null length={trace['boundaries']['empty_length']}",
        f"APPEND value=50 tail={trace['boundaries']['tail']} link_updates={trace['boundaries']['append_link_updates']} state={arrow(trace['boundaries']['state'])}",
        "COST index_access=O(n) known_predecessor_insert=O(1) position_search=O(n) delete_requires_predecessor=true",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    trace = make_trace()
    if "--trace" in sys.argv:
        print(json.dumps(trace, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        sys.stdout.write(emit_stdout(trace))
