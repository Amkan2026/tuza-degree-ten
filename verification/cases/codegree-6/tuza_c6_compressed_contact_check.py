                                                                      

                                                                          
                                                                          
   
from pathlib import Path
from itertools import combinations, permutations
from functools import lru_cache
import subprocess
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
PAIR6 = tuple(combinations(range(6), 2))


def edge(a, b):
    return tuple(sorted((a, b)))


def read_core(g):
    bits = [ord(c) - 63 for c in g]
    order = bits[0]
    nb = [set() for _ in range(order)]
    k = 0
    for j in range(1, order):
        for i in range(j):
            if bits[1 + k // 6] & (1 << (5 - k % 6)):
                nb[i].add(j); nb[j].add(i)
            k += 1
    isolated = [v for v in range(order) if not nb[v]]
    if len(isolated) < 2:
        return None
    vertices = [v for v in range(order) if v not in isolated[:2]]
    assert len(vertices) == 6
    return {edge(a, b) for a, b in PAIR6 if vertices[b] in nb[vertices[a]]}


def adjacency(es, n):
    nb = [set() for _ in range(n)]
    for a, b in es:
        nb[a].add(b); nb[b].add(a)
    return nb


def connected(nb):
    seen = {0}
    while True:
        new = seen.union(*(nb[v] for v in seen))
        if new == seen:
            return len(seen) == len(nb)
        seen = new


def wke(es):
    nb = adjacency(es, 8)
    @lru_cache(None)
    def matching(vs):
        if not vs:
            return 0
        v = min(vs)
        rest = vs - {v}
        return max([matching(rest)] + [1 + matching(rest - {w}) for w in nb[v] & rest])
    full = frozenset(range(8))
    for size in range(5):
        for q in combinations(range(8), size):
            outside = full - set(q)
            forced = [e for e in es if set(e) <= outside]
            used = [v for e in forced for v in e]
            if len(used) != len(set(used)):
                continue
            if len(forced) + matching(full - set(used)) >= size:
                return True
    return False


def graph(H, a, b):
    return ({edge(x + 2, y + 2) for x, y in H}
            | {(0, 1), (0, 8), (1, 9)}
            | {(h, c) for h in (0, 1) for c in range(2, 8)}
            | {(c + 2, 8) for c in range(6) if a >> c & 1}
            | {(c + 2, 9) for c in range(6) if b >> c & 1})


def validate(S, X, es):
    selected = set(map(tuple, X))
    assert selected <= es and len(selected) == len(X)
    assert len(selected) <= 2 * len(S)
    used = set()
    for t in S:
        assert len(t) == 3 and len(set(t)) == 3
        edges = {edge(a, b) for a, b in combinations(t, 2)}
        assert edges <= es and not edges & used
        used |= edges
    assert all(e in selected for e in used if not {0, 1}.intersection(e))
    for t in combinations(range(10), 3):
        if not {0, 1}.intersection(t):
            continue
        edges = set(combinations(t, 2))
        if edges <= es:
            assert edges & selected


def transformed(template, p, swap):
    move = {0: int(swap), 1: 1 - int(swap),
            8: 9 if swap else 8, 9: 8 if swap else 9}
    move.update({v + 2: p[v] + 2 for v in range(6)})
    S = [sorted(move[v] for v in t) for t in template['packing']]
    X = sorted(edge(move[a], move[b]) for a, b in template['cover'])
    return S, X


def fits(template, p, swap, a, b):
    z, w = template['required_contacts']
    req = (p[z] if z >= 0 else -1, p[w] if w >= 0 else -1)
    if swap:
        req = req[::-1]
    return all(v < 0 or mask >> v & 1 for v, mask in zip(req, (a, b)))


def main():
    human = '--human-hybrid' in sys.argv
    source = 'tuza_c6_human_compressed_templates.json' if human else 'tuza_c6_compressed_contact_templates.json'
    expected_templates = 24 if human else 32
    raw = (HERE / source).read_bytes()
    data = json.loads(raw)
    rows = {r['key']: r for r in data['rows']}
    assert len(rows) == 20 and sum(len(r['selected_templates']) for r in rows.values()) == expected_templates
    fresh = subprocess.run(['/opt/homebrew/bin/geng', '-q', '8'], check=True,
                           capture_output=True, text=True).stdout
    cores = {g: H for g in fresh.splitlines() if (H := read_core(g)) is not None}
    assert len(cores) == 156 and set(rows) <= set(cores)
    universal = 0
    pair_count = 0
    counts = {}
    for key, row in rows.items():
        H = cores[key]
        assert set(map(tuple, row['core_edges'])) == H
        ps = [p for p in permutations(range(6))
              if {edge(p[a], p[b]) for a, b in H} == H]
        assert len(ps) == row['core_automorphisms']
        for template in row['selected_templates']:
            z, w = template['required_contacts']
            assert human or z >= 0 or w >= 0
            a = 1 << z if z >= 0 else 0
            b = 1 << w if w >= 0 else 0
            minimal = graph(H, a, b)
            validate(template['packing'], template['cover'], minimal)
            validate(template['packing'], template['cover'], minimal | {(8, 9)})
                                                                          
                                                                           
            assert (0, 8) in map(tuple, template['cover'])
            assert (1, 9) in map(tuple, template['cover'])
            universal += 1
        sides = []
        for mask in range(64):
            link = H | {(c, 6) for c in range(6)} | {(c, 7) for c in range(6) if mask >> c & 1}
            if connected(adjacency(link, 8)) and not wke(link):
                sides.append(mask)
        count = 0
        pairs = list(combinations(sides, 2)) + [(a, a) for a in sides]
        for a, b in pairs:
            a, b = sorted((a, b))
            es = graph(H, a, b)
            nb = adjacency(es, 10)
            if max(map(len, nb)) > 8 or any(len(nb[x] & nb[y]) > 6 for x, y in es):
                continue
            choices = ((template, p, swap) for template in row['selected_templates']
                       for p in ps for swap in (False, True)
                       if fits(template, p, swap, a, b))
            template, p, swap = next(choices, (None, None, None))
            assert template is not None, (key, a, b)
            S, X = transformed(template, p, swap)
            validate(S, X, es)
            validate(S, X, es | {(8, 9)})
            count += 1
        assert count == row['attachment_pairs']
        counts[key] = count
        pair_count += count
    assert universal == expected_templates and pair_count == 5629
    result = {'result': 'PASS', 'fresh_six_core_count': len(cores),
              'compressed_core_diagrams': len(rows), 'universal_templates': universal,
              'fresh_admitted_attachment_pairs': pair_count,
              'cross_literal_checks': 2 * pair_count,
              'all_templates_monotone': True, 'per_core_pairs': counts,
              'compressed_payload_sha256': hashlib.sha256(raw).hexdigest()}
    target = 'tuza_c6_human_compressed_verified.json' if human else 'tuza_c6_compressed_contact_verified.json'
    (HERE / target).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
