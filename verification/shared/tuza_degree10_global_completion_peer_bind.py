                                                                            
from pathlib import Path
import hashlib
import json

BASE = Path('work')
bindings = json.loads((BASE/'tuza_degree10_global_peer_current_hashes.json').read_text())


def read(name):
    path = BASE/name
    raw = path.read_bytes()
    bindings[str(path)] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
    value = json.loads(raw)
    assert str(value.get('result', value.get('status', ''))).startswith('PASS'), name
    return value


reports = {name: read(name) for name in [
    'tuza_degree10_subcubic_link_basis_verified.json',
    'tuza_degree10_c4_final_verified.json',
    'tuza_degree10_c5_verification_manifest.json',
    'tuza_degree10_c5_final_scope_gate.json',
    'tuza_degree10_c7_compressed_verified.json',
    'tuza_degree10_c8_verified.json',
    'tuza_degree10_c9_verified.json',
    'tuza_degree10_high_sparse_verified.json',
    'tuza_degree10_c6_fresh_source_verified.json',
]}


def bound(report, field, filename):
    assert report[field] == bindings['work/'+filename]['sha256'], (field, filename)


r = reports['tuza_degree10_subcubic_link_basis_verified.json']
for field, name in [
    ('payload_sha256', 'tuza_degree10_subcubic_link_basis.json.gz'),
    ('proof_sha256', 'tuza_degree10_subcubic_branch_proof.txt'),
    ('source_sha256', 'tuza_degree10_subcubic_link_basis_check.py'),
    ('helper_source_sha256', 'tuza_book3_condensed_root_check.py'),
]:
    bound(r, field, name)
r = reports['tuza_degree10_c4_final_verified.json']
bound(r, 'source_sha256', 'tuza_degree10_c4_lex_intervals.json')
assert r['all_48_domains_match_initial_catalog'] and not r['uncovered_after_human_case']
r = reports['tuza_degree10_c5_verification_manifest.json']
assert r['complete_graph_scope'] and not r['complete_pair_scope'] and not r['graph_cases_unclosed']
r = reports['tuza_degree10_c7_compressed_verified.json']
assert r['new_complete_lanes'] == 662
for field, name in [
    ('core_sha256', 'tuza_degree10_c7_core_certificates.json'),
    ('domain_sha256', 'tuza_degree10_c7_side_domain.json'),
    ('residual_sha256', 'tuza_degree10_c7_compressed_certificates.json'),
]:
    bound(r, field, name)
for c in [8, 9]:
    r = reports[f'tuza_degree10_c{c}_verified.json']
    bound(r, 'core_sha256', 'tuza_degree10_common8_slack2_probe.json')
    bound(r, 'residual_sha256', f'tuza_degree10_c{c}_residual_certificates.json')
    if c == 9:
        bound(r, 'human_sha256', 'tuza_degree10_c9_dense_human_certificates.json')

old = {
    4: {(7,7), (7,8), (8,8)},
    5: {(7,7), (7,8), (7,9), (8,8), (8,9), (9,9)},
    6: {(7,7), (7,8), (7,9), (8,8), (8,9)},
    7: {(8,8), (8,9), (9,9)},
    8: {(9,9)},
    9: set(),
}
old_sources = {
    4: 'work/tuza_degree10_c4_old_transfer_verified.json',
    5: 'work/tuza_degree10_c5_verification_manifest.json',
    6: 'work/tuza_degree10_c6_lower_endpoint_transfer_audit.json',
    7: 'work/tuza_degree10_c7_old_lane_transfer_audit.json',
    8: 'work/tuza_degree9_common8_pair_verified.json plus work/tuza_degree10_high_sparse_verified.json',
}
new_sources = {
    4: 'work/tuza_degree10_c4_final_verified.json',
    5: 'work/tuza_degree10_c5_verification_manifest.json',
    7: 'work/tuza_degree10_c7_compressed_verified.json',
    8: 'work/tuza_degree10_c8_verified.json',
    9: 'work/tuza_degree10_c9_verified.json',
}
lanes = []
for c, minimum in [(4,7), (5,7), (6,7), (7,8), (8,9), (9,10)]:
    for a in range(minimum, 11):
        for b in range(a, 11):
            if c == 6 and (a,b) not in old[c]:
                status = 'PENDING final common-six 780 replay'
                source = 'root final payload and complete780 independent report, not yet closed'
            elif (a,b) in old[c]:
                status = 'PASS ambient-ten scope transfer'
                source = old_sources[c]
            else:
                status = 'PASS complete ambient-ten graph scope'
                source = new_sources[c]
            lanes.append({'maximum_codegree': c, 'endpoint_degrees': [a,b], 'status': status, 'binding_source': source})
assert len(lanes) == len({(r['maximum_codegree'], *r['endpoint_degrees']) for r in lanes}) == 40
assert sum(r['status'].startswith('PENDING') for r in lanes) == 5

for name in ['tuza_degree10_global_completion_peer_audit.txt', 'tuza_degree10_subcubic_branch_peer_audit.txt']:
    path = BASE/name
    raw = path.read_bytes()
    bindings[str(path)] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}

c9_chain = BASE/'tuza_degree10_c9_full_children_verified.json'
if c9_chain.exists():
    report = read(c9_chain.name)
    assert report['all_canonical_children'] == 2472012
    c9_chain_status = 'PASS complete independent child regeneration'
else:
    c9_chain_status = 'source and corpus byte-bound; fresh complete independent regeneration in progress'

output = {
    'status': 'PENDING common-six closure',
    'claims_full_maximum_degree_ten_theorem': False,
    'scope': 'Complete logical partition and byte-bound completed inputs for ambient maximum degree ten',
    'minimality': 'proper vertex and edge subgraphs',
    'max_codegree_possible': 9,
    'global_minimum_degree': 5,
    'global_minimum_degree_seven_only_branch': 4,
    'required_unordered_endpoint_lanes': 40,
    'completed_endpoint_lanes': 35,
    'pending_endpoint_lanes': 5,
    'endpoint_lane_table': lanes,
    'codegree_at_most_three': 'PASS standalone subcubic P/R branch; no MAD theorem dependency',
    'common9_full_deletion_chain': c9_chain_status,
    'required_remaining_gate': {
        'branch': 6,
        'endpoint_lanes': [[7,10], [8,10], [9,9], [9,10], [10,10]],
        'common_graph_types_per_lane': 156,
        'total_required_domain_rows': 780,
        'required': [
            'final producer complete with no unresolved records',
            'fresh independent complete780 domain and literal reduction replay',
            'actual final payload SHA bound by that PASS report',
            'current positive-side and density-selection source chain bound',
            'actual H4/H5/K24 human graph-tail proof bytes bound',
        ],
        'prefix_reports_satisfy_gate': False,
        'automatically_promote_when_file_exists': False,
    },
    'common6_side_source_chain': {
        'status': 'PASS fresh complete raw and density source replay',
        'report': 'work/tuza_degree10_c6_fresh_source_verified.json',
        'complete_single_side_domains': 624,
        'common_core_types': 156,
        'all_boolean_patterns': 328443804,
        'constructively_excluded_WKE_patterns': 109611539,
        'fresh_literal_WKE_intervals': 175058,
        'selected_canonical_patterns': 1803814,
        'final780_pair_or_graph_closure_implied': False,
    },
    'human_sparse_premise': {
        'source': 'work/tuza_degree10_high_sparse_human_proof.txt',
        'report': 'work/tuza_degree10_high_sparse_verified.json',
        'old_common8_sparse_rows': 804,
        'fresh_all_common9_sparse_types': 2233,
        'ambient_degree_bound_used': False,
        'removed_vertices': 'selected hub pair only',
    },
    'source_bindings': bindings,
    'scope_notes': {
        'pair_graph_distinction': 'C4/C5/C6 graph tails may use an ambient-edge forcing or a saturated-edge deletion extension; do not infer universal pair reducibility',
        'old_dense_c7': 'Use corrected STS9 twelve-triangle hub-pair reducer, never older full-K9 larger-U ambient-nine budget',
        'old_dense_c5': 'Use corrected30 literal two-hub intervals, never older outside-neighbor budget',
        'old_c6_full_common_cuts': 'Not transferred; old larger-U cuts lie in9/9, included in required fresh780 gate',
        'subcubic_checker_packaging': 'Current checker derives frozen n10 basis from larger positive source. Include it, or make a read-only n10 payload replay and rerun before freeze.',
    },
}
inheritance = BASE/'tuza_degree10_inherited_archive_bindings_verified.json'
if inheritance.exists():
    output['immutable_inherited_source_chain'] = read(inheritance.name)
path = BASE/'tuza_degree10_global_completion_peer_audit.json'
path.write_text(json.dumps(output, indent=2))
print(json.dumps({'status': output['status'], 'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'lanes': 40, 'complete': 35, 'pending': 5}, indent=2))
