"""Builds and runs both examples, keeps their real output, and checks that they agree.

usage: python3 films/fenwick-20261022/examples/run_examples.py
writes: examples/out/python.txt, examples/out/cpp.txt, examples/out/run.json (commands, exit codes, sha256, tool versions)
exit: 0 when both programs exit 0 and their outputs are byte-identical, else 1.
"""
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
ROOT = HERE.parents[2]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
rel = lambda p: str(Path(p).resolve().relative_to(ROOT))


def run(cmd, out_file=None):
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    if out_file:
        Path(out_file).write_text(r.stdout)
    return {'cmd': ' '.join(str(c) for c in cmd), 'exit': r.returncode, 'seconds': round(time.time() - t0, 2),
            'stderr': r.stderr.strip()[-2000:], **({'stdout_file': rel(out_file), 'stdout_sha256': sha(out_file)} if out_file else {})}


def main():
    OUT.mkdir(exist_ok=True)
    cxx = shutil.which('c++') or shutil.which('g++') or shutil.which('clang++')
    binary = OUT / 'fenwick'
    steps = [
        run([sys.executable, str(HERE / 'fenwick.py')], OUT / 'python.txt'),
        run([cxx, '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic', '-o', str(binary), str(HERE / 'fenwick.cpp')]),
    ]
    steps.append(run([str(binary)], OUT / 'cpp.txt') if steps[1]['exit'] == 0 else {'cmd': str(binary), 'exit': None, 'skipped': 'compile failed'})
    same = (OUT / 'python.txt').read_bytes() == (OUT / 'cpp.txt').read_bytes() if (OUT / 'cpp.txt').exists() else False
    ok = all(s.get('exit') == 0 for s in steps) and same
    cxx_ver = subprocess.run([cxx, '--version'], capture_output=True, text=True).stdout.splitlines()[0]
    report = {
        'status': 'PASS' if ok else 'FAIL',
        'outputs_identical': same,
        'sources': {rel(HERE / f): sha(HERE / f) for f in ('fenwick.py', 'fenwick.cpp', 'run_examples.py')},
        'tools': {'python': sys.version.split()[0], 'cxx': cxx, 'cxx_version': cxx_ver, 'platform': platform.platform()},
        'steps': steps,
    }
    (OUT / 'run.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps({k: report[k] for k in ('status', 'outputs_identical')}, ensure_ascii=False))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
