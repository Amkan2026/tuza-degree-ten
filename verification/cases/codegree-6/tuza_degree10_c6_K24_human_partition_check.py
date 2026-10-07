from pathlib import Path
import hashlib,json
P=Path('work');source=P/'tuza_degree10_c6_K24_residual_pairs.json';data=json.loads(source.read_bytes());pairs=list(map(tuple,data['residual_pairs']))
def profile(p):
    contacts=[p&63,p>>6&63];leaf=[z&15 for z in contacts];center=[z>>4 for z in contacts];internal=bool(p&4096)
    if internal:
        for j in (0,1):
            if leaf[j]==15 and center[j] in (1,2) and center[1-j]==0 and leaf[1-j].bit_count()>=3:
                return 'single_center_private_edge',{'full_private':j,'center':center[j],'leaf_contacts':leaf}
    if leaf==[15,15]:
        if not internal and sorted(center)==[0,3]:return 'full_leaf_basic',{'form':0,'center':center}
        if sorted(center)==[1,2]:return 'full_leaf_basic',{'form':2 if internal else 1,'center':center}
    if leaf[0]==leaf[1] and leaf[0].bit_count()==2 and sorted(center)==[1,2]:
        return 'two_leaf',{'leaf_pair':leaf[0],'center':center,'internal':internal}
    raise ValueError(('Unclassified private side',p))
records=[];counts={}
for p,q in pairs:
    a,aa=profile(p);b,bb=profile(q)
    if a==b=='single_center_private_edge':case='two_private_edges'
    elif {a,b}=={'single_center_private_edge','full_leaf_basic'}:case='one_private_edge'
    elif a==b=='full_leaf_basic':case='full_leaf'
    elif a==b=='two_leaf':
        assert aa['leaf_pair']^bb['leaf_pair']==15 and not aa['leaf_pair']&bb['leaf_pair']
        case='two_leaf'
    else:raise ValueError(('Unclassified pair',p,q,a,b))
    counts[case]=counts.get(case,0)+1;records.append({'p':p,'q':q,'human_case':case,'first_profile':aa,'second_profile':bb})
assert len(pairs)==len(set(pairs))==193
assert counts=={'full_leaf':9,'one_private_edge':60,'two_leaf':24,'two_private_edges':100} or counts==dict(full_leaf=9,one_private_edge=60,two_leaf=24,two_private_edges=100)
files={}
for case,stem in [('two_private_edges','private_edges'),('one_private_edge','one_private_edge'),('full_leaf','full_leaf'),('two_leaf','two_leaf')]:
    report=P/f'tuza_degree10_c6_K24_{stem}_human_verified.json';proof=P/f'tuza_degree10_c6_K24_{stem}_human_proof.txt';check=P/f'tuza_degree10_c6_K24_{stem}_human_check.py';r=json.loads(report.read_bytes())
    assert r['status']=='PASS'
    assert hashlib.sha256(proof.read_bytes()).hexdigest()==r['proof_sha256']
    assert hashlib.sha256(check.read_bytes()).hexdigest()==r['source_sha256']
    files[case]={'proof':proof.name,'proof_sha256':r['proof_sha256'],'checker':check.name,'checker_sha256':r['source_sha256'],'verified_report':report.name,'verified_report_sha256':hashlib.sha256(report.read_bytes()).hexdigest()}
out={'status':'PASS','ordered_residual_pairs':193,'cross_patterns_per_pair':16,'human_case_counts':counts,'all_cases_have_complete_human_proofs':True,'source_residual_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'proof_binding':files,'records':records,'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
dest=P/'tuza_degree10_c6_K24_human_partition_verified.json';tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(dest);print(json.dumps({k:v for k,v in out.items() if k!='records'}))
