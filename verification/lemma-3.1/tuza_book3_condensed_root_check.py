                                                                        

                                                                       
                                                                       
   
import gzip
import hashlib
import itertools
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def graph(key):
    n = ord(key[0]) - 63
    bits = [(ord(c)-63 >> i) & 1 for c in key[1:] for i in range(5, -1, -1)]
    pairs = [(a, b) for b in range(n) for a in range(b)]
    assert len(bits) >= len(pairs)
    return n, {e for e, bit in zip(pairs, bits) if bit}


def literal(n, E, M, Q):
    M = list(map(tuple, M)); Q = list(Q)
    assert len(M) == len(set(M)) and set(M) <= E
    assert len({v for e in M for v in e}) == 2*len(M)
    assert len(Q) == len(set(Q)) and set(Q) <= set(range(n))
    assert len(Q) <= len(M)
    assert all(e in M or any(v in Q for v in e) for e in E)


def color_to_witness(row):
    n, E = graph(row['g6'])
    triples = row['edge_colors']
    colors = {tuple(t[:2]): t[2] for t in triples}
    assert len(colors) == len(triples) and set(colors) == E
    assert set(colors.values()) <= {0, 1, 2}
    for v in range(n):
        used = [c for e, c in colors.items() if v in e]
        assert len(used) == len(set(used))
    improvements = 0
    while True:
        M = {e for e, c in colors.items() if c == 2}
        residual = E - M
        for size in range(len(M)+1):
            for Q in itertools.combinations(range(n), size):
                mask = sum(1 << v for v in Q)
                if all(mask & ((1 << a) | (1 << b)) for a, b in residual):
                    literal(n, E, M, Q)
                    return improvements
                                                                        
                                                                
        unseen = set(residual)
        while unseen:
            component = {unseen.pop()}
            vertices = set(next(iter(component)))
            changed = True
            while changed:
                adjacent = {e for e in unseen if set(e) & vertices}
                changed = bool(adjacent)
                component |= adjacent; unseen -= adjacent
                vertices |= {v for e in adjacent for v in e}
            if sum(colors[e] == 1 for e in component) > sum(colors[e] == 0 for e in component):
                for e in component:
                    colors[e] = 1 - colors[e]
        assert sum(c == 0 for c in colors.values()) > len(M)
        colors = {e: 2 if c == 0 else 0 if c == 2 else 1 for e, c in colors.items()}
        improvements += 1
        assert improvements <= n//2


def named(name):
    if name == 'P':
        pairs = list(itertools.combinations(range(5), 2))
        return 10, {(i, j) for i, j in itertools.combinations(range(10), 2)
                    if not set(pairs[i]) & set(pairs[j])}
    assert name in {'R', 'R11'}
    E = set()
    for start, z in [(0, 4), (5, 9)]:
        E |= set(itertools.combinations(range(start, start+4), 2)) - {(start, start+1)}
        E |= {(start, z), (start+1, z)}
    E |= {(4, 9)} if name == 'R' else {(4, 10), (9, 10)}
    return 10 if name == 'R' else 11, E


def main():
    started = time.time()
    source = ROOT / 'tuza_subcubic_condensed_basis.json.gz'
    encoded = source.read_bytes(); raw = gzip.decompress(encoded); data = json.loads(raw)
    C, W, R = (data[k] for k in ['positive_edge_colorings', 'positive_matching_cover_records', 'remaining'])
    assert (len(C), len(W), len(R)) == (6325, 287, 9)
    improvements = [color_to_witness(r) for r in C]
    for row in W:
        n, E = graph(row['g6']); literal(n, E, row['matching'], row['cover'])
    twelve = dict(zip('ABCDEF', ['K?AB?pa[CWP_', 'K?ABCiWFBOKO', 'K?ABBF_e?wB_',
                               'K?`@E`gFCKEO', 'K?`@CqW[AKCo', 'K?`CPbGP`gEG']))
    assert {r['name'] for r in R} == {'P', 'R', 'R11', *twelve}
    for row in R:
        n, E = graph(row['g6'])
        if row['name'] in twelve:
            assert n == 12 and row['g6'] == twelve[row['name']]
        else:
            order, F = named(row['name'])
            f = {int(a): b for a, b in row['bijection'].items()}
            assert order == n and set(f) == set(f.values()) == set(range(n))
            assert {tuple(sorted((f[a], f[b]))) for a, b in E} == F
        if n <= 10:
            assert n == 10 and all(sum(v in e for e in E) == 3 for v in range(n))
    keys = [r['g6'] for r in C+W+R]
    assert len(keys) == len(set(keys)) == 6621
    min2 = set(); whole = set(); counts = {}
    for n in range(5, 13):
        full_bytes = subprocess.check_output(['/opt/homebrew/bin/geng', '-q', '-c', '-D3', str(n)])
        min_bytes = subprocess.check_output(['/opt/homebrew/bin/geng', '-q', '-c', '-d2', '-D3', str(n)])
        F = set(full_bytes.decode().splitlines()); S = set(min_bytes.decode().splitlines())
        assert S <= F
        for key in F:
            order, E = graph(key)
            degrees = [sum(v in e for e in E) for v in range(n)]
            assert order == n and max(degrees) <= 3
            assert (min(degrees) >= 2) == (key in S)
            if key not in S:
                assert min(degrees) == 1
        counts[n] = {'whole': len(F), 'min2': len(S), 'leaf': len(F-S)}
        min2 |= S; whole |= F
    assert set(keys) == min2 and len(whole) == 27515
    controls = 0
    try:
        bad = json.loads(json.dumps(C[0]))
        bad['edge_colors'][0][2] = bad['edge_colors'][1][2]
        color_to_witness(bad)
    except AssertionError:
        controls += 1
    try:
        row = W[0]; n, E = graph(row['g6'])
        literal(n, E, row['matching']*2, row['cover'])
    except AssertionError:
        controls += 1
    try:
        assert set(keys[:-1]) == min2
    except AssertionError:
        controls += 1
    assert controls == 3
    report = {'result': 'PASS', 'fresh_domains': counts, 'whole_link_types': len(whole),
              'proper_colorings_converted_to_literal_WKE': len(C), 'direct_WKE': len(W),
              'remaining_types': sorted(r['name'] for r in R), 'leaf_types': len(whole-min2),
              'maximum_recoloring_improvements': max(improvements), 'negative_controls': controls,
              'raw_payload_sha256': hashlib.sha256(raw).hexdigest(),
              'compressed_payload_sha256': hashlib.sha256(encoded).hexdigest(),
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'Positive finite basis plus separately reviewed human leaf induction through order twelve',
              'seconds': time.time()-started}
    target = ROOT / 'tuza_book3_condensed_root_verified.json'
    temporary = target.with_suffix('.pending'); temporary.write_text(json.dumps(report, indent=2)); temporary.replace(target)
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
