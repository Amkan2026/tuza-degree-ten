                                                                                  
from pathlib import Path
from itertools import combinations
import importlib.util,subprocess,json,hashlib,time
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('literal8',HERE/'tuza_degree8_codegree6_check.py')
c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
edge=c.edge;need=c.need
def graph(H,B):
 return {edge(a+2,b+2) for a,b in H}|{(0,1),(1,9)}|{(h,z) for h in (0,1) for z in range(2,8)}|{(z+2,9) for z in range(6) if B>>z&1}
def human(H,B):
 zz=[z for z in range(6) if all(e in H for e in combinations([i for i in range(6) if i!=z],2))]
 if zz:
  z=next((z for z in zz if B>>z&1),zz[0]);K=[i+2 for i in range(6) if i!=z];Z=z+2
  S=c.fano(0,1,K);X=set(combinations(K,2))|{(0,1),(1,9)}
  if B>>z&1:return S+[(1,9,Z)],X|{edge(0,Z),edge(1,Z),edge(9,Z)},'augmented_Fano'
  D=[i+2 for i in range(6) if edge(i,z) in H]
  if len(D)<=2:return S,X|{edge(Z,d) for d in D},'Fano_small_z'
  need(len(D)==3,'unhandled K5 exception')
  E=[i for i in K if i not in D];I=[i+2 for i in range(6) if B>>i&1]
  need(set(I)<=set(E) and I,'invalid high-codegree contact')
  k=I[0];l=next(i for i in E if i!=k);p,q,r=D
  A0,A1=Z,0;B0,B1=k,1;C0,C1=l,p;D0,D1=q,r
  full=[(A0,B0,C0),(A1,B1,C1),(A0,B1,D0),(A1,B0,D1),(A0,C1,D1),(A1,C0,D0),(B0,C1,D0),(B1,C0,D1)]
  S=full[1:]+[(1,9,k)];X={edge(a+2,b+2) for a,b in H}|{(0,1),(1,9),edge(9,k)}
  return S,X,'K5_z3_cocktail_trade'
 deg={i:sum(i in e for e in H) for i in range(6)}
 I=[i+2 for i in range(6) if deg[i]==3];K=[i+2 for i in range(6) if deg[i]==5]
 need(len(I)==len(K)==3 and len(H)==12,'unknown non-K5 exception')
 contacts=[i+2 for i in range(6) if B>>i&1];need(contacts and set(contacts)<=set(I),'wrong split contact')
 k=contacts[0];i,j=[v for v in I if v!=k];r,s,t=K
 S=[(0,1,t),(0,i,r),(0,j,s),(1,i,s),(1,j,r),(1,9,k)]
 X={(0,1),(1,9),edge(i,r),edge(i,s),edge(j,r),edge(j,s),edge(k,r),edge(0,s),edge(1,s),edge(0,t),edge(1,t),edge(9,k)}
 return S,X,'split_K3_I3'
def main():
 start=time.monotonic();fresh=subprocess.run(['/opt/homebrew/bin/geng','-q','8'],check=True,capture_output=True,text=True).stdout
 domain={}
 for key in fresh.splitlines():
  adj=c.decode(key);iso=[i for i,a in enumerate(adj) if not a]
  if len(iso)<2:continue
  keep=[v for v in range(8) if v not in iso[:2]]
  domain[key]={edge(i,j) for i,j in combinations(range(6),2) if keep[j] in adj[keep[i]]}
 need(len(domain)==156,'core count')
 path=HERE/'tuza_degree8_mixed_codegree6_certificates.json';raw=path.read_bytes();P=json.loads(raw)
 recs={r['key']:r for r in P['records']};exc={r['key']:r for r in P['exceptions']}
 need(len(recs)==151 and len(exc)==5 and set(recs)|set(exc)==set(domain),'classification coverage')
 counts={};total=0
 for key,H in domain.items():
  if key in recs:
   r=recs[key];need(set(map(tuple,r['core_edges']))==H,'wrong core');c.verify(r['packing'],r['cover'],graph(H,63))
  for B in range(64):
   if not c.connected(8,c.side_link(H,B)):continue
   G=graph(H,B)
   if not c.admitted(G):continue
   total+=1
   if key in recs:r=recs[key];S,X,kind=r['packing'],r['cover'],'ordinary_template'
   else:S,X,kind=human(H,B)
   c.verify(S,X,G);counts[kind]=counts.get(kind,0)+1
 out={'pass':True,'core_count':156,'ordinary_templates':151,'human_exception_types':5,
      'admitted_side_models':total,'coverage_counts':counts,'payload_sha256':hashlib.sha256(raw).hexdigest(),'seconds':time.monotonic()-start}
 (HERE/'tuza_degree8_mixed_codegree6_verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
