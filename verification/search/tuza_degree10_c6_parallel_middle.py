                                                                             

                                                                          
                                                                       
   
import itertools,json,sys,time,hashlib,zipfile,zlib,errno
from pathlib import Path
import numpy as np
sys.path.insert(0,'work')
from tuza_degree10_c6_full_rectangles import patterns,autos,common_maps,cover_pair,cover_cut,exclude
from tuza_degree10_c6_solve import pair,cut
from tuza_degree10_c6_pair_wide import pair_wide

pop8=np.array([i.bit_count() for i in range(256)],dtype=np.uint8)
class PackedRectangles:
    def __init__(self,n,m):
        self.n=n;self.m=m;self.nword=(m+63)//64;self.cursor=0;self.steps=0
        self.U=np.full((n,self.nword),np.iinfo(np.uint64).max,dtype=np.uint64)
        if m%64 and n:self.U[:,-1]&=np.uint64((1<<(m%64))-1)
    def add(self,I,J):
        if not I or not J:return
        index=np.flatnonzero(np.unpackbits(np.frombuffer(I.to_bytes((self.n+7)//8,'little'),dtype=np.uint8),bitorder='little')[:self.n])
        mask=np.frombuffer(J.to_bytes(8*self.nword,'little'),dtype='<u8')
        self.U[index]&=~mask;self.steps+=1
    def first(self):
        while self.cursor<self.n:
            row=self.U[self.cursor]
            cols=np.flatnonzero(row)
            if len(cols):
                k=int(cols[0]);v=int(row[k]);return self.cursor,64*k+(v&-v).bit_length()-1
            self.cursor+=1
        return None
    def residual(self):return int(pop8[self.U.view(np.uint8)].sum(dtype=np.uint64))

if __name__=='__main__':
    start=time.time();snapshot=Path('work/tuza_degree10_c6_pre_packed_snapshot.json')
    old=json.loads(snapshot.read_text())
    records=list(old['records']);reports=[r for r in old['reports'] if r['residual']==0]
    for r in reports:r['transferred_from_full_unselected_domain']=True
    done={(r['g6'],r['lane']) for r in reports};failures=[]
    dom=[r for r in json.loads(Path('work/tuza_degree10_c6_domain.json').read_text())['records'] if r['g6'] in ['E]zo','E]zg','E]yw','E]zw']]
    core={r['g6']:r['certificates'] for r in json.loads(Path('work/tuza_degree10_c6_core_certificates.json').read_text())['records']}
    prior={}
    for r in records:prior.setdefault((r['g6'],r['lane']),[]).append(r)
    for r in json.loads(Path('work/tuza_degree10_c6_monotone_checkpoint.json').read_text())['records']:
        if r['kind']=='pair':prior.setdefault((r['g6'],r['lane']),[]).append(r)
    checkpoint=Path('work/tuza_degree10_c6_packed_checkpoint_parallel_middle.json')
    if checkpoint.exists():
        o=json.loads(checkpoint.read_text());records=o['records'];reports=o['reports'];failures=o['failures']
        done={(r['g6'],r['lane']) for r in reports if r['residual']==0}
        for r in records:prior.setdefault((r['g6'],r['lane']),[]).append(r)
                                                                           
                                                                            
    selected_rows={r['g6']:r for r in json.loads(Path('work/tuza_degree10_c6_density_domain.json').read_text())['records']}
    density_bytes=Path('work/tuza_degree10_c6_density_verified.json').read_bytes()
    density_check=json.loads(density_bytes)
    assert density_check['result']=='PASS' and density_check['complete_side_domains']==624
    selected_hashes={(r['g6'],r['private_size']):r['selected_sha256'] for r in density_check['records']}
    selected_cache=zipfile.ZipFile('work/tuza_degree10_c6_density_patterns_cache.zip')
    supplements=[]
    binding=Path('work/tuza_degree10_c6_K24_complete_verified.json')
    if binding.exists():
        binding_bytes=binding.read_bytes();bound=json.loads(binding_bytes)
        selected_records=[r for r in records if r['g6']=='E?~o' and r['lane']=='9/9']
        assert bound['result']=='PASS' and bound['complete_graph_scope']
        assert hashlib.sha256(json.dumps(selected_records,sort_keys=True).encode()).hexdigest()==bound['ordinary_certificate_subset_sha256']
        assert hashlib.sha256(density_bytes).hexdigest()==bound['density_verification_sha256']
        supplements.append({'g6':'E?~o','lane':'9/9','verification_file':str(binding),'sha256':hashlib.sha256(binding_bytes).hexdigest()})
        done.add(('E?~o','9/9'))
    def save():
        tmp=checkpoint.with_suffix('.tmp')
        while True:
            try:
                tmp.write_text(json.dumps({'records':records,'reports':reports,'failures':failures,'independently_verified_supplements':supplements,'seconds':time.time()-start}));tmp.replace(checkpoint)
                return
            except OSError as exc:
                if exc.errno!=errno.ENOSPC:raise
                if tmp.exists():tmp.unlink()
                print('STORAGE_WAIT retained all search state in memory',flush=True)
                time.sleep(15)
    for row in dom:
        if all((row['g6'],f'{7+sa}/{7+sb}') in done for sa,sb in [(0,3),(1,3),(2,3),(3,3),(2,2)]):
            continue
        H=row['H'];AU=autos(H);CM=common_maps(AU);PP={}
        for r in range(4):
            encoded=selected_cache.read(selected_rows[row['g6']]['sides'][str(r)]['file'])
            assert hashlib.sha256(encoded).hexdigest()==selected_hashes[row['g6'],r]
            PP[r]=np.frombuffer(zlib.decompress(encoded),dtype='<u4')
        for sa,sb in [(0,3),(1,3),(2,3),(3,3),(2,2)]:
            lane=f'{7+sa}/{7+sb}';key=(row['g6'],lane)
            if key in done:continue
            if row['g6'] in ['E?Bo','E?Bw']:
                reports.append({'g6':row['g6'],'lane':lane,'human_star_lemma':True,'residual':0,'proof_review_required':True});save();continue
            if core[row['g6']].get(str(sa+sb),{}).get('status')=='PASS':
                reports.append({'g6':row['g6'],'lane':lane,'core_only':True,'residual':0});save();continue
            P=PP[sa];Q=PP[sb];R=PackedRectangles(len(P),len(Q));exclude(H,P,Q,R,sa,sb)
            before=len(records)
            for rec in prior.get(key,[]):
                if rec['kind']=='pair':cover_pair(rec,AU,CM,P,Q,R,sa,sb)
                elif rec['kind']=='subset_cut':cover_cut(rec,H,AU,CM,P,Q,R,sa,sb)
            solves=0;failed=False;print('START',key,len(P),len(Q),'remaining',R.residual(),flush=True)
            while R.first() is not None:
                i,j=R.first();p=int(P[i]);q=int(Q[j]);solves+=1
                ans=pair_wide(H,sa,sb,p,q,tlim=.5,fixed=True)
                if ans['status']!='PASS':ans=pair_wide(H,sa,sb,p,q,tlim=2)
                if ans['status']!='PASS':ans=cut(H,sa,sb,p,q,tlim=5)
                if ans['status'] not in ['PASS','INFEASIBLE']:ans=pair(H,sa,sb,p,q,fixed=False,tlim=10)
                rec={'g6':row['g6'],'lane':lane,'sa':sa,'sb':sb,'p':p,'q':q,**ans}
                if ans['status']!='PASS':
                    failures.append(rec);failed=True;save();print('GAP',key,p,q,ans['status'],flush=True);break
                records.append(rec)
                if ans['kind']=='pair':cover_pair(rec,AU,CM,P,Q,R,sa,sb)
                else:cover_cut(rec,H,AU,CM,P,Q,R,sa,sb)
                save()
                if solves%10==0:print('progress',key,solves,R.residual(),round(time.time()-start,1),flush=True)
                if solves>=1000:failed=True;print('LIMIT',key,flush=True);break
            report={'g6':row['g6'],'lane':lane,'selected_density_side_counts':[len(P),len(Q)],'certificates_added':len(records)-before,'solves':solves,'residual':R.residual(),'closed_discovery':not failed and R.first() is None}
            reports=[r for r in reports if (r['g6'],r['lane'])!=key]+[report];save();print('END',report,flush=True)
    supplemented={(r['g6'],r['lane']) for r in supplements}
    out={'records':records,'reports':reports,'failures':failures,'independently_verified_supplements':supplements,'complete_discovery':all(r['residual']==0 or (r['g6'],r['lane']) in supplemented for r in reports) and len(reports)==780,'human_proof_review_required':True,'seconds':time.time()-start}
    target=Path('work/tuza_degree10_c6_packed_certificates_parallel_middle.json');tmp=target.with_suffix('.tmp')
    while True:
        try:tmp.write_text(json.dumps(out));tmp.replace(target);break
        except OSError as exc:
            if exc.errno!=errno.ENOSPC:raise
            if tmp.exists():tmp.unlink()
            print('STORAGE_WAIT final output retained in memory',flush=True);time.sleep(15)
    print('FINISHED',len(reports),len(records),out['complete_discovery'],flush=True)
