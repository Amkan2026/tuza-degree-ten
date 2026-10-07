                                                                           

                                                                           
                                                                            
                                                                             
                                                 
   
from pathlib import Path
from itertools import combinations, permutations
from functools import lru_cache
import json
import subprocess

HERE = Path(__file__).resolve().parent
PAIRS = tuple(combinations(range(6), 2))


def edge(x, y):
    return tuple(sorted((x, y)))


def adjacency(es, n):
    nb = [set() for _ in range(n)]
    for x, y in es:
        nb[x].add(y)
        nb[y].add(x)
    return nb


def connected(es, n):
    nb = adjacency(es, n)
    seen = {0}
    while True:
        more = seen.union(*(nb[x] for x in seen))
        if more == seen:
            return len(seen) == n
        seen = more


def wke(es, n):
    nb = adjacency(es, n)
    @lru_cache(None)
    def maximum_matching(vs):
        if not vs:
            return 0
        x = min(vs)
        rest = vs - {x}
        return max([maximum_matching(rest)] +
                   [1 + maximum_matching(rest - {y}) for y in nb[x] & rest])
    all_vertices = frozenset(range(n))
    for size in range(n // 2 + 1):
        for q in combinations(range(n), size):
            outside = all_vertices - set(q)
            forced = [e for e in es if set(e) <= outside]
            used = [x for e in forced for x in e]
            if len(used) != len(set(used)):
                continue
            if len(forced) + maximum_matching(all_vertices - set(used)) >= size:
                return True
    return False


def decode_core(key):
    bits = [ord(c) - 63 for c in key]
    n = bits[0]
    nb = [set() for _ in range(n)]
    k = 0
    for y in range(1, n):
        for x in range(y):
            if bits[1 + k // 6] & (1 << (5 - k % 6)):
                nb[x].add(y)
                nb[y].add(x)
            k += 1
    isolated = [x for x in range(n) if not nb[x]]
    if len(isolated) < 2:
        return None
    keep = [x for x in range(n) if x not in isolated[:2]]
    assert len(keep) == 6
    return {e for e in PAIRS if keep[e[1]] in nb[keep[e[0]]]}


def graph(H, side):
    return ({(x + 2, y + 2) for x, y in H}
            | {(0, 1), (1, 9)}
            | {(h, c) for h in (0, 1) for c in range(2, 8)}
            | {(x + 2, 9) for x in range(6) if side >> x & 1})


def validate(S, X, G):
    X = set(map(tuple, X))
    assert X <= G and len(X) <= 2 * len(S)
    used = set()
    for t in S:
        assert len(t) == 3 and len(set(t)) == 3
        es = {edge(x, y) for x, y in combinations(t, 2)}
        assert es <= G and not used & es
        used |= es
    assert all(e in X for e in used if not set(e) & {0, 1})
    for t in combinations(range(10), 3):
        if not set(t) & {0, 1}:
            continue
        es = set(combinations(t, 2))
        if es <= G:
            assert es & X


def transformed(S, X, p, swap=False):
    move = {0: int(swap), 1: 1 - int(swap),
            8: 9 if swap else 8, 9: 8 if swap else 9}
    move.update({x + 2: p[x] + 2 for x in range(6)})
    return ([sorted(move[x] for x in t) for t in S],
            {edge(move[x], move[y]) for x, y in X})


def delete_absent_side(S, X):
    return [t for t in S if 8 not in t], {e for e in X if 8 not in e}


def interval_witness(interval, H):
    R = set(map(tuple, interval['R']))
    Q = set(interval['Q'])
    for p in permutations(range(6)):
        moved_R = {edge(p[x], p[y]) for x, y in R}
        moved_Q = {p[x] for x in Q}
        if moved_R <= H and all(set(e) & moved_Q for e in H - moved_R):
            S, X = transformed(interval['packing'], interval['cover'], p)
            return delete_absent_side(S, X)
    return None


def main():
    fresh = subprocess.run(['/opt/homebrew/bin/geng', '-q', '8'],
                           check=True, capture_output=True, text=True).stdout
    domain = {key: H for key in fresh.splitlines()
              if (H := decode_core(key)) is not None}
    assert len(domain) == 156
    intervals = json.loads((HERE / 'tuza_c6_active_ordinary_interval_templates.json').read_text())['intervals']
    rows = json.loads((HERE / 'tuza_c6_human_compressed_templates.json').read_text())['rows']
    row_by_key = {r['key']: r for r in rows}
    count = 0
    counts = {}
    remainder = {}
    used_core = set()
    deletion_checks = 0
                                                                           
                                                                            
                                                                       
    for row in rows:
        H = set(map(tuple, row['core_edges']))
        for t in row['selected_templates']:
            for swap in (False, True):
                S, X = transformed(t['packing'], t['cover'], range(6), swap)
                S, X = delete_absent_side(S, X)
                w = t['required_contacts'][int(not swap)]
                side = 1 << w if w >= 0 else 0
                validate(S, X, graph(H, side))
                deletion_checks += 1
    for key, H in domain.items():
        seven_link = H | {(x, 6) for x in range(6)}
        if wke(seven_link, 7):
            continue
        ordinary = interval_witness(intervals[0], H) if False else None
        for interval in intervals:
            if (ordinary := interval_witness(interval, H)) is not None:
                break
        if key in row_by_key:
            ps = [p for p in permutations(range(6))
                  if {edge(p[x], p[y]) for x, y in H} == H]
        for side in range(64):
            eight_link = seven_link | {(x, 7) for x in range(6) if side >> x & 1}
            if not connected(eight_link, 8) or wke(eight_link, 8):
                continue
            G = graph(H, side)
            nb = adjacency(G, 10)
            if max(map(len, nb)) > 8 or any(len(nb[x] & nb[y]) > 6 for x, y in G):
                continue
            count += 1
            used_core.add(key)
            if ordinary is not None:
                S, X = ordinary
                kind = 'interval'
            elif key in row_by_key:
                chosen = None
                for t in row_by_key[key]['selected_templates']:
                    for p in ps:
                        for swap in (False, True):
                            contact = t['required_contacts'][int(not swap)]
                            if contact >= 0 and not side >> p[contact] & 1:
                                continue
                            S, X = transformed(t['packing'], t['cover'], p, swap)
                            chosen = delete_absent_side(S, X)
                            break
                        if chosen is not None:
                            break
                    if chosen is not None:
                        break
                assert chosen is not None, (key, side, 'uncovered projected contact')
                S, X = chosen
                kind = 'displayed_twenty_core'
            else:
                assert any(all(e in H for e in combinations([x for x in range(6) if x != z], 2))
                           for z in range(6)) or (
                           len(H) == 13 and len({x for e in set(PAIRS) - H for x in e}) == 4), (key, side)
                remainder[key] = remainder.get(key, 0) + 1
                continue
            validate(S, X, G)
            counts[kind] = counts.get(kind, 0) + 1
    assert len(used_core) == 43 and count == 693
    result = {'result': 'PASS', 'fresh_common_cores': len(domain),
              'mixed_active_common_cores': len(used_core),
              'mixed_side_models': count, 'projected_minimal_template_checks': deletion_checks,
              'coverage_counts': counts, 'remaining_human_clique_or_two_matching_cores': remainder}
    (HERE / 'tuza_c6_mixed_reuse_verified.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
