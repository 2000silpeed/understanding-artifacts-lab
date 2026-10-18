#!/usr/bin/env python3
import json
import sys


def is_heap(a):
    return all(a[(i - 1) // 2] <= a[i] for i in range(1, len(a)))


def run(values, extra=None):
    heap = []
    events = []

    def snapshot(kind, value=None, index=None, parent=None, child=None, swapped=False, heap_state=None):
        current = heap if heap_state is None else heap_state
        events.append({
            "kind": kind,
            "value": value,
            "index": index,
            "parent": parent,
            "child": child,
            "swapped": swapped,
            "heap": current[:],
            "is_heap": is_heap(current),
        })

    for value in values + ([] if extra is None else [extra]):
        heap.append(value)
        snapshot("push_append", value=value, index=len(heap) - 1)
        i = len(heap) - 1
        while i > 0:
            p = (i - 1) // 2
            snapshot("push_compare", value=value, index=i, parent=p)
            if heap[p] <= heap[i]:
                break
            heap[p], heap[i] = heap[i], heap[p]
            snapshot("push_swap", value=value, index=i, parent=p, swapped=True)
            i = p

    initial = heap[:]
    snapshot("before_pop", heap_state=heap[:])
    if not heap:
        snapshot("empty_pop", heap_state=[])
        return {"input": values, "initial_heap": initial, "events": events,
                "pop_min": None, "after_pop": [], "peek": None}
    popped = heap[0]
    last = heap.pop()
    if heap:
        heap[0] = last
        snapshot("pop_move_last", value=popped, index=0)
        i = 0
        while True:
            left = 2 * i + 1
            right = left + 1
            if left >= len(heap):
                break
            child = left
            if right < len(heap) and heap[right] < heap[left]:
                child = right
            snapshot("pop_compare", value=popped, index=i, child=child)
            if heap[i] <= heap[child]:
                break
            heap[i], heap[child] = heap[child], heap[i]
            snapshot("pop_swap", value=popped, index=i, child=child, swapped=True)
            i = child
    snapshot("after_pop", value=popped, heap_state=heap[:])
    return {
        "input": values,
        "initial_heap": initial,
        "events": events,
        "pop_min": popped,
        "after_pop": heap,
        "peek": heap[0] if heap else None,
    }


def main():
    extra = 0 if "--alternate" in sys.argv else 3
    values = [9, 4, 7, 1] if "--alternate" in sys.argv else [4, 9, 7, 15, 12, 10]
    trace = {"canonical": run(values, extra), "edges": {
        "empty": run([]),
        "one": run([8]),
        "duplicates": run([5, 5, 2, 2]),
        "left_only": run([1, 2, 3]),
        "alternate": run([9, 4, 7, 1], 0),
    }}
    if "--trace" in sys.argv:
        print(json.dumps(trace, ensure_ascii=False, separators=(",", ":")))
        return
    c = trace["canonical"]
    base = run(c['input'])['initial_heap']
    print(f"initial input: {c['input']}")
    print(f"heap after pushes: {base}")
    print(f"push({extra}) heap: {c['initial_heap']}")
    print(f"pop_min(): {c['pop_min']}")
    print(f"heap after pop_min: {c['after_pop']}")
    print(f"heap property: {str(is_heap(c['after_pop'])).lower()}")
    print(f"pop trace events: {len(c['events'])}")


if __name__ == "__main__":
    main()
