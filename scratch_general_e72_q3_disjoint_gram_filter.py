"""Exact disjoint-block Gram/profile filter for E72 local representatives.

The overlap-Gram filter fixes ``H`` in ``Z = W H W^T`` whenever its rational
linear system has a unique solution.  In that case every disjoint exceptional
fibre pair also has a fixed block total ``D_FG = 4 - Z_FG``.  The earlier
forced-C4 test checked each low vertex's disjoint-neighbour profile separately;
this file additionally requires the four profiles in every fibre to have the
fixed column totals D_FG.  The check is an exact finite integer DP.

Underdetermined Gram systems are retained conservatively.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path

import scratch_general_e79_local_audit as local79
from scratch_theory_local_psd_filter import analyze_representative
from scratch_theory_unsigned_kernel_filter import nullspace


DEFAULT_INPUT = Path("scratch_general_e72_q3_gram_frontier_local_graph_reps.json")
DEFAULT_OUTPUT = Path(
    "scratch_general_e72_q3_gram_frontier_disjoint_gram_filtered_reps.json"
)
PARAMETRIC_INPUT = Path("scratch_theory_e72_source332_parametric_gram.json")


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def row_geometry(row):
    supports = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
    vertices_by_fibre = tuple(
        tuple(
            local79.vertex_label(support, bits)
            for bits in itertools.product((0, 1), repeat=2)
        )
        for support in supports
    )
    fibre_of = {
        vertex: fibre
        for fibre, vertices in enumerate(vertices_by_fibre)
        for vertex in vertices
    }
    incidence_t = [
        [int(group in support) for support in supports]
        for group in local79.GROUPS
    ]
    basis_columns = nullspace(incidence_t)
    W = tuple(
        tuple(basis_columns[column][fibre] for column in range(len(basis_columns)))
        for fibre in range(len(supports))
    )
    return supports, vertices_by_fibre, fibre_of, W


def overlap_key(supports, fibre_of, edges):
    counts = Counter()
    for left, right in edges:
        left_fibre = fibre_of[left]
        right_fibre = fibre_of[right]
        if left_fibre == right_fibre:
            continue
        if set(supports[left_fibre]) & set(supports[right_fibre]):
            counts[tuple(sorted((left_fibre, right_fibre)))] += 1
    return tuple(sorted(counts.items()))


def gram_disjoint_targets(row, representative, supports, W):
    analysis = analyze_representative(row, representative)
    assert analysis["passes_or_undecided"]
    if analysis["solution_dimension"] != 0:
        return None, {
            "status": "UNDERDETERMINED_RETAINED",
            "kernel_dimension": analysis["kernel_dimension"],
            "solution_dimension": analysis["solution_dimension"],
        }
    H = tuple(
        tuple(Fraction(value) for value in line)
        for line in analysis["unique_solution"]
    )

    def z_entry(left, right):
        return sum(
            W[left][a] * H[a][b] * W[right][b]
            for a in range(len(H))
            for b in range(len(H))
        )

    overlap = {
        (left, right): count
        for left, right, count in analysis["overlap_block_totals"]
    }
    targets = {}
    for left, right in itertools.combinations(range(len(supports)), 2):
        z_value = z_entry(left, right)
        if set(supports[left]) & set(supports[right]):
            assert z_value == -overlap.get((left, right), 0)
            continue
        d_value = Fraction(4) - z_value
        if d_value.denominator != 1 or not (0 <= d_value <= 16):
            return False, {
                "status": "IMPOSSIBLE_DISJOINT_GRAM_TOTAL",
                "fibre_pair": [left, right],
                "D": str(d_value),
            }
        targets[(left, right)] = int(d_value)
    return targets, {
        "status": "UNIQUE_GRAM_DISJOINT_TOTALS",
        "kernel_dimension": analysis["kernel_dimension"],
        "targets": [[left, right, value] for (left, right), value in sorted(targets.items())],
    }


def vertex_z_options(
    fibre,
    vertex,
    supports,
    vertices_by_fibre,
    fibre_of,
    neighbours,
    profile_cache=None,
):
    support = supports[fibre]
    disjoint = tuple(
        other
        for other, other_support in enumerate(supports)
        if not set(support) & set(other_support)
    )
    a = sum(other in neighbours[vertex] for other in vertices_by_fibre[fibre] if other != vertex)
    overlap_neighbours = tuple(
        other
        for other in neighbours[vertex]
        if fibre_of[other] != fibre
        and bool(set(support) & set(supports[fibre_of[other]]))
    )
    assert 2 * a + len(overlap_neighbours) == 4
    required = len(disjoint) + a - 2
    if required < 0:
        return disjoint, ()
    external_groups = tuple(group for group in local79.GROUPS if group not in support)
    target = tuple(
        sum(group in supports[other] for other in disjoint)
        for group in external_groups
    )
    observed = tuple(
        sum(group in supports[fibre_of[other]] for other in overlap_neighbours)
        for group in external_groups
    )
    wanted = tuple(left - right for left, right in zip(target, observed))
    if min(wanted, default=0) < 0:
        return disjoint, ()
    cache_key = (fibre, a, wanted)
    if profile_cache is not None and cache_key in profile_cache:
        return disjoint, profile_cache[cache_key]
    options = []
    for values in itertools.product(range(5), repeat=len(disjoint)):
        if sum(values) != required:
            continue
        if all(
            sum(
                value
                for value, other in zip(values, disjoint)
                if group in supports[other]
            )
            == need
            for group, need in zip(external_groups, wanted)
        ):
            options.append(values)
    options = tuple(options)
    if profile_cache is not None:
        profile_cache[cache_key] = options
    return disjoint, options


def representative_feasible(
    row,
    representative,
    gram_cache,
    geometry=None,
    profile_cache=None,
    parametric_target_cases=None,
):
    if geometry is None:
        geometry = row_geometry(row)
    supports, vertices_by_fibre, fibre_of, W = geometry
    edges = frozenset(
        tuple(sorted((tuple(left), tuple(right))))
        for left, right in representative["edges"]
    )
    key = overlap_key(supports, fibre_of, edges)
    if key not in gram_cache:
        gram_cache[key] = gram_disjoint_targets(row, representative, supports, W)
    targets, gram_detail = gram_cache[key]
    if targets is None and not parametric_target_cases:
        return True, gram_detail
    if targets is False:
        return False, gram_detail

    neighbours = local79.neighbour_sets(tuple(fibre_of), edges)
    cases = [targets] if targets is not None else list(parametric_target_cases)
    passing_cases = []
    first_failure = None
    for case_index, target_case in enumerate(cases):
        case_passes = True
        for fibre, vertices in enumerate(vertices_by_fibre):
            disjoint = tuple(
                other
                for other in range(len(supports))
                if not set(supports[fibre]) & set(supports[other])
            )
            target = tuple(
                target_case[tuple(sorted((fibre, other)))] for other in disjoint
            )
            possible = {tuple(0 for _ in disjoint)}
            for vertex in vertices:
                option_disjoint, options = vertex_z_options(
                    fibre,
                    vertex,
                    supports,
                    vertices_by_fibre,
                    fibre_of,
                    neighbours,
                    profile_cache,
                )
                assert option_disjoint == disjoint
                updated = set()
                for partial in possible:
                    for option in options:
                        value = tuple(
                            left + right for left, right in zip(partial, option)
                        )
                        if all(left <= right for left, right in zip(value, target)):
                            updated.add(value)
                possible = updated
                if not possible:
                    break
            if target not in possible:
                case_passes = False
                if first_failure is None:
                    first_failure = {
                        **gram_detail,
                        "status": "DISJOINT_PROFILE_COLUMN_TOTAL_FAILURE",
                        "fibre": fibre,
                        "support": list(supports[fibre]),
                        "disjoint_fibres": list(disjoint),
                        "required_column_totals": list(target),
                    }
                break
        if case_passes:
            passing_cases.append(case_index)
    if not passing_cases:
        return False, first_failure
    return True, {
        **gram_detail,
        "status": (
            gram_detail["status"]
            if targets is not None
            else "PARAMETRIC_GRAM_CASE_RETAINED"
        ),
        "passing_parametric_case_indices": passing_cases,
    }


def run(input_path: Path, output_path: Path):
    source = json.loads(input_path.read_text(encoding="utf-8"))
    assert source["status"] == "COMPLETE"
    rows_out = []
    q_input = Counter()
    q_passing = Counter()
    failure_status = Counter()
    input_raw = input_orbits = passing_raw = passing_orbits = 0
    parametric_cases = {}
    if PARAMETRIC_INPUT.exists():
        parametric = json.loads(PARAMETRIC_INPUT.read_text(encoding="utf-8"))
        macro = parametric["macro"]
        key = (tuple([2, 2, 2, 1, 1, 1, 1, 1, 1]), macro["compression_orbit_index"])
        parametric_cases[key] = [
            {
                tuple(sorted((left, right))): int(Fraction(value))
                for left, right, value in item["disjoint_exceptional_block_totals"]
            }
            for item in parametric["feasible_parameters"]
        ]
    for row in source["support_rows"]:
        gram_cache = {}
        profile_cache = {}
        geometry = row_geometry(row)
        passing = []
        row_input_raw = sum(rep["orbit_size"] for rep in row["representatives"])
        row_passing_raw = 0
        for representative in row["representatives"]:
            q_input[representative["Q"]] += representative["orbit_size"]
            feasible, detail = representative_feasible(
                row,
                representative,
                gram_cache,
                geometry,
                profile_cache,
                parametric_cases.get(
                    (tuple(row["partition"]), row["compression_orbit_index"])
                ),
            )
            if feasible:
                passing.append({**representative, "disjoint_Gram_profile": detail})
                row_passing_raw += representative["orbit_size"]
                q_passing[representative["Q"]] += representative["orbit_size"]
            else:
                failure_status[detail["status"]] += 1
        input_raw += row_input_raw
        input_orbits += len(row["representatives"])
        passing_raw += row_passing_raw
        passing_orbits += len(passing)
        if passing:
            assert sum(rep["orbit_size"] for rep in passing) == row_passing_raw
            rows_out.append(
                {
                    **{key: value for key, value in row.items() if key != "representatives"},
                    "input_raw_survivors": row_input_raw,
                    "input_orbits": len(row["representatives"]),
                    "raw_survivors": row_passing_raw,
                    "orbit_count": len(passing),
                    "representatives": passing,
                }
            )
    assert input_raw == source["summary"]["raw_BP_survivors"]
    assert input_orbits == source["summary"]["local_graph_orbits"]
    result = {
        "status": "COMPLETE",
        "model": "exact unique-Gram disjoint block totals plus forced-profile column DP",
        "input": {"path": str(input_path), "sha256": sha256(input_path)},
        "parametric_input": (
            None
            if not PARAMETRIC_INPUT.exists()
            else {"path": str(PARAMETRIC_INPUT), "sha256": sha256(PARAMETRIC_INPUT)}
        ),
        "scope": (
            "unique rational Gram solutions fix every disjoint exceptional block "
            "total; underdetermined systems are conservatively retained"
        ),
        "summary": {
            "input_support_rows": len(source["support_rows"]),
            "passing_support_rows": len(rows_out),
            "input_raw_survivors": input_raw,
            "passing_raw_survivors": passing_raw,
            "input_orbits": input_orbits,
            "passing_orbits": passing_orbits,
            "input_Q_histogram": {str(k): v for k, v in sorted(q_input.items())},
            "passing_Q_histogram": {str(k): v for k, v in sorted(q_passing.items())},
            "failed_orbits_by_reason": dict(sorted(failure_status.items())),
            "all_passing_orbit_mass_identities_verified": True,
        },
        "support_rows": rows_out,
    }
    assert sum(row["raw_survivors"] for row in rows_out) == passing_raw
    assert sum(row["orbit_count"] for row in rows_out) == passing_orbits
    atomic_json(output_path, result)
    print(json.dumps({"status": "COMPLETE", **result["summary"]}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.input, args.output)


if __name__ == "__main__":
    main()
