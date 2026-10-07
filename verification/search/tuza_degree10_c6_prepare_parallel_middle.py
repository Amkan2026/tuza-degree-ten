                                                                              
import datetime
import hashlib
import json
from pathlib import Path

W = Path(__file__).resolve().parent
KEYS = ['E]zo','E]zg','E]yw','E]zw']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    original = W/'tuza_degree10_c6_packed_rectangles.py'
    original_bytes = original.read_bytes()
    code = original_bytes.decode()
    replacements = {
        "dom=json.loads(Path('work/tuza_degree10_c6_domain.json').read_text())['records']":
        "dom=[r for r in json.loads(Path('work/tuza_degree10_c6_domain.json').read_text())['records'] if r['g6'] in ['E]zo','E]zg','E]yw','E]zw']]",
        "checkpoint=Path('work/tuza_degree10_c6_packed_checkpoint.json')":
        "checkpoint=Path('work/tuza_degree10_c6_packed_checkpoint_parallel_middle.json')",
        "target=Path('work/tuza_degree10_c6_packed_certificates.json')":
        "target=Path('work/tuza_degree10_c6_packed_certificates_parallel_middle.json')",
    }
    for before,after in replacements.items():
        assert code.count(before) == 1
        code = code.replace(before,after)
    reconstructed = code
    for before,after in replacements.items():
        assert reconstructed.count(after) == 1
        reconstructed = reconstructed.replace(after,before)
    assert reconstructed.encode() == original_bytes
    worker = W/'tuza_degree10_c6_parallel_middle.py'
    assert not worker.exists()
    worker.write_text(code)
    checkpoint = W/'tuza_degree10_c6_packed_checkpoint.json'
    seed_bytes = checkpoint.read_bytes()
    seed = json.loads(seed_bytes)
    worker_checkpoint = W/'tuza_degree10_c6_packed_checkpoint_parallel_middle.json'
    assert not worker_checkpoint.exists()
    pending = worker_checkpoint.with_suffix('.tmp')
    pending.write_bytes(seed_bytes);pending.replace(worker_checkpoint)
    assert worker_checkpoint.read_bytes() == seed_bytes
    done = {(r['g6'],r['lane']) for r in seed['reports'] if r['residual']==0}
    required = [(h,f'{7+a}/{7+b}') for h in KEYS for a,b in [(0,3),(1,3),(2,3),(3,3),(2,2)]]
    metadata = {
        'purpose':'Partial positive discovery worker; original main producer and checkpoint untouched',
        'initialized_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'allowed_common_graph6':KEYS,
        'full_discovery_claim_intended':False,
        'full780_independent_replay_still_required':True,
        'original_source':str(original),'original_source_sha256':digest(original_bytes),
        'worker_source':str(worker),'worker_source_sha256':digest(worker.read_bytes()),
        'exact_changes':'common-domain filter and two output/checkpoint path literals only',
        'original_checkpoint':str(checkpoint),'seed_checkpoint_sha256':digest(seed_bytes),
        'seed_checkpoint_bytes':len(seed_bytes),
        'worker_checkpoint':str(worker_checkpoint),
        'seed_record_count':len(seed['records']),
        'seed_report_count':len(seed['reports']),
        'seed_failure_count':len(seed['failures']),
        'required_worker_lanes':required,
        'worker_lanes_pending_at_seed':[k for k in required if k not in done],
        'seed_worker_reports':[r for r in seed['reports'] if r['g6'] in KEYS],
        'preparation_source_sha256':digest(Path(__file__).read_bytes()),
    }
    path = W/'tuza_degree10_c6_parallel_middle_metadata.json'
    path.write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps({'worker_source_sha256':metadata['worker_source_sha256'],
                      'original_source_sha256':metadata['original_source_sha256'],
                      'seed_sha256':metadata['seed_checkpoint_sha256'],
                      'seed_records':metadata['seed_record_count'],
                      'pending_lanes':len(metadata['worker_lanes_pending_at_seed'])}),flush=True)


if __name__ == '__main__':
    main()
