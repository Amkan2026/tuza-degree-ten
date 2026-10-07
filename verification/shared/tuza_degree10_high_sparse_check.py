                                                         

                                                                             
   
from pathlib import Path
from itertools import combinations
import hashlib
import json
import subprocess


def decode(g):
    n = ord(g[0]) - 63
    bits = ''.join(format(ord(c) - 63, '06b') for c in g[1:])
    edges = set()
    position = 0
    for b in range(1, n):
        for a in range(b):
            if bits[position] == '1':
                edges.add((a, b))
            position += 1
    return n, edges


def sparse_center(n, edges):
    for z in range(n):
        remaining = {e for e in edges if z not in e}
        if all(sum(c in e for e in remaining) <= 2 for c in range(n) if c != z):
            return z
    return None


def construct(n, edges, z):
    u, v = n, n + 1
    rims = {e for e in edges if z not in e}
    if not rims:
        if not edges:
            return [[u, v, z]], {(u, v)}
        x = next(c for c in range(n) if c != z and tuple(sorted((c, z))) in edges)
        y = next(c for c in range(n) if c not in (z, x))
        return [[u, z, x], [u, v, y]], {(u, v), tuple(sorted((z, x))), (z, u), (z, v)}

    adjacency = {c: set() for c in range(n) if c != z}
    for a, b in rims:
        adjacency[a].add(b)
        adjacency[b].add(a)
    remaining = set(rims)
    packing = [[u, v, z]]
    while remaining:
        component = set()
        todo = [next(iter(remaining))[0]]
        while todo:
            a = todo.pop()
            if a in component:
                continue
            component.add(a)
            todo.extend(adjacency[a] - component)
        ends = [a for a in component if len(adjacency[a]) == 1]
        start = min(ends or component)
        ordered = []
        previous = None
        current = start
        while True:
            choices = [b for b in adjacency[current] if b != previous and tuple(sorted((current, b))) in remaining]
            if not choices:
                break
            following = min(choices)
            rim = tuple(sorted((current, following)))
            remaining.remove(rim)
            ordered.append(rim)
            previous, current = current, following
            if current == start:
                break
        if not ends and len(ordered) % 2:
            ordered.pop()
        for index, (a, b) in enumerate(ordered):
            packing.append([u if index % 2 == 0 else v, a, b])
    return packing, rims | {(u, v), (z, u), (z, v)}


def literal(n, common_edges, packing, cover):
    u, v = n, n + 1
    edges = common_edges | {(c, h) for c in range(n) for h in (u, v)} | {(u, v)}
    assert cover <= edges and len(cover) <= 2 * len(packing)
    used = set()
    for triangle in packing:
        triangle_edges = set(combinations(sorted(triangle), 2))
        assert len(set(triangle)) == 3 and triangle_edges <= edges and not triangle_edges & used
        assert all(e in cover for e in triangle_edges if not set(e) & {u, v})
        used.update(triangle_edges)
    for triangle in combinations(range(n + 2), 3):
        triangle_edges = set(combinations(triangle, 2))
        if set(triangle) & {u, v} and triangle_edges <= edges:
            assert triangle_edges & cover


source = Path('work/tuza_degree9_common8_pair_probe.json')
payload = json.loads(source.read_text())
fresh8 = set(subprocess.check_output(['/opt/homebrew/bin/geng', '-q', '8'], text=True).splitlines())
assert len(fresh8) == 12346 and {r['g6'] for r in payload['records']} == fresh8
sparse8 = [r['g6'] for r in payload['records'] if r['status'] == 'SPARSE']
assert len(sparse8) == 804
for g in sparse8:
    n, edges = decode(g)
    z = sparse_center(n, edges)
    assert z is not None
    literal(n, edges, *construct(n, edges, z))

fresh9 = subprocess.check_output(['/opt/homebrew/bin/geng', '-q', '9'], text=True).splitlines()
assert len(fresh9) == len(set(fresh9)) == 274668
count9 = 0
for g in fresh9:
    n, edges = decode(g)
    z = sparse_center(n, edges)
    if z is not None:
        literal(n, edges, *construct(n, edges, z))
        count9 += 1

sample_n, sample_edges = decode(sparse8[0])
packing, cover = construct(sample_n, sample_edges, sparse_center(sample_n, sample_edges))
negative = 0
for bad_packing, bad_cover in [(packing + [packing[0]], cover), (packing, set())]:
    try:
        literal(sample_n, sample_edges, bad_packing, bad_cover)
    except AssertionError:
        negative += 1
assert negative == 2
proof = Path('work/tuza_degree10_high_sparse_human_proof.txt')
out = {
    'result': 'PASS',
    'scope': 'pure two-hub sparse reduction, any ambient degree',
    'old_common8_sparse_types': 804,
    'fresh_common9_types': 274668,
    'all_common9_sparse_types_constructively_verified': count9,
    'negative_controls': negative,
    'old_common8_payload_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'human_proof_sha256': hashlib.sha256(proof.read_bytes()).hexdigest(),
    'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
Path('work/tuza_degree10_high_sparse_verified.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
