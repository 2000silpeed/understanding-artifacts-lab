"""Writes an SRT of the caption phrases the film draws, for a film-time range.

usage: python3 -B src/write_srt.py <out.srt> [--from <s>] [--to <s>]
Same rule as film.js CAP: a phrase is shown from its first aligned character until the next phrase in the scene starts,
or until 0.3 s after its last aligned character. Times = scene start + line offset + provider alignment (shots.json).
Phrases that start inside [from, to) are written, clipped to `to`, with times relative to `from`.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
plan = json.loads((HERE / 'shots.json').read_text())
arg = lambda k, d: float(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
t0, t1 = arg('--from', 0.0), arg('--to', float('inf'))
B = plan['music']['beatSeconds']
start = {}
for s in plan['shots']:
    start.setdefault(s['scene'], s['startBeat'] * B)
rows = []
for sid, v in plan['voice'].items():
    ph = [{'text': p['text'], 'at': l['at'] + p['start'], 'endVoice': l['at'] + p['end']} for l in v['lines'] for p in l['phrases']]
    for i, p in enumerate(ph):
        end = min(ph[i + 1]['at'], p['endVoice'] + 0.3) if i + 1 < len(ph) else p['endVoice'] + 0.3
        rows.append((start[sid] + p['at'], start[sid] + end, p['text']))
ms = lambda x: int(round(x * 1000))
ts = lambda x: f'{ms(x) // 3600000:02d}:{ms(x) // 60000 % 60:02d}:{ms(x) // 1000 % 60:02d},{ms(x) % 1000:03d}'
out = [f'{n}\n{ts(a - t0)} --> {ts(min(b, t1) - t0)}\n{text}\n' for n, (a, b, text) in enumerate((r for r in rows if t0 <= r[0] < t1), start=1)]
Path(sys.argv[1]).write_text('\n'.join(out), encoding='utf-8')
print('srt', sys.argv[1], 'cues', len(out), 'range', t0, t1)
