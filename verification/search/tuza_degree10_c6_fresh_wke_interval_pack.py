                                                                        
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import zipfile

WORK = Path(__file__).resolve().parent
proof_path = WORK / 'tuza_degree10_c6_fresh_source_verified.json'
proof_bytes = proof_path.read_bytes()
proof = json.loads(proof_bytes)
assert proof['result'] == 'PASS_FRESH_COMPLETE_RAW_AND_DENSITY_REPLAY'
domain_bytes = (WORK / 'tuza_degree10_c6_domain.json').read_bytes()
domain = json.loads(domain_bytes)['records']
by_key = {(r['g6'], r['private_size']): r for r in proof['records']}
assert len(by_key) == 624 and len(domain) == 156


def read_entry(item):
    index, row, private_size = item
    name = f'{index:03d}_{private_size}.txt'
    data = (WORK / 'tuza_degree10_c6_fresh_source_snapshot' / 'intervals' / name).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    expected = by_key[row['g6'], private_size]
    assert digest == expected['fresh_literal_intervals_sha256'], name
    assert len(data.splitlines()) == expected['literal_WKE_intervals'], name
    return name, data, {'g6': row['g6'], 'private_size': private_size,
                        'file': f'intervals/{name}', 'bytes': len(data),
                        'sha256': digest,
                        'literal_intervals': expected['literal_WKE_intervals']}


items = [(i, row, r) for i, row in enumerate(domain) for r in range(4)]
entries = []
with ThreadPoolExecutor(max_workers=8) as pool:
    for i, entry in enumerate(pool.map(read_entry, items)):
        entries.append(entry)
        if i % 50 == 0:
            print('INTERVAL_PACK', i, entry[0], flush=True)
assert sum(e[2]['literal_intervals'] for e in entries) == 175058
manifest = {'result': 'PASS_LITERAL_CORPUS_BINDING',
            'scope': 'Exact freshly regenerated positive interval bytes, not a new domain replay.',
            'fresh_replay_report_sha256': hashlib.sha256(proof_bytes).hexdigest(),
            'domain_sha256': hashlib.sha256(domain_bytes).hexdigest(),
            'packer_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'side_domains': 624, 'literal_intervals': 175058,
            'records': [entry[2] for entry in entries]}
target = WORK / 'tuza_degree10_c6_fresh_wke_intervals.zip'
temp = target.with_suffix('.tmp')
with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for name, data, record in entries:
        archive.writestr(record['file'], data)
    archive.writestr('manifest.json', json.dumps(manifest, indent=2) + '\n')
temp.replace(target)
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == 625
report = {'result': 'PASS', 'side_domains': 624, 'literal_intervals': 175058,
          'archive_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
          'archive_bytes': target.stat().st_size,
          'manifest_sha256': hashlib.sha256((json.dumps(manifest, indent=2) + '\n').encode()).hexdigest(),
          'fresh_replay_report_sha256': manifest['fresh_replay_report_sha256'],
          'packer_source_sha256': manifest['packer_source_sha256'],
          'crc_pass': True}
(WORK / 'tuza_degree10_c6_fresh_wke_intervals_verified.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report), flush=True)
