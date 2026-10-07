                                                                           

                                                                
   
from pathlib import Path
from itertools import combinations,permutations
from functools import lru_cache
import subprocess,json,hashlib,time
import numpy as np
HERE=Path('work');start=time.monotonic();CE=tuple(combinations(range(4),2));CP=tuple(permutations(range(4)));AP=tuple(permutations(range(5)))
SE=tuple((c,a)for c in range(4)for a in range(4,9))+tuple(combinations(range(4,9),2));SI={e:i for i,e in enumerate(SE)};CI={e:i for i,e in enumerate(CE)}
def edge(a,b):return tuple(sorted((a,b)))
def decode(line):
 assert ord(line[0])-63==10
 A=[set()for _ in range(10)];k=0
 for b in range(1,10):
  for a in range(b):
   if(ord(line[1+k//6])-63)>>(5-k%6)&1:A[a].add(b);A[b].add(a)
   k+=1
 return A

def literal(A,Q,M):
 assert 0<=Q<1024
 E=tuple(combinations(range(10),2));used=set();count=0
 for j,(a,b)in enumerate(E):
  if M>>j&1:
   assert b in A[a]and a not in used and b not in used
   used|={a,b};count+=1
  elif b in A[a]:assert Q>>a&1 or Q>>b&1
 assert Q.bit_count()<=count

def outside_wke(A):
 @lru_cache(None)
 def maximum(mask):
  if not mask:return 0
  v=(mask&-mask).bit_length()-1;rest=mask^(1<<v);best=maximum(rest)
  for w in A[v]:
   if rest>>w&1:best=max(best,1+maximum(rest^(1<<w)))
  return best
 for Q in range(1024):
  k=Q.bit_count()
  if k>5:continue
  W=set(range(10))-{i for i in range(10)if Q>>i&1};forced=set();good=True;num=0
  for v in W:
   N=A[v]&W
   if len(N)>1:good=False;break
   if N:forced.add(v);num+=1
  if good and num//2+maximum(sum(1<<v for v in set(range(10))-forced))>=k:return False
 return True

fresh=subprocess.run(['/opt/homebrew/bin/geng','-q','-c','-D4','10'],capture_output=True,text=True,check=True).stdout.splitlines()
rows=(HERE/'tuza_degree10_c4_wke_witnesses.txt').read_text().splitlines()
assert len(fresh)==len(rows)==89402
bad=[];wke=0
for expected,row in zip(fresh,rows):
 line,qs,ms=row.split();assert line==expected;Q=int(qs);M=int(ms);A=decode(line)
 assert max(map(len,A))<=4
 if Q==-1:assert outside_wke(A);bad.append(line)
 else:literal(A,Q,M);wke+=1
assert len(bad)==262 and bad==(HERE/'tuza_degree10_nonwke_link4.g6').read_text().splitlines()
                                                           
weights=np.empty((24,120,30),dtype=np.uint32)
core_weights=np.empty((24,6),dtype=np.uint32)
for j,p in enumerate(CP):
 for k,(a,b)in enumerate(CE):core_weights[j,k]=1<<CI[edge(p[a],p[b])]
 for q,ap in enumerate(AP):
  mp={i:p[i]for i in range(4)}|{a+4:b+4 for a,b in enumerate(ap)}
  for k,(a,b)in enumerate(SE):weights[j,q,k]=1<<SI[edge(mp[a],mp[b])]
rooted={};roots=0
for line in bad:
 A=decode(line)
 for v in range(10):
  if len(A[v])!=4:continue
  roots+=1;labels=sorted(A[v])+sorted(set(range(10))-{v}-A[v])
  hc=[k for k,(a,b)in enumerate(CE)if labels[b]in A[labels[a]]]
  si=[k for k,(a,b)in enumerate(SE)if labels[b]in A[labels[a]]]
  images=core_weights[:,hc].sum(axis=1,dtype=np.uint32)if hc else np.zeros(24,dtype=np.uint32)
  h=int(images.min());all_side=weights[:,:,si].sum(axis=2,dtype=np.uint32)if si else np.zeros((24,120),dtype=np.uint32)
  for j in np.flatnonzero(images==h):rooted.setdefault(h,set()).add(int(all_side[j].min()))
P=json.loads((HERE/'tuza_degree10_c4_all_sides.json').read_text())['10']
assert list(map(list,SE))==P['side_edges']
claimed={int(h):set(ms)for h,ms in P['core_sides'].items()}
assert rooted==claimed
(HERE/'tuza_degree10_c4_side_direct10.txt').write_text(''.join(f'{h} {m}\n'for h,ms in sorted(rooted.items())for m in sorted(ms)))
                                                                     
wrong={h:set(ms)for h,ms in claimed.items()};h=next(iter(wrong));wrong[h].pop();assert wrong!=rooted
                                                                                 
control=False
for row in rows:
 line,qs,ms=row.split()
 if int(qs)>0:
  try:literal(decode(line),int(qs),0)
  except AssertionError:control=True;break
assert control
report={'result':'PASS','fresh_graph_types':len(fresh),'literal_WKE_witnesses':wke,'nonWKE_types':len(bad),'degree_four_roots':roots,'rooted_side_counts':{str(h):len(ms)for h,ms in sorted(rooted.items())},'rooted_sides':sum(map(len,rooted.values())),'negative_controls':2,'source_sha256':hashlib.sha256((HERE/'tuza_degree10_c4_all_sides.json').read_bytes()).hexdigest(),'seconds':time.monotonic()-start}
(HERE/'tuza_degree10_c4_side_independent_verified.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
