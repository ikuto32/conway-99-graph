"""Exact search for an srg(99,14,1,2) with a semiregular C11 action.

Vertices are ``(fibre, coordinate)`` in ``{0,...,8} x Z/11Z`` and the
putative automorphism adds one to every coordinate.  There are only 441 edge
orbits.  For one representative of every unordered vertex-pair orbit, the
SRG common-neighbour condition is encoded as

    number_of_common_neighbours + adjacency = 2.

The model is exact inside this automorphism class.  Any SAT result is expanded
to all 99 vertices and checked directly before ``submission.txt`` is written.
An UNSAT result excludes only the semiregular-order-11 subclass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path


N_FIBRES = 9
MODULUS = 11
N = N_FIBRES * MODULUS
CNF_PATH = Path("scratch_root_c11_semiregular.cnf")
META_PATH = Path("scratch_root_c11_semiregular_build.json")
RESULT_PATH = Path("scratch_root_c11_semiregular_result.json")
SOLUTION_PATH = Path("scratch_root_c11_semiregular_solution.json")
NORMALIZED_CNF_PATH = Path("scratch_root_c11_semiregular_normalized.cnf")
NORMALIZED_META_PATH = Path("scratch_root_c11_semiregular_normalized_build.json")
NORMALIZED_RESULT_PATH = Path("scratch_root_c11_semiregular_normalized_result.json")


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def vertex(fibre: int, coordinate: int) -> int:
    return MODULUS * fibre + coordinate % MODULUS


def split_vertex(value: int) -> tuple[int, int]:
    return divmod(value, MODULUS)


def edge_keys() -> tuple[tuple, ...]:
    keys = []
    for left in range(N_FIBRES):
        for difference in range(1, (MODULUS + 1) // 2):
            keys.append((left, left, difference))
        for right in range(left + 1, N_FIBRES):
            for difference in range(MODULUS):
                keys.append((left, right, difference))
    assert len(keys) == N_FIBRES * 5 + (N_FIBRES * 8 // 2) * MODULUS == 441
    return tuple(keys)


EDGE_KEYS = edge_keys()
EDGE_VARIABLE = {key: index + 1 for index, key in enumerate(EDGE_KEYS)}


def canonical_edge_key(left: int, right: int) -> tuple | None:
    """Return the C11 edge-orbit key for two numbered vertices."""

    if left == right:
        return None
    left_fibre, left_coordinate = split_vertex(left)
    right_fibre, right_coordinate = split_vertex(right)
    if left_fibre == right_fibre:
        difference = (right_coordinate - left_coordinate) % MODULUS
        difference = min(difference, MODULUS - difference)
        assert 1 <= difference <= 5
        return left_fibre, left_fibre, difference
    if left_fibre < right_fibre:
        return left_fibre, right_fibre, (right_coordinate - left_coordinate) % MODULUS
    return right_fibre, left_fibre, (left_coordinate - right_coordinate) % MODULUS


def edge_literal(left: int, right: int) -> int:
    key = canonical_edge_key(left, right)
    assert key is not None
    return EDGE_VARIABLE[key]


def pair_representatives() -> tuple[tuple[int, int], ...]:
    pairs = []
    for left_fibre in range(N_FIBRES):
        left = vertex(left_fibre, 0)
        for difference in range(1, 6):
            pairs.append((left, vertex(left_fibre, difference)))
        for right_fibre in range(left_fibre + 1, N_FIBRES):
            for difference in range(MODULUS):
                pairs.append((left, vertex(right_fibre, difference)))
    assert len(pairs) == 441
    assert len({canonical_edge_key(*pair) for pair in pairs}) == 441
    return tuple(pairs)


PAIR_REPRESENTATIVES = pair_representatives()


def integer_partitions_fixed_length(
    total: int, length: int, maximum: int
) -> tuple[tuple[int, ...], ...]:
    """Nonincreasing length-``length`` partitions, padded by zeroes."""

    answer = []

    def visit(prefix: tuple[int, ...], remaining: int, ceiling: int) -> None:
        slots = length - len(prefix)
        if not slots:
            if remaining == 0:
                answer.append(prefix)
            return
        high = min(ceiling, maximum, remaining)
        low = max(0, remaining - maximum * (slots - 1))
        for value in range(high, low - 1, -1):
            visit(prefix + (value,), remaining - value, value)

    visit((), total, maximum)
    return tuple(answer)


def internal_pattern_orbits(size: int) -> tuple[tuple[int, ...], ...]:
    """Canonical subsets of the five signed differences under Z11 units."""

    import itertools

    def image(pattern: tuple[int, ...], unit: int) -> tuple[int, ...]:
        values = []
        for difference in pattern:
            mapped = unit * difference % MODULUS
            values.append(min(mapped, MODULUS - mapped))
        return tuple(sorted(values))

    remaining = set(itertools.combinations(range(1, 6), size))
    representatives = []
    while remaining:
        seed = min(remaining)
        orbit = {image(seed, unit) for unit in range(1, MODULUS)}
        assert all(len(value) == size for value in orbit)
        assert orbit <= set(itertools.combinations(range(1, 6), size))
        representative = min(orbit)
        representatives.append(representative)
        remaining.difference_update(orbit)
    return tuple(sorted(representatives))


def normalized_branch_specs() -> tuple[dict, ...]:
    """Complete WLOG cases for the quotient row at fibre zero.

    The other eight C11 orbits may be sorted by their number of neighbours of
    ``(0,0)``.  Every nonempty cross-neighbour set can then be shifted so that
    difference zero is present.  Finally, replacing the C11 generator by a
    nonzero power acts transitively through the signed-difference rotations,
    allowing the internal difference set to be chosen canonically.
    """

    specs = []
    # Fourier inversion below forces five internal signed differences in
    # total, so at least one vertex orbit contains one.  Choose that orbit as
    # fibre zero.  It need not be the unique or maximum such orbit.
    for internal_count in range(1, 6):
        cross_total = 14 - 2 * internal_count
        if cross_total < 0:
            continue
        partitions = tuple(
            cross_counts
            for cross_counts in integer_partitions_fixed_length(
                cross_total, 8, MODULUS
            )
            # The diagonal entry of B^2+B=12I+22J for the symmetric
            # equitable quotient B, where B_00=2*internal_count.
            if 4 * internal_count * internal_count
            + 2 * internal_count
            + sum(value * value for value in cross_counts)
            == 34
        )
        for internal_pattern in internal_pattern_orbits(internal_count):
            for cross_counts in partitions:
                specs.append({
                    "internal_pattern": list(internal_pattern),
                    "cross_counts": list(cross_counts),
                })
    assert len({
        (tuple(spec["internal_pattern"]), tuple(spec["cross_counts"]))
        for spec in specs
    }) == len(specs)
    return tuple(specs)


def build() -> dict:
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF, IDPool

    started = time.monotonic()
    formula = CNF()
    pool = IDPool(start_from=len(EDGE_KEYS) + 1)
    degree_occurrences = 0
    product_occurrences = 0

    # Use distinct occurrence variables instead of repeated weighted literals.
    # This makes every cardinality encoder invocation a plain set of variables.
    for fibre in range(N_FIBRES):
        root = vertex(fibre, 0)
        degree_terms = []
        for neighbour in range(N):
            if neighbour == root:
                continue
            edge = edge_literal(root, neighbour)
            occurrence = pool.id(("degree", fibre, neighbour))
            formula.append([-occurrence, edge])
            formula.append([occurrence, -edge])
            degree_terms.append(occurrence)
            degree_occurrences += 1
        assert len(degree_terms) == N - 1
        formula.extend(
            CardEnc.equals(
                degree_terms,
                bound=14,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
        )

    for pair_number, (left, right) in enumerate(PAIR_REPRESENTATIVES):
        common_terms = []
        for witness in range(N):
            if witness in (left, right):
                continue
            first = edge_literal(left, witness)
            second = edge_literal(right, witness)
            product = pool.id(("product", pair_number, witness))
            formula.append([-product, first])
            formula.append([-product, second])
            formula.append([product, -first, -second])
            common_terms.append(product)
            product_occurrences += 1
        assert len(common_terms) == N - 2
        # Adjacent pairs need one common neighbour and nonadjacent pairs two.
        # Hence common_count + edge_indicator is always exactly two.
        formula.extend(
            CardEnc.equals(
                common_terms + [edge_literal(left, right)],
                bound=2,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
        )

    temporary = CNF_PATH.with_suffix(CNF_PATH.suffix + f".{os.getpid()}.tmp")
    formula.to_file(str(temporary))
    temporary.replace(CNF_PATH)
    result = {
        "status": "BUILT",
        "model": "exact SRG(99,14,1,2) with a semiregular C11 automorphism",
        "vertex_coordinates": "{0,...,8} x Z/11Z",
        "edge_orbit_variables": len(EDGE_KEYS),
        "unordered_pair_orbits": len(PAIR_REPRESENTATIVES),
        "degree_occurrence_helpers": degree_occurrences,
        "common_neighbour_product_helpers": product_occurrences,
        "variables": formula.nv,
        "clauses": len(formula.clauses),
        "cnf": str(CNF_PATH),
        "cnf_sha256": sha256(CNF_PATH),
        "build_seconds": round(time.monotonic() - started, 6),
        "claim_boundary": (
            "Exact only for graphs admitting a fixed-point-free automorphism "
            "of order 11 whose nine cycles all have length 11."
        ),
    }
    atomic_json(META_PATH, result)
    return result


def build_normalized() -> dict:
    """Add exact, selector-gated WLOG quotient-row normalizations."""

    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF, IDPool

    started = time.monotonic()
    base_meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    assert base_meta["status"] == "BUILT"
    assert sha256(CNF_PATH) == base_meta["cnf_sha256"]
    formula = CNF(from_file=str(CNF_PATH))
    assert formula.nv == base_meta["variables"]
    pool = IDPool(start_from=formula.nv + 1)

    # The invariant (character-zero) quotient contains 14 once and, by
    # Galois conjugacy of the ten nontrivial C11 character blocks, exactly
    # four copies each of 3 and -4.  Hence its trace is 10.  More strongly,
    # every nontrivial block has trace -1.  Fourier inversion then says that
    # each of the five signed nonzero differences occurs internally in
    # exactly one of the nine vertex orbits.
    for difference in range(1, 6):
        formula.extend(
            CardEnc.equals(
                [EDGE_VARIABLE[(fibre, fibre, difference)]
                 for fibre in range(N_FIBRES)],
                bound=1,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
        )
    specs = normalized_branch_specs()
    selectors = []

    for branch_index, spec in enumerate(specs):
        selector = pool.id(("branch", branch_index))
        selectors.append(selector)
        selected_internal = set(spec["internal_pattern"])
        # Fix the complete within-orbit difference set for fibre zero.
        for difference in range(1, 6):
            edge = EDGE_VARIABLE[(0, 0, difference)]
            formula.append([-selector, edge if difference in selected_internal else -edge])
        for right_fibre, count in enumerate(spec["cross_counts"], start=1):
            block = [
                EDGE_VARIABLE[(0, right_fibre, difference)]
                for difference in range(MODULUS)
            ]
            conditional = CardEnc.equals(
                block,
                bound=count,
                vpool=pool,
                encoding=EncType.seqcounter,
            )
            for clause in conditional.clauses:
                formula.append([-selector] + clause)
            if count:
                # Independent coordinate shifts on each C11 orbit preserve the
                # simultaneous translation and move a chosen edge to d=0.
                formula.append([-selector, EDGE_VARIABLE[(0, right_fibre, 0)]])

    formula.extend(
        CardEnc.equals(
            selectors,
            bound=1,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    temporary = NORMALIZED_CNF_PATH.with_suffix(
        NORMALIZED_CNF_PATH.suffix + f".{os.getpid()}.tmp"
    )
    formula.to_file(str(temporary))
    temporary.replace(NORMALIZED_CNF_PATH)
    by_internal_count = {}
    for spec in specs:
        key = str(len(spec["internal_pattern"]))
        by_internal_count[key] = by_internal_count.get(key, 0) + 1
    result = {
        "status": "BUILT",
        "model": "C11-semiregular exact CNF with complete quotient-row WLOG",
        "input": str(CNF_PATH),
        "input_sha256": base_meta["cnf_sha256"],
        "normalization": [
            "permute the nine C11 vertex orbits and choose one containing an internal edge as fibre zero",
            "sort the other fibres by their cross-neighbour counts",
            "shift every directly adjacent fibre so difference zero is an edge",
            "replace the C11 generator by a unit power and canonicalize the signed internal differences",
        ],
        "C11_character_consequences": {
            "invariant_quotient_spectrum": "14^1,3^4,(-4)^4",
            "invariant_quotient_trace": 10,
            "each_nontrivial_character_spectrum": "3^5,(-4)^4",
            "each_nontrivial_character_trace": -1,
            "Fourier_inversion": (
                "for each signed difference d=1,...,5, exactly one of the "
                "nine internal circulants contains +/-d"
            ),
        },
        "quotient_row_consequence": (
            "with t internal signed differences and sorted cross counts c_j, "
            "4*t^2+2*t+sum(c_j^2)=34, the diagonal entry of "
            "B^2+B=12I+22J"
        ),
        "branch_count": len(specs),
        "branches_by_internal_edge_orbits": by_internal_count,
        "branches": [
            {"branch_index": index, "selector": selectors[index], **spec}
            for index, spec in enumerate(specs)
        ],
        "variables": formula.nv,
        "clauses": len(formula.clauses),
        "cnf": str(NORMALIZED_CNF_PATH),
        "cnf_sha256": sha256(NORMALIZED_CNF_PATH),
        "build_seconds": round(time.monotonic() - started, 6),
        "claim_boundary": base_meta["claim_boundary"],
    }
    atomic_json(NORMALIZED_META_PATH, result)
    return result


def expanded_edges(positive: set[int]) -> list[tuple[int, int]]:
    edges = []
    for left in range(N):
        for right in range(left + 1, N):
            if edge_literal(left, right) in positive:
                edges.append((left + 1, right + 1))
    return edges


def verify(edges: list[tuple[int, int]]) -> dict:
    adjacency = [set() for _ in range(N)]
    for left, right in edges:
        assert 1 <= left < right <= N
        adjacency[left - 1].add(right - 1)
        adjacency[right - 1].add(left - 1)
    degrees = [len(row) for row in adjacency]
    common_histogram: dict[str, int] = {}
    bad_pairs = []
    for left in range(N):
        for right in range(left + 1, N):
            common = len(adjacency[left] & adjacency[right])
            expected = 1 if right in adjacency[left] else 2
            key = f"edge={int(right in adjacency[left])},common={common}"
            common_histogram[key] = common_histogram.get(key, 0) + 1
            if common != expected and len(bad_pairs) < 25:
                bad_pairs.append([left + 1, right + 1, common, expected])
    # Directly check invariance without relying on the orbit encoder.
    edge_set = {(left - 1, right - 1) for left, right in edges}
    shifted = {
        tuple(sorted((
            vertex(split_vertex(left)[0], split_vertex(left)[1] + 1),
            vertex(split_vertex(right)[0], split_vertex(right)[1] + 1),
        )))
        for left, right in edge_set
    }
    return {
        "ok": (
            len(edges) == 693
            and all(degree == 14 for degree in degrees)
            and not bad_pairs
            and shifted == edge_set
        ),
        "edge_count": len(edges),
        "degree_histogram": {
            str(degree): degrees.count(degree) for degree in sorted(set(degrees))
        },
        "common_neighbour_histogram": dict(sorted(common_histogram.items())),
        "bad_pairs_first_25": bad_pairs,
        "C11_translation_invariant": shifted == edge_set,
        "edges": edges,
    }


def solve(conflicts: int | None) -> dict:
    from pysat.formula import CNF
    from pysat.solvers import Solver

    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    assert meta["status"] == "BUILT"
    assert sha256(CNF_PATH) == meta["cnf_sha256"]
    formula = CNF(from_file=str(CNF_PATH))
    started = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        if conflicts is None:
            answer = solver.solve()
        else:
            solver.conf_budget(conflicts)
            answer = solver.solve_limited()
        stats = solver.accum_stats()
        model = solver.get_model() if answer is True else None
    status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
    result = {
        "status": status,
        "model": meta["model"],
        "cnf": str(CNF_PATH),
        "cnf_sha256": meta["cnf_sha256"],
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "conflict_budget": conflicts,
        "solve_seconds": round(time.monotonic() - started, 6),
        "stats": stats,
        "claim_boundary": meta["claim_boundary"],
    }
    if model is not None:
        positive = {literal for literal in model if 0 < literal <= len(EDGE_KEYS)}
        checked = verify(expanded_edges(positive))
        result["verification"] = {
            key: value for key, value in checked.items() if key != "edges"
        }
        if not checked["ok"]:
            raise AssertionError(result["verification"])
        atomic_json(SOLUTION_PATH, checked)
        submission = "".join(f"{{{left}, {right}}}\n" for left, right in checked["edges"])
        Path("submission.txt").write_text(submission, encoding="ascii", newline="\n")
    atomic_json(RESULT_PATH, result)
    return result


def solve_normalized(
    conflicts: int | None, branch_indices: set[int] | None = None
) -> dict:
    """Solve every exact WLOG branch incrementally and verify any witness."""

    from pysat.formula import CNF
    from pysat.solvers import Solver

    meta = json.loads(NORMALIZED_META_PATH.read_text(encoding="utf-8"))
    assert meta["status"] == "BUILT"
    assert sha256(NORMALIZED_CNF_PATH) == meta["cnf_sha256"]
    formula = CNF(from_file=str(NORMALIZED_CNF_PATH))
    records = []
    started = time.monotonic()
    verified = None
    selected_branches = [
        branch for branch in meta["branches"]
        if branch_indices is None or branch["branch_index"] in branch_indices
    ]
    if branch_indices is not None:
        assert {branch["branch_index"] for branch in selected_branches} == branch_indices
    output_path = (
        NORMALIZED_RESULT_PATH if branch_indices is None else
        Path(
            "scratch_root_c11_semiregular_normalized_branches_"
            + "_".join(map(str, sorted(branch_indices)))
            + ("_unlimited" if conflicts is None else f"_c{conflicts}")
            + ".json"
        )
    )
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        for branch in selected_branches:
            before = solver.accum_stats()
            tick = time.monotonic()
            if conflicts is not None:
                solver.conf_budget(conflicts)
                answer = solver.solve_limited(assumptions=[branch["selector"]])
            else:
                answer = solver.solve(assumptions=[branch["selector"]])
            after = solver.accum_stats()
            status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
            record = {
                **branch,
                "status": status,
                "solve_seconds": round(time.monotonic() - tick, 6),
                "stats_delta": {
                    key: after.get(key, 0) - before.get(key, 0)
                    for key in set(before) | set(after)
                },
            }
            records.append(record)
            print(json.dumps(record, sort_keys=True), flush=True)
            if answer is True:
                model = solver.get_model()
                positive = {
                    literal for literal in model if 0 < literal <= len(EDGE_KEYS)
                }
                checked = verify(expanded_edges(positive))
                record["verification"] = {
                    key: value for key, value in checked.items() if key != "edges"
                }
                if not checked["ok"]:
                    raise AssertionError(record["verification"])
                atomic_json(SOLUTION_PATH, checked)
                Path("submission.txt").write_text(
                    "".join(
                        f"{{{left}, {right}}}\n" for left, right in checked["edges"]
                    ),
                    encoding="ascii",
                    newline="\n",
                )
                verified = record["verification"]
                break
            atomic_json(output_path, {
                "status": "IN_PROGRESS",
                "records": records,
            })
    counts = {
        status: sum(record["status"] == status for record in records)
        for status in ("SAT", "UNSAT", "UNKNOWN")
    }
    overall = (
        "SAT" if counts["SAT"] else
        "UNSAT" if len(records) == len(selected_branches) and not counts["UNKNOWN"] else
        "UNKNOWN"
    )
    result = {
        "status": overall,
        "model": meta["model"],
        "cnf": str(NORMALIZED_CNF_PATH),
        "cnf_sha256": meta["cnf_sha256"],
        "solver": "CaDiCaL 1.9.5 via one incremental PySAT instance",
        "conflict_budget_per_branch": conflicts,
        "selected_branch_indices": (
            None if branch_indices is None else sorted(branch_indices)
        ),
        "counts": counts,
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "verification": verified,
        "records": records,
        "claim_boundary": meta["claim_boundary"],
        "output": str(output_path),
    }
    atomic_json(output_path, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--build-normalized", action="store_true")
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--solve-normalized", action="store_true")
    parser.add_argument("--conflicts", type=int)
    parser.add_argument("--branch-indices", type=str)
    args = parser.parse_args()
    if args.build or not CNF_PATH.exists():
        print(json.dumps(build(), sort_keys=True), flush=True)
    if args.build_normalized or (
        args.solve_normalized and not NORMALIZED_CNF_PATH.exists()
    ):
        print(json.dumps(build_normalized(), sort_keys=True), flush=True)
    if args.solve:
        print(json.dumps(solve(args.conflicts), sort_keys=True), flush=True)
    if args.solve_normalized:
        branch_indices = (
            None if args.branch_indices is None else
            {int(value) for value in args.branch_indices.split(",")}
        )
        result = solve_normalized(args.conflicts, branch_indices)
        print(json.dumps({
            "status": result["status"],
            "counts": result["counts"],
            "elapsed_seconds": result["elapsed_seconds"],
        }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
