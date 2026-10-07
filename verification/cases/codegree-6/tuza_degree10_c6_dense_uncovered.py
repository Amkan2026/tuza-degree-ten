                                                                               

                                                                        
                                                                        
                                                                        
   
import hashlib
import json
import random
import time
from pathlib import Path

import numpy as np
from tuza_degree10_c6_coverage_prefix_check import Uncovered as Compressed


class Uncovered:
    def __init__(self, n, m):
        self.n, self.m = n, m
        self.old = Compressed(n, m) if n * m > 5_000_000_000 else None
        self.cached_left = {}
        if self.old is None:
            self.words = (m + 63) // 64
            self.matrix = np.full((n, self.words), np.iinfo(np.uint64).max, dtype=np.uint64)
            if m % 64 and n:
                self.matrix[:, -1] = (1 << (m % 64)) - 1

    @property
    def rows(self):
        return self.old.rows if self.old is not None else self

    def __bool__(self):
        return bool(self.old.rows) if self.old is not None else bool(np.any(self.matrix))

    def cover(self, left, right):
        if not left or not right:
            return
        if self.old is not None:
            self.old.cover(left, right)
            return
        assert left >> self.n == right >> self.m == 0
        indices = self.cached_left.get(left)
        if indices is None:
            bits = np.frombuffer(left.to_bytes((self.n + 7) // 8, 'little'), dtype=np.uint8)
            indices = np.flatnonzero(np.unpackbits(bits, bitorder='little')[:self.n])
            if len(self.cached_left) >= 256:
                self.cached_left.clear()
            self.cached_left[left] = indices
        keep = np.bitwise_not(np.frombuffer(right.to_bytes(8 * self.words, 'little'), dtype='<u8'))
        for begin in range(0, len(indices), 512):
            selected = indices[begin:begin + 512]
            self.matrix[selected] = np.bitwise_and(self.matrix[selected], keep)

    def count(self):
        if self.old is not None:
            return self.old.count()
        counts = np.array([i.bit_count() for i in range(256)], dtype=np.uint8)
        return sum(int(counts[self.matrix[begin:begin + 512].view(np.uint8)].sum(dtype=np.uint64))
                   for begin in range(0, self.n, 512))

    def items(self):
        if self.old is not None:
            return self.old.rows.items()
        groups = {}
        for i, row in enumerate(self.matrix):
            remaining = int.from_bytes(row.tobytes(), 'little')
            if remaining:
                groups[remaining] = groups.get(remaining, 0) | (1 << i)
        return groups.items()


def check():
    started = time.time()
    rng = random.Random(3910407)
    total = 0
    dimensions = [(0, 0), (0, 7), (7, 0), (1, 1), (9, 63), (9, 64), (9, 65), (65, 130)]
    dimensions += [(rng.randrange(1, 131), rng.randrange(1, 131)) for _ in range(48)]
    for n, m in dimensions:
        fast, old = Uncovered(n, m), Compressed(n, m)
        literal = {(i, j) for i in range(n) for j in range(m)}
        for step in range(50):
            L = {i for i in range(n) if rng.randrange(5) < 2}
            R = {j for j in range(m) if rng.randrange(5) < 2}
            left = sum(1 << i for i in L)
            right = sum(1 << j for j in R)
            fast.cover(left, right)
            old.cover(left, right)
            literal.difference_update((i, j) for i in L for j in R)
            assert fast.count() == old.count() == len(literal)
            assert bool(fast.rows) == bool(literal)
            reconstructed = set()
            for columns, rows in fast.rows.items():
                reconstructed.update((i, j) for i in range(n) if rows >> i & 1
                                     for j in range(m) if columns >> j & 1)
            assert reconstructed == literal
            total += 1
        fast.cover((1 << n) - 1, (1 << m) - 1)
        assert not fast.rows and fast.count() == 0
    report = {'result': 'PASS', 'literal_relation_checks': total,
              'dimensions_checked': len(dimensions), 'empty_and_64_bit_boundaries': True,
              'fallback_source_sha256': hashlib.sha256((Path(__file__).parent / 'tuza_degree10_c6_coverage_prefix_check.py').read_bytes()).hexdigest(),
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'seconds': time.time() - started}
    (Path(__file__).parent / 'tuza_degree10_c6_dense_uncovered_verified.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    check()
