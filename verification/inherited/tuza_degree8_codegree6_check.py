                                                                    

                                                                           
                                                                               
                                                                               
   
from pathlib import Path
from itertools import combinations
import json,hashlib,subprocess,time
HERE=Path(__file__).resolve().parent

def need(c,m):
 if not c:raise AssertionError(m)
def edge(a,b):return tuple(sorted((a,b)))
def decode(g):
 data=[ord(x)-63 for x in g];n=data[0];adj=[set() for _ in range(n)];k=0
 for j in range(1,n):
  for i in range(j):
   if data[1+k//6]>>(5-k%6)&1:adj[i].add(j);adj[j].add(i)
   k+=1
 return adj
def connected(n,E):
 seen={0};todo=[0]
 while todo:
  v=todo.pop()
  for a,b in E:
   if v not in (a,b):continue
   w=b if a==v else a
   if w not in seen:seen.add(w);todo.append(w)
 return len(seen)==n
LE=list(combinations(range(8),2));LI={e:i for i,e in enumerate(LE)}
def matchings(vs):
 if not vs:yield 0,0;return
 v,*rest=vs
 yield from matchings(rest)
 for i,w in enumerate(rest):
  for m,k in matchings(rest[:i]+rest[i+1:]):yield m|(1<<LI[edge(v,w)]),k+1
ALLMATCH=sorted(matchings(list(range(8))),key=lambda mk:-mk[1]);need(len(ALLMATCH)==764,'matching count')
OUTSIDE=[sum(1<<i for i,(a,b) in enumerate(LE) if not(q>>a&1 or q>>b&1)) for q in range(256)]
def wke(E):
 G=sum(1<<LI[e] for e in E)
 allowed=[(m,k) for m,k in ALLMATCH if m&~G==0]
 for q in range(256):
  k=q.bit_count()
  if k>4:continue
  F=G&OUTSIDE[q]
  if any(ms>=k and F&~M==0 for M,ms in allowed):return True
 return False
def side_link(H,mask):
 return H|{(i,6) for i in range(6)}|{(i,7) for i in range(6) if mask>>i&1}
def graph(H,a,b):
 return {edge(x+2,y+2) for x,y in H}|{(0,1),(0,8),(1,9)}|{(h,c) for h in (0,1) for c in range(2,8)}|{(c+2,8) for c in range(6) if a>>c&1}|{(c+2,9) for c in range(6) if b>>c&1}
def admitted(G):
 adj=[set() for _ in range(10)]
 for a,b in G:adj[a].add(b);adj[b].add(a)
 return max(map(len,adj))<=8 and all(len(adj[a]&adj[b])<=6 for a,b in G)
def verify(S,X,G):
 X=set(map(tuple,X));need(X<=G,'absent cover edge');used=set()
 for t in S:
  need(len(t)==3 and len(set(t))==3,'malformed triangle')
  es={edge(a,b) for a,b in combinations(t,2)}
  need(es<=G,'absent packed edge');need(not es&used,'packing collision');used|=es
 need(len(X)<=2*len(S),'budget failed')
 for t in combinations(range(10),3):
  if 0 not in t and 1 not in t:continue
  es=set(combinations(t,2))
  if es<=G:need(bool(es&X),'unhit hub triangle')
 need(all(e in X for e in used if 0 not in e and 1 not in e),'uncovered outside packed edge')

def fano(u,v,K):
 i,j,k,l,m=K
 return [(u,v,i),(u,j,k),(u,l,m),(v,j,l),(v,k,m),(i,j,m),(i,k,l)]
def human(H,a,b):
 K5zs=[z for z in range(6) if all(e in H for e in combinations([i for i in range(6) if i!=z],2))]
 if K5zs:
  z=next((z for z in K5zs if (a|b)>>z&1),K5zs[0]);K=[i+2 for i in range(6) if i!=z];zz=z+2
  S=fano(0,1,K);base=set(combinations(K,2))|{(0,1),(0,8),(1,9)}
  if (a|b)>>z&1:
   h,w=(0,8) if a>>z&1 else (1,9)
   return S+[(h,w,zz)],base|{edge(0,zz),edge(1,zz),edge(w,zz)},'augmented_Fano'
  D=[i+2 for i in range(6) if edge(i,z) in H];E=[i for i in K if i not in D]
  if len(D)<=1:return S,base|{edge(zz,d) for d in D},'small_z_Fano'
  A={i+2 for i in range(6) if a>>i&1};B={i+2 for i in range(6) if b>>i&1}
  need(A<=set(E) and B<=set(E),'bad K5 contact domain')
  u,v,aa,bb=0,1,8,9
  if len(D)==2:
   need(len(A)==len(B)==2 and len(A&B)==1,'bad degree-two contacts')
   r=next(iter(A&B));p=next(iter(A-B));q=next(iter(B-A));s,t=D
   S=[(u,v,p),(u,r,aa),(u,zz,t),(u,q,s),(v,r,q),(v,s,t)]
   X=[(u,p),(u,s),(u,t),(v,r),(v,zz),(v,p),(v,q),(r,q),(r,aa),(zz,t),(q,s),(s,t)]
   kind='K5_z2'
  else:
   need(len(D)==3,'unhandled degree of z')
   if len(A)==2:u,v,aa,bb=1,0,9,8;A,B=B,A
   need(len(A)==1 and B and len(A&B)<=1,'bad degree-three contacts')
   r=next(iter(A));p=next(i for i in E if i!=r);q,s,t=D
   if B==A:
    S=[(u,v,r),(u,zz,q),(u,p,s),(v,zz,s),(v,p,q)]
    X=[(u,v),(u,r),(u,t),(v,r),(v,t),(zz,q),(zz,s),(p,q),(p,s),(q,s)];kind='K5_z3_same'
   elif len(B)==1:
    S=[(u,v,q),(u,r,aa),(v,r,t),(v,zz,s),(v,p,bb),(r,p,s)]
    X=[(u,v),(u,q),(u,t),(v,q),(v,t),(r,p),(r,s),(r,t),(r,aa),(zz,s),(p,s),(p,bb)];kind='K5_z3_distinct'
   else:
    S=[(u,v,r),(u,zz,s),(u,p,q),(v,zz,t),(v,p,bb),(p,s,t)]
    X=[(u,v),(u,r),(u,q),(v,r),(v,q),(zz,s),(zz,t),(p,q),(p,s),(p,t),(p,bb),(s,t)];kind='K5_z3_full'
  return S,{edge(*e) for e in X},kind
 missing=set(combinations(range(6),2))-H
 if len(missing)==2 and len({v for e in missing for v in e})==4:
  (i,j),(k,l)=sorted(missing);r,s=sorted(set(range(6))-{i,j,k,l});i,j,k,l,r,s=[x+2 for x in (i,j,k,l,r,s)]
  S=[(i,k,r),(j,l,s),(0,i,l),(1,j,k),(1,i,s),(0,j,r),(0,k,s),(1,l,r)]
  X={edge(x+2,y+2) for x,y in H}|{(0,1),(0,8),(1,9)}
  return S,X,'K6_minus_2_matching'
 return None

def main():
 start=time.monotonic();fresh=subprocess.run(['/opt/homebrew/bin/geng','-q','8'],check=True,capture_output=True,text=True).stdout
 domain={}
 for key in fresh.splitlines():
  adj=decode(key);iso=[i for i,a in enumerate(adj) if not a]
  if len(iso)<2:continue
  keep=[v for v in range(8) if v not in iso[:2]]
  domain[key]={edge(i,j) for i,j in combinations(range(6),2) if keep[j] in adj[keep[i]]}
 need(len(domain)==156,'six-core domain incomplete')
 path=HERE/'tuza_degree8_codegree6_template_certificates.json';raw=path.read_bytes();P=json.loads(raw)
 basic={r['key']:r for r in P['basic_core_records']};extra={(r['key'],r['left_mask'],r['right_mask']):r for r in P['augmented_pair_records']}
 need(len(basic)==len(P['basic_core_records'])==120,'basic duplicate or count')
 need(len(extra)==len(P['augmented_pair_records'])==5629,'augmented duplicate or count')
 need(set(basic)<=set(domain),'unknown basic core')
 for key,r in basic.items():need(set(map(tuple,r['core_edges']))==domain[key],'basic core mismatch')
 usedextra=set();counts={};total=0
 for key,H in domain.items():
  sides=[mask for mask in range(64) if connected(8,side_link(H,mask)) and not wke(side_link(H,mask))]
  for a in sides:
   for b in sides:
    if b<a:continue
    G=graph(H,a,b)
    if not admitted(G):continue
    total+=1
    if key in basic:
     r=basic[key];S,X,kind=r['packing'],r['cover'],'ordinary_template'
    elif (key,a,b) in extra:
     usedextra.add((key,a,b));r=extra[key,a,b];S,X,kind=r['packing'],r['cover'],'augmented_template'
    else:
     ans=human(H,a,b);need(ans is not None,'uncovered local model');S,X,kind=ans
    verify(S,X,G);verify(S,X,G|{(8,9)})
    counts[kind]=counts.get(kind,0)+1
 need(usedextra==set(extra),'extra record outside actual domain')
                                                         
 sample=next(iter(extra.values()));H=domain[sample['key']];G=graph(H,sample['left_mask'],sample['right_mask'])
 for badS,badX in [(sample['packing']+sample['packing'][:1],sample['cover']),(sample['packing'],[])]:
  try:verify(badS,badX,G)
  except AssertionError:pass
  else:raise AssertionError('hostile literal mutation accepted')
 out={'pass':True,'fresh_six_core_count':len(domain),'basic_cores':len(basic),'augmented_records':len(extra),
      'admitted_unordered_pairs':total,'AB_extension_checks':2*total,'coverage_counts':counts,
      'mutation_controls':2,'payload_sha256':hashlib.sha256(raw).hexdigest(),'seconds':time.monotonic()-start}
 (HERE/'tuza_degree8_codegree6_verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
