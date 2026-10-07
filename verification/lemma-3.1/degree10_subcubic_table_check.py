                                                                               
import gzip
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / 'tuza_degree10_subcubic_link_basis.json.gz'


def graph(key):
    n = ord(key[0]) - 63
    bits = [(ord(c) - 63 >> i) & 1 for c in key[1:] for i in range(5, -1, -1)]
    pairs = [(a, b) for b in range(n) for a in range(b)]
    return n, {e for e, bit in zip(pairs, bits) if bit}


def edge(a, b):
    return tuple(sorted((a, b)))


def main():
    encoded = SOURCE.read_bytes()
    data = json.loads(gzip.decompress(encoded))
    rows = data['positive_matching_cover_records']
    assert len(rows) == 40
    forms = defaultdict(list)
    for row in rows:
        n, E = graph(row['g6'])
        M = {edge(*e) for e in row['matching']}
        Q = set(row['cover'])
        assert M <= E and len({v for e in M for v in e}) == 2 * len(M)
        assert len(Q) <= len(M) and all(e in M or set(e) & Q for e in E)
                                                                                
        for v in range(n):
            if len(Q) == len(M):
                break
            Q.add(v)
        assert len(Q) == len(M)
        ordered = sorted(M, key=lambda e: (-len(set(e) & Q), e))
        f = {}
        for i, e in enumerate(ordered):
            a, b = sorted(e, key=lambda v: (v not in Q, v))
            f[a], f[b] = 2 * i, 2 * i + 1
        remaining = sorted(set(range(n)) - set(f), key=lambda v: (v not in Q, v))
        f.update({v: 2 * len(M) + i for i, v in enumerate(remaining)})
        assert set(f) == set(f.values()) == set(range(n))
        canonical_M = {edge(f[a], f[b]) for a, b in M}
        canonical_Q = {f[v] for v in Q}
        canonical_E = {edge(f[a], f[b]) for a, b in E}
        one = sum(len(set(e) & Q) == 1 for e in M)
        two = sum(len(set(e) & Q) == 2 for e in M)
        outside = len(Q - {v for e in M for v in e})
        expected_M = {(2 * i, 2 * i + 1) for i in range(len(M))}
        expected_Q = set(range(2 * two)) | {2 * i for i in range(two, two + one)}
        expected_Q |= set(range(2 * len(M), 2 * len(M) + outside))
        assert canonical_M == expected_M and canonical_Q == expected_Q
        upper = {e for e in itertools.combinations(range(n), 2) if set(e) & expected_Q} | expected_M
        assert expected_M <= canonical_E <= upper
        forms[n, len(M), one, two, outside].append({'g6': row['g6'], 'bijection': f})
    assert len(forms) == 9 and sum(map(len, forms.values())) == 40
    count_by_order = {}
    for n in range(5, 11):
        count_by_order[n] = {
            k: sum(ord(row['g6'][0]) - 63 == n for row in data[k])
            for k in ['positive_edge_colorings', 'positive_matching_cover_records', 'remaining']
        }
    result = {
        'result': 'PASS',
        'direct_positive_records': 40,
        'marked_matching_forms': 9,
        'uniform_interval_rule': 'Required matching M, every other edge must meet Q, |Q|=|M|',
        'counts_by_order': count_by_order,
        'forms': [{'vertices': k[0], 'matching_size': k[1], 'one_dark_pairs': k[2],
                   'two_dark_pairs': k[3], 'dark_unmatched': k[4], 'members': v}
                  for k, v in sorted(forms.items())],
        'source_file': SOURCE.name,
        'source_sha256': hashlib.sha256(encoded).hexdigest(),
        'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'full_subcubic_coverage_required_separately': True,
    }
    target = BASE / 'degree10_subcubic_table_verified.json'
    target.write_text(json.dumps(result, indent=2))
    print(json.dumps({k: result[k] for k in ['result', 'direct_positive_records', 'marked_matching_forms']}))


if __name__ == '__main__':
    main()
