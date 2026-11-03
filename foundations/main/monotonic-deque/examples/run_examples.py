"""Runs the Python and C++17 examples for real and keeps what they printed.

  python3 films/monotonic-deque-20261103/examples/run_examples.py        # exit 0 when every check holds

For each fixture (input.txt = the film, practice.txt = lesson.md exercise, latency-day.txt = the use case,
random-input.txt = seeded cross-check):
  python3 monotonic_deque.py <fixture>         → results/py-<name>.txt
  <c++ -std=c++17 build> <fixture>              → results/cpp-<name>.txt   (must equal the Python bytes)
  the answers are also checked against a brute-force max over each window (independent of both programs).
Then python3 monotonic_deque.py input.txt --json → ../trace.json (the number source of the film), the terminal lines
of the film's code scene copied from results/py-input.txt → ../screen-excerpt.json, and results/run-receipt.json
(commands, exit codes, compiler, sha256 of every input and output).
The C++ binary is built in a temporary directory outside the repository and removed afterwards.
"""
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILM = HERE.parent
RES = HERE / 'results'
FIXTURES = ['input.txt', 'practice.txt', 'latency-day.txt', 'random-input.txt']
CXX = os.environ.get('CXX') or shutil.which('c++') or shutil.which('g++') or shutil.which('clang++')
FLAGS = ['-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic', '-Werror']

sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import monotonic_deque as md  # noqa: E402


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(cmd, out=None):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)
    if out is not None:
        out.write_text(r.stdout)
    return {'cmd': ' '.join(str(c) for c in cmd), 'exit': r.returncode, 'stderr': r.stderr.strip()[-400:]}


def brute_ok(fixture, text):
    """The printed answers equal max(a[s:s+k]) computed directly (all of them for small cases, count/first 5/largest otherwise)."""
    a, k, _ = md.read_input(HERE / fixture)
    want = [max(a[s:s + k]) for s in range(len(a) - k + 1)]
    line = next((ln for ln in text.splitlines() if ln.startswith('answers ')), '')
    if len(a) <= md.SMALL:
        return line == 'answers ' + ' '.join(map(str, want))
    m = re.match(r'^answers (\d+) values, first 5: ([-\d ]+), largest (-?\d+)$', line)
    return bool(m) and int(m[1]) == len(want) and list(map(int, m[2].split())) == want[:5] and int(m[3]) == max(want) \
        and 'check naive == deque: yes' in text


def main():
    RES.mkdir(exist_ok=True)
    steps, checks = [], {}
    tmp = Path(tempfile.mkdtemp(prefix='monotonic-deque-build-'))
    try:
        binary = tmp / 'monotonic_deque'
        comp = run([CXX, *FLAGS, '-o', str(binary), 'monotonic_deque.cpp'])
        comp['cmd'] = comp['cmd'].replace(str(binary), '<tmp>/monotonic_deque')
        steps.append(comp)
        for fx in FIXTURES:
            name = fx.rsplit('.', 1)[0]
            py, cpp = RES / f'py-{name}.txt', RES / f'cpp-{name}.txt'
            steps.append(run([sys.executable, 'monotonic_deque.py', fx], py))
            if comp['exit'] == 0:
                s = run([str(binary), fx], cpp)
                s['cmd'] = s['cmd'].replace(str(binary), '<tmp>/monotonic_deque')
                steps.append(s)
            checks[fx] = {'pythonEqualsCpp': comp['exit'] == 0 and cpp.exists() and py.read_bytes() == cpp.read_bytes(),
                          'bruteForcePython': brute_ok(fx, py.read_text()),
                          'bruteForceCpp': cpp.exists() and brute_ok(fx, cpp.read_text())}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    steps.append(run([sys.executable, 'monotonic_deque.py', 'input.txt', '--json'], FILM / 'trace.json'))
    # the terminal panel of the film's code scene: lines copied from the real Python run, never retyped
    out_lines = (RES / 'py-input.txt').read_text().splitlines()
    excerpt = {'source': 'examples/results/py-input.txt (= cpp-input.txt)', 'command': 'python3 monotonic_deque.py input.txt',
               'lines': [ln for ln in out_lines if ln.startswith(('answers ', 'deque ', 'naive ', 'check '))],
               'answers': [int(x) for x in next(ln for ln in out_lines if ln.startswith('answers ')).split()[1:]]}
    (FILM / 'screen-excerpt.json').write_text(json.dumps(excerpt, ensure_ascii=False, indent=1) + '\n')
    cxx_version = subprocess.run([CXX, '--version'], capture_output=True, text=True).stdout.splitlines()[:1]
    ok = all(s['exit'] == 0 for s in steps) and all(all(c.values()) for c in checks.values())
    outputs = sorted(RES.glob('*.txt')) + [FILM / 'trace.json', FILM / 'screen-excerpt.json']
    receipt = {
        'ok': ok,
        'host': {'system': platform.system(), 'machine': platform.machine(), 'python': platform.python_version(), 'cxx': cxx_version},
        'cxxFlags': ' '.join(FLAGS),
        'cwd': 'films/monotonic-deque-20261103/examples',
        'steps': steps,
        'checks': checks,
        'inputs': {fx: sha(HERE / fx) for fx in FIXTURES},
        'sources': {f: sha(HERE / f) for f in ('monotonic_deque.py', 'monotonic_deque.cpp', 'make_random.py')},
        'outputs': {str(p.relative_to(FILM)): sha(p) for p in outputs},
    }
    (RES / 'run-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps({'ok': ok, 'checks': checks, 'exits': [s['exit'] for s in steps]}))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
