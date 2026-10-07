                                                                           
from itertools import combinations
from pathlib import Path
import subprocess,json
BASE=json.loads(Path('work/tuza_degree10_K11_seventeen.json').read_text());S0=list(map(tuple,BASE['S']));L0=set(map(tuple,BASE['leave']));E11=set(combinations(range(11),2));cycles=[]
for Q in combinations(range(11),4):
 a,b,c,d=Q
 for cy in [(a,b,c,d),(a,b,d,c),(a,c,b,d)]:
  L={tuple(sorted((cy[i],cy[(i+1)%4])))for i in range(4)};cycles.append((cy,L))
def decode(line):
 n=ord(line[0])-63;bits=''.join(format(ord(x)-63,'06b')for x in line[1:]);E=set();i=0
 for b in range(1,n):
  for a in range(b):
   if bits[i]=='1':E.add((a,b))
   i+=1
 return n,E
def transformed(cy,T=None):
 for direction in [1,-1]:
  for shift in range(4):
   mp={i:cy[(shift+direction*i)%4]for i in range(4)}
   possibilities=[None]if T is None else[t for t in S0 if {mp[x]for x in t if x<4}==set(T)&set(cy)]
   for source in possibilities:
    p=mp.copy()
    if source is not None:
     p.update(zip(sorted(x for x in source if x>=4),sorted(set(T)-set(cy))))
    p.update(zip(sorted(set(range(11))-set(p)),sorted(set(range(11))-set(p.values()))))
    S=[tuple(sorted(p[x]for x in t))for t in S0]
    if T is None or tuple(sorted(T))in S:return S
 return None
records=[]
for line in subprocess.check_output(['/opt/homebrew/bin/geng','-q','9','0:5'],text=True).splitlines():
 n,F=decode(line);assert n==9;r=len(F);found=None
 for cy,L in cycles:
  q=len(F&L)
  if q>=min(2,r) and r<=4 or r==5 and q>=3:
   S=transformed(cy);found=(S,cy,None);break
  if r==5 and q>=2:
   for f,g in combinations(F-L,2):
    T=set(f)|set(g)
    if len(T)==3 and not(set(combinations(sorted(T),2))&L):
     S=transformed(cy,T)
     if S is not None:found=(S,cy,sorted(T));break
   if found:break
 assert found is not None,(line,sorted(F))
 S,cy,T=found;S=[t for t in S if not(set(combinations(t,2))&F)]
 used=[e for t in S for e in combinations(t,2)];assert len(used)==len(set(used))and set(used)<=E11-F
 part=next(set(A)for A in combinations(range(11),5)if all(set(e)<=set(A)or set(e).isdisjoint(A)for e in F))
 X={e for e in E11-F if set(e)<=part or set(e).isdisjoint(part)};assert len(X)==25-r
 assert len(X)+2*r<=2*len(S)
 records.append({'g6':line,'missing':sorted(F),'S':S,'X':sorted(X),'cut_class':sorted(part),'leave_cycle':cy,'forced_triangle':T,'outside_degree_budget':2*r})
counts={r:sum(len(x['missing'])==r for x in records)for r in range(6)}
                                                                        
                                                 
orbits=set(len(set(t)&set(range(4)))for t in S0);assert orbits=={0,1,2}
assert all(len(set(t)&set(range(4)))<=2 for t in combinations(range(11),3)if not(set(combinations(t,2))&L0))
Path('work/tuza_degree10_c9_dense_human_certificates.json').write_text(json.dumps({'records':records,'core_counts_by_missing_edges':counts,'complete':True},indent=2));print(json.dumps({'types':len(records),'core_counts_by_missing_edges':counts,'min_packing':min(len(x['S'])for x in records),'result':'PASS'},indent=2))
