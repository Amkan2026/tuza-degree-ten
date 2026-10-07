import itertools,json,sys,time,zlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'work')
from tuza_degree10_c6_solve import pair,cut,graph,variables
from tuza_degree10_c6_monotone_probe import autos,required
from tuza_degree10_c6_cached_patterns import read_pattern_bytes

def bits(v):return int.from_bytes(np.packbits(v,bitorder='little').tobytes(),'little')

def permute_array(P,r,q):
    ans=np.zeros(len(P),dtype=np.uint32)
    for j in range(r):ans|=((P>>(6*j))&63)<<(6*q[j])
    V=list(itertools.combinations(range(r),2))
    for i,(a,b) in enumerate(V):
        j=V.index(tuple(sorted((q[a],q[b]))))
        ans|=((P>>(6*r+i))&1)<<(6*r+j)
    return ans

def patterns(row,r):
    P=np.frombuffer(zlib.decompress(read_pattern_bytes(row['sides'][str(r)]['file'])),dtype='<u4')
    out=P.copy()
    for q in itertools.permutations(range(r)):out=np.minimum(out,permute_array(P,r,q))
    return np.unique(out)

class Rectangles:
    def __init__(self,n,m):
        self.fullP=(1<<n)-1;self.fullQ=(1<<m)-1
        self.parts={0:self.fullP} if n and m else {}
        self.steps=0
    def add(self,I,J):
        if not I or not J:return
        out={}
        for C,K in self.parts.items():
            if not J&~C:
                out[C]=out.get(C,0)|K;continue
            hit=K&I;miss=K^hit
            if miss:out[C]=out.get(C,0)|miss
            if hit:
                D=C|J;out[D]=out.get(D,0)|hit
        self.parts=out;self.steps+=1
    def first(self):
        for C,K in self.parts.items():
            rem=self.fullQ&~C
            if K and rem:return ((K&-K).bit_length()-1,(rem&-rem).bit_length()-1)
        return None
    def residual(self):return sum(K.bit_count()*(self.fullQ&~C).bit_count() for C,K in self.parts.items())

def common_maps(AU):return [[sum(1<<p[c] for c in range(6) if d>>c&1) for d in range(64)] for p in AU]

def trans(p,r,cm,pp):
    ans=sum(cm[(p>>(6*j))&63]<<(6*pp[j]) for j in range(r))
    V=list(itertools.combinations(range(r),2))
    for i,(a,b) in enumerate(V):
        if p>>(6*r+i)&1:ans|=1<<(6*r+V.index(tuple(sorted((pp[a],pp[b])))))
    return ans

def side_variants(lo,F,r,cm):return tuple(sorted({(trans(lo,r,cm,p),trans(F,r,cm,p)) for p in itertools.permutations(range(r))}))

def fit(P,v):
    ans=np.zeros(len(P),dtype=bool)
    for a,f in v:ans|=(P&a==a)&(P&f==0)
    return ans

def pair_interval(rec,sa,sb):
    X={tuple(e) for e in rec['X']};S=rec['S'];result=[]
    for r,first,u in [(sa,8,6),(sb,11,7)]:
        lo=required(S,r,first);F=0
        for i,e in enumerate(variables(r,first)):
            if e not in X and all(tuple(sorted((u,v))) not in X for v in e):F|=1<<i
        assert not lo&F
        result.append((lo,F))
    return result

def cover_pair(rec,AU,CM,P,Q,R,sa,sb):
    aa,bb=pair_interval(rec,sa,sb);seen=set()
    for cm in CM:
        av=side_variants(*aa,sa,cm);bv=side_variants(*bb,sb,cm)
        options=[(av,bv)]+([(bv,av)] if sa==sb else [])
        for a,b in options:
            if (a,b) in seen:continue
            seen.add((a,b));R.add(bits(fit(P,a)),bits(fit(Q,b)))

def counts(P,r,a,b=None):
    out=np.zeros(len(P),dtype=np.int16)
    for j in range(r):
        hit=(P>>(6*j+a)&1)>0
        if b is not None:hit&=(P>>(6*j+b)&1)>0
        out+=hit
    return out

def exclude(H,P,Q,R,sa,sb):
    H={tuple(e) for e in H}
    for a,b in H:
        com=sum(tuple(sorted((a,c))) in H and tuple(sorted((b,c))) in H for c in range(6) if c not in (a,b))
        cap=4-com;ca=counts(P,sa,a,b);cb=counts(Q,sb,a,b)
        for k in np.unique(ca):R.add(bits(ca==k),bits(cb>cap-k))
    for c in range(6):
        if not any(c in e for e in H):R.add(bits(counts(P,sa,c)==0),bits(counts(Q,sb,c)==0))

def weight(P,r,positive,negative):
    val=np.zeros(len(P),dtype=np.int16)
    for c in range(6):
        k=int(c in positive)-int(c in negative)
        if k:val+=k*counts(P,r,c)
    for i in range(r*(r-1)//2):val+=(P>>(6*r+i)&1).astype(np.int16)
    return val

def cover_cut(rec,H,AU,CM,P,Q,R,sa,sb):
    assert set(rec['U'])<=set(range(8)) and {6,7}<=set(rec['U'])
    Z={c for c in rec['U'] if c<6};col=rec['colors'];S=rec['S']
    baseline=graph(H,sa,sb,0,0)[0]
    const=sum(col[a]==col[b] for a,b in baseline)+sum(8-sum(c in e for e in H) for c in Z)
    aa=required(S,sa,8);bb=required(S,sb,11);seen=set()
    for p,cm in zip(AU,CM):
        nz={p[c] for c in Z};c0={p[c] for c in range(6) if col[c]==0};c1=set(range(6))-c0
        av=side_variants(aa,0,sa,cm);bv=side_variants(bb,0,sb,cm)
        opts=[(av,bv,c0,c1)]
        if sa==sb:opts.append((bv,av,c1,c0))
        for a,b,pa,pb in opts:
            key=(a,b,tuple(sorted(pa)),tuple(sorted(pb)),tuple(sorted(nz)))
            if key in seen:continue
            seen.add(key)
            AP=fit(P,a);BQ=fit(Q,b);L=weight(P,sa,pa,nz);V=weight(Q,sb,pb,nz)
            for v in np.unique(L[AP]):R.add(bits(AP&(L==v)),bits(BQ&(const+v+V<=2*len(S))))

if __name__=='__main__':
    started=time.time()
    dom=json.loads(Path('work/tuza_degree10_c6_domain.json').read_text())['records']
    core={r['g6']:r['certificates'] for r in json.loads(Path('work/tuza_degree10_c6_core_certificates.json').read_text())['records']}
    preliminary=json.loads(Path('work/tuza_degree10_c6_monotone_checkpoint.json').read_text())['records']
    prior={}
    for r in preliminary:
        if r['kind']=='pair':prior.setdefault((r['g6'],r['lane']),[]).append(r)
    checkpoint=Path('work/tuza_degree10_c6_full_rectangles_checkpoint.json')
    records=[];fails=[];reports=[]
    if checkpoint.exists():
        o=json.loads(checkpoint.read_text());records=o['records'];fails=o['failures'];reports=o['reports']
    done={(r['g6'],r['lane']) for r in reports}
    def save():checkpoint.write_text(json.dumps({'records':records,'failures':fails,'reports':reports,'seconds':time.time()-started}))
    for row in dom:
        H=row['H'];AU=autos(H);CM=common_maps(AU);PP={r:patterns(row,r) for r in range(4)}
        for sa,sb in [(0,3),(1,3),(2,3),(3,3),(2,2)]:
            lane=f'{7+sa}/{7+sb}'
            if (row['g6'],lane) in done:continue
            if core[row['g6']].get(str(sa+sb),{}).get('status')=='PASS':
                reports.append({'g6':row['g6'],'lane':lane,'core_only':True,'residual':0});save();continue
            P=PP[sa];Q=PP[sb];R=Rectangles(len(P),len(Q));exclude(H,P,Q,R,sa,sb)
            before=len(records);failed=False
            for r in prior.get((row['g6'],lane),[]):
                records.append(r);cover_pair(r,AU,CM,P,Q,R,sa,sb)
            solves=0
            while R.first() is not None:
                i,j=R.first();p=int(P[i]);q=int(Q[j]);solves+=1
                ans=pair(H,sa,sb,p,q,fixed=False,tlim=3)
                if ans['status']!='PASS':ans=cut(H,sa,sb,p,q,tlim=5)
                rec={'g6':row['g6'],'lane':lane,'sa':sa,'sb':sb,'p':p,'q':q,**ans}
                if ans['status']!='PASS':
                    fails.append(rec);failed=True;save();print('GAP',row['g6'],lane,p,q,ans['status'],flush=True);break
                records.append(rec)
                if ans['kind']=='pair':cover_pair(rec,AU,CM,P,Q,R,sa,sb)
                else:cover_cut(rec,H,AU,CM,P,Q,R,sa,sb)
                save()
                if solves%10==0:print('progress',row['g6'],lane,solves,len(R.parts),R.residual(),round(time.time()-started,1),flush=True)
                if solves>=300:
                    failed=True;print('LIMIT',row['g6'],lane,flush=True);break
            reports.append({'g6':row['g6'],'lane':lane,'canonical_full_side_counts':[len(P),len(Q)],'rectangles':len(R.parts),'certificates':len(records)-before,'solves':solves,'residual':R.residual(),'closed_discovery':not failed and R.first() is None})
            save();print('CORE',row['g6'],lane,reports[-1],round(time.time()-started,1),flush=True)
    result={'records':records,'failures':fails,'reports':reports,'complete_discovery':all(r['residual']==0 for r in reports),'seconds':time.time()-started}
    Path('work/tuza_degree10_c6_full_rectangles_certificates.json').write_text(json.dumps(result))
    print('FINISHED',len(records),len(fails),result['complete_discovery'],time.time()-started,flush=True)
