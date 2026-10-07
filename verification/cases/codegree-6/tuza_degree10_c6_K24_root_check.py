                                                                           

                                                                           
                                                                          
   
from itertools import combinations
from pathlib import Path
import hashlib
import json
import time

ROOT = Path(__file__).resolve().parent

def load(name):
    b = (ROOT / name).read_bytes()
    return json.loads(b), hashlib.sha256(b).hexdigest()

def edge(a, b):
    return min(a, b), max(a, b)

def graph(p, q, cross):
    E = {edge(6, 7)}
    E.update(edge(h, c) for h in (6, 7) for c in range(6))
    E.update(edge(c, d) for c in range(4) for d in (4, 5))
    for h, side, bits in ((6, (8, 9), p), (7, (11, 12), q)):
        E.update(edge(h, a) for a in side)
        for j, a in enumerate(side):
            E.update(edge(a, c) for c in range(6) if bits & (1 << (6*j+c)))
        if bits & (1 << 12):
            E.add(edge(*side))
    E.update(e for j, e in enumerate(((8, 11), (8, 12), (9, 11), (9, 12))) if cross & (1 << j))
    return E

def convert(x):
    return {10: 11, 11: 12}.get(x, x)

def certify(E, S, X, I):
    U = {6, 7} | I
    if not X <= E or not I <= set(range(6)):
        return False
    used = set()
    for T in S:
        if len(T) != 3 or len(set(T)) != 3:
            return False
        F = {edge(a, b) for a, b in combinations(T, 2)}
        if not F <= E or F & used:
            return False
        if any(not (set(e) & U) and e not in X for e in F):
            return False
        used |= F
    vertices = set(range(10)) | {11, 12}
    for T in combinations(vertices, 3):
        F = {edge(a, b) for a, b in combinations(T, 2)}
        if set(T) & U and F <= E and not F & X:
            return False
                                                                        
                                                                        
                                                                             
    deficit = sum(10 - sum(c in f for f in E) for c in I)
    if any(sum(c in f for f in E) > 10 for c in I):
        return False
    return len(X) + deficit <= 2 * len(S)

def run():
    started = time.time()
    names = ['tuza_degree10_c6_K24_residual_pairs.json',
             'tuza_degree10_c6_K24_extension_probe.json',
             'tuza_degree10_c6_K24_general_extension_probe.json']
    files = [load(n) for n in names]
    pairs = {tuple(x) for x in files[0][0]['residual_pairs']}
    assert len(pairs) == 193
    assert files[0][0]['g6'] == 'E?~o' and files[0][0]['lane'] == '9/9'
    seen = set()
    counts = {'all_R_rims': 0, 'general_cover': 0, 'known_codegree_exclusion': 0}
    controls = None
    for method, records in [('all_R_rims', files[1][0]['records']),
                            ('general_cover', files[2][0]['records']),
                            ('known_codegree_exclusion', files[2][0]['excluded_codegree'])]:
        for r in records:
            k = r['p'], r['q'], r['cross']
            assert k not in seen and k[:2] in pairs and 0 <= k[2] < 16
            seen.add(k)
            E = graph(*k)
            if method == 'known_codegree_exclusion':
                a, b = map(convert, r['edge'])
                common = {v for v in range(13) if edge(v, a) in E and edge(v, b) in E}
                assert edge(a, b) in E and len(common) >= 7
                assert common == {convert(v) for v in r['common_neighbors']}
            else:
                I = set(range(4)) if method == 'all_R_rims' else set(r['I'])
                X = ({e for e in E if not set(e) & I} if method == 'all_R_rims'
                     else {edge(*map(convert, e)) for e in r['cover']})
                S = [tuple(map(convert, T)) for T in r['packing']]
                outside = sum(10-sum(c in e for e in E) for c in I)
                assert outside == r['outside']
                assert certify(E, S, X, I), ('Invalid certificate', k)
                if controls is None:
                    outer = next(e for T in S for e in map(lambda f: edge(*f), combinations(T, 2))
                                 if not set(e) & ({6, 7} | I))
                    controls = {'empty_cover': not certify(E, S, set(), I),
                                'duplicate_triangle': not certify(E, S + [S[0]], X, I),
                                'missing_outer_rim': not certify(E, S, X-{outer}, I),
                                'invalid_removed_vertex': not certify(E, S, X, I | {8})}
            counts[method] += 1
    assert seen == {(p, q, k) for p, q in pairs for k in range(16)}
    assert all(controls.values())
    output = {'result': 'PASS', 'scope': 'the stated 193 residual pairs and every cross pattern',
              'ordered_pairs': len(pairs), 'cross_patterns': len(seen), 'methods': counts,
              'ambient_maximum_degree': 10, 'root_B_labels': [11, 12],
              'outside_spoke_budget_recomputed': True,
              'ordinary_interval_residual_binding_required': True,
              'negative_controls': controls,
              'inputs': {n: d for n, (_, d) in zip(names, files)},
              'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'seconds': time.time()-started}
    target = ROOT / 'tuza_degree10_c6_K24_root_verified.json'
    tmp = target.with_suffix('.tmp')
    tmp.write_text(json.dumps(output, indent=2) + '\n')
    tmp.replace(target)
    print(json.dumps(output), flush=True)

if __name__ == '__main__':
    run()
