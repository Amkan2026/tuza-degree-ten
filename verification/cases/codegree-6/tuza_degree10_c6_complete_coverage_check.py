                                                                      

                                                                       
                                                              
   
import argparse
import hashlib
import json
import sys
import time
import zipfile
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from tuza_degree10_c6_coverage_prefix_check import (
    Uncovered, apply_certificate, remove_impossible, symmetries,
)
from tuza_degree10_c6_literal_prefix_check import check_pair, check_cut


def sha(body):
    return hashlib.sha256(body).hexdigest()


def load(name):
    body = (ROOT / name).read_bytes()
    return body, json.loads(body)


def bind_k24(data, density_bytes, uncovered, P, Q):
    body, report = load('tuza_degree10_c6_K24_human_complete_verified.json')
    assert report['result'] == 'PASS' and report['complete_graph_scope']
    assert report['entire_residual_has_human_proofs']
    assert report['full_cartesian_pairs'] == len(P) * len(Q) == 946729
    assert report['density_verification_sha256'] == sha(density_bytes)
    ordinary = [r for r in data['records'] if r['g6'] == 'E?~o' and r['lane'] == '9/9']
    assert len(ordinary) == report['ordinary_intervals'] == 41
    assert sha(json.dumps(ordinary, sort_keys=True).encode()) == report['ordinary_certificate_subset_sha256']
    residual_bytes, residual = load('tuza_degree10_c6_K24_residual_pairs.json')
    assert sha(residual_bytes) == report['residual_source_sha256']
    expected = {tuple(p) for p in residual['residual_pairs']}
    actual = set()
    for columns, rows in uncovered.rows.items():
        left = []
        right = []
        while rows:
            bit = rows & -rows
            left.append(bit.bit_length() - 1)
            rows ^= bit
        while columns:
            bit = columns & -columns
            right.append(bit.bit_length() - 1)
            columns ^= bit
        actual.update((int(P[i]), int(Q[j])) for i in left for j in right)
    assert actual == expected and len(actual) == report['independent_residual_pairs'] == 193
    partition_bytes, partition = load('tuza_degree10_c6_K24_human_partition_verified.json')
    assert sha(partition_bytes) == report['human_partition_sha256']
    assert partition['status'] == 'PASS' and partition['all_cases_have_complete_human_proofs']
    assert {(r['p'], r['q']) for r in partition['records']} == expected
    assert partition['human_case_counts'] == {
        'two_private_edges': 100, 'one_private_edge': 60, 'full_leaf': 9, 'two_leaf': 24,
    }
    for item in report['proof_bindings'].values():
        proof_bytes = (ROOT / item['proof']).read_bytes()
        checker_bytes = (ROOT / item['checker']).read_bytes()
        witness_bytes, witness = load(item['verified_report'])
        assert sha(proof_bytes) == item['proof_sha256'] == witness['proof_sha256']
        assert sha(checker_bytes) == item['checker_sha256'] == witness['source_sha256']
        assert sha(witness_bytes) == item['verified_report_sha256']
        assert witness['status'] == 'PASS'
    return {'binding_report': 'tuza_degree10_c6_K24_human_complete_verified.json',
            'binding_report_sha256': sha(body), 'ordinary_intervals': 41,
            'fresh_independent_complement_pairs': 193, 'human_proof_partition': partition['human_case_counts']}


def bind_star(name):
    root_bytes, root_review = load('tuza_degree10_c6_human_scope_root_verified.json')
    assert root_review['result'] == 'PASS'
    if name == 'E?Bo':
        proofs = ['tuza_degree10_c6_four_private_human_proof.txt']
        reports = ['tuza_degree10_c6_four_private_human_verified.json',
                   'tuza_degree10_c6_four_private_glue_verified.json']
    else:
        assert name == 'E?Bw'
        proofs = ['tuza_degree10_c6_empty_core_human_proof.txt',
                  'tuza_degree10_c6_double_hub_human_proof.txt',
                  'tuza_degree10_c6_three_hub_human_proof.txt']
        reports = ['tuza_degree10_c6_three_hub_human_verified.json']
    bindings = {name: sha((ROOT / name).read_bytes()) for name in proofs}
    for name in reports:
        body, report = load(name)
        assert report.get('result', report.get('status')) == 'PASS'
        bindings[name] = sha(body)
    checkers = (['tuza_degree10_c6_four_private_human_check.c', 'tuza_degree10_c6_four_private_glue_check.py']
                if 'tuza_degree10_c6_four_private_human_proof.txt' in proofs
                else ['tuza_degree10_c6_three_hub_human_check.py'])
    bindings.update({name: sha((ROOT / name).read_bytes()) for name in checkers})
    assert all(root_review['bindings'][name]['sha256'] == value for name, value in bindings.items())
    return {'proofs_checkers_and_positive_replays': bindings,
            'human_root_review_sha256': sha(root_bytes), 'human_argument_required': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default='tuza_degree10_c6_packed_certificates.json')
    parser.add_argument('--report', default='tuza_degree10_c6_complete_coverage_verified.json')
    args = parser.parse_args()
    started = time.time()
    source_bytes, data = load(args.source)
    domain_bytes, domain_data = load('tuza_degree10_c6_density_domain.json')
    domain = domain_data['records']
    assert len(domain) == 156 and len({r['g6'] for r in domain}) == 156
    lanes = {'7/10', '8/10', '9/10', '10/10', '9/9'}
    expected = {(r['g6'], lane) for r in domain for lane in lanes}
    actual = [(r['g6'], r['lane']) for r in data['reports']]
    assert len(actual) == len(set(actual)) == len(expected) == 780 and set(actual) == expected
    cores_bytes, core_data = load('tuza_degree10_c6_core_certificates.json')
    cores = {r['g6']: r for r in core_data['records']}
    density_bytes, density = load('tuza_degree10_c6_density_verified.json')
    assert density['result'] == 'PASS' and density['complete_side_domains'] == 624
    meta = {(r['g6'], r['private_size']): r for r in density['records']}
    assert set(meta) == {(r['g6'], size) for r in domain for size in range(4)}
    raw_bytes, raw = load('tuza_degree10_c6_domain_independent_verified.json')
    assert raw['result'] == 'PASS' and raw['complete_side_domains'] == 624
    raw_map = {(r['g6'], r['private_size']): r for r in raw['records']}
    assert len(raw['records']) == len(raw_map) == 624 and set(raw_map) == set(meta)
    for key, record in raw_map.items():
        assert record['result'] == 'PASS'
        assert record['patterns_sha256'] == meta[key]['raw_sha256']
        assert record['retained_candidate_patterns'] == meta[key]['raw_retained_patterns']
    orbit_bytes, orbit = load('tuza_degree10_c6_common_orbit_verified.json')
    assert orbit['status'] == 'PASS' and orbit['full_common_graph_domain']
    assert orbit['all_graph6_H_labels_consistent'] and orbit['all_orbits_pairwise_disjoint']
    assert orbit['common_graph_types'] == 156 and orbit['all_labelled_six_vertex_graphs'] == 32768
    assert orbit['density_domain_sha256'] == sha(domain_bytes)
    assert orbit['source_sha256'] == sha((ROOT / 'tuza_degree10_c6_common_orbit_audit.py').read_bytes())
    by_name = {r['g6']: r for r in domain}
    certificates = {}
    literal_count = {'pair': 0, 'subset_cut': 0}
    for rec in data['records']:
        key = (rec['g6'], rec['lane'])
        assert key in expected and rec['kind'] in literal_count
        sa, sb = (int(d) - 7 for d in rec['lane'].split('/'))
        H = by_name[rec['g6']]['H']
        proof = check_pair(rec, H, sa, sb) if rec['kind'] == 'pair' else check_cut(rec, H, sa, sb)
        certificates.setdefault(key, []).append((rec, proof))
        literal_count[rec['kind']] += 1
    core_count = 0
    for row in core_data['records']:
        for spare, rec in row['certificates'].items():
            if rec['status'] == 'PASS':
                check_pair(rec, row['H'], 0, 0, int(spare))
                core_count += 1
    output = []
    human = []
    total = 0
    resolved = set()
    with zipfile.ZipFile(ROOT / 'tuza_degree10_c6_density_patterns_cache.zip') as cache:
        for report in data['reports']:
            name, lane = report['g6'], report['lane']
            sa, sb = (int(d) - 7 for d in lane.split('/'))
            row = by_name[name]
            H = row['H']
            arrays = []
            for size in (sa, sb):
                encoded = cache.read(row['sides'][str(size)]['file'])
                assert sha(encoded) == meta[name, size]['selected_sha256']
                arrays.append(np.frombuffer(zlib.decompress(encoded), dtype='<u4'))
            P, Q = arrays
            count = len(P) * len(Q)
            total += count
            if 'selected_density_side_counts' in report:
                assert report['selected_density_side_counts'] == [len(P), len(Q)]
            if count == 0:
                assert report['residual'] == 0
                mode = 'empty_domain'
            elif report.get('core_only'):
                assert report['residual'] == 0
                rec = cores[name]['certificates'][str(sa + sb)]
                assert rec['status'] == 'PASS'
                check_pair(rec, H, 0, 0, sa + sb)
                mode = 'core_with_selected_private_spokes'
            elif report.get('human_star_lemma'):
                assert report['residual'] == 0 and lane == '10/10'
                degrees = sorted(sum(v in e for e in H) for v in range(6))
                assert degrees == ([0, 1, 1, 1, 1, 4] if name == 'E?Bo' else [1, 1, 1, 1, 1, 5])
                binding = bind_star(name)
                human.append({'g6': name, 'lane': lane, 'candidate_pairs': count, **binding})
                mode = 'bound_universal_human_star_argument'
            else:
                uncovered = Uncovered(len(P), len(Q))
                remove_impossible(H, P, Q, sa, sb, uncovered)
                autos = symmetries(H)
                for rec, proof in certificates.get((name, lane), []):
                    apply_certificate(rec, proof, autos, P, Q, sa, sb, uncovered)
                    if not uncovered.rows:
                        break
                if (name, lane) == ('E?~o', '9/9'):
                    assert report['residual'] == 193
                    binding = bind_k24(data, density_bytes, uncovered, P, Q)
                    resolved.add((name, lane))
                    human.append({'g6': name, 'lane': lane, 'candidate_pairs': count, **binding})
                    mode = 'ordinary_intervals_plus_bound_human_complement'
                else:
                    assert report['residual'] == 0 and uncovered.count() == 0, (name, lane, uncovered.count())
                    mode = 'independent_interval_replay'
            output.append({'g6': name, 'lane': lane, 'candidate_pairs': count, 'proof_mode': mode})
            print('PASS', name, lane, count, mode, round(time.time() - started, 1), flush=True)
    for failure in data.get('failures', []):
        assert (failure['g6'], failure['lane']) in resolved
        assert failure['status'] == 'UNKNOWN' and failure['p'] == failure['q'] == 1023
    required_helpers = ['tuza_degree10_c6_coverage_prefix_check.py', 'tuza_degree10_c6_literal_prefix_check.py']
    result = {'result': 'PASS', 'scope': 'all 780 complete endpoint lanes, with named human arguments bound separately',
              'complete_domain': True, 'closed_lanes_replayed': len(output), 'candidate_pairs': total,
              'ordinary_pair_certificates': literal_count['pair'], 'subset_cut_certificates': literal_count['subset_cut'],
              'core_spare_certificates': core_count, 'human_arguments': human, 'records': output,
              'historical_unknown_diagnostics': len(data.get('failures', [])), 'unresolved_diagnostics': 0,
              'source_sha256': sha(source_bytes), 'domain_sha256': sha(domain_bytes), 'core_sha256': sha(cores_bytes),
              'density_verification_sha256': sha(density_bytes), 'checker_sha256': sha(Path(__file__).read_bytes()),
              'raw_domain_verification_sha256': sha(raw_bytes), 'common_orbit_verification_sha256': sha(orbit_bytes),
              'helper_source_sha256': {name: sha((ROOT / name).read_bytes()) for name in required_helpers},
              'seconds': time.time() - started}
    target = ROOT / args.report
    pending = target.with_suffix('.pending')
    pending.write_text(json.dumps(result, indent=2))
    pending.replace(target)
    print('COMPLETE', len(output), total, len(human), flush=True)


if __name__ == '__main__':
    main()
