"""Corruption controls for the independently rebuilt whole-matching proof.

All mutations are in memory. Matrix hashes are rebound before semantic controls,
so these checks do not merely exercise a checksum. No producer is imported.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import time

from audit_certificate import full_graph, require
from audit_matching_farkas import audit


AUDITOR_SHA = "3bf8d8fee271594cfbc3fba8855897cd84eb2cbd889d8857183e3be42120f2e5"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


class MemoryPath:
    def __init__(self, path, value):
        self.path = path
        self.data = (json.dumps(value, separators=(",", ":")) + "\n").encode()

    def read_bytes(self):
        return self.data

    def __str__(self):
        return str(self.path)


def recalculate(matrix, certificate):
    """Retain internally consistent integer arithmetic after a matrix edit."""
    boxed = certificate["projected_box_columns"]
    coefficients, rhs = [0] * boxed, 0
    for row, multiplier in certificate["weighted_rows"]:
        bound = matrix["row_lower" if multiplier > 0 else "row_upper"][row]
        require(bound is not None, "Control requested an infinite selected bound")
        rhs += multiplier * bound
        for k in range(matrix["csr_start"][row], matrix["csr_start"][row + 1]):
            column = matrix["csr_index"][k]
            if column < boxed:
                coefficients[column] += multiplier * matrix["csr_value"][k]
    certificate["combined_coefficients"] = coefficients
    certificate["combined_lower_rhs"] = rhs
    certificate["box_upper_bound"] = sum(max(0, c) for c in coefficients)
    certificate["contradiction_margin"] = rhs - certificate["box_upper_bound"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--wrong-base", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve prior control report")
    started = time.perf_counter()
    auditor = Path(__file__).with_name("audit_matching_farkas.py")
    require(digest(auditor) == AUDITOR_SHA, "Auditor is not the reviewed frozen version")
    source_hash = digest(Path(__file__))
    matrix = json.loads(args.matrix.read_bytes())
    certificate = json.loads(args.certificate.read_bytes())
    original_graph, _ = full_graph(json.loads(args.candidate.read_bytes()))
    wrong_graph, _ = full_graph(json.loads(args.wrong_base.read_bytes()))
    allowed = {tuple(edge) for edge in matrix["matching_variables"]}
    old_edges = {(u, v) for u in range(84) for v in range(u+1, 84) if v+15 in original_graph[u+15]}
    wrong_edges = {(u, v) for u in range(84) for v in range(u+1, 84) if v+15 in wrong_graph[u+15]}
    require(bool((old_edges ^ wrong_edges) - allowed), "Wrong base must change a fixed matching coordinate")
    baseline = audit(args.candidate, args.matrix, args.certificate)
    require(baseline["status"] == "INDEPENDENT_WHOLE_MATCHING_MATRIX_AND_INTEGER_FARKAS_AUDIT_PASS", "Baseline failed")
    records = []

    def trial(name, mutation, expected_reason, candidate_path=None, expected_pass=False):
        changed_matrix, changed_certificate = deepcopy(matrix), deepcopy(certificate)
        mutation(changed_matrix, changed_certificate)
        matrix_path = MemoryPath(args.matrix, changed_matrix)
        changed_certificate["matrix_sha256"] = digest(matrix_path)
        cert_path = MemoryPath(args.certificate, changed_certificate)
        result, reason = None, None
        try:
            result = audit(candidate_path or args.candidate, matrix_path, cert_path)
        except ValueError as error:
            reason = str(error)
        passed = result is not None
        require(passed == expected_pass, f"Unexpected control result {name}: {reason or 'accepted'}")
        if not expected_pass:
            require(expected_reason in reason, f"Wrong rejection layer for {name}: {reason}")
        record = dict(name=name, expected="ACCEPT" if expected_pass else "REJECT", observed="ACCEPT" if passed else "REJECT",
                      matrix_sha256=digest(matrix_path), certificate_sha256=digest(cert_path),
                      matrix_hash_rebound=True, reason=reason)
        if passed:
            record.update(audit_status=result["status"], contradiction_margin=result["contradiction_margin"])
        records.append(record)

    def wrong_base(m, c):
        bound_name = next(name for name in m["inputs_sha256"] if Path(name).resolve() == args.candidate.resolve())
        del m["inputs_sha256"][bound_name]
        m["inputs_sha256"][str(args.wrong_base)] = digest(args.wrong_base)
        c["candidate_sha256"] = digest(args.wrong_base)

    trial("legal_wrong_base_fixed_coordinates_rebound", wrong_base, "mismatch", candidate_path=args.wrong_base)
    trial("wrong_matching_class", lambda m,c: m.update(matching_class="same_1"), "mismatch")
    trial("wrong_root_group", lambda m,c: m.update(root_group=(m["root_group"]+1)%7), "mismatch")
    for field in ("edge_variables", "matching_variables"):
        def swap_columns(m, c, field=field):
            m[field][0], m[field][1] = m[field][1], m[field][0]
        trial("swapped_" + field, swap_columns, "column coordinates/order mismatch")

    weighted = {row for row, _ in certificate["weighted_rows"]}
    weighted_row = certificate["weighted_rows"][0][0]
    unused_row = next(row for row in range(matrix["nrows"]) if row not in weighted and matrix["csr_start"][row] < matrix["csr_start"][row+1])
    for name, row in (("weighted", weighted_row), ("unweighted", unused_row)):
        def coefficient(m, c, row=row):
            k = m["csr_start"][row]
            m["csr_value"][k] *= 2
            recalculate(m, c)
        trial(name + "_row_coefficient_with_recomputed_proof", coefficient, "Independent row coefficient mismatch")
    upper_index = next(i for i,(r,n) in enumerate(certificate["weighted_rows"]) if matrix["row_lower"][r] is None and matrix["row_upper"][r] is not None)
    upper_row = certificate["weighted_rows"][upper_index][0]

    def tightened_bound(m, c):
        m["row_upper"][upper_row] -= 1
        recalculate(m, c)
    trial("tightened_upper_bound_with_recomputed_proof", tightened_bound, "Row bound mismatch")
    for field, column, value in (("col_upper", 0, 2), ("col_lower", 0, 1),
                                  ("col_cost", 1740, 0), ("col_upper", 1740, 1)):
        def bad_column(m, c, field=field, column=column, value=value):
            m[field][column] = value
        trial(f"{field}_column_{column}_value_{value}", bad_column, "Column bounds/cost mismatch")

    def remove_row(m, c):
        row = unused_row
        start, end = m["csr_start"][row:row+2]
        width = end-start
        del m["csr_index"][start:end]
        del m["csr_value"][start:end]
        m["csr_start"] = m["csr_start"][:row+1]+[value-width for value in m["csr_start"][row+2:]]
        del m["row_lower"][row]
        del m["row_upper"][row]
        m["nrows"] -= 1
        c["matrix_rows"] -= 1
        c["weighted_rows"] = [[i-(i>row), n] for i,n in c["weighted_rows"]]
        recalculate(m, c)
        require(c["combined_coefficients"] == certificate["combined_coefficients"] and c["contradiction_margin"] == certificate["contradiction_margin"],
                "Removing an unused row changed the proof arithmetic")
    trial("missing_unweighted_row_with_consistent_csr_and_proof", remove_row, "Matrix dimensions mismatch")

    def duplicate_row(m, c):
        c["weighted_rows"].insert(1, list(c["weighted_rows"][0]))
    trial("duplicate_multiplier_row", duplicate_row, "Duplicate/unsorted/out-of-range/zero weighted row")
    trial("omitted_multiplier_row", lambda m,c: c["weighted_rows"].pop(), "Declared combined coefficients mismatch")

    def flipped_sign(m, c):
        c["weighted_rows"][upper_index][1] *= -1
    trial("wrong_upper_only_multiplier_sign", flipped_sign, "Multiplier sign selects an infinite row bound")

    def altered_coefficient(m, c):
        c["combined_coefficients"][0] += 1
    trial("wrong_combined_coefficient", altered_coefficient, "Declared combined coefficients mismatch")
    for field in ("combined_lower_rhs", "box_upper_bound", "contradiction_margin"):
        def scalar(m, c, field=field):
            c[field] += 1
        trial("wrong_"+field, scalar, "Declared exact proof scalar mismatch")
    for value, label in ((1.0, "float"), (True, "boolean")):
        def noninteger(m, c, value=value):
            c["weighted_rows"][0][1] = value
        trial(label+"_multiplier", noninteger, "Invalid weighted row")
    trial("empty_proof", lambda m,c: c.update(weighted_rows=[]), "No exact zero-slack contradiction")
    trial("wrong_projected_dimension", lambda m,c: c.update(projected_box_columns=1741), "Certificate projected dimensions mismatch")
    trial("missing_zeroed_slack", lambda m,c: c.update(zeroed_slack_columns=5165), "Certificate projected dimensions mismatch")

    scale = 10**30
    def arbitrary_integer_scale(m, c):
        c["weighted_rows"] = [[row, n*scale] for row,n in c["weighted_rows"]]
        c["combined_coefficients"] = [n*scale for n in c["combined_coefficients"]]
        for field in ("combined_lower_rhs", "box_upper_bound", "contradiction_margin", "multiplier_scale"):
            c[field] *= scale
    trial("positive_uniform_rescaling_beyond_i64", arbitrary_integer_scale, None, expected_pass=True)
    require(digest(auditor) == AUDITOR_SHA and digest(Path(__file__)) == source_hash, "Source changed during controls")
    report = dict(status="INDEPENDENT_WHOLE_MATCHING_FARKAS_CORRUPTION_CONTROLS_PASS",
                  reviewer_sha256=source_hash, auditor_sha256=AUDITOR_SHA,
                  inputs_sha256={str(path):digest(path) for path in (args.candidate,args.matrix,args.certificate,args.wrong_base,auditor,Path(__file__).with_name("audit_certificate.py"))},
                  baseline_status=baseline["status"], baseline_contradiction_margin=baseline["contradiction_margin"],
                  negative_controls=len(records)-1, all_negative_controls_rejected=True, additional_positive_controls=1,
                  baseline_full_semantic_audit_performed=True, arbitrary_integer_scale=scale,
                  wrong_base_full99_partial_caps_valid=True, wrong_base_changes_fixed_coordinates=True,
                  controls=records, all_mutations_in_memory_only=True, producer_or_optimizer_imported=False,
                  elapsed_seconds=time.perf_counter()-started,
                  scope="Regression and adversarial corruption checks of the frozen independent checker; these supplement its exact matrix/proof audit, not a general proof of software correctness or a global Conway exclusion.")
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("controls","inputs_sha256")}))


if __name__ == "__main__":
    main()
