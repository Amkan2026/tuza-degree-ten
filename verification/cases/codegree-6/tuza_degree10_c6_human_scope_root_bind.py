                                                                          

                                                                          
                                                                    
   
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    'tuza_degree10_c6_four_private_human_proof.txt': '885ecfe156937ae6396523aff7de5d0f34d92e3fc75b3692f68de1dce9432e3e',
    'tuza_degree10_c6_four_private_human_check.c': '4dce580376ebaa4a04f2f85c8bd0ae0efa72b2d499cd811f47b87798c241b14f',
    'tuza_degree10_c6_four_private_human_verified.json': '272b7c2e3b51973036cecd4c49174f8ff0f07f181c7e03d1886d4a940890adca',
    'tuza_degree10_c6_four_private_glue_check.py': '2cbfb849439ef9fd78dfb16bc457198f18212c72a724ac57fe53d5be5074ac4a',
    'tuza_degree10_c6_four_private_glue_verified.json': '17121d7664820bf6d5b439a199bcc7a232078acd50712b0097a3122432d8e1cf',
    'tuza_degree10_c6_empty_core_human_proof.txt': 'a8d98c54cd51e80880cc6f2d6add9d480dd226287f94a409fa52208ff54530ed',
    'tuza_degree10_c6_double_hub_human_proof.txt': '3084e8de92cb7054ac4094b4736003b0e7bec447d5b6c02606721db02d33c36a',
    'tuza_degree10_c6_three_hub_human_proof.txt': '6d9e0f4d035ae28b490d53d1358a6dcfa2263b42d1d3c4d393f37bd75eca7765',
    'tuza_degree10_c6_three_hub_human_check.py': '6a0eaf4c1ba34b187b1cd5f72e2d2e8a45c84626ac985c4b9499706a036457b7',
    'tuza_degree10_c6_three_hub_human_verified.json': 'c0ac82e6f6c8c867ecb24a32a05e8a55edb7285e40c5c0a00fdc12072ccbe402',
}


def main():
    bindings = {}
    for name, expected in EXPECTED.items():
        body = (ROOT / name).read_bytes()
        value = hashlib.sha256(body).hexdigest()
        assert value == expected, (name, value)
        bindings[name] = {'sha256': value, 'bytes': len(body)}
        if name.endswith('_verified.json'):
            report = json.loads(body)
            assert report.get('result', report.get('status')) == 'PASS'
    private = json.loads((ROOT / 'tuza_degree10_c6_four_private_human_verified.json').read_bytes())
    assert private['source_sha256'] == EXPECTED['tuza_degree10_c6_four_private_human_check.c']
    result = {
        'result': 'PASS',
        'scope': 'Human star arguments for E?Bo and E?Bw in the maximum-degree-ten common-six partition',
        'human_argument_required': True,
        'reviews': {
            'E?Bo': 'The private graph on at most four vertices admits the stated matching and cover cases. The two private matchings use at most two contacts each. The three core triangles use distinct leaves under the displayed availability bounds. All packed outer rims belong to X. Saturation at maximum common-neighbor count six excludes center-private edges. Arbitrary private cross edges remain covered.',
            'E?Bw': 'The independent-five one-hub analysis handles matchings of private size one, two and three. Its only retained private P3 or triangle contacts use the same two leaves. The double-hub construction covers deletion and the missing-leaf case. The three-hub construction combines six private triangles and three hub-pair triangles with distinct leaves, giving nine packed triangles and eighteen covering edges. Every packed outer rim belongs to X.',
        },
        'bindings': bindings,
        'binding_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'external_peer_review': False,
        'full_780_lane_coverage_claimed': False,
    }
    target = ROOT / 'tuza_degree10_c6_human_scope_root_verified.json'
    temporary = target.with_suffix('.pending')
    temporary.write_text(json.dumps(result, indent=2))
    temporary.replace(target)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
