                                                                                                       
from pathlib import Path
from itertools import combinations,permutations
from functools import lru_cache
import json,time,hashlib,copy,sys
import numpy as np
sys.path.insert(0,str(Path(__file__).parent));import tuza_degree10_c5_independent_check as iv
st=time.time();P=json.loads(Path('work/tuza_degree10_c5_density_sides.json').read_text());oldP=json.loads(Path('work/tuza_degree9_c5_sides.json').read_text());full10=json.loads(Path('work/tuza_degree10_c5_sides_order10.json').read_text());direct10=json.loads(Path('work/tuza_degree10_c5_star_side_direct.json').read_text());assert full10['core_sides']['15']==direct10['core_sides']
CE=list(combinations(range(5),2));CI={e:i for i,e in enumerate(CE)};CP=[(0,)+p for p in permutations(range(1,5))];EC=list(combinations(range(4),2));IC={e:i for i,e in enumerate(EC)}

def sidegraph(n,h,m):
 adj=[set()for _ in range(n)]
 def edge(a,b):adj[a].add(b);adj[b].add(a)
 for c in range(1,6):edge(0,c)
 for i,(a,b)in enumerate(CE):
  if h>>i&1:edge(a+1,b+1)
 for i,(a,b)in enumerate(iv.sidepairs(n)):
  if m>>i&1:edge(a+1,b+1)
 return adj

def density_ok(adj,count):return all(sum(b in adj[a]for a,b in combinations(adj[v],2))<=count for v in range(len(adj))if len(adj[v])==5)

S={n:np.array(P[str(n)]['core_sides']['15'],dtype=np.uint32)for n in (9,10)}
for n,full in ((9,oldP['9']['core_sides']['15']),(10,direct10['core_sides'])):
 selected=[m for m in full if density_ok(sidegraph(n,15,m),4)];assert selected==list(S[n])
print('PASS density-selected star side domains',len(S[9]),len(S[10]),flush=True)

                                                                            
                                                                          
                                                                       
capcheck=json.loads(Path('work/tuza_degree10_c5_private_cap_direct.json').read_text());assert capcheck['status']=='PASS'and {r['core']for r in capcheck['cores']}=={23,29,184}and all(r['outsideWKE']==0 and r['all_contact_states']==65536 for r in capcheck['cores']);CAPS={15:6,23:5,29:5,54:6,58:6,184:5}
@lru_cache(None)
def hcanon(es):return min(sum(1<<CI[tuple(sorted((p[a],p[b])))]for a,b in es)for p in permutations(range(5)))
PRIVATE={};BOUND={};CONTACT={}
for n in (9,10):
 r=n-6;p=[];bound=[];contacts=[]
 for m0 in S[n]:
  m=int(m0);adj=sidegraph(n,15,m);limits=[]
  for q in range(n):
   if len(adj[q])!=5:continue
   C=sorted(adj[q]);H=tuple((a,b)for a,b in CE if C[b]in adj[C[a]])
   if len(H)!=4:continue
   A=set(range(n))-{q}-adj[q];private=sum(b in adj[a]for a,b in combinations(A,2));k=CAPS[hcanon(H)];limits.append((private+k)*16+min(private,k))
  assert limits;bound.append(min(limits));p.append((m>>(5*r)).bit_count());contacts.append([sum((m>>(5*b+c))&1 for b in range(r))for c in range(1,5)])
 PRIVATE[n]=np.array(p,dtype=np.int16);BOUND[n]=np.array(bound,dtype=np.int16);CONTACT[n]=np.array(contacts,dtype=np.int8)

                                                                          
def pair_literal(rec,ds):
 nl,nr=ds;r=nl-6;s=nr-6;nv=7+r+s;base=iv.build(15,nl,nr,0,0);actual=[]
 for n,start in ((nl,7),(nr,7+r)):
  mp={**{c:c+2 for c in range(5)},**{c+5:start+c for c in range(n-6)}};actual.append([tuple(sorted((mp[a],mp[b])))for a,b in iv.sidepairs(n)])
 return literal(rec,base,actual,{0,1},nv,{(a,b)for a in range(7,7+r)for b in range(7+r,nv)})

def literal(rec,base,actual,U,nv,unknown):
 RF=rec['side_intervals'];assert len(RF)==len(actual);low=set(base);high=set(base)
 for es,(R,F)in zip(actual,RF):
  assert not R&F and R<(1<<len(es))and F<(1<<len(es))
  for i,e in enumerate(es):
   if e is None:assert not R>>i&1;continue
   if R>>i&1:low.add(e)
   if not F>>i&1:high.add(e)
 S0=[tuple(t)for t in rec['packing']];X=set(map(tuple,rec['cover']));assert len(X)==len(rec['cover']);used=[e for t in S0 for e in combinations(t,2)];assert len(used)==len(set(used));assert set(used)<=low and X<=low;assert len(X)+rec.get('outside_bound',0)<=2*len(S0);assert all(e in X for e in used if not set(e)&U);assert all(tuple(sorted(t))==t and len(set(t))==3 for t in S0)
 high|=unknown
 for t in combinations(range(nv),3):
  te=set(combinations(t,2))
  if set(t)&U and te<=high:assert X&te
 return True

old=json.loads(Path('work/tuza_degree9_c5_complete_certificates.json').read_text());oldrow=next(r for r in old['cores']if r['degrees']==[9,9]and r['core']==15);lifts=json.loads(Path('work/tuza_degree10_c5_star_lift.json').read_text());PAIR={(9,9):oldrow['intervals']};PAIR.update({tuple(r['degrees']):r['intervals']for r in lifts['lanes']})
U={}
for ds,recs in PAIR.items():
 a,b=ds;uncovered=np.ones((len(S[a]),len(S[b])),dtype=bool)
 for rec in recs:
  pair_literal(rec,ds)
  for cp in CP:
   x=iv.hit(a,S[a],rec['side_intervals'][0],cp);y=iv.hit(b,S[b],rec['side_intervals'][1],cp);uncovered[np.ix_(x,y)]=False
   if a==b:uncovered[np.ix_(y,x)]=False
 U[a,b]=uncovered
 if a!=b:U[b,a]=uncovered.T
print('PASS pair literals',sum(map(len,PAIR.values())),flush=True)

                                                                          
                                                                              
fan=json.loads(Path('work/tuza_degree10_c5_star_fan_intervals.json').read_text());GOOD={n:np.zeros(len(S[n]),dtype=np.uint8)for n in (9,10)}
def fan_literal(rec,n):
 r=n-6;es=[None if i%5==0 else(i%5-1,4+i//5)for i in range(5*r)]+list(combinations(range(4,4+r),2));R,F=rec['R'],rec['F'];M=[tuple(e)for e in rec['matching']];Q=set(rec['Q']);assert len(M)in(2,3)and len(Q)<=len(M)+1;v=[v for e in M for v in e];assert len(v)==len(set(v));assert all(e[0]not in(0,1)for e in M);low={e for i,e in enumerate(es)if e is not None and R>>i&1};high={e for i,e in enumerate(es)if e is not None and not F>>i&1};assert set(M)<=low;assert all(set(e)&Q or e in M for e in high);assert not R&F
for row in fan['rows']:
 n=row['degree'];assert row['blocked_leaves']==[0,1]
 for rec in row['intervals']:
  fan_literal(rec,n)
  for cp in CP:
   blocked=IC[tuple(sorted((cp[1]-1,cp[2]-1)))];ids=iv.hit(n,S[n],[rec['R'],rec['F']],cp);GOOD[n][ids]|=1<<blocked
print('PASS fan literals',sum(len(r['intervals'])for r in fan['rows']),flush=True)
RAIN=np.zeros((64,64,64),dtype=bool);gm=np.arange(64,dtype=np.uint8)
for a,b,c in permutations(range(4),3):
 k1=IC[tuple(sorted((a,c)))];k2=IC[tuple(sorted((a,b)))];k3=IC[tuple(sorted((b,c)))];RAIN|=(((gm>>k1)&1)[:,None,None]&((gm>>k2)&1)[None,:,None]&((gm>>k3)&1)[None,None,:]).astype(bool)

                                                                             
def tail_geometry(ds):
 base=set(combinations(range(3),2))|{(h,c)for h in range(3)for c in range(3,7)};actual=[];blocks=[];start=7
 for h,n in enumerate(ds):
  r=n-6;B=list(range(start,start+r));start+=r;blocks.append(B);base|={(h,b)for b in B};es=[]
  for b in B:es.append(None);es.extend((c,b)for c in range(3,7))
  es.extend(combinations(B,2));actual.append(es)
 unknown={tuple(sorted((a,b)))for h,k in combinations(range(3),2)for a in blocks[h]for b in blocks[k]};return base,actual,start,unknown

tail=json.loads(Path('work/tuza_degree10_c5_star_tail_reduce.json').read_text());assert tail['complete'];tailrec=tail['records'];assert len(tailrec)==3
for rec in tailrec:
 assert rec['removed']==[0,1,2]and rec['outside_bound']==0;base,es,nv,unknown=tail_geometry(rec['degrees']);literal(rec,base,es,{0,1,2},nv,unknown)
print('PASS tail literals',len(tailrec),flush=True)
reports=[];total=0
for ds in ((9,9,9),(9,9,10),(9,10,10),(10,10,10)):
 a,b,c=ds;bad=np.any(~RAIN[:,:,np.unique(GOOD[c])],axis=2);pairs=np.argwhere(U[a,b]&bad[GOOD[a][:,None],GOOD[b][None,:]]);tuples=[]
 for i,j in pairs:
  if a==b and i>j:continue
  good=U[a,c][i]&U[b,c][j]&np.all(CONTACT[c]+CONTACT[a][i]+CONTACT[b][j]<=7,axis=1)&~RAIN[GOOD[a][i],GOOD[b][j],GOOD[c]]
  sab=(PRIVATE[a][i]+PRIVATE[b][j])*16+min(PRIVATE[a][i],PRIVATE[b][j]);sac=(PRIVATE[a][i]+PRIVATE[c])*16+np.minimum(PRIVATE[a][i],PRIVATE[c]);sbc=(PRIVATE[b][j]+PRIVATE[c])*16+np.minimum(PRIVATE[b][j],PRIVATE[c]);score=np.minimum(sab,np.minimum(sac,sbc));bound=np.minimum(BOUND[a][i],np.minimum(BOUND[b][j],BOUND[c]));good&=score<=bound
  if b==c:good[:j]=False
  tuples.extend((int(i),int(j),int(k))for k in np.flatnonzero(good))
 ids=np.array(tuples,dtype=np.int32).reshape((-1,3));covered=np.zeros(len(ids),dtype=bool)
 for rec in tailrec:
  for perm in permutations(range(3)):
   if any(ds[h]!=rec['degrees'][perm[h]]for h in range(3)):continue
   for cp in CP:
    hit=[np.zeros(len(S[n]),dtype=bool)for n in ds]
    for h,n in enumerate(ds):hit[h][iv.hit(n,S[n],rec['side_intervals'][perm[h]],cp)]=True
    if len(ids):covered|=hit[0][ids[:,0]]&hit[1][ids[:,1]]&hit[2][ids[:,2]]
 assert np.all(covered),(ds,len(ids),int(np.sum(~covered)));total+=len(ids);reports.append({'degrees':list(ds),'tail_after_all_graph_filters':len(ids),'tail_covered':int(np.sum(covered)),'unclosed':0});print('PASS graph domain',ds,len(ids),flush=True)
controls=[]
for name,mut in [('duplicate tail triangle',lambda r:r['packing'].append(r['packing'][0])),('empty tail cover',lambda r:r.__setitem__('cover',[])),('missing lower packing edge',lambda r:r['side_intervals'][0].__setitem__(0,0))]:
 rec=copy.deepcopy(tailrec[0]);mut(rec);base,es,nv,unknown=tail_geometry(rec['degrees'])
 try:literal(rec,base,es,{0,1,2},nv,unknown)
 except(AssertionError,KeyError,IndexError,ValueError):controls.append(name)
 else:raise AssertionError('corruption accepted '+name)
files=['work/tuza_degree10_c5_star_side_direct.json','work/tuza_degree10_c5_density_sides.json','work/tuza_degree10_c5_private_cap_direct.json','work/tuza_degree9_c5_complete_certificates.json','work/tuza_degree10_c5_star_lift.json','work/tuza_degree10_c5_star_fan_intervals.json','work/tuza_degree10_c5_star_tail_reduce.json']
out={'status':'PASS','complete_selected_star_graph_domain':True,'complete_pair_domain':False,'ambient_degree_bound':10,'density_selected_star_sides':{str(n):len(S[n])for n in S},'initial_partner_private_caps':CAPS,'pair_intervals_verified':sum(map(len,PAIR.values())),'fan_intervals_verified':sum(len(r['intervals'])for r in fan['rows']),'tail_intervals_verified':len(tailrec),'graph_reports':reports,'total_tail':total,'graph_cases_unclosed':0,'negative_controls_rejected':controls,'source_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in files},'elapsed_seconds':time.time()-st};Path('work/tuza_degree10_c5_star_independent.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in('source_sha256','graph_reports')},indent=2),flush=True)
