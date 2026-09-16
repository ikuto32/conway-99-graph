"""Independent exhaustive labelled-state port audit for E0=76.

This implementation reads only the independent balance output.  It rebuilds
the admissible four-vertex fibre states from all 64 edge subsets and uses an
exact perfect-matching DFS for every group/state restriction.  No existing
E0=76 port implementation is read or imported.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
import itertools
import json
import math
from pathlib import Path


INPUT = Path("scratch_e76_independent_balance.json")
OUTPUT = Path("scratch_e76_independent_port.json")
VERTICES = tuple(itertools.product((0, 1), repeat=2))
PAIRS = tuple(itertools.combinations(range(4), 2))
SIDES = frozenset(
    pair
    for pair in PAIRS
    if sum(VERTICES[pair[0]][axis] != VERTICES[pair[1]][axis] for axis in (0, 1)) == 1
)
DIAGONALS = frozenset(set(PAIRS) - set(SIDES))


def locally_admissible(selected):
    selected = frozenset(selected)
    # The two BP sign bins in each support coordinate have capacity one.
    for u in range(4):
        for axis in (0, 1):
            for required_sign in (0, 1):
                if sum(
                    tuple(sorted((u, v))) in selected
                    and VERTICES[v][axis] == required_sign
                    for v in range(4)
                    if v != u
                ) > 1:
                    return False
    # Fixed internal contributions cannot exceed a full outer-pair equality.
    for u, v in PAIRS:
        common = sum(
            tuple(sorted((u, w))) in selected
            and tuple(sorted((v, w))) in selected
            for w in range(4)
            if w not in (u, v)
        )
        adjacency = (u, v) in selected
        intersection = sum(VERTICES[u][axis] == VERTICES[v][axis] for axis in (0, 1))
        if common + adjacency > 2 - intersection:
            return False
    return True


def state_type(deficit, selected):
    selected = frozenset(selected)
    if deficit == 0:
        return "C4"
    if deficit == 1:
        return "P4"
    if deficit == 2:
        if selected == DIAGONALS:
            return "two_diagonals"
        first, second = tuple(selected)
        return "adjacent_sides" if set(first) & set(second) else "opposite_sides"
    if deficit == 3:
        return "one_side" if selected <= SIDES else "one_diagonal"
    if deficit == 4:
        return "empty"
    raise ValueError(deficit)


def build_state_domains():
    domains = defaultdict(list)
    for word in itertools.product((0, 1), repeat=6):
        selected = frozenset(pair for pair, bit in zip(PAIRS, word) if bit)
        if not locally_admissible(selected):
            continue
        deficit = 4 - len(selected)
        ports_by_axis = []
        for axis in (0, 1):
            ports = []
            for u in range(4):
                actual_sign = VERTICES[u][axis]
                neighbours = [
                    v for v in range(4)
                    if v != u and tuple(sorted((u, v))) in selected
                ]
                for needed_sign in (0, 1):
                    used = sum(VERTICES[v][axis] == needed_sign for v in neighbours)
                    assert used <= 1
                    if used == 0:
                        ports.append((u, actual_sign, needed_sign))
            assert len(ports) == 2 * deficit
            ports_by_axis.append(tuple(ports))
        domains[deficit].append({
            "edges": tuple(sorted(selected)),
            "type": state_type(deficit, selected),
            "ports_by_axis": tuple(ports_by_axis),
        })
    assert {deficit: len(states) for deficit, states in domains.items()} == {
        0: 1, 1: 4, 2: 7, 3: 6, 4: 1
    }
    assert Counter(state["type"] for state in domains[2]) == Counter({
        "adjacent_sides": 4,
        "opposite_sides": 2,
        "two_diagonals": 1,
    })
    assert Counter(state["type"] for state in domains[3]) == Counter({
        "one_side": 4,
        "one_diagonal": 2,
    })
    return {deficit: tuple(states) for deficit, states in domains.items()}


def exact_matching_count(ports):
    """Count every perfect matching of compatible labelled ports exactly."""
    ports = tuple(ports)
    if len(ports) % 2:
        return 0
    size = len(ports)
    adjacency = [0] * size
    endpoint_pair_candidates = Counter()
    for left, right in itertools.combinations(range(size), 2):
        fibre_u, vertex_u, actual_u, need_u = ports[left]
        fibre_v, vertex_v, actual_v, need_v = ports[right]
        if fibre_u == fibre_v:
            continue
        if need_u != actual_v or need_v != actual_u:
            continue
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left
        endpoint_pair_candidates[
            tuple(sorted(((fibre_u, vertex_u), (fibre_v, vertex_v))))
        ] += 1
    # A fixed pair of graph vertices determines each endpoint's required sign,
    # so it can represent at most one port-pair candidate.  Thus a matching is
    # automatically a simple-edge set; no post-filter is hidden here.
    assert max(endpoint_pair_candidates.values(), default=0) <= 1

    @lru_cache(maxsize=None)
    def visit(mask):
        if mask == 0:
            return 1
        candidates = []
        probe = mask
        while probe:
            bit = probe & -probe
            u = bit.bit_length() - 1
            available = adjacency[u] & mask
            candidates.append((available.bit_count(), u, available))
            probe ^= bit
        degree, u, available = min(candidates)
        if degree == 0:
            return 0
        total = 0
        remaining_without_u = mask & ~(1 << u)
        while available:
            bit = available & -available
            v = bit.bit_length() - 1
            total += visit(remaining_without_u & ~(1 << v))
            available ^= bit
        return total

    return visit((1 << size) - 1)


def group_tables(supports, deficits, domains):
    answer = []
    dfs_instances = 0
    for group in range(7):
        incident = []
        for fibre_index, support in enumerate(supports):
            if group in support:
                incident.append((fibre_index, support.index(group)))
        table = {}
        state_ranges = [range(len(domains[deficits[index]])) for index, _axis in incident]
        for restriction in itertools.product(*state_ranges):
            ports = []
            for (fibre_index, axis), state_index in zip(incident, restriction):
                state = domains[deficits[fibre_index]][state_index]
                ports.extend(
                    (fibre_index, vertex, actual, needed)
                    for vertex, actual, needed in state["ports_by_axis"][axis]
                )
            table[restriction] = exact_matching_count(ports)
            dfs_instances += 1
        answer.append({
            "group": group,
            "incident": tuple(incident),
            "table": table,
            "restrictions": len(table),
            "positive_restrictions": sum(value > 0 for value in table.values()),
        })
    return answer, dfs_instances


def audit_row(row, domains):
    supports = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
    deficits = tuple(item["deficit"] for item in row["exceptional_supports"])
    assert sum(deficits) == 8
    tables, dfs_instances = group_tables(supports, deficits, domains)
    ranges = tuple(range(len(domains[deficit])) for deficit in deficits)
    tested = math.prod(map(len, ranges))
    feasible = 0
    completion_sum = 0
    completion_min = None
    completion_max = 0
    first = None
    type_histogram = Counter()
    for assignment in itertools.product(*ranges):
        matching_counts = []
        for data in tables:
            restriction = tuple(assignment[index] for index, _axis in data["incident"])
            count = data["table"][restriction]
            if count == 0:
                break
            matching_counts.append(count)
        else:
            product = math.prod(matching_counts)
            feasible += 1
            completion_sum += product
            completion_min = product if completion_min is None else min(completion_min, product)
            completion_max = max(completion_max, product)
            types = tuple(
                domains[deficit][state_index]["type"]
                for deficit, state_index in zip(deficits, assignment)
            )
            type_histogram[types] += 1
            if first is None:
                first = {
                    "state_indices": assignment,
                    "types": types,
                    "matching_counts_by_group": matching_counts,
                    "matching_completion_product": product,
                }
    return {
        "partition": list(row["partition"]),
        "orbit_index": row["orbit_index"],
        "orbit_size": row["orbit_size"],
        "exceptional_supports": row["exceptional_supports"],
        "labelled_state_assignments_tested": tested,
        "group_DFS_instances": dfs_instances,
        "group_table_sizes": [data["restrictions"] for data in tables],
        "group_positive_table_sizes": [data["positive_restrictions"] for data in tables],
        "port_feasible_state_assignments": feasible,
        "exact_matching_completion_sum": completion_sum,
        "completion_product_min": completion_min,
        "completion_product_max": completion_max,
        "feasible_type_histogram": {
            "|".join(types): count for types, count in sorted(type_histogram.items())
        },
        "first_feasible": first,
    }


def main():
    domains = build_state_domains()
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    assert source["ok"] and source["totals"]["balanced_orbits"] == 36
    rows = []
    for offset, source_row in enumerate(source["balanced_survivors"]):
        row = audit_row(source_row, domains)
        rows.append(row)
        print(json.dumps({
            "offset": offset,
            "partition": row["partition"],
            "orbit": row["orbit_index"],
            "tested": row["labelled_state_assignments_tested"],
            "feasible": row["port_feasible_state_assignments"],
        }), flush=True)

    by_partition = defaultdict(lambda: {
        "input_orbits": 0,
        "state_assignments_tested": 0,
        "port_survivor_orbits": 0,
        "port_feasible_state_assignments": 0,
        "matching_completions": 0,
    })
    for row in rows:
        key = "+".join(map(str, row["partition"]))
        record = by_partition[key]
        record["input_orbits"] += 1
        record["state_assignments_tested"] += row["labelled_state_assignments_tested"]
        record["port_survivor_orbits"] += row["port_feasible_state_assignments"] > 0
        record["port_feasible_state_assignments"] += row["port_feasible_state_assignments"]
        record["matching_completions"] += row["exact_matching_completion_sum"]

    result = {
        "model": "independent exhaustive labelled-state and exact-matching E0=76 port audit",
        "input": str(INPUT),
        "local_state_counts": {
            "delta0": 1,
            "delta1": 4,
            "delta2": 7,
            "delta3": 6,
            "delta4": 1,
        },
        "coverage": (
            "all products of all locally admissible labelled fibre states on all "
            "36 orientation-free balance survivors; exact perfect-matching DFS "
            "with labelled ports and distinct fibres in every group"
        ),
        "claim_boundary": (
            "port feasibility only; disjoint-support edges and full common-neighbour "
            "equalities are not imposed"
        ),
        "input_support_orbits": len(rows),
        "labelled_state_assignments_tested": sum(
            row["labelled_state_assignments_tested"] for row in rows
        ),
        "port_survivor_orbits": sum(row["port_feasible_state_assignments"] > 0 for row in rows),
        "port_feasible_state_assignments": sum(
            row["port_feasible_state_assignments"] for row in rows
        ),
        "exact_matching_completion_sum": sum(row["exact_matching_completion_sum"] for row in rows),
        "by_partition": dict(sorted(by_partition.items())),
        "rows": rows,
        "existing_E76_port_code_read_or_imported": False,
        "ok": True,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "tested": result["labelled_state_assignments_tested"],
        "survivor_orbits": result["port_survivor_orbits"],
        "feasible_states": result["port_feasible_state_assignments"],
        "by_partition": result["by_partition"],
    }))


if __name__ == "__main__":
    main()
