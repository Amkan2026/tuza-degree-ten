                                                           
                                                                                
                                                                      
   
from pathlib import Path
from itertools import combinations,permutations
import json,time,hashlib,sys
import numpy as np
CE=list(combinations(range(5),2));SOURCE=Path(sys.argv[1]) if __name__=='__main__' and len(sys.argv)>1 else Path(__file__).with_name('tuza_degree9_c5_intervals.json');OUT=Path(sys.argv[2]) if __name__=='__main__' and len(sys.argv)>2 else Path(__file__).with_suffix('.json');SIDES={n:{}for n in(7,8,9)}
for line in Path(__file__).with_name('tuza_degree9_c5_side_direct.txt').read_text().splitlines():
 n,h,s=map(int,line.split());SIDES[n].setdefault(h,[]).append(s)

def sidepairs(n):
 r=n-6;return[(c,a)for a in range(5,5+r)for c in range(5)]+list(combinations(range(5,5+r),2))
def build(h,nl,nr,l,r):
 a=nl-6;b=nr-6;nv=7+a+b;E={(0,1)}|{(u,c)for u in(0,1)for c in range(2,7)}|{(0,z)for z in range(7,7+a)}|{(1,z)for z in range(7+a,nv)}|{(c+2,d+2)for i,(c,d)in enumerate(CE)if h>>i&1}
 for n,m,first in[(nl,l,7),(nr,r,7+a)]:
  mp={**{c:c+2 for c in range(5)},**{c+5:first+c for c in range(n-6)}}
  E|={tuple(sorted((mp[x],mp[y])))for i,(x,y)in enumerate(sidepairs(n))if m>>i&1}
 return E

def derive(rec):
 nl,nr,h,l,r=rec['key'];a=nl-6;b=nr-6;nv=7+a+b;base=build(h,nl,nr,0,0);S=[tuple(t)for t in rec['packing']];X=set(map(tuple,rec['cover']));used=[e for t in S for e in combinations(t,2)]
 assert all(tuple(sorted(t))==t and len(set(t))==3 for t in S);assert len(used)==len(set(used));assert len(X)==len(rec['cover'])and len(X)<=2*len(S);assert all(e in X for e in used if not(set(e)&{0,1}));assert set(used)<=build(h,nl,nr,l,r)
 RF=[];actual=[]
 for n,hub,first in[(nl,0,7),(nr,1,7+a)]:
  mp={**{c:c+2 for c in range(5)},**{c+5:first+c for c in range(n-6)}};es=[tuple(sorted((mp[x],mp[y])))for x,y in sidepairs(n)];rr=ff=0
  for i,e in enumerate(es):
   if e in X or e in used:rr|=1<<i
   if e not in X and tuple(sorted((hub,e[0])))not in X and tuple(sorted((hub,e[1])))not in X:ff|=1<<i
  assert rr&ff==0;RF.append([rr,ff]);actual.append(es)
 assert RF==rec['side_intervals'];lower=base|{e for es,rf in zip(actual,RF)for i,e in enumerate(es)if rf[0]>>i&1};upper=base|{e for es,rf in zip(actual,RF)for i,e in enumerate(es)if not(rf[1]>>i&1)}
 assert X<=lower and set(used)<=lower
 for t in combinations(range(nv),3):
  te=set(combinations(t,2))
  if set(t)&{0,1}and te<=upper:assert X&te
 return RF

def adata(n,ms):
 r=n-6;cc=np.zeros((len(ms),10),dtype=np.int8);union=np.zeros(len(ms),dtype=np.uint8)
 for j,m in enumerate(ms):
  nb=[0]*5
  for a in range(r):
   d=(m>>(5*a))&31;union[j]|=d
   for c in range(5):
    if d>>c&1:nb[c]|=1<<a
  for k,(c,d)in enumerate(CE):cc[j,k]=(nb[c]&nb[d]).bit_count()
 return cc,union

def admitted(h,nl,nr):
 L=SIDES[nl][h];R=SIDES[nr][h];CL,UL=adata(nl,L);CR,UR=adata(nr,R);H={e for i,e in enumerate(CE)if h>>i&1};nb=[set()for _ in range(5)]
 for c,d in H:nb[c].add(d);nb[d].add(c)
 U=np.ones((len(L),len(R)),dtype=bool)
 for k,(c,d)in enumerate(CE):
  if(c,d)in H:U&=CL[:,k,None]+CR[None,:,k]+2+len(nb[c]&nb[d])<=5
 for c in range(5):
  if not nb[c]:U&=((UL[:,None]|UR[None,:])&(1<<c))!=0
 if nl==nr:U[np.tril_indices(len(L),-1)]=False
 return np.array(L,dtype=np.uint32),np.array(R,dtype=np.uint32),U

def hit(n,masks,rf,cp):
 ps=sidepairs(n);ix={e:i for i,e in enumerate(ps)};z=np.zeros(len(masks),dtype=bool)
 for perm in permutations(range(5,5+n-6)):
  mp={**dict(enumerate(cp)),**dict(zip(range(5,5+n-6),perm))};req=forbid=0
  for j,(c,d)in enumerate(ps):
   bit=1<<ix[tuple(sorted((mp[c],mp[d])))]
   if rf[0]>>j&1:req|=bit
   if rf[1]>>j&1:forbid|=bit
  z|=((masks&req)==req)&((masks&forbid)==0)
 return np.flatnonzero(z)

def main():
 start=time.monotonic();payload=SOURCE.read_bytes();p=json.loads(payload);reports=[]
 for row in p['cores']:
  if not row.get('complete'):continue
  nl,nr=row['degrees'];h=row['core'];L,R,U=admitted(h,nl,nr);count=int(np.sum(U));assert count==row['admitted_pairs'];H={e for i,e in enumerate(CE)if h>>i&1};cp=[perm for perm in permutations(range(5))if{tuple(sorted((perm[c],perm[d])))for c,d in H}==H]
  for rec in row['intervals']:
   RF=derive(rec)
   for perm in cp:
    a=hit(nl,L,RF[0],perm);b=hit(nr,R,RF[1],perm);U[np.ix_(a,b)]=False
    if nl==nr:U[np.ix_(b,a)]=False
  assert not np.any(U),(nl,nr,h,int(np.sum(U)));reports.append({'degrees':[nl,nr],'core':h,'admitted_pairs':count,'intervals':len(row['intervals']),'result':'PASS'});print('PASS',nl,nr,h,count,len(row['intervals']),flush=True)
                                                                                   
 import copy
 if reports:
  rec=next(rec for row in p['cores']if row.get('complete')for rec in row['intervals']);controls=[]
  for name,mutate in [('duplicate triangle',lambda x:x['packing'].append(x['packing'][0])),('empty cover',lambda x:x.__setitem__('cover',[])),('missing required mask',lambda x:x['side_intervals'][0].__setitem__(0,x['side_intervals'][0][0]^1))]:
   q=copy.deepcopy(rec);mutate(q)
   try:derive(q)
   except(AssertionError,KeyError,ValueError,IndexError):controls.append(name)
   else:raise AssertionError('mutation accepted '+name)
 else:controls=[]
 out={'complete_lane':p.get('complete',False)and len(reports)==len(p['cores']),'verified_complete_cores':len(reports),'reports':reports,'admitted_pairs_verified':sum(r['admitted_pairs']for r in reports),'intervals_verified':sum(r['intervals']for r in reports),'negative_controls_rejected':controls,'source_sha256':hashlib.sha256(payload).hexdigest(),'elapsed_seconds':time.monotonic()-start,'result':'PASS'};OUT.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='reports'},indent=2),flush=True)
if __name__=='__main__':main()
