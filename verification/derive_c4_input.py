import hashlib
import io
import itertools
import json
import pathlib
import sys
import zipfile


def graph(key):
    core, left, right = key
    edges = {(0, 1)} | {(h, c) for h in (0, 1) for c in range(2, 6)}
    edges |= {(0, 6), (0, 7), (1, 8), (1, 9)}
    edges |= {(a + 2, b + 2) for k, (a, b) in enumerate(itertools.combinations(range(4), 2)) if core >> k & 1}
    pairs = [(a, c) for a in (4, 5) for c in range(4)] + [(4, 5)]
    for mask, mapping in [(left, {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7}), (right, {0: 2, 1: 3, 2: 4, 3: 5, 4: 8, 5: 9})]:
        edges |= {tuple(sorted((mapping[a], mapping[b]))) for k, (a, b) in enumerate(pairs) if mask >> k & 1}
    return edges


def derive(root):
    root = pathlib.Path(root)
    archive = root / 'outputs/tuza_degree9_verification.zip'
    with zipfile.ZipFile(archive) as outer:
        payload = outer.read('outputs/tuza_degree8_verification.zip')
    with zipfile.ZipFile(io.BytesIO(payload)) as inner:
        source = 'work/tuza_degree8_seven_seven_c4_shared_diagrams.json'
        raw = inner.read(source)
        assert hashlib.sha256(raw).hexdigest() == '350ba8ab4d7585a76967eb75f39663a793d6a5fff41c39e91eaec4c6afcf5b80'
        data = json.loads(raw)
        for name in ['work/degree8_mixed_c4_discovery.json', 'work/degree8_eight_eight_c4_discovery.json']:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(inner.read(name))
    rows = {}
    for template in data['templates']:
        for row in template['relabeled_coverage']:
            key = tuple(row['key'])
            mapping = row['mapping']
            packing = [sorted(mapping[v] for v in triangle) for triangle in template['packing']]
            cover = {tuple(sorted((mapping[a], mapping[b]))) for a, b in template['cover']}
            edges = graph(key)
            cover &= edges
            used = []
            for triangle in packing:
                packed = set(itertools.combinations(triangle, 2))
                assert len(set(triangle)) == 3 and packed <= edges
                assert all(e in cover for e in packed if not set(e) & {0, 1})
                used.extend(packed)
            assert len(used) == len(set(used)) and len(cover) <= 2 * len(packing)
            for triangle in itertools.combinations(range(10), 3):
                triangle_edges = set(itertools.combinations(triangle, 2))
                if set(triangle) & {0, 1} and triangle_edges <= edges:
                    assert triangle_edges & cover
            rows.setdefault(key, {'key': list(key), 'packing': packing, 'cover': sorted(cover)})
    assert len(rows) == 110
    target = root / 'work/degree8_unrestricted_codegree4_certificates.json'
    target.write_text(json.dumps({'source': source, 'source_sha256': hashlib.sha256(raw).hexdigest(), 'records': list(rows.values())}, indent=2))
    assert hashlib.sha256(target.read_bytes()).hexdigest() == 'a828fc7e90fbc3d0b86f6a0c1d1635db8ab3d536eec10715c7c9c55515ce81c3'
    return {'status': 'PASS', 'models': len(rows), 'source': source, 'source_sha256': hashlib.sha256(raw).hexdigest(), 'derived_input_sha256': hashlib.sha256(target.read_bytes()).hexdigest()}


if __name__ == '__main__':
    if sys.flags.optimize:
        raise SystemExit('Run Python without -O.')
    print(json.dumps(derive(sys.argv[1]), indent=2))
