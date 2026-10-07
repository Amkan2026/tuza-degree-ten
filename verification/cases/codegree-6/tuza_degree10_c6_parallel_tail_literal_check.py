                                                                             
from pathlib import Path
import copy
import hashlib
import json
from tuza_degree10_c6_literal_prefix_check import check_pair

WORK = Path(__file__).resolve().parent
source = WORK / 'tuza_degree10_c6_parallel_tail_certificates.json'
source_bytes = source.read_bytes()
data = json.loads(source_bytes)
metadata_path = WORK / 'tuza_degree10_c6_parallel_tail_metadata.json'
metadata_bytes = metadata_path.read_bytes()
metadata = json.loads(metadata_bytes)
domain_path = WORK / 'tuza_degree10_c6_domain.json'
domain_bytes = domain_path.read_bytes()
domain = {r['g6']: r['H'] for r in json.loads(domain_bytes)['records']}
selected = set(metadata['selected_common_graphs'])
new = data['records'][metadata['seed_record_count']:]
assert len(new) == 82
literal_records = []
for record in new:
    assert record['g6'] in selected
    assert record['status'] == 'PASS' and record['kind'] == 'pair'
    sa, sb = [int(v) - 7 for v in record['lane'].split('/')]
    intervals = check_pair(record, domain[record['g6']], sa, sb)
    literal_records.append({'g6': record['g6'], 'lane': record['lane'],
                            'p': record['p'], 'q': record['q'],
                            'packing_size': len(record['S']),
                            'cover_size': len(record['X']),
                            'intervals': intervals})
controls = []
original = new[0]
sa, sb = [int(v) - 7 for v in original['lane'].split('/')]
for name in ['duplicate_triangle', 'empty_cover']:
    bad = copy.deepcopy(original)
    if name == 'duplicate_triangle':
        bad['S'].append(bad['S'][0])
    else:
        bad['X'] = []
    try:
        check_pair(bad, domain[bad['g6']], sa, sb)
    except AssertionError:
        controls.append({'mutation': name, 'rejected': True})
    else:
        raise AssertionError(name)
report = {
    'result': 'PASS',
    'scope': 'The 82 new literal tail pair certificates and their universal contact intervals. Final complete 780-lane coverage is a separate gate.',
    'new_literal_pair_certificates': len(new),
    'optimizer_used': False,
    'bindings': {
        'source': hashlib.sha256(source_bytes).hexdigest(),
        'metadata': hashlib.sha256(metadata_bytes).hexdigest(),
        'domain': hashlib.sha256(domain_bytes).hexdigest(),
        'literal_helper': hashlib.sha256((WORK / 'tuza_degree10_c6_literal_prefix_check.py').read_bytes()).hexdigest(),
        'checker': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    },
    'negative_controls': controls,
    'records': literal_records,
}
target = WORK / 'tuza_degree10_c6_parallel_tail_literal_verified.json'
target.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'records'}), flush=True)
