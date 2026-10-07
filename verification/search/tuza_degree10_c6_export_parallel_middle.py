                                                                                 
import hashlib
import json
from pathlib import Path

W = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    metadata_path = W/'tuza_degree10_c6_parallel_middle_metadata.json'
    metadata_bytes = metadata_path.read_bytes()
    metadata = json.loads(metadata_bytes)
    source = W/'tuza_degree10_c6_packed_certificates_parallel_middle.json'
    original_bytes = source.read_bytes()
    data = json.loads(original_bytes)
    assert sha(Path(metadata['worker_source']).read_bytes()) == metadata['worker_source_sha256']
    assert sha(Path(metadata['original_source']).read_bytes()) == metadata['original_source_sha256']
    allowed = set(metadata['allowed_common_graph6'])
    records = data['records'][metadata['seed_record_count']:]
    failures = data['failures'][metadata['seed_failure_count']:]
    assert all(r['g6'] in allowed for r in records+failures)
    reports = [r for r in data['reports'] if r['g6'] in allowed]
    keys = {(r['g6'],r['lane']) for r in reports}
    assert keys == {tuple(k) for k in metadata['required_worker_lanes']}
    assert len(reports) == len(keys) == 20
    assert all((r['g6'],r['lane']) in keys and r['status']=='PASS'
               and r['kind'] in ['pair','subset_cut'] for r in records)
    snapshot = {
        'scope':'Four-common-core positive discovery worker only; full780 independent replay remains required',
        'allowed_common_graph6':metadata['allowed_common_graph6'],
        'complete_full_discovery_claimed':False,
        'worker_global_complete_discovery':data['complete_discovery'],
        'all_assigned_lanes_closed_in_discovery':all(r['residual']==0 for r in reports),
        'independent_verification_claimed':False,
        'records':records,'reports':reports,'new_failures':failures,
        'new_certificate_count':len(records),'new_failure_count':len(failures),
        'seed_record_count':metadata['seed_record_count'],
        'seed_checkpoint_sha256':metadata['seed_checkpoint_sha256'],
        'worker_output':str(source),'worker_output_sha256':sha(original_bytes),
        'metadata_sha256':sha(metadata_bytes),
        'original_source_sha256':metadata['original_source_sha256'],
        'worker_source_sha256':metadata['worker_source_sha256'],
        'export_source_sha256':sha(Path(__file__).read_bytes()),
    }
    target = W/'tuza_degree10_c6_parallel_middle_newcerts_snapshot.json'
    pending = target.with_suffix('.tmp')
    pending.write_text(json.dumps(snapshot,indent=2)+'\n');pending.replace(target)
    print(json.dumps({'assigned_lanes':len(reports),
                      'all_closed_discovery':snapshot['all_assigned_lanes_closed_in_discovery'],
                      'new_certificates':len(records),'new_failures':len(failures),
                      'snapshot_sha256':sha(target.read_bytes())}),flush=True)


if __name__ == '__main__':
    main()
