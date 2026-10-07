                                                                       
from pathlib import Path
from itertools import combinations
import json, hashlib, subprocess

base = Path('work')
payload = base / 'tuza_degree10_common8_slack2_probe.json'
data = json.loads(payload.read_text())
records = data['records']
assert len(records) == 12346
fresh = set(subprocess.check_output(['/opt/homebrew/bin/geng', '-q', '8'], text=True).splitlines())
assert {r['g6'] for r in records} == fresh
positive = {i for i, r in enumerate(records) if r['status'] == 'PASS'}
assert len(positive) == 12116
edges = list(combinations(range(8), 2))

def decode(key):
    bits = ''.join(format(ord(c) - 63, '06b') for c in key[1:])
    out = set()
    k = 0
    for v in range(1, 8):
        for u in range(v):
            if bits[k] == '1':
                out.add((u, v))
            k += 1
    return out

def interval(i):
    row = records[i]
    assert row['status'] == 'PASS'
    selected = set(map(tuple, row['X']))
    packed = {e for t in row['triangles'] for e in map(tuple, t)}
    required = {e for e in packed if max(e) < 8}
    allowed = {e for e in edges if e in selected or
               (any((v, 8) in selected for v in e) and
                any((v, 9) in selected for v in e))}
    assert required <= decode(row['g6']) <= allowed
    assert (8, 9) in selected or all((v, 8) in selected or (v, 9) in selected for v in range(8))
    return required, allowed

templates = {}
for line in (base / 'tuza_degree10_c8_interval_greedy_selected.txt').read_text().splitlines():
    i, r, t, gain = map(int, line.split())
    assert i not in templates and gain > 0
    req, allow = interval(i)
    assert req == {e for k, e in enumerate(edges) if r >> k & 1}
    assert allow == {e for k, e in enumerate(edges) if t >> k & 1}
    templates[i] = req, allow

def replay(target, source, permutation):
    assert target in positive and source in templates
    assert sorted(permutation) == list(range(8))
    def image(e):
        return tuple(sorted(permutation[v] if v < 8 else v for v in e))
    H = decode(records[target]['g6'])
    req, allow = templates[source]
    assert {image(e) for e in req} <= H <= {image(e) for e in allow}
    E = H | {(v, h) for v in range(8) for h in (8, 9)} | {(8, 9)}
    X = {image(tuple(e)) for e in records[source]['X']}
    X &= E
    used = set()
    packing = records[source]['triangles']
    for tri in packing:
        es = {image(tuple(e)) for e in tri}
        vs = set(v for e in es for v in e)
        assert len(vs) == 3 and es == set(combinations(sorted(vs), 2))
        assert es <= E and not es & used
        assert all(e in X for e in es if not (set(e) & {8, 9}))
        used |= es
    assert len(X) + 2 <= 2 * len(packing)
    for tri in combinations(range(10), 3):
        es = set(combinations(tri, 2))
        if set(tri) & {8, 9} and es <= E:
            assert es & X

seen = set()
for line in (base / 'tuza_degree10_c8_interval_greedy_embeddings.txt').read_text().splitlines():
    i, source, *permutation = map(int, line.split())
    assert i not in seen
    replay(i, source, permutation)
    seen.add(i)
assert seen == positive
negative = 0
i, source, *permutation = map(int, (base / 'tuza_degree10_c8_interval_greedy_embeddings.txt').read_text().splitlines()[0].split())
bad = permutation[:]
bad[0] = bad[1]
try:
    replay(i, source, bad)
except AssertionError:
    negative += 1
else:
    raise AssertionError('non-bijection accepted')
out = {'result': 'PASS', 'full_core_types': 12346, 'positive_spare_two_types': len(positive),
       'interval_templates': len(templates), 'literal_embeddings': len(seen),
       'negative_controls': negative, 'payload_sha256': hashlib.sha256(payload.read_bytes()).hexdigest()}
(base / 'tuza_degree10_c8_intervals237_verified.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
