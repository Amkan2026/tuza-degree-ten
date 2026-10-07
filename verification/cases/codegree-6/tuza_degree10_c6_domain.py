import ctypes, itertools, json, subprocess, sys, time, zlib
from pathlib import Path
import numpy as np

sys.path.insert(0, 'work')
from tuza_degree9_high_probe import decode, GENG

LIB = ctypes.CDLL(str(Path('work/tuza_degree10_c6_domain.dylib').resolve()))
LIB.side_patterns.argtypes = [ctypes.c_uint,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint64)]
LIB.side_patterns.restype = ctypes.c_int
PAIRS = list(itertools.combinations(range(6),2))

def permute(p, r, perm):
    ds=[(p>>(6*j))&63 for j in range(r)]
    out=sum(ds[j]<<(6*perm[j]) for j in range(r))
    for bit,(a,b) in enumerate(itertools.combinations(range(r),2)):
        if p>>(6*r+bit)&1:
            e=tuple(sorted((perm[a],perm[b])))
            k=list(itertools.combinations(range(r),2)).index(e)
            out|=1<<(6*r+k)
    return out

def basis(patterns, bits, r):
    up=np.zeros(1<<bits,dtype=bool)
    up[patterns]=True
    for b in range(bits):
        z=up.reshape(-1,2,1<<b)
        z[:,1,:]|=z[:,0,:]
    mins=[]
    for pp in patterns:
        p=int(pp)
        if not any(up[p^(1<<b)] for b in range(bits) if p>>b&1):
            mins.append(p)
    permutations=list(itertools.permutations(range(r)))
    return sorted({min(permute(p,r,q) for q in permutations) for p in mins})

if __name__=='__main__':
    started=time.time()
    rows=[]
    dest=Path('work/tuza_degree10_c6_patterns')
    dest.mkdir(exist_ok=True)
    old=Path('work/tuza_degree10_c6_domain_checkpoint.json')
    if old.exists():rows=json.loads(old.read_text())['records']
    done={r['g6'] for r in rows}
    for idx,key in enumerate(subprocess.check_output([GENG,'-q','6'],text=True).splitlines()):
        if key in done:continue
        _,HH=decode(key)
        H={tuple(e) for e in HH}
        hmask=sum(1<<i for i,e in enumerate(PAIRS) if e in H)
        sides={}
        for r in [0,1,2,3]:
            bits=6*r+r*(r-1)//2
            out=np.empty(1<<bits,dtype=np.uint32)
            stats=(ctypes.c_uint64*4)()
            count=LIB.side_patterns(hmask,r,out.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),stats)
            P=out[:count]
            mins=basis(P,bits,r)
            file=dest/f'{idx:03d}_{r}.bin.z'
            file.write_bytes(zlib.compress(P.astype('<u4').tobytes()))
            sides[str(r)]={'raw_patterns':count,'minimal_private_orbits':mins,'file':str(file),'counts':list(stats)}
        rows.append({'g6':key,'H':sorted(H),'sides':sides})
        old.write_text(json.dumps({'records':rows,'seconds':time.time()-started}))
        print(idx,key,[(r,sides[str(r)]['raw_patterns'],len(sides[str(r)]['minimal_private_orbits'])) for r in [1,2,3]],round(time.time()-started,1),flush=True)
    Path('work/tuza_degree10_c6_domain.json').write_text(json.dumps({'records':rows,'seconds':time.time()-started}))
    print('COMPLETE',len(rows),time.time()-started,flush=True)
