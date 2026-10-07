                                                                        
import itertools,json,sys,time,zlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'work')
from tuza_degree10_c6_full_rectangles import patterns

pop=np.array([i.bit_count() for i in range(64)],dtype=np.int16)

def density_admitted(H,P,r):
    H=set(map(tuple,H));m=len(H)
    hh=[sum(1<<b for b in range(6) if tuple(sorted((a,b))) in H) for a in range(6)]
    eh=np.array([sum((q>>a&1) and (q>>b&1) for a,b in H) for q in range(64)],dtype=np.int16)
    V=list(itertools.combinations(range(r),2))
    D=[((P>>(6*j))&63).astype(np.int16) for j in range(r)]
    Q=(P>>(6*r)).astype(np.int16)
    good=np.ones(len(P),dtype=bool)
    for c in range(6):
        C=[(d>>c&1).astype(np.int16) for d in D]
        degree=1+hh[c].bit_count()+sum(C)
        den=np.full(len(P),hh[c].bit_count()+int(eh[hh[c]]),dtype=np.int16)
        for j in range(r):den+=C[j]*pop[D[j]&hh[c]]
        for bit,(i,j) in enumerate(V):den+=(Q>>bit&1)*C[i]*C[j]
        good&=~((degree==6)&(den>m))
    for i in range(r):
        degree=pop[D[i]].copy();den=eh[D[i]].copy();N={}
        for j in range(r):
            if i==j:continue
            bit=V.index(tuple(sorted((i,j))))
            N[j]=(Q>>bit&1).astype(np.int16)
            degree+=N[j];den+=N[j]*pop[D[i]&D[j]]
        for bit,(a,b) in enumerate(V):
            if a!=i and b!=i:den+=(Q>>bit&1)*N[a]*N[b]
        good&=~((degree==6)&(den>m))
    return good

if __name__=='__main__':
    start=time.time();out=[];dest=Path('work/tuza_degree10_c6_density_patterns');dest.mkdir(exist_ok=True)
    D=json.loads(Path('work/tuza_degree10_c6_domain.json').read_text())['records']
    for idx,row in enumerate(D):
        sides={}
        for r in range(4):
            P=patterns(row,r);keep=density_admitted(row['H'],P,r);Q=P[keep]
            file=dest/f'{idx:03d}_{r}.bin.z';file.write_bytes(zlib.compress(Q.astype('<u4').tobytes()))
            sides[str(r)]={'canonical_candidates':len(P),'selected_density_candidates':len(Q),'excluded_by_hub_pivot':int((~keep).sum()),'file':str(file)}
        out.append({'g6':row['g6'],'H':row['H'],'sides':sides})
        if sides['3']['excluded_by_hub_pivot']:print(idx,row['g6'],sides['3']['canonical_candidates'],sides['3']['selected_density_candidates'],round(time.time()-start,1),flush=True)
    result={'records':out,'selection':'Among maximum-codegree-six edges choose one maximizing the common-graph edge count. Every excluded side contains an incident maximum-codegree edge with a denser common graph.','seconds':time.time()-start}
    Path('work/tuza_degree10_c6_density_domain.json').write_text(json.dumps(result,indent=2))
    print('COMPLETE',len(out),sum(r['sides']['3']['canonical_candidates'] for r in out),sum(r['sides']['3']['selected_density_candidates'] for r in out),flush=True)
