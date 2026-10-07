import itertools,json,subprocess,time,hashlib
from pathlib import Path
from functools import lru_cache
GENG='/opt/homebrew/bin/geng'
def decode(s):
 n=ord(s[0])-63;bits=''.join(format(ord(c)-63,'06b')for c in s[1:]);i=0;E=set()
 for j in range(1,n):
  for k in range(j):
   if bits[i]=='1':E.add((k,j))
   i+=1
 return n,E

def iwke(n,E):
 A=[set()for _ in range(n)]
 for a,b in E:A[a].add(b);A[b].add(a)
 @lru_cache(None)
 def maximum(W):
  if not W:return 0
  a=W[0];z=maximum(W[1:]);Ws=set(W)
  for b in A[a]&Ws:z=max(z,1+maximum(tuple(x for x in W if x not in[a,b])))
  return z
 for k in range(n//2+1):
  for q in itertools.combinations(range(n),k):
   Q=set(q);F=[e for e in E if not set(e)&Q];flat=[x for e in F for x in e]
   if len(set(flat))!=len(flat):continue
   rem=tuple(x for x in range(n)if x not in flat)
   if len(F)+maximum(rem)>=k:return True
 return False

def literal(row,spare=0):
 n,H=decode(row['g6']);assert n==7
 u,v=7,8;da=row.get('da',0);db=row.get('db',0)
 E=H|{(i,u)for i in range(7)}|{(i,v)for i in range(7)}|{(u,v)}
 if da:E.add((u,9));E|={(i,9)for i in range(7)if da>>i&1}
 if db:E.add((v,10));E|={(i,10)for i in range(7)if db>>i&1}
 X={tuple(e)for e in row['X']};assert len(X)==len(row['X'])and X<=E
 packed=set();S=[]
 if'triangles'in row:
  for te in row['triangles']:
   ee={tuple(e)for e in te};vs={x for e in ee for x in e};assert len(vs)==3
   S.append(tuple(sorted(vs)));assert ee==set(itertools.combinations(sorted(vs),2))
 else:S=[tuple(t)for t in row['S']]
 for t in S:
  ee=set(itertools.combinations(t,2));assert len(ee)==3 and ee<=E and not ee&packed
  assert all(e in X for e in ee if u not in e and v not in e);packed|=ee
 assert len(X)+spare<=2*len(S)
 for t in itertools.combinations(range(11),3):
  if u not in t and v not in t:continue
  ee=set(itertools.combinations(t,2));assert not ee<=E or ee&X

def auts(H):
 deg=[sum(a in e for e in H)for a in range(7)];out=[]
 for p in itertools.permutations(range(7)):
  if any(deg[a]!=deg[p[a]]for a in range(7)):continue
  if {tuple(sorted((p[a],p[b])))for a,b in H}!=H:continue
  out.append([sum(1<<p[i]for i in range(7)if m>>i&1)for m in range(128)])
 return out

start=time.time();P=Path('work/tuza_degree9_common7_slack2_probe.json');R=Path('work/tuza_degree9_c7_residual_certificates.json');core=json.loads(P.read_text());res=json.loads(R.read_text());assert res['count']==1563 and not res['failures'];fresh=set(subprocess.check_output([GENG,'-q','7'],text=True).splitlines());assert len(fresh)==1044;assert{r['g6']for r in core['records']}==fresh
covered=set();resby={}
for r in core['records']:
 if r['status']=='PASS':literal(r,2);covered.add(r['g6'])
for r in res['records']:literal(r);resby.setdefault(r['g6'],[]).append(r)
assert len(covered)==1027
labelled_pair_count=0;mixed_count=0;excluded=0
for key in sorted(fresh-covered):
 _,H=decode(key);degree=[sum(a in e for e in H)for a in range(7)]
 Ds=[]
 for D in range(1,128):
  if any(D>>a&1 and degree[a]>=6 for a in range(7)):continue
  L=H|{(a,7)for a in range(7)}|{(a,8)for a in range(7)if D>>a&1}
  if not iwke(9,L):Ds.append(D)
 allowed=set()
 for a in Ds:
  for b in Ds:
   if a>b:continue
   ok=True
   for x,y in H:
    common=sum(tuple(sorted((x,z)))in H and tuple(sorted((y,z)))in H for z in range(7)if z not in[x,y])
    if 2+common+int((a>>x&1)and(a>>y&1))+int((b>>x&1)and(b>>y&1))>7:ok=False;break
   if ok:allowed.add((a,b))
 mixed=set()
 if not iwke(8,H|{(a,7)for a in range(7)}):mixed={(0,d)for d in Ds}
 maps=auts(H);actual=set()
 for r in resby.get(key,[]):
  for mp in maps:
   a,b=mp[r['da']],mp[r['db']]
   actual.add((min(a,b),max(a,b)))
 assert allowed|mixed<=actual,(key,len((allowed|mixed)-actual))
 assert actual<=allowed|mixed
 labelled_pair_count+=len(allowed);mixed_count+=len(mixed)
 if not allowed and not mixed:excluded+=1
print('domains',labelled_pair_count,mixed_count,excluded,flush=True)
                                                            
neg=0
r=json.loads(json.dumps(res['records'][0]));r['X']=[]
try:literal(r)
except AssertionError:neg+=1
r=json.loads(json.dumps(res['records'][0]));r['S'][0]=[7,9,10]
try:literal(r)
except AssertionError:neg+=1
assert neg==2
out={'status':'PASS','core_types':1044,'universal_spare2_core_certificates':1027,'remaining_core_types':17,'excluded_no_side_cores':excluded,'residual_core_types':len(resby),'residual_orbit_certificates':1563,'residual_labelled_unordered_pair_models':labelled_pair_count,'residual_labelled_mixed_models':mixed_count,'negative_controls':neg,'core_payload_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'residual_payload_sha256':hashlib.sha256(R.read_bytes()).hexdigest(),'seconds':time.time()-start}
Path('work/tuza_degree9_c7_verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
