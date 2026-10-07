                                                                           
from pathlib import Path
from itertools import combinations,permutations
import json
from tuza_degree10_c4_density_independent_verify import core_edges,side_edges,pair_base,side_to_pair,edge,CP,image_core,adjacency
HERE=Path('work');P=json.loads((HERE/'tuza_degree10_c4_all_sides.json').read_text());sources={}
for nl,nr,file in [(7,7,'degree8_unrestricted_codegree4_certificates.json'),(7,8,'degree8_mixed_c4_discovery.json'),(8,8,'degree8_eight_eight_c4_discovery.json')]:
 q=json.loads((HERE/file).read_text());rows={}
 for r in q['records']:
  key=tuple(r['key'])if 'key'in r else(r['core_mask'],r['left_side_mask'],r['right_side_mask'])
  rows[key]=r
 sources[nl,nr]=rows

def old_mask(n,F,cp,ap):
 old=tuple(edge(a,c)for a in range(4,n-1)for c in range(4))+tuple(combinations(range(4,n-1),2));ix={e:j for j,e in enumerate(old)}
 mp=dict(enumerate(cp))|dict(zip(range(4,n-1),ap))
 return sum(1<<ix[edge(mp[a],mp[b])]for a,b in F)

def literal(E,n,S,X):
 X=set(map(tuple,X));assert X<=E and len(X)<=2*len(S);used=[]
 for t in S:
  F={edge(a,b)for a,b in combinations(t,2)};assert len(set(t))==3 and F<=E and all(set(e)&{0,1}or e in X for e in F);used.extend(F)
 assert len(used)==len(set(used))
 for t in combinations(range(n),3):
  F={edge(a,b)for a,b in combinations(t,2)}
  if set(t)&{0,1}and F<=E:assert F&X
reports=[]
for nl,nr in sources:
 counts=0;robust=0;types=set()
 for hs,left in P[str(nl)]['core_sides'].items():
  h=int(hs);right=P[str(nr)]['core_sides'].get(hs,[]);autos=[p for p in CP if image_core(h,p)==h]
  for i,l in enumerate(left):
   LF=side_edges(nl,l)
   for j,r in enumerate(right):
    if nl==nr and j<i:continue
    E=pair_base(nl,nr,h)|{side_to_pair(e,nl,0)for e in LF}|{side_to_pair(e,nl,1)for e in side_edges(nr,r)};D=adjacency(E)
    if any(len(D[a]&D[b])>4 for a,b in E):continue
    assert max(map(len,D.values()))<=8
    counts+=1;keys=[]
    for p in autos:
     li=[old_mask(nl,LF,p,a)for a in permutations(range(4,nl-1))]
     ri=[old_mask(nr,side_edges(nr,r),p,a)for a in permutations(range(4,nr-1))]
     keys.extend((h,*sorted((a,b)))if nl==nr else(h,a,b)for a in li for b in ri)
    key=min(keys);assert key in sources[nl,nr],(nl,nr,key)
    rec=sources[nl,nr][key];types.add(key)
                                                                     
    oldpot=lambda n:tuple(edge(a,c)for a in range(4,n-1)for c in range(4))+tuple(combinations(range(4,n-1),2))
    G=pair_base(nl,nr,key[0])
    for side,n,m in [(0,nl,key[1]),(1,nr,key[2])]:G|={side_to_pair(e,nl,side)for k,e in enumerate(oldpot(n))if m>>k&1}
    if 'packing'in rec:literal(G,nl+nr-4,rec['packing'],rec['cover'])
    else:
     assert nl==nr==8
     DD=adjacency(G);assert any(DD[c]=={0,1}for c in range(2,6))
                                                                      
                                                                   
     robust+=1
 reports.append({'degrees':[nl,nr],'admitted_canonical_side_pairs':counts,'source_orbits_used':len(types),'robustness_exclusions':robust})
report={'result':'PASS','reports':reports,'ambient_maximum_degree_not_used_in_literal_reducers':True,'sole_old_larger_removed_set_excluded_by_maximum_codegree_four':True}
(HERE/'tuza_degree10_c4_old_transfer_verified.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
