                                                                                          
from pathlib import Path
from itertools import combinations
import json,subprocess,hashlib
P=Path('work/tuza_degree9_c7_no_side_certificates.json')
rows=json.loads(P.read_text())['records']
fresh=set(subprocess.check_output(['/opt/homebrew/bin/geng','-q','7'],text=True).splitlines())
assert len(rows)==len(fresh)==1044 and len({r['g6']for r in rows})==1044
assert {r['g6']for r in rows}==fresh

def decode(key):
    bits=''.join(format(ord(c)-63,'06b')for c in key[1:]);H=set();i=0
    for b in range(1,7):
        for a in range(b):
            if bits[i]=='1':H.add((a,b))
            i+=1
    return H

def verify(row):
    H=decode(row['g6'])
    if row['kind']=='cone_wke':
        L=H|{(c,7)for c in range(7)}
        Q=set(row['Q']);M=set(map(tuple,row['M']))
        assert Q<=set(range(8))and len(Q)==len(row['Q'])
        assert len(M)==len(row['M'])and M<=L
        endpoints=[v for e in M for v in e]
        assert len(endpoints)==len(set(endpoints))and len(Q)<=len(M)
        assert all(set(e)&Q for e in L-M)
        return 'cone_wke'
    assert row['kind']=='pair'and row['spare']in(0,2)
    E=H|{(c,h)for c in range(7)for h in(7,8)}|{(7,8)}
    X=set(map(tuple,row['X']));assert len(X)==len(row['X'])and X<=E
    used=set()
    for t in row['S']:
        assert len(t)==len(set(t))==3
        es=set(combinations(sorted(t),2));assert es<=E and not es&used
        assert all(e in X for e in es if not set(e)&{7,8})
        used|=es
    assert len(X)+row['spare']<=2*len(row['S'])
    for t in combinations(range(9),3):
        es=set(combinations(t,2))
        if set(t)&{7,8}and es<=E:assert es&X
    return 'spare_two_pair'if row['spare']==2 else'ordinary_pair'

counts={}
for row in rows:
    kind=verify(row);counts[kind]=counts.get(kind,0)+1
assert counts=={'cone_wke':13,'spare_two_pair':1027,'ordinary_pair':4}
negative=0
bad=json.loads(json.dumps(next(r for r in rows if r['kind']=='pair')))
bad['S'].append(bad['S'][0])
try:verify(bad)
except AssertionError:negative+=1
else:raise AssertionError('duplicate triangle accepted')
bad=json.loads(json.dumps(next(r for r in rows if r['kind']=='cone_wke')))
bad['Q']=[]
try:verify(bad)
except AssertionError:negative+=1
else:raise AssertionError('empty cone cover accepted')
assert negative==2
out={'result':'PASS','fresh_core_types':1044,'certificate_counts':counts,'negative_controls':negative,
     'ambient_transfer':'Every pair certificate removes only the two hubs. Every WKE certificate reduces a complete cone link. Neither depends on outside degrees.',
     'payload_sha256':hashlib.sha256(P.read_bytes()).hexdigest()}
Path('work/tuza_degree9_c7_no_side_verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
