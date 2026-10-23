"""Runs the Python and C++17 examples and the practice-page core on the real input files, keeps their output, and
records every command with its exit code and output hash.

  examples/runs/python-input.out, cpp-input.out, python-random.out, cpp-random.out   real stdout of each run
  qa/examples-run.json                                                                commands, exits, sha256, comparisons
  data/runs.json                                                                      input + stdout shown in the code scene

The C++ binary is built in scratch/segment-tree-20261023/ (temporary, git-ignored), never in the film folder.
usage: python3 films/segment-tree-20261023/examples/run_examples.py    exit 0 = every comparison PASS
"""
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EX = Path(__file__).resolve().parent
FILM = EX.parent
ROOT = FILM.parent.parent
BIN_DIR = ROOT / 'scratch' / 'segment-tree-20261023'
RUNS = EX / 'runs'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    return str(Path(p).relative_to(ROOT))


def run(cmd, stdin=None, out=None):
    r = subprocess.run(cmd, input=Path(stdin).read_bytes() if stdin else None, capture_output=True, cwd=ROOT)
    rec = {'cmd': ' '.join(rel(c) if isinstance(c, Path) else c for c in cmd) + (f' < {rel(stdin)}' if stdin else ''),
           'exit': r.returncode, 'stderr': r.stderr.decode(errors='replace').strip()[-2000:]}
    if out:
        out.write_bytes(r.stdout)
        rec.update(stdout=rel(out), stdoutSha256=sha(out), stdoutLines=len(r.stdout.decode().split()))
    else:
        rec['stdout'] = r.stdout.decode(errors='replace').strip()[-2000:]
    return rec, r.stdout.decode()


def main():
    RUNS.mkdir(exist_ok=True)
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    cxx = shutil.which('c++') or shutil.which('g++') or shutil.which('clang++')
    binary = BIN_DIR / 'segment_tree'
    cmds, results = [], {}
    rec, _ = run([cxx, '-std=c++17', '-O2', '-Wall', '-Wextra', '-Wpedantic', '-Werror', '-o', binary, EX / 'segment_tree.cpp'])
    rec['cmd'] = rec['cmd'].replace(cxx, 'c++')
    cmds.append(rec)
    built = rec['exit'] == 0
    for name, inp in (('input', EX / 'input.txt'), ('random', EX / 'random-input.txt')):
        rec, results[f'python-{name}'] = run([sys.executable, EX / 'segment_tree.py'], inp, RUNS / f'python-{name}.out')
        rec['cmd'] = rec['cmd'].replace(sys.executable, 'python3')
        cmds.append(rec)
        if built:
            rec, results[f'cpp-{name}'] = run([binary], inp, RUNS / f'cpp-{name}.out')
            cmds.append(rec)
    rec, _ = run(['node', FILM / 'practice' / 'check_core.cjs'])
    core = json.loads(rec['stdout']) if rec['stdout'].startswith('{') else {'pass': False}
    rec['stdout'] = f"pass={core.get('pass')} checks={len(core.get('checks', []))}"
    cmds.append(rec)
    rec, _ = run([sys.executable, EX / 'make_data.py', '--check'])
    rec['cmd'] = rec['cmd'].replace(sys.executable, 'python3')
    cmds.append(rec)

    expect = (EX / 'expected_output.txt').read_text()
    rexpect = (EX / 'random-expected.txt').read_text()
    trace = json.loads((FILM / 'data' / 'trace.json').read_text())
    comparisons = {
        'python input.txt == expected_output.txt': results.get('python-input') == expect,
        'c++ input.txt == expected_output.txt': results.get('cpp-input') == expect,
        'python random-input.txt == random-expected.txt (brute force)': results.get('python-random') == rexpect,
        'c++ random-input.txt == random-expected.txt (brute force)': results.get('cpp-random') == rexpect,
        'data/trace.json outputs == expected_output.txt': '\n'.join(trace['outputs']) + '\n' == expect,
        'practice core (node) PASS': core.get('pass') is True,
        'make_data.py --check: data up to date': cmds[-1]['exit'] == 0,
        'every command exit 0': all(c['exit'] == 0 for c in cmds),
    }
    report = {
        'film': 'segment-tree-20261023',
        'what': 'real execution of the Python and C++17 examples and of the practice page core logic; not an independent review',
        'ranAt': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'host': {'platform': platform.platform(), 'python': platform.python_version(),
                 'cxx': subprocess.run([cxx, '--version'], capture_output=True, text=True).stdout.splitlines()[0],
                 'node': subprocess.run(['node', '--version'], capture_output=True, text=True).stdout.strip()},
        'inputs': {rel(p): sha(p) for p in (EX / 'input.txt', EX / 'expected_output.txt', EX / 'random-input.txt', EX / 'random-expected.txt')},
        'sources': {rel(p): sha(p) for p in (EX / 'segment_tree.py', EX / 'segment_tree.cpp', EX / 'make_data.py', FILM / 'practice' / 'index.html', FILM / 'practice' / 'check_core.cjs')},
        'binary': {'path': rel(binary), 'temporary': True} if built else None,
        'commands': cmds,
        'comparisons': comparisons,
        'pass': all(comparisons.values()),
    }
    # what the code scene shows: the real input and the real stdout of both runs (film.js imports this file)
    (FILM / 'data' / 'runs.json').write_text(json.dumps({
        'source': 'qa/examples-run.json (examples/run_examples.py)', 'input': (EX / 'input.txt').read_text().split('\n')[:-1],
        'python': {'cmd': 'python3 segment_tree.py < input.txt', 'stdout': results.get('python-input', '').split()},
        'cpp': {'cmd': './segment_tree < input.txt', 'build': 'c++ -std=c++17 -O2 -o segment_tree segment_tree.cpp', 'stdout': results.get('cpp-input', '').split()},
    }, ensure_ascii=False, indent=1) + '\n')
    (FILM / 'qa' / 'examples-run.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps({'pass': report['pass'], 'comparisons': comparisons}, ensure_ascii=False, indent=1))
    sys.exit(0 if report['pass'] else 1)


if __name__ == '__main__':
    main()
