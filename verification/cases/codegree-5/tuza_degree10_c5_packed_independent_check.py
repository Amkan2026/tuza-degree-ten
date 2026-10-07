                                                                                
from pathlib import Path
from itertools import combinations,permutations
import sys,json,time,hashlib,copy
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
import tuza_degree10_c5_independent_check as ck
PC=np.array([sum(x>>k&1 for k in range(8))for x in range(256)],dtype=np.uint8)
def total(U):return int(np.sum(PC[U],dtype=np.uint64))

def admitted(h,nl,nr):
 L=ck.SIDES[nl][h];R=ck.SIDES[nr][h];CL,UL=ck.adata(nl,L);CR,UR=ck.adata(nr,R)
 H={e for k,e in enumerate(ck.CE)if h>>k&1};neighbors=[{d for d in range(5)if tuple(sorted((c,d)))in H}for c in range(5)]
 U=np.zeros((len(L),(len(R)+7)//8),dtype=np.uint8)
 for first in range(0,len(L),64):
  end=min(first+64,len(L));part=np.ones((end-first,len(R)),dtype=bool)
  for k,(c,d)in enumerate(ck.CE):
   if(c,d)in H:part&=CL[first:end,k,None]+CR[None,:,k]<=3-len(neighbors[c]&neighbors[d])
  for c in range(5):
   if not neighbors[c]:part&=((UL[first:end,None]|UR[None,:])&(1<<c))!=0
  if nl==nr:
   for row in range(first,end):part[row-first,:row]=False
  U[first:end]=np.packbits(part,axis=1,bitorder='little')
 return np.array(L,dtype=np.uint32),np.array(R,dtype=np.uint32),U

def remove(U,rows,columns):
 if not len(rows)or not len(columns):return
 selected=np.zeros(U.shape[1],dtype=np.uint8)
 np.bitwise_or.at(selected,columns//8,(1<<(columns%8)).astype(np.uint8))
 remaining=np.bitwise_not(selected)
 for first in range(0,len(rows),64):
  take=rows[first:first+64];U[take]=np.bitwise_and(U[take],remaining)

def save(payload):
 temporary=output.with_suffix(".pending.json")
 while True:
  try:
   temporary.write_text(json.dumps(payload,indent=2)+"\n");temporary.replace(output);return
  except OSError as error:
   if error.errno!=28:raise
   print("WAIT_STORAGE",flush=True);time.sleep(15)

source=Path(sys.argv[1]);output=Path(sys.argv[2]);raw=source.read_bytes();payload=json.loads(raw);reports=[];partial=[];start=time.monotonic()
for row in payload['cores']:
 nl,nr=row['degrees'];h=row['core']
 if not row.get('complete'):
  partial.append({'degrees':[nl,nr],'core':h,'complete_graph_domain':row.get('complete_graph_domain',False),'graph_extension':row.get('graph_extension')});continue
 L,R,U=admitted(h,nl,nr);count=total(U);assert count==row['admitted_pairs']
 H={e for k,e in enumerate(ck.CE)if h>>k&1}
 autos=[p for p in permutations(range(5))if{tuple(sorted((p[a],p[b])))for a,b in H}==H]
 for rec in row['intervals']:
  RF=ck.derive(rec)
  for p in autos:
   left=ck.hit(nl,L,RF[0],p);right=ck.hit(nr,R,RF[1],p)
   remove(U,left,right)
   if nl==nr:remove(U,right,left)
 assert not np.any(U),(nl,nr,h,total(U))
 report={'degrees':[nl,nr],'core':h,'admitted_pairs':count,'intervals':len(row['intervals']),'status':'PASS'};reports.append(report);print(json.dumps(report),flush=True)
 save({'status':'RUNNING','source_sha256':hashlib.sha256(raw).hexdigest(),'reports':reports,'partial':partial})
controls=[];rec=next(r for row in payload['cores']if row.get('complete')for r in row['intervals'])
for name,mutate in [('duplicate triangle',lambda q:q['packing'].append(q['packing'][0])),('empty cover',lambda q:q.__setitem__('cover',[])),('wrong required mask',lambda q:q['side_intervals'][0].__setitem__(0,q['side_intervals'][0][0]^1))]:
 q=copy.deepcopy(rec);mutate(q)
 try:ck.derive(q)
 except(AssertionError,KeyError,ValueError,IndexError):controls.append(name)
 else:raise AssertionError('Accepted corrupted certificate '+name)
lane=tuple(payload['cores'][0]['degrees']);expected=(set(ck.SIDES[lane[0]])&set(ck.SIDES[lane[1]]))-{15};keys={r['core']for r in reports}|{r['core']for r in partial if r['complete_graph_domain']and r['graph_extension']}
result={'status':'PASS','scope':'complete ordinary rows only; referenced graph extensions require their separate manifests','source':str(source),'source_sha256':hashlib.sha256(raw).hexdigest(),'complete_graph_lane_with_referenced_extensions':keys==expected,'ordinary_rows':len(reports),'canonical_side_pairs':sum(r['admitted_pairs']for r in reports),'intervals':sum(r['intervals']for r in reports),'reports':reports,'partial':partial,'negative_controls':controls,'seconds':time.monotonic()-start}
save(result);print('FINISHED',result['ordinary_rows'],result['canonical_side_pairs'],flush=True)
