from pathlib import Path
from itertools import combinations,permutations
import sys,json,numpy as np
sys.path.insert(0,'work');import tuza_degree10_c5_independent_check as ck

def make(kind,w):
 CA=(2,3);a,b,c=7,8,9;d=10;B=(11,12,13,14);A=(a,b,c);z=min(set(range(2,7))-set(CA)-{w})
 S=[(0,2,a),(0,3,b),(3,a,c),(2,b,c)];X={(x,v)for x in CA for v in A}|{(a,b),(0,c),(0,d),(0,1)};safe=set(combinations(A,2));required=set(combinations(A,2))|{(x,v)for x in CA for v in A}
 if kind=='K4-minus-edge':
  t,blank,p,q=B
  S.extend([tuple(sorted(T))for T in[(1,w,p),(1,blank,q),(t,w,q),(t,blank,p)]])
  right_edges=(set(combinations(B,2))-{(p,q)})|{(w,k)for k in(t,p,q)}
  X|=right_edges;required|=right_edges
 else:
  p,q,r,blank=B
  S.extend([tuple(sorted(T))for T in[(1,p,w),(1,q,blank),(p,r,blank),(q,r,w)]])
  X|={(x,k)for x in(w,blank)for k in(p,q,r)}|{(p,q),(1,r)}
  safe|=set(combinations((p,q,r),2));required|=set(combinations(B,2))|{(w,k)for k in(p,q,r)}
 S.append((0,1,z));S=[tuple(sorted(T))for T in S];X={tuple(sorted(e))for e in X};required={tuple(sorted(e))for e in required};used=[e for T in S for e in combinations(T,2)];assert len(used)==len(set(used))and len(X)==18 and len(S)==9
 base=ck.build(0,10,10,0,0);RF=[];actual=[]
 for hub,first in[(0,7),(1,11)]:
  mp={**{k:k+2 for k in range(5)},**{k+5:first+k for k in range(4)}};es=[tuple(sorted((mp[i],mp[j])))for i,j in ck.sidepairs(10)];R=F=0
  for k,e in enumerate(es):
   if e in X or e in used or e in required:R|=1<<k
   if e not in X and tuple(sorted((hub,e[0])))not in X and tuple(sorted((hub,e[1])))not in X:F|=1<<k
  assert R&F==0;RF.append([R,F]);actual.append(es)
 lower=base|{e for es,rf in zip(actual,RF)for k,e in enumerate(es)if rf[0]>>k&1};upper=base|{e for es,rf in zip(actual,RF)for k,e in enumerate(es)if not rf[1]>>k&1};assert X|set(used)<=lower
 for e in safe:
  known={j for j in range(15)if tuple(sorted((j,e[0])))in lower and tuple(sorted((j,e[1])))in lower};assert len(known)==4
  assert sum(tuple(sorted((i,j)))in lower for i,j in combinations(known,2))==5
  for j in known:assert set(combinations(tuple(sorted((*e,j))),2))&X
 for T in combinations(range(15),3):
  es=set(combinations(T,2))
  if set(T)&{0,1}and es<=upper:assert es&X
 assert all(e in X or e in safe or set(e)&{0,1}for e in used)
 return {'kind':kind,'right_common_contact':w,'fresh_book_vertex':z,'packing':S,'cover':sorted(X),'safe_nonhub_edges':sorted(safe),'side_intervals':RF}

previous=json.loads(Path('work/tuza_degree10_c5_h0_human_templates.json').read_text());row=next(r for r in previous['reports']if r['degrees']==[10,10]);L,R,U=ck.admitted(0,10,10);idxL={int(a):i for i,a in enumerate(L)};idxR={int(a):i for i,a in enumerate(R)};U[:]=False
for a,b in row['remaining_pairs']:U[idxL[a],idxR[b]]=True
count0=int(np.sum(U));assert count0==160;records=[]
for kind in['K4-minus-edge','K4']:
 for w in[2,4]:
  rec=make(kind,w);before=int(np.sum(U))
  for perm in permutations(range(5)):
   a=ck.hit(10,L,rec['side_intervals'][0],perm);b=ck.hit(10,R,rec['side_intervals'][1],perm);U[np.ix_(a,b)]=False;U[np.ix_(b,a)]=False
  rec['new_pairs']=before-int(np.sum(U));records.append(rec)
left=int(np.sum(U));out={'status':'PASS'if not left else'UNRESOLVED','degrees':[10,10],'core':0,'incoming_residual':count0,'human_templates':records,'graph_cases_unclosed':left,'complete_graph_domain':not left,'complete_pair_domain':False};Path('work/tuza_degree10_c5_h0_nontriangle_human.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='human_templates'}),flush=True)
