#!/usr/bin/env python3
"""Canonical trie contract for the 2026-10-20 DS lesson."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Optional

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
BASE_WORDS = ["car", "cat", "dog"]

@dataclass
class Node:
    char: str
    parent: Optional[int]
    children: list[Optional[int]] = field(default_factory=lambda: [None] * 26)
    terminal: bool = False

class Trie:
    def __init__(self) -> None:
        self.nodes = [Node("", None)]
        self.events: list[dict] = []

    def snapshot(self) -> list[dict]:
        return [
            {"id": i, "parent": node.parent, "char": node.char, "terminal": node.terminal}
            for i, node in enumerate(self.nodes)
        ]

    def event(self, operation: str, word: str, index: int, action: str,
              node_id: Optional[int], result: str, changed: bool) -> None:
        self.events.append({
            "operation": operation,
            "word": word,
            "index": index,
            "char": word[index] if index < len(word) else None,
            "action": action,
            "node": node_id,
            "result": result,
            "changed": changed,
            "snapshot": self.snapshot(),
        })

    def validate(self, word: str) -> Optional[str]:
        if word == "":
            return "empty"
        if any(ch not in ALPHABET for ch in word):
            return "lowercase_a_z_only"
        return None

    def insert(self, word: str) -> dict:
        reason = self.validate(word)
        if reason:
            self.event("insert", word, 0, "reject", None, reason, False)
            return {"accepted": False, "reason": reason, "word": word}
        node_id = 0
        changed = False
        for index, char in enumerate(word):
            slot = ord(char) - ord("a")
            child = self.nodes[node_id].children[slot]
            if child is None:
                child = len(self.nodes)
                self.nodes[node_id].children[slot] = child
                self.nodes.append(Node(char, node_id))
                action = "create"
                changed = True
            else:
                action = "follow"
            node_id = child
            self.event("insert", word, index, action, node_id, "step", action == "create")
        already = self.nodes[node_id].terminal
        if not already:
            self.nodes[node_id].terminal = True
            changed = True
        self.event("terminal", word, len(word), "check", node_id,
                   "duplicate" if already else "marked", not already)
        return {"accepted": True, "word": word, "terminal": True, "changed": changed}

    def search(self, word: str, exact: bool) -> dict:
        operation = "exact" if exact else "prefix"
        reason = self.validate(word)
        if reason:
            self.event(operation, word, 0, "reject", None, reason, False)
            return {"query": word, "result": False, "reason": reason}
        node_id = 0
        for index, char in enumerate(word):
            child = self.nodes[node_id].children[ord(char) - ord("a")]
            if child is None:
                self.event(operation, word, index, "missing", None, "false", False)
                return {"query": word, "result": False}
            node_id = child
            self.event(operation, word, index, "follow", node_id, "step", False)
        result = self.nodes[node_id].terminal if exact else True
        self.event(operation, word, len(word), "terminal_check", node_id,
                   "true" if result else "false", False)
        return {"query": word, "result": result}

    def insert_words(self, words: list[str]) -> list[dict]:
        return [self.insert(word) for word in words]

def run_canonical() -> dict:
    trie = Trie()
    inserted = trie.insert_words(BASE_WORDS)
    queries = [trie.search("car", True), trie.search("ca", True),
               trie.search("ca", False), trie.search("cap", True)]
    ca_insert = trie.insert("ca")
    preserved = [trie.search("car", True), trie.search("cat", True)]
    duplicate = trie.insert("ca")
    return {
        "input": BASE_WORDS,
        "inserted": inserted,
        "queries": queries,
        "insert_ca": ca_insert,
        "preserved": preserved,
        "duplicate_ca": duplicate,
        "events": trie.events,
        "final_nodes": trie.snapshot(),
    }

def run_edge() -> dict:
    trie = Trie()
    empty = trie.insert("")
    uppercase = trie.insert("Car")
    missing = trie.search("cap", True)
    return {"input": [], "empty_insert": empty, "uppercase_insert": uppercase,
            "missing_search": missing, "events": trie.events, "final_nodes": trie.snapshot()}

def run_transfer() -> dict:
    trie = Trie()
    trie.insert_words(BASE_WORDS)
    before_exact = trie.search("do", True)
    before_prefix = trie.search("do", False)
    inserted = trie.insert("do")
    after_exact = trie.search("do", True)
    after_prefix = trie.search("do", False)
    dog_preserved = trie.search("dog", True)
    return {"input": BASE_WORDS, "before": {"exact_do": before_exact, "prefix_do": before_prefix},
            "insert_do": inserted, "after": {"exact_do": after_exact, "prefix_do": after_prefix,
            "exact_dog": dog_preserved}, "events": trie.events, "final_nodes": trie.snapshot()}

def trace() -> dict:
    return {"canonical": run_canonical(), "edge": run_edge(), "transfer": run_transfer()}

def fmt(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

def main() -> None:
    args = set(sys.argv[1:])
    if "--trace" in args:
        print(fmt(trace()))
        return
    if "--edge" in args:
        edge = run_edge()
        print(f"edge empty insert accepted: {str(edge['empty_insert']['accepted']).lower()}, reason: {edge['empty_insert']['reason']}")
        print(f"edge uppercase insert accepted: {str(edge['uppercase_insert']['accepted']).lower()}, reason: {edge['uppercase_insert']['reason']}")
        print(f"edge missing cap: {str(edge['missing_search']['result']).lower()}")
        print(f"edge trace events: {len(edge['events'])}")
        return
    if "--transfer" in args:
        transfer = run_transfer()
        print(f"transfer do before exact: {str(transfer['before']['exact_do']['result']).lower()}")
        print(f"transfer do before prefix: {str(transfer['before']['prefix_do']['result']).lower()}")
        print(f"transfer insert do changed: {str(transfer['insert_do']['changed']).lower()}")
        print(f"transfer do after exact: {str(transfer['after']['exact_do']['result']).lower()}")
        print(f"transfer do after prefix: {str(transfer['after']['prefix_do']['result']).lower()}")
        print(f"transfer dog preserved: {str(transfer['after']['exact_dog']['result']).lower()}")
        print(f"transfer trace events: {len(transfer['events'])}")
        return
    canonical = run_canonical()
    print(f"trie input: {fmt(canonical['input'])}")
    print(f"exact car: {str(canonical['queries'][0]['result']).lower()}")
    print(f"exact ca before terminal: {str(canonical['queries'][1]['result']).lower()}")
    print(f"prefix ca: {str(canonical['queries'][2]['result']).lower()}")
    print(f"exact cap: {str(canonical['queries'][3]['result']).lower()}")
    print(f"insert ca changed: {str(canonical['insert_ca']['changed']).lower()}")
    print(f"exact car preserved: {str(canonical['preserved'][0]['result']).lower()}")
    print(f"exact cat preserved: {str(canonical['preserved'][1]['result']).lower()}")
    print(f"duplicate ca changed: {str(canonical['duplicate_ca']['changed']).lower()}")
    print(f"final node count: {len(canonical['final_nodes'])}")
    print(f"trace events: {len(canonical['events'])}")

if __name__ == "__main__":
    main()
