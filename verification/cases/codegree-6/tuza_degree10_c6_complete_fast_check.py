                                                                          

                                                                      
                                                                       
                                                                           
   
import argparse
import hashlib
import json
import sys
from pathlib import Path

import tuza_degree10_c6_complete_coverage_check as verifier
from tuza_degree10_c6_dense_uncovered import Uncovered

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', default='tuza_degree10_c6_packed_certificates.json')
    p.add_argument('--report', default='tuza_degree10_c6_complete_coverage_verified.json')
    a = p.parse_args()
    relation_path = ROOT / 'tuza_degree10_c6_dense_uncovered_verified.json'
    relation = json.loads(relation_path.read_bytes())
    assert relation['result'] == 'PASS' and relation['literal_relation_checks'] == 2800
    assert relation['source_sha256'] == digest(ROOT / 'tuza_degree10_c6_dense_uncovered.py')
    assert relation['fallback_source_sha256'] == digest(ROOT / 'tuza_degree10_c6_coverage_prefix_check.py')
    fresh_path = ROOT / 'tuza_degree10_c6_fresh_source_verified.json'
    fresh = json.loads(fresh_path.read_bytes())
    assert fresh['result'] == 'PASS_FRESH_COMPLETE_RAW_AND_DENSITY_REPLAY'
    assert fresh['complete_side_domains'] == 624 and fresh['common_graph_types'] == 156
    assert fresh['all_literal_interval_digests_reproduced']
    for name, row in fresh['bindings'].items():
        if name in ('raw_review.dylib', 'density_review.dylib'):
            continue
        path = ROOT / ('tuza_degree10_c6_fresh_source_replay.py' if name == 'fresh_replay_source' else name)
        assert row['sha256'] == digest(path), name
    inner = 'tuza_degree10_c6_fast_inner_verified.json'
    sys.argv = [sys.argv[0], '--source', a.source, '--report', inner]
    verifier.Uncovered = Uncovered
    verifier.main()
    report = json.loads((ROOT / inner).read_bytes())
    assert report['result'] == 'PASS' and report['closed_lanes_replayed'] == 780
    assert report['density_verification_sha256'] == fresh['bindings']['tuza_degree10_c6_density_verified.json']['sha256']
    assert report['raw_domain_verification_sha256'] == fresh['bindings']['tuza_degree10_c6_domain_independent_verified.json']['sha256']
    assert report['domain_sha256'] == fresh['bindings']['tuza_degree10_c6_density_domain.json']['sha256']
    report['rectangle_representation'] = 'direct bit matrix below5billion pairs, original compressed relation otherwise'
    report['certificate_source_file'] = a.source
    report['optimized_wrapper_source_sha256'] = digest(Path(__file__))
    report['optimized_relation_source_sha256'] = relation['source_sha256']
    report['literal_relation_verification_sha256'] = digest(relation_path)
    report['fresh_side_source_verification_sha256'] = digest(fresh_path)
    report['fresh_side_domains_replayed'] = 624
    report['fresh_boolean_patterns_replayed'] = fresh['all_boolean_patterns']
    report['fresh_literal_WKE_intervals_replayed'] = fresh['fresh_literal_WKE_intervals']
    target = ROOT / a.report
    temporary = target.with_suffix('.pending')
    temporary.write_text(json.dumps(report, indent=2))
    temporary.replace(target)
    print('BOUND COMPLETE PASS', report['closed_lanes_replayed'], report['candidate_pairs'], flush=True)


if __name__ == '__main__':
    main()
