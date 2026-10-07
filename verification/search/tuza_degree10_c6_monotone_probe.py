import itertools,json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,'work')
from tuza_degree10_c6_solve import pair,cut,variables,graph

def autos(H):
    H={tuple(e) for e in H};d=[sum(a in e for e in H) for a in range(6)]
    return [p for p in itertools.permutations(range(6)) if all(d[a]==d[p[a]] for a in range(6)) and {tuple(sorted((p[a],p[b]))) for a,b in H}==H]

def required(S,r,first):
    return sum(1<<i for i,e in enumerate(variables(r,first)) if any(set(e)<=set(t) for t in S))

def lower_variants(mask,r,perm):
    out=[]
    V=variables(r,0)
                                                                               
    V=variables(r,8)
    for q in itertools.permutations(range(r)):
        transformed=set()
        for i,(a,b) in enumerate(V):
            if not mask>>i&1:continue
            aa=perm[a] if a<6 else 8+q[a-8]
            bb=perm[b] if b<6 else 8+q[b-8]
            transformed.add(tuple(sorted((aa,bb))))
        out.append(sum(1<<i for i,e in enumerate(V) if e in transformed))
    return tuple(sorted(set(out)))

def bits(x):return int.from_bytes(np.packbits(x,bitorder='little').tobytes(),'little')

def cover(rec,AU,P,Q,covered,sa,sb):
    if rec['kind'] in ['monotone_cut','monotone_general']:
        a=rec['p'];b=rec['q']
    else:
        a=required(rec['S'],sa,8);b=required(rec['S'],sb,11)
    seen=set()
    exchange=sa==sb
    for perm in AU:
        av=lower_variants(a,sa,perm);bv=lower_variants(b,sb,perm)
        options=[(av,bv)]+([(bv,av)] if exchange else [])
        for aa,bb in options:
            if (aa,bb) in seen:continue
            seen.add((aa,bb))
            goodP=np.zeros(len(P),dtype=bool);goodQ=np.zeros(len(Q),dtype=bool)
            for lo in aa:goodP|=P&lo==lo
            for lo in bb:goodQ|=Q&lo==lo
            qbits=bits(goodQ)
            for i in np.flatnonzero(goodP):covered[int(i)]|=qbits

def domain(H,P,Q,sa,sb):
    H={tuple(e) for e in H};constraints=[]
    for a,b in H:
        com=sum(tuple(sorted((a,c))) in H and tuple(sorted((b,c))) in H for c in range(6) if c not in (a,b))
        cap=4-com
        def count(patterns,r):
            out=np.zeros(len(patterns),dtype=np.uint8)
            for j in range(r):out+=((patterns>>(6*j+a)&1)>0)&((patterns>>(6*j+b)&1)>0)
            return out
        ca=count(P,sa);cb=count(Q,sb)
        if max(ca,default=0)+max(cb,default=0)>cap:constraints.append((cap,ca,cb))
    out=[]
    for i in range(len(P)):
        legal=np.ones(len(Q),dtype=bool)
        if sa==sb:legal&=Q>=P[i]
        for cap,a,b in constraints:legal&=a[i]+b<=cap
        out.append(bits(legal))
    return out

def seed(r,sa,sb):
    oldsa=r['sa']
    if oldsa>sa or sb<2:return None
    def vertex(a):return a+1 if a>=10 else a
    S=[sorted(vertex(v) for v in t) for t in r['S']]
    X={tuple(sorted(vertex(v) for v in e)) for e in r['X'] if max(e)<8 or 6 in e or 7 in e}
    X|={(6,8+j) for j in range(sa)}|{(7,11+j) for j in range(sb)}
    X|={e for t in S for e in itertools.combinations(t,2) if 6 not in e and 7 not in e}
    if len(X)>2*len(S):return None
    return {'status':'PASS','kind':'pair','fixed_spokes':True,'U':[6,7],'S':S,'X':sorted(X),'seed':'degree9_fixed_spoke'}

if __name__=='__main__':
    started=time.time()
    D=json.loads(Path('work/tuza_degree10_c6_domain.json').read_text())
    C=json.loads(Path('work/tuza_degree10_c6_core_certificates.json').read_text())
    core={r['g6']:r['certificates'] for r in C['records']}
    old=json.loads(Path('work/tuza_degree9_c6_monotone_certificates.json').read_text())['records']
    by={}
    for r in old:by.setdefault(r['g6'],[]).append(r)
    checkpoint=Path('work/tuza_degree10_c6_monotone_checkpoint.json')
    records=[];failures=[];results=[]
    if checkpoint.exists():
        saved=json.loads(checkpoint.read_text());records=saved['records'];failures=saved['failures'];results=saved['results']
    done={(r['g6'],r['lane']) for r in results}
    def save():checkpoint.write_text(json.dumps({'records':records,'failures':failures,'results':results,'seconds':time.time()-started}))
    for row in D['records']:
        H=row['H'];AU=autos(H)
        for sa,sb in [(0,3),(1,3),(2,3),(3,3),(2,2)]:
            lane=f'{7+sa}/{7+sb}'
            if (row['g6'],lane) in done:continue
            k=sa+sb
            if core[row['g6']].get(str(k),{}).get('status')=='PASS':
                results.append({'g6':row['g6'],'lane':lane,'core_only':True,'models':0,'intervals':0});save();continue
            P=np.array(row['sides'][str(sa)]['minimal_private_orbits'],dtype=np.uint32)
            Q=np.array(row['sides'][str(sb)]['minimal_private_orbits'],dtype=np.uint32)
            allow=domain(H,P,Q,sa,sb);covered=[0]*len(P);attempted=[0]*len(P)
            begin=len(records);nfail=len(failures)
            for r in by.get(row['g6'],[]):
                rr=seed(r,sa,sb)
                if rr is None:continue
                records.append({'g6':row['g6'],'lane':lane,'sa':sa,'sb':sb,**rr})
                cover(rr,AU,P,Q,covered,sa,sb)
            for rr in records[begin:]:pass
            solves=0
            while True:
                found=None
                for i,(a,c,t) in enumerate(zip(allow,covered,attempted)):
                    rem=a&~c&~t
                    if rem:found=(i,(rem&-rem).bit_length()-1);break
                if found is None:break
                i,j=found;p=int(P[i]);q=int(Q[j]);solves+=1
                r=pair(H,sa,sb,p,q,tlim=2)
                if r['status']!='PASS':r=cut(H,sa,sb,p,q,tlim=3,monotone='bounded')
                if r['status']=='PASS':
                    rec={'g6':row['g6'],'lane':lane,'sa':sa,'sb':sb,'p':p,'q':q,**r}
                    records.append(rec);cover(rec,AU,P,Q,covered,sa,sb)
                else:
                    failures.append({'g6':row['g6'],'lane':lane,'sa':sa,'sb':sb,'p':p,'q':q,**r});attempted[i]|=1<<j
                if solves%10==0:
                    save();print('progress',row['g6'],lane,solves,len(failures)-nfail,round(time.time()-started,1),flush=True)
                if solves>=200:
                    print('LIMIT',row['g6'],lane,flush=True);break
            residual=sum((a&~c).bit_count() for a,c in zip(allow,covered))
            results.append({'g6':row['g6'],'lane':lane,'minimal_pair_models':sum(a.bit_count() for a in allow),'intervals':len(records)-begin,'uncovered_minimal_pairs':residual,'solver_failures':len(failures)-nfail,'solves':solves})
            save();print('CORE',row['g6'],lane,results[-1],round(time.time()-started,1),flush=True)
    out={'records':records,'failures':failures,'results':results,'seconds':time.time()-started,'complete_discovery':all(r.get('uncovered_minimal_pairs',0)==0 for r in results)}
    Path('work/tuza_degree10_c6_monotone_certificates.json').write_text(json.dumps(out))
    print('FINISHED',len(records),len(failures),out['complete_discovery'],time.time()-started,flush=True)
