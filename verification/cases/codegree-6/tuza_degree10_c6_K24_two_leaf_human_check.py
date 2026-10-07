from itertools import combinations
from pathlib import Path
import hashlib,json,time
def e(x,y):return tuple(sorted((x,y)))
r,s,u,v,a,b,c,d=range(4,12);U={r,s,u,v}
base={e(u,v)}|{e(h,z) for h in (u,v) for z in range(6)}|{e(h,z) for h in (r,s) for z in range(4)}|{e(u,a),e(u,b),e(v,c),e(v,d)}
base|={e(z,l) for z in (a,b) for l in (0,1)}|{e(z,l) for z in (c,d) for l in (2,3)}|{e(s,a),e(r,b),e(s,c),e(r,d)}
optional=list(combinations((a,b,c,d),2))
S=[(0,r,b),(0,s,a),(0,u,v),(1,s,v),(1,u,b),(2,r,u),(2,s,c),(2,v,d),(3,r,v),(3,s,u)]
X0={e(*f) for f in [(0,a),(0,b),(1,b),(2,v),(2,c),(2,d),(3,c),(r,u),(r,v),(r,d),(s,u),(s,v),(s,a),(u,v),(u,a),(v,d)]}
assert len(base)==37 and len(X0)==16 and len(S)==10
def literal(E,S,X):
    if not X<=E or len(X)>2*len(S):return False
    used=set()
    for T in S:
        if len(T)!=3 or len(set(T))!=3:return False
        F={e(x,y) for x,y in combinations(T,2)}
        if not F<=E or F&used:return False
        if any(f not in X for f in F if not set(f)&U):return False
        used|=F
    V=set().union(*map(set,E))
    for h in U:
        N=[z for z in V if z!=h and e(z,h) in E]
        for x,y in combinations(N,2):
            if e(x,y) in E and not {e(h,x),e(h,y),e(x,y)}&X:return False
    return True
start=time.time();negative={}
for mask in range(64):
    E=base|{optional[j] for j in range(6) if mask>>j&1};X=set(X0)
    for h in (r,s):assert sum(h in f for f in E)==8
    for h,Z in [(r,[12,13]),(s,[14,15])]:
        for z in Z:E.add(e(h,z));X.add(e(h,z))
    outside=list(range(12,16));unremoved=set(range(12))-U
    E|={e(z,w) for z in outside for w in unremoved}|{e(z,w) for z,w in combinations(outside,2)}
    assert len(X)==20 and literal(E,S,X),mask
    if not negative:
        negative={'empty_cover':not literal(E,S,set()),'duplicate_triangle':not literal(E,S+[S[0]],X),'missing_packed_outer_rim':not literal(E,S,X-{e(0,a)}),'missing_outside_spoke':not literal(E,S,X-{e(r,12)})}
assert all(negative.values())
proof=Path('work/tuza_degree10_c6_K24_two_leaf_human_proof.txt')
out={'status':'PASS','private_edge_patterns':64,'same_packing_and_cover_for_all_patterns':True,'packing_size':10,'local_cover_size':16,'outside_spokes_at_degree_ten_bound':4,'all_outside_to_unremoved_and_outside_to_outside_edges_allowed':True,'negative_controls':negative,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'proof_sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),'seconds':time.time()-start}
dest=Path('work/tuza_degree10_c6_K24_two_leaf_human_verified.json');tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(dest);print(json.dumps(out))
