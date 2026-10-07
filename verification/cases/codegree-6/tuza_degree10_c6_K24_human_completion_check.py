                                                                            

                                                                         
                                                                         
   
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(name):
    data = (ROOT / name).read_bytes()
    return data, json.loads(data)


def main():
    bindings = {}
    complete_bytes, complete = read("tuza_degree10_c6_K24_complete_verified.json")
    assert complete["result"] == "PASS" and complete["complete_graph_scope"]
    assert complete["side_patterns"] == 973
    assert complete["full_cartesian_pairs"] == 946729
    assert complete["independent_residual_count"] == 193
    checkpoint_bytes, checkpoint = read("tuza_degree10_c6_packed_checkpoint.json")
    ordinary = [r for r in checkpoint["records"] if r["g6"] == "E?~o" and r["lane"] == "9/9"]
    assert len(ordinary) == complete["ordinary_certificates"] == 41
    assert sha(json.dumps(ordinary, sort_keys=True).encode()) == complete["ordinary_certificate_subset_sha256"]
    residual_bytes, residual = read("tuza_degree10_c6_K24_residual_pairs.json")
    assert sha(residual_bytes) == complete["residual_pair_sha256"]
    pairs = {tuple(p) for p in residual["residual_pairs"]}
    assert len(pairs) == 193
    density_bytes, density = read("tuza_degree10_c6_density_verified.json")
    assert density["result"] == "PASS" and density["complete_side_domains"] == 624
    assert sha(density_bytes) == complete["density_verification_sha256"]
    selected = next(r for r in density["records"] if r["g6"] == "E?~o" and r["private_size"] == 2)
    assert selected["selected_sha256"] == complete["selected_domain_sha256"]
    human_bytes, human = read("tuza_degree10_c6_K24_human_partition_verified.json")
    assert human["status"] == "PASS" and human["all_cases_have_complete_human_proofs"]
    assert human["source_residual_sha256"] == sha(residual_bytes)
    assert human["ordered_residual_pairs"] == 193
    assert {(r["p"], r["q"]) for r in human["records"]} == pairs
    assert human["human_case_counts"] == {"two_private_edges": 100, "one_private_edge": 60,
                                          "full_leaf": 9, "two_leaf": 24}
    for case, item in human["proof_binding"].items():
        proof = (ROOT / item["proof"]).read_bytes()
        checker = (ROOT / item["checker"]).read_bytes()
        report_bytes, report = read(item["verified_report"])
        assert sha(proof) == item["proof_sha256"] == report["proof_sha256"]
        assert sha(checker) == item["checker_sha256"] == report["source_sha256"]
        assert sha(report_bytes) == item["verified_report_sha256"]
        assert report["status"] == "PASS"
        bindings[case] = item
    partition_source = (ROOT / "tuza_degree10_c6_K24_human_partition_check.py").read_bytes()
    assert sha(partition_source) == human["checker_sha256"]
    root_bytes, root = read("tuza_degree10_c6_K24_root_partition_verified.json")
    assert root["result"] == "PASS" and root["input_sha256"] == sha(residual_bytes)
    assert root["ordered_pairs"] == 193
    assert root["classes"] == {"private_edges": 100, "one_private_edge": 60,
                               "full_leaf": 9, "opposite_two_leaf": 24}
    result = {"result": "PASS", "g6": "E?~o", "lane": "9/9",
              "complete_graph_scope": True, "full_cartesian_pairs": 946729,
              "ordinary_intervals": 41, "independent_residual_pairs": 193,
              "entire_residual_has_human_proofs": True,
              "ordinary_certificate_subset_sha256": complete["ordinary_certificate_subset_sha256"],
              "independent_complement_report_sha256": sha(complete_bytes),
              "residual_source_sha256": sha(residual_bytes),
              "density_verification_sha256": sha(density_bytes),
              "selected_domain_sha256": selected["selected_sha256"],
              "human_partition_sha256": sha(human_bytes),
              "root_partition_sha256": sha(root_bytes), "proof_bindings": bindings,
              "checker_sha256": sha(Path(__file__).read_bytes())}
    target = ROOT / "tuza_degree10_c6_K24_human_complete_verified.json"
    temporary = target.with_suffix(".pending")
    temporary.write_text(json.dumps(result, indent=2))
    temporary.replace(target)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
