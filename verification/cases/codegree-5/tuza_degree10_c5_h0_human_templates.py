from pathlib import Path
from itertools import combinations,permutations
import sys,json,numpy as np
sys.path.insert(0,'work');import tuza_degree10_c5_independent_check as ck

def template(nl,nr,CA,CB,z,p=None):
 A=(7,8,9);B=tuple(range(7+nl-6,10+nl-6));da=10 if nl==10 else None;db=10+nl-6
 x,y=CA;a,b,c=A;rr,s,t=B;pp,q=CB
 S=[tuple(sorted(T))for T in [(0,a,x),(0,b,y),(a,c,y),(b,c,x),(1,rr,pp),(1,s,q),(rr,t,q),(s,t,pp),(0,1,z)]]
 X={tuple(sorted(e))for e in [(w,k)for w in CA for k in A]+[(a,b),(0,c)]+[(w,k)for w in CB for k in B]+[(rr,s),(1,t),(1,db),(0,1)]}
 if da is not None:
  X.add((0,da));assert p is not None;S.append(tuple(sorted((0,da,p))));X.add(tuple(sorted((da,p))))
 safe=set(combinations(A,2))|set(combinations(B,2));nv=7+(nl-6)+(nr-6);base=ck.build(0,nl,nr,0,0);RF=[];actual=[]
 used=[e for T in S for e in combinations(T,2)];assert len(used)==len(set(used))and len(X)==2*len(S)
 for n,hub,first,V,C in[(nl,0,7,A,CA),(nr,1,7+nl-6,B,CB)]:
  mp={**{k:k+2 for k in range(5)},**{k+5:first+k for k in range(n-6)}};es=[tuple(sorted((mp[i],mp[j])))for i,j in ck.sidepairs(n)];witness=set(combinations(V,2))|{tuple(sorted((w,v)))for w in C for v in V};req=forbid=0
  for k,e in enumerate(es):
   if e in X or e in used or e in witness:req|=1<<k
   if e not in X and tuple(sorted((hub,e[0])))not in X and tuple(sorted((hub,e[1])))not in X:forbid|=1<<k
  assert req&forbid==0;RF.append([req,forbid]);actual.append(es)
 lower=base|{e for es,rf in zip(actual,RF)for k,e in enumerate(es)if rf[0]>>k&1};upper=base|{e for es,rf in zip(actual,RF)for k,e in enumerate(es)if not rf[1]>>k&1}
 assert X|set(used)<=lower
 for e in safe:
  common={w for w in range(nv)if tuple(sorted((w,e[0])))in lower and tuple(sorted((w,e[1])))in lower};assert len(common)==4
  assert sum(tuple(sorted((i,j)))in lower for i,j in combinations(common,2))==5
  for w in common:assert set(combinations(tuple(sorted((*e,w))),2))&X
 for T in combinations(range(nv),3):
  es=set(combinations(T,2))
  if set(T)&{0,1}and es<=upper:assert es&X
 return {'degrees':[nl,nr],'contact_pairs':[CA,CB],'fresh_book_vertex':z,'extra_isolate_contact':p,'packing':S,'cover':sorted(X),'safe_nonhub_edges':sorted(safe),'side_intervals':RF}

out={'status':'PASS','selected_common_density':0,'templates':[],'reports':[]}
for lane,name in [((9,10),'nine_ten'),((10,10),'ten_ten')]:
 source=Path('work/tuza_degree10_c5_h0_'+name+'_pair_residual.json');z=json.loads(source.read_text());L,R,U=ck.admitted(0,*lane)
 for rec in z['pair_intervals']:
  rf=ck.derive(rec)
  for perm in permutations(range(5)):
   a=ck.hit(lane[0],L,rf[0],perm);b=ck.hit(lane[1],R,rf[1],perm);U[np.ix_(a,b)]=False
   if lane[0]==lane[1]:U[np.ix_(b,a)]=False
 original=int(np.sum(U));rows=[]
 for CB in[(5,6),(2,4),(2,3)]:
  CA=(2,3);book=min(set(range(2,7))-set(CA)-set(CB));contacts=[None]if lane[0]==9 else sorted(set(range(2,7))-set(CA)-{book})
  for p in contacts:
   rec=template(*lane,CA,CB,book,p);count0=int(np.sum(U))
   for perm in permutations(range(5)):
    a=ck.hit(lane[0],L,rec['side_intervals'][0],perm);b=ck.hit(lane[1],R,rec['side_intervals'][1],perm);U[np.ix_(a,b)]=False
    if lane[0]==lane[1]:U[np.ix_(b,a)]=False
   rec['new_pairs']=count0-int(np.sum(U));rows.append(rec);out['templates'].append(rec)
 remaining=int(np.sum(U));pairs=[(int(L[a]),int(R[b]))for a,b in np.argwhere(U)]
 report={'degrees':lane,'admitted_pairs':z['admitted_pairs'],'pair_residual':original,'human_templates':len(rows),'human_closed_pairs':original-remaining,'graph_cases_unclosed':remaining,'complete_graph_domain':remaining==0,'complete_pair_domain':False,'remaining_pairs':pairs};out['reports'].append(report)
 if remaining:out['status']='PARTIAL';print('remaining',lane,remaining,flush=True)
 print('REPORT',json.dumps({k:v for k,v in report.items()if k!='remaining_pairs'}),flush=True)
Path('work/tuza_degree10_c5_h0_human_templates.json').write_text(json.dumps(out,indent=2)+'\n')
