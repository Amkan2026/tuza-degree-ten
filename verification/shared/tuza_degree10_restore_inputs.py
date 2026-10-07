                                                                           
import gzip, hashlib, io, json, zipfile
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
inv = json.loads((BASE / 'work/tuza_degree10_selective_file_inventory.json').read_bytes())
extra = json.loads((BASE / 'work/tuza_degree10_extra_restore_inputs.json').read_bytes())
peer = json.loads((BASE / 'work/tuza_degree10_global_completion_peer_audit.json').read_bytes())
def save(name, body, row):
    assert hashlib.sha256(body).hexdigest() == row['sha256'], name
    assert len(body) == row['bytes'], name
    p = BASE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        assert p.read_bytes() == body, name
    else:
        p.write_bytes(body)
for name, row in {**inv['old_archive_members_required'], **extra}.items():
    with zipfile.ZipFile(BASE / row['archive']) as outer:
        if row.get('nested_member'):
            with zipfile.ZipFile(io.BytesIO(outer.read(row['nested_member']))) as inner:
                body = inner.read(row['member'])
        else:
            body = outer.read(row['member'])
    save(name, body, row)
for name, row in inv['logical_cache_members'].items():
    with zipfile.ZipFile(BASE / row['storage']) as archive:
        save(name, archive.read(row['member']), row)
for name, row in peer['source_bindings'].items():
    if 'read_from_exact_gzip' in row:
        save(name, gzip.decompress((BASE / row['read_from_exact_gzip']).read_bytes()), row)
print('PASS: required older and compressed inputs restored with their recorded byte hashes')
