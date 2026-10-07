from pathlib import Path
from itertools import combinations,permutations
import sys,json,hashlib,copy
import numpy as np
sys.path.insert(0,str(Path(__file__).parent));import tuza_degree9_c5_independent_check as f
                                                                         
source=Path(__file__).with_name('tuza_degree9_c5_old_interval_compress.json');payload=source.read_bytes();p=json.loads(payload)
assert {x['core']for x in p['cores']}==set(f.SIDES[8]);reports=[]
for row in p['cores']:
 h=row['core'];L,R,U=f.admitted(h,8,8);count=int(U.sum());assert count==row['admitted_pairs'];H={e for i,e in enumerate(f.CE)if h>>i&1};auts=[q for q in permutations(range(5))if{tuple(sorted((q[a],q[b])))for a,b in H}==H]
 for rec in row['intervals']:
  RF=f.derive(rec)
  for cp in auts:
   a=f.hit(8,L,RF[0],cp);b=f.hit(8,R,RF[1],cp);U[np.ix_(a,b)]=False;U[np.ix_(b,a)]=False
 remaining=[(int(L[i]),int(R[j]))for i,j in np.argwhere(U)]
 assert not remaining and row['special_human_cases']==0
 reports.append({'core':h,'admitted_pairs':count,'intervals':len(row['intervals']),'human_cases':len(remaining),'result':'PASS'})
rec=next(r for row in p['cores']for r in row['intervals']);negative=[]
for name,mutation in [('duplicate triangle',lambda r:r['packing'].append(r['packing'][0])),('empty cover',lambda r:r.__setitem__('cover',[])),('wrong required mask',lambda r:r['side_intervals'][0].__setitem__(0,r['side_intervals'][0][0]^1))]:
 q=copy.deepcopy(rec);mutation(q)
 try:f.derive(q)
 except(AssertionError,ValueError,KeyError):negative.append(name)
 else:raise AssertionError(name)
out={'complete_graph_lane':True,'literal_intervals':sum(r['intervals']for r in reports),'canonical_side_pairs_verified':sum(r['admitted_pairs']for r in reports),'human_dense_cases':sum(r['human_cases']for r in reports),'common_cores':len(reports),'reports':reports,'negative_controls_rejected':negative,'source_sha256':hashlib.sha256(payload).hexdigest(),'result':'PASS'};Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items()if k!='reports'},indent=2),flush=True)
