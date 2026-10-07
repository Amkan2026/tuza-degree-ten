                                                                          
import hashlib
import json
import time
import sys
import zipfile
import zlib
from pathlib import Path

import numpy as np
from tuza_degree10_c6_dense_uncovered import Uncovered
from tuza_degree10_c6_coverage_prefix_check import apply_certificate, remove_impossible, symmetries
from tuza_degree10_c6_literal_prefix_check import check_pair, check_cut

ROOT = Path(__file__).resolve().parent
started = time.time()
source = (ROOT / 'tuza_degree10_c6_packed_checkpoint.json').read_bytes()
data = json.loads(source)
domain = json.loads((ROOT / 'tuza_degree10_c6_density_domain.json').read_bytes())['records']
key = sys.argv[1] if len(sys.argv) > 1 else 'E?~o'
row = next(r for r in domain if r['g6'] == key)
report = next(r for r in data['reports'] if r['g6'] == key and r['lane'] == '10/10')
assert report['residual'] == 0
with zipfile.ZipFile(ROOT / 'tuza_degree10_c6_density_patterns_cache.zip') as cache:
    encoded = cache.read(row['sides']['3']['file'])
    P = np.frombuffer(zlib.decompress(encoded), dtype='<u4')
U = Uncovered(len(P), len(P))
H = row['H']
remove_impossible(H, P, P, 3, 3, U)
autos = symmetries(H)
count = 0
for rec in data['records']:
    if rec['g6'] != key or rec['lane'] != '10/10':
        continue
    proof = check_pair(rec, H, 3, 3) if rec['kind'] == 'pair' else check_cut(rec, H, 3, 3)
    apply_certificate(rec, proof, autos, P, P, 3, 3, U)
    count += 1
    if count % 10 == 0:
        print(count, U.count(), round(time.time() - started, 1), flush=True)
    if not U.rows:
        break
assert U.count() == 0
out = {'result':'PASS','g6':key,'lane':'10/10','candidate_pairs':len(P)**2,
       'literal_certificates_replayed':count,'checkpoint_sha256':hashlib.sha256(source).hexdigest(),
       'relation_source_sha256':hashlib.sha256((ROOT/'tuza_degree10_c6_dense_uncovered.py').read_bytes()).hexdigest(),
       'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
       'seconds':time.time()-started,'full780_scope':False}
target = 'tuza_degree10_c6_dense_largest_verified.json' if len(sys.argv) > 1 else 'tuza_degree10_c6_dense_lane_verified.json'
(ROOT/target).write_text(json.dumps(out,indent=2))
print(json.dumps(out),flush=True)
