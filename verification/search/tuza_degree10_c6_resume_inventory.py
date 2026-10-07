                                                                                 
from pathlib import Path
import ast
import hashlib
import json
import time

WORK = Path(__file__).resolve().parent

CATEGORIES = {
    'fresh_raw_and_density_foundation': [
        'tuza_degree10_c6_domain_independent.c',
        'tuza_degree10_c6_domain_independent.py',
        'tuza_degree10_c6_density_check.c',
        'tuza_degree10_c6_density_check.py',
        'tuza_degree10_c6_density.py',
        'tuza_degree10_c6_cached_patterns.py',
        'tuza_degree10_c6_domain.c',
        'tuza_degree10_c6_domain.py',
        'tuza_degree10_c6_domain.json',
        'tuza_degree10_c6_density_domain.json',
        'tuza_degree10_c6_domain_independent_verified.json',
        'tuza_degree10_c6_density_verified.json',
        'tuza_degree10_c6_patterns_cache.zip',
        'tuza_degree10_c6_density_patterns_cache.zip',
        'tuza_degree10_c6_fresh_source_replay.py',
        'tuza_degree10_c6_fresh_source_verified.json',
        'tuza_degree10_c6_source_scope_audit.py',
        'tuza_degree10_c6_source_scope_verified.json',
        'tuza_degree10_c6_source_mathematical_review.txt',
        'tuza_degree10_c6_fresh_wke_interval_pack.py',
        'tuza_degree10_c6_fresh_wke_intervals.zip',
        'tuza_degree10_c6_fresh_wke_intervals_verified.json',
    ],
    'complete_coverage_interface_and_core': [
        'tuza_degree10_c6_complete_fast_check.py',
        'tuza_degree10_c6_complete_coverage_check.py',
        'tuza_degree10_c6_complete_coverage_human_audit.txt',
        'tuza_degree10_c6_coverage_prefix_check.py',
        'tuza_degree10_c6_literal_prefix_check.py',
        'tuza_degree10_c6_dense_uncovered.py',
        'tuza_degree10_c6_dense_uncovered_verified.json',
        'tuza_degree10_c6_dense_uncovered_peer_review.txt',
        'tuza_degree10_c6_dense_uncovered_peer_verified.json',
        'tuza_degree10_c6_core_certificates.json',
        'tuza_degree10_c6_common_orbit_audit.py',
        'tuza_degree10_c6_common_orbit_verified.json',
        'tuza_degree10_c6_common_census_verified.json',
    ],
    'human_star_cases': [
        'tuza_degree10_c6_empty_core_human_proof.txt',
        'tuza_degree10_c6_double_hub_human_proof.txt',
        'tuza_degree10_c6_four_private_human_proof.txt',
        'tuza_degree10_c6_four_private_human_check.c',
        'tuza_degree10_c6_four_private_human_verified.json',
        'tuza_degree10_c6_four_private_glue_check.py',
        'tuza_degree10_c6_four_private_glue_verified.json',
        'tuza_degree10_c6_three_hub_human_proof.txt',
        'tuza_degree10_c6_three_hub_human_check.py',
        'tuza_degree10_c6_three_hub_human_verified.json',
        'tuza_degree10_c6_human_scope_root_bind.py',
        'tuza_degree10_c6_human_scope_root_verified.json',
    ],
    'human_K24_residual': [
        'tuza_degree10_c6_K24_residual_pairs.json',
        'tuza_degree10_c6_K24_human_partition_check.py',
        'tuza_degree10_c6_K24_human_partition_verified.json',
        'tuza_degree10_c6_K24_human_completion_check.py',
        'tuza_degree10_c6_K24_human_complete_verified.json',
        'tuza_degree10_c6_K24_complete_verified.json',
        'tuza_degree10_c6_K24_root_check.py',
        'tuza_degree10_c6_K24_root_verified.json',
        'tuza_degree10_c6_K24_root_partition_verified.json',
        'tuza_degree10_c6_K24_broad_human_peer_audit.txt',
        'tuza_degree10_c6_K24_full_leaf_peer_audit.txt',
    ] + [
        f'tuza_degree10_c6_K24_{stem}_human_{suffix}'
        for stem in ['private_edges', 'one_private_edge', 'full_leaf', 'two_leaf']
        for suffix in ['proof.txt', 'check.py', 'verified.json']
    ],
    'lower_endpoint_transfer_and_replay': [
        'tuza_degree10_c6_lower_endpoint_transfer_audit.txt',
        'tuza_degree10_c6_lower_endpoint_transfer_audit.json',
        'tuza_degree8_codegree6_template_certificates.json',
        'tuza_degree8_codegree6_check.py',
        'tuza_degree8_codegree6_verified.json',
        'tuza_degree8_codegree6_k5_core_analytic.txt',
        'tuza_degree8_mixed_codegree6_certificates.json',
        'tuza_degree8_mixed_codegree6_check.py',
        'tuza_degree8_mixed_codegree6_verified.json',
        'tuza_c6_compressed_contact_templates.json',
        'tuza_c6_compressed_contact_check.py',
        'tuza_c6_compressed_contact_verified.json',
        'tuza_c6_human_compressed_templates.json',
        'tuza_c6_human_compressed_verified.json',
        'tuza_c6_mixed_interval_templates.json',
        'tuza_c6_active_ordinary_interval_templates.json',
        'tuza_c6_mixed_reuse_check.py',
        'tuza_c6_mixed_reuse_verified.json',
        'tuza_degree9_c6_core_spare_certificates.json',
        'tuza_degree9_c6_monotone_certificates.json',
        'tuza_degree9_c6_full_combined_certificates.json',
        'tuza_degree9_c6_minimal_domain.json',
        'tuza_degree9_c6_side_classification_full_intervals.json',
        'tuza_degree9_c6_check.py',
        'tuza_degree9_c6_verified.json',
    ],
    'resume_discovery_sources': [
        'tuza_degree10_c6_packed_rectangles.py',
        'tuza_degree10_c6_full_rectangles.py',
        'tuza_degree10_c6_solve.py',
        'tuza_degree10_c6_pair_wide.py',
        'tuza_degree10_c6_parallel_tail.py',
        'tuza_degree10_c6_parallel_tail_metadata.json',
        'tuza_degree10_c6_parallel_finish.py',
        'tuza_degree10_c6_parallel_finish_metadata.json',
    ],
    'mutable_resume_state': [
        'tuza_degree10_c6_pre_packed_snapshot.json',
        'tuza_degree10_c6_monotone_checkpoint.json',
        'tuza_degree10_c6_packed_checkpoint.json',
        'tuza_degree10_c6_parallel_tail_checkpoint.json',
        'tuza_degree10_c6_parallel_finish_checkpoint.json',
    ],
    'completed_partial_discovery_payload': [
        'tuza_degree10_c6_parallel_tail_certificates.json',
        'tuza_degree10_c6_parallel_tail_scope_verified.json',
        'tuza_degree10_c6_parallel_tail_literal_check.py',
        'tuza_degree10_c6_parallel_tail_literal_verified.json',
    ],
}

PENDING = [
    {'path': 'tuza_degree10_c6_merged_certificates.json',
     'gate': 'Merged immutable main/middle/tail payload. Require literal and all 780 domain replay.'},
    {'path': 'tuza_degree10_c6_complete_coverage_verified.json',
     'gate': 'Independent full 780-lane coverage PASS with current source and input hash bindings.'},
    {'path': 'tuza_degree10_c6_parallel_tail_certificates.json',
     'gate': 'Partial discovery only. Merge its new records and selected reports, then independently replay.'},
]


def source_dependencies(name):
    path = WORK / name
    if path.suffix != '.py':
        return []
    tree = ast.parse(path.read_text())
    result = set()
    for node in ast.walk(tree):
        modules = []
        if isinstance(node, ast.Import):
            modules = [item.name for item in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules = [node.module]
        for module in modules:
            if module.startswith('tuza_') and (WORK / f'{module}.py').is_file():
                result.add(f'{module}.py')
    return sorted(result)


def main():
    started = time.time()
    categories = {key: list(value) for key, value in CATEGORIES.items()}
                                                                                
                                                                                 
    all_names = set(name for names in categories.values() for name in names)
    queue = list(sorted(all_names))
    dependencies = {}
    while queue:
        name = queue.pop()
        if not (WORK / name).is_file():
            continue
        imports = source_dependencies(name)
        if imports:
            dependencies[name] = imports
        for item in imports:
            if item not in all_names:
                all_names.add(item)
                queue.append(item)
                categories.setdefault('local_import_dependencies', []).append(item)
    records, missing = [], []
    for i, name in enumerate(sorted(all_names)):
        path = WORK / name
        if not path.is_file():
            missing.append(name)
            continue
        data = path.read_bytes()
        records.append({'path': f'work/{name}', 'bytes': len(data),
                        'sha256': hashlib.sha256(data).hexdigest(),
                        'categories': [key for key, names in categories.items() if name in names],
                        'mutable': name in categories['mutable_resume_state']})
        if i % 10 == 0:
            print('INVENTORY', i, name, flush=True)
    foundation = json.loads((WORK / 'tuza_degree10_c6_fresh_source_verified.json').read_text())
    assert foundation['result'] == 'PASS_FRESH_COMPLETE_RAW_AND_DENSITY_REPLAY'
    assert foundation['complete_side_domains'] == 624
    assert foundation['common_graph_types'] == 156
    assert foundation['fresh_literal_WKE_intervals'] == 175058
    report = {
        'result': 'PASS_SELECTIVE_INVENTORY' if not missing else 'INVENTORY_WITH_MISSING_INPUTS',
        'scope': 'C6 input and resume inventory. This is not a declaration of full Delta ten completion.',
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'categories': categories, 'files': records, 'missing': missing,
        'pending_final_inputs': PENDING, 'local_import_dependencies': dependencies,
        'verified_foundation': {key: foundation[key] for key in [
            'complete_side_domains', 'common_graph_types', 'all_boolean_patterns',
            'legal_connected_patterns', 'retained_candidate_patterns',
            'excluded_positive_WKE_patterns', 'fresh_literal_WKE_intervals',
            'all_literal_interval_digests_reproduced', 'selected_canonical_patterns',
            'excluded_raw_by_density']},
        'lower_endpoint_scope': ['7/7', '7/8', '7/9', '8/8', '8/9'],
        'new_complete_lane_scope': ['7/10', '8/10', '9/10', '10/10', '9/9'],
        'excluded_material': [
            'individual uncompressed pattern arrays', 'compiled libraries and bytecode',
            'solver experiments not needed by the selected producer',
            'old alternative discovery checkpoints', 'unrelated graph classes and manuscripts'],
        'generated_literal_intervals': {
            'path': 'work/tuza_degree10_c6_fresh_source_snapshot/intervals',
            'compact_archive': 'work/tuza_degree10_c6_fresh_wke_intervals.zip',
            'files': 624, 'literal_intervals': 175058,
            'status': 'The compact ZIP binds all 624 regenerated positive witness files, exact per-file interval counts and SHA256 values. The replay can also regenerate these files from the selected C source.'},
        'runtime_dependencies': {
            'replay': ['Python 3', 'numpy', 'C compiler', 'geng'],
            'discovery_only': ['ortools']},
        'mutation_note': 'Mutable checkpoints are byte snapshots at inventory time. Their digests must be refreshed when freezing final resume state.',
        'seconds': time.time() - started,
    }
    target = WORK / 'tuza_degree10_c6_resume_inventory.json'
    tmp = target.with_suffix('.tmp')
    tmp.write_text(json.dumps(report, indent=2) + '\n')
    tmp.replace(target)
    print(json.dumps({'result': report['result'], 'files': len(records),
                      'missing': missing, 'total_bytes': sum(r['bytes'] for r in records),
                      'inventory_sha256': hashlib.sha256(target.read_bytes()).hexdigest()}), flush=True)


if __name__ == '__main__':
    main()
