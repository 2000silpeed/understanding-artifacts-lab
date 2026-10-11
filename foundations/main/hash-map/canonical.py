#!/usr/bin/env python3
"""Toy separate chaining; instrumentation snapshots are excluded from map bounds."""
import json
import sys

class ToyMap:
    def __init__(self):
        self.buckets = [[] for _ in range(4)]

    def snapshot(self):
        return [[{'key': k, 'value': v} for k, v in chain] for chain in self.buckets]

    def execute(self, op, key, value=None):
        before = self.snapshot()
        record = {'op': op, 'key': key, 'value': value, 'before': before,
                  'bucket': None, 'comparisons': [], 'events': []}
        if type(key) is not int or key < 0:
            record.update(result='invalid_key', after=self.snapshot())
            record['events'].append({'kind': 'reject'})
            return record
        bucket = key % 4
        record['bucket'] = bucket
        record['events'].append({'kind': 'select', 'bucket': bucket})
        chain = self.buckets[bucket]
        found = None
        for i, (stored_key, _) in enumerate(chain):
            equal = stored_key == key
            comparison = {'stored_key': stored_key, 'query_key': key, 'equal': equal}
            record['comparisons'].append(comparison)
            record['events'].append({'kind': 'compare', **comparison})
            if equal:
                found = i
                break
        if op == 'put':
            if found is None:
                chain.append((key, value))
                result = 'inserted'
            else:
                chain[found] = (key, value)
                result = 'updated'
        elif op == 'get':
            result = chain[found][1] if found is not None else None
        elif op == 'delete':
            result = found is not None
            if found is not None:
                chain.pop(found)
        else:
            raise ValueError('unknown operation')
        record['events'].append({'kind': 'finish', 'result': result})
        record.update(result=result, after=self.snapshot())
        return record

CANONICAL = [('put', 2, '사과'), ('put', 6, '배'), ('put', 3, '귤'),
             ('get', 6, None), ('put', 6, '포도'), ('delete', 2, None), ('get', 10, None)]
EDGES = [('get', 0, None), ('delete', 0, None), ('put', -1, '금지'),
         ('get', -1, None), ('delete', -1, None), ('put', 0, '영'),
         ('put', 4, '넷'), ('put', 4, '새 값'), ('delete', 8, None),
         ('get', 4, None), ('delete', 0, None), ('get', 0, None)]

def execution(operations):
    m = ToyMap()
    return {'bucket_count': 4, 'key_domain': 'nonnegative_integer',
            'rule': 'key%4', 'initial': m.snapshot(),
            'records': [m.execute(*args) for args in operations]}

if __name__ == '__main__':
    record = execution(EDGES if '--edges' in sys.argv else CANONICAL)
    output = record if '--trace' in sys.argv else [r['result'] for r in record['records']]
    print(json.dumps(output, ensure_ascii=False, separators=(',', ':')))
