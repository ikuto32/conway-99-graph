"""Direct exact-CNF lift of the dominant E72 source-row 134 fibre states.

The selected support graph is K4 on root groups 0,1,2,3.  Its six fibres all
have deficit two.  The independently enumerated 181 port-feasible labelled
fibre states are quotiented by the complete weighted residual action into five
orbits.  For each orbit representative this program fixes all 21 same-support
four-vertex fibre graphs (six exceptional states and fifteen ordinary C4s) as
complete assumptions.  A support-specific CNF is obtained from the genuinely
unrestricted ``scratch_general_exact.cnf`` by adding only macro facts common
to all five branches: ordinary C4/overlap consequences, twelve adjacent
exceptional block totals D=2, and three opposite exceptional block totals
D=0.  No overlap graph is enumerated locally.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

from scratch_general_exact_sat import CNF_PATH, coordinates, verify
from scratch_root_e73_q4_port_census import FIBRE_STATES


PORT = Path("scratch_general_e72_q3_port_feasible_states.json")
BASE_META = Path("scratch_general_exact_build.json")
MACRO_CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
MACRO_CNF = Path("scratch_root_e72_source134_macro.cnf")
BUILD = Path("scratch_root_e72_source134_state_build.json")
DEFAULT_OUTPUT = Path("scratch_root_e72_source134_state_c100000.json")
SOURCE_ROW_INDEX = 134
GROUPS = tuple(range(7))
SUPPORTS = tuple(itertools.combinations(GROUPS, 2))
BITS = tuple(itertools.product((0, 1), repeat=2))
PAIR_POSITIONS = tuple(itertools.combinations(range(4), 2))
SIDES = frozenset(
    pair for pair in PAIR_POSITIONS
    if sum(BITS[pair[0]][axis] != BITS[pair[1]][axis] for axis in (0, 1)) == 1
)
DIAGONALS = frozenset(set(PAIR_POSITIONS) - set(SIDES))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def cnf_audit(path: Path) -> dict:
    """Independently count a DIMACS file, including embedded unit clauses."""
    declared_variables = declared_clauses = None
    actual_clauses = unit_clauses = 0
    maximum_variable = 0
    with path.open("rb") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith(b"c"):
                continue
            if line.startswith(b"p"):
                fields = line.split()
                assert fields[:2] == [b"p", b"cnf"] and len(fields) == 4
                declared_variables, declared_clauses = map(int, fields[2:])
                continue
            literals = tuple(map(int, line.split()))
            assert literals and literals[-1] == 0 and 0 not in literals[:-1]
            actual_clauses += 1
            unit_clauses += len(literals) == 2
            if len(literals) > 1:
                maximum_variable = max(maximum_variable, max(map(abs, literals[:-1])))
    assert declared_variables is not None and declared_clauses is not None
    assert actual_clauses == declared_clauses
    assert maximum_variable <= declared_variables
    return {
        "declared_variables": declared_variables,
        "declared_clauses": declared_clauses,
        "actual_clauses": actual_clauses,
        "unit_clauses": unit_clauses,
        "maximum_variable_seen": maximum_variable,
    }


def local_label(support, bits):
    return tuple(sorted((2 * support[0] + bits[0], 2 * support[1] + bits[1])))


def selected_row() -> tuple[dict, bytes]:
    raw = PORT.read_bytes()
    document = json.loads(raw)
    matches = [
        row for row in document["rows"]
        if int(row.get("source_row_index", -1)) == SOURCE_ROW_INDEX
    ]
    assert len(matches) == 1
    row = matches[0]
    expected_supports = tuple(itertools.combinations(range(4), 2))
    supports = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
    deficits = tuple(int(item["deficit"]) for item in row["exceptional_supports"])
    assert supports == expected_supports
    assert deficits == (2,) * 6
    assert row["partition"] == [2] * 6
    assert row["compression_orbit_index"] == 1
    assert row["support_orbit_size"] == 35
    assert row["weighted_stabilizer_order"] == 144
    assert row["locally_port_feasible_assignments"] == 181
    assert len(row["feasible_state_indices"]) == 181
    return row, raw


def state_internal_edges(supports, state_indices):
    edges = set()
    for support, state_index in zip(supports, state_indices):
        vertices = tuple(local_label(support, bits) for bits in BITS)
        state = FIBRE_STATES[2][state_index]
        assert len(state["edges"]) == 2
        for left, right in state["edges"]:
            edges.add(tuple(sorted((vertices[left], vertices[right]))))
    assert len(edges) == 12
    return frozenset(edges)


def state_q(state_indices):
    return sum(
        tuple(edge) in DIAGONALS
        for state_index in state_indices
        for edge in FIBRE_STATES[2][state_index]["edges"]
    )


def state_orbits(row: dict) -> tuple[tuple[dict, ...], dict]:
    supports = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
    vertices = tuple(sorted(
        local_label(support, bits) for support in supports for bits in BITS
    ))
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    pair_positions = tuple(itertools.combinations(range(len(vertices)), 2))
    pair_index = {pair: bit for bit, pair in enumerate(pair_positions)}

    def mask_of(edges):
        mask = 0
        for left, right in edges:
            pair = tuple(sorted((vertex_index[left], vertex_index[right])))
            mask |= 1 << pair_index[pair]
        return mask

    preserving = []
    exceptional = frozenset(supports)
    for permutation in itertools.permutations(GROUPS):
        image = frozenset(
            tuple(sorted((permutation[left], permutation[right])))
            for left, right in supports
        )
        if image == exceptional:
            preserving.append(permutation)
    assert len(preserving) == row["weighted_stabilizer_order"] == 144
    used = tuple(sorted(set().union(*map(set, supports))))
    actions = set()
    for permutation in preserving:
        for flip_bits in itertools.product((0, 1), repeat=len(used)):
            flips = dict(zip(used, flip_bits))
            action = []
            for vertex in vertices:
                image = tuple(sorted(
                    2 * permutation[symbol // 2]
                    + ((symbol % 2) ^ flips.get(symbol // 2, 0))
                    for symbol in vertex
                ))
                action.append(vertex_index[image])
            actions.add(tuple(action))
    actions = tuple(sorted(actions))
    assert len(actions) == 384

    action_pair_maps = tuple(
        tuple(pair_index[tuple(sorted((action[left], action[right])))]
              for left, right in pair_positions)
        for action in actions
    )

    def transform(mask, pair_map):
        answer = 0
        work = mask
        while work:
            low = work & -work
            answer |= 1 << pair_map[low.bit_length() - 1]
            work ^= low
        return answer

    assignments = tuple(tuple(map(int, state)) for state in row["feasible_state_indices"])
    masks = tuple(mask_of(state_internal_edges(supports, state)) for state in assignments)
    assert len(set(masks)) == len(masks) == 181
    assignment_by_mask = dict(zip(masks, assignments))
    feasible = set(masks)
    remaining = set(masks)
    result = []
    closure_union = set()
    while remaining:
        representative_mask = min(remaining)
        orbit = {transform(representative_mask, pair_map) for pair_map in action_pair_maps}
        assert orbit <= feasible
        assert not (closure_union & orbit)
        stabilizer_size = sum(
            transform(representative_mask, pair_map) == representative_mask
            for pair_map in action_pair_maps
        )
        assert len(actions) == len(orbit) * stabilizer_size
        q_values = {state_q(assignment_by_mask[mask]) for mask in orbit}
        assert len(q_values) == 1
        state = assignment_by_mask[representative_mask]
        result.append({
            "branch_index": len(result),
            "state_indices": list(state),
            "internal_mask_hex": hex(representative_mask),
            "state_orbit_size": len(orbit),
            "state_stabilizer_size": stabilizer_size,
            "Q": next(iter(q_values)),
        })
        closure_union.update(orbit)
        remaining.difference_update(orbit)
    assert closure_union == feasible
    assert len(result) == 5
    assert sorted(item["state_orbit_size"] for item in result) == [1, 4, 32, 48, 96]
    assert sum(item["state_orbit_size"] for item in result) == 181
    weighted_q = Counter()
    for item in result:
        weighted_q[item["Q"]] += item["state_orbit_size"]
    assert weighted_q == Counter({4: 144, 6: 36, 12: 1})
    audit = {
        "feasible_labelled_states": len(assignments),
        "effective_residual_actions": len(actions),
        "state_orbits": len(result),
        "state_orbit_size_histogram": {
            str(size): count
            for size, count in sorted(Counter(item["state_orbit_size"] for item in result).items())
        },
        "weighted_Q_histogram": {
            str(q): count for q, count in sorted(weighted_q.items())
        },
        "all_orbits_closed_in_feasible_state_set": True,
        "orbits_pairwise_disjoint_and_cover_all_states": True,
        "orbit_stabilizer_identity_verified": True,
        "Q_invariant_on_every_orbit": True,
    }
    return tuple(result), audit


def all_internal_assumptions(row: dict, branch: dict) -> tuple[int, ...]:
    labels, index, _variables, edge = coordinates()
    del labels
    exceptional_supports = tuple(
        tuple(item["support"]) for item in row["exceptional_supports"]
    )
    state_by_support = dict(zip(exceptional_supports, branch["state_indices"]))
    units = []
    positive = 0
    for support in SUPPORTS:
        fibre = tuple(index[local_label(support, bits)] for bits in BITS)
        if support in state_by_support:
            chosen = {
                tuple(sorted(pair))
                for pair in FIBRE_STATES[2][state_by_support[support]]["edges"]
            }
        else:
            chosen = set(SIDES)
        for left, right in PAIR_POSITIONS:
            variable = edge(fibre[left], fibre[right])
            if (left, right) in chosen:
                units.append(variable)
                positive += 1
            else:
                units.append(-variable)
    assert len(units) == 21 * 6 == 126
    assert len({abs(unit) for unit in units}) == len(units)
    assert positive == 15 * 4 + 6 * 2 == 72
    return tuple(units)


def exactly_two_clauses(literals) -> list[list[int]]:
    """A transparent no-auxiliary encoding of exactly two true literals."""
    literals = tuple(literals)
    assert len(literals) == 16 and len(set(literals)) == 16
    # At least two: for every possible sole true literal, the other 15 must
    # contain a true literal.  These 16 clauses also exclude the all-zero row.
    clauses = [
        [literal for index, literal in enumerate(literals) if index != omitted]
        for omitted in range(len(literals))
    ]
    # At most two: no triple can be simultaneously true.
    clauses.extend(
        [-left, -middle, -right]
        for left, middle, right in itertools.combinations(literals, 3)
    )
    assert len(clauses) == 16 + math.comb(16, 3) == 576
    return clauses


def macro_common_clauses(row: dict, branches: tuple[dict, ...]) -> tuple[list[list[int]], dict]:
    """Build the fixed support/Gram layer shared by all five state branches."""
    _labels, index, _variables, edge = coordinates()
    exceptional_supports = tuple(
        tuple(item["support"]) for item in row["exceptional_supports"]
    )
    exceptional = frozenset(exceptional_supports)
    ordinary = frozenset(set(SUPPORTS) - set(exceptional_supports))
    fibres = {
        support: tuple(index[local_label(support, bits)] for bits in BITS)
        for support in SUPPORTS
    }

    clauses: list[list[int]] = []
    ordinary_internal_units = []
    for support in sorted(ordinary):
        fibre = fibres[support]
        for left, right in PAIR_POSITIONS:
            variable = edge(fibre[left], fibre[right])
            literal = variable if (left, right) in SIDES else -variable
            clauses.append([literal])
            ordinary_internal_units.append(literal)
    assert len(ordinary_internal_units) == 15 * 6 == 90
    assert sum(value > 0 for value in ordinary_internal_units) == 15 * 4 == 60

    # This is the exact ordinary-C4 overlap consequence used as a constant in
    # build_shared_cnf: a singly-overlapping block incident with an ordinary
    # fibre is entirely zero.
    ordinary_overlap_pairs = []
    ordinary_overlap_variables = []
    for left, right in itertools.combinations(SUPPORTS, 2):
        if not (set(left) & set(right)):
            continue
        if left in exceptional and right in exceptional:
            continue
        variables = tuple(
            edge(u, v) for u in fibres[left] for v in fibres[right]
        )
        assert len(variables) == len(set(variables)) == 16
        clauses.extend([[-variable] for variable in variables])
        ordinary_overlap_pairs.append((left, right))
        ordinary_overlap_variables.extend(variables)
    assert len(ordinary_overlap_pairs) == 93
    assert len(ordinary_overlap_variables) == 93 * 16 == 1488
    assert len(set(ordinary_overlap_variables)) == len(ordinary_overlap_variables)

    adjacent_rows = []
    opposite_rows = []
    exceptional_block_variables = set()
    for left_index, right_index in itertools.combinations(range(6), 2):
        left = exceptional_supports[left_index]
        right = exceptional_supports[right_index]
        variables = tuple(
            edge(u, v) for u in fibres[left] for v in fibres[right]
        )
        assert len(variables) == len(set(variables)) == 16
        assert not (exceptional_block_variables & set(variables))
        exceptional_block_variables.update(variables)
        if set(left) & set(right):
            clauses.extend(exactly_two_clauses(variables))
            adjacent_rows.append([left_index, right_index, 2])
        else:
            clauses.extend([[-variable] for variable in variables])
            opposite_rows.append([left_index, right_index, 0])
    assert len(adjacent_rows) == 12
    assert len(opposite_rows) == 3
    assert len(exceptional_block_variables) == 15 * 16

    # Bind the five independently reconstructed state orbits to the complete
    # Gram macro catalog.  For this K4 row there is exactly one D signature per
    # state orbit, and all twelve catalogued overlap totals equal two.
    catalog_raw = MACRO_CATALOG.read_bytes()
    catalog = json.loads(catalog_raw)
    entries = [
        item for item in catalog["macro_entries"]
        if int(item["source_row_index"]) == SOURCE_ROW_INDEX
    ]
    assert len(entries) == 5
    entry_by_state = {tuple(item["state_indices"]): item for item in entries}
    assert len(entry_by_state) == 5
    assert set(entry_by_state) == {tuple(item["state_indices"]) for item in branches}
    for branch in branches:
        entry = entry_by_state[tuple(branch["state_indices"])]
        assert entry["state_orbit_size"] == branch["state_orbit_size"]
        assert entry["state_stabilizer_order"] == branch["state_stabilizer_size"]
        assert entry["Q"] == branch["Q"]
        assert entry["overlap_block_totals"] == adjacent_rows
        assert entry["signature_stabilizer_canonical"] is True
        assert entry["signature_stabilizer_orbit_size"] == 1
    matching_coverage = sum(
        int(item["labelled_state_matching_coverage"]) for item in entries
    )
    assert matching_coverage == 101593088

    expected_clause_count = 90 + 93 * 16 + 12 * 576 + 3 * 16
    assert len(clauses) == expected_clause_count == 8538
    unit_literals = [clause[0] for clause in clauses if len(clause) == 1]
    assert len(unit_literals) == 90 + 93 * 16 + 3 * 16 == 1626
    assert len({abs(value) for value in unit_literals}) == len(unit_literals)
    return clauses, {
        "macro_catalog": str(MACRO_CATALOG),
        "macro_catalog_sha256": hashlib.sha256(catalog_raw).hexdigest().upper(),
        "catalog_entries_for_source_row": len(entries),
        "catalog_state_orbits_bound_exactly": True,
        "catalog_exact_overlap_completion_coverage": matching_coverage,
        "ordinary_c4_fibres": len(ordinary),
        "ordinary_internal_unit_clauses": len(ordinary_internal_units),
        "ordinary_overlap_zero_blocks": len(ordinary_overlap_pairs),
        "ordinary_overlap_zero_unit_clauses": len(ordinary_overlap_variables),
        "adjacent_exceptional_D2_blocks": len(adjacent_rows),
        "adjacent_exceptional_D2_rows": adjacent_rows,
        "adjacent_exceptional_D2_encoding": (
            "16 at-least-two length-15 clauses plus C(16,3)=560 at-most-two clauses"
        ),
        "opposite_exceptional_D0_blocks": len(opposite_rows),
        "opposite_exceptional_D0_rows": opposite_rows,
        "macro_unit_clauses": len(unit_literals),
        "macro_clauses": len(clauses),
        "macro_new_variables": 0,
        "overlap_graphs_enumerated": 0,
    }


def write_macro_cnf(base_audit: dict, clauses: list[list[int]]) -> dict:
    """Append the audited macro layer while preserving all base clauses."""
    expected_variables = base_audit["declared_variables"]
    expected_clauses = base_audit["declared_clauses"] + len(clauses)
    temporary = MACRO_CNF.with_suffix(MACRO_CNF.suffix + f".{os.getpid()}.tmp")
    with CNF_PATH.open("rb") as source, temporary.open("wb") as target:
        old_header = source.readline().split()
        assert old_header == [
            b"p", b"cnf", str(expected_variables).encode("ascii"),
            str(base_audit["declared_clauses"]).encode("ascii"),
        ]
        target.write(f"p cnf {expected_variables} {expected_clauses}\n".encode("ascii"))
        shutil.copyfileobj(source, target, length=1 << 20)
        for clause in clauses:
            target.write((" ".join(map(str, clause)) + " 0\n").encode("ascii"))
    temporary.replace(MACRO_CNF)
    audit = cnf_audit(MACRO_CNF)
    assert audit["declared_variables"] == expected_variables
    assert audit["declared_clauses"] == expected_clauses
    assert audit["unit_clauses"] == len(
        [clause for clause in clauses if len(clause) == 1]
    )
    audit["sha256"] = sha256(MACRO_CNF)
    return audit


def build() -> dict:
    row, port_raw = selected_row()
    branches, orbit_audit = state_orbits(row)
    base_meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    base_audit = cnf_audit(CNF_PATH)
    assert sha256(CNF_PATH) == base_meta["cnf_sha256"]
    assert base_audit["declared_variables"] == base_meta["variables"]
    assert base_audit["declared_clauses"] == base_meta["clauses"]
    # The five historical fixed-edge branches are metadata used by the old
    # portfolio runner, not clauses embedded in the base formula.  This is the
    # critical safety check: none is combined with the K4 normalization.
    assert base_meta["branch_units"]
    assert base_audit["unit_clauses"] == 0

    macro_clauses, macro_audit = macro_common_clauses(row, branches)
    macro_cnf_audit = write_macro_cnf(base_audit, macro_clauses)
    completed = []
    for raw in branches:
        branch = dict(raw)
        assumptions = all_internal_assumptions(row, branch)
        word = " ".join(map(str, assumptions)).encode("ascii")
        branch.update({
            "assumption_count": len(assumptions),
            "positive_assumptions": sum(value > 0 for value in assumptions),
            "negative_assumptions": sum(value < 0 for value in assumptions),
            "assumption_sha256": hashlib.sha256(word).hexdigest().upper(),
            "assumptions": list(assumptions),
        })
        completed.append(branch)
    result = {
        "status": "BUILD_COMPLETE",
        "model": "direct full exact-CNF lift of E72 source row 134 state orbits",
        "source": str(PORT),
        "source_sha256": hashlib.sha256(port_raw).hexdigest().upper(),
        "source_row_index": SOURCE_ROW_INDEX,
        "normalized_positive_row_index": next(
            index for index, candidate in enumerate(json.loads(port_raw)["rows"])
            if candidate.get("source_row_index") == SOURCE_ROW_INDEX
        ),
        "compression_orbit_index": row["compression_orbit_index"],
        "support_orbit_size": row["support_orbit_size"],
        "exceptional_supports": [item["support"] for item in row["exceptional_supports"]],
        "deficits": [item["deficit"] for item in row["exceptional_supports"]],
        "ordinary_c4_fibres": 15,
        "unrestricted_base_cnf": str(CNF_PATH),
        "unrestricted_base_cnf_sha256": sha256(CNF_PATH),
        "unrestricted_base_cnf_audit": base_audit,
        "historical_portfolio_branch_units_present_only_in_metadata": True,
        "historical_portfolio_branch_units_applied": False,
        "macro_cnf": str(MACRO_CNF),
        "macro_cnf_sha256": macro_cnf_audit["sha256"],
        "macro_cnf_audit": macro_cnf_audit,
        "macro_layer_audit": macro_audit,
        "base_cnf_variables": base_meta["variables"],
        "base_cnf_clauses": macro_cnf_audit["declared_clauses"],
        "assumptions_per_branch": 126,
        "ordinary_internal_assumptions_duplicated_by_fixed_macro_units": 90,
        "exceptional_internal_assumptions_per_branch": 36,
        "state_orbit_audit": orbit_audit,
        "branches": completed,
        "coverage": (
            "All 181 port-feasible labelled internal states on the normalized K4 "
            "support representative, covered by five exact residual-symmetry orbits; "
            "the unique Gram block-total signature covers 101,593,088 labelled "
            "state/matching completions without enumerating them."
        ),
        "selector_ready": True,
        "claim_boundary": (
            "Only the E72 source-row 134 support orbit and its Gram-forced macro "
            "signature are covered. Solver-terminal UNSAT is computational unless "
            "a separately checked proof is emitted."
        ),
    }
    atomic_json(BUILD, result)
    return result


def stats_delta(before, after):
    return {
        key: int(after.get(key, 0)) - int(before.get(key, 0))
        for key in sorted(set(before) | set(after))
    }


def solve(conflicts: int, output: Path) -> dict:
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.formula import CNF
    from pysat.solvers import Solver

    build_doc = build()
    started = time.monotonic()
    formula = CNF(from_file=str(MACRO_CNF))
    loaded = time.monotonic()
    solver = Solver(name="cadical195", bootstrap_with=formula.clauses)
    solver_loaded = time.monotonic()
    records = []
    verified_solution = None
    try:
        for branch in build_doc["branches"]:
            assumptions = tuple(branch["assumptions"])
            assumption_set = frozenset(assumptions)
            covers = [
                prior for prior in records
                if prior.get("assumption_core")
                and frozenset(prior["assumption_core"]) <= assumption_set
            ]
            record = {
                key: value for key, value in branch.items() if key != "assumptions"
            }
            branch_started = time.monotonic()
            if covers:
                cover = min(covers, key=lambda row: len(row["assumption_core"]))
                core = tuple(cover["assumption_core"])
                record.update({
                    "status": "COVERED_UNSAT",
                    "logical_status": "UNSAT",
                    "resolution": "ASSUMPTION_CORE_CONTAINMENT",
                    "solve_seconds": round(time.monotonic() - branch_started, 6),
                    "assumption_core_size": len(core),
                    "assumption_core": list(core),
                    "covered_by_branch_index": cover["branch_index"],
                    "formal_proof_certificate": None,
                })
            else:
                before = solver.accum_stats()
                if conflicts:
                    solver.conf_budget(conflicts)
                    answer = solver.solve_limited(
                        assumptions=list(assumptions), expect_interrupt=True
                    )
                else:
                    answer = solver.solve(assumptions=list(assumptions))
                after = solver.accum_stats()
                status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
                record.update({
                    "status": status,
                    "logical_status": status,
                    "resolution": "CADICAL",
                    "solve_seconds": round(time.monotonic() - branch_started, 6),
                    "incremental_stats_delta": stats_delta(before, after),
                    "incremental_stats_cumulative": after,
                    "formal_proof_certificate": None,
                })
                if answer is False:
                    core = tuple(solver.get_core() or ())
                    assert core and len(core) == len(set(core)) and set(core) <= assumption_set
                    record["assumption_core_size"] = len(core)
                    record["assumption_core"] = list(core)
                elif answer is True:
                    model = solver.get_model()
                    positive = {literal for literal in model if 0 < literal <= 3486}
                    checked = verify(positive)
                    record["direct_99_vertex_verification"] = {
                        key: value for key, value in checked.items() if key != "edges"
                    }
                    record["positive_edge_variables"] = sorted(positive)
                    assert checked["ok"], "SAT model failed direct 99-vertex verification"
                    verified_solution = checked
            records.append(record)
            partial = make_result(
                build_doc, records, conflicts, started, loaded, solver_loaded,
                verified_solution,
            )
            atomic_json(output, partial)
            print(json.dumps({
                "branch_index": record["branch_index"],
                "state_orbit_size": record["state_orbit_size"],
                "Q": record["Q"],
                "status": record["status"],
                "solve_seconds": record["solve_seconds"],
                "core_size": record.get("assumption_core_size"),
            }), flush=True)
            if verified_solution is not None:
                solution_path = Path("scratch_root_e72_source134_verified_solution.json")
                atomic_json(solution_path, verified_solution)
                break
    finally:
        solver.delete()
    result = make_result(
        build_doc, records, conflicts, started, loaded, solver_loaded,
        verified_solution,
    )
    atomic_json(output, result)
    return result


def make_result(build_doc, records, conflicts, started, loaded, solver_loaded,
                verified_solution):
    complete = len(records) == len(build_doc["branches"]) or verified_solution is not None
    status = (
        "SAT" if verified_solution is not None
        else "UNSAT" if len(records) == len(build_doc["branches"])
        and all(row["logical_status"] == "UNSAT" for row in records)
        else "UNKNOWN" if complete else "IN_PROGRESS"
    )
    return {
        "status": status,
        "model": build_doc["model"],
        "solver": "CaDiCaL 1.9.5 via PySAT assumptions",
        "build": str(BUILD),
        "build_sha256": sha256(BUILD),
        "cnf": str(MACRO_CNF),
        "cnf_sha256": build_doc["macro_cnf_sha256"],
        "unrestricted_base_cnf": str(CNF_PATH),
        "unrestricted_base_cnf_sha256": build_doc["unrestricted_base_cnf_sha256"],
        "source_row_index": SOURCE_ROW_INDEX,
        "conflict_budget_per_direct_branch": conflicts or None,
        "cnf_parse_seconds": round(loaded - started, 6),
        "solver_load_seconds": round(solver_loaded - loaded, 6),
        "checkpoint_complete": complete,
        "completed_branches": len(records),
        "state_orbits": len(build_doc["branches"]),
        "labelled_states_covered": sum(
            row["state_orbit_size"] for row in records
            if row["logical_status"] in ("UNSAT", "SAT")
        ),
        "direct_unsat": sum(row["status"] == "UNSAT" for row in records),
        "core_covered_unsat": sum(row["status"] == "COVERED_UNSAT" for row in records),
        "unknown": sum(row["status"] == "UNKNOWN" for row in records),
        "sat": sum(row["status"] == "SAT" for row in records),
        "records": records,
        "verified_99_vertex_solution": verified_solution is not None,
        "claim_boundary": (
            "The unrestricted rooted CNF, support-specific ordinary consequences, "
            "Gram-forced D=2/D=0 block totals, and all 126 internal-edge assumptions "
            "are exact for source row 134. CaDiCaL UNSAT results remain computational "
            "until a proof is emitted and independently checked."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--conflicts", type=int, default=100000)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.solve:
        result = solve(args.conflicts, args.output)
        print(json.dumps({
            "status": result["status"],
            "state_orbits": result["state_orbits"],
            "direct_unsat": result["direct_unsat"],
            "covered_unsat": result["core_covered_unsat"],
            "unknown": result["unknown"],
            "sat": result["sat"],
            "labelled_states_covered": result["labelled_states_covered"],
        }, sort_keys=True), flush=True)
    elif args.build:
        result = build()
        print(json.dumps({
            "status": result["status"],
            **result["state_orbit_audit"],
            "assumptions_per_branch": result["assumptions_per_branch"],
        }, sort_keys=True), flush=True)
    else:
        parser.error("choose --build or --solve")


if __name__ == "__main__":
    main()
