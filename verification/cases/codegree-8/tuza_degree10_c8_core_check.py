                                                                               
from itertools import combinations
from pathlib import Path
import subprocess,json,hashlib
P=Path('work/tuza_degree10_common8_slack2_probe.json');D=json.loads(P.read_text());keys=[r['g6']for r in D['records']];fresh=set(subprocess.check_output(['/opt/homebrew/bin/geng','-q','8'],text=True).splitlines());assert len(keys)==len(set(keys))==12346 and set(keys)==fresh

def decode(g6):
 bits=''.join(format(ord(x)-63,'06b')for x in g6[1:]);E=set();i=0
 for b in range(1,8):
  for a in range(b):
   if bits[i]=='1':E.add((a,b))
   i+=1
 return E

def verify(r):
 H=decode(r['g6']);E=H|{(c,h)for c in range(8)for h in(8,9)}|{(8,9)};X=set(map(tuple,r['X']));assert len(X)==len(r['X'])and X<=E
 used=[]
 for edges in r['triangles']:
  es=set(map(tuple,edges));v=set(x for e in es for x in e);assert len(v)==3 and es==set(combinations(sorted(v),2));assert es<=E
  assert all(e in X for e in es if not(set(e)&{8,9}));used+=list(es)
 assert len(used)==len(set(used))and len(X)+2<=2*len(r['triangles'])
 for t in combinations(range(10),3):
  es=set(combinations(t,2))
  if set(t)&{8,9}and es<=E:assert es&X
positive=[r for r in D['records']if r['status']=='PASS'];bad=[r for r in D['records']if r['status']!='PASS'];assert len(positive)==12116 and len(bad)==230
for r in positive:verify(r)
assert {r['g6']for r in bad}=={r['g6']for r in D['failures']}
corrupt=json.loads(json.dumps(positive[0]));corrupt['triangles'].append(corrupt['triangles'][0])
try:verify(corrupt)
except AssertionError:pass
else:raise AssertionError('duplicate accepted')
out={'full_core_types':12346,'unconditional_spare_two_certificates':12116,'residual_core_types':230,'negative_controls':1,'payload_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'result':'PASS'};Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
