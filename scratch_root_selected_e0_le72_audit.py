"""Aggregate audit of the selected-root reduction E0 <= 72.

This binds the self-contained side theorem, the solver-free E0>=75
exclusions, and the separately certificate-checked E0=74 and E0=73
exclusions.  It also recomputes the elementary high-E0 diagonal-capacity
case split without importing any search generator.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


OUTPUT = Path("scratch_root_selected_e0_le72_audit.json")
SUMMARY = Path("scratch_root_selected_e0_le72_audit.md")
FILES = {
    "side": Path("scratch_root_side_bound_selfcontained_audit.json"),
    "e75": Path("scratch_theory_e75_gram_audit.json"),
    "e75_independent": Path("scratch_theory_e75_gram_independent_audit.json"),
    "e76": Path("scratch_theory_e76_analytic_audit.json"),
    "e76_independent": Path("scratch_theory_e76_occupancy_independent_audit.json"),
    "e73": Path("scratch_root_e73_q4_formal_exclusion_audit.json"),
    "e74": Path("scratch_root_e74_q5_formal_exclusion_audit.json"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def deficit_partitions(total: int, maximum_parts: int = 21):
    """Nonincreasing partitions with parts in 1..4."""
    answer = []

    def visit(remaining, ceiling, prefix):
        if not remaining:
            answer.append(tuple(prefix))
            return
        if len(prefix) == maximum_parts:
            return
        for value in range(min(ceiling, 4, remaining), 0, -1):
            visit(remaining - value, value, prefix + [value])

    visit(total, 4, [])
    return answer


def main() -> None:
    errors = []
    documents = {name: load(path) for name, path in FILES.items()}

    def require(condition, message):
        if not condition:
            errors.append(message)

    side = documents["side"]
    require(side.get("ok") is True, "side audit not ok")
    require(side.get("status") == "LOGIC_AND_ARITHMETIC_VERIFIED", "side status")
    require("S(r)<=69" in side.get("conclusion", ""), "side conclusion")

    capacity = {0: 0, 1: 0, 2: 2, 3: 1, 4: 0}
    high_rows = []
    for e0 in range(77, 85):
        deficit = 84 - e0
        partitions = deficit_partitions(deficit)
        maximum_q = max(
            (sum(capacity[value] for value in partition) for partition in partitions),
            default=0,
        )
        required_q = e0 - 69
        require(maximum_q < required_q, f"capacity does not exclude E0={e0}")
        high_rows.append({
            "E0": e0,
            "total_deficit": deficit,
            "partitions_checked": len(partitions),
            "maximum_Q_capacity": maximum_q,
            "required_Q_from_S_le_69": required_q,
            "excluded": maximum_q < required_q,
        })

    e75 = documents["e75"]
    e75i = documents["e75_independent"]
    require(e75.get("status") == "EXACT_ARITHMETIC_VERIFIED", "E75 exact status")
    require(e75.get("totals", {}).get("labelled_weighted_placements") == 1_210_965, "E75 placement coverage")
    require(e75.get("totals", {}).get("PSD_compatible_placements") == 0, "E75 PSD survivors")
    require(e75i.get("status") == "INDEPENDENT_GRAPH_CLASSIFICATION_VERIFIED", "E75 independent status")
    require(e75i.get("total_weighted_cases_after_degree_one_filter") == 48_930, "E75 independent cases")
    require(e75i.get("total_compatible_cases") == 0, "E75 independent survivors")

    e76 = documents["e76"]
    e76i = documents["e76_independent"]
    require(e76.get("status") == "EXACT_ARITHMETIC_VERIFIED", "E76 exact status")
    require(e76.get("fibre_capacity", {}).get("forced_Q") == 8, "E76 forced Q")
    require(e76.get("collision_equalities", {}).get("equality_forced") is True, "E76 equality chain")
    require(e76.get("conclusion") == "The selected root cannot have E0=76.", "E76 conclusion")
    require(e76i.get("status") == "INDEPENDENT_EXHAUSTIVE_OCCUPANCY_VERIFIED", "E76 independent status")
    require(e76i.get("target_reachable") is True, "E76 occupancy target")
    require(e76i.get("any_target_path_with_nonzero_spoke_q") is False, "E76 spoke equality")
    require(e76i.get("any_target_path_with_outside_abs_q_not_four") is False, "E76 outside equality")

    for value in (73, 74):
        audit = documents[f"e{value}"]
        require(audit.get("ok") is True, f"E{value} formal audit not ok")
        require(
            audit.get("status") == "FORMAL_COMPUTER_ASSISTED_EXCLUSION_VERIFIED",
            f"E{value} formal status",
        )
    checker73 = documents["e73"].get("checker_fingerprint", {})
    checker74 = documents["e74"].get("checker_fingerprint", {})
    require(checker73.get("binary_sha256") == checker74.get("binary_sha256"), "proof checker binary mismatch")
    require(checker73.get("upstream_commit") == checker74.get("upstream_commit"), "proof checker commit mismatch")

    result = {
        "status": "SELECTED_ROOT_E0_LE_72_VERIFIED" if not errors else "AUDIT_FAILED",
        "ok": not errors,
        "errors": errors,
        "theorem": "Every putative srg(99,14,1,2) has a root r with S(r)<=69 and E0(r)<=72.",
        "logical_chain": [
            "the self-contained triangle/prism argument selects a root with S<=69",
            "Q=E0-S and the exact fibre catalogue exclude E0>=77 by diagonal capacity",
            "exact Gram circulation and an independent graph classification exclude E0=75",
            "the integral residual/collision argument and an independent occupancy census exclude E0=76",
            "complete local reductions plus independently checked hash-bound DRUP proofs exclude E0=74 and E0=73",
            "therefore the selected root has E0<=72",
        ],
        "capacity_rows_E0_77_through_84": high_rows,
        "computer_assisted_branches": {
            "E0_74": documents["e74"].get("coverage_totals"),
            "E0_73": documents["e73"].get("coverage_totals"),
        },
        "proof_checker": {
            "binary_sha256": checker73.get("binary_sha256"),
            "source_sha256": checker73.get("source_sha256"),
            "upstream_commit": checker73.get("upstream_commit"),
        },
        "artifacts": {
            name: {"path": str(path), "sha256": sha256(path)}
            for name, path in FILES.items()
        },
        "claim_boundary": (
            "This is a necessary selected-root reduction, not a construction or "
            "a nonexistence proof. The E0<=72 search remains open."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    SUMMARY.write_text(
        "# Selected-root reduction to E0 <= 72\n\n"
        f"Status: `{result['status']}`.  \n"
        f"Errors: `{len(errors)}`.\n\n"
        "The self-contained side bound selects a root with `S<=69`. "
        "Solver-free arguments exclude `E0>=75`; complete local enumerations "
        "and independently checked, hash-bound DRUP certificates exclude "
        "`E0=74` and `E0=73`. Hence every putative target has a selected root "
        "with `E0<=72`.\n\n"
        "This does not settle existence: the `E0<=72` region remains.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "errors": len(errors)}))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
