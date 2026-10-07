from itertools import combinations,permutations,product
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
    vertices=set().union(*map(set,E))
    for z in U:
        N=[w for w in vertices if w!=z and edge(z,w) in E]
        for x,y in combinations(N,2):
            if edge(x,y) in E and not {edge(z,x),edge(z,y),edge(x,y)}&X:return False
    return True

def color4(E):
    colors={};used={z:0 for z in R}
    def visit():
        if len(colors)==len(E):return True
        f=min((f for f in E if f not in colors),key=lambda f:((15&~(used[f[0]]|used[f[1]])).bit_count(),-sum(f[0] in g or f[1] in g for g in E)))
        x,y=f;available=15&~(used[x]|used[y])
        for col in range(4):
            bit=1<<col
            if available&bit:
                colors[f]=col;used[x]|=bit;used[y]|=bit
                if visit():return True
                del colors[f];used[x]^=bit;used[y]^=bit
        return False
    assert visit(),E
    return colors

start=time.time();counts=[0,0,0];negative={};toptypes={}
for kind,missing,k in product(range(3),range(-1,4),range(16)):
    beta=int(kind==2);actual={cross[i] for i in range(4) if k>>i&1};nc=len(actual)
    q=(nc+1)//2 if not beta else nc//2
    fixed={edge(*f) for f in [(u,v),(u,r),(u,s),(v,r),(v,s),(u,a),(u,b),(v,c),(v,d),(r,a),(a,b)]}
    if kind==0:fixed|={edge(r,c),edge(s,c)}
    else:fixed|={edge(r,c),edge(s,d)}
    if beta:fixed.add(edge(c,d))
    assert len(fixed)==13+beta
    if q==0:keep=set()
    elif q==1:keep={min(actual)}
    else:
        allowed=[(0,3),(1,2),(1,3)] if kind==0 else [(0,2),(1,3),(0,3),(1,2)] if kind==1 else [(0,3)]
        keep=next(({cross[x],cross[y]} for x,y in allowed if {cross[x],cross[y]}<=actual),None)
        assert keep is not None
    K=(fixed-internaledges)|keep;degree={z:sum(z in f for f in K) for z in R}
    assert max(degree.values())<=4 and degree[b]<=3
    high={z for z in R if degree[z]==4};parent={z:z for z in high}
    def find(z):
        while parent[z]!=z:z=parent[z]
        return z
    high_edges={f for f in K if set(f)<=high}
    for x,y in high_edges:
        px,py=find(x),find(y)
        assert px!=py,('cycle in high-degree core',kind,missing,k,K)
        parent[px]=py
    toptypes[(kind,len(high),len(high_edges))]=toptypes.get((kind,len(high),len(high_edges)),0)+1
    coloring=color4(K);rows=[[f for f,col in coloring.items() if col==i] for i in range(4)]
    assignment=next(z for z in permutations(L) if all(not(missing==leaf and any(b in f for f in row)) for leaf,row in zip(z,rows)))
    S=[internal]+[(leaf,x,y) for leaf,row in zip(assignment,rows) for x,y in row]
    assert len(S)==11+beta+q
    Er=fixed|actual;E=Er|{edge(leaf,z) for leaf in L for z in R if not(z==b and leaf==missing)};X=set(Er);outside=[];n=12
    for leaf in L:
        allowance=10-sum(edge(leaf,z) in E for z in range(12) if z!=leaf)
        for _ in range(allowance):outside.append(n);E.add(edge(leaf,n));X.add(edge(leaf,n));n+=1
    E|={edge(z,w) for z in outside for w in R if w not in U}|{edge(z,w) for z,w in combinations(outside,2)}
    assert literal(E,S,X),(kind,missing,k)
    counts[kind]+=1
    if not negative:
        rim=next(f for T in S for f in (edge(*z) for z in combinations(T,2)) if not set(f)&U)
        spoke=next(f for f in X if any(z>=12 for z in f))
        negative={'empty_cover':not literal(E,S,set()),'duplicate_triangle':not literal(E,S+[S[0]],X),'missing_packed_outer_rim':not literal(E,S,X-{rim}),'missing_outside_spoke':not literal(E,S,X-{spoke})}
assert counts==[80,80,80] and all(negative.values())
proof=Path('work/tuza_degree10_c6_K24_one_private_edge_human_proof.txt');src=Path(__file__)
out={'status':'PASS','private_profiles':3,'absence_choices':5,'cross_choices':16,'constructive_patterns':240,'original_ordered_side_pairs':60,'degree_four_vertices_induce_forest':True,'proper_four_colors_found_directly':True,'maximum_degree_ten_outside_allowance_all_used':True,'unknown_outside_edges_all_allowed':True,'negative_controls':negative,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'proof_sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),'seconds':time.time()-start}
dest=Path('work/tuza_degree10_c6_K24_one_private_edge_human_verified.json');tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(dest);print(json.dumps(out))
