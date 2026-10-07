                                                                          
import itertools,json,subprocess,time,hashlib
from functools import lru_cache
from pathlib import Path
start=time.time();P=Path('work/tuza_degree10_common8_slack2_probe.json');R=Path('work/tuza_degree10_c8_residual_certificates.json')
def decode(s):
 n=ord(s[0])-63;bits=''.join(format(ord(c)-63,'06b')for c in s[1:]);E=set();i=0
 for b in range(1,n):
  for a in range(b):
   if bits[i]=='1':E.add((a,b))
   i+=1
 return n,E
def iwke(n,E):
 N=[set()for _ in range(n)]
 for a,b in E:N[a].add(b);N[b].add(a)
 @lru_cache(None)
 def match(W):
  if not W:return 0
  a=W[0];best=match(W[1:])
  for b in N[a]&set(W):best=max(best,1+match(tuple(v for v in W if v not in(a,b))))
  return best
 for k in range(n//2+1):
  for qq in itertools.combinations(range(n),k):
   Q=set(qq);F=[e for e in E if not(set(e)&Q)];flat=[v for e in F for v in e]
   if len(flat)!=len(set(flat)):continue
   if len(F)+match(tuple(v for v in range(n)if v not in flat))>=k:return True
 return False

def auts(H):
 deg=[sum(v in e for e in H)for v in range(8)];classes=[]
 for d in sorted(set(deg)):classes.append([v for v in range(8)if deg[v]==d])
 maps=[]
 for choice in itertools.product(*(itertools.permutations(c)for c in classes)):
  p=list(range(8))
  for c,perm in zip(classes,choice):
   for a,b in zip(c,perm):p[a]=b
  if {tuple(sorted((p[a],p[b])))for a,b in H}!=H:continue
  maps.append([sum(1<<p[i]for i in range(8)if D>>i&1)for D in range(256)])
 return maps

def literal(r):
 n,H=decode(r['g6']);assert n==8;da,db=r['da'],r['db'];E=H|{(c,h)for c in range(8)for h in(8,9)}|{(8,9)}
 if da:E.add((8,10));E|={(c,10)for c in range(8)if da>>c&1}
 if db:E.add((9,11));E|={(c,11)for c in range(8)if db>>c&1}
 X=set(map(tuple,r['X']));assert len(X)==len(r['X'])and X<=E;used=set()
 for t in r['S']:
  assert len(t)==len(set(t))==3;es=set(itertools.combinations(sorted(t),2));assert es<=E and not es&used;assert all(e in X for e in es if not(set(e)&{8,9}));used|=es
 assert len(X)<=2*len(r['S'])
                                                                          
                                                                       
 upper=E|{(10,11)}
 for t in itertools.combinations(range(12),3):
  es=set(itertools.combinations(t,2))
  if set(t)&{8,9}and es<=upper:assert es&X
 req=[0,0];allow=[0,0];present=[]
 for z,(hub,side)in enumerate([(8,10),(9,11)]):
  present.append((hub,side)in X)
  for c in range(8):
   if(c,side)in used or(c,side)in X:req[z]|=1<<c
   if(c,hub)in X or(hub,side)in X or(c,side)in X:allow[z]|=1<<c
 assert [req,allow,present]==r['contact_interval'];assert all(not(req[z]&~allow[z])for z in range(2))
 return req,allow,present

@lru_cache(None)
def masks(req,allow,present):return tuple(D for D in range(256)if not req&~D and not D&~allow and(not present or D))
core=json.loads(P.read_text());res=json.loads(R.read_text());assert res['complete']and not res['failures'];fresh=set(subprocess.check_output(['/opt/homebrew/bin/geng','-q','8'],text=True).splitlines());assert len(fresh)==12346 and {r['g6']for r in core['records']}==fresh
proof=json.loads(Path('work/tuza_degree10_c8_core_check.json').read_text());assert proof['result']=='PASS'and proof['payload_sha256']==hashlib.sha256(P.read_bytes()).hexdigest();covered={r['g6']for r in core['records']if r['status']=='PASS'};remaining=fresh-covered;assert len(covered)==12116 and len(remaining)==230
rows={r['g6']:r for r in res['rows']};assert set(rows)==remaining
certby={}
for r in res['certificates']:
 assert r['status']=='PASS';interval=literal(r);certby.setdefault(r['g6'],[]).append(interval)
counts={'pairs':0,'mixed':0,'excluded_cores':0,'certificate_cores':len(certby)};computed_rows={}
for pos,key in enumerate(sorted(remaining)):
 _,H=decode(key);deg=[sum(c in e for e in H)for c in range(8)];Ds=[]
 for D in range(1,256):
  if any(D>>c&1 and deg[c]>=7 for c in range(8)):continue
  L=H|{(c,8)for c in range(8)}|{(c,9)for c in range(8)if D>>c&1}
  if not iwke(10,L):Ds.append(D)
 assert Ds==rows[key]['side_masks']
 if not Ds:assert not rows[key]['pairs']and not rows[key]['mixed'];counts['excluded_cores']+=1;continue
 maps=auts(H);covered_rows=[0]*256
 for req,allow,present in certby.get(key,[]):
  for mp in maps:
   aa=masks(mp[req[0]],mp[allow[0]],present[0]);bb=masks(mp[req[1]],mp[allow[1]],present[1]);bitsa=sum(1<<D for D in aa);bitsb=sum(1<<D for D in bb)
   for D in aa:covered_rows[D]|=bitsb
   for D in bb:covered_rows[D]|=bitsa
 allowed=[]
 badedges=[]
 for x,y in H:
  common=sum(tuple(sorted((x,z)))in H and tuple(sorted((y,z)))in H for z in range(8)if z not in(x,y));badedges.append((x,y,common))
 for ia,a in enumerate(Ds):
  for b in Ds[ia:]:
   if any(2+common+int(a>>x&1 and a>>y&1)+int(b>>x&1 and b>>y&1)>8 for x,y,common in badedges):continue
   assert covered_rows[a]>>b&1,(key,a,b);allowed.append((a,b));counts['pairs']+=1
 if not iwke(9,H|{(c,8)for c in range(8)}):
  for D in Ds:assert covered_rows[0]>>D&1,(key,0,D);counts['mixed']+=1
 if pos%20==0:print('CORE',pos,'counts',counts,'seconds',round(time.time()-start,1),flush=True)
neg=0;r=json.loads(json.dumps(res['certificates'][0]));r['S'].append(r['S'][0])
try:literal(r)
except AssertionError:neg+=1
r=json.loads(json.dumps(res['certificates'][0]));r['contact_interval'][1][0]=255-r['contact_interval'][1][0]
try:literal(r)
except AssertionError:neg+=1
assert neg==2
out={'result':'PASS','core_types':12346,'unconditional_spare_two':12116,'residual_core_types':230,'interval_certificates':len(res['certificates']),'residual_labelled_unordered_pairs':counts['pairs'],'residual_labelled_mixed_models':counts['mixed'],'excluded_no_side_cores':counts['excluded_cores'],'certificate_cores':counts['certificate_cores'],'negative_controls':neg,'core_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'residual_sha256':hashlib.sha256(R.read_bytes()).hexdigest(),'seconds':time.time()-start};Path('work/tuza_degree10_c8_verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
