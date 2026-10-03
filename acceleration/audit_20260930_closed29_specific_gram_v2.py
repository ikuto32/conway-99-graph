"""Independent literal integer audit of two raw induced29 Gram obstructions.

Imports no discovery, encoder, graph-validator, Gram, or screen implementation.
No census or extension-screen coverage is reviewed by this checker.
"""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "acceleration/results/20260930_closed29_extension_screen/run01/negative_candidates.json"
RAW_SHA = "6f8655fdd8770770eab6571600414ffe1dbbc8ef72e06151067d6b5d480f8d1a"
SCOPE = ROOT / "acceleration/results/20260917_partial_eight_matchings/manifest.json"
LEMMA = ROOT / "acceleration/results/20260930_independent_review/target_gram_support_lemma.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, obj):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def matrix_check(a):
    require(type(a) is list and len(a) == 29, "matrix must have29 rows")
    require(all(type(row) is list and len(row) == 29 for row in a), "matrix shape")
    require(all(type(v) is int and v in (0, 1) for row in a for v in row), "matrix nonbinary")
    require(all(a[u][u] == 0 for u in range(29)), "matrix diagonal")
    require(all(a[u][v] == a[v][u] for u, v in combinations(range(29), 2)), "matrix asymmetry")


def quadratic(a, vector):
    require(type(vector) is list and len(vector) == len(a) and all(type(x) is int for x in vector), "integer vector shape/type")
    # Independent literal full-matrix evaluation, followed by an edge-list form.
    literal = sum(vector[i] * (27 * int(i == j) - 9 * a[i][j] + 1) * vector[j]
                  for i in range(len(a)) for j in range(len(a)))
    edge_form = 27 * sum(x * x for x in vector) + sum(vector) ** 2
    edge_form -= 18 * sum(vector[u] * vector[v] for u, v in combinations(range(len(a)), 2) if a[u][v])
    require(literal == edge_form, "two exact quadratic evaluations disagree")
    return literal


def negative_check(record):
    a, vector = record["adjacency_full29"], record["integer_negative_vector"]
    matrix_check(a)
    require(record["matrix"] == "27I-9A+J", "wrong Gram matrix label")
    q = quadratic(a, vector)
    require(type(record["quadratic"]) is int and record["quadratic"] == q, "claimed quadratic differs")
    require(q < 0, "quadratic is not strictly negative")
    return q


def fixed_family(scope):
    # Independently reconstruct labels in the declared support-major convention.
    labels = []
    for low in range(7):
        for high in range(low + 1, 7):
            for first in range(2):
                for second in range(2):
                    labels.append((2 * low + first, 2 * high + second))
    fixed = {(0, v) for v in range(1, 15)}
    fixed |= {(2 * group + 1, 2 * group + 2) for group in range(7)}
    fixed |= {(symbol + 1, outer + 15) for outer, label in enumerate(labels) for symbol in label}
    require(len(fixed) == 189, "root scaffold count")
    overlap = {tuple(edge) for edge in scope["remaining_fixed_K_edges_outer"]}
    unknown = {(u + 15, v + 15) for u, v in scope["unknown_edges_outer"]}
    require(len(overlap) == 120 and len(unknown) == 2160, "scope counts")
    fixed |= {(u + 15, v + 15) for u, v in overlap}
    require(not fixed & unknown and all(0 <= u < v < 99 for u, v in fixed | unknown), "scope pairs")
    return fixed, unknown


def cap_failures(a):
    neighbors = [{v for v, value in enumerate(row) if value} for row in a]
    failed = []
    for u, v in combinations(range(len(a)), 2):
        common = sorted(neighbors[u] & neighbors[v])
        if len(common) + a[u][v] > 2:
            failed.append({"pair": [u, v], "adjacent": a[u][v], "common_neighbors": common,
                           "common_count": len(common), "cap": 2 - a[u][v]})
    return failed, [len(row) for row in neighbors]


def scope_check(record, fixed, unknown):
    a, mapping = record["adjacency_full29"], record["full99_vertex_map"]
    require(type(mapping) is list and len(mapping) == 29 and len(set(mapping)) == 29,
            "full99 map must be injective")
    require(all(type(v) is int and 0 <= v < 99 for v in mapping), "full99 map range/type")
    matrix_check(a)
    completion_edges = set(fixed)
    fixed_entries = variable_entries = 0
    for i, j in combinations(range(29), 2):
        pair = tuple(sorted((mapping[i], mapping[j])))
        if pair in unknown:
            variable_entries += 1
        else:
            fixed_entries += 1
            require(a[i][j] == int(pair in fixed), "raw matrix disagrees with fixed family entry")
        if a[i][j]:
            completion_edges.add(pair)
    partial = [[0] * 99 for _ in range(99)]
    for u, v in completion_edges:
        partial[u][v] = partial[v][u] = 1
    internal_bad, internal_degrees = cap_failures(a)
    global_bad, partial_degrees = cap_failures(partial)
    require(not internal_bad, "induced29 pair-cap violation")
    require(max(partial_degrees) <= 14, "partial full99 overdegree")
    return {"fixed_entries_checked": fixed_entries, "free_entries_checked": variable_entries,
        "induced29_pairs_checked": 406, "induced29_pair_caps_passed": True,
        "full99_partial_pairs_checked": 4851, "full99_partial_pair_caps_passed": not global_bad,
        "full99_partial_cap_failures": global_bad, "max_full99_partial_degree": max(partial_degrees),
        "family_entry_compatibility_passed": True,
        "partial99_semantics": "All family-fixed present edges plus this induced29 assignment; every remaining unknown edge temporarily absent for a necessary lower-cap test, not declared permanently absent."}


def controls(records, fixed, unknown):
    calibrated = []
    for index, record in enumerate(records):
        require(negative_check(record) == (-64940, -5868)[index], "raw positive certificate control")
        for name in ("loop", "asymmetry", "nonbinary", "wrong_vector_entry", "wrong_quadratic",
                     "zero_vector", "truncated_vector", "wrong_matrix_label", "flipped_edge"):
            bad = deepcopy(record)
            if name == "loop":
                bad["adjacency_full29"][0][0] = 1
            elif name == "asymmetry":
                bad["adjacency_full29"][0][1] ^= 1
            elif name == "nonbinary":
                bad["adjacency_full29"][0][1] = 2
            elif name == "wrong_vector_entry":
                bad["integer_negative_vector"][0] += 1
            elif name == "wrong_quadratic":
                bad["quadratic"] += 1
            elif name == "zero_vector":
                bad["integer_negative_vector"] = [0] * 29
                bad["quadratic"] = 0
            elif name == "truncated_vector":
                bad["integer_negative_vector"].pop()
            elif name == "wrong_matrix_label":
                bad["matrix"] = "27I+9A+J"
            else:
                bad["adjacency_full29"][0][1] ^= 1
                bad["adjacency_full29"][1][0] ^= 1
            try:
                negative_check(bad)
            except ValueError as error:
                calibrated.append({"record": index, "corruption": name, "rejected": True, "reason": str(error)})
            else:
                raise ValueError("corruption accepted: " + name)
        wrong_map = deepcopy(record)
        wrong_map["full99_vertex_map"][0], wrong_map["full99_vertex_map"][1] = wrong_map["full99_vertex_map"][1], wrong_map["full99_vertex_map"][0]
        try:
            scope_check(wrong_map, fixed, unknown)
        except ValueError as error:
            calibrated.append({"record": index, "corruption": "swapped_root_map", "rejected": True, "reason": str(error)})
        else:
            raise ValueError("corrupt map accepted")
    edgeless = [[0] * 29 for _ in range(29)]
    positive = {"adjacency_full29": edgeless, "integer_negative_vector": [1] + [0] * 28,
                "matrix": "27I-9A+J", "quadratic": 28}
    require(quadratic(edgeless, positive["integer_negative_vector"]) == 28, "positive quadratic calibration")
    try:
        negative_check(positive)
    except ValueError as error:
        positive_rejected = str(error)
    else:
        raise ValueError("positive direction falsely certified negative")
    return {"valid_negative_certificate_controls": 2, "corruptions_rejected": calibrated,
            "known_positive_matrix": "G=27I+J from edgeless29; e0 quadratic28",
            "positive_direction_rejected_as_obstruction": positive_rejected,
            "strict_zero_rejected": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--claim-id", default="C-CLOSED29-TWO-SPECIFIC-GRAM-OBSTRUCTIONS")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    require(digest(RAW) == RAW_SHA, "raw discovery artifact changed")
    raw, scope, lemma = [json.loads(path.read_text()) for path in (RAW, SCOPE, LEMMA)]
    require(lemma["status"] == "INDEPENDENT_TARGET_GRAM_PSD_SUPPORT_LEMMA_PASS", "support lemma gate")
    records = raw["records"]
    require(len(records) == 2, "exact two-record artifact")
    fixed, unknown = fixed_family(scope)
    results, sources = [], [RAW, SCOPE, LEMMA, Path(__file__), ROOT / "uv.lock",
        ROOT / "acceleration/results/20260930_independent_review/closed29_specific_gram/failure.json"]
    for index, record in enumerate(records):
        source_pair = ROOT / record["source_pair"]
        require(digest(source_pair) == record["source_pair_sha256"], "changed source pair")
        sources.append(source_pair)
        q = negative_check(record)
        require(q == (-64940, -5868)[index], "unexpected exact raw quadratic")
        checked_scope = scope_check(record, fixed, unknown)
        results.append({"record_index": index, "case_index": record["case_index"],
            "full99_vertex_map": record["full99_vertex_map"], "extra_vertex": record["outer_extra_vertex"],
            "exact_quadratic": q, "integer_vector": record["integer_negative_vector"],
            "matrix_sha256": sha256(json.dumps(record["adjacency_full29"], separators=(",", ":")).encode()).hexdigest(),
            "matrix_hash_serialization": "UTF-8 compact JSON integer list of rows, no trailing newline",
            "specific_induced_pattern_excluded": True, **checked_scope})
    require(results[0]["full99_partial_cap_failures"] == [{"pair": [5, 28], "adjacent": 0,
             "common_neighbors": [63, 71, 72], "common_count": 3, "cap": 2}], "first restored-cap observation differs")
    require(results[1]["full99_partial_pair_caps_passed"], "second restored-cap observation differs")
    save(args.out / "controls.json", controls(records, fixed, unknown))
    sources.append(args.out / "controls.json")
    save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "status": "INDEPENDENT_TWO_SPECIFIC_CLOSED29_GRAM_OBSTRUCTIONS_PASS",
        "claim_id": args.claim_id, "claim_revision": 1, "recommendation": "VERIFIED",
        "verifier": "/root/structural_attack independent checker of /root/eight_domain_audit discovery artifacts",
        "verification_type": "Independent raw integer matrix evaluation, exact scope reconstruction, all induced29 and restored-partial99 cap checks, positive and corrupted controls",
        "statement": "For each of the two exact raw29 adjacency matrices in the hash-bound negative_candidates.json, no symmetric binary99by99zero-diagonal target A with A^2=12I-A+2J has that matrix as the indicated induced principal submatrix.",
        "scope": "Only these two specific induced29 patterns; no entire closed28 graph, center-star domain, or eight-coordinate family is excluded.",
        "inputs_sha256": {key(p): digest(p) for p in sources}, "records": results,
        "checked_objects": {"raw_induced29_matrices": 2, "quadratic_directions": 2,
            "induced29_pair_checks": 812, "restored_partial99_pair_checks": 9702,
            "restored_partial99_cap_survivors": 1, "restored_partial99_cap_failures": 1},
        "dependencies": [{"id": "C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS", "revision": 1, "relation": "uses_result"}],
        "written_derivation": "A target's diagonal forces degree14. Hence AJ=JA=14J and J^2=99J. For G=27I-9A+J, exact expansion gives coefficients (1701,-567,63)=63(27,-9,1), so G^2=63G. Symmetry implies x^TGx=||Gx||^2/63>=0. Extend each recorded integer29vector by zero to99coordinates. Its directly checked negative quadratic contradicts this necessary PSD identity.",
        "falsification_finding": "The w71 raw29 pattern passes its406induced caps, but restoring other family-fixed edges gives nonadjacent full99 pair(5,28) three known common neighbors63,71,72. It is already excluded by that cheaper cap. The w81 pattern passes all4851restored partial caps and has exact negative Gram quadratic-5868.",
        "prior_checker_failure": "Version1 independently computed the cap failure but stopped because its handwritten expected witness list was wrong. The retained failure record and unchanged v1 source document the error; v2 corrects only that expectation and written list.",
        "producer_imported": False, "shared_components": ["Python standard-library integer arithmetic", "previous independently reviewed universal Gram lemma"],
        "limitations": ["No screen population or completeness count was independently reproduced; historical surviving-assignment counts are not approved.",
            "No claim that both patterns survive restored full99 caps; exactly one does.",
            "No assumption of automorphisms, universal rook containment, or unrestricted family coverage."],
        "external_review": False, "target_resolution": False, "artifact_availability": "LOCAL_ONLY"})
    print(json.dumps({"status": "INDEPENDENT_TWO_SPECIFIC_CLOSED29_GRAM_OBSTRUCTIONS_PASS",
        "quadratics": [r["exact_quadratic"] for r in results], "full99_cap_survivors": 1,
        "summary_sha256": digest(args.out / "summary.json")}))


if __name__ == "__main__":
    main()
