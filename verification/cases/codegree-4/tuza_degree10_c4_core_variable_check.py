                                                                          

                                                                             
   
from copy import deepcopy
from itertools import combinations
from pathlib import Path
import hashlib,json,sys,time
import tuza_degree10_c4_density_independent_verify as audit

HERE=Path('work');started=time.monotonic()
path=HERE/'tuza_degree10_c4_core_variable_compressed.json';raw=path.read_bytes();data=json.loads(raw)
assert data['complete'];rows=data['intervals'];assert len(rows)==341
sourcepath=HERE/'tuza_degree10_c4_lex_intervals.json';sourcebytes=sourcepath.read_bytes();old=json.loads(sourcebytes)

def literal(row):
    nl,nr=row['degrees'];R,F,T,V=map(lambda es:{tuple(e)for e in es},row['signature'])
    rc,fc=row['Rcore'],row['Fcore'];assert 0<=rc<64 and 0<=fc<64 and not rc&fc
    assert not R&F and not T&V and R|F<=set(audit.potentials(nl))and T|V<=set(audit.potentials(nr))
    lower=audit.pair_base(nl,nr,rc)|{audit.side_to_pair(e,nl,0)for e in R}|{audit.side_to_pair(e,nl,1)for e in T}
    upper=audit.pair_base(nl,nr,63^fc)|{audit.side_to_pair(e,nl,0)for e in set(audit.potentials(nl))-F}|{audit.side_to_pair(e,nl,1)for e in set(audit.potentials(nr))-V}
    X={tuple(e)for e in row['X']};S=row['S'];assert S and X<=lower and len(X)==len(row['X'])and len(X)<=2*len(S)
    used=[]
    for tri in S:
        E={audit.edge(a,b)for a,b in combinations(tri,2)}
        assert len(set(tri))==3 and E<=lower
        assert all(set(e)&{0,1}or e in X for e in E);used.extend(E)
    assert len(used)==len(set(used))
    for tri in combinations(range(nl+nr-4),3):
        E={audit.edge(a,b)for a,b in combinations(tri,2)}
        if set(tri)&{0,1}and E<=upper:assert E&X

for row in rows:literal(row)
expanded=deepcopy(old);count=0
for domain in expanded['domains']:
    nl,nr=domain['degrees'];h=domain['core'];domain['templates']=[]
    autos=[p for p in audit.CP if audit.image_core(h,p)==h]
    for case,row in enumerate(rows):
        if row['degrees']!=domain['degrees']:continue
        seen=set()
        for p in audit.CP:
            if p in seen:continue
            rc=audit.image_core(row['Rcore'],p);fc=audit.image_core(row['Fcore'],p)
            if h&rc!=rc or h&fc:continue
            seen|={tuple(a[p[i]]for i in range(4))for a in autos}
            mp={v:v for v in range(nl+nr-4)};mp.update({c+2:p[c]+2 for c in range(4)})
            signature=[]
            for part in row['signature']:
                signature.append([list(audit.edge(p[a]if a<4 else a,p[b]if b<4 else b))for a,b in part])
            transformed={'signature':signature,'S':[[mp[v]for v in tri]for tri in row['S']],
                         'X':[list(audit.edge(mp[a],mp[b]))for a,b in row['X']],
                         'core_variable_case':case,'common_map':p}
            audit.literal_interval(nl,nr,h,transformed)
            domain['templates'].append(transformed);count+=1
replay_path=HERE/'tuza_degree10_c4_core_variable_lex_intervals_replay.json'
replay_path.write_text(json.dumps(expanded)+'\n')
sys.argv=[__file__,str(replay_path)]
audit.main(report_target='tuza_degree10_c4_core_variable_replay_verified.json')
replay=json.loads((HERE/'tuza_degree10_c4_core_variable_replay_verified.json').read_text())
initial=json.loads((HERE/'tuza_degree10_c4_final_verified.json').read_text())
assert initial['result']=='PASS'and initial['source_sha256']==hashlib.sha256(sourcebytes).hexdigest()
actual={(r['degrees'][0],r['degrees'][1],r['core'])for r in replay['reports']}
assert actual=={tuple(x)for x in initial['domains']}and len(actual)==len(replay['reports'])==48
uncovered=[r for r in replay['reports']if not r['covered']]
assert len(uncovered)==1 and uncovered[0]['degrees']==[9,9]and uncovered[0]['core']==12
assert uncovered[0]['first_uncovered']==[[12,1979340,1981500]]
human=json.loads((HERE/'tuza_degree10_c4_h12_human_verified.json').read_text())
assert human['result']=='PASS'and human['hard_pair_cross_orbit_size']==16
controls=[]
for name,mutator in [('empty cover',lambda r:r.update(X=[])),('duplicate packed triangle',lambda r:r['S'].append(deepcopy(r['S'][0])))]:
    bad=deepcopy(rows[0]);mutator(bad)
    try:literal(bad)
    except AssertionError:controls.append(name)
    else:raise AssertionError('Negative control accepted: '+name)
assert path.read_bytes()==raw and sourcepath.read_bytes()==sourcebytes
out={'verified':True,'compressed_intervals':len(rows),'projection_intervals':sum('projection'in r for r in rows),
     'literal_lower_upper_checks':len(rows),'fixed_core_expansion_rows':count,'all_48_domains_verified':True,
     'admitted_models':sum(r['admitted_after_all_choices']for r in replay['reports']),
     'ordinary_uncovered_before_human_case':1,'uncovered_after_human_case':0,'negative_controls_rejected':controls,
     'compressed_source_sha256':hashlib.sha256(raw).hexdigest(),'original_source_sha256':hashlib.sha256(sourcebytes).hexdigest(),
     'seconds':time.monotonic()-started,'scope':'The generalized intervals cover the same selected-edge domains as the completed c4 proof.'}
(HERE/'tuza_degree10_c4_core_variable_verified.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
