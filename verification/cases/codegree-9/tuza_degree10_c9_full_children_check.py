                                                                      

                                                                      
                                                                               
   
from pathlib import Path
import hashlib
import json
import subprocess
import threading
import time

started = time.time()
base = Path('work')
parent_path = base/'tuza_degree10_c9_all_graph6.txt'
child_path = base/'tuza_degree10_c9_deleted_canonical_graph6.txt'
parents = subprocess.check_output(['/opt/homebrew/bin/geng', '-q', '9'])
assert parents == parent_path.read_bytes()
lines = parents.splitlines()
assert len(lines) == len(set(lines)) == 274668 and all(len(g) == 7 and g[0] == ord('H') for g in lines)
expected = child_path.read_bytes()
expected_sha = hashlib.sha256(expected).hexdigest()
assert expected.count(b'\n') == 2472012

                                                                             
                                                                             
lookups = []
for omitted in range(9):
    vertices = [v for v in range(9) if v != omitted]
    positions = []
    for j in range(1, 8):
        for i in range(j):
            a, b = vertices[i], vertices[j]
            positions.append(b*(b-1)//2 + a)
    positions += [None, None]
    pieces = []
    for offset in range(0, 30, 6):
        contributions = {}
        for local, index in enumerate(positions[offset:offset+6]):
            if index is not None:
                contributions.setdefault(index//6, []).append((5-index%6, 5-local))
        pieces.append([(source, [sum(((value >> source_bit)&1) << target_bit for source_bit,target_bit in pairs)
                                  for value in range(64)]) for source,pairs in contributions.items()])
    lookups.append(pieces)

process = subprocess.Popen(['/opt/homebrew/bin/labelg', '-q'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
digest = hashlib.sha256()
state = {'bytes': 0, 'lines': 0}


def consume():
    while True:
        block = process.stdout.read(1024*1024)
        if not block:
            return
        digest.update(block)
        state['bytes'] += len(block)
        state['lines'] += block.count(b'\n')


reader = threading.Thread(target=consume)
reader.start()
buffer = bytearray()
for position, graph in enumerate(lines):
    values = [c-63 for c in graph[1:]]
    for child in lookups:
        buffer.append(ord('G'))
        for piece in child:
            buffer.append(63 + sum(table[values[source]] for source,table in piece))
        buffer.append(10)
    if len(buffer) >= 65536:
        process.stdin.write(buffer)
        buffer.clear()
    if position and position % 50000 == 0:
        print('PARENTS', position, 'seconds', round(time.time()-started,1), flush=True)
if buffer:
    process.stdin.write(buffer)
process.stdin.close()
reader.join()
stderr = process.stderr.read()
assert process.wait() == 0, stderr.decode(errors='replace')
assert state == {'bytes': len(expected), 'lines': 2472012}, state
assert digest.hexdigest() == expected_sha
                                                                         
bad = bytearray(expected)
bad[1] ^= 1
assert hashlib.sha256(bad).hexdigest() != digest.hexdigest()
assert state['lines']-1 != 2472012
out = {
    'result': 'PASS',
    'fresh_common9_parent_types': 274668,
    'all_canonical_children': 2472012,
    'generation': 'independent Python graph6 deletion for every parent and every omitted vertex',
    'parent_sha256': hashlib.sha256(parents).hexdigest(),
    'complete_child_sha256': digest.hexdigest(),
    'complete_child_bytes': state['bytes'],
    'negative_controls': 2,
    'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'seconds': time.time()-started,
}
(base/'tuza_degree10_c9_full_children_verified.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2),flush=True)
