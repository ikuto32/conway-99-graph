"""Independent mechanical/scope audit of the corrected S(r) <= 69 CNF.

The public proof of n3 >= 708 is deliberately outside this audit.  No SAT
solve is run.  The appended sequential counter is rebuilt and compared byte
for byte, and the 84 side inputs are reconstructed without using the target
builder's coordinate helper.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys


TARGET_SOURCE = Path("scratch_root_side_bound_sat.py")
BASE = Path("scratch_general_exact.cnf")
BASE_META = Path("scratch_general_exact_build.json")
CONDITIONED = Path("scratch_root_side_le69.cnf")
BUILD_META = Path("scratch_root_side_le69_build.json")
PORTFOLIO = Path("scratch_root_side_le69_portfolio.json")
OLD_E0_META = Path("scratch_root_e0_le69_build.json")
OLD_E0_CNF = Path("scratch_root_e0_le69.cnf")
OUTPUT = Path("scratch_root_side_bound_audit.json")
PINNED_BASE_SHA256 = (
    "91D22E62625E1221DD46B819E89494DB8141DD4DDC9A06F13B9ABDB530B83242"
)


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest().upper()


def sha256(path):
    return sha256_bytes(path.read_bytes())


def split_dimacs(raw):
    header, newline, body = raw.partition(b"\n")
    if not newline:
        raise ValueError("DIMACS has no header newline")
    fields = header.decode("ascii").split()
    if len(fields) != 4 or fields[:2] != ["p", "cnf"]:
        raise ValueError(f"bad DIMACS header {fields}")
    return (int(fields[2]), int(fields[3])), body


def independent_coordinates_and_partition():
    labels = tuple(
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    )
    variables = {
        pair: identifier
        for identifier, pair in enumerate(itertools.combinations(range(84), 2), 1)
    }
    sides = []
    diagonals = []
    same_by_fibre = Counter()
    side_by_fibre = Counter()
    diagonal_by_fibre = Counter()
    for (u, v), identifier in variables.items():
        left_support = tuple(symbol // 2 for symbol in labels[u])
        right_support = tuple(symbol // 2 for symbol in labels[v])
        if left_support != right_support:
            continue
        fibre = left_support
        same_by_fibre[fibre] += 1
        common_symbols = len(set(labels[u]).intersection(labels[v]))
        if common_symbols == 1:
            sides.append(identifier)
            side_by_fibre[fibre] += 1
        elif common_symbols == 0:
            diagonals.append(identifier)
            diagonal_by_fibre[fibre] += 1
        else:
            raise AssertionError("distinct same-fibre vertices meet in 0 or 1 symbols")
    return {
        "labels": labels,
        "variables": variables,
        "sides": tuple(sorted(sides)),
        "diagonals": tuple(sorted(diagonals)),
        "same_by_fibre": same_by_fibre,
        "side_by_fibre": side_by_fibre,
        "diagonal_by_fibre": diagonal_by_fibre,
    }


def parse_suffix_clauses(raw):
    clauses = []
    for line_number, raw_line in enumerate(raw.splitlines(), 1):
        values = list(map(int, raw_line.split()))
        if not values or values[-1] != 0 or 0 in values[:-1]:
            raise ValueError(f"bad suffix clause line {line_number}")
        clauses.append(values[:-1])
    return clauses


def main():
    errors = []
    warnings = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    independent = independent_coordinates_and_partition()
    sides = independent["sides"]
    diagonals = independent["diagonals"]
    same = frozenset(sides) | frozenset(diagonals)
    require(len(independent["labels"]) == 84, "outer label count differs")
    require(len(independent["variables"]) == 3486, "outer variable count differs")
    require(len(sides) == 84, "side count is not 84")
    require(len(diagonals) == 42, "diagonal count is not 42")
    require(not set(sides).intersection(diagonals), "side/diagonal sets overlap")
    require(len(same) == 126, "same-fibre union is not 126")
    require(
        len(independent["same_by_fibre"]) == 21
        and set(independent["same_by_fibre"].values()) == {6},
        "same-fibre candidates are not 6 per fibre",
    )
    require(
        set(independent["side_by_fibre"].values()) == {4},
        "side candidates are not 4 per fibre",
    )
    require(
        set(independent["diagonal_by_fibre"].values()) == {2},
        "diagonal candidates are not 2 per fibre",
    )

    # Differential check of the target source's two selectors.
    import scratch_root_side_bound_sat as target

    target_sides = tuple(target.side_variables())
    target_diagonals = tuple(target.diagonal_variables())
    require(target_sides == sides, "target side_variables differs from independent set")
    require(
        target_diagonals == diagonals,
        "target diagonal_variables differs from independent set",
    )

    base_raw = BASE.read_bytes()
    conditioned_raw = CONDITIONED.read_bytes()
    base_header, base_body = split_dimacs(base_raw)
    conditioned_header, conditioned_body = split_dimacs(conditioned_raw)
    require(sha256(BASE) == PINNED_BASE_SHA256, "base CNF hash differs from pin")
    require(
        conditioned_body.startswith(base_body),
        "conditioned CNF does not preserve base clause body byte-for-byte",
    )
    appended = (
        conditioned_body[len(base_body):]
        if conditioned_body.startswith(base_body)
        else b""
    )

    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.card import CardEnc, EncType

    rebuilt = CardEnc.atmost(
        list(sides), bound=69, top_id=base_header[0], encoding=EncType.seqcounter
    )
    rebuilt_suffix = b"".join(
        (" ".join(map(str, clause)) + " 0\n").encode("ascii")
        for clause in rebuilt.clauses
    )
    require(appended == rebuilt_suffix, "appended suffix differs from rebuilt seqcounter")
    suffix_clauses = parse_suffix_clauses(appended)
    suffix_variables = {
        abs(literal) for clause in suffix_clauses for literal in clause
    }
    suffix_outer_inputs = {variable for variable in suffix_variables if variable <= 3486}
    suffix_old_aux = {
        variable for variable in suffix_variables if 3486 < variable <= base_header[0]
    }
    suffix_new_aux = {variable for variable in suffix_variables if variable > base_header[0]}
    require(suffix_outer_inputs == set(sides), "suffix outer inputs are not exactly sides")
    require(not suffix_outer_inputs.intersection(diagonals), "suffix contains a diagonal input")
    require(not suffix_old_aux, "suffix unexpectedly refers to a base auxiliary variable")
    require(
        suffix_new_aux == set(range(base_header[0] + 1, rebuilt.nv + 1)),
        "new sequential-counter auxiliary range is not contiguous/exhaustive",
    )
    require(len(suffix_clauses) == len(rebuilt.clauses), "suffix clause count differs")
    require(
        conditioned_header == (rebuilt.nv, base_header[1] + len(rebuilt.clauses)),
        "conditioned DIMACS header differs from reconstruction",
    )
    require(
        len(conditioned_raw.splitlines()) == conditioned_header[1] + 1,
        "conditioned DIMACS line count differs from header",
    )

    base_meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    meta = json.loads(BUILD_META.read_text(encoding="utf-8"))
    require(base_header == (817278, 1622502), "base header differs")
    require(base_meta.get("cnf_sha256") == sha256(BASE), "base metadata hash differs")
    require(
        (base_meta.get("variables"), base_meta.get("clauses")) == base_header,
        "base metadata/header differs",
    )
    require(meta.get("status") == "BUILT", "build status label differs")
    require(meta.get("base_cnf_sha256") == sha256(BASE), "build base hash differs")
    require(meta.get("bound") == 69, "metadata bound differs")
    require(meta.get("side_variable_count") == 84, "metadata side count differs")
    require(
        tuple(meta.get("side_variables", ())) == sides,
        "metadata side-variable list differs",
    )
    require(
        meta.get("diagonal_variable_count_excluded_from_cardinality") == 42,
        "metadata excluded diagonal count differs",
    )
    require(
        tuple(meta.get("diagonal_variables_not_bounded", ())) == diagonals,
        "metadata diagonal-variable list differs",
    )
    require(meta.get("added_variables") == rebuilt.nv - base_header[0], "added vars differ")
    require(meta.get("added_clauses") == len(rebuilt.clauses), "added clauses differ")
    require(
        (meta.get("variables"), meta.get("clauses")) == conditioned_header,
        "conditioned metadata/header differs",
    )
    require(meta.get("cnf_sha256") == sha256(CONDITIONED), "conditioned hash differs")
    require(
        meta.get("external_premises_not_replayed_here")
        == ["n3 >= 708", "n3 + 3 P = 4158"],
        "external premise scope field differs",
    )
    require(meta.get("internal_bridge") == "sum over roots of S(r) = 6 P", "bridge differs")
    require(
        meta.get("encoded_quantity") == "S(r): same-fibre square sides only",
        "encoded-quantity field differs",
    )
    require(
        "conditional" in meta.get("claim_boundary", "").lower()
        and "99 vertices" in meta.get("claim_boundary", ""),
        "claim boundary omits conditional UNSAT or direct SAT verification",
    )
    non69_fail_closed = False
    try:
        target.build(68, Path("scratch_root_side_bound_must_not_exist.cnf"), Path("scratch_root_side_bound_must_not_exist.json"))
    except ValueError:
        non69_fail_closed = True
    require(non69_fail_closed, "builder does not fail closed for a bound other than 69")
    require(
        not Path("scratch_root_side_bound_must_not_exist.cnf").exists()
        and not Path("scratch_root_side_bound_must_not_exist.json").exists(),
        "rejected non-69 build wrote an artifact",
    )

    # Arithmetic only: the external n3 proof itself is intentionally not replayed.
    n3_lower = 708
    constant = 4158
    p_upper = (constant - n3_lower) // 3
    six_p_upper = 6 * p_upper
    min_side_upper = six_p_upper // 99
    require((p_upper, six_p_upper, min_side_upper) == (1150, 6900, 69), "arithmetic differs")

    # Explicitly distinguish this sound conditional input set from the old,
    # quarantined 126-variable E0=S+D cardinality.
    old_meta = json.loads(OLD_E0_META.read_text(encoding="utf-8"))
    old_inputs = frozenset(old_meta.get("fibre_edge_variables", ()))
    require(old_meta.get("status") == "QUARANTINED_UNSOUND_PREMISE_NEVER_SOLVED", "old E0 artifact is not quarantined")
    require(old_inputs == same, "old 126-variable input is not sides union diagonals")
    require(set(sides) == old_inputs - set(diagonals), "corrected input is not old minus diagonals")
    require(sha256(CONDITIONED) != sha256(OLD_E0_CNF), "corrected and quarantined CNFs coincide")

    portfolio_status = None
    portfolio_counts = None
    if PORTFOLIO.exists():
        portfolio = json.loads(PORTFOLIO.read_text(encoding="utf-8"))
        portfolio_status = portfolio.get("status")
        portfolio_counts = portfolio.get("counts")
        require(portfolio_status != "UNSAT", "existing portfolio unexpectedly claims UNSAT")
        require(
            portfolio.get("external_premises_not_replayed_here")
            == meta.get("external_premises_not_replayed_here"),
            "portfolio premise scope differs from build metadata",
        )
        require(
            portfolio.get("claim_boundary") == meta.get("claim_boundary"),
            "portfolio claim boundary differs from build metadata",
        )

    document = {
        "status": (
            "FAILED" if errors
            else "VERIFIED_WITH_NONMATERIAL_WARNINGS" if warnings
            else "VERIFIED"
        ),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "scope": {
            "external_n3_lower_bound_proof_replayed": False,
            "identity_n3_plus_3P_replayed": False,
            "corrected_prism_bridge_reproved_here": False,
            "arithmetic_from_stated_external_premises_checked": True,
            "heavy_sat_sweep_run_by_this_audit": False,
            "existing_unknown_portfolio_used_as_proof": False,
        },
        "variable_partition": {
            "outer_vertices": 84,
            "outer_edge_variables": 3486,
            "support_fibres": 21,
            "same_fibre_candidates": 126,
            "sides_bounded": len(sides),
            "diagonals_excluded": len(diagonals),
            "per_fibre": {"same": 6, "sides": 4, "diagonals": 2},
            "side_selector": "same group-support fibre and exactly one shared symbol",
            "diagonal_selector": "same group-support fibre and zero shared symbols",
            "target_selector_matches_independent_reconstruction": (
                target_sides == sides and target_diagonals == diagonals
            ),
            "side_variables_sha256": hashlib.sha256(
                " ".join(map(str, sides)).encode("ascii")
            ).hexdigest().upper(),
            "diagonal_variables_sha256": hashlib.sha256(
                " ".join(map(str, diagonals)).encode("ascii")
            ).hexdigest().upper(),
        },
        "arithmetic_under_external_premises": {
            "premises": ["n3 >= 708", "n3 + 3 P = 4158", "sum_r S(r) = 6 P"],
            "P_upper": p_upper,
            "six_P_upper": six_p_upper,
            "floor_six_P_over_99": min_side_upper,
            "conclusion": "some root has S(r) <= 69",
            "does_not_imply": "some root has E0(r)=S(r)+D(r) <= 69",
            "external_proofs_not_replayed": True,
            "builder_rejects_every_bound_other_than_69": non69_fail_closed,
        },
        "cnf_audit": {
            "base_header": list(base_header),
            "conditioned_header": list(conditioned_header),
            "base_sha256": sha256(BASE),
            "base_clause_body_sha256": sha256_bytes(base_body),
            "base_clause_body_preserved_byte_for_byte": conditioned_body.startswith(base_body),
            "appended_suffix_sha256": sha256_bytes(appended),
            "appended_suffix_equals_rebuilt_pysat_seqcounter": appended == rebuilt_suffix,
            "cardinality_encoding": "PySAT EncType.seqcounter at-most-69",
            "cardinality_input_count": len(sides),
            "appended_counter_clauses": len(suffix_clauses),
            "added_auxiliary_variables": rebuilt.nv - base_header[0],
            "suffix_outer_inputs_are_exactly_84_sides": suffix_outer_inputs == set(sides),
            "suffix_contains_no_diagonal_input": not suffix_outer_inputs.intersection(diagonals),
            "suffix_contains_no_old_base_auxiliary": not suffix_old_aux,
            "maximum_variable_seen_in_suffix": max(suffix_variables),
            "conditioned_sha256": sha256(CONDITIONED),
            "header_hash_metadata_all_match": (
                meta.get("cnf_sha256") == sha256(CONDITIONED)
                and (meta.get("variables"), meta.get("clauses")) == conditioned_header
            ),
        },
        "separation_from_quarantined_e0": {
            "old_artifact_status": old_meta.get("status"),
            "old_cardinality_inputs": len(old_inputs),
            "old_inputs_equal_sides_union_diagonals": old_inputs == same,
            "corrected_inputs_equal_old_minus_diagonals": set(sides) == old_inputs - set(diagonals),
            "corrected_added_clauses": len(rebuilt.clauses),
            "quarantined_added_clauses": old_meta.get("added_clauses"),
            "corrected_added_variables": rebuilt.nv - base_header[0],
            "quarantined_added_variables": old_meta.get("added_variables"),
            "cnf_hashes_differ": sha256(CONDITIONED) != sha256(OLD_E0_CNF),
            "no_e0_bound_claim_in_corrected_metadata": "E0" not in json.dumps(meta),
        },
        "existing_portfolio_observation": {
            "exists": PORTFOLIO.exists(),
            "status": portfolio_status,
            "counts": portfolio_counts,
            "used_by_audit": False,
        },
        "artifacts": {
            str(TARGET_SOURCE): sha256(TARGET_SOURCE),
            str(BASE): sha256(BASE),
            str(BASE_META): sha256(BASE_META),
            str(CONDITIONED): sha256(CONDITIONED),
            str(BUILD_META): sha256(BUILD_META),
        },
        "claim_boundary": (
            "The CNF mechanically and exactly encodes at most 69 of the 84 side "
            "variables, not E0. Conditional nonexistence would additionally rely "
            "on the unreplayed external n3/P premises and an exhaustive UNSAT solve. "
            "No solve was run by this audit; the existing portfolio is UNKNOWN."
        ),
    }
    temporary = OUTPUT.with_name(OUTPUT.name + ".tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    temporary.replace(OUTPUT)
    print(json.dumps({
        "ok": document["ok"],
        "errors": len(errors),
        "warnings": len(warnings),
        "conditioned_header": conditioned_header,
        "added_clauses": len(suffix_clauses),
        "added_variables": rebuilt.nv - base_header[0],
        "output": str(OUTPUT),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
