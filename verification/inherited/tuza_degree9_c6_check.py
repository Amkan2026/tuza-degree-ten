import itertools,json,subprocess,time,hashlib
from pathlib import Path
from functools import lru_cache
import numpy as np
GENG='/opt/homebrew/bin/geng'
def decode(s):
 n=ord(s[0])-63;bits=''.join(format(ord(c)-63,'06b')for c in s[1:]);z=0;H=set()
 for b in range(1,n):
  for a in range(b):
   if bits[z]=='1':H.add((a,b))
   z+=1
 return n,H

def variables(k,first):return[(a,first+j)for j in range(k)for a in range(6)]+([(first,first+1)]if k==2 else[])
def graph(H,sa,sb,p,q):
 E=set(H)|{(a,6)for a in range(6)}|{(a,7)for a in range(6)}|{(6,7)}|{(6,8+j)for j in range(sa)}|{(7,10+j)for j in range(sb)}
 E|={e for bit,e in enumerate(variables(sa,8))if p>>bit&1};E|={e for bit,e in enumerate(variables(sb,10))if q>>bit&1};return E

def pack(S,E,U,X):
 used=set()
 for t in S:
  assert len(set(t))==3;es=set(itertools.combinations(sorted(t),2));assert es<=E and not used&es
  assert all(e in X for e in es if not set(e)&U);used|=es

def cover_hubs(E,X):
 for t in itertools.combinations(range(12),3):
  if 6 not in t and 7 not in t:continue
  es=set(itertools.combinations(t,2));assert not es<=E or bool(es&X)

def literal_core(H,r,k):
 E=graph(H,0,0,0,0);X={tuple(e)for e in r['X']};assert X<=E;pack(r['S'],E,{6,7},X);cover_hubs(E,X);assert len(X)+k<=2*len(r['S'])

def literal_pair(H,r):
 sa=r['sa'];E=graph(H,sa,2,r['p'],r['q']);X={tuple(e)for e in r['X']};assert X<=E;pack(r['S'],E,{6,7},X);cover_hubs(E,X);assert len(X)<=2*len(r['S'])
                                                                   
 a,f,b,g=interval(r['S'],X,sa)
 upper=graph(H,sa,2,((1<<len(variables(sa,8)))-1)^f,8191^g);lower=graph(H,sa,2,a,b)
 assert X<=upper;pack(r['S'],lower,{6,7},X);cover_hubs(upper,X)

def interval(S,X,sa):
 lo=[];forbidden=[]
 for W,u in[(variables(sa,8),6),(variables(2,10),7)]:
  a=f=0
  for bit,e in enumerate(W):
   if any(set(e)<=set(t)for t in S):a|=1<<bit
   if e not in X and all(tuple(sorted((u,x)))not in X for x in e):f|=1<<bit
  assert not a&f;lo.append(a);forbidden.append(f)
 return(lo[0],forbidden[0],lo[1],forbidden[1])

def literal_cut(H,r):
 E=graph(H,2,2,r['p'],r['q']);colors=[r['cut_mask']>>a&1 for a in range(8)]+[0,0,1,1];X={e for e in E if colors[e[0]]==colors[e[1]]};assert X=={tuple(e)for e in r['X']}
 U=set(r['U']);assert {6,7}<=U<=set(range(8));pack(r['S'],E,U,X);outside=sum(9-sum(a in e for e in E)for a in U if a<6);assert outside>=0 and outside==r['outside_bound'];assert len(X)+outside<=2*len(r['S'])
                                                                 
 assert all(colors[a]!=colors[b]for a in[8,9]for b in[10,11])

def swap(p):return((p&63)<<6)|((p>>6)&63)|(p&4096)
def legal(H,k):
 d=[sum(a in e for e in H)for a in range(6)];ce={e:sum(tuple(sorted((e[0],z)))in H and tuple(sorted((e[1],z)))in H for z in range(6)if z not in e)for e in H};ans=[]
 for p in range(1<<(6*k+(k==2))):
  ds=[p>>(6*j)&63 for j in range(k)];aa=int(bool(p&4096))if k==2 else 0
  if aa:
   if not any(ds):continue
  elif any(not z for z in ds):continue
  if any(z.bit_count()+aa>6 for z in ds):continue
  if any(d[a]+sum(z>>a&1 for z in ds)>5 for a in range(6)):continue
  if any(2+c+sum(int(bool(z>>a&1 and z>>b&1))for z in ds)>6 for(a,b),c in ce.items()):continue
  ans.append(p)
 return np.array(ans,dtype=np.uint16)

def classification(H,row):
 k=row['size'];P=legal(H,k);base=set(H)|{(a,6)for a in range(6)};V=variables(k,7);wk=np.zeros(len(P),dtype=bool)
 for w in row['wke_intervals']:
  Q=set(w['Q']);M={tuple(e)for e in w['M']};lo=w['lo'];f=w['forbidden'];flat=[a for e in M for a in e];assert len(flat)==len(set(flat))and len(Q)<=len(M)
  low=base|{e for bit,e in enumerate(V)if lo>>bit&1};assert M<=low
  assert all(e in M for e in base if not set(e)&Q)
  assert all(f>>bit&1 for bit,e in enumerate(V)if not set(e)&Q and e not in M)
  wk|=(P&lo==lo)&(P&f==0)
 mins=row['minimum_patterns'];up=np.zeros(len(P),dtype=bool)
 for p in mins:
  up|=P&p==p
  if k==2:up|=P&swap(p)==swap(p)
 assert np.all(wk|up),(row['g6'],k)
 return P[~wk],mins

def iwke(n,E):
 A=[set()for _ in range(n)]
 for a,b in E:A[a].add(b);A[b].add(a)
 @lru_cache(None)
 def mm(W):
  if not W:return 0
  a=W[0];v=mm(W[1:])
  for b in A[a]&set(W):v=max(v,1+mm(tuple(z for z in W if z not in[a,b])))
  return v
 for q in range(1<<n):
  if q.bit_count()>n//2:continue
  Q={a for a in range(n)if q>>a&1};F=[e for e in E if not set(e)&Q];flat=[a for e in F for a in e]
  if len(flat)!=len(set(flat)):continue
  if len(F)+mm(tuple(a for a in range(n)if a not in flat))>=len(Q):return True
 return False

def automorphisms(H):
 d=[sum(a in e for e in H)for a in range(6)];out=[]
 for p in itertools.permutations(range(6)):
  if any(d[a]!=d[p[a]]for a in range(6)):continue
  if{tuple(sorted((p[a],p[b])))for a,b in H}==H:out.append(p)
 return out

def transformed(r,autos):
 sa=r['sa'];huboptions=[False,True]if sa==2 else[False];out=[]
 for a in autos:
  for h in huboptions:
   for swA in([False,True]if sa==2 else[False]):
    for swB in[False,True]:
     p=list(range(12));p[:6]=a;p[6],p[7]=(7,6)if h else(6,7)
     for j in range(sa):p[8+j]=(10 if h else 8)+(1-j if swA else j)
     for j in range(2):p[10+j]=(8 if h else 10)+(1-j if swB else j)
     S=[tuple(sorted(p[x]for x in t))for t in r['S']];X={tuple(sorted(p[x]for x in e))for e in r['X']}
     if r.get('kind')in['core_cut','subset_cut']:
      col0=[r['cut_mask']>>x&1 for x in range(8)]+[0,0,1,1];cols=[0]*12
      for x,y in enumerate(p):cols[y]=col0[x]^int(h)
      out.append((S,X,cols,{p[z]for z in r['U']if z<6}))
     else:out.append(interval(S,X,sa))
 return out

def bits(v):return int.from_bytes(np.packbits(v,bitorder='little').tobytes(),'little')
def pc(v):return np.array([int(z).bit_count()for z in v],dtype=np.int16)
def pair_cover_family(r,autos,P,Q,covered,H):
 for a,f,b,g in set(transformed(r,autos)):
  rows=np.flatnonzero((P&a==a)&(P&f==0));q=bits((Q&b==b)&(Q&g==0))
  for i in rows:covered[int(i)]|=q

def cut_cover_family(r,autos,P,covered,H):
 seen=set();base=graph(H,2,2,0,0);aa=(P&4096>0).astype(np.int16)
 for S,X,c,Z in transformed(r,autos):
  a,_,b,_=interval(S,X,2);weights=[]
  for W in[variables(2,8),variables(2,10)]:
   pos=neg=0
   for bit,(v,w)in enumerate(W):
    if v>=6:continue
    coeff=int(c[v]==c[w])-int(v in Z)
    if coeff==1:pos|=1<<bit
    if coeff==-1:neg|=1<<bit
   weights.append((pos,neg))
  pa,na=weights[0];pb,nb=weights[1];C=sum(c[u]==c[v]for u,v in base)+sum(7-sum(z in e for e in H)for z in Z);key=(a,b,pa,na,pb,nb,C)
  if key in seen:continue
  seen.add(key);PA=P&a==a;QB=P&b==b;left=C+pc(P&pa)-pc(P&na)+aa;right=pc(P&pb)-pc(P&nb)+aa
  for val in np.unique(left[PA]):
   q=bits(QB&(val+right<=2*len(S)))
   for i in np.flatnonzero(PA&(left==val)):covered[int(i)]|=q

def permitted(H,P,Q,unordered=False):
 constraints=[]
 for a,b in H:
  common=sum(tuple(sorted((a,z)))in H and tuple(sorted((b,z)))in H for z in range(6)if z not in[a,b]);t=4-common
  if t>=4:continue
  def cc(p):return int(bool(p>>a&1 and p>>b&1))+int(bool(p>>(a+6)&1 and p>>(b+6)&1))
  constraints.append((t,np.array([cc(int(p))for p in P],dtype=np.uint8),np.array([cc(int(q))for q in Q],dtype=np.uint8)))
 rows=[]
 for i in range(len(P)):
  ok=np.ones(len(Q),dtype=bool)
  if unordered:ok&=Q>=P[i]
  for t,aa,bb in constraints:ok&=aa[i]+bb<=t
  rows.append(bits(ok))
 return rows

if __name__=='__main__':
 start=time.time();paths=['work/tuza_degree9_c6_core_spare_certificates.json','work/tuza_degree9_c6_minimal_domain.json','work/tuza_degree9_c6_monotone_certificates.json','work/tuza_degree9_c6_full_combined_certificates.json','work/tuza_degree9_c6_side_classification_full_intervals.json'];files=[json.loads(Path(p).read_text())for p in paths];core,dom,fixed,full,clas=files;assert not full['failures'];fresh=set(subprocess.check_output([GENG,'-q','6'],text=True).splitlines());assert len(fresh)==156
 assert{r['g6']for r in core['records']}==fresh=={r['g6']for r in dom['records']};ct={r['g6']:r for r in core['records']};cl={(r['g6'],r['size']):r for r in clas['records']};Htypes={key:decode(key)[1]for key in fresh};allcert=fixed['records']+full['records'];certby={}
 for r in allcert:
  H=Htypes[r['g6']]
  if r.get('kind')in['core_cut','subset_cut']:literal_cut(H,r)
  else:literal_pair(H,r)
  certby.setdefault((r['g6'],r['lane']),[]).append(r)
 hard={r['g6']for r in fixed['failures']};stats={'7/9_minimal_models':0,'8/9_minimal_models':0,'9/9_minimal_models':0,'9/9_full_models':0,'core_certificates':0,'wke_intervals':clas['intervals']};fullcounts=[]
 for idx,key in enumerate(sorted(fresh)):
  H=Htypes[key];au=automorphisms(H);candidate={};mins={}
  for k in[1,2]:candidate[k],mins[k]=classification(H,cl[key,k])
  for label,sa,k in[('7/9',0,2),('8/9',1,3),('9/9',2,4)]:
   cr=ct[key]['certificates'][str(k)]
   if cr['status']=='PASS':literal_core(H,cr,k);stats['core_certificates']+=1;continue
   if sa==0:
    if iwke(7,set(H)|{(a,6)for a in range(6)}):continue
    P=np.array([0],dtype=np.uint16)
   else:P=np.array(mins[sa],dtype=np.uint16)
   Q=np.array(mins[2],dtype=np.uint16);usefull=sa==2 and key in hard
   if usefull:P=Q=np.array(sorted({min(int(p),swap(int(p)))for p in candidate[2]}),dtype=np.uint16)
   allowed=permitted(H,P,Q,unordered=sa==2);covered=[0]*len(P)
   for r in certby.get((key,label),[]):
    if r.get('kind')in['core_cut','subset_cut']:cut_cover_family(r,au,P,covered,H)
    else:pair_cover_family(r,au,P,Q,covered,H)
   assert all(not(a&~c)for a,c in zip(allowed,covered)),(key,label,sum((a&~c).bit_count()for a,c in zip(allowed,covered)))
   count=sum(a.bit_count()for a in allowed)
   if usefull:stats['9/9_full_models']+=count;fullcounts.append({'g6':key,'models':count})
   else:stats[label+'_minimal_models']+=count
  if idx%20==0:print('checked',idx,round(time.time()-start,1),flush=True)
                                                                                                
 neg=0;r=json.loads(json.dumps(fixed['records'][0]));r['X']=[]
 try:literal_pair(Htypes[r['g6']],r)
 except AssertionError:neg+=1
 r=json.loads(json.dumps(fixed['records'][0]));r['S'][0]=[6,8,10]
 try:literal_pair(Htypes[r['g6']],r)
 except AssertionError:neg+=1
 assert neg==2
 stats.update({'status':'PASS','core_types':156,'fixed_spoke_contact_templates':len(fixed['records']),'additional_contact_templates':sum(r.get('kind')not in['core_cut','subset_cut']for r in full['records']),'full_core_cut_templates':sum(r.get('kind')in['core_cut','subset_cut']for r in full['records']),'negative_controls':neg,'seconds':time.time()-start,'payload_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in paths},'full_domain_counts':fullcounts})
 Path('work/tuza_degree9_c6_verified.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats))
