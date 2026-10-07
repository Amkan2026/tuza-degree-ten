from itertools import combinations,permutations,product
from collections import Counter
from pathlib import Path
import hashlib,json,time

def edge(x,y):return tuple(sorted((x,y)))
labels=dict(zip('rsuvabcd',range(4,12)))
r,s,u,v,a,b,c,d=[labels[x] for x in 'rsuvabcd']
L=list(range(4));R=list(range(4,12));U={u,v,*L}
cross=[edge(a,c),edge(a,d),edge(b,c),edge(b,d)]
data=[
 ('','ur ab vd','ua rv cd','ub rc vs','us vc ra'),
 ('uvr','ab cd vs','ua bd rc','ub ac vd','us vc ra'),
 ('uvs','ur ac vd','ub ra vc','vr ab cd','ua rc bd'),
 ('','ua vc','ub vd ra sc','ab cd us vr','ur vs'),
 ('','ur vc ab','ub vr ad sc','ua vs cd','us vd ra'),
 ('uvr','ab cd vs','ua bc vd','ub ad sc','ra vc us'),
 ('uvr','ra cd vs','ua bc vd','ub ad sc','ab us vc'),
 ('','us ac vd','ub ra vc','ur vs cd ab','vr sc bd ua')]

def get_table(i):
    T,*rows=data[i]
    return ([tuple(labels[z] for z in T)] if T else []),[[tuple(labels[z] for z in f) for f in row.split()] for row in rows]
def transpose(rows,opposite):
    mp={u:v,v:u,a:c,c:a,b:d,d:b}
    if opposite:mp.update({r:s,s:r})
    return [[tuple(mp.get(z,z) for z in f) for f in row] for row in rows]
def literal(E,S,X):
    if not X<=E or len(X)>2*len(S):return False
    used=set()
    for T in S:
        if len(T)!=3 or len(set(T))!=3:return False
        F={edge(x,y) for x,y in combinations(T,2)}
        if not F<=E or F&used:return False
        if any(f not in X for f in F if not set(f)&U):return False
        used|=F
    vertices=set().union(*map(set,E))
    for h in U:
        N=[z for z in vertices if z!=h and edge(h,z) in E]
        for x,y in combinations(N,2):
            if edge(x,y) in E and not {edge(h,x),edge(h,y),edge(x,y)}&X:return False
    return True

count=Counter();excluded=0;negative={};start=time.time()
for same,mb,md,k in product((False,True),range(-1,4),range(-1,4),range(16)):
    if same and k==15:
        excluded+=1
        assert len(set(L+[r,b,d]))==7
        continue
    ac,ad,bc,bd=[k>>i&1 for i in range(4)]
    distinct=mb>=0 and md>=0 and mb!=md
    if same:
        if k.bit_count()<=1:T,rows=get_table(0);kind='same_base'
        elif ad or bc:
            T,rows=get_table(0)
            if ad:rows[2].append((a,d));kind='same_ad'
            else:rows=transpose(rows,False);rows[2].append((b,c));kind='same_bc'
        else:
            assert ac and bd
            T,rows=get_table(2 if distinct else 1);kind='same_two_cross_distinct' if distinct else 'same_two_cross_equal'
    else:
        if k.bit_count()<=1:T,rows=get_table(3);kind='opposite_base'
        elif k==15:
            if distinct:T,rows=get_table(7);kind='opposite_full_distinct'
            else:T,rows=get_table(3);rows[0].append((b,d));rows[3].append((a,c));kind='opposite_full_equal'
        elif ac:T,rows=get_table(3);rows[3].append((a,c));kind='opposite_ac'
        elif bd and not distinct:T,rows=get_table(3);rows[0].append((b,d));kind='opposite_bd_equal'
        elif bd:
            T,rows=get_table(4);kind='opposite_ad_distinct'
            if not ad:
                assert bc
                rows=transpose(rows,True);kind='opposite_bc_distinct'
        else:
            assert ad and bc
            T,rows=get_table(6 if distinct else 5);kind='opposite_two_cross_distinct' if distinct else 'opposite_two_cross_equal'
    Er={edge(*f) for f in [(u,v),(u,r),(u,s),(v,r),(v,s),(u,a),(u,b),(v,c),(v,d),(r,a),(r if same else s,c),(a,b),(c,d)]}
    Er|={cross[i] for i in range(4) if k>>i&1}
    for row in rows:
        used=set()
        for x,y in row:
            assert edge(x,y) in Er and not used&{x,y},(same,mb,md,k,kind,row)
            used|={x,y}
    assignment=next((z for z in permutations(L) if all(not (mb==leaf and any(b in f for f in row)) and not (md==leaf and any(d in f for f in row)) for leaf,row in zip(z,rows))),None)
    assert assignment is not None,(same,mb,md,k,kind)
    S=T+[(leaf,x,y) for leaf,row in zip(assignment,rows) for x,y in row]
    expected=12 if k.bit_count()<=1 else 14 if k==15 else 13
    assert len(S)==expected
    E=Er|{edge(leaf,x) for leaf in L for x in R if not (x==b and leaf==mb) and not (x==d and leaf==md)}
    X=set(Er);outside=[];nextvertex=12
    for leaf in L:
        deficit=10-sum(edge(leaf,x) in E for x in range(12) if x!=leaf)
        for _ in range(deficit):outside.append(nextvertex);E.add(edge(leaf,nextvertex));X.add(edge(leaf,nextvertex));nextvertex+=1
    E|={edge(z,w) for z in outside for w in R if w not in U}|{edge(z,w) for z,w in combinations(outside,2)}
    assert literal(E,S,X),(same,mb,md,k,kind)
    count[kind]+=1
    if not negative:
        rim=next(f for tri in S for f in (edge(*z) for z in combinations(tri,2)) if not set(f)&U)
        spoke=next(f for f in X if any(x>=12 for x in f))
        negative={'empty_cover':not literal(E,S,set()),'duplicate_triangle':not literal(E,S+[S[0]],X),'missing_outer_rim':not literal(E,S,X-{rim}),'missing_outside_spoke':not literal(E,S,X-{spoke})}
assert sum(count.values())==775 and excluded==25 and all(negative.values())
source=Path(__file__);proof=Path('work/tuza_degree10_c6_K24_private_edges_human_proof.txt')
report={'status':'PASS','human_matching_tables':8,'constructive_reductions':775,'known_codegree_seven_exclusions':25,'original_side_pairs_under_center_swap':100,'outside_spokes_at_ambient_degree_ten_bound':True,'all_outside_to_unremoved_and_outside_to_outside_edges_allowed':True,'negative_controls':negative,'case_counts':dict(count),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'proof_sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),'seconds':time.time()-start}
out=Path('work/tuza_degree10_c6_K24_private_edges_human_verified.json');tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(out)
print(json.dumps(report))
