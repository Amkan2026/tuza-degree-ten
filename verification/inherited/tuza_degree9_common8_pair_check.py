import json,itertools,subprocess,hashlib,time
from pathlib import Path
SRC=Path('work/tuza_degree9_common8_pair_probe.json'); GENG='/opt/homebrew/bin/geng'
def readgraph(g):
 n=ord(g[0])-63; vals=[ord(c)-63 for c in g[1:]]; edges=set();bit=0
 for j in range(1,n):
  for i in range(j):
   if vals[bit//6]&(1<<(5-bit%6)):edges.add((i,j))
   bit+=1
 return n,edges

def valid(row):
 n,H=readgraph(row['g6']);assert n==8
 if row['status']=='SPARSE':
  assert any(all(sum(w in e for e in H if z not in e)<=2 for w in range(8)if w!=z)for z in range(8));return
 assert row['status']=='PASS'
 E=H|{(i,8)for i in range(8)}|{(i,9)for i in range(8)}|{(8,9)}
 X={tuple(e)for e in row['X']};assert len(X)==len(row['X']);assert X<=E
 packed=set();s=0
 for triple in row['triangles']:
  ee={tuple(e)for e in triple};verts=set(v for e in ee for v in e)
  assert len(ee)==3 and len(verts)==3 and ee==set(itertools.combinations(sorted(verts),2))
  assert ee<=E and not ee&packed
  assert all(e in X for e in ee if 8 not in e and 9 not in e)
  packed.update(ee);s+=1
 assert len(X)<=2*s
 for t in itertools.combinations(range(10),3):
  if not({8,9}&set(t)):continue
  ee=set(itertools.combinations(t,2))
  assert not ee<=E or bool(ee&X)

def run(rows):
 keys=[r['g6']for r in rows];assert len(set(keys))==len(keys)==12346
 fresh=set(subprocess.check_output([GENG,'-q','8'],text=True).splitlines());assert set(keys)==fresh
 for r in rows:valid(r)

start=time.time();obj=json.loads(SRC.read_text());assert obj['count']==12346 and not obj['failures'];run(obj['records'])
first=next(r for r in obj['records']if r['status']=='PASS')
neg=0
r=json.loads(json.dumps(first));r['X']=[]
try:valid(r)
except AssertionError:neg+=1
r=json.loads(json.dumps(first));r['triangles'][0]=[(8,9),(0,8),(1,9)]
try:valid(r)
except AssertionError:neg+=1
try:run(obj['records'][:-1])
except AssertionError:neg+=1
assert neg==3
out={'status':'PASS','common_order':8,'core_types':12346,'sparse_human':sum(r['status']=='SPARSE'for r in obj['records']),'literal_certificates':sum(r['status']=='PASS'for r in obj['records']),'negative_controls':neg,'payload_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'seconds':time.time()-start}
Path('work/tuza_degree9_common8_pair_verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
