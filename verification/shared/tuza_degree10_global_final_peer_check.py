                                                                         

                                                                      
                                                                           
   
import gzip
import hashlib
import json
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
WORK = BASE / 'work'


def digest(body):
    return hashlib.sha256(body).hexdigest()


def load(name):
    body = (WORK / name).read_bytes()
    return body, json.loads(body)


def actual(name, row):
    if 'read_from_exact_gzip' in row:
        return gzip.decompress((BASE / row['read_from_exact_gzip']).read_bytes())
    if 'read_from_immutable_zip' in row:
        with zipfile.ZipFile(BASE / row['read_from_immutable_zip']) as archive:
            return archive.read(row['member'])
    return (BASE / name).read_bytes()


def main():
    pending_bytes, peer = load('tuza_degree10_global_completion_peer_audit.json')
    assert not peer['claims_full_maximum_degree_ten_theorem']
    assert peer['completed_endpoint_lanes'] == 35 and peer['pending_endpoint_lanes'] == 5
    bindings = peer['source_bindings']

                                                                              
                                                                                  
    refreshed_c6 = {
        'work/tuza_degree10_c6_human_scope_root_verified.json',
    }
    for name, row in bindings.items():
        if name in refreshed_c6:
            continue
        body = actual(name, row)
        assert digest(body) == row['sha256'], name
        assert len(body) == row['bytes'], name

    def bind(name, expected_hash=None):
        body = (WORK / name).read_bytes()
        if expected_hash is not None:
            assert digest(body) == expected_hash, name
        bindings['work/' + name] = {'sha256': digest(body), 'bytes': len(body)}
        return body

    report_bytes, report = load('tuza_degree10_c6_complete_coverage_verified.json')
    assert report['result'] == 'PASS' and report['complete_domain']
    assert report['closed_lanes_replayed'] == len(report['records']) == 780
    assert report['unresolved_diagnostics'] == 0
    assert report['fresh_side_domains_replayed'] == 624
    assert report['fresh_boolean_patterns_replayed'] == 328443804
    assert report['fresh_literal_WKE_intervals_replayed'] == 175058
    source_name = report['certificate_source_file']
    assert source_name in (
        'tuza_degree10_c6_packed_certificates.json',
        'tuza_degree10_c6_merged_certificates.json',
    )
    source_bytes = bind(source_name, report['source_sha256'])
    source = json.loads(source_bytes)
    assert source['complete_discovery']
    domain_bytes = bind('tuza_degree10_c6_density_domain.json', report['domain_sha256'])
    domain = json.loads(domain_bytes)['records']
    assert len(domain) == len({r['g6'] for r in domain}) == 156
    lanes = {'7/10', '8/10', '9/9', '9/10', '10/10'}
    expected = {(r['g6'], lane) for r in domain for lane in lanes}
    observed = [(r['g6'], r['lane']) for r in report['records']]
    assert len(observed) == len(set(observed)) == len(expected) == 780
    assert set(observed) == expected
    assert {(r['g6'], r['lane']) for r in source['reports']} == expected
    assert len(source['reports']) == 780
    assert report['candidate_pairs'] == sum(r['candidate_pairs'] for r in report['records'])
    bind('tuza_degree10_c6_core_certificates.json', report['core_sha256'])
    for field, name in {
        'checker_sha256': 'tuza_degree10_c6_complete_coverage_check.py',
        'optimized_wrapper_source_sha256': 'tuza_degree10_c6_complete_fast_check.py',
        'optimized_relation_source_sha256': 'tuza_degree10_c6_dense_uncovered.py',
        'literal_relation_verification_sha256': 'tuza_degree10_c6_dense_uncovered_verified.json',
        'fresh_side_source_verification_sha256': 'tuza_degree10_c6_fresh_source_verified.json',
        'density_verification_sha256': 'tuza_degree10_c6_density_verified.json',
        'raw_domain_verification_sha256': 'tuza_degree10_c6_domain_independent_verified.json',
        'common_orbit_verification_sha256': 'tuza_degree10_c6_common_orbit_verified.json',
    }.items():
        bind(name, report[field])
    for name, value in report['helper_source_sha256'].items():
        bind(name, value)

    _, relation = load('tuza_degree10_c6_dense_uncovered_verified.json')
    assert relation['result'] == 'PASS' and relation['literal_relation_checks'] == 2800
    bind('tuza_degree10_c6_dense_uncovered.py', relation['source_sha256'])
    bind('tuza_degree10_c6_coverage_prefix_check.py', relation['fallback_source_sha256'])
    _, fresh = load('tuza_degree10_c6_fresh_source_verified.json')
    assert fresh['result'] == 'PASS_FRESH_COMPLETE_RAW_AND_DENSITY_REPLAY'
    assert fresh['complete_side_domains'] == 624 and fresh['common_graph_types'] == 156
    assert fresh['all_literal_interval_digests_reproduced']
    for name, row in fresh['bindings'].items():
        if name in ('raw_review.dylib', 'density_review.dylib'):
            continue
        filename = 'tuza_degree10_c6_fresh_source_replay.py' if name == 'fresh_replay_source' else name
        bind(filename, row['sha256'])

    human = report['human_arguments']
    assert {(r['g6'], r['lane']) for r in human} == {
        ('E?Bo', '10/10'), ('E?Bw', '10/10'), ('E?~o', '9/9'),
    }
    for entry in human:
        if entry['g6'] != 'E?~o':
            root_bytes = bind('tuza_degree10_c6_human_scope_root_verified.json',
                              entry['human_root_review_sha256'])
            root = json.loads(root_bytes)
            assert root['result'] == 'PASS' and root['human_argument_required']
            for name, value in entry['proofs_checkers_and_positive_replays'].items():
                bind(name, value)
                assert root['bindings'][name]['sha256'] == value
        else:
            body = bind(entry['binding_report'], entry['binding_report_sha256'])
            tail = json.loads(body)
            assert tail['result'] == 'PASS' and tail['complete_graph_scope']
            assert tail['entire_residual_has_human_proofs']
            assert tail['full_cartesian_pairs'] == 946729
            assert tail['independent_residual_pairs'] == entry['fresh_independent_complement_pairs'] == 193
            assert tail['ordinary_intervals'] == 41
            bind('tuza_degree10_c6_K24_residual_pairs.json', tail['residual_source_sha256'])
            partition_bytes = bind('tuza_degree10_c6_K24_human_partition_verified.json',
                                   tail['human_partition_sha256'])
            partition = json.loads(partition_bytes)
            assert partition['status'] == 'PASS' and partition['all_cases_have_complete_human_proofs']
            assert partition['human_case_counts'] == {
                'two_private_edges': 100, 'one_private_edge': 60,
                'full_leaf': 9, 'two_leaf': 24,
            }
            for item in tail['proof_bindings'].values():
                bind(item['proof'], item['proof_sha256'])
                bind(item['checker'], item['checker_sha256'])
                witness_bytes = bind(item['verified_report'], item['verified_report_sha256'])
                witness = json.loads(witness_bytes)
                assert witness['status'] == 'PASS'
                assert witness['proof_sha256'] == item['proof_sha256']
                assert witness['source_sha256'] == item['checker_sha256']

    bind('tuza_degree10_c6_complete_coverage_verified.json', digest(report_bytes))
    bind(Path(__file__).name)
    final_note = WORK / 'tuza_degree10_global_final_peer_audit.txt'
    final_note.write_text(
        'MAXIMUM DEGREE TEN: FINAL PEER CLOSURE AUDIT\n\n'
        'The complete common-six gate passes all780 required graph domains '
        'over156 common graphs in the five endpoint lanes7/10,8/10,9/9,9/10,10/10. '
        'Its source-bound independent report checks every literal pair and common-subset cut, '
        'the exact selected-side domains, all common automorphisms, and the three human graph tails.\n\n'
        'The fresh source-compiled624-side premise, current raw and density reports, '
        '2800 exact relation tests, helper and wrapper sources, and final certificate bytes '
        'match their published hashes. The accelerated storage changes no rectangle '
        'subtraction, literal reduction rule, or finite graph domain.\n\n'
        'The two star tails use the recorded private matching constructions. '
        'The K1,4-plus-isolate argument uses the non-WKE private classification '
        'and the maximum-common-density choice to exclude center/private contacts. '
        'The K1,5 argument joins the two retained private P3 or triangle links '
        'through three closed hubs, with nine packed triangles and eighteen cover edges. '
        'The K2,4 complement contains exactly193 pairs, partitioned into100 two-private-edge, '
        '60 one-private-edge, nine full-leaf and24 two-leaf cases, each with its bound human proof.\n\n'
        'The earlier pending peer audit supplies the independently reviewed global '
        'partition, lower-endpoint transfers, C4/C5 graph extensions, standalone '
        'subcubic P/R argument, C7 full contact replay, C8 spare-two and sparse proof, '
        'and the C9 complete deletion chain and five-hole proof. Their reviewed byte '
        'bindings remain unchanged. The new complete common-six gate closes its only '
        'remaining premise. All40 unordered endpoint lanes now pass.\n\n'
        'This is a computer-assisted proof record for finite simple graphs '
        'of maximum degree at most ten. It asserts no publication priority '
        'and records no external referee review.\n'
    )
    bind(final_note.name)
    snapshot = WORK / 'tuza_degree10_global_completion_peer_pending_snapshot.json'
    if snapshot.exists():
        assert snapshot.read_bytes() == pending_bytes
    else:
        snapshot.write_bytes(pending_bytes)
    final_lanes = []
    for row in peer['endpoint_lane_table']:
        updated = dict(row)
        if updated['maximum_codegree'] == 6 and updated['status'].startswith('PENDING'):
            updated['status'] = 'PASS complete ambient-ten graph scope'
            updated['binding_source'] = 'work/tuza_degree10_c6_complete_coverage_verified.json'
        final_lanes.append(updated)
    assert len(final_lanes) == 40 and all(r['status'].startswith('PASS') for r in final_lanes)
    peer.update({
        'status': 'PASS_COMPLETE_MAXIMUM_DEGREE_TEN_PEER_SCOPE_AND_BINDINGS',
        'claims_full_maximum_degree_ten_theorem': True,
        'completed_endpoint_lanes': 40,
        'pending_endpoint_lanes': 0,
        'endpoint_lane_table': final_lanes,
        'source_bindings': bindings,
        'common6_final_gate': {
            'result': 'PASS', 'required_domain_rows': 780,
            'complete_report': 'work/tuza_degree10_c6_complete_coverage_verified.json',
            'complete_report_sha256': digest(report_bytes),
            'final_payload': 'work/' + source_name,
            'final_payload_sha256': digest(source_bytes),
            'candidate_pairs': report['candidate_pairs'],
            'fresh_side_domains': 624,
            'fresh_WKE_intervals': 175058,
            'human_graph_tails': [['E?Bo', '10/10'], ['E?Bw', '10/10'], ['E?~o', '9/9']],
            'historical_diagnostics_are_resolved_K24_only': True,
        },
        'prior_pending_audit_sha256': digest(pending_bytes),
        'final_peer_checker_sha256': digest(Path(__file__).read_bytes()),
        'external_peer_review': False,
        'priority_claim': False,
    })
    peer['required_remaining_gate'] = {
        'status': 'SATISFIED_BY_EXPLICIT_FINAL_SOURCE_AND_COMPLETE780_REPLAY',
        'automatically_promote_when_file_exists': False,
    }
    target = WORK / 'tuza_degree10_global_completion_peer_audit.json'
    temporary = target.with_suffix('.pending')
    temporary.write_text(json.dumps(peer, indent=2))
    temporary.replace(target)
    print(json.dumps({'status': peer['status'], 'required_lanes': 40,
                      'complete_lanes': 40, 'c6_domains': 780,
                      'peer_report_sha256': digest(target.read_bytes())}, indent=2))


if __name__ == '__main__':
    main()
