"""Builds and runs the Python and C++17 examples on both graphs and keeps the real results.

usage: python3 films/bellman-ford-20261022/examples/run_examples.py
writes examples/out/: <lang>-<graph>.txt (stdout), trace-<graph>.json (Python trace the film reads),
cpp-build.log, receipt.json (commands, exit codes, sha256 of every input and output). Exit 1 if any run fails
or the two languages print different text.
"""
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
GRAPHS = {'graph': 'graph.txt', 'cycle': 'graph-negative-cycle.txt'}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(cmd, log=None):
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
    if log:
        (OUT / log).write_text(r.stdout + r.stderr)
    return r


def main():
    OUT.mkdir(exist_ok=True)
    cxx = shutil.which('c++') or shutil.which('g++') or shutil.which('clang++')
    receipt = {'host': platform.platform(), 'python': sys.version.split()[0], 'cxx': cxx, 'runs': [], 'inputs': {}, 'outputs': {}}
    cxx_ver = subprocess.run([cxx, '--version'], capture_output=True, text=True).stdout.splitlines()[0]
    receipt['cxxVersion'] = cxx_ver
    exe = str(OUT / 'bellman_ford')
    build = [cxx, '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic', '-o', exe, 'bellman_ford.cpp']
    r = run(build, 'cpp-build.log')
    receipt['runs'].append({'cmd': ' '.join(build).replace(str(HERE) + '/', ''), 'exit': r.returncode, 'warnings': (r.stdout + r.stderr).strip()})
    ok = r.returncode == 0
    for key, g in GRAPHS.items():
        py = [sys.executable, 'bellman_ford.py', g, '--trace', f'out/trace-{key}.json']
        rp = run(py)
        (OUT / f'py-{key}.txt').write_text(rp.stdout)
        receipt['runs'].append({'cmd': ' '.join(['python3'] + py[1:]), 'exit': rp.returncode, 'stdout': f'out/py-{key}.txt', 'stderr': rp.stderr.strip()})
        rc = run([exe, g]) if ok else None
        if rc:
            (OUT / f'cpp-{key}.txt').write_text(rc.stdout)
            receipt['runs'].append({'cmd': f'out/bellman_ford {g}', 'exit': rc.returncode, 'stdout': f'out/cpp-{key}.txt', 'stderr': rc.stderr.strip()})
        same = bool(rc) and rc.stdout == rp.stdout
        receipt['runs'].append({'compare': f'py-{key}.txt == cpp-{key}.txt', 'identical': same})
        ok = ok and rp.returncode == 0 and bool(rc) and rc.returncode == 0 and same
    for p in ['graph.txt', 'graph-negative-cycle.txt', 'bellman_ford.py', 'bellman_ford.cpp', 'run_examples.py']:
        receipt['inputs'][p] = sha(HERE / p)
    for p in sorted(OUT.glob('*')):
        if p.name not in ('receipt.json', 'bellman_ford'):
            receipt['outputs']['out/' + p.name] = sha(p)
    receipt['ok'] = ok
    (OUT / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + '\n')
    print('examples', 'OK' if ok else 'FAILED', '→', OUT)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
