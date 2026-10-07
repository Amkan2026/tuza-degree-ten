                                                                        

                                                                          
                                                                         
                                                                          
   
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = ['tuza_degree10_c6_packed_checkpoint.json',
           'tuza_degree10_c6_packed_checkpoint_parallel_middle.json',
           'tuza_degree10_c6_parallel_tail_checkpoint.json',
           'tuza_degree10_c6_parallel_finish_checkpoint.json']
LANES = ['7/10', '8/10', '9/10', '10/10', '9/9']


def digest(body):
    return hashlib.sha256(body).hexdigest()


def main():
    domain = json.loads((ROOT / 'tuza_degree10_c6_density_domain.json').read_bytes())['records']
    expected = {(r['g6'], lane) for r in domain for lane in LANES}
    assert len(expected) == 780
    closed = {}
    records, failures, supplements = [], [], []
    seen_records, seen_failures, seen_supplements = set(), set(), set()
    provenance = {}
    for name in SOURCES:
        path = ROOT / name
        if not path.exists():
            continue
        body = path.read_bytes()
        data = json.loads(body)
        provenance[name] = {'bytes': len(body), 'sha256': digest(body)}
        for rec in data['reports']:
            key = (rec['g6'], rec['lane'])
            assert key in expected
            if rec['residual'] == 0:
                closed.setdefault(key, {**rec, 'merged_from': name})
            elif key == ('E?~o', '9/9'):
                assert rec['residual'] == 193
                closed.setdefault(key, {**rec, 'merged_from': name})
        for key, rows, seen in [('records', records, seen_records), ('failures', failures, seen_failures),
                                ('independently_verified_supplements', supplements, seen_supplements)]:
            for row in data.get(key, []):
                marker = json.dumps(row, sort_keys=True, separators=(',', ':'))
                if marker not in seen:
                    seen.add(marker)
                    rows.append(row)
    binding_path = ROOT / 'tuza_degree10_c6_K24_human_complete_verified.json'
    binding = json.loads(binding_path.read_bytes())
    assert binding['result'] == 'PASS' and binding['complete_graph_scope']
    assert binding['entire_residual_has_human_proofs']
    missing = sorted(expected - set(closed))
    progress = {'status': 'READY_FOR_FULL780_REPLAY' if not missing else 'PENDING',
                'closed_domain_rows': len(closed), 'required_domain_rows': 780,
                'missing_domain_rows': missing, 'literal_certificates': len(records),
                'source_snapshots': provenance, 'historical_diagnostics': len(failures),
                'complete_theorem_claimed': False,
                'merger_source_sha256': digest(Path(__file__).read_bytes())}
    (ROOT / 'tuza_degree10_c6_parallel_merge_progress.json').write_text(json.dumps(progress, indent=2))
    print(json.dumps({k: v for k, v in progress.items() if k not in ('missing_domain_rows', 'source_snapshots')}), flush=True)
    if missing:
        return
    assert all((r['g6'], r['lane']) == ('E?~o', '9/9') and r['status'] == 'UNKNOWN'
               and r['p'] == r['q'] == 1023 for r in failures)
    frozen = ROOT / 'tuza_degree10_c6_parallel_snapshot_inputs'
    frozen.mkdir(exist_ok=True)
    for name, row in provenance.items():
        body = (ROOT / name).read_bytes()
        assert digest(body) == row['sha256'], 'A producer snapshot changed while merging. Retry from a stable checkpoint.'
        (frozen / name).write_bytes(body)
    out = {'records': records, 'reports': [closed[key] for key in sorted(expected)],
           'failures': failures, 'independently_verified_supplements': supplements,
           'complete_discovery': True, 'human_proof_review_required': True,
           'parallel_merge_provenance': provenance,
           'parallel_merge_source_sha256': progress['merger_source_sha256'],
           'K24_human_completion_sha256': digest(binding_path.read_bytes()),
           'independent_full_coverage_required': True}
    target = ROOT / 'tuza_degree10_c6_merged_certificates.json'
    temporary = target.with_suffix('.pending')
    temporary.write_text(json.dumps(out))
    temporary.replace(target)
    print('MERGED780 ready for independent complete replay', flush=True)


if __name__ == '__main__':
    main()
