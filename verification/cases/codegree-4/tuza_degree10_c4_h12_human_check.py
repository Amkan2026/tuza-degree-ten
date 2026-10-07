                                                                       
from itertools import combinations,permutations
from pathlib import Path
import json

def edge(a,b):return tuple(sorted((a,b)))
CE=tuple(combinations(range(4),2))
SE=tuple((c,a)for c in range(4)for a in range(4,8))+tuple(combinations(range(4,8),2))
def graph(key):
    h,l,r=key
    E={(0,1)}|{edge(z,c+2)for z in (0,1)for c in range(4)}|{(0,a)for a in range(6,10)}|{(1,b)for b in range(10,14)}
    E|={(a+2,b+2)for i,(a,b)in enumerate(CE)if h>>i&1}
    for m,offset in ((l,6),(r,10)):
        mp={**{i:i+2 for i in range(4)},**{i:i+offset-4 for i in range(4,8)}}
        E|={edge(mp[a],mp[b])for i,(a,b)in enumerate(SE)if m>>i&1}
    return E
def literal(E,U,S,X):
    X={tuple(e)for e in X};U=set(U)
    assert U=={0,1}and X<=E and len(X)<=2*len(S)
    used=[]
    for tri in S:
        F={edge(a,b)for a,b in combinations(tri,2)}
        assert len(set(tri))==3 and F<=E
        assert all(set(e)&U or e in X for e in F)
        used.extend(F)
    assert len(used)==len(set(used))
    upper=E|{(a,b)for a in range(6,10)for b in range(10,14)}
    for tri in combinations(range(14),3):
        F={edge(a,b)for a,b in combinations(tri,2)}
        if set(tri)&U and F<=upper:assert F&X

remaining=json.loads(Path('work/tuza_degree9_c4_h12_remaining_keys.json').read_text())['remaining_keys']
key=remaining[0];E=graph(key)
                                                                      
D={v:{b if a==v else a for a,b in E if v in (a,b)}for v in range(14)}
c=2;mate=5
A=sorted(D[0]&D[c]-{1,mate});B=sorted(D[1]&D[c]-{0,mate})
assert A==[8,9]and B==[12,13]and D[c]=={0,1,mate,*A,*B}
L={e for e in E if set(e)<=D[c]}
assert L=={(0,1),(0,mate),(1,mate)}|{(0,a)for a in A}|{(1,b)for b in B}
assert len(D[0])==len(D[1])==9
                                                                     
                                                                          
data=json.loads(Path('work/tuza_degree9_c4_h12_one_cross.json').read_text())
required=tuple(data['required_cross'][0])
literal(E|{required},data['U'],data['S'],data['X'])
maps=[];orbit={}
for swap in (0,1):
    for cp in permutations(range(2,6)):
        for ap in permutations(range(6,10)if not swap else range(10,14)):
            for bp in permutations(range(10,14)if not swap else range(6,10)):
                mp={0:swap,1:1-swap}|dict(zip(range(2,6),cp))|dict(zip(range(6,10),ap))|dict(zip(range(10,14),bp))
                image={edge(mp[a],mp[b])for a,b in E}
                if image!=E:continue
                q=edge(*(mp[a]for a in required))
                if q not in orbit:
                    S=[[mp[a]for a in tri]for tri in data['S']]
                    X=[edge(mp[a],mp[b])for a,b in data['X']]
                    literal(E|{q},[mp[a]for a in data['U']],S,X)
                    orbit[q]=mp
                maps.append(mp)
assert set(orbit)=={(a,b)for a in range(6,10)for b in range(10,14)}
other=json.loads(Path('work/tuza_degree9_c4_h12_other_reducers.json').read_text())
assert {tuple(row['key'])for row in other}=={tuple(k)for k in remaining[1:]}
for row in other:
    assert not row['required_cross']and row['outside_budget']==0
    literal(graph(row['key']),row['U'],row['S'],row['X'])

                                                                             
                                                                        
import hashlib
catalog=Path('work/tuza_degree10_c4_all_sides.json')
fresh=json.loads(Path('work/tuza_degree10_c4_side_independent_verified.json').read_text())
assert fresh['result']=='PASS' and fresh['nonWKE_types']==262
assert fresh['source_sha256']==hashlib.sha256(catalog.read_bytes()).hexdigest()
bad=Path('work/tuza_degree10_nonwke_link4.g6').read_text().splitlines()
found=[];types=set()
for line in bad:
    A=[set()for _ in range(10)];k=0
    for b in range(1,10):
        for a in range(b):
            if (ord(line[1+k//6])-63)>>(5-k%6)&1:A[a].add(b);A[b].add(a)
            k+=1
    for u,v in combinations(range(10),2):
        if v not in A[u]or len(A[u])!=4 or len(A[v])!=4:continue
        common=A[u]&A[v]
        if len(common)!=1:continue
        t=next(iter(common));L=A[u]-{v,t};R=A[v]-{u,t}
        if any(b in A[a]for a,b in combinations(L,2))or any(b in A[a]for a,b in combinations(R,2)):continue
        if any(t in A[a]for a in L|R)or any(b in A[a]for a in L for b in R):continue
        pivots=[]
        for z in range(10):
            if len(A[z])!=4:continue
            density=sum(b in A[a]for a,b in combinations(A[z],2))
            if density>2:pivots.append([z,density])
        assert pivots,'A density-admissible order-ten no-cross link survived'
        found.append({'g6':line,'u':u,'v':v,'t':t,'A':sorted(L),'B':sorted(R),'pivots':pivots});types.add(line)
assert len(found)==8 and len(types)==6
old=json.loads(Path('work/tuza_degree9_c4_h12_no_cross_independent.json').read_text())
assert old['verified']and old['one_cross_certificate']['covers_all_optional_private_cross_edges']
assert old['no_cross_all_labelled_completions']=={'0':1,'1':32,'2':2048}
out={'result':'PASS','order_ten_nonWKE_types_checked':len(bad),'order_ten_no_cross_types':len(types),'order_ten_no_cross_embeddings':len(found),'all_no_cross_types_have_denser_codegree_four_pivot':True,'density_witnesses':found,'hard_pair_automorphisms':len(maps),'hard_pair_cross_orbit_size':len(orbit),'one_cross_packing_size':len(data['S']),'one_cross_cover_size':len(data['X']),'covers_all_optional_private_cross_edges':True,'scope':'Global maximum codegree four, maximum degree ten, selected common core density two. The original order-at-most-nine human WKE lemma and these six denser-pivot exclusions force the private cross edge.'}
Path('work/tuza_degree10_c4_h12_human_verified.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
