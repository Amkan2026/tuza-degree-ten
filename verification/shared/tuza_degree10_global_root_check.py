                                                                         

                                                                          
                                                                         
                                                      
   
import gzip
import hashlib
import itertools
import json
import time
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
WORK = BASE / 'work'


def sha(body):
    return hashlib.sha256(body).hexdigest()


def load(name):
    body = (WORK / name).read_bytes()
    return body, json.loads(body)


def bound_bytes(name, row):
    if 'read_from_exact_gzip' in row:
        return gzip.decompress((BASE / row['read_from_exact_gzip']).read_bytes())
    if 'read_from_immutable_zip' in row:
        with zipfile.ZipFile(BASE / row['read_from_immutable_zip']) as archive:
            return archive.read(row['member'])
    return (BASE / name).read_bytes()


def main():
    started = time.time()
    peer_bytes, peer = load('tuza_degree10_global_completion_peer_audit.json')
    assert peer['claims_full_maximum_degree_ten_theorem'] is True
    assert peer['completed_endpoint_lanes'] == peer['required_unordered_endpoint_lanes'] == 40
    assert peer['pending_endpoint_lanes'] == 0
    expected = {(c, a, b) for c in range(4, 10)
                for a, b in itertools.combinations_with_replacement(range(max(7, c + 1), 11), 2)}
    assert len(expected) == 40
    rows = peer['endpoint_lane_table']
    actual = [(r['maximum_codegree'], *r['endpoint_degrees']) for r in rows]
    assert len(actual) == len(set(actual)) == 40 and set(actual) == expected
    assert all(r['status'].startswith('PASS') for r in rows)
    assert peer['global_minimum_degree'] == 5
    assert peer['global_minimum_degree_seven_only_branch'] == 4
    assert peer['max_codegree_possible'] == 9
    bindings = {}
    for name, row in peer['source_bindings'].items():
        body = bound_bytes(name, row)
        assert sha(body) == row['sha256'], name
        if 'bytes' in row:
            assert len(body) == row['bytes'], name
        bindings[name] = {'bytes': len(body), 'sha256': sha(body)}
    c6_bytes, c6 = load('tuza_degree10_c6_complete_coverage_verified.json')
    payload_name = c6['certificate_source_file']
    assert payload_name in ('tuza_degree10_c6_packed_certificates.json', 'tuza_degree10_c6_merged_certificates.json')
    payload = (WORK / payload_name).read_bytes()
    assert c6['result'] == 'PASS' and c6['complete_domain']
    assert c6['source_sha256'] == sha(payload)
    assert c6['closed_lanes_replayed'] == 780 and c6['unresolved_diagnostics'] == 0
    six_expected = {(g, lane) for g in [r['g6'] for r in json.loads((WORK / 'tuza_degree10_c6_density_domain.json').read_bytes())['records']]
                    for lane in ['7/10', '8/10', '9/10', '10/10', '9/9']}
    assert len(six_expected) == 780
    assert {(r['g6'], r['lane']) for r in c6['records']} == six_expected
    assert len(c6['records']) == 780
    assert c6['fresh_side_domains_replayed'] == 624
    assert c6['fresh_boolean_patterns_replayed'] == 328443804
    assert c6['fresh_literal_WKE_intervals_replayed'] == 175058
    source_hash_fields = {
        'checker_sha256': 'tuza_degree10_c6_complete_coverage_check.py',
        'optimized_wrapper_source_sha256': 'tuza_degree10_c6_complete_fast_check.py',
        'optimized_relation_source_sha256': 'tuza_degree10_c6_dense_uncovered.py',
        'literal_relation_verification_sha256': 'tuza_degree10_c6_dense_uncovered_verified.json',
        'fresh_side_source_verification_sha256': 'tuza_degree10_c6_fresh_source_verified.json',
        'density_verification_sha256': 'tuza_degree10_c6_density_verified.json',
        'raw_domain_verification_sha256': 'tuza_degree10_c6_domain_independent_verified.json',
        'common_orbit_verification_sha256': 'tuza_degree10_c6_common_orbit_verified.json',
    }
    for field, name in source_hash_fields.items():
        body = (WORK / name).read_bytes()
        assert c6[field] == sha(body), name
        bindings['work/' + name] = {'bytes': len(body), 'sha256': sha(body)}
    for name, value in c6['helper_source_sha256'].items():
        assert value == sha((WORK / name).read_bytes()), name
    sub_bytes, sub = load('tuza_degree10_subcubic_link_basis_verified.json')
    assert sub['result'] == 'PASS' and sub['complete_min2_domain_types'] == 702
    assert sub['whole_connected_types'] == 2561
    assert sub['proper_colorings_converted_to_literal_WKE'] == 660 and sub['direct_WKE_witnesses'] == 40
    assert sub['only_remaining_types'] == ['P', 'R']
    assert sub['Petersen_pair']['common_identifications'] == 6
    assert len(sub['Petersen_pair']['packing']) == 7 and len(sub['Petersen_pair']['cover']) == 14
    assert sub['payload_sha256'] == sha((WORK / 'tuza_degree10_subcubic_link_basis.json.gz').read_bytes())
    children_bytes, children = load('tuza_degree10_c9_full_children_verified.json')
    assert children['result'] == 'PASS' and children['all_canonical_children'] == 2472012
    assert children['fresh_common9_parent_types'] == 274668
    assert children['complete_child_sha256'] == sha((WORK / 'tuza_degree10_c9_deleted_canonical_graph6.txt').read_bytes())
    assert children['parent_sha256'] == sha((WORK / 'tuza_degree10_c9_all_graph6.txt').read_bytes())
    assert children['checker_sha256'] == sha((WORK / 'tuza_degree10_c9_full_children_check.py').read_bytes())
    result = {
        'result': 'PASS_COMPLETE_MAXIMUM_DEGREE_TEN_SCOPE_AND_BINDINGS',
        'theorem': 'Every finite simple graph G with maximum degree at most10 satisfies tau(G)<=2nu(G).',
        'computer_assisted': True,
        'external_peer_review': False,
        'priority_claim': False,
        'required_endpoint_lanes': 40,
        'completed_endpoint_lanes': 40,
        'all_maximum_codegrees_covered': list(range(10)),
        'codegree_at_most_three': 'human coloring/leaf/diamond/Petersen proof with complete702-type positive premise',
        'human_proofs_required': True,
        'human_review': 'Root reviewed the global partition, ambient degree scope and recorded human lemmas. The source-bound peer audit supplies the same independent review.',
        'endpoint_lane_table': rows,
        'c6_complete_lanes': 780,
        'c6_candidate_pairs': c6['candidate_pairs'],
        'c6_payload_sha256': sha(payload),
        'c6_payload_file': payload_name,
        'c6_complete_report_sha256': sha(c6_bytes),
        'peer_scope_report_sha256': sha(peer_bytes),
        'subcubic_report_sha256': sha(sub_bytes),
        'full_common9_children_report_sha256': sha(children_bytes),
        'source_bindings': bindings,
        'root_checker_sha256': sha(Path(__file__).read_bytes()),
        'seconds': time.time() - started,
    }
    target = WORK / 'tuza_degree10_global_root_verified.json'
    temporary = target.with_suffix('.pending')
    temporary.write_text(json.dumps(result, indent=2))
    temporary.replace(target)
    print(json.dumps({k: v for k, v in result.items() if k not in ('endpoint_lane_table', 'source_bindings')}), flush=True)


if __name__ == '__main__':
    main()
