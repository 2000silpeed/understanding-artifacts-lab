"""Writes random-input.txt: a seeded cross-check case for Python vs C++ vs brute force (negatives and many ties).

  python3 make_random.py            # rewrites random-input.txt (same bytes every time)
"""
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent


def text():
    rng = random.Random(20261103)
    a = [rng.randint(-9, 9) for _ in range(500)]
    return '# seeded by make_random.py (random.Random(20261103)): n = 500, values -9..9, window 7\nk 7\na ' + ' '.join(map(str, a)) + '\n'


if __name__ == '__main__':
    (HERE / 'random-input.txt').write_text(text())
