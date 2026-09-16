"""Hash-bound audit of the formal E72 source-row 134 elimination."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import scratch_root_e72_source134_state_sat as pilot


SELECTOR_META = Path("scratch_root_e72_source134_selector.json")
DRAT_AUDIT = Path("scratch_root_e72_source134_selector_drat_audit.json")
OUTPUT = Path("scratch_root_e72_source134_formal_audit.json")
REPORT = Path("scratch_root_e72_source134_formal_audit.md")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def update_clause(digest, clause) -> None:
    digest.update((" ".join(map(str, clause)) + " 0\n").encode("ascii"))


def hash_base_plus(base: Path, variables: int, clause_count: int, suffix) -> str:
    digest = hashlib.sha256()
    digest.update(f"p cnf {variables} {clause_count}\n".encode("ascii"))
    with base.open("rb") as handle:
        header = handle.readline()
        assert header.startswith(b"p cnf ")
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    for clause in suffix:
        update_clause(digest, clause)
    return digest.hexdigest().upper()


def exactly_two_truth_table() -> dict:
    variables = tuple(range(1, 17))
    clauses = pilot.exactly_two_clauses(variables)
    accepted = 0
    for mask in range(1 << 16):
        satisfied = all(
            any(
                bool(mask & (1 << (abs(literal) - 1))) == (literal > 0)
                for literal in clause
            )
            for clause in clauses
        )
        expected = mask.bit_count() == 2
        assert satisfied == expected
        accepted += satisfied
    assert accepted == len(tuple(itertools.combinations(range(16), 2))) == 120
    return {
        "assignments_tested": 1 << 16,
        "accepted_assignments": accepted,
        "expected_weight_two_assignments": 120,
        "encoding_equivalence_verified": True,
    }


def main() -> None:
    build = json.loads(pilot.BUILD.read_text(encoding="utf-8"))
    checkpoint_path = Path("scratch_root_e72_source134_state_c1000000.json")
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    selector = json.loads(SELECTOR_META.read_text(encoding="utf-8"))
    drat = json.loads(DRAT_AUDIT.read_text(encoding="utf-8"))

    row, _raw = pilot.selected_row()
    branches, orbit_audit = pilot.state_orbits(row)
    assert orbit_audit == build["state_orbit_audit"]
    assert [list(item["state_indices"]) for item in branches] == [
        item["state_indices"] for item in build["branches"]
    ]
    assert [item["state_orbit_size"] for item in branches] == [
        item["state_orbit_size"] for item in build["branches"]
    ]
    assert sum(item["state_orbit_size"] for item in branches) == 181

    base_audit = pilot.cnf_audit(pilot.CNF_PATH)
    assert base_audit == build["unrestricted_base_cnf_audit"]
    assert base_audit["unit_clauses"] == 0
    assert build["historical_portfolio_branch_units_applied"] is False
    macro_clauses, macro_audit = pilot.macro_common_clauses(row, branches)
    assert macro_audit == build["macro_layer_audit"]
    assert macro_audit["adjacent_exceptional_D2_blocks"] == 12
    assert macro_audit["opposite_exceptional_D0_blocks"] == 3
    assert macro_audit["catalog_exact_overlap_completion_coverage"] == 101593088

    macro_variables = base_audit["declared_variables"]
    macro_clause_count = base_audit["declared_clauses"] + len(macro_clauses)
    expected_macro_hash = hash_base_plus(
        pilot.CNF_PATH, macro_variables, macro_clause_count, macro_clauses
    )
    assert expected_macro_hash == sha256(pilot.MACRO_CNF)
    assert expected_macro_hash == build["macro_cnf_sha256"]
    macro_file_audit = pilot.cnf_audit(pilot.MACRO_CNF)
    assert macro_file_audit["declared_clauses"] == macro_clause_count
    assert macro_file_audit["unit_clauses"] == macro_audit["macro_unit_clauses"]

    assert checkpoint["status"] == "UNSAT" and checkpoint["checkpoint_complete"]
    assert checkpoint["completed_branches"] == checkpoint["direct_unsat"] == 5
    assert checkpoint["unknown"] == checkpoint["sat"] == 0
    assert checkpoint["labelled_states_covered"] == 181
    selector_suffix = []
    selectors = []
    selector_first = macro_variables + 1
    selectors = list(range(selector_first, selector_first + 5))
    selector_suffix.append(selectors)
    implication_count = 0
    for branch, record in zip(build["branches"], checkpoint["records"]):
        assert branch["branch_index"] == record["branch_index"]
        assert record["status"] == record["logical_status"] == "UNSAT"
        assumptions = frozenset(branch["assumptions"])
        core = tuple(record["assumption_core"])
        assert core and len(core) == len(set(core)) and set(core) <= assumptions
        for literal in core:
            selector_suffix.append([-selectors[branch["branch_index"]], literal])
            implication_count += 1
    assert implication_count == selector["selector_core_implications"]
    selector_clause_count = macro_clause_count + len(selector_suffix)
    expected_selector_hash = hash_base_plus(
        pilot.MACRO_CNF, selectors[-1], selector_clause_count, selector_suffix
    )
    # hash_base_plus used the macro file as its prefix, so its replacement
    # header is followed by exactly the macro body and then selector clauses.
    assert expected_selector_hash == selector["cnf_sha256"]
    assert expected_selector_hash == sha256(Path(selector["cnf"]))
    assert selector["clauses"] == selector_clause_count
    assert selector["variables"] == selectors[-1]
    assert selector["terminal_empty_clause_present"] is True
    assert selector["terminal_empty_clause_appended_for_external_check"] is False

    assert drat["status"] == "DRAT_VERIFIED" and drat["ok"] is True
    assert drat["cnf_sha256"] == selector["cnf_sha256"]
    assert drat["proof_sha256"] == selector["proof_sha256"]
    assert sha256(Path(selector["proof"])) == selector["proof_sha256"]
    assert drat["checker_upstream_commit"] == "2e3b2dc0ecf938addbd779d42877b6ed69d9a985"

    truth_table = exactly_two_truth_table()
    result = {
        "status": "FORMAL_AUDIT_PASS",
        "scope": "E72 source row 134, K4 deficit-two support orbit, unique Gram macro",
        "source_row_index": 134,
        "support_orbit_size": build["support_orbit_size"],
        "port_feasible_labelled_internal_states": 181,
        "state_orbits": 5,
        "state_orbit_sizes": [item["state_orbit_size"] for item in branches],
        "state_orbit_closure_and_partition_verified": True,
        "effective_residual_actions": orbit_audit["effective_residual_actions"],
        "labelled_state_matching_coverage": macro_audit["catalog_exact_overlap_completion_coverage"],
        "overlap_graphs_explicitly_enumerated_by_sat_lift": 0,
        "unrestricted_base_has_no_embedded_fixed_edge_units": True,
        "historical_portfolio_branch_units_applied": False,
        "macro": {
            "ordinary_c4_fibres": macro_audit["ordinary_c4_fibres"],
            "ordinary_overlap_zero_blocks": macro_audit["ordinary_overlap_zero_blocks"],
            "adjacent_exceptional_D2_blocks": macro_audit["adjacent_exceptional_D2_blocks"],
            "opposite_exceptional_D0_blocks": macro_audit["opposite_exceptional_D0_blocks"],
            "exactly_two_encoder_truth_table": truth_table,
            "variables": macro_file_audit["declared_variables"],
            "clauses": macro_file_audit["declared_clauses"],
            "cnf": str(pilot.MACRO_CNF),
            "cnf_sha256": expected_macro_hash,
            "byte_reconstruction_verified": True,
        },
        "computational_checkpoint": {
            "path": str(checkpoint_path),
            "sha256": sha256(checkpoint_path),
            "direct_unsat_branches": checkpoint["direct_unsat"],
            "unknown": checkpoint["unknown"],
        },
        "selector_certificate": {
            "selectors": 5,
            "selector_core_implications": implication_count,
            "variables": selector["variables"],
            "clauses": selector["clauses"],
            "cnf": selector["cnf"],
            "cnf_sha256": selector["cnf_sha256"],
            "cnf_byte_reconstruction_verified": True,
            "proof": selector["proof"],
            "proof_sha256": selector["proof_sha256"],
            "proof_lines": selector["proof_lines"],
            "external_checker_status": drat["status"],
            "checker": drat["checker"],
            "checker_sha256": drat["checker_sha256"],
            "checker_upstream_commit": drat["checker_upstream_commit"],
        },
        "inputs": {
            "pilot_script": str(Path(pilot.__file__).name),
            "pilot_script_sha256": sha256(Path(pilot.__file__)),
            "selector_script": "scratch_root_e72_source134_selector_drup.py",
            "selector_script_sha256": sha256(Path("scratch_root_e72_source134_selector_drup.py")),
            "build": str(pilot.BUILD),
            "build_sha256": sha256(pilot.BUILD),
            "selector_metadata": str(SELECTOR_META),
            "selector_metadata_sha256": sha256(SELECTOR_META),
            "drat_audit": str(DRAT_AUDIT),
            "drat_audit_sha256": sha256(DRAT_AUDIT),
        },
        "logical_conclusion": (
            "No exact rooted completion exists in E72 source row 134 for its unique "
            "Gram-feasible K4 macro signature."
        ),
        "claim_boundary": (
            "This is a machine-checked CNF/DRUP elimination of one support orbit. "
            "It is not by itself a formal proof that the upstream E72 census, port "
            "filter, Gram derivation, or all other E72 support rows are exhaustive."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# E72 source-row 134 formal audit\n\n"
        "Status: **FORMAL_AUDIT_PASS**.\n\n"
        "The 181 port-feasible labelled internal states form five exact residual-"
        "symmetry orbits.  The K4 Gram macro fixes 12 adjacent exceptional blocks "
        "to D=2 and three opposite blocks to D=0, covering 101,593,088 labelled "
        "state/matching completions without enumerating their overlap graphs.\n\n"
        f"The selector CNF has {selector['variables']:,} variables and "
        f"{selector['clauses']:,} clauses.  Its {selector['proof_lines']:,}-line "
        "DRUP certificate was independently accepted by the pinned drat-trim "
        f"commit `{drat['checker_upstream_commit']}`.\n\n"
        "Boundary: this certifies source row 134 and its unique Gram macro only; "
        "the upstream global E72 census/exhaustiveness bridge remains separate.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "state_orbits": result["state_orbits"],
        "labelled_states": result["port_feasible_labelled_internal_states"],
        "matching_coverage": result["labelled_state_matching_coverage"],
        "proof_lines": result["selector_certificate"]["proof_lines"],
        "drat": result["selector_certificate"]["external_checker_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
