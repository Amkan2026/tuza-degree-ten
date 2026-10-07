from pathlib import Path
from itertools import combinations,permutations
import sys,json,numpy as np
sys.path.insert(0,str(Path(__file__).parent));import tuza_degree10_c5_independent_check as ck

def derive(rec):
 nl,nr,h,l,r=rec['key'];nv=7+nl-6+nr-6;S=list(map(tuple,rec['packing']));X=set(map(tuple,rec['cover']));D={tuple(z['edge']):set(z['known_common'])for z in rec['safe_edges']};used=[e for t in S for e in combinations(t,2)];assert all(tuple(sorted(t))==t and len(set(t))==3 for t in S);assert len(used)==len(set(used));assert len(X)==len(rec['cover'])and len(X)<=2*len(S);assert rec['selected_common_density']==h.bit_count();assert len(D)==len(rec['safe_edges']);original=ck.build(h,nl,nr,l,r);assert set(used)|X<=original
 required=set(used)|X
 for e,known in D.items():
  assert tuple(sorted(e))==e and not set(e)&{0,1} and len(known)==4
  assert {w for w in range(nv)if tuple(sorted((w,e[0])))in original and tuple(sorted((w,e[1])))in original}==known
  required|={e}|{tuple(sorted((a,b)))for a in e for b in known}|{tuple(sorted((a,b)))for a,b in combinations(known,2)if tuple(sorted((a,b)))in original}
 actual=[];RF=[]
 for n,hub,first in[(nl,0,7),(nr,1,7+nl-6)]:
  mp={**{c:c+2 for c in range(5)},**{c+5:first+c for c in range(n-6)}};es=[tuple(sorted((mp[a],mp[b])))for a,b in ck.sidepairs(n)];R=F=0
  for i,e in enumerate(es):
   if e in required:R|=1<<i
   if e not in X and tuple(sorted((hub,e[0])))not in X and tuple(sorted((hub,e[1])))not in X:F|=1<<i
  assert not R&F;RF.append([R,F]);actual.append(es)
 assert RF==rec['side_intervals'];base=ck.build(h,nl,nr,0,0);lower=base|{e for es,rf in zip(actual,RF)for i,e in enumerate(es)if rf[0]>>i&1};upper=base|{e for es,rf in zip(actual,RF)for i,e in enumerate(es)if not rf[1]>>i&1};assert set(used)|X<=lower
 for e,known in D.items():
  assert {w for w in range(nv)if tuple(sorted((w,e[0])))in lower and tuple(sorted((w,e[1])))in lower}==known
  assert sum(tuple(sorted((a,b)))in lower for a,b in combinations(known,2))>h.bit_count()
  for w in known:assert set(combinations(tuple(sorted((*e,w))),2))&X
 for t in combinations(range(nv),3):
  tes=set(combinations(t,2))
  if set(t)&{0,1}and tes<=upper:assert tes&X
 assert all(set(e)&{0,1}or e in X or e in D for e in used)
 return RF

def apply(U,L,R,nl,nr,h,RF):
 H={e for i,e in enumerate(ck.CE)if h>>i&1}
 for p in permutations(range(5)):
  if {tuple(sorted((p[a],p[b])))for a,b in H}!=H:continue
  a=ck.hit(nl,L,RF[0],p);b=ck.hit(nr,R,RF[1],p);U[np.ix_(a,b)]=False
  if nl==nr:U[np.ix_(b,a)]=False

def main():
 import hashlib,time,copy
 source=Path(sys.argv[1]);outpath=Path(sys.argv[2]);raw=source.read_bytes();z=json.loads(raw);reports=[]
 for row in z['cores']:
  nl,nr=row['degrees'];h=row['core'];L,R,U=ck.admitted(h,nl,nr);count=int(np.sum(U));assert count==row['admitted_pairs']
  for cert in row['pair_intervals']:apply(U,L,R,nl,nr,h,ck.derive(cert))
  before=int(np.sum(U));assert before==row['initial_pair_residual']
  for cert in row['edge_intervals']:apply(U,L,R,nl,nr,h,derive(cert))
  remaining=int(np.sum(U));assert remaining==0
  reports.append({'degrees':[nl,nr],'core':h,'admitted_pairs':count,'pair_intervals':len(row['pair_intervals']),'initial_pair_residual':before,'edge_intervals':len(row['edge_intervals']),'graph_cases_unclosed':remaining,'status':'PASS'});print(json.dumps(reports[-1]),flush=True)
                                                              
 cert=z['cores'][0]['edge_intervals'][0];bad=copy.deepcopy(cert);bad['packing'].append(bad['packing'][0]);bad2=copy.deepcopy(cert);bad2['cover']=[];bad3=copy.deepcopy(cert);bad3['safe_edges'][0]['known_common']=[];controls=0
 for b in[bad,bad2,bad3]:
  try:derive(b)
  except (AssertionError,KeyError):controls+=1
 assert controls==3
 report={'status':'PASS','complete_graph_domain':True,'complete_pair_domain':False,'graph_cases_unclosed':0,'corruption_controls_rejected':controls,'cores':reports,'source':str(source),'source_sha256':hashlib.sha256(raw).hexdigest()};outpath.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
