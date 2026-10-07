                                                                                 
import hashlib,itertools,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def decode(key):
    n=ord(key[0])-63;bits=''.join(format(ord(c)-63,'06b')for c in key[1:]);E=set();i=0
    for b in range(1,n):
        for a in range(b):
            if bits[i]=='1':E.add((a,b))
            i+=1
    return n,E

def main():
    snap=ROOT/'tuza_degree10_c6_fresh_source_snapshot'
    raw=json.loads((ROOT/'tuza_degree10_c6_domain.json').read_bytes())['records']
    selected=json.loads((ROOT/'tuza_degree10_c6_density_domain.json').read_bytes())['records']
    source=ROOT/'tuza_degree10_c6_fresh_source_replay.py'
    replay=ROOT/'tuza_degree10_c6_fresh_source_verified.json'
    R=json.loads(replay.read_bytes());assert R['result']=='PASS_FRESH_COMPLETE_RAW_AND_DENSITY_REPLAY'
    assert R['bindings']['fresh_replay_source']['sha256']==digest(source)
    assert R['complete_side_domains']==624 and R['fresh_literal_WKE_intervals']==175058
    expected=set(subprocess.check_output(['/opt/homebrew/bin/geng','-q','6']).decode().splitlines())
    assert len(expected)==len(raw)==len(selected)==156
    assert expected=={r['g6']for r in raw}
    for a,b in zip(raw,selected):
        assert a['g6']==b['g6'] and a['H']==b['H']
        n,E=decode(a['g6']);assert n==6 and E==set(map(tuple,a['H']))
        assert set(a['sides'])==set(b['sides'])==set(map(str,range(4)))
    records={(r['g6'],r['private_size']):r for r in R['records']}
    assert len(records)==len(R['records'])==624
    assert set(records)=={(g6,r)for g6 in expected for r in range(4)}
    for (_,r),row in records.items():assert row['all_boolean_patterns']==1<<(6*r+r*(r-1)//2)
    assert sum(row['literal_WKE_intervals']for row in records.values())==175058
    assert sum(row['all_boolean_patterns']for row in records.values())==328443804
    assert sum(row['selected_canonical_patterns']for row in records.values())==1803814
    for name,binding in R['bindings'].items():
        if name=='fresh_replay_source':continue
        path=snap/name if name.endswith('.dylib')else ROOT/name
        assert digest(path)==binding['sha256'],name
    controls=0
    for kind in ('wrong_H','missing_domain','wrong_source_binding'):
        try:
            if kind=='wrong_H':assert set(map(tuple,raw[0]['H']))|{(0,1)}==decode(raw[0]['g6'])[1]
            elif kind=='missing_domain':assert expected-{next(iter(expected))}==set(records_i[0]for records_i in records)
            else:assert R['bindings']['fresh_replay_source']['sha256']=='0'*64
        except AssertionError:controls+=1
    assert controls==3
    report={'result':'PASS_SOURCE_SCOPE_AND_FRESH_REPORT_BINDINGS','common_types':156,
            'independent_g6_to_H_interface':True,'complete_fresh_domains':624,
            'source_and_immutable_input_bindings_current':True,'negative_controls':controls,
            'fresh_replay_report_sha256':digest(replay),'fresh_replay_source_sha256':digest(source),
            'source_sha256':digest(Path(__file__)),
            'scope':'The raw WKE exclusion and density-selected side quotient are complete. Pair-coverage completion is a separate root-owned proof step.'}
    target=ROOT/'tuza_degree10_c6_source_scope_verified.json';tmp=target.with_suffix('.pending')
    tmp.write_text(json.dumps(report,indent=2));tmp.replace(target);print(json.dumps(report),flush=True)

if __name__=='__main__':main()
