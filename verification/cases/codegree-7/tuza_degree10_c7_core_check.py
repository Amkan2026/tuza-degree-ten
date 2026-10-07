                                                                               
from pathlib import Path
from itertools import combinations
import json,subprocess,hashlib

P=Path('work/tuza_degree10_c7_core_certificates.json')
D=json.loads(P.read_text())
assert D['complete']
fresh=set(subprocess.check_output(['/opt/homebrew/bin/geng','-q','7'],text=True).splitlines())
assert len(D['records'])==len(fresh)==1044 and {r['g6']for r in D['records']}==fresh
def core(key):
    bits=''.join(format(ord(c)-63,'06b')for c in key[1:])
    H=set();j=0
    for b in range(1,7):
        for a in range(b):
            if bits[j]=='1':H.add((a,b))
            j+=1
    return H
def replay(H,row,k):
    E=H|{(a,h)for a in range(7)for h in(7,8)}|{(7,8)}
    X=set(map(tuple,row['X']))
    assert len(X)==len(row['X'])and X<=E
    used=set()
    for t in row['S']:
        assert len(t)==len(set(t))==3
        es=set(combinations(sorted(t),2))
        assert es<=E and not es&used
        assert all(e in X for e in es if not set(e)&{7,8})
        used|=es
    assert len(X)+k<=2*len(row['S'])
    for t in combinations(range(9),3):
        es=set(combinations(t,2))
        if set(t)&{7,8}and es<=E:assert es&X
counts={k:0 for k in('4','3','2')}
for r in D['records']:
    H=core(r['g6'])
    for k,c in r['certificates'].items():
        if c['status']=='PASS':replay(H,c,int(k));counts[k]+=1
first=next((r,c,k)for r in D['records']for k,c in r['certificates'].items()if c['status']=='PASS')
r,c,k=first;bad=json.loads(json.dumps(c));bad['S'].append(bad['S'][0]);neg=0
try:replay(core(r['g6']),bad,int(k))
except AssertionError:neg+=1
assert neg==1
out={'result':'PASS','full_core_types':1044,'spare_counts':counts,'negative_controls':neg,'payload_sha256':hashlib.sha256(P.read_bytes()).hexdigest()}
Path('work/tuza_degree10_c7_core_verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
