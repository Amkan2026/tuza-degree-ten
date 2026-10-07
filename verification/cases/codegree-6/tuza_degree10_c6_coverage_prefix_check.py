                                                                            
import hashlib
import itertools
import json
import sys
import time
import zipfile
import zlib
from pathlib import Path
import numpy as np
sys.path.insert(0, 'work')
from tuza_degree10_c6_literal_prefix_check import check_pair, check_cut, variables

def bitset(values):
    return int.from_bytes(np.packbits(values, bitorder='little').tobytes(), 'little')

class Uncovered:
    def __init__(self, n, m):
        self.rows = {(1 << m)-1: (1 << n)-1} if n and m else {}
    def cover(self, left, right):
        if not left or not right: return
        out = {}
        for remaining, indices in self.rows.items():
            hit = indices & left
            if not hit or not remaining & right:
                out[remaining] = out.get(remaining, 0) | indices
                continue
            miss = indices ^ hit
            if miss: out[remaining] = out.get(remaining, 0) | miss
            new = remaining & ~right
            if new: out[new] = out.get(new, 0) | hit
        self.rows = out
    def count(self):
        return sum(a.bit_count()*b.bit_count() for a, b in self.rows.items())

def symmetries(H):
    E = set(map(tuple, H))
    return [p for p in itertools.permutations(range(6)) if {tuple(sorted((p[a], p[b]))) for a, b in E} == E]

def transform(mask, size, common, private):
    old = variables(size, 8)
    lookup = {e: i for i, e in enumerate(old)}
    result = 0
    for i, (a, b) in enumerate(old):
        if mask >> i & 1:
            x = common[a] if a < 6 else 8+private[a-8]
            y = common[b] if b < 6 else 8+private[b-8]
            result |= 1 << lookup[tuple(sorted((x, y)))]
    return result

def transformed_coefficients(coefficients, size, common, private):
    result = [0]*len(coefficients)
    for i, value in enumerate(coefficients):
        target = transform(1 << i, size, common, private).bit_length()-1
        result[target] = value
    return result

def fit(P, required, forbidden=0):
    return (P & required == required) & (P & forbidden == 0)

def contact_count(P, size, a, b=None):
    result = np.zeros(len(P), dtype=np.int16)
    for j in range(size):
        yes = (P >> (6*j+a) & 1).astype(np.int16)
        if b is not None: yes *= (P >> (6*j+b) & 1).astype(np.int16)
        result += yes
    return result

def remove_impossible(H, P, Q, sa, sb, uncovered):
    adj = [set() for _ in range(6)]
    for a, b in H: adj[a].add(b); adj[b].add(a)
    for a, b in H:
        cap = 4-len(adj[a] & adj[b])
        left = contact_count(P, sa, a, b); right = contact_count(Q, sb, a, b)
        for value in np.unique(left):
            uncovered.cover(bitset(left == value), bitset(right > cap-int(value)))
    for c in range(6):
        if not adj[c]:
            uncovered.cover(bitset(contact_count(P, sa, c) == 0), bitset(contact_count(Q, sb, c) == 0))

def apply_certificate(rec, proof, autos, P, Q, sa, sb, uncovered):
    permutations_a = list(itertools.permutations(range(sa)))
    permutations_b = list(itertools.permutations(range(sb)))
    seen = set()
    for common in autos:
        if rec['kind'] == 'pair':
            left_options = {tuple(transform(v, sa, common, a) for v in proof[0]) for a in permutations_a}
            right_options = {tuple(transform(v, sb, common, b) for v in proof[1]) for b in permutations_b}
            options = [(left_options, right_options)] + ([(right_options, left_options)] if sa == sb else [])
            for left, right in options:
                key = (tuple(sorted(left)), tuple(sorted(right)))
                if key in seen: continue
                seen.add(key)
                lp = np.zeros(len(P), dtype=bool); lq = np.zeros(len(Q), dtype=bool)
                for x in left: lp |= fit(P, *x)
                for y in right: lq |= fit(Q, *y)
                uncovered.cover(bitset(lp), bitset(lq))
            continue
        if rec['kind'] != 'pair':
            left_required = {transform(proof['required'][0], sa, common, a) for a in permutations_a}
            right_required = {transform(proof['required'][1], sb, common, b) for b in permutations_b}
            left_coefficients = {tuple(transformed_coefficients(proof['coefficients'][0], sa, common, a)) for a in permutations_a}
            right_coefficients = {tuple(transformed_coefficients(proof['coefficients'][1], sb, common, b)) for b in permutations_b}
            assert len(left_coefficients) == len(right_coefficients) == 1
            ca = next(iter(left_coefficients)); cb = next(iter(right_coefficients))
            options = [(left_required, right_required, ca, cb)] + ([(right_required, left_required, cb, ca)] if sa == sb else [])
            for left, right, cx, cy in options:
                key = (tuple(sorted(left)), tuple(sorted(right)), cx, cy)
                if key in seen: continue
                seen.add(key)
                lp = np.zeros(len(P), dtype=bool); lq = np.zeros(len(Q), dtype=bool)
                for x in left: lp |= fit(P, x)
                for y in right: lq |= fit(Q, y)
                wp = sum((((P >> i) & 1).astype(np.int16)*v for i, v in enumerate(cx)), np.zeros(len(P), dtype=np.int16))
                wq = sum((((Q >> i) & 1).astype(np.int16)*v for i, v in enumerate(cy)), np.zeros(len(Q), dtype=np.int16))
                bound = 2*len(rec['S'])-proof['constant']
                for value in np.unique(wp[lp]):
                    uncovered.cover(bitset(lp & (wp == value)), bitset(lq & (wq <= bound-int(value))))
            continue
        for a in permutations_a:
            for b in permutations_b:
                if rec['kind'] == 'pair':
                    left = tuple(transform(v, sa, common, a) for v in proof[0])
                    right = tuple(transform(v, sb, common, b) for v in proof[1])
                    for x, y in [(left, right)] + ([(right, left)] if sa == sb else []):
                        key = (x, y)
                        if key in seen: continue
                        seen.add(key)
                        uncovered.cover(bitset(fit(P, *x)), bitset(fit(Q, *y)))
                else:
                    la = transform(proof['required'][0], sa, common, a)
                    lb = transform(proof['required'][1], sb, common, b)
                    ca = transformed_coefficients(proof['coefficients'][0], sa, common, a)
                    cb = transformed_coefficients(proof['coefficients'][1], sb, common, b)
                    for x, y, cx, cy in [(la, lb, ca, cb)] + ([(lb, la, cb, ca)] if sa == sb else []):
                        key = (x, y, tuple(cx), tuple(cy))
                        if key in seen: continue
                        seen.add(key)
                        lp = fit(P, x); lq = fit(Q, y)
                        wp = sum((((P >> i) & 1).astype(np.int16)*v for i, v in enumerate(cx)), np.zeros(len(P), dtype=np.int16))
                        wq = sum((((Q >> i) & 1).astype(np.int16)*v for i, v in enumerate(cy)), np.zeros(len(Q), dtype=np.int16))
                        bound = 2*len(rec['S'])-proof['constant']
                        for value in np.unique(wp[lp]):
                            uncovered.cover(bitset(lp & (wp == value)), bitset(lq & (wq <= bound-int(value))))

if __name__ == '__main__':
    start = time.time()
    source = Path('work/tuza_degree10_c6_packed_checkpoint.json').read_bytes()
    data = json.loads(source)
    domain = json.loads(Path('work/tuza_degree10_c6_density_domain.json').read_bytes())['records']
    cores_bytes = Path('work/tuza_degree10_c6_core_certificates.json').read_bytes()
    cores = {r['g6']: r for r in json.loads(cores_bytes)['records']}
    cache = zipfile.ZipFile('work/tuza_degree10_c6_density_patterns_cache.zip')
    verified_bytes = Path('work/tuza_degree10_c6_density_verified.json').read_bytes()
    verified = json.loads(verified_bytes)
    assert verified['result'] == 'PASS' and verified['complete_side_domains'] == 624
    meta = {(r['g6'], r['private_size']): r for r in verified['records']}
    by_name = {r['g6']: r for r in domain}
    certificates = {}
    for rec in data['records']:
        certificates.setdefault((rec['g6'], rec['lane']), []).append(rec)
    output = []; human = []; total = 0
    for report in data['reports']:
        if report['residual']: continue
        name = report['g6']; sa, sb = (int(d)-7 for d in report['lane'].split('/'))
        row = by_name[name]; H = row['H']
        arrays = []
        for r in (sa, sb):
            encoded = cache.read(row['sides'][str(r)]['file'])
            assert hashlib.sha256(encoded).hexdigest() == meta[name, r]['selected_sha256']
            arrays.append(np.frombuffer(zlib.decompress(encoded), dtype='<u4'))
        P, Q = arrays; count = len(P)*len(Q); total += count
        if not count:
            mode = 'empty_domain'
        elif report.get('core_only'):
            rec = cores[name]['certificates'][str(sa+sb)]
            assert rec['status'] == 'PASS'
            check_pair(rec, H, 0, 0, sa+sb); mode = 'core_spare'
        elif report.get('human_star_lemma'):
            assert name in ('E?Bo', 'E?Bw')
            human.append({'g6': name, 'lane': report['lane'], 'domain': count})
            mode = 'separate_human_proof_required'
        else:
            uncovered = Uncovered(len(P), len(Q)); remove_impossible(H, P, Q, sa, sb, uncovered)
            autos = symmetries(H)
            for rec in certificates.get((name, report['lane']), []):
                proof = check_pair(rec, H, sa, sb) if rec['kind'] == 'pair' else check_cut(rec, H, sa, sb)
                apply_certificate(rec, proof, autos, P, Q, sa, sb, uncovered)
                if not uncovered.rows: break
            assert uncovered.count() == 0, (name, report['lane'], uncovered.count())
            mode = 'independent_interval_replay'
        output.append({'g6': name, 'lane': report['lane'], 'candidate_pairs': count, 'proof_mode': mode})
        print('PASS', name, report['lane'], count, mode, round(time.time()-start, 1), flush=True)
    result = {'result': 'PASS', 'scope': 'all computationally closed checkpoint lanes; listed human lanes require their separate proofs', 'source_sha256': hashlib.sha256(source).hexdigest(), 'core_source_sha256': hashlib.sha256(cores_bytes).hexdigest(), 'density_verification_sha256': hashlib.sha256(verified_bytes).hexdigest(), 'closed_lanes_replayed': len(output), 'candidate_pairs': total, 'human_lanes': human, 'records': output, 'seconds': time.time()-start}
    Path('work/tuza_degree10_c6_coverage_prefix_verified.json').write_text(json.dumps(result, indent=2))
    print('COMPLETE', len(output), total, len(human), flush=True)
