                                                                               
from itertools import combinations, permutations
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
EDGES = list(combinations(range(6), 2))
INDEX = {e: i for i, e in enumerate(EDGES)}


def decode_graph6(s):
    assert len(s) == 4 and ord(s[0]) - 63 == 6
    values = [ord(c) - 63 for c in s[1:]]
    assert all(0 <= v < 64 for v in values)
    bits = [v >> j & 1 for v in values for j in range(5, -1, -1)]
    assert bits[15:] == [0, 0, 0]
    return {(i, j) for bit, (i, j) in zip(bits, ((i, j) for j in range(1, 6) for i in range(j))) if bit}


def main():
    path = ROOT / 'tuza_degree10_c6_density_domain.json'
    raw = path.read_bytes()
    rows = json.loads(raw)['records']
    assert len(rows) == 156 and len({r['g6'] for r in rows}) == 156
    relabelings = list(permutations(range(6)))
    all_graphs = set()
    records = []
    for row in rows:
        H = set(map(tuple, row['H']))
        assert len(H) == len(row['H']) and H <= set(EDGES)
        assert H == decode_graph6(row['g6'])
        orbit = {sum(1 << INDEX[tuple(sorted((p[a], p[b])))] for a, b in H) for p in relabelings}
        assert orbit and all_graphs.isdisjoint(orbit), row['g6']
        all_graphs.update(orbit)
        records.append({'g6': row['g6'], 'edges': len(H), 'labelled_orbit_size': len(orbit), 'graph6_H_consistent': True})
    assert all_graphs == set(range(1 << 15))
    out = {
        'status': 'PASS',
        'method': 'Decode each graph6 string directly, relabel every H by all 720 permutations, require pairwise disjoint orbits and equality with all 2^15 edge masks',
        'common_graph_types': 156,
        'all_labelled_six_vertex_graphs': 32768,
        'all_graph6_H_labels_consistent': True,
        'all_orbits_pairwise_disjoint': True,
        'full_common_graph_domain': True,
        'density_domain_sha256': hashlib.sha256(raw).hexdigest(),
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'records': records,
    }
    output = ROOT / 'tuza_degree10_c6_common_orbit_verified.json'
    output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k != 'records'}, indent=2), flush=True)
    print('report_sha256', hashlib.sha256(output.read_bytes()).hexdigest(), flush=True)


if __name__ == '__main__':
    main()
