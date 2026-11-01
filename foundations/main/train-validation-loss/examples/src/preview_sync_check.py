"""Measures the short native preview against the plan: voice placement in the muxed AAC and caption first frames.

usage: python3 -B src/preview_sync_check.py <preview.mp4> <preview-render-receipts.json> <out.json>
Voice: each line whose WAV starts inside the preview is cross-correlated with the decoded AAC (±0.25 s around the
planned film time); the measured lag is reported in ms. Captions: the first frame each caption phrase is drawn (from the
render receipts) against round(plan time × 30). Needs numpy + ffmpeg. Measurement only; it changes nothing.
"""
import json, subprocess, sys, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parents[1]
mp4, rr_p, out_p = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
plan = json.loads((HERE / 'shots.json').read_text())
rr = json.loads(rr_p.read_text())
SR, FPS, B = 48000, plan['fps'], plan['music']['beatSeconds']
dur = rr['range'][1] / FPS
pcm = np.frombuffer(subprocess.check_output(['/opt/homebrew/bin/ffmpeg', '-v', 'error', '-i', str(mp4), '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']), dtype='<f4')
starts, b = {}, 0
for s in plan['shots']:
    starts.setdefault(s['scene'], s['startBeat'] * B)
voice, captions = [], []
for sid, v in plan['voice'].items():
    for l in v['lines']:
        if l['filmAt'] + l['len'] > dur:
            continue
        with wave.open(l['file']) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32) / 32768
        i0, W = int(round(l['filmAt'] * SR)), int(0.25 * SR)
        seg = pcm[max(0, i0 - W): i0 + len(x) + W]
        c = np.correlate(seg, x, mode='valid')
        lag = (np.argmax(c) + max(0, i0 - W) - i0) / SR
        voice.append({'line': l['id'], 'plannedFilmAt': l['filmAt'], 'measuredLagMs': round(lag * 1000, 2), 'corrPeakNorm': round(float(c.max() / (np.linalg.norm(x) ** 2 + 1e-9)), 3)})
        for p in l['phrases']:
            t = starts[sid] + l['at'] + p['start']
            first = next((x for x in rr['texts'] if x['kind'] == 'text' and x['text'] == p['text']), None)
            captions.append({'line': l['id'], 'text': p['text'], 'plannedFrame': round(t * FPS), 'plannedFrameCeil': int(np.ceil(t * FPS - 1e-9)), 'firstDrawnFrame': first and first['first'], 'lastDrawnFrame': first and first['last']})
lags = [v['measuredLagMs'] for v in voice]
ok_v = bool(voice) and all(abs(x) <= 500 / FPS for x in lags)  # within half a frame (16.7 ms)
ok_c = all(c['firstDrawnFrame'] == c['plannedFrameCeil'] for c in captions)
res = {'preview': str(mp4), 'rangeFrames': rr['range'], 'voice': voice, 'captions': captions,
       'voiceWithinHalfFrame': ok_v, 'voiceLagMs': {'min': min(lags), 'max': max(lags), 'spread': round(max(lags) - min(lags), 3)},
       'voiceLagNote': 'a constant lag on every line is a property of the audio chain (inference: pipeline/audio.py alimiter attack=4 ms look-ahead), not of the plan; recorded, not compensated', 'captionFirstFrameEqualsCeilOfAlignedStart': ok_c,
       'note': 'measurement of the actual muxed AAC and the renderer text receipts; not human listening'}
out_p.write_text(json.dumps(res, ensure_ascii=False, indent=1) + '\n')
print('voice', [(v['line'], v['measuredLagMs']) for v in voice]); print('captions ok', ok_c, [(c['text'][:12], c['plannedFrameCeil'], c['firstDrawnFrame']) for c in captions])
sys.exit(0 if ok_v and ok_c else 1)
