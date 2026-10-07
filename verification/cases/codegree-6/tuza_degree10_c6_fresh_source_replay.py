                                                                               

                                                                      
                                                                        
                                                                           
   
import array,concurrent.futures,ctypes,hashlib,itertools,json,os,subprocess,sys,time,zlib,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SNAP=ROOT/'tuza_degree10_c6_fresh_source_snapshot'
SOURCE_NAMES=['tuza_degree10_c6_domain_independent.c','tuza_degree10_c6_domain_independent.py',
              'tuza_degree10_c6_density_check.c','tuza_degree10_c6_density_check.py',
              'tuza_degree10_c6_density.py','tuza_degree10_c6_cached_patterns.py',
              'tuza_degree10_c6_full_rectangles.py','tuza_degree10_c6_domain.c',
              'tuza_degree10_c6_domain.py']
INPUT_NAMES=['tuza_degree10_c6_domain.json','tuza_degree10_c6_density_domain.json',
             'tuza_degree10_c6_domain_independent_verified.json','tuza_degree10_c6_density_verified.json']
RAWZIP=ROOT/'tuza_degree10_c6_patterns_cache.zip'
SELZIP=ROOT/'tuza_degree10_c6_density_patterns_cache.zip'
EXPECTED={'tuza_degree10_c6_domain_independent_verified.json':'48434eb29de94cbae37bedd43307e4de5fa5a1e02c3b9ce42bb370561d577793',
          'tuza_degree10_c6_density_verified.json':'ba027ada6dad2fc106595d5c59cc4cb2a1aab9fcdaf01726ef156fb2df2aa5c3',
          'tuza_degree10_c6_density_domain.json':'803fc4e48fb519d082ec5bab6a39f9159e83e18696b6f873c4c83aaeeed9accc'}

def digest(raw):return hashlib.sha256(raw).hexdigest()

def atomic(path,data):
    tmp=path.with_suffix(path.suffix+'.pending');tmp.write_bytes(data);tmp.replace(path)

def initializer():
    global V,D,RZ,SZ
    V=ctypes.CDLL(str(SNAP/'raw_review.dylib'));D=ctypes.CDLL(str(SNAP/'density_review.dylib'))
    U32=ctypes.POINTER(ctypes.c_uint32);U64=ctypes.POINTER(ctypes.c_uint64)
    V.verify_domain.argtypes=[ctypes.c_uint,ctypes.c_int,U32,ctypes.c_int,ctypes.c_char_p,U64]
    V.verify_domain.restype=ctypes.c_int
    D.check_density.argtypes=[ctypes.c_uint,ctypes.c_int,U32,ctypes.c_int,U32,ctypes.c_int,U64]
    D.check_density.restype=ctypes.c_int
    RZ=zipfile.ZipFile(RAWZIP);SZ=zipfile.ZipFile(SELZIP)

def u32(raw):
    unpacked=zlib.decompress(raw);assert len(unpacked)%4==0
    values=array.array('I');values.frombytes(unpacked)
    assert values.itemsize==4
    if sys.byteorder!='little':values.byteswap()
    return values,(ctypes.c_uint32*len(values)).from_buffer(values)

def replay(task):
    idx,r,H,record,selected,ds=task
    begun=time.time();rb=RZ.read(record['patterns_file']);sb=SZ.read(selected['file'])
    assert digest(rb)==record['patterns_sha256']==ds['raw_sha256']
    assert digest(sb)==ds['selected_sha256']
    P,pp=u32(rb);Q,qq=u32(sb)
    assert len(P)==record['retained_candidate_patterns']==ds['raw_retained_patterns']
    assert len(Q)==ds['selected_canonical_patterns']==selected['selected_density_candidates']
    hm=sum(1<<i for i,e in enumerate(itertools.combinations(range(6),2))if list(e)in H)
    den=(ctypes.c_uint64*3)()
    status=D.check_density(hm,r,pp,len(P),qq,len(Q),den)
    assert status==1,('density',idx,r,status)
    assert list(den)==[len(P),ds['selected_raw_patterns'],ds['excluded_raw_patterns']]
    output=SNAP/'intervals'/f'{idx:03d}_{r}.txt';stats=(ctypes.c_uint64*6)()
    status=V.verify_domain(hm,r,pp,len(P),str(output).encode(),stats)
    assert status==1,('raw',idx,r,status)
    expected=[record[k]for k in ['all_boolean_patterns','legal_connected_patterns',
                                'retained_candidate_patterns','excluded_positive_WKE_patterns','literal_WKE_intervals']]
    assert list(stats)[:5]==expected
    literal=output.read_bytes();assert digest(literal)==record['WKE_sha256']
    assert len(literal.splitlines())==record['literal_WKE_intervals']
    return {'g6':record['g6'],'private_size':r,'result':'PASS_FRESH_RAW_AND_DENSITY',
            'all_boolean_patterns':stats[0],'legal_connected_patterns':stats[1],
            'retained_candidate_patterns':stats[2],'excluded_positive_WKE_patterns':stats[3],
            'literal_WKE_intervals':stats[4],'selected_canonical_patterns':len(Q),
            'excluded_by_density':ds['excluded_raw_patterns'],
            'raw_patterns_sha256':digest(rb),'selected_patterns_sha256':digest(sb),
            'fresh_literal_intervals_sha256':digest(literal),'seconds':time.time()-begun}

def main():
    started=time.time();SNAP.mkdir(exist_ok=True);(SNAP/'intervals').mkdir(exist_ok=True)
    bindings={}
    for name in SOURCE_NAMES+INPUT_NAMES:
        raw=(ROOT/name).read_bytes()
        if name in EXPECTED:assert digest(raw)==EXPECTED[name]
        atomic(SNAP/name,raw);bindings[name]={'bytes':len(raw),'sha256':digest(raw)}
    for path in (RAWZIP,SELZIP):
        raw=path.read_bytes();bindings[path.name]={'bytes':len(raw),'sha256':digest(raw)}
    rawdomain=json.loads((SNAP/'tuza_degree10_c6_domain.json').read_bytes())['records']
    selected=json.loads((SNAP/'tuza_degree10_c6_density_domain.json').read_bytes())['records']
    oldraw=json.loads((SNAP/'tuza_degree10_c6_domain_independent_verified.json').read_bytes())
    olddensity=json.loads((SNAP/'tuza_degree10_c6_density_verified.json').read_bytes())
    domain=subprocess.check_output(['/opt/homebrew/bin/geng','-q','6']).decode().splitlines()
    assert len(domain)==len(set(domain))==len(rawdomain)==len(selected)==156
    assert set(domain)=={r['g6']for r in rawdomain}=={r['g6']for r in selected}
    records={(r['g6'],r['private_size']):r for r in oldraw['records']}
    density={(r['g6'],r['private_size']):r for r in olddensity['records']}
    assert len(records)==len(density)==624
    assert sum(r['literal_WKE_intervals']for r in records.values())==175058
    tasks=[]
    for idx,(a,b)in enumerate(zip(rawdomain,selected)):
        assert a['g6']==b['g6']and a['H']==b['H']
        key=a['g6']
        for r in range(4):
            record=records[key,r];ds=density[key,r]
            assert record['patterns_file']==a['sides'][str(r)]['file']
            assert a['sides'][str(r)]['raw_patterns']==record['retained_candidate_patterns']
            tasks.append((idx,r,a['H'],record,b['sides'][str(r)],ds))
    for c,out in [('tuza_degree10_c6_domain_independent.c','raw_review.dylib'),
                  ('tuza_degree10_c6_density_check.c','density_review.dylib')]:
        subprocess.run(['/usr/bin/clang','-O3','-dynamiclib',str(SNAP/c),'-o',str(SNAP/out)],check=True)
        bindings[out]={'bytes':(SNAP/out).stat().st_size,'sha256':digest((SNAP/out).read_bytes())}
    bindings['fresh_replay_source']={'sha256':digest(Path(__file__).read_bytes())}
    atomic(SNAP/'bindings.json',json.dumps(bindings,indent=2).encode())
    print(json.dumps({'phase':'BOUND_AND_SOURCE_COMPILED','domains':624,'old_literal_intervals':175058,
                      'snapshot':str(SNAP),'bindings':bindings}),flush=True)
    checkpoint=ROOT/'tuza_degree10_c6_fresh_source_checkpoint.json'
    rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=3,initializer=initializer)as pool:
        pending={pool.submit(replay,task):task for task in tasks}
        for future in concurrent.futures.as_completed(pending):
            row=future.result();rows.append(row)
            rows.sort(key=lambda x:(x['g6'],x['private_size']))
            atomic(checkpoint,json.dumps({'result':'RUNNING','records':rows,'seconds':time.time()-started},indent=2).encode())
            if len(rows)%12==0 or row['private_size']==3:
                print(json.dumps({'phase':'FRESH_REPLAY','completed':len(rows),'last_g6':row['g6'],
                                  'private_size':row['private_size'],'last_seconds':row['seconds'],
                                  'seconds':time.time()-started}),flush=True)
    assert len(rows)==624
    assert sum(r['literal_WKE_intervals']for r in rows)==175058
    assert sum(r['selected_canonical_patterns']for r in rows)==1803814
    assert sum(r['excluded_by_density']for r in rows)==10284150
                                                                               
    for name in SOURCE_NAMES+INPUT_NAMES:
        assert digest((ROOT/name).read_bytes())==bindings[name]['sha256']
    for path in (RAWZIP,SELZIP):assert digest(path.read_bytes())==bindings[path.name]['sha256']
    report={'result':'PASS_FRESH_COMPLETE_RAW_AND_DENSITY_REPLAY',
            'complete_side_domains':624,'common_graph_types':156,
            'all_boolean_patterns':sum(r['all_boolean_patterns']for r in rows),
            'legal_connected_patterns':sum(r['legal_connected_patterns']for r in rows),
            'retained_candidate_patterns':sum(r['retained_candidate_patterns']for r in rows),
            'excluded_positive_WKE_patterns':sum(r['excluded_positive_WKE_patterns']for r in rows),
            'fresh_literal_WKE_intervals':175058,'all_literal_interval_digests_reproduced':True,
            'selected_canonical_patterns':1803814,'excluded_raw_by_density':10284150,
            'source_compiled_in_isolated_snapshot':True,'bindings':bindings,
            'records':rows,'seconds':time.time()-started}
    final=ROOT/'tuza_degree10_c6_fresh_source_verified.json'
    atomic(final,json.dumps(report,indent=2).encode())
    print(json.dumps({k:v for k,v in report.items()if k not in('bindings','records')}),flush=True)

if __name__=='__main__':main()
