                                                                                 
import gzip
import hashlib
import itertools
import json
import subprocess
import time
from pathlib import Path

from tuza_book3_condensed_root_check import graph, literal, color_to_witness, named

ROOT = Path(__file__).resolve().parent


def edge(a, b):
    return min(a, b), max(a, b)


def check_pair():
    rim = [('c0','a4'),('c0','a5'),('c1','a2'),('c1','a3'),('c2','a0'),('c2','a1'),
           ('a0','a3'),('a0','a5'),('a1','a2'),('a1','a4'),('a2','a5'),('a3','a4')]
    swap = {'c0':'c0','c1':'c2','c2':'c1', **{f'a{i}':f'b{i}' for i in range(6)}}
    E = {edge(*e) for e in rim} | {edge(swap[a],swap[b]) for a,b in rim}
    E |= {edge('u','v')} | {edge(h,f'c{i}') for h in ['u','v'] for i in range(3)}
    E |= {edge('u',f'a{i}') for i in range(6)} | {edge('v',f'b{i}') for i in range(6)}
    U = {'u','v'}
    S = [('u','c0','v'),('v','c1','b1'),('u','c2','a1'),('u','a2','a5'),
         ('u','a3','a4'),('v','b2','b5'),('v','b3','b4')]
    X = {edge(*e) for e in [('u','c0'),('v','c0'),('u','c1'),('c1','b1'),('v','c2'),('c2','a1'),
                           ('u','a0'),('u','a1'),('v','b0'),('v','b1'),
                           ('a2','a5'),('a3','a4'),('b2','b5'),('b3','b4')]}
    assert len(S) == 7 and len(X) == 14 and X <= E
    packed = []
    for t in S:
        assert len(set(t)) == 3
        edges = {edge(*e) for e in itertools.combinations(t,2)}
        assert edges <= E and {e for e in edges if not set(e)&U} <= X
        packed += list(edges)
    assert len(packed) == len(set(packed)) == 21
    upper = E | {edge(f'a{i}',f'b{j}') for i in range(6) for j in range(6)}
    for h in U:
        N = {b if a == h else a for a,b in upper if h in (a,b)}
        assert len(N) == 10
        for a,b in itertools.combinations(N,2):
            if edge(a,b) in upper:
                assert {edge(h,a),edge(h,b),edge(a,b)} & X
                                                                          
    assignment = {'v':{0,1},'c0':{2,3},'c1':{2,4},'c2':{3,4},
                  'a0':{0,2},'a1':{1,2},'a2':{0,3},'a3':{1,3},'a4':{0,4},'a5':{1,4}}
    for h,f in [('u',assignment), ('v',{'u':assignment['v'], **{swap[k]:v for k,v in assignment.items() if k!='v'}})]:
        assert len(f) == 10 and len({tuple(sorted(v)) for v in f.values()}) == 10
        for a,b in itertools.combinations(f,2):
            assert (edge(a,b) in E) == (not f[a]&f[b])
                                                                           
    common = [{2,3},{2,4},{3,4}]; images = set()
    for p in itertools.permutations([2,3,4]):
        f = {0:0,1:1,**dict(zip([2,3,4],p))}
        images.add(tuple(common.index({f[a] for a in c}) for c in common))
    assert images == set(itertools.permutations(range(3)))
    return {'packing': S, 'cover': sorted(X), 'common_identifications': len(images),
            'arbitrary_exclusive_cross_edges': True}


def main():
    started = time.time()
    helper = ROOT/'tuza_book3_condensed_root_check.py'
    assert hashlib.sha256(helper.read_bytes()).hexdigest() == '69d34a99fd41535d62b9bb8f8b212c191bca33e991bfaaffb29524ba69046102'
    full = json.loads(gzip.decompress((ROOT/'tuza_subcubic_condensed_basis.json.gz').read_bytes()))
    keys = ['positive_edge_colorings','positive_matching_cover_records','remaining']
    data = {'scope':'Connected subcubic graphs of minimum degree at least two, orders five through ten'}
    for k in keys:
        data[k] = [r for r in full[k] if ord(r['g6'][0])-63 <= 10]
    raw = json.dumps(data,sort_keys=True,separators=(',',':')).encode()
    source = ROOT/'tuza_degree10_subcubic_link_basis.json.gz'
    encoded = gzip.compress(raw,mtime=0); source.write_bytes(encoded)
    C,W,R = (data[k] for k in keys)
    assert (len(C),len(W),len(R)) == (660,40,2)
    for row in C:
        color_to_witness(row)
    for row in W:
        n,E = graph(row['g6']); literal(n,E,row['matching'],row['cover'])
    assert {r['name'] for r in R} == {'P','R'}
    for row in R:
        n,E = graph(row['g6']); m,F = named(row['name']); f = {int(a):b for a,b in row['bijection'].items()}
        assert n == m == 10 and set(f) == set(f.values()) == set(range(n))
        assert {edge(f[a],f[b]) for a,b in E} == F
        assert all(sum(v in e for e in E) == 3 for v in range(n))
    actual = [r['g6'] for r in C+W+R]; expected=set(); whole=set(); counts={}
    for n in range(5,11):
        F = set(subprocess.check_output(['/opt/homebrew/bin/geng','-q','-c','-D3',str(n)]).decode().splitlines())
        M = set(subprocess.check_output(['/opt/homebrew/bin/geng','-q','-c','-d2','-D3',str(n)]).decode().splitlines())
        assert M <= F
        for key in F-M:
            order,E = graph(key)
            assert order == n and min(sum(v in e for e in E) for v in range(n)) == 1
        counts[n] = {'whole':len(F),'min2':len(M),'leaf':len(F-M)}
        expected |= M; whole |= F
    assert len(actual) == len(set(actual)) == len(expected) == 702 and set(actual) == expected
    assert len(whole) == 2561
    pair = check_pair()
    proof = (ROOT/'tuza_degree10_subcubic_branch_proof.txt').read_bytes()
    report = {'result':'PASS','complete_min2_domain_types':702,'whole_connected_types':2561,
              'proper_colorings_converted_to_literal_WKE':660,'direct_WKE_witnesses':40,
              'only_remaining_types':['P','R'],'human_leaf_induction_required':True,
              'human_diamond_tip_argument_required':True,'Petersen_pair':pair,
              'payload_sha256':hashlib.sha256(encoded).hexdigest(),'raw_payload_sha256':hashlib.sha256(raw).hexdigest(),
              'proof_sha256':hashlib.sha256(proof).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'helper_source_sha256':hashlib.sha256(helper.read_bytes()).hexdigest(),'seconds':time.time()-started}
    target=ROOT/'tuza_degree10_subcubic_link_basis_verified.json'
    temporary=target.with_suffix('.pending');temporary.write_text(json.dumps(report,indent=2));temporary.replace(target)
    print(json.dumps(report),flush=True)


if __name__ == '__main__':
    main()
