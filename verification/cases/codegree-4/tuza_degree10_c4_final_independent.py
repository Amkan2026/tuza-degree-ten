                                                                                
from copy import deepcopy
from pathlib import Path
import hashlib,json,runpy,sys
import tuza_degree10_c4_density_independent_verify as audit
HERE=Path('work');source=HERE/'tuza_degree10_c4_lex_intervals.json';raw=source.read_bytes();data=json.loads(raw)
assert data['complete']and not data['unresolved']
sys.argv=[__file__,str(source)];audit.main()
runpy.run_path(str(HERE/'tuza_degree10_c4_h12_human_check.py'),run_name='__main__')
ordinary=json.loads((HERE/'tuza_degree10_c4_lex_independent_verified.json').read_text())
human=json.loads((HERE/'tuza_degree10_c4_h12_human_verified.json').read_text())
assert ordinary['verified']and human['result']=='PASS'
assert ordinary['literal_intervals']==1357
catalog=json.loads((HERE/'tuza_degree10_c4_density_sides.json').read_text())
pairs=[(7,9),(8,9),(9,9),(7,10),(8,10),(9,10),(10,10)]
expected={(nl,nr,int(h))for nl,nr in pairs for h,ms in catalog[str(nl)]['core_sides'].items()if ms and catalog[str(nr)]['core_sides'].get(h)}
actual={(r['degrees'][0],r['degrees'][1],r['core'])for r in data['domains']}
assert actual==expected and len(actual)==len(data['domains'])==48
assert all(r['complete']for r in data['domains'])
claims=[(r['degrees'],r['core'],x)for r in data['domains']for x in r.get('human_cases',[])]
assert len(claims)==1 and claims[0][:2]==([9,9],12)and claims[0][2]['key']==[12,1979340,1981500]
uncovered=[r for r in ordinary['reports']if not r['covered']]
assert len(uncovered)==1 and uncovered[0]['degrees']==[9,9]and uncovered[0]['core']==12 and uncovered[0]['first_uncovered']==[[12,1979340,1981500]]
assert sum(r['admitted_after_all_choices']for r in ordinary['reports'])==1109148

def reject(name,f):
 try:f()
 except AssertionError:return name
 raise AssertionError('Negative control accepted: '+name)
first=next(d for d in data['domains']if d['templates']);nl,nr=first['degrees'];h=first['core'];template=first['templates'][0]
a=deepcopy(template);a['X']=[];b=deepcopy(template);b['S'].append(deepcopy(b['S'][0]))
caps=ordinary['initial_density_private_caps'];derived={int(h):v for h,v in caps.items()};wrong=dict(caps);k=next(iter(wrong));wrong[k]+=1
controls=[reject('empty cover',lambda:audit.literal_interval(nl,nr,h,a)),reject('duplicate packed triangle',lambda:audit.literal_interval(nl,nr,h,b)),reject('wrong initial partner cap',lambda:audit.assert_caps_equal(wrong,derived))]
assert source.read_bytes()==raw
report={'result':'PASS','source_file':str(source),'source_sha256':hashlib.sha256(raw).hexdigest(),'all_48_domains_match_initial_catalog':True,'domains':sorted(map(list,actual)),'admitted_models':1109148,'ordinary_literal_intervals':1357,'human_forced_cross_cases':1,'uncovered_after_human_case':0,'raw_complete_side_counts':ordinary['raw_side_counts'],'density_side_exclusions':ordinary['density_side_exclusions'],'literal_private_bound_witnesses':ordinary['literal_private_bound_witnesses'],'negative_controls_rejected':controls,'scope':'Every maximum-codegree-four selected-edge domain with an endpoint of degree nine or ten, under maximum degree ten. The global proof supplies endpoint degrees at most eight separately, and uses the ambient degree independent order-five component lemma and the human thin-six lemma to establish minimum degree seven and connected links.'}
(HERE/'tuza_degree10_c4_final_verified.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
