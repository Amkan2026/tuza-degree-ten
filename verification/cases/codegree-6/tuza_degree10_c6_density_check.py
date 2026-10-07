import ctypes,hashlib,itertools,json,time,zlib,sys,zipfile
from pathlib import Path
import numpy as np
sys.path.insert(0,'work')
from tuza_degree10_c6_cached_patterns import read_pattern_bytes
from tuza_degree10_c6_full_rectangles import patterns
from tuza_degree10_c6_density import density_admitted
lib=ctypes.CDLL(str(Path('work/tuza_degree10_c6_density_check.dylib').resolve()))
U32=ctypes.POINTER(ctypes.c_uint32)
lib.check_density.argtypes=[ctypes.c_uint,ctypes.c_int,U32,ctypes.c_int,U32,ctypes.c_int,ctypes.POINTER(ctypes.c_uint64)]
lib.check_density.restype=ctypes.c_int
raw=json.loads(Path('work/tuza_degree10_c6_domain.json').read_text())['records']
sel=json.loads(Path('work/tuza_degree10_c6_density_domain.json').read_text())['records']
assert len(raw)==len(sel)==156
start=time.time();rows=[];pairs=list(itertools.combinations(range(6),2));controls=[]
selected_cache=zipfile.ZipFile('work/tuza_degree10_c6_density_patterns_cache.tmp','w',zipfile.ZIP_STORED)
for a,b in zip(raw,sel):
    assert a['g6']==b['g6'] and a['H']==b['H']
    hm=sum(1<<i for i,e in enumerate(pairs) if list(e) in a['H'])
    for r in range(4):
        rb=read_pattern_bytes(a['sides'][str(r)]['file'])
        P=np.frombuffer(zlib.decompress(rb),dtype='<u4')
        candidates=patterns(a,r);keep=density_admitted(a['H'],candidates,r)
        Q=candidates[keep].astype('<u4');sb=zlib.compress(Q.tobytes())
        assert len(Q)==b['sides'][str(r)]['selected_density_candidates']
        stats=(ctypes.c_uint64*3)();status=lib.check_density(hm,r,P.ctypes.data_as(U32),len(P),Q.ctypes.data_as(U32),len(Q),stats)
        assert status==1,(a['g6'],r,status)
        if not controls and len(Q):
            omitted=Q[1:].copy();duplicate=np.insert(Q,0,Q[0]).astype('<u4')
            for name,bad in [('omitted_required_pattern',omitted),('duplicate_selected_pattern',duplicate)]:
                result=lib.check_density(hm,r,P.ctypes.data_as(U32),len(P),bad.ctypes.data_as(U32),len(bad),stats)
                assert result<0,(name,result)
                controls.append({'mutation':name,'rejected':True,'status':result})
        if len(controls)==2 and (~keep).any():
            bad=np.sort(np.append(Q,candidates[~keep][0])).astype('<u4')
            result=lib.check_density(hm,r,P.ctypes.data_as(U32),len(P),bad.ctypes.data_as(U32),len(bad),stats)
            assert result<0,('included_excluded_pattern',result)
            controls.append({'mutation':'included_excluded_pattern','rejected':True,'status':result})
        stats=(ctypes.c_uint64*3)()
        assert lib.check_density(hm,r,P.ctypes.data_as(U32),len(P),Q.ctypes.data_as(U32),len(Q),stats)==1
        selected_cache.writestr(b['sides'][str(r)]['file'],sb)
        rows.append({'g6':a['g6'],'private_size':r,'raw_retained_patterns':len(P),'selected_canonical_patterns':len(Q),'selected_raw_patterns':stats[1],'excluded_raw_patterns':stats[2],'raw_sha256':hashlib.sha256(rb).hexdigest(),'selected_sha256':hashlib.sha256(sb).hexdigest()})
    print(a['g6'],round(time.time()-start,1),flush=True)
assert len(rows)==624 and len(controls)==3
selected_cache.writestr('manifest.json',json.dumps(rows,indent=2));selected_cache.close()
Path('work/tuza_degree10_c6_density_patterns_cache.tmp').replace('work/tuza_degree10_c6_density_patterns_cache.zip')
out={'result':'PASS','complete_side_domains':624,'fresh_graph_reconstruction':True,'independent_private_quotient':True,'selected_arrays_regenerated_then_independently_verified':True,'selected_canonical_patterns':sum(r['selected_canonical_patterns'] for r in rows),'excluded_raw_patterns':sum(r['excluded_raw_patterns'] for r in rows),'negative_controls':controls,'records':rows,'seconds':time.time()-start}
Path('work/tuza_degree10_c6_density_verified.json').write_text(json.dumps(out,indent=2));print('PASS',out['selected_canonical_patterns'],out['excluded_raw_patterns'],flush=True)
