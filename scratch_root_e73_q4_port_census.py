"""Self-contained-root-reduced E0=73,Q>=4 fibre-state port census.

Only the Q>=4 subset of each complete Cartesian product is a target branch,
but both the full-product and target-subset coverage identities are checked.
Every allowed labelled fibre state and orientation remains distinct.  A
prefix is pruned only when no completion can reach Q>=4 or when an exact
per-group Hall lookahead proves that no port-matching completion exists.

The root choice S(r)<=69 is a self-contained audited consequence of the SRG
axioms, so no external n3 premise is used.  This remains only a necessary
branch reduction, not a claim that E0=73 is impossible, and uses no SAT/CP-SAT
result.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path

import scratch_general_e76_port_audit as port76
import scratch_general_e78_port_audit as port78
import scratch_general_e75_port_audit as port75


INPUT_PATH = Path("scratch_root_e73_q4_compression_audit.json")
OUTPUT_PATH = Path("scratch_root_e73_q4_port_census.json")
Q_MIN = 4
FIBRE_STATES = dict(port76.FIBRE_STATES)
assert tuple(len(FIBRE_STATES[d]) for d in range(1, 5)) == (4, 7, 6, 1)
DIAGONAL_PAIRS = frozenset((frozenset((0, 3)), frozenset((1, 2))))


def part_path(partition_index):
    return Path(f"scratch_root_e73_q4_port_part_{partition_index:02d}.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def product(values):
    answer = 1
    for value in values:
        answer *= value
    return answer


def state_q(deficit, state_index):
    state = FIBRE_STATES[deficit][state_index]
    return sum(frozenset(edge) in DIAGONAL_PAIRS for edge in state["edges"])


Q_VALUES = {
    deficit: tuple(
        state_q(deficit, state_index)
        for state_index in range(len(FIBRE_STATES[deficit]))
    )
    for deficit in range(1, 5)
}
assert Counter(Q_VALUES[1]) == Counter({0: 4})
assert Counter(Q_VALUES[2]) == Counter({0: 6, 2: 1})
assert Counter(Q_VALUES[3]) == Counter({0: 4, 1: 2})
assert Counter(Q_VALUES[4]) == Counter({0: 1})


def state_signature(deficit, state_index, axis):
    state = FIBRE_STATES[deficit][state_index]
    ports = port78.fibre_ports((0, 1), state["edges"], 0)
    counts = Counter(
        (sigma, required)
        for group, _fibre, _vertex, sigma, required in ports
        if group == axis
    )
    signature = tuple(
        counts[category]
        for category in ((0, 0), (0, 1), (1, 0), (1, 1))
    )
    assert sum(signature) == 2 * deficit
    return signature


SIGNATURES = {
    deficit: tuple(
        tuple(state_signature(deficit, state_index, axis) for axis in (0, 1))
        for state_index in range(len(FIBRE_STATES[deficit]))
    )
    for deficit in range(1, 5)
}


def assignment_order(supports, deficits):
    incident = {
        group: {index for index, support in enumerate(supports) if group in support}
        for group in range(7)
    }
    remaining = set(range(len(supports)))
    assigned = set()
    order = []
    while remaining:
        def score(index):
            endpoints = supports[index]
            closes = sum((incident[group] - {index}) <= assigned for group in endpoints)
            progress = sum(
                len(incident[group].intersection(assigned)) / len(incident[group])
                for group in endpoints
            )
            return closes, progress, -len(FIBRE_STATES[deficits[index]]), -index

        chosen = max(remaining, key=score)
        order.append(chosen)
        assigned.add(chosen)
        remaining.remove(chosen)
    assert sorted(order) == list(range(len(supports)))
    return tuple(order)


def signature_for(supports, deficits, variable, state_index, group):
    axis = supports[variable].index(group)
    return SIGNATURES[deficits[variable]][state_index][axis]


def build_group_lookahead(group, variables, supports, deficits, domains, position):
    ordered = tuple(sorted(variables, key=position.__getitem__))
    allowed = [set() for _ in range(len(ordered) + 1)]
    full_count = product(len(domains[index]) for index in ordered)
    matchable_count = 0
    for choices in itertools.product(*(domains[index] for index in ordered)):
        signatures = tuple(
            signature_for(supports, deficits, index, state_index, group)
            for index, state_index in zip(ordered, choices)
        )
        # Use the independently audited closed Hall formula from the E75 path.
        if not port75.group_matchable_signatures(signatures):
            continue
        matchable_count += 1
        for length in range(len(ordered) + 1):
            allowed[length].add(choices[:length])
    return {
        "group": group,
        "variables": ordered,
        "full_local_assignments": full_count,
        "matchable_full_local_assignments": matchable_count,
        "allowed_prefix_counts": [len(values) for values in allowed],
        "allowed": allowed,
    }


def suffix_q_distributions(order, deficits, domains):
    distributions = [Counter() for _ in range(len(order) + 1)]
    distributions[len(order)][0] = 1
    for depth in range(len(order) - 1, -1, -1):
        variable = order[depth]
        current = Counter()
        for state_index in domains[variable]:
            q_here = Q_VALUES[deficits[variable]][state_index]
            for q_suffix, count in distributions[depth + 1].items():
                current[q_here + q_suffix] += count
        distributions[depth] = current
    return distributions


def direct_check(exceptional, assignment):
    choices = tuple(
        FIBRE_STATES[item["deficit"]][state_index]
        for item, state_index in zip(exceptional, assignment)
    )
    by_group = port76.assignment_ports(exceptional, choices)
    hall = [port78.group_matchable(ports) for ports in by_group]
    direct = [port78.direct_matching_exists(ports) for ports in by_group]
    assert hall == direct and all(hall)
    return {
        "state_indices": list(assignment),
        "types": [choice["type"] for choice in choices],
        "Q": sum(
            state_q(item["deficit"], state_index)
            for item, state_index in zip(exceptional, assignment)
        ),
        "port_counts_by_group": [len(ports) for ports in by_group],
        "closed_Hall_test": hall,
        "direct_matching_DFS": direct,
    }


def audit_row(source):
    exceptional = source["exceptional_supports"]
    supports = tuple(tuple(item["support"]) for item in exceptional)
    deficits = tuple(item["deficit"] for item in exceptional)
    assert all(deficit in (1, 2, 3, 4) for deficit in deficits)
    domains = tuple(tuple(range(len(FIBRE_STATES[d]))) for d in deficits)
    full_total = product(len(domain) for domain in domains)
    order = assignment_order(supports, deficits)
    position = {variable: rank for rank, variable in enumerate(order)}
    incident = {
        group: tuple(index for index, support in enumerate(supports) if group in support)
        for group in range(7)
    }
    lookahead = {
        group: build_group_lookahead(
            group, variables, supports, deficits, domains, position
        )
        for group, variables in incident.items()
        if variables
    }
    local_rank = {
        (group, variable): rank
        for group, data in lookahead.items()
        for rank, variable in enumerate(data["variables"])
    }
    suffix_q = suffix_q_distributions(order, deficits, domains)
    suffix_total = [sum(distribution.values()) for distribution in suffix_q]
    assert suffix_total[0] == full_total
    q_eligible_total = sum(
        count for q, count in suffix_q[0].items() if q >= Q_MIN
    )
    q_ineligible_total = full_total - q_eligible_total

    def eligible_suffix_count(depth, current_q):
        return sum(
            count
            for added_q, count in suffix_q[depth].items()
            if current_q + added_q >= Q_MIN
        )

    assignment = [-1] * len(supports)
    feasible = []
    feasible_q_histogram = Counter()
    port_pruned_q_eligible = 0
    q_ineligible_accounted = 0
    partial_nodes = 0
    prefix_tests = 0
    pruned_by_group = [0] * 7

    def visit(depth, current_q):
        nonlocal port_pruned_q_eligible, q_ineligible_accounted
        nonlocal partial_nodes, prefix_tests
        if depth == len(order):
            if current_q >= Q_MIN:
                feasible.append(tuple(assignment))
                feasible_q_histogram[current_q] += 1
            else:
                q_ineligible_accounted += 1
            return
        variable = order[depth]
        for state_index in domains[variable]:
            partial_nodes += 1
            assignment[variable] = state_index
            next_q = current_q + Q_VALUES[deficits[variable]][state_index]
            eligible_below = eligible_suffix_count(depth + 1, next_q)
            if not eligible_below:
                q_ineligible_accounted += suffix_total[depth + 1]
                assignment[variable] = -1
                continue
            failed_group = None
            for group in supports[variable]:
                prefix_tests += 1
                data = lookahead[group]
                length = local_rank[(group, variable)] + 1
                prefix = tuple(
                    assignment[index] for index in data["variables"][:length]
                )
                assert all(value >= 0 for value in prefix)
                if prefix not in data["allowed"][length]:
                    failed_group = group
                    break
            if failed_group is None:
                visit(depth + 1, next_q)
            else:
                port_pruned_q_eligible += eligible_below
                q_ineligible_accounted += suffix_total[depth + 1] - eligible_below
                pruned_by_group[failed_group] += eligible_below
            assignment[variable] = -1

    visit(0, 0)
    assert len(feasible) + port_pruned_q_eligible == q_eligible_total
    assert q_ineligible_accounted == q_ineligible_total
    assert q_ineligible_accounted + port_pruned_q_eligible + len(feasible) == full_total
    assert len(feasible) == sum(feasible_q_histogram.values())
    first = direct_check(exceptional, feasible[0]) if feasible else None
    group_records = []
    for group in sorted(lookahead):
        data = lookahead[group]
        group_records.append({
            key: list(value) if key == "variables" else value
            for key, value in data.items()
            if key != "allowed"
        })
    return {
        "partition": source["partition"],
        "compression_orbit_index": source["orbit_index"],
        "support_orbit_size": source["orbit_size"],
        "weighted_stabilizer_order": source["weighted_stabilizer_order"],
        "exceptional_supports": exceptional,
        "maximum_Q_capacity": source["maximum_Q_capacity"],
        "joint_square_budget": source["joint_off_diagonal_square_budget"],
        "overlap_relaxed_minimum_square": source["overlap"]["minimum_square"],
        "disjoint_continuous_minimum": source["disjoint_continuous_minimum"],
        "full_labelled_fibre_state_product": full_total,
        "Q_at_least_4_assignments_covered": q_eligible_total,
        "Q_below_4_assignments_excluded": q_ineligible_total,
        "Q_at_least_4_assignments_pruned_by_port": port_pruned_q_eligible,
        "locally_port_feasible_Q_at_least_4_assignments": len(feasible),
        "full_product_coverage_identity_verified": (
            q_ineligible_accounted + port_pruned_q_eligible + len(feasible) == full_total
        ),
        "Q_target_coverage_identity_verified": (
            len(feasible) + port_pruned_q_eligible == q_eligible_total
        ),
        "partial_assignment_nodes_tested": partial_nodes,
        "group_prefix_tests": prefix_tests,
        "Q_target_assignments_pruned_by_first_failing_group": pruned_by_group,
        "assignment_order": list(order),
        "suffix_Q_distribution": {
            str(q): count for q, count in sorted(suffix_q[0].items())
        },
        "group_lookahead": group_records,
        "feasible_Q_histogram": {
            str(q): count for q, count in sorted(feasible_q_histogram.items())
        },
        "feasible_state_indices": [list(row) for row in feasible],
        "first_feasible_direct_control": first,
    }


def source_rows_by_partition():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    assert source["status"] == "COMPLETE"
    assert source["summary"]["spectral_real_surviving_support_orbits"] == 295
    partition_index = {
        tuple(row["partition"]): row["partition_index"]
        for row in source["by_partition"]
    }
    grouped = {}
    for row in source["rows"]:
        assert row["passes_weighted_port_overlap_and_real_relaxation"]
        grouped.setdefault(partition_index[tuple(row["partition"])], []).append(row)
    assert sum(map(len, grouped.values())) == 295
    return source, grouped


def summarize(rows):
    q_histogram = Counter()
    for row in rows:
        q_histogram.update(
            {int(q): count for q, count in row["feasible_Q_histogram"].items()}
        )
    return {
        "input_support_orbits": len(rows),
        "full_labelled_fibre_state_product": sum(
            row["full_labelled_fibre_state_product"] for row in rows
        ),
        "Q_at_least_4_assignments_covered": sum(
            row["Q_at_least_4_assignments_covered"] for row in rows
        ),
        "Q_below_4_assignments_excluded": sum(
            row["Q_below_4_assignments_excluded"] for row in rows
        ),
        "partial_assignment_nodes_tested": sum(
            row["partial_assignment_nodes_tested"] for row in rows
        ),
        "Q_at_least_4_assignments_pruned_by_port": sum(
            row["Q_at_least_4_assignments_pruned_by_port"] for row in rows
        ),
        "locally_port_feasible_support_orbits": sum(
            row["locally_port_feasible_Q_at_least_4_assignments"] > 0 for row in rows
        ),
        "locally_port_feasible_Q_at_least_4_assignments": sum(
            row["locally_port_feasible_Q_at_least_4_assignments"] for row in rows
        ),
        "feasible_Q_histogram": {
            str(q): count for q, count in sorted(q_histogram.items())
        },
        "all_full_product_identities_verified": all(
            row["full_product_coverage_identity_verified"] for row in rows
        ),
        "all_Q_target_identities_verified": all(
            row["Q_target_coverage_identity_verified"] for row in rows
        ),
    }


def refresh_scope_fields(result):
    result["model"] = (
        "self-contained-root-reduced E0=73,Q>=4 labelled fibre-state port census"
    )
    result.pop("conditional_scope", None)
    result["root_reduction_scope"] = (
        "E0=73 plus the independently audited self-contained S(r)<=69 theorem; "
        "no external n3 bound"
    )
    result["claim_boundary"] = (
        "Necessary E0=73,Q>=4 root branch only; exact port census, not an E0=73 exclusion."
    )
    return result


def run_partition(partition_index, force=False):
    _source, grouped = source_rows_by_partition()
    rows_in = grouped.get(partition_index, [])
    path = part_path(partition_index)
    if path.exists() and not force:
        result = json.loads(path.read_text(encoding="utf-8"))
        if result["status"] == "COMPLETE":
            refresh_scope_fields(result)
            atomic_json(path, result)
            print(json.dumps({"phase": "resume", "partition_index": partition_index, "status": "COMPLETE"}), flush=True)
            return result
        completed = {row["compression_orbit_index"] for row in result["rows"]}
    else:
        result = {
            "status": "ENUMERATING",
            "model": "self-contained-root-reduced E0=73,Q>=4 labelled fibre-state port census",
            "partition_index": partition_index,
            "partition": rows_in[0]["partition"] if rows_in else None,
            "input_support_orbits": len(rows_in),
            "fibre_state_counts": {str(d): len(FIBRE_STATES[d]) for d in range(1, 5)},
            "fibre_state_Q_histograms": {
                str(d): {str(q): count for q, count in sorted(Counter(Q_VALUES[d]).items())}
                for d in range(1, 5)
            },
            "coverage": (
                "all distinct labelled state indices with Q>=4; exact suffix-Q "
                "counts split every pruned subtree and prove both target-subset and "
                "full-Cartesian-product coverage identities"
            ),
            "root_reduction_scope": (
                "uses E0=73 plus the independently audited self-contained S(r)<=69 theorem"
            ),
            "rows": [],
        }
        completed = set()
        atomic_json(path, result)
    for offset, source_row in enumerate(rows_in):
        if source_row["orbit_index"] in completed:
            continue
        record = audit_row(source_row)
        result["rows"].append(record)
        result["summary"] = summarize(result["rows"])
        atomic_json(path, result)
        print(json.dumps({
            "phase": "row",
            "partition_index": partition_index,
            "offset": offset,
            "compression_orbit_index": source_row["orbit_index"],
            "Q_covered": record["Q_at_least_4_assignments_covered"],
            "port_feasible": record["locally_port_feasible_Q_at_least_4_assignments"],
            "partial_nodes": record["partial_assignment_nodes_tested"],
        }), flush=True)
    assert len(result["rows"]) == len(rows_in)
    assert len({row["compression_orbit_index"] for row in result["rows"]}) == len(rows_in)
    result["status"] = "COMPLETE"
    result["summary"] = summarize(result["rows"])
    refresh_scope_fields(result)
    atomic_json(path, result)
    return result


def merge_parts():
    source, grouped = source_rows_by_partition()
    parts = []
    for partition_index in sorted(grouped):
        path = part_path(partition_index)
        if not path.exists():
            raise RuntimeError(f"missing {path}")
        part = json.loads(path.read_text(encoding="utf-8"))
        if part["status"] != "COMPLETE":
            raise RuntimeError(f"incomplete {path}: {part['status']}")
        parts.append(part)
    rows = [row for part in parts for row in part["rows"]]
    result = {
        "status": "COMPLETE",
        "model": "self-contained-root-reduced E0=73,Q>=4 labelled fibre-state port census",
        "input": str(INPUT_PATH),
        "input_sha256": sha256(INPUT_PATH),
        "input_support_orbits": 295,
        "fibre_state_counts": {str(d): len(FIBRE_STATES[d]) for d in range(1, 5)},
        "fibre_state_Q_histograms": {
            str(d): {str(q): count for q, count in sorted(Counter(Q_VALUES[d]).items())}
            for d in range(1, 5)
        },
        "matching_test": (
            "exact per-group category/Hall condition with extendable-prefix "
            "lookahead; first feasible assignment per positive support row is "
            "checked by independent direct port-matching DFS"
        ),
        "coverage": (
            "all labelled fibre-state assignments with Q>=4, with no orientation, "
            "type, or symmetry WLOG; per-row exact suffix-Q counts verify both "
            "Q-target and full-product identities"
        ),
        "summary": summarize(rows),
        "by_partition": [
            {
                "partition_index": part["partition_index"],
                "partition": part["partition"],
                **part["summary"],
                "artifact": str(part_path(part["partition_index"])),
            }
            for part in parts
        ],
        "rows": rows,
        "claim_boundary": (
            "This is an exact solver-free census only inside the necessary "
            "E0=73,Q>=4 root branch. The independently audited self-contained "
            "S<=69 theorem is used, no external n3 bound is used, and no E0=73 "
            "exclusion is claimed."
        ),
    }
    assert result["summary"]["input_support_orbits"] == 295
    assert result["summary"]["all_full_product_identities_verified"]
    assert result["summary"]["all_Q_target_identities_verified"]
    atomic_json(OUTPUT_PATH, result)
    print(json.dumps({"path": str(OUTPUT_PATH), "status": "COMPLETE", **result["summary"]}, sort_keys=True), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition-index", type=int)
    parser.add_argument("--partition-indices", type=str)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    selected = sum((
        args.partition_index is not None,
        args.partition_indices is not None,
        args.all,
        args.merge,
    ))
    if selected != 1:
        parser.error("choose exactly one input mode")
    _source, grouped = source_rows_by_partition()
    if args.partition_index is not None:
        run_partition(args.partition_index, args.force)
    elif args.partition_indices is not None:
        indices = tuple(int(value) for value in args.partition_indices.split(","))
        if not indices or len(indices) != len(set(indices)):
            parser.error("partition indices must be nonempty and unique")
        for index in indices:
            run_partition(index, args.force)
    elif args.all:
        for index in sorted(grouped):
            run_partition(index, args.force)
    else:
        merge_parts()


if __name__ == "__main__":
    main()
