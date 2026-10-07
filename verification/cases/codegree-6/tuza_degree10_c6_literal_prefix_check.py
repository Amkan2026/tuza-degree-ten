                                                                           
import copy
import hashlib
import itertools
import json
from pathlib import Path

def edge(a, b):
    return tuple(sorted((a, b)))

def variables(size, first):
    return [(c, first+j) for j in range(size) for c in range(6)] + list(itertools.combinations(range(first, first+size), 2))

def baseline(H, sa, sb):
    return set(map(tuple, H)) | {(c, h) for c in range(6) for h in (6, 7)} | {(6, 7)} | {(6, a) for a in range(8, 8+sa)} | {(7, b) for b in range(11, 11+sb)}

def local(H, sa, sb, p, q):
    E = baseline(H, sa, sb)
    for r, first, value in [(sa, 8, p), (sb, 11, q)]:
        E.update(e for i, e in enumerate(variables(r, first)) if value >> i & 1)
    return E

def triples(E):
    return [t for t in itertools.combinations(range(14), 3) if all(e in E for e in itertools.combinations(t, 2))]

def packing(S, E):
    used = set()
    for t in S:
        assert len(t) == 3 and len(set(t)) == 3
        rims = {edge(a, b) for a, b in itertools.combinations(t, 2)}
        assert rims <= E and not used & rims
        used.update(rims)
    return used

def check_pair(rec, H, sa, sb, spare=0):
    X = set(map(tuple, rec['X']))
    if 'p' in rec and 'q' in rec:
        E = local(H, sa, sb, rec['p'], rec['q'])
    else:
        E = baseline(H, sa, sb) | X
        E.update(edge(a, b) for t in rec['S'] for a, b in itertools.combinations(t, 2))
        possible = baseline(H, sa, sb) | set(variables(sa, 8)) | set(variables(sb, 11))
        assert E <= possible
    assert len(X) == len(rec['X']) and X <= E
    used = packing(rec['S'], E)
    assert len(X)+spare <= 2*len(rec['S'])
    assert all({6, 7} & set(e) or e in X for e in used)
    low = baseline(H, sa, sb)
    upper = set(low)
    masks = []
    for r, first, hub in [(sa, 8, 6), (sb, 11, 7)]:
        required = forbidden = 0
        for i, e in enumerate(variables(r, first)):
            if e in used:
                required |= 1 << i
                low.add(e)
            if e not in X and all(edge(hub, v) not in X for v in e):
                forbidden |= 1 << i
            else:
                upper.add(e)
        assert not required & forbidden
        masks.append([required, forbidden])
    packing(rec['S'], low)
    for t in triples(upper):
        if {6, 7} & set(t):
            assert set(itertools.combinations(t, 2)) & X
    return masks

def check_cut(rec, H, sa, sb):
    E = local(H, sa, sb, rec['p'], rec['q'])
    U = set(rec['U']); Z = U-{6, 7}
    assert {6, 7} <= U <= set(range(8))
    colors = rec['colors']
    assert len(colors) == 14 and set(colors) <= {0, 1}
    assert all(colors[a] == 0 for a in range(8, 8+sa))
    assert all(colors[b] == 1 for b in range(11, 11+sb))
    X = {e for e in E if colors[e[0]] == colors[e[1]]}
    assert X == set(map(tuple, rec['X']))
    used = packing(rec['S'], E)
    assert all(U & set(e) or e in X for e in used)
    deficit = sum(10-sum(c in e for e in E) for c in Z)
    assert all(sum(c in e for e in E) <= 10 for c in Z)
    assert rec['outside_bound'] == deficit
    assert rec['total_cover_bound'] == len(X)+deficit <= 2*len(rec['S'])
    base = baseline(H, sa, sb)
    constant = sum(colors[a] == colors[b] for a, b in base) + sum(10-sum(c in e for e in base) for c in Z)
    coefficients = []
    required = []
    evaluated = constant
    for r, first, value in [(sa, 8, rec['p']), (sb, 11, rec['q'])]:
        coef = []; bits = 0
        for i, (a, b) in enumerate(variables(r, first)):
            coefficient = int(colors[a] == colors[b])-int(a in Z)-int(b in Z)
            coef.append(coefficient)
            if value >> i & 1:
                evaluated += coefficient
            if (a, b) in used:
                bits |= 1 << i
        coefficients.append(coef); required.append(bits)
    assert evaluated == len(X)+deficit
    return {'required': required, 'constant': constant, 'coefficients': coefficients}

if __name__ == '__main__':
    path = Path('work/tuza_degree10_c6_packed_checkpoint.json')
    source = path.read_bytes(); data = json.loads(source)
    dom = json.loads(Path('work/tuza_degree10_c6_domain.json').read_text())['records']
    by_name = {r['g6']: r['H'] for r in dom}
    output = []; pair_count = cut_count = 0
    for rec in data['records']:
        sa, sb = (int(d)-7 for d in rec['lane'].split('/'))
        H = by_name[rec['g6']]
        if rec['kind'] == 'pair':
            proof = check_pair(rec, H, sa, sb); pair_count += 1
        else:
            assert rec['kind'] == 'subset_cut'
            proof = check_cut(rec, H, sa, sb); cut_count += 1
        output.append({'g6': rec['g6'], 'lane': rec['lane'], 'kind': rec['kind'], 'interval': proof})
    cores_path = Path('work/tuza_degree10_c6_core_certificates.json')
    cores_bytes = cores_path.read_bytes(); core_count = 0
    for row in json.loads(cores_bytes)['records']:
        for spare, rec in row['certificates'].items():
            if rec['status'] == 'PASS':
                check_pair(rec, row['H'], 0, 0, int(spare)); core_count += 1
    original = next(r for r in data['records'] if r['kind'] == 'pair')
    sa, sb = (int(d)-7 for d in original['lane'].split('/'))
    controls = []
    for name, mutation in [('duplicated_triangle', 'duplicate'), ('empty_cover', 'cover'), ('absent_packing_edge', 'edge')]:
        bad = copy.deepcopy(original)
        if mutation == 'duplicate': bad['S'].append(bad['S'][0])
        if mutation == 'cover': bad['X'] = []
        if mutation == 'edge': bad['S'][0] = [6, 7, 13]
        try: check_pair(bad, by_name[bad['g6']], sa, sb)
        except AssertionError: controls.append({'mutation': name, 'rejected': True})
        else: raise AssertionError(name)
    result = {'result': 'PASS', 'scope': 'literal certificate library only; full finite coverage remains a separate check', 'source_sha256': hashlib.sha256(source).hexdigest(), 'core_source_sha256': hashlib.sha256(cores_bytes).hexdigest(), 'ordinary_pair_certificates': pair_count, 'subset_cut_certificates': cut_count, 'core_spare_certificates': core_count, 'negative_controls': controls, 'records': output}
    Path('work/tuza_degree10_c6_literal_prefix_verified.json').write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'records'}), flush=True)
