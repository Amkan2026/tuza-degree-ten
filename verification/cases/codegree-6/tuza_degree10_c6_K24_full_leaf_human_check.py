from itertools import combinations,product
from pathlib import Path
import hashlib,json,time
def edge(x,y):return tuple(sorted((x,y)))
r,s,u,v,a,b,c,d=range(4,12);L=list(range(4));R=list(range(4,12));U={u,v,*L}
cross=[edge(a,c),edge(a,d),edge(b,c),edge(b,d)]
internal=(u,v,r);internaledges={edge(x,y) for x,y in combinations(internal,2)}
def literal(E,S,X):
    if not X<=E or len(X)>2*len(S):return False
    used=set()
    for T in S:
        F={edge(x,y) for x,y in combinations(T,2)}
        if len(F)!=3 or not F<=E or F&used:return False
        if any(f not in X for f in F if not set(f)&U):return False
        used|=F
    V=set().union(*map(set,E))
    for h in U:
        N=[z for z in V if z!=h and edge(z,h) in E]
        for x,y in combinations(N,2):
            if edge(x,y) in E and not {edge(h,x),edge(h,y),edge(x,y)}&X:return False
    return True
def color4(E):
    result={};used={z:0 for z in R}
    def go():
        if len(result)==len(E):return True
        f=min((f for f in E if f not in result),key=lambda f:(15&~(used[f[0]]|used[f[1]])).bit_count());x,y=f
        choices=15&~(used[x]|used[y])
        for col in range(4):
            bit=1<<col
            if choices&bit:
                result[f]=col;used[x]|=bit;used[y]|=bit
                if go():return True
                del result[f];used[x]^=bit;used[y]^=bit
        return False
    assert go();return result
start=time.time();records=0;negative={}
for ka,kb,mask in product(range(3),range(3),range(16)):
    actual={cross[j] for j in range(4) if mask>>j&1};nc=len(actual);eps=int(ka==2)+int(kb==2)
    fixed={edge(*f) for f in [(u,v),(u,r),(u,s),(v,r),(v,s),(u,a),(u,b),(v,c),(v,d)]}
    for kind,x,y in [(ka,a,b),(kb,c,d)]:
        if kind==0:fixed|={edge(x,r),edge(x,s)}
        else:fixed|={edge(x,r),edge(y,s)}
        if kind==2:fixed.add(edge(x,y))
    assert len(fixed)==13+eps
    base=fixed-internaledges;degree={z:sum(z in e for e in base) for z in R}
    q=max(0,(nc-eps)//2)
    if q==0:keep=set()
    elif q==1:
        keep={next(f for f in actual if not(degree[f[0]]==3 and degree[f[1]]==3 and edge(f[0],s) in base and edge(f[1],s) in base))}
    else:
        assert q==2 and eps==0 and mask==15
        keep={edge(a,d),edge(b,c)}
    K=base|keep;degree={z:sum(z in f for f in K) for z in R}
    assert max(degree.values())<=4
    high={z for z in R if degree[z]==4};parent={z:z for z in high}
    def find(z):
        while parent[z]!=z:z=parent[z]
        return z
    for x,y in K:
        if x in high and y in high:
            px,py=find(x),find(y);assert px!=py;parent[px]=py
    coloring=color4(K);S=[internal]+[(L[col],x,y) for (x,y),col in coloring.items()]
    assert len(S)==11+eps+q
    Er=fixed|actual;E=Er|{edge(leaf,z) for leaf in L for z in R};X=set(Er);outside=list(range(12,20))
    for leaf in L:
        for z in outside[2*leaf:2*leaf+2]:E.add(edge(leaf,z));X.add(edge(leaf,z))
    E|={edge(z,w) for z in outside for w in R if w not in U}|{edge(z,w) for z,w in combinations(outside,2)}
    assert literal(E,S,X),(ka,kb,mask)
    records+=1
    if not negative:
        rim=next(f for T in S for f in (edge(*z) for z in combinations(T,2)) if not set(f)&U)
        spoke=next(f for f in X if any(z>=12 for z in f))
        negative={'empty_cover':not literal(E,S,set()),'duplicate_triangle':not literal(E,S+[S[0]],X),'missing_outer_rim':not literal(E,S,X-{rim}),'missing_outside_spoke':not literal(E,S,X-{spoke})}
assert records==144 and all(negative.values())
proof=Path('work/tuza_degree10_c6_K24_full_leaf_human_proof.txt')
out={'status':'PASS','ordered_private_profiles':9,'cross_patterns':16,'constructive_reductions':144,'maximum_degree_four_remainder':True,'degree_four_vertices_induce_forest':True,'proper_four_colors_found_directly':True,'outside_leaf_spokes_at_degree_ten_bound':8,'all_unknown_outside_edges_allowed':True,'negative_controls':negative,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'proof_sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),'seconds':time.time()-start}
dest=Path('work/tuza_degree10_c6_K24_full_leaf_human_verified.json');tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(dest);print(json.dumps(out))
