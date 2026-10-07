                                                                                    
from pathlib import Path
from itertools import combinations
import json,hashlib,subprocess,time,sys,zipfile,gzip,numpy as np

def input_bytes(path):
    compressed=path.with_suffix(path.suffix+'.gz')
    if compressed.exists():
        with gzip.open(compressed,'rb')as stream:
            return stream.read()
    archive_path=path.parent/'tuza_degree10_c7_resume_cache.zip'
    if archive_path.exists():
        with zipfile.ZipFile(archive_path)as archive:
            if path.name in archive.namelist():
                raw=archive.read(path.name)
                manifest=json.loads(archive.read('manifest.json'))
                assert hashlib.sha256(raw).hexdigest()==manifest[path.name]['sha256']
                return raw
    return path.read_bytes()

base=Path('work');started=time.time()
CP=base/'tuza_degree10_c7_core_certificates.json'
DP=base/'tuza_degree10_c7_side_domain.json'
RP=Path(sys.argv[1])if len(sys.argv)>1 else base/'tuza_degree10_c7_residual_certificates.json'
def read_bound(path):
    raw=input_bytes(path)
    return json.loads(raw),hashlib.sha256(raw).hexdigest()
cores,core_sha=read_bound(CP);domain,domain_sha=read_bound(DP);res,residual_sha=read_bound(RP)
assert cores['complete']and domain['complete']and res['complete']and not res['failures']
proof=json.loads((base/'tuza_degree10_c7_core_verified.json').read_text())
assert proof['result']=='PASS'and proof['payload_sha256']==core_sha
proof=json.loads((base/'tuza_degree10_c7_side_verified.json').read_text())
assert proof['result']=='PASS'and proof['domain_sha256']==domain_sha
fresh=set(subprocess.check_output(['/opt/homebrew/bin/geng','-q','7'],text=True).splitlines())
core_rows={r['g6']:r for r in cores['records']}
assert len(core_rows)==len(cores['records'])==len(fresh)==1044 and set(core_rows)==fresh
need={k for k,r in core_rows.items()if r['certificates']['4']['status']!='PASS'}
assert len(need)==625 and {r['g6']for r in domain['records']}==need

def decode(key):
    stream=[(ord(c)-63>>b)&1 for c in key[1:]for b in range(5,-1,-1)]
    E=set();i=0
    for v in range(1,7):
        for u in range(v):
            if stream[i]:E.add((u,v))
            i+=1
    return E

def local(H,sizes,pats):
    E=set(H)|{(c,h)for c in range(7)for h in(7,8)}|{(7,8)}
    for z,size in enumerate(sizes):
        hub=7+z
        for j in range(size):
            a=9+2*z+j;E.add((hub,a))
            E|={(c,a)for c in range(7)if pats[z]>>(7*j+c)&1}
        if size==2 and pats[z]>>14&1:E.add((9+2*z,10+2*z))
    return E

def variables(size,z):
    return[(c,9+2*z+j)for j in range(size)for c in range(7)]+([(9+2*z,10+2*z)]if size==2 else[])

def literal(row):
    H=decode(row['g6']);sizes=row['sizes'];pats=row['patterns'];E=local(H,sizes,pats)
    assert len(sizes)==len(pats)==2 and all(s in(0,1,2)for s in sizes)
    X=set(map(tuple,row['X']));assert len(X)==len(row['X'])and X<=E
    cut=row.get('type')=='common_subset_cut'
    U=set(row['U'])if cut else{7,8}
    assert {7,8}<=U<=set(range(9))
    used=set()
    for t in row['S']:
        assert len(t)==len(set(t))==3
        es=set(combinations(sorted(t),2));assert es<=E and not es&used
        assert all(e in X for e in es if not set(e)&U)
        used|=es
    cross={(9+j,11+k)for j in range(sizes[0])for k in range(sizes[1])}
    for t in combinations(range(13),3):
        es=set(combinations(t,2))
        if set(t)&U and es<=E|cross:assert es&X
    intervals=[]
    if cut:
        color=row['color'];assert len(color)==13 and set(color)<={0,1}
        assert all(color[9+j]==0 for j in range(sizes[0]))and all(color[11+j]==1 for j in range(sizes[1]))
        assert X=={e for e in E if color[e[0]]==color[e[1]]}
        Z=U-{7,8}
        deficit=sum(10-sum(v in e for e in E)for v in Z)
        assert deficit>=0 and deficit==row['source_deficit']
        if row.get('contact_reserve_codegree'):
            assert row['contact_reserve_codegree']==7
            reserve=0
            for c in range(7):
                if c in Z:continue
                side=color[c];cap=6-sum(c in e for e in H)
                present=sum((c,9+2*side+j)in E for j in range(sizes[side]))
                remaining=min(sizes[side],cap)-present;assert remaining>=0
                reserve+=remaining
            reserve+=sum(size==2 and(9+2*z,10+2*z)not in E for z,size in enumerate(sizes))
        else:
            reserve=sum(e not in E and not set(e)&U and color[e[0]]==color[e[1]]for z,size in enumerate(sizes)for e in variables(size,z))
        assert reserve==row['addition_reserve']
        assert len(X)+deficit+reserve==row['universal_cover_bound']<=2*len(row['S'])
        for z,size in enumerate(sizes):
            req=0;V=variables(size,z)
            for j,e in enumerate(V):
                if e in used or(e in E and set(e)&Z):req|=1<<j
            intervals.append([req,(1<<len(V))-1])
    else:
        assert len(X)<=2*len(row['S'])
        for z,size in enumerate(sizes):
            hub=7+z;req=allow=0
            for j,e in enumerate(variables(size,z)):
                if e in used or(e in X and not row.get('trim_absent_variable_cover',False)):req|=1<<j
                if e[0]<7:
                    c,a=e;hit=e in X or(c,hub)in X or(hub,a)in X
                else:
                    a,b=e;hit=e in X or(hub,a)in X or(hub,b)in X
                if hit:allow|=1<<j
            intervals.append([req,allow])
    assert intervals==row['intervals']
    for p,(r,t)in zip(pats,intervals):assert not r&~p and not p&~t
    return intervals

by_lane={};types={}
for row in res['certificates']:
    assert row['g6']in need and row['status']=='PASS'
    intervals=literal(row);by_lane.setdefault((row['g6'],tuple(row['sizes'])),[]).append(intervals)
    typ=row.get('type','ordinary_pair');types[typ]=types.get(typ,0)+1

def automorphisms(H):
    neighbors=[{b if a==v else a for a,b in H if v in(a,b)}for v in range(7)]
    order=sorted(range(7),key=lambda v:(-len(neighbors[v]),v));out=[];image=[-1]*7
    def visit(i,used):
        if i==7:
            out.append([sum(1<<image[v]for v in range(7)if mask>>v&1)for mask in range(128)]);return
        v=order[i]
        for w in range(7):
            if used>>w&1 or len(neighbors[v])!=len(neighbors[w]):continue
            if any((a in neighbors[v])!=(image[a]in neighbors[w])for a in order[:i]):continue
            image[v]=w;visit(i+1,used|(1<<w));image[v]=-1
    visit(0,0)
    assert out
    return out

def transform(p,size,lut,swap):
    if size==0:return 0
    a=lut[p&127]
    if size==1:return a
    b=lut[p>>7&127]
    if swap:a,b=b,a
    return a|(b<<7)|(p&(1<<14))

def boolbits(values):return int.from_bytes(np.packbits(np.asarray(values,dtype=np.uint8),bitorder='little').tobytes(),'little')

def validity(H,As,Bs):
    nb=[{b if a==v else a for a,b in H if v in(a,b)}for v in range(7)]
    B=np.array(Bs,dtype=np.uint16);constraints=[]
    for x,y in H:
        cap=5-len(nb[x]&nb[y])
        if cap>=4:continue
        bcount=((B>>x&1)*(B>>y&1))+((B>>(x+7)&1)*(B>>(y+7)&1))
        thresholds=[boolbits(bcount<=bound)for bound in(0,1)]
        constraints.append((x,y,cap,thresholds))
    rows=[];full=(1<<len(Bs))-1
    for a in As:
        valid=full
        for x,y,cap,thresholds in constraints:
            acount=((a>>x)&1)*((a>>y)&1)+((a>>(x+7))&1)*((a>>(y+7))&1)
            bound=cap-acount
            if bound<0:valid=0;break
            if bound<2:valid&=thresholds[bound]
        rows.append(valid)
    return rows

expected_rows={};models={};completed=0
for pos,row in enumerate(domain['records']):
    key=row['g6'];H=decode(key);autos=automorphisms(H)
    for sizes in((0,2),(1,2),(2,2)):
        if core_rows[key]['certificates'][str(max(2,sum(sizes)))]['status']=='PASS':continue
        if sizes[0]==0:
            if row['cone_wke']:continue
            As=[0]
        else:As=row['side'+str(sizes[0])]
        Bs=row['side2']
        if not As or not Bs:continue
        valid=validity(H,As,Bs);total=sum(v.bit_count()for v in valid)
        expected_rows[key,sizes]=total
        label=''.join(map(str,sizes));models[label]=models.get(label,0)+total
        arrays=[np.array(As,dtype=np.uint16),np.array(Bs,dtype=np.uint16)]
        covered=[0]*len(As);cache=[{},{}]
        def hit(z,r,t):
            token=(r,t)
            if token not in cache[z]:
                flags=(arrays[z]&r==r)&(arrays[z]&(65535^t)==0)
                cache[z][token]=(np.flatnonzero(flags),boolbits(flags))
            return cache[z][token]
        for interval in by_lane.get((key,sizes),[]):
            seen=set()
            for lut in autos:
                for sw0 in range(1+(sizes[0]==2)):
                    for sw1 in range(1+(sizes[1]==2)):
                        req=[];allow=[]
                        for z,sw in enumerate((sw0,sw1)):
                            r,t=interval[z];req.append(transform(r,sizes[z],lut,sw));allow.append(transform(t,sizes[z],lut,sw))
                        token=tuple(zip(req,allow))
                        if token in seen:continue
                        seen.add(token)
                        ia,ba=hit(0,req[0],allow[0]);ib,bb=hit(1,req[1],allow[1])
                        for i in ia:covered[int(i)]|=bb
                        if sizes[0]==sizes[1]:
                            for i in ib:covered[int(i)]|=ba
        assert all(not(v&~c)for v,c in zip(valid,covered)),(key,sizes)
        completed+=1
    if pos%25==0:print('CORE',pos,'complete_lanes',completed,'models',models,'seconds',round(time.time()-started,1),flush=True)
stored={(r['g6'],tuple(r['sizes'])):r['labelled_ordered_models']for r in res['rows']}
assert len(stored)==len(res['rows'])and stored==expected_rows and models==res['counts']
negative=0;first=res['certificates'][0];bad=json.loads(json.dumps(first));bad['S'].append(bad['S'][0])
try:literal(bad)
except AssertionError:negative+=1
else:raise AssertionError('duplicate triangle accepted')
bad=json.loads(json.dumps(first));bad['intervals'][0][1]^=1
try:literal(bad)
except AssertionError:negative+=1
else:raise AssertionError('wrong interval accepted')
assert negative==2
out={'result':'PASS','full_common_core_types':1044,'residual_core_types':625,'new_complete_lanes':completed,
     'labelled_ordered_contact_models':models,'literal_certificates':len(res['certificates']),'certificate_types':types,
     'negative_controls':negative,'core_sha256':core_sha,
     'domain_sha256':domain_sha,'residual_sha256':residual_sha,
     'seconds':time.time()-started}
output=base/('tuza_degree10_c7_compressed_verified.json'if 'compressed'in RP.name else'tuza_degree10_c7_verified.json')
output.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
