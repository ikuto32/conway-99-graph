"""Produce, but do not approve, a full99 necessary Gram box clause from w81."""
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, product
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "acceleration/results/20260930_closed29_extension_screen/run01/negative_candidates.json"
RAW_SHA = "6f8655fdd8770770eab6571600414ffe1dbbc8ef72e06151067d6b5d480f8d1a"
MODEL = ROOT / "acceleration/results/20260930_eight_full99_cnf/model.json"
MODEL_SHA = "f2b7a649e74aa476380e14066239a188a2d2122d2ba1cc6e330e9a094d2cc0ee"
CNF = ROOT / "acceleration/results/20260930_eight_full99_cnf/instance.cnf"
CNF_SHA = "f247be8432d69f4feec037833a6923ef623e20c0aa0dbdea77fd13ec218d095b"
PRIOR = ROOT / "acceleration/results/20260930_independent_review/closed29_specific_gram_v2/summary.json"
PRIOR_SHA = "a4481e0969c17a302ae5d8812c98dd42608178a8daaa5f5a92b12b14a63bf879"
LEMMA = ROOT / "acceleration/results/20260930_independent_review/target_gram_support_lemma.json"


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, obj):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def maximize(constant, terms, fixed):
    return constant + sum(coefficient * fixed[index] if index in fixed else max(0, coefficient)
                          for index, coefficient in enumerate(terms))


def drop_literals(constant, terms, assignment):
    value = constant + sum(coefficient * bit for coefficient, bit in zip(terms, assignment))
    assert value < 0
    fixed = {i: bit for i, (coefficient, bit) in enumerate(zip(terms, assignment)) if coefficient}
    gains = sorted((max(0, terms[i] * (1 - 2 * bit)), i) for i, bit in fixed.items())
    for gain, index in gains:
        if value + gain < 0:
            value += gain
            del fixed[index]
    assert maximize(constant, terms, fixed) == value < 0
    return fixed, value


def controls():
    cases = 0
    for terms in product(range(-3, 4), repeat=3):
        for assignment in product((0, 1), repeat=3):
            constant = -1 - sum(c * a for c, a in zip(terms, assignment))
            fixed, bound = drop_literals(constant, terms, assignment)
            corners = [constant + sum(c * bit for c, bit in zip(terms, values))
                       for values in product((0, 1), repeat=3)
                       if all(values[index] == bit for index, bit in fixed.items())]
            assert max(corners) == bound < 0
            cases += 1
    rejected = []
    for label, constant in (("zero", 0), ("positive", 1)):
        try:
            drop_literals(constant, [0], [0])
        except AssertionError:
            rejected.append(label)
        else:
            raise AssertionError("nonnegative direction accepted")
    return {"status": "PRODUCER_BOX_CONTROLS_PASS", "exhaustive_three_bit_cases": cases,
            "nonnegative_controls_rejected": rejected, "independent_verification": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    assert digest(RAW) == RAW_SHA and digest(MODEL) == MODEL_SHA and digest(CNF) == CNF_SHA and digest(PRIOR) == PRIOR_SHA
    inputs = [Path(__file__), Path(__file__).with_name("theory_20260930_eight_raw29_gram_cut_spec.md"),
              RAW, MODEL, CNF, PRIOR, LEMMA, ROOT / "uv.lock"]
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "input_hashes": {key(path): digest(path) for path in inputs},
        "scope": "One w81 direction in the frozen120fixedK/2160free-edge full99 family; no automorphism or coverage assumption.",
        "question": "How many literals can be removed while the exact Boolean-box maximum remains strictly negative?",
        "selection": "Raw negative_candidates record1, extra full99vertex81, q=-5868; deterministic gain-then-ID ordering.",
        "limits": {"wall_seconds": 120, "selected_vectors": 1, "solver_calls": 0},
        "status": "CANDIDATE_PRODUCER", "independent_review_pending": True})
    save(args.out / "controls.json", controls())
    raw = json.loads(RAW.read_text())["records"][1]
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "INDEPENDENT_TWO_SPECIFIC_CLOSED29_GRAM_OBSTRUCTIONS_PASS"
    assert prior["records"][1]["extra_vertex"] == raw["outer_extra_vertex"] == 81
    assert prior["records"][1]["full99_partial_pair_caps_passed"]
    model = json.loads(MODEL.read_text())
    assert model["schema"] == "EIGHT_FULL99_EXACT_PREFIX_CNF_V1"
    mapping, small_a = raw["full99_vertex_map"], raw["adjacency_full29"]
    reverse = {vertex: i for i, vertex in enumerate(mapping)}
    vector = [0] * 99
    for vertex, value in zip(mapping, raw["integer_negative_vector"]):
        vector[vertex] = value
    known = model["known_adjacency_full99"]
    constant = 27 * sum(x * x for x in vector) + sum(vector) ** 2
    constant -= 18 * sum(vector[u] * vector[v] for u, v in combinations(range(99), 2) if known[u][v] == 1)
    terms, assignment, rows = [], [], []
    for entry in model["edge_variables"]:
        variable, u, v = entry["id"], entry["u"], entry["v"]
        assert variable == len(terms) + 1 and known[u][v] == known[v][u] == -1
        coefficient = -18 * vector[u] * vector[v]
        bit = small_a[reverse[u]][reverse[v]] if u in reverse and v in reverse else 0
        assert coefficient == 0 or (u in reverse and v in reverse)
        terms.append(coefficient)
        assignment.append(bit)
        rows.append({"variable": variable, "edge_full99": [u, v], "coefficient": coefficient,
            "raw_pattern_value": bit if u in reverse and v in reverse else None,
            "raw_pattern_value_null_reason": "At least one endpoint is outside the raw29 pattern; coefficient is zero." if u not in reverse or v not in reverse else None})
    assert len(terms) == 2160
    initial_q = constant + sum(c * a for c, a in zip(terms, assignment))
    assert initial_q == raw["quadratic"] == -5868
    support_clause = [-(i + 1) if assignment[i] else i + 1 for i, c in enumerate(terms) if c]
    fixed, upper = drop_literals(constant, terms, assignment)
    final_clause = [-(i + 1) if fixed[i] else i + 1 for i in sorted(fixed)]
    corner = [fixed[i] if i in fixed else int(c > 0) for i, c in enumerate(terms)]
    matrix = [[max(0, value) for value in row] for row in known]
    for row, bit in zip(model["edge_variables"], corner):
        u, v = row["u"], row["v"]
        matrix[u][v] = matrix[v][u] = bit
    literal_corner_q = sum(vector[u] * (27 * int(u == v) - 9 * matrix[u][v] + 1) * vector[v]
                           for u in range(99) for v in range(99))
    assert literal_corner_q == upper < 0
    for i, row in enumerate(rows):
        row.update(free=i not in fixed, fixed_value=fixed.get(i),
            fixed_value_null_reason="Variable was freed or has zero coefficient." if i not in fixed else None,
            maximizing_corner_value=corner[i], maximum_gain_if_freed=max(0, terms[i] * (1 - 2 * assignment[i])))
    corner_path = args.out / "maximizing_corner.json"
    save(corner_path, {"adjacency_full99": matrix, "all2160edge_values": corner,
        "integer_vector_full99": vector, "exact_quadratic": literal_corner_q,
        "satisfies_full_SRG_or_family_degrees": None,
        "satisfies_full_SRG_or_family_degrees_null_reason": "Not required: corner maximizes over all independent Boolean edge choices with the retained fixed literals; graph constraints are intentionally not assumed for this upper bound."})
    certificate_path = args.out / "certificate.json"
    save(certificate_path, {"schema": "FULL99_TARGET_GRAM_BOOLEAN_BOX_NOGOOD_V1", "status": "CANDIDATE",
        "raw_artifact": key(RAW), "raw_artifact_sha256": RAW_SHA, "raw_record_index": 1,
        "prior_specific_graph_audit": key(PRIOR), "prior_specific_graph_audit_sha256": PRIOR_SHA,
        "encoding_model": key(MODEL), "encoding_model_sha256": MODEL_SHA,
        "base_cnf": key(CNF), "base_cnf_sha256": CNF_SHA,
        "matrix": "27I-9A+J", "integer_vector_full99": vector,
        "raw29_vertex_map": mapping, "affine_constant": constant, "all2160variable_coefficients": rows,
        "raw_pattern_quadratic": initial_q, "support_nogood_clause": support_clause,
        "nogood_clause": final_clause, "global_boolean_box_upper_bound": upper,
        "maximizing_corner_path": key(corner_path), "maximizing_corner_sha256": digest(corner_path),
        "selection_rule": "Free increasing nonnegative maximum gain, ties by variable ID, only under strict negative cumulative upper bound.",
        "scope": "Necessary for any target extension retaining the exact model's fixed entries; not implied merely by the weaker CNF or by discovery-agent approval.",
        "independent_review_pending": True})
    with (args.out / "nogood.clause").open("x", encoding="ascii", newline="\n") as stream:
        stream.write(" ".join(map(str, final_clause)) + " 0\n")
    assert time.monotonic() - started < 120
    save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CANDIDATE_EXACT_FULL99_GRAM_CUT_PENDING_INDEPENDENT_CHECK",
        "scope": "One w81 integer direction and one candidate edge clause, exact fixed120K full99 family.",
        "support_literals": len(support_clause), "box_literals": len(final_clause),
        "nonzero_vector_coordinates": sum(x != 0 for x in vector),
        "nonzero_edge_coefficients": sum(c != 0 for c in terms), "raw_quadratic": initial_q,
        "exact_box_upper_bound": upper, "certificate_sha256": digest(certificate_path),
        "corner_sha256": digest(corner_path), "clause_sha256": digest(args.out / "nogood.clause"),
        "elapsed_seconds": time.monotonic() - started, "solver_calls": 0, "cnf_modified": False,
        "target_resolution": False, "clause_minimality_claimed": False})
    print(json.dumps({"status": "CANDIDATE", "support_literals": len(support_clause), "box_literals": len(final_clause),
                      "box_upper_bound": upper, "certificate_sha256": digest(certificate_path)}))


if __name__ == "__main__":
    main()
