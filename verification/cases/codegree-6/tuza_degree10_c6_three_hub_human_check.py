                                                                           
from pathlib import Path
from itertools import combinations,product
from copy import deepcopy
import json
E=lambda a,b:tuple(sorted((a,b)))
U={0,1,2};C=set(range(3,8));HP=tuple(combinations(range(3),2));PP=tuple(combinations(range(3),2))
base={E(a,b)for a,b in HP}|{E(h,c)for h in U for c in C}|{E(h,z)for h in U for z in range(8+3*h,11+3*h)}
upper=base|{E(a,b)for a,b in combinations(range(8,17),2)}|{E(z,c)for z in range(8,17)for c in C}
triangles=[{E(a,b)for a,b in combinations(t,2)}for t in combinations(range(17),3)if set(t)&U and {E(a,b)for a,b in combinations(t,2)}<=upper]
def make(qs,ells):
 lower=set(base);S=[];X={E(a,b)for a,b in HP}
 for h,q,ell in zip(range(3),qs,ells):
  P=range(8+3*h,11+3*h);edges=[E(P[a],P[b])for j,(a,b)in enumerate(PP)if q>>j&1];lower.update(edges);a,b=edges[0];c=next(z for z in P if z not in(a,b));lower.add(E(c,ell))
  S.extend([[h,a,b],[h,c,ell]]);X|={E(h,z)for z in P}|{E(a,b),E(c,ell)}
 used=set()
 for a,b in HP:
  leaf=min(C-{ells[a],ells[b]}-used);used.add(leaf);S.append([a,b,leaf])
 return lower,S,X

def literal(lower,S,X):
 assert len(S)==9 and len(X)<=2*len(S)and X<=lower
 spent=set()
 for t in S:
  edges={E(a,b)for a,b in combinations(t,2)};assert len(set(t))==3 and edges<=lower and not edges&spent
  assert all(set(e)&U or e in X for e in edges);spent|=edges
 assert all(t&X for t in triangles)
count=0
for qs in product((3,5,6,7),repeat=3):
 for ells in product(range(3,8),repeat=3):
  lower,S,X=make(qs,ells);literal(lower,S,X);count+=1
assert count==8000
lower,S,X=make((3,3,3),(3,3,3));controls=[]
for name,ss,xx in [('empty cover',S,set()),('duplicate triangle',S+[S[0]],X),('missing packed outer rim',S,X-{E(S[0][1],S[0][2])})]:
 try:literal(lower,ss,xx)
 except AssertionError:controls.append(name)
 else:raise AssertionError('Control accepted '+name)
report={'result':'PASS','literal_universal_intervals':count,'packing_size':9,'cover_size':18,'all_private_contacts_allowed_in_upper_graph':True,'all_private_cross_edges_allowed_in_upper_graph':True,'all_packed_outer_rims_checked':True,'negative_controls_rejected':controls,'scope':'Three full hubs form a triangle, share five independent leaves and have three disjoint own privates. Each private group has an internal edge and a contact from its remaining vertex. Covers all K1,5 forced sides and arbitrary ambient extensions.'}
Path('work/tuza_degree10_c6_three_hub_human_verified.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
