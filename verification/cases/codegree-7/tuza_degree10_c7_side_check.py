                                                                                      
from pathlib import Path
from itertools import combinations
import json,subprocess,hashlib,time,numpy as np

base=Path('work');started=time.time()
core_path=base/'tuza_degree10_c7_core_certificates.json'
domain_path=base/'tuza_degree10_c7_side_domain.json'
wke_path=base/'tuza_degree10_c7_side_wke_intervals.json'
core=json.loads(core_path.read_text());domain=json.loads(domain_path.read_text());wke=json.loads(wke_path.read_text())
assert core['complete']and domain['complete']and wke['complete']
fresh=set(subprocess.check_output(['/opt/homebrew/bin/geng','-q','7'],text=True).splitlines())
assert len(fresh)==1044 and {r['g6']for r in core['records']}==fresh
core_proof=json.loads((base/'tuza_degree10_c7_core_verified.json').read_text())
assert core_proof['result']=='PASS'and core_proof['payload_sha256']==hashlib.sha256(core_path.read_bytes()).hexdigest()
needed={r['g6']for r in core['records']if r['certificates']['4']['status']!='PASS'}
assert len(needed)==625 and {r['g6']for r in domain['records']}==needed

def decode(key):
    values=[ord(c)-63 for c in key[1:]];bits=[(v>>j)&1 for v in values for j in range(5,-1,-1)]
    E=set();i=0
    for b in range(1,7):
        for a in range(b):
            if bits[i]:E.add((a,b))
            i+=1
    return E

def legal_patterns(H,size):
    pats=np.arange(1<<(7*size+(size==2)),dtype=np.uint16)
    d=[pats&127]
    if size==2:d.append((pats>>7)&127)
    internal=(pats>>14)&1 if size==2 else np.zeros(len(pats),dtype=np.uint16)
    if size==1:ok=d[0]>0
    else:ok=((d[0]>0)&(d[1]>0))|((internal==1)&((d[0]|d[1])>0))
    pop=np.array([bin(z).count('1')for z in range(128)],dtype=np.uint8)
    for contacts in d:ok&=pop[contacts]+internal<=7
    neighbors=[{b if a==v else a for a,b in H if v in(a,b)}for v in range(7)]
    for v in range(7):
        count=sum((contacts>>v)&1 for contacts in d)
        ok&=count<=6-len(neighbors[v])
    for a,b in H:
        count=sum(((contacts>>a)&1)*((contacts>>b)&1)for contacts in d)
        ok&=count<=5-len(neighbors[a]&neighbors[b])
    return pats[ok]

def matching_cover(E,row):
    Q=set(row['Q']);M=set(map(tuple,row['M']))
    assert len(Q)==len(row['Q'])and len(M)==len(row['M'])and M<=E
    vertices=[v for e in M for v in e]
    assert len(vertices)==len(set(vertices))and len(Q)<=len(M)
    assert all(set(e)&Q for e in E-M)

cone=json.loads((base/'tuza_degree10_c7_cone_wke_certificates.json').read_text())['records']
cone_map={r['g6']:r for r in cone}
assert len(cone_map)==len(cone)==520
assert set(cone_map)=={r['g6']for r in domain['records']if r['cone_wke']}
for key,r in cone_map.items():
    assert set(r['Q'])<=set(range(8))
    matching_cover(decode(key)|{(c,7)for c in range(7)},r)

records={(r['g6'],r['size']):r for r in wke['records']}
assert len(records)==len(wke['records'])==1250
legal_count=inside_count=interval_count=0
for i,row in enumerate(domain['records']):
    H=decode(row['g6'])
    fixed=H|{(c,7)for c in range(7)}
    for size in(1,2):
        pats=legal_patterns(H,size);legal_count+=len(pats)
        inside=set(row['side'+str(size)]);inside_count+=len(inside)
        assert len(inside)==len(row['side'+str(size)])and inside<=set(map(int,pats))
        intervals=records[row['g6'],size]['intervals'];interval_count+=len(intervals)
        assert records[row['g6'],size]['legal_count']==len(pats)
        variables=[(c,8+j)for j in range(size)for c in range(7)]+([(8,9)]if size==2 else[])
        covered=np.zeros(len(pats),dtype=bool)
        for cert in intervals:
            required=cert['required'];forbidden=cert['forbidden']
            assert 0<=required<(1<<len(variables))and 0<=forbidden<(1<<len(variables))and not required&forbidden
            minimum=fixed|{e for j,e in enumerate(variables)if required>>j&1}
            maximum=fixed|{e for j,e in enumerate(variables)if not(forbidden>>j&1)}
            assert set(cert['Q'])<=set(range(8+size))
            matching_cover(minimum,cert)
                                                                               
            M=set(map(tuple,cert['M']));Q=set(cert['Q'])
            assert all(set(e)&Q for e in maximum-M)
            covered|=(pats&required==required)&(pats&forbidden==0)
        wanted=np.array([int(p)not in inside for p in pats],dtype=bool)
        assert np.array_equal(covered,wanted),(row['g6'],size)
    if i%100==0:print('CORE',i,'legal',legal_count,'intervals',interval_count,'seconds',round(time.time()-started,1),flush=True)
assert legal_count==13546254 and inside_count==4473122 and interval_count==140073
negative=0;key,r=next(iter(cone_map.items()));bad=json.loads(json.dumps(r));bad['M'].append(bad['M'][0])
try:matching_cover(decode(key)|{(c,7)for c in range(7)},bad)
except AssertionError:negative+=1
else:raise AssertionError('duplicate matching edge accepted')
bad=json.loads(json.dumps(r));bad['Q']=[]
try:matching_cover(decode(key)|{(c,7)for c in range(7)},bad)
except AssertionError:negative+=1
else:raise AssertionError('empty cover accepted')
assert negative==2
out={'result':'PASS','full_core_types':1044,'residual_core_types':625,'all_legal_single_side_patterns':legal_count,
     'remaining_single_side_patterns':inside_count,'positive_WKE_intervals':interval_count,'positive_cone_witnesses':520,
     'negative_controls':negative,'domain_sha256':hashlib.sha256(domain_path.read_bytes()).hexdigest(),
     'WKE_sha256':hashlib.sha256(wke_path.read_bytes()).hexdigest(),'seconds':time.time()-started}
(base/'tuza_degree10_c7_side_verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
