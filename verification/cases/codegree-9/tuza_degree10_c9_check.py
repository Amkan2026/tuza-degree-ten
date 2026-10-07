                                                                               
                                                                     
   
from pathlib import Path
from itertools import combinations
import subprocess,json,hashlib,time
start=time.time();CORE=Path('work/tuza_degree10_common8_slack2_probe.json');RES=Path('work/tuza_degree10_c9_residual_certificates.json');HUMAN=Path('work/tuza_degree10_c9_dense_human_certificates.json')
def decode(s):
 n=ord(s[0])-63;bits=''.join(format(ord(c)-63,'06b')for c in s[1:]);i=0;E=set()
 for b in range(1,n):
  for a in range(b):
   if bits[i]=='1':E.add((a,b))
   i+=1
 return n,E
def encode(n,E):
 bits=''.join('1'if(a,b)in E else'0'for b in range(1,n)for a in range(b));bits+='0'*((-len(bits))%6)
 return chr(n+63)+''.join(chr(int(bits[i:i+6],2)+63)for i in range(0,len(bits),6))
def canon(lines):return subprocess.check_output(['/opt/homebrew/bin/labelg','-q'],input=''.join(s+'\n'for s in lines),text=True).splitlines()
def literal(E,U,S,X,budget=0):
 X=set(map(tuple,X));assert X<=E and len(X)+budget<=2*len(S);used=set()
 for t in S:
  assert len(t)==len(set(t))==3;es=set(combinations(sorted(t),2));assert es<=E and not es&used;assert all(e in X for e in es if not(set(e)&U));used|=es
 for t in combinations(range(11),3):
  es=set(combinations(t,2))
  if set(t)&U and es<=E:assert es&X

core=json.loads(CORE.read_text());records=core['records'];c8canon=canon([r['g6']for r in records]);assert len(set(c8canon))==len(records)==12346
positive={c for c,r in zip(c8canon,records)if r['status']=='PASS'};negative=set(c8canon)-positive;assert len(positive)==12116 and len(negative)==230
report=json.loads(Path('work/tuza_degree10_c8_core_check.json').read_text());assert report['result']=='PASS'and report['payload_sha256']==hashlib.sha256(CORE.read_bytes()).hexdigest()
parents=Path('work/tuza_degree10_c9_all_graph6.txt').read_text().splitlines();fresh=subprocess.check_output(['/opt/homebrew/bin/geng','-q','9'],text=True).splitlines();assert parents==fresh and len(parents)==len(set(parents))==274668
children=iter(Path('work/tuza_degree10_c9_deleted_canonical_graph6.txt').read_text().splitlines());remaining=[];sparse=[];lifted=0
for key in parents:
 chunk=[next(children)for _ in range(9)];assert all(c in positive or c in negative for c in chunk)
 if any(c in positive for c in chunk):lifted+=1;continue
 _,H=decode(key)
 if any(max((sum(c in e and z not in e for e in H)for c in range(9)if c!=z),default=0)<=2 for z in range(9)):sparse.append(key)
 else:remaining.append(key)
try:next(children)
except StopIteration:pass
else:raise AssertionError('extra child graph')
assert lifted==274429 and len(sparse)==5 and len(remaining)==234
assert remaining==Path('work/tuza_degree10_c9_residual_graph6.txt').read_text().splitlines()
res=json.loads(RES.read_text());assert res['complete']and not res['failures'];assert {r['g6']for r in res['records']}==set(remaining)
pair_count=cut_count=dense_count=0;dense_codes=[]
for r in res['records']:
 assert r['status']=='PASS';n,H=decode(r['g6']);assert n==9;E=H|{(c,h)for c in range(9)for h in(9,10)}|{(9,10)}
 if r['kind']=='dense_human':assert len(H)>=31;dense_count+=1;dense_codes.append(encode(9,set(combinations(range(9),2))-H));continue
 U=set(r['U']);assert {9,10}<=U;budget=sum(8-sum(c in e for e in H)for c in U if c<9);assert budget==r['outside_budget'];literal(E,U,r['S'],r['X'],budget)
 if r['kind']=='pair':assert U=={9,10};pair_count+=1
 else:
  assert r['kind']=='cut';cut_count+=1;assert set(map(tuple,r['X']))=={e for e in E if r['colors'][e[0]]==r['colors'][e[1]]}
human=json.loads(HUMAN.read_text());assert human['complete']and len(human['records'])==45;human_codes=canon([r['g6']for r in human['records']]);assert set(canon(dense_codes))<=set(human_codes)
for r in human['records']:
 _,F=decode(r['g6']);assert F==set(map(tuple,r['missing']));E=set(combinations(range(11),2))-F;assert r['outside_degree_budget']==2*len(F);literal(E,set(range(11)),r['S'],r['X'],r['outside_degree_budget'])
                                                                         
                                                                  
selection=set(remaining+sparse+parents[::997]);g6=[];expected=[]
for key in sorted(selection):
 _,E=decode(key)
 for z in range(9):
  mp={v:i for i,v in enumerate(v for v in range(9)if v!=z)};sub={tuple(sorted((mp[a],mp[b])))for a,b in E if z not in(a,b)};g6.append(encode(8,sub));expected.append((key,z))
independent_children=canon(g6);parent_index={s:i for i,s in enumerate(parents)};all_children=Path('work/tuza_degree10_c9_deleted_canonical_graph6.txt').read_text().splitlines()
assert all(c==all_children[9*parent_index[k]+z]for c,(k,z)in zip(independent_children,expected))
neg=0;sample=next(r for r in res['records']if r['kind']=='pair');_,H=decode(sample['g6']);E=H|{(c,h)for c in range(9)for h in(9,10)}|{(9,10)}
try:literal(E,{9,10},sample['S']+[sample['S'][0]],sample['X'])
except AssertionError:neg+=1
try:assert set(remaining[:-1])=={r['g6']for r in res['records']}
except AssertionError:neg+=1
assert neg==2
out={'result':'PASS','full_common9_types':274668,'lifted_spare_two_types':lifted,'sparse_human_types':len(sparse),'residual_types':len(remaining),'residual_pair_certificates':pair_count,'residual_cut_certificates':cut_count,'residual_dense_human_types':dense_count,'dense_human_missing_graph_types':45,'independent_python_deleted_subgraphs_checked':len(expected),'negative_controls':neg,'core_sha256':hashlib.sha256(CORE.read_bytes()).hexdigest(),'residual_sha256':hashlib.sha256(RES.read_bytes()).hexdigest(),'human_sha256':hashlib.sha256(HUMAN.read_bytes()).hexdigest(),'seconds':time.time()-start};Path('work/tuza_degree10_c9_verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
