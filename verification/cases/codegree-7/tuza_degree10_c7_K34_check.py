                                                                     
from pathlib import Path
from itertools import combinations
import json
H={(q,p)for q in range(4)for p in(4,5,6)}
fixed=H|{(c,h)for c in range(7)for h in(7,8)}|{(7,8),(7,9),(7,10),(8,11),(8,12)}
U={4,5,6,7,8};one={4,5,6,7,11,12}
S=[(0,4,7),(0,5,9),(0,6,8),(1,4,9),(1,5,10),(1,6,7),(2,4,10),(2,5,8),(2,7,9),(3,6,10),(3,7,8),(4,8,11)]
used=[e for t in S for e in combinations(t,2)]
assert len(used)==len(set(used))==36
required={(p,a)for p in(4,5,6)for a in(9,10,11,12)}|{(q,9)for q in(0,1,2)}|{(q,10)for q in(1,2,3)}
variable={(c,a)for c in range(7)for a in(9,10,11,12)}|{(9,10),(11,12)}
assert set(used)<=fixed|required
optional=sorted(variable-required);assert len(optional)==12
cross_private={(a,b)for a in(9,10)for b in(11,12)}
count=0;max_cover=0
for mask in range(1<<len(optional)):
    E=fixed|required|{e for j,e in enumerate(optional)if mask>>j&1}
    assert all(sum(v in e for e in E)==10 for v in U)
    X={e for e in E if(e[0]in one)==(e[1]in one)}
    assert len(X)<=23 and len(X)<=2*len(S)
    assert all(e in X for e in used if not set(e)&U)
                                                                       
    upper=E|cross_private
    for t in combinations(range(13),3):
        es=set(combinations(t,2))
        if set(t)&U and es<=upper:assert es&X
    max_cover=max(max_cover,len(X));count+=1
out={'result':'PASS','labelled_contact_and_internal_edge_patterns':count,'arbitrary_cross_side_edges':True,'triangles':12,'maximum_cover':max_cover,'outside_neighbor_budget':0}
Path('work/tuza_degree10_c7_K34_verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
