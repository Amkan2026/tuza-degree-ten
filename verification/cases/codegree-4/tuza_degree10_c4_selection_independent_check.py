                                                                                

                                                                         
                                                                      
   
from itertools import combinations,permutations
from pathlib import Path
import json,time,sys
import numpy as np

HERE=Path(__file__).resolve().parent
CE=tuple(combinations(range(4),2));CI={e:i for i,e in enumerate(CE)}
CP=tuple(permutations(range(4)))

def edge(a,b):return tuple(sorted((a,b)))
def core_edges(h):return {e for j,e in enumerate(CE)if h>>j&1}
def image_core(h,p):return sum(1<<CI[edge(p[a],p[b])]for a,b in core_edges(h))
def core_canonical(h):return min(image_core(h,p)for p in CP)
def potentials(n):return tuple((c,a)for c in range(4)for a in range(4,n-1))+tuple(combinations(range(4,n-1),2))
def side_edges(n,m):return {e for j,e in enumerate(potentials(n))if m>>j&1}
def private_count(n,m):return sum(a>=4 for a,b in side_edges(n,m))

def assert_caps_equal(supplied,derived):
    assert {int(h):b for h,b in supplied.items()}==derived

def partial_side(n,h,m):
                                                               
    E={(0,v)for v in range(1,n+1)}|{(1,c)for c in range(2,6)}
    E|={(a+2,b+2)for a,b in core_edges(h)|side_edges(n,m)}
    return E

def adjacency(E):
    d={v:set()for e in E for v in e}
    for a,b in E:d[a].add(b);d[b].add(a)
    return d

def known_density_violation(E,m):
    D=adjacency(E)
    for a,b in E:
        C=D[a]&D[b]
        if len(C)==4 and sum(edge(x,y)in E for x,y in combinations(C,2))>m:
            return a,b
    return None

def pair_base(nl,nr,h):
    split=nl+1
    E={(0,1)}|{edge(hub,c)for hub in (0,1)for c in range(2,6)}
    E|={(0,a)for a in range(6,split)}|{(1,b)for b in range(split,split+nr-5)}
    E|={(a+2,b+2)for a,b in core_edges(h)}
    return E

def side_to_pair(e,nl,side):
    offset=6 if side==0 else nl+1
    return edge(*(v+2 if v<4 else v+offset-4 for v in e))

def literal_interval(nl,nr,h,row):
    R,F,T,V=map(lambda es:{tuple(e)for e in es},row['signature'])
    assert not R&F and not T&V
    assert R|F<=set(potentials(nl))and T|V<=set(potentials(nr))
    lower=pair_base(nl,nr,h)|{side_to_pair(e,nl,0)for e in R}|{side_to_pair(e,nl,1)for e in T}
    upper=pair_base(nl,nr,h)|{side_to_pair(e,nl,0)for e in set(potentials(nl))-F}|{side_to_pair(e,nl,1)for e in set(potentials(nr))-V}
    S=row['S'];X={tuple(e)for e in row['X']}
    assert S and X<=lower and len(X)<=2*len(S)
    used=[]
    for t in S:
        E={edge(a,b)for a,b in combinations(t,2)}
        assert len(set(t))==3 and E<=lower
        used.extend(E)
        assert all(set(e)&{0,1}or e in X for e in E)
    assert len(used)==len(set(used))
    N=nl+nr-4
    for t in combinations(range(N),3):
        E={edge(a,b)for a,b in combinations(t,2)}
        if set(t)&{0,1}and E<=upper:assert E&X

def main(report_target=None):
    started=time.monotonic()
    allside=json.loads((HERE/'tuza_degree10_c4_all_sides.json').read_text())
    density=json.loads((HERE/'tuza_degree10_c4_density_sides.json').read_text())
    sourcepath=Path(sys.argv[1])if len(sys.argv)>1 else HERE/'tuza_degree9_c4_density_intervals.json'
    source=json.loads(sourcepath.read_text())
                                                                         
    assert {core_canonical(h)for h in range(64)}=={0,1,3,7,11,12,13,15,30,31,63}
    raw_counts={}
    for n in (7,8,9,10):
        assert list(map(list,potentials(n)))==allside[str(n)]['side_edges']
        fresh={}
        freshfile=HERE/f'tuza_degree9_c4_side_direct{n}_audit.txt'if n<9 else HERE/f'tuza_degree{10 if n==10 else 9}_c4_side_direct{n}.txt'
        for line in freshfile.read_text().splitlines():
            h,m=map(int,line.split());fresh.setdefault(h,set()).add(m)
        claimed={int(h):set(ms)for h,ms in allside[str(n)]['core_sides'].items()if ms}
        assert fresh==claimed,(n,'fresh direct side domain differs')
        raw_counts[n]=sum(map(len,fresh.values()))
                                                                  
    filtered={};excluded=0
    for n in (7,8,9,10):
        filtered[n]={}
        for hs,ms in allside[str(n)]['core_sides'].items():
            h=int(hs)
            good=[]
            for m in ms:
                if known_density_violation(partial_side(n,h,m),h.bit_count())is None:good.append(m)
                else:excluded+=1
            if good:filtered[n][h]=good
        claimed={int(h):list(ms)for h,ms in density[str(n)]['core_sides'].items()}
        assert filtered[n]==claimed,(n,'density filter differs')
                                                                   
    exclusions=json.loads((HERE/'tuza_degree10_c4_density_side_exclusions.json').read_text())
    assert len(exclusions)==excluded
    for row in exclusions:
        E=partial_side(row['degree'],row['core'],row['side']);D=adjacency(E)
        a,b=row['edge'];C=D[a]&D[b]
        assert (a,b)in E and len(C)==4 and C==set(row['common'])
        assert sum(edge(x,y)in E for x,y in combinations(C,2))==row['density']>row['core'].bit_count()
                                                                            
    caps={}
    for n,cores in filtered.items():
        for h,ms in cores.items():
            caps[h]=max(caps.get(h,0),max(private_count(n,m)for m in ms))
    bounds={};pivot_witnesses=[]
    for n,cores in filtered.items():
        for h,ms in cores.items():
            for m in ms:
                E=partial_side(n,h,m);D=adjacency(E);best=None
                for w in sorted(D[0]):
                    C=D[0]&D[w]
                    if len(C)!=4:continue
                    labels=sorted(C);ph=sum(1<<j for j,(a,b)in enumerate(CE)if edge(labels[a],labels[b])in E)
                    if ph.bit_count()!=h.bit_count():continue
                    canonical=core_canonical(ph)
                    assert canonical in caps
                    A=D[0]-{w}-C
                    p=sum(edge(a,b)in E for a,b in combinations(A,2))
                    bound=(p+caps[canonical],min(p,caps[canonical]))
                    if best is None or bound<best:
                        best=bound;best_row={'degree':n,'core':h,'side':m,'pivot':[0,w],'pivot_core':canonical,'known_private_edges':p,'partner_cap':caps[canonical],'bound':bound}
                assert best is not None
                bounds[n,h,m]=best;pivot_witnesses.append(best_row)
                                                                           
    supplied=json.loads((HERE/'tuza_degree10_c4_private_bounds.json').read_text())
    assert_caps_equal(supplied['partner_caps'],caps)
    supplied_bounds=0
    for ns,cores in supplied['bounds'].items():
        n=int(ns)
        for hs,models in cores.items():
            h=int(hs)
            for ms,row in models.items():
                m=int(ms)
                assert tuple(row['bound'])==bounds[n,h,m]
                assert row['private_edges']==private_count(n,m)
                w=row['witness'];E=partial_side(n,h,m);D=adjacency(E)
                a,b=w['pivot'];assert a==0 and (a,b)in E
                C=D[a]&D[b];assert len(C)==4 and C==set(w['common'])
                labels=sorted(C);ph=sum(1<<j for j,(x,y)in enumerate(CE)if edge(labels[x],labels[y])in E)
                assert ph.bit_count()==h.bit_count()and core_canonical(ph)==w['pivot_core']
                A=D[a]-{b}-C;p=sum(edge(x,y)in E for x,y in combinations(A,2))
                assert p==w['known_private_edges']and caps[w['pivot_core']]==w['partner_cap']
                assert tuple(w['bound'])==(p+caps[w['pivot_core']],min(p,caps[w['pivot_core']]))==bounds[n,h,m]
                supplied_bounds+=1
    assert supplied_bounds==len(bounds)
                                                
    assert 0 not in filtered[7]and 0 not in filtered[8]
    assert len(filtered[9][0])==36 and caps[0]==4
    types={};c4_pivots=0
    for m in filtered[9][0]:
        F={e for e in side_edges(9,m)if e[0]>=4}
        degrees=sorted(sum(v in e for e in F)for v in range(4,8))
        key=(len(F),tuple(degrees));types[str(key)]=types.get(str(key),0)+1
        if degrees==[2,2,2,2]:
            E=partial_side(9,0,m);D=adjacency(E)
            for w in range(6,10):
                C=D[0]&D[w];A=D[0]-{w}-C
                assert len(C)==4 and not any(edge(a,b)in E for a,b in combinations(C,2))
                assert sum(edge(a,b)in E for a,b in combinations(A,2))==2
                c4_pivots+=1
    assert c4_pivots==12
    report={'result':'PASS','raw_side_counts':raw_counts,'density_side_exclusions':excluded,'initial_density_private_caps':caps,'literal_private_bound_witnesses':supplied_bounds,'seconds':time.monotonic()-started}
    (HERE/'tuza_degree10_c4_selection_independent_verified.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report)

if __name__=='__main__':main()
