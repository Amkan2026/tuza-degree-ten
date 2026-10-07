import json,itertools,subprocess,time
from pathlib import Path
from functools import lru_cache
from ortools.sat.python import cp_model
GENG='/opt/homebrew/bin/geng'
def decode(s):
 s=s.strip();n=ord(s[0])-63;bits=[]
 for c in s[1:]:bits.extend((ord(c)-63>>k)&1 for k in range(5,-1,-1))
 es=[];i=0
 for b in range(1,n):
  for a in range(b):
   if bits[i]:es.append((a,b))
   i+=1
 return n,es

def wke(n,es):
 adj=[0]*n
 for a,b in es:adj[a]|=1<<b;adj[b]|=1<<a
 @lru_cache(None)
 def match(mask):
  if not mask:return 0
  lb=mask&-mask;v=lb.bit_length()-1;rest=mask^lb
  z=match(rest);cand=adj[v]&rest
  while cand:
   x=cand&-cand;cand^=x;z=max(z,1+match(rest^x))
  return z
 full=(1<<n)-1
 for k in range(n//2+1):
  for q in itertools.combinations(range(n),k):
   out=full^sum(1<<a for a in q);used=0;r=0;ok=True
   for a,b in es:
    z=(1<<a)|(1<<b)
    if out&z==z:
     if used&z:ok=False;break
     used|=z;r+=1
   if ok and r+match(full^used)>=k:return q
 return None

def pair(n,core,tlim=5):
 es=list(core)+[(a,n) for a in range(n)]+[(a,n+1) for a in range(n)]+[(n,n+1)]
 ed={e:i for i,e in enumerate(es)};ts=[]
 for a,b,c in itertools.combinations(range(n+2),3):
  ee=[(a,b),(a,c),(b,c)]
  if all(e in ed for e in ee):ts.append(tuple(ed[e] for e in ee))
 model=cp_model.CpModel();x=[model.new_bool_var(f'x{i}') for i in range(len(es))];y=[model.new_bool_var(f'y{i}') for i in range(len(ts))]
 use=[[]for _ in es]
 for j,t in enumerate(ts):
  for e in t:use[e].append(y[j])
  if any(n in es[e] or n+1 in es[e] for e in t):model.add(sum(x[e] for e in t)>=1)
 for e in range(len(es)):
  model.add(sum(use[e])<=1)
  if e<len(core):model.add(sum(use[e])<=x[e])
 model.add(sum(x)<=2*sum(y));solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=tlim;solver.parameters.num_search_workers=1
 st=solver.solve(model)
 if st not in [cp_model.FEASIBLE,cp_model.OPTIMAL]:return {'status':solver.status_name(st)}
 return {'status':'PASS','X':[es[i]for i,z in enumerate(x)if solver.value(z)],'S':[[a,b,c]for a,b,c in itertools.combinations(range(n+2),3)if tuple(ed.get(e,-1)for e in [(a,b),(a,c),(b,c)])in []] ,'triangles':[[es[e]for e in ts[i]]for i,z in enumerate(y)if solver.value(z)]}
if __name__=='__main__':
 import sys
 if sys.argv[1]=='wke':
  records=[];fail=[]
  for line in subprocess.check_output([GENG,'-q','9','-c','-D3'],text=True).splitlines():
   n,es=decode(line);q=wke(n,es)
   if q is None:fail.append({'g6':line,'edges':es})
   records.append({'g6':line,'q':q})
  out={'order':9,'count':len(records),'failures':fail,'records':records};Path('work/tuza_degree9_subcubic9_wke.json').write_text(json.dumps(out));print(json.dumps({'count':len(records),'failures':fail}))
 elif sys.argv[1]=='pair':
  n=8;start=time.time();records=[];fails=[]
  lines=subprocess.check_output([GENG,'-q',str(n)],text=True).splitlines()
  for i,line in enumerate(lines):
   _,es=decode(line)
                                                       
   sparse=any(max([sum(a in e and z not in e for e in es)for a in range(n)if a!=z],default=0)<=2 for z in range(n))
   if sparse:r={'status':'SPARSE'}
   else:r=pair(n,es)
   if r['status'] not in ['PASS','SPARSE']:fails.append({'g6':line,'edges':es,'result':r})
   records.append({'g6':line,**r})
   if i%100==0:print(i,len(fails),round(time.time()-start,2),flush=True)
  Path('work/tuza_degree9_common8_pair_probe.json').write_text(json.dumps({'count':len(lines),'failures':fails,'records':records}));print('FINAL',len(lines),len(fails),time.time()-start)
