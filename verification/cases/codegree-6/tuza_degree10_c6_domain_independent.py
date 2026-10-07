                                                                            
import ctypes,hashlib,itertools,json,time,zlib
from pathlib import Path
import numpy as np

lib=ctypes.CDLL(str(Path('work/tuza_degree10_c6_domain_independent.dylib').resolve()))
lib.verify_domain.argtypes=[ctypes.c_uint,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_int,ctypes.c_char_p,ctypes.POINTER(ctypes.c_uint64)]
lib.verify_domain.restype=ctypes.c_int
dest=Path('work/tuza_degree10_c6_wke_intervals');dest.mkdir(exist_ok=True)
report=Path('work/tuza_degree10_c6_domain_independent_checkpoint.json')
rows=[]
if report.exists():rows=json.loads(report.read_text())['records']
done={(x['g6'],x['private_size']) for x in rows}
start=time.time()
domain=json.loads(Path('work/tuza_degree10_c6_domain.json').read_text())['records']
assert len(domain)==156 and len({r['g6'] for r in domain})==156
P6=list(itertools.combinations(range(6),2))
for idx,row in enumerate(domain):
    hm=sum(1<<i for i,e in enumerate(P6) if list(e) in row['H'])
    for r in range(4):
        if (row['g6'],r) in done:continue
        side=row['sides'][str(r)];b=Path(side['file']).read_bytes()
        P=np.frombuffer(zlib.decompress(b),dtype='<u4')
        assert len(P)==side['raw_patterns']
        out=dest/f'{idx:03d}_{r}.txt'
        stats=(ctypes.c_uint64*6)()
        status=lib.verify_domain(hm,r,P.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),len(P),str(out).encode(),stats)
        assert status==1,(row['g6'],r,status)
        a=list(stats)
        rows.append({'g6':row['g6'],'private_size':r,'result':'PASS','all_boolean_patterns':a[0],'legal_connected_patterns':a[1],'retained_candidate_patterns':a[2],'excluded_positive_WKE_patterns':a[3],'literal_WKE_intervals':a[4],'patterns_file':side['file'],'patterns_sha256':hashlib.sha256(b).hexdigest(),'WKE_file':str(out),'WKE_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        report.write_text(json.dumps({'records':rows,'seconds':time.time()-start},indent=2))
        if r==3:print(idx,row['g6'],a,round(time.time()-start,1),flush=True)
assert len(rows)==624
out={'result':'PASS','complete_side_domains':624,'common_graph_types':156,'scope':'Every omitted legal connected side pattern has a positive literal WKE witness; all non-WKE sides lie in the retained candidate domain. Retained patterns need not themselves be certified non-WKE.','total_positive_WKE_intervals':sum(r['literal_WKE_intervals'] for r in rows),'total_retained_patterns':sum(r['retained_candidate_patterns'] for r in rows),'records':rows,'seconds':time.time()-start}
Path('work/tuza_degree10_c6_domain_independent_verified.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='records'}),flush=True)
