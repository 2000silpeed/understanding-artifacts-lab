"""Verifies the revised-opening inputs (7 new hook lines + the 36 original body lines + the existing Suno bed) before use.

usage: python3 -B src/hook43_inputs_check.py <out.json>
Checks, and exits 1 on any mismatch (measurement only; it changes nothing):
  - every file listed in the integration run's input-manifest.json has its recorded SHA-256, and the approved hashes;
  - the original 38-line ElevenLabs manifest and every original body WAV have their recorded hashes;
  - narration.json (revised, 43 lines): every body line's text/tts (UTF-8 bytes), claims and screen = the original 36 lines;
  - the 43-line manifest: order = script order, text = tts, hook WAVs = files in the run, body rows = the original rows
    (same WAV hash, samples, duration, provider alignment), and every WAV's header length = its recorded length;
  - the Suno files' durations by ffprobe (measured, not assumed).
"""
import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path

RUN = Path('/Users/sungwoon/ai-projects/topic-only-runs/20261029-train-validation-loss/integration-20261030-hook43')
INP = RUN / 'input'
ORIG = Path('/Users/sungwoon/ai-projects/topic-only-runs/20261029-train-validation-loss/parent-audio-20261029-1010')
APPROVED = {
    'audio/final-narration-manifest.json': '0591a75a4c8fc5dbe7053ea810d5078ad4ed0883f3978974ba5455be5f992d0c',
    'source/narration.json': '32373929756b894d3fd36ec513d2f603458974b24437dc73ba9c733355f98a20',
    'music/original-suno-bed.wav': '94144b42d72502664e3382eeac47b8091e710ce2d4540f0a788ec189acf9b54b',
    'music/derived-suno-same-track-loop-bed-317.8s.wav': '8e486b5901348a2255caad3fd1b2e0ef59f11bb4843eb6e67eec7900a1ebba0a',
}
ORIG_MANIFEST_SHA = 'e6cc68faba7487f40d51953a3e948dc26b3c41f341319ef1261e3938c90f2a55'
ORIG_NARRATION_SHA = 'd07b87442dfd594d419c62c1976824052f1087928a1fcd2d166b2dedd915ebe8'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
fails = []


def check(ok, what):
    if not ok:
        fails.append(what)
    return bool(ok)


def wav_len(p):
    with wave.open(str(p)) as w:
        return w.getnframes(), w.getframerate(), w.getnchannels()


# 1. supplied inputs
im = json.loads((RUN / 'input-manifest.json').read_text())
inputs = []
for f in im['files']:
    p = INP / f['path']
    h = sha(p)
    row = {'path': str(p), 'bytes': p.stat().st_size, 'sha256': h, 'recorded_sha256': f['sha256'],
           'match': check(h == f['sha256'] and p.stat().st_size == f['bytes'], f'input {f["path"]}')}
    if f['path'] in APPROVED:
        row['approved_sha256'] = APPROVED[f['path']]
        row['approved_match'] = check(h == APPROVED[f['path']], f'approved hash {f["path"]}')
    inputs.append(row)
check(set(APPROVED) <= {f['path'] for f in im['files']}, 'approved file missing from input-manifest')

# 2. original body recording
om_p = ORIG / 'eleven' / 'manifest.json'
om = json.loads(om_p.read_text())
check(sha(om_p) == ORIG_MANIFEST_SHA, 'original manifest hash')
check(om['status'] == 'COMPLETE' and len(om['lines']) == 38, 'original manifest shape')
orows = {l['cue']: l for l in om['lines']}
on_p = ORIG / 'source' / 'script' / 'narration.json'
check(sha(on_p) == ORIG_NARRATION_SHA, 'original narration hash')

# 3. narration: revised hook, body byte-for-byte
nn_p = INP / 'source' / 'narration.json'
nb, ob = nn_p.read_bytes(), on_p.read_bytes()
nn, on = json.loads(nb), json.loads(ob)
# The revised file is re-serialised (indent 2; the original is hand-wrapped), so whole-file bytes differ by whitespace.
# Byte equality is checked where it matters: the UTF-8 bytes of every body line's text and tts, its claims, and every
# body scene's screen strings, plus the canonical JSON of the whole body.
canon = lambda sc: json.dumps(sc, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
nbody, obody = nn['scenes'][1:], on['scenes'][1:]
key = b'"id": "loss"'
file_tail_bytes_equal = nb[nb.rfind(b'{', 0, nb.index(key)):] == ob[ob.rfind(b'{', 0, ob.index(key)):]
nl = [l for sc in nbody for l in sc['lines']]
ol = [l for sc in obody for l in sc['lines']]
line_bytes = [{'id': a['id'], 'text_bytes_equal': a['text'].encode() == b['text'].encode(), 'tts_bytes_equal': a['tts'].encode() == b['tts'].encode(),
               'claims_equal': a['claims'] == b['claims']} for a, b in zip(nl, ol)]
check(len(nl) == len(ol) == 36 and all(all(v for k, v in x.items() if k != 'id') for x in line_bytes), 'body line bytes')
check(all([s.encode() for s in a['screen']] == [s.encode() for s in b['screen']] for a, b in zip(nbody, obody)), 'body screen bytes')
body_bytes_equal = check(canon(nbody) == canon(obody), 'body canonical JSON')
check([k for k in nn if k != 'scenes'] == [k for k in on if k != 'scenes'] and all(nn[k] == on[k] for k in nn if k != 'scenes'), 'narration header')
check(nn['scenes'][1:] == on['scenes'][1:], 'narration body scenes')
new_ids = [l['id'] for sc in nn['scenes'] for l in sc['lines']]
old_ids = [l['id'] for sc in on['scenes'] for l in sc['lines']]
check(len(new_ids) == 43 and new_ids[:7] == [f'hook-{i}' for i in range(1, 8)], 'revised line ids')
check(new_ids[7:] == old_ids[2:] and len(old_ids[2:]) == 36, 'body ids = original loss-1 .. outro-2')
tts = {l['id']: l['tts'] for sc in nn['scenes'] for l in sc['lines']}

# 4. the 43-line manifest
nm = json.loads((INP / 'audio' / 'final-narration-manifest.json').read_text())
check(nm['status'] == 'COMPLETE' and nm['source_sha256'] == APPROVED['source/narration.json'] and len(nm['lines']) == 43, 'manifest shape')
check(nm['new_music'] is False, 'manifest new_music')
check([l['cue'] for l in nm['lines']] == new_ids, 'manifest order = script order')
lines = []
for l in nm['lines']:
    cue = l['cue']
    check(l['text'] == tts[cue], f'manifest text = tts {cue}')
    a = l['alignment']
    check(''.join(a['characters']) == tts[cue] and a['invented_timings'] is False and a['source'] == 'provider-character-timestamps', f'alignment {cue}')
    if cue.startswith('hook-'):
        src = INP / 'audio' / l['wav']
        kind = 'revised hook (supplied)'
    else:
        src = ORIG / 'eleven' / f'{cue}.wav'
        kind = 'original body (reused, not regenerated)'
        o = orows[cue]
        check(l['wav_sha256'] == o['wav_sha256'] and l['wav_duration_samples'] == o['wav_duration_samples']
              and l['wav_duration_seconds'] == o['wav_duration_seconds'] and l['alignment'] == o['alignment'] and l['text'] == o['text'],
              f'body row = original row {cue}')
    h = sha(src)
    n, sr, ch = wav_len(src)
    check(h == l['wav_sha256'], f'wav hash {cue}')
    check(n == l['wav_duration_samples'] and abs(n / sr - l['wav_duration_seconds']) < 1e-9 and sr == 48000 and ch == 1, f'wav length {cue}')
    lines.append({'cue': cue, 'kind': kind, 'file': str(src), 'sha256': h, 'samples': n, 'seconds': n / sr, 'match': h == l['wav_sha256']})


# 5. music, measured
def probe(p):
    r = subprocess.run(['/opt/homebrew/bin/ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_name,sample_rate,channels', '-of', 'json', str(p)], capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    return {'duration_seconds': float(j['format']['duration']), 'codec': j['streams'][0]['codec_name'], 'sample_rate': int(j['streams'][0]['sample_rate']), 'channels': j['streams'][0]['channels']}


music = {n: {'path': str(INP / 'music' / n), 'sha256': sha(INP / 'music' / n), **probe(INP / 'music' / n)}
         for n in ('original-suno-bed.wav', 'derived-suno-same-track-loop-bed-317.8s.wav')}

res = {'schema': 'tvl-hook43-inputs-check/1', 'status': 'PASS' if not fails else 'FAIL', 'failures': fails,
       'inputs': inputs, 'original_manifest': {'path': str(om_p), 'sha256': sha(om_p), 'lines': len(om['lines'])},
       'original_narration': {'path': str(on_p), 'sha256': sha(on_p)},
       'narration': {'path': str(nn_p), 'sha256': sha(nn_p), 'lines': len(new_ids), 'hook_lines': 7, 'body_lines': len(new_ids) - 7,
                     'body_canonical_json_equal_original': body_bytes_equal, 'body_canonical_sha256': hashlib.sha256(canon(nbody)).hexdigest(),
                     'body_canonical_sha256_original': hashlib.sha256(canon(obody)).hexdigest(),
                     'body_file_tail_bytes_equal_original': file_tail_bytes_equal,
                     'body_file_tail_note': 'whole-file bytes differ only by JSON whitespace (revised file is indent-2, original is hand-wrapped); line strings compared as UTF-8 bytes below',
                     'body_lines': line_bytes},
       'wavs': lines, 'wav_matches': sum(x['match'] for x in lines), 'music_ffprobe': music}
Path(sys.argv[1]).write_text(json.dumps(res, ensure_ascii=False, indent=1) + '\n')
print(res['status'], 'inputs', sum(x['match'] for x in inputs), '/', len(inputs), 'wavs', res['wav_matches'], '/', len(lines),
      'body canonical equal', body_bytes_equal, 'line bytes equal', all(all(v for k, v in x.items() if k != 'id') for x in line_bytes), {k: v['duration_seconds'] for k, v in music.items()})
for f in fails:
    print('FAIL', f)
sys.exit(0 if not fails else 1)
