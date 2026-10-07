                                                                           
from itertools import combinations, permutations
from pathlib import Path
import hashlib
import json

def e(a,b): return tuple(sorted((a,b)))
C=range(4)
s,u,v,t=4,5,6,7
A=(8,9,10)
B=(11,12,13)
U={u,v,t}
count=0
negative={"empty_cover":False,"duplicate_triangle":False,"missing_outer_rim":False}

def check(E,S,X):
    seen=set()
    for a,b,c in S:
        tri={e(a,b),e(a,c),e(b,c)}
        if not tri<=E or seen&tri: return False
        seen|=tri
        if any(z not in X for z in tri if not (set(z)&U)): return False
    if len(X)>2*len(S): return False
    for h in U:
        nbr=[z for z in range(18) if z!=h and e(h,z) in E]
        for a,b in combinations(nbr,2):
            if e(a,b) in E and not ({e(h,a),e(h,b),e(a,b)}&X): return False
    return True

for r in (3,4):
    D=tuple(range(14,14+r))
    pools=[]
    for a,b in combinations(D,2):
        rem=[d for d in D if d not in (a,b)]
        for d in rem:
            for c in C: pools.append((e(a,b),e(d,c)))
        if r==4:
            pools.append((e(a,b),e(*rem)))
            for x,y in permutations(C,2):
                pools.append((e(a,b),e(rem[0],x),e(rem[1],y)))
    pools=sorted(set(tuple(sorted(M)) for M in pools))
    vertices=tuple(C)+D
    for M in pools:
        assert len(set(z for edge in M for z in edge))==2*len(M)
        T={z for edge in M for z in edge if z in C}
        assert len(T)<=2
        for qsize in range(len(M)+2):
            for Qtuple in combinations(vertices,qsize):
                Q=set(Qtuple)
                J=set(M)
                J|={e(a,b) for a,b in combinations(D,2) if a in Q or b in Q}
                J|={e(a,c) for a in D for c in C if a in Q or c in Q}
                for p in tuple(C)+(s,):
                    V=set() if p==s else {p}
                    chosen=[]
                    for allowed in (set(C)-(T|V),set(C)-T,set(C)-V):
                        q=min(allowed-set(chosen));chosen.append(q)
                    qvt,qut,quv=chosen
                    S=[(u,A[0],A[1]),(u,A[2],s),(v,B[0],B[1]),(v,B[2],p)]
                    S += [(t,*edge) for edge in M]
                    S += [(v,t,qvt),(u,t,qut),(u,v,quv)]
                    X={e(u,v),e(u,t),e(v,t),e(A[0],A[1]),e(A[2],s),e(B[0],B[1]),e(B[2],p)}
                    X|={e(u,a) for a in A}|{e(v,b) for b in B}|set(M)|{e(t,q) for q in Q}
                    E={e(u,v),e(u,t),e(v,t)}
                    E|={e(h,c) for h in U for c in C}|{e(u,s),e(v,s)}
                    E|={e(u,a) for a in A}|{e(v,b) for b in B}|{e(t,d) for d in D}
                    E|={e(a,c) for a in A+B for c in tuple(C)+(s,)}
                    E|={e(a,b) for a,b in combinations(A+B+D,2) if not (a in D and b in D)}
                    E|={e(d,s) for d in D}|J
                    assert X<=E
                    assert check(E,S,X),(r,M,Q,p,S,X)
                    count+=1
                    if count==1:
                        negative["empty_cover"]=not check(E,S,set())
                        negative["duplicate_triangle"]=not check(E,S+[S[0]],X)
                        Xbad=X-{e(A[2],s)}
                        negative["missing_outer_rim"]=not check(E,S,Xbad)
assert all(negative.values())
src=Path(__file__)
report={"status":"PASS","universal_matching_cover_intervals":count,
        "closed_hubs":3,"private_groups_u_v":3,"center_privates":[3,4],
        "all_private_cross_edges_allowed":True,"all_u_v_private_contacts_allowed":True,
        "packing_size":"|M|+7","cover_size_bound":"2|M|+14",
        "one_side_private_triangle_uses_isolate":True,"negative_controls":negative,
        "source_sha256":hashlib.sha256(src.read_bytes()).hexdigest()}
Path('work/tuza_degree10_c6_four_private_glue_verified.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
