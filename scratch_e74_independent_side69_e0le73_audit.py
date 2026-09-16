"""Independent byte/coordinate audit of the side69 + E0<=73 search CNF.

This file deliberately does not import the builder being audited.  It
reconstructs the 84 rooted outer labels, their 3,486 edge-variable numbers,
the 126 same-fibre variables, and the PySAT sequential-counter suffix.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


INPUT_CNF = Path("scratch_root_side_le69.cnf")
INPUT_META = Path("scratch_root_side_le69_build.json")
OUTPUT_CNF = Path("scratch_root_side69_e0le73.cnf")
OUTPUT_META = Path("scratch_root_side69_e0le73_build.json")
BUILDER = Path("scratch_root_side69_e0le73_sat.py")
DIRECT_VERIFIER = Path("scratch_general_exact_sat.py")
GRAPH_CHECKER = Path("scratch_bp_seed.py")
SIDE_SOURCE = Path("scratch_root_side_bound_selfcontained.json")
AUDIT_OUTPUT = Path("scratch_e74_independent_side69_e0le73_audit.json")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def split_dimacs(data: bytes) -> tuple[int, int, bytes, bytes]:
    end = data.find(b"\n")
    if end < 0:
        raise ValueError("DIMACS file has no header newline")
    header = data[: end + 1]
    fields = header.decode("ascii").strip().split()
    if len(fields) != 4 or fields[:2] != ["p", "cnf"]:
        raise ValueError(f"unexpected first line: {header!r}")
    return int(fields[2]), int(fields[3]), header, data[end + 1 :]


def first_difference(left: bytes, right: bytes) -> int | None:
    upto = min(len(left), len(right))
    for offset in range(upto):
        if left[offset] != right[offset]:
            return offset
    return None if len(left) == len(right) else upto


def independent_coordinates() -> dict[str, object]:
    # This is an explicit reconstruction, not a call to coordinates() in the
    # production model.  Lexicographic label order is the rooted-model order.
    labels = [
        (a, b)
        for a in range(14)
        for b in range(a + 1, 14)
        if a // 2 != b // 2
    ]
    if len(labels) != 84 or len(set(labels)) != 84:
        raise AssertionError("outer-label reconstruction failed")

    pair_variable: dict[tuple[int, int], int] = {}
    variable = 1
    for u in range(84):
        for v in range(u + 1, 84):
            pair_variable[(u, v)] = variable
            variable += 1
    if variable != 3487:
        raise AssertionError("outer-pair numbering failed")

    fibres: dict[tuple[int, int], list[int]] = {}
    for u, (a, b) in enumerate(labels):
        fibres.setdefault((a // 2, b // 2), []).append(u)
    if len(fibres) != 21 or any(len(vertices) != 4 for vertices in fibres.values()):
        raise AssertionError("fibre reconstruction failed")

    sides: list[int] = []
    diagonals: list[int] = []
    per_fibre: list[dict[str, object]] = []
    for support, vertices in sorted(fibres.items()):
        fibre_sides: list[int] = []
        fibre_diagonals: list[int] = []
        for i, u in enumerate(vertices):
            for v in vertices[i + 1 :]:
                edge_variable = pair_variable[(u, v)]
                common_symbols = len(set(labels[u]).intersection(labels[v]))
                if common_symbols == 1:
                    sides.append(edge_variable)
                    fibre_sides.append(edge_variable)
                elif common_symbols == 0:
                    diagonals.append(edge_variable)
                    fibre_diagonals.append(edge_variable)
                else:
                    raise AssertionError("distinct same-fibre labels overlap twice")
        if len(fibre_sides) != 4 or len(fibre_diagonals) != 2:
            raise AssertionError("a fibre is not a four-cycle plus two diagonals")
        per_fibre.append(
            {
                "support": list(support),
                "outer_indices": vertices,
                "labels": [list(labels[u]) for u in vertices],
                "side_variables": sorted(fibre_sides),
                "diagonal_variables": sorted(fibre_diagonals),
            }
        )
    return {
        "labels": labels,
        "side_variables": sorted(sides),
        "diagonal_variables": sorted(diagonals),
        "local_variables": sorted(sides + diagonals),
        "per_fibre": per_fibre,
    }


def main() -> None:
    # Imported only for independently regenerating the documented encoding;
    # the audited builder module itself is never imported.
    from pysat.card import CardEnc, EncType

    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    input_meta = json.loads(INPUT_META.read_text(encoding="utf-8"))
    output_meta = json.loads(OUTPUT_META.read_text(encoding="utf-8"))
    side_source = json.loads(SIDE_SOURCE.read_text(encoding="utf-8"))
    input_data = INPUT_CNF.read_bytes()
    output_data = OUTPUT_CNF.read_bytes()
    input_variables, input_clauses, input_header, input_body = split_dimacs(input_data)
    output_variables, output_clauses, output_header, output_body = split_dimacs(output_data)

    input_hash = sha256_bytes(input_data)
    output_hash = sha256_bytes(output_data)
    side_source_hash = sha256_file(SIDE_SOURCE)
    check(input_hash == input_meta.get("cnf_sha256"), "input CNF hash != input metadata")
    check(input_hash == output_meta.get("input_cnf_sha256"), "input CNF hash != output metadata")
    check(output_hash == output_meta.get("cnf_sha256"), "output CNF hash != output metadata")
    check(side_source_hash == output_meta.get("side_bound_source_sha256"), "side-source hash mismatch")
    check((input_variables, input_clauses) == (818313, 1624518), "unexpected input header")
    check((output_variables, output_clauses) == (822182, 1632236), "unexpected output header")
    check(input_meta.get("variables") == input_variables, "input variable count metadata mismatch")
    check(input_meta.get("clauses") == input_clauses, "input clause count metadata mismatch")
    check(output_meta.get("variables") == output_variables, "output variable count metadata mismatch")
    check(output_meta.get("clauses") == output_clauses, "output clause count metadata mismatch")
    check(len(input_body.splitlines()) == input_clauses, "input body line count != clause count")
    check(len(output_body.splitlines()) == output_clauses, "output body line count != clause count")
    check(b"\r" not in input_data and b"\r" not in output_data, "CNF is not LF-only")
    check(input_data.endswith(b"\n") and output_data.endswith(b"\n"), "CNF lacks final LF")

    coordinates = independent_coordinates()
    sides = coordinates["side_variables"]
    diagonals = coordinates["diagonal_variables"]
    local = coordinates["local_variables"]
    assert isinstance(sides, list) and isinstance(diagonals, list) and isinstance(local, list)
    check(len(sides) == 84 and len(set(sides)) == 84, "side count is not 84")
    check(len(diagonals) == 42 and len(set(diagonals)) == 42, "diagonal count is not 42")
    check(set(sides).isdisjoint(diagonals), "side and diagonal sets overlap")
    check(len(local) == 126 and len(set(local)) == 126, "local E0 count is not 126")
    check(sides == input_meta.get("side_variables"), "independent sides != input metadata")
    check(
        diagonals == input_meta.get("diagonal_variables_not_bounded"),
        "independent diagonals != input metadata",
    )
    check(local == output_meta.get("e0_variables"), "independent E0 variables != output metadata")
    check(output_meta.get("e0_variable_count") == 126, "output E0 count metadata mismatch")

    card = CardEnc.atmost(
        lits=local,
        bound=73,
        top_id=input_variables,
        encoding=EncType.seqcounter,
    )
    expected_suffix = b"".join(
        (" ".join(map(str, clause)) + " 0\n").encode("ascii")
        for clause in card.clauses
    )
    body_prefix = output_body[: len(input_body)]
    actual_suffix = output_body[len(input_body) :]
    body_preserved = body_prefix == input_body
    suffix_identical = actual_suffix == expected_suffix
    check(body_preserved, "input CNF body is not a byte-identical output prefix")
    check(suffix_identical, "sequential-counter suffix is not byte-identical")
    check(card.nv - input_variables == 3869, "sequential counter did not add 3869 variables")
    check(len(card.clauses) == 7718, "sequential counter did not add 7718 clauses")
    check(3869 == 73 * (126 - 73), "added-variable arithmetic identity failed")
    clause_length_histogram = Counter(map(len, card.clauses))
    check(
        clause_length_histogram == {2: 3902, 3: 3816},
        "unexpected sequential-counter clause-length histogram",
    )
    check(output_variables == card.nv, "output max variable != regenerated counter max")
    check(output_clauses == input_clauses + len(card.clauses), "output clause total mismatch")
    check(output_header == b"p cnf 822182 1632236\n", "output header bytes differ")
    check(output_hash == "7FAB56D135701EB8CAE8F7179E337B85E0EC679E571F5BA6D186E93CD50E7923", "unexpected output hash")
    check(input_hash == "C2B9C01DC6E11EC03E5B387060FCA71FEDA893BA12C007F0105326A1D7CB9828", "unexpected input hash")

    builder_text = BUILDER.read_text(encoding="utf-8")
    verifier_text = DIRECT_VERIFIER.read_text(encoding="utf-8")
    checker_text = GRAPH_CHECKER.read_text(encoding="utf-8")
    sat_gate_checks = {
        "model_requested_on_sat": "model = solver.get_model()" in builder_text,
        "only_3486_graph_variables_decoded": "0 < lit <= 3486" in builder_text,
        "direct_verifier_called": "verified = verify(positive)" in builder_text,
        "bad_verification_rejected": 'if not verified["ok"]:' in builder_text
        and "raise AssertionError" in builder_text,
        "solution_written_only_after_gate": builder_text.find('if not verified["ok"]:')
        < builder_text.find('Path("scratch_root_side69_e0le73_solution.json")'),
        "verifier_expands_graph": "expand_and_check(labels, variables, positive)" in verifier_text,
        "checker_has_99_adjacency_rows": "adj = [set() for _ in range(99)]" in checker_text,
        "checker_tests_all_99_pairs": "for u in range(99):" in checker_text
        and "for v in range(u + 1, 99):" in checker_text,
        "checker_requires_degree_14": "assert degrees == [14] * 99" in checker_text,
        "checker_requires_693_edges": "assert len(edges) == 693" in checker_text,
        "verifier_requires_zero_pair_residual": 'result["energy"] == 0' in verifier_text
        and 'result["bad_pairs"] == 0' in verifier_text,
    }
    for name, passed in sat_gate_checks.items():
        check(passed, f"SAT verification gate static check failed: {name}")

    nonformal_checks = {
        "metadata_marks_search_strengthening": output_meta.get("status")
        == "BUILT_SEARCH_STRENGTHENING",
        "computational_premises_have_no_certificate": output_meta.get(
            "proof_certificate_for_computational_premises"
        )
        is False,
        "claim_explicitly_rejects_formal_unsat_conclusion": "UNSAT is not a formal"
        in output_meta.get("claim_boundary", ""),
        "side_source_is_arithmetic_verified": side_source.get("status")
        == "ARITHMETIC_VERIFIED",
        "side_source_yields_69": side_source.get("prism_and_root_side", {}).get(
            "some_root_side_ceiling"
        )
        == 69,
        "side_source_itself_claims_no_formal_certificate": side_source.get(
            "claim_boundary", {}
        ).get("formal_proof_certificate")
        is False,
    }
    for name, passed in nonformal_checks.items():
        check(passed, f"scope check failed: {name}")

    result = {
        "status": "AUDIT_PASS" if not errors else "AUDIT_FAIL",
        "ok": not errors,
        "errors": errors,
        "independence": {
            "builder_imported": False,
            "coordinates_imported": False,
            "coordinates_method": "explicit lexicographic reconstruction of 84 labels and 3486 pairs",
            "counter_method": "fresh PySAT CardEnc.atmost(seqcounter) regeneration",
        },
        "files": {
            "input_cnf": str(INPUT_CNF),
            "input_sha256": input_hash,
            "output_cnf": str(OUTPUT_CNF),
            "output_sha256": output_hash,
            "builder": str(BUILDER),
            "builder_sha256": sha256_file(BUILDER),
            "side_source": str(SIDE_SOURCE),
            "side_source_sha256": side_source_hash,
        },
        "headers": {
            "input": {"variables": input_variables, "clauses": input_clauses},
            "output": {"variables": output_variables, "clauses": output_clauses},
        },
        "body_preservation": {
            "input_body_bytes": len(input_body),
            "input_body_sha256": sha256_bytes(input_body),
            "output_prefix_bytes": len(body_prefix),
            "output_prefix_sha256": sha256_bytes(body_prefix),
            "byte_identical": body_preserved,
            "first_difference": first_difference(input_body, body_prefix),
        },
        "e0_coordinate_audit": {
            "outer_vertices": 84,
            "fibres": 21,
            "vertices_per_fibre": 4,
            "side_variables": 84,
            "diagonal_variables": 42,
            "e0_variables": 126,
            "side_definition": "same support and one common inner symbol (Hamming distance 1)",
            "diagonal_definition": "same support and no common inner symbol (Hamming distance 2)",
            "all_lists_match_metadata": sides == input_meta.get("side_variables")
            and diagonals == input_meta.get("diagonal_variables_not_bounded")
            and local == output_meta.get("e0_variables"),
            "per_fibre": coordinates["per_fibre"],
        },
        "sequential_counter_suffix": {
            "bound": 73,
            "input_count": 126,
            "added_variables": card.nv - input_variables,
            "added_clauses": len(card.clauses),
            "clause_length_histogram": {
                str(length): count for length, count in sorted(clause_length_histogram.items())
            },
            "expected_suffix_bytes": len(expected_suffix),
            "actual_suffix_bytes": len(actual_suffix),
            "expected_suffix_sha256": sha256_bytes(expected_suffix),
            "actual_suffix_sha256": sha256_bytes(actual_suffix),
            "byte_identical": suffix_identical,
            "first_difference": first_difference(expected_suffix, actual_suffix),
        },
        "sat_direct_verification_gate": sat_gate_checks,
        "claim_scope": {
            "checks": nonformal_checks,
            "conclusion": (
                "A SAT model is usable only after the built-in direct 99-vertex verification. "
                "A solver UNSAT result for this restricted CNF is computational and not a "
                "formal nonexistence proof, because inherited E0 exclusions lack DRAT/LRAT certificates."
            ),
        },
    }
    AUDIT_OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "errors": errors}, sort_keys=True))


if __name__ == "__main__":
    main()
