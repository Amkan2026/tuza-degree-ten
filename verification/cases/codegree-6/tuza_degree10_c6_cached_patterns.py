                                                                                
import hashlib
import json
import zipfile
from pathlib import Path

_archive = None
_manifest = None

def read_pattern_bytes(name):
    global _archive, _manifest
    if _archive is None:
        _archive = zipfile.ZipFile('work/tuza_degree10_c6_patterns_cache.zip')
        rows = json.loads(_archive.read('manifest.json'))
        assert len(rows) == 624
        _manifest = {row['path']: row for row in rows}
    data = _archive.read(str(Path(name)))
    row = _manifest[str(Path(name))]
    assert len(data) == row['bytes']
    assert hashlib.sha256(data).hexdigest() == row['sha256']
    return data
