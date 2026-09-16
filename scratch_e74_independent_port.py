"""Independent solver-free audit of the E0=74 port census.

This program reads committed JSON data, but neither imports nor reads any E74
discovery/counting source file.  It reconstructs the four-vertex state domains
from all 64 edge subsets, derives a closed Hall test for group ports, checks
that test against a separate labelled-port matching DFS, enumerates every
globally feasible state tuple with independent prefix projections, and counts
all exact overlap matchings.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path


COMPRESSION = Path("scratch_general_e74_compression_audit.json")
TARGET_CENSUS = Path("scratch_general_e74_port_census.json")
TARGET_STATES = Path("scratch_general_e74_port_feasible_states.json")
TARGET_COMPLETIONS = Path("scratch_general_e74_local_completion_counts.json")
STATE_OUTPUT = Path("scratch_e74_independent_state_catalog.json")
GROUP_OUTPUT = Path("scratch_e74_independent_group_matching.json")
FEASIBLE_OUTPUT = Path("scratch_e74_independent_feasible_states.json")
AUDIT_OUTPUT = Path("scratch_e74_independent_port_audit.json")

VERTICES = tuple(itertools.product((0, 1), repeat=2))
PAIRS = tuple(itertools.combinations(range(4), 2))
SIDES = frozenset(
    pair for pair in PAIRS
    if sum(VERTICES[pair[0]][axis] != VERTICES[pair[1]][axis]
           for axis in (0, 1)) == 1
)
DIAGONALS = frozenset(set(PAIRS) - set(SIDES))
SIDE_ORDER = tuple(pair for pair in PAIRS if pair in SIDES)
PORT_TYPES = ((0, 0), (0, 1), (1, 0), (1, 1))


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locally_admissible(selected):
    """Necessary BP-bin and induced-pair checks inside one four-set."""
    selected = frozenset(selected)
    for u in range(4):
        for axis in (0, 1):
            for needed_sign in (0, 1):
                used = sum(
                    tuple(sorted((u, v))) in selected
                    and VERTICES[v][axis] == needed_sign
                    for v in range(4) if v != u
                )
                if used > 1:
                    return False
    for u, v in PAIRS:
        common = sum(
            tuple(sorted((u, w))) in selected
            and tuple(sorted((v, w))) in selected
            for w in range(4) if w not in (u, v)
        )
        adjacent = (u, v) in selected
        fixed_inner_common = sum(
            VERTICES[u][axis] == VERTICES[v][axis] for axis in (0, 1)
        )
        if common + adjacent > 2 - fixed_inner_common:
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
        return "single_side" if selected <= SIDES else "single_diagonal"
    if deficit == 4:
        return "empty"
    raise ValueError(deficit)


def local_Q(deficit, selected):
    """Reconstruct the Q convention used in the committed state catalog."""
    selected = frozenset(selected)
    return len(selected & DIAGONALS)


def build_domains():
    domains = defaultdict(list)
    # The labelled state index is the increasing six-bit edge mask with PAIRS
    # in lexicographic order and PAIRS[0] as the least-significant bit.
    for mask in range(1 << len(PAIRS)):
        selected = frozenset(
            pair for index, pair in enumerate(PAIRS) if mask & (1 << index)
        )
        if not locally_admissible(selected):
            continue
        deficit = 4 - len(selected)
        ports_by_axis = []
        for axis in (0, 1):
            ports = []
            for vertex in range(4):
                actual = VERTICES[vertex][axis]
                neighbours = [
                    other for other in range(4)
                    if other != vertex
                    and tuple(sorted((vertex, other))) in selected
                ]
                for needed in (0, 1):
                    used = sum(VERTICES[other][axis] == needed for other in neighbours)
                    assert used <= 1
                    if used == 0:
                        ports.append((vertex, actual, needed))
            assert len(ports) == 2 * deficit
            ports_by_axis.append(tuple(ports))
        domains[deficit].append({
            "state_index": len(domains[deficit]),
            "edges": tuple(sorted(selected)),
            "type": state_type(deficit, selected),
            "ports_by_axis": tuple(ports_by_axis),
            "Q": local_Q(deficit, selected),
        })
    answer = {deficit: tuple(states) for deficit, states in domains.items()}
    # E74's labelled index convention lists the six two-side states first and
    # the two-diagonal state last.  Other deficits already follow edge-mask
    # order.  This explicit crosswalk prevents a type-correct but label-wrong
    # audit (in particular, delta2 index 6 is two_diagonals).
    delta2_order = [frozenset(edges) for edges in itertools.combinations(SIDE_ORDER, 2)]
    delta2_order.append(DIAGONALS)
    by_edges = {frozenset(state["edges"]): state for state in answer[2]}
    answer[2] = tuple(by_edges[edges] for edges in delta2_order)
    for deficit, states in answer.items():
        for state_index, state in enumerate(states):
            state["state_index"] = state_index
            state["Q"] = local_Q(deficit, state["edges"])
    assert {deficit: len(answer[deficit]) for deficit in range(5)} == {
        0: 1, 1: 4, 2: 7, 3: 6, 4: 1,
    }
    assert Counter(state["type"] for state in answer[1]) == Counter({"P4": 4})
    assert Counter(state["type"] for state in answer[2]) == Counter({
        "adjacent_sides": 4, "opposite_sides": 2, "two_diagonals": 1,
    })
    assert Counter(state["type"] for state in answer[3]) == Counter({
        "single_side": 4, "single_diagonal": 2,
    })
    diagonal_states = [state for state in answer[3]
                       if state["type"] == "single_diagonal"]
    assert {state["edges"] for state in diagonal_states} == {
        ((0, 3),), ((1, 2),),
    }
    assert len({state["state_index"] for state in diagonal_states}) == 2
    return answer


def port_signature(ports, fibre_count):
    counts = [[0] * 4 for _ in range(fibre_count)]
    type_index = {kind: index for index, kind in enumerate(PORT_TYPES)}
    for fibre, _vertex, actual, needed in ports:
        counts[fibre][type_index[(actual, needed)]] += 1
    return tuple(tuple(row) for row in counts)


def hall_matchable(signature):
    """Closed Hall criterion for the four reciprocal port categories."""
    # 00 and 11 pair inside their own category, but never within one fibre.
    for category in (0, 3):
        total = sum(row[category] for row in signature)
        if total % 2:
            return False
        if max((row[category] for row in signature), default=0) * 2 > total:
            return False
    # 01 pairs only with 10.  Hall for K_{L,R} minus same-fibre blocks reduces
    # to equality of the shores and the one-fibre inequalities below.
    left = sum(row[1] for row in signature)
    right = sum(row[2] for row in signature)
    if left != right:
        return False
    if any(row[1] + row[2] > left for row in signature):
        return False
    return True


def direct_matching_count(ports):
    """Separate labelled-port perfect-matching DFS; returns the exact count."""
    ports = tuple(ports)
    if len(ports) % 2:
        return 0
    size = len(ports)
    adjacency = [0] * size
    endpoint_candidates = Counter()
    for left, right in itertools.combinations(range(size), 2):
        fibre_u, vertex_u, actual_u, needed_u = ports[left]
        fibre_v, vertex_v, actual_v, needed_v = ports[right]
        if fibre_u == fibre_v:
            continue
        if needed_u != actual_v or needed_v != actual_u:
            continue
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left
        endpoint_candidates[
            tuple(sorted(((fibre_u, vertex_u), (fibre_v, vertex_v))))
        ] += 1
    assert max(endpoint_candidates.values(), default=0) <= 1

    @lru_cache(maxsize=None)
    def visit(mask):
        if mask == 0:
            return 1
        choices = []
        probe = mask
        while probe:
            bit = probe & -probe
            u = bit.bit_length() - 1
            available = adjacency[u] & mask
            choices.append((available.bit_count(), u, available))
            probe ^= bit
        degree, u, available = min(choices)
        if degree == 0:
            return 0
        remainder = mask & ~(1 << u)
        total = 0
        while available:
            bit = available & -available
            v = bit.bit_length() - 1
            total += visit(remainder & ~(1 << v))
            available ^= bit
        return total

    return visit((1 << size) - 1)


class LayoutTable:
    def __init__(self, layout, domains):
        self.layout = tuple(layout)
        self.ranges = tuple(range(len(domains[deficit]))
                            for deficit, _axis in self.layout)
        self.full_assignment_count = math.prod(map(len, self.ranges))
        self.matching_counts = {}
        self.signature_counts = {}
        self.hall_direct_disagreements = 0
        representative_ports = {}
        for restriction in itertools.product(*self.ranges):
            ports = []
            for fibre, ((deficit, axis), state_index) in enumerate(
                    zip(self.layout, restriction)):
                state = domains[deficit][state_index]
                ports.extend(
                    (fibre, vertex, actual, needed)
                    for vertex, actual, needed in state["ports_by_axis"][axis]
                )
            signature = port_signature(ports, len(self.layout))
            representative_ports.setdefault(signature, tuple(ports))
            self.signature_counts[restriction] = signature
        self.signature_matching_counts = {}
        for signature, ports in representative_ports.items():
            hall = hall_matchable(signature)
            direct = direct_matching_count(ports)
            if hall != (direct > 0):
                self.hall_direct_disagreements += 1
            self.signature_matching_counts[signature] = direct
        for restriction, signature in self.signature_counts.items():
            self.matching_counts[restriction] = self.signature_matching_counts[signature]

        # Projection to every subset makes prefix pruning independent of the
        # chosen global variable order.
        self.allowed_by_mask = [set() for _ in range(1 << len(self.layout))]
        for restriction, count in self.matching_counts.items():
            if count == 0:
                continue
            for mask in range(1 << len(self.layout)):
                self.allowed_by_mask[mask].add(tuple(
                    restriction[position]
                    for position in range(len(self.layout))
                    if mask & (1 << position)
                ))

    def prefix_allowed(self, assignment, incident):
        mask = 0
        values = []
        for position, fibre_index in enumerate(incident):
            value = assignment[fibre_index]
            if value >= 0:
                mask |= 1 << position
                values.append(value)
        return tuple(values) in self.allowed_by_mask[mask]


def independent_assignment_order(supports, domains, deficits):
    """Graph-local deterministic order, derived without target order fields."""
    incident = {
        group: tuple(index for index, support in enumerate(supports) if group in support)
        for group in range(7)
    }
    selected = set()
    order = []
    while len(order) < len(supports):
        candidates = []
        for index, support in enumerate(supports):
            if index in selected:
                continue
            completes = sum(
                all(other in selected or other == index for other in incident[group])
                for group in support
            )
            contacts = sum(
                sum(other in selected for other in incident[group])
                for group in support
            )
            domain_size = len(domains[deficits[index]])
            candidates.append(((completes, contacts, -domain_size, -index), index))
        _score, chosen = max(candidates)
        selected.add(chosen)
        order.append(chosen)
    return tuple(order)


def row_key(row, orbit_field):
    return tuple(row["partition"]), int(row[orbit_field])


def histogram_to_json(counter):
    return {str(key): counter[key] for key in sorted(counter)}


def main():
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    domains = build_domains()
    compression = read(COMPRESSION)
    target_census = read(TARGET_CENSUS)
    target_states = read(TARGET_STATES)
    target_completions = read(TARGET_COMPLETIONS)

    input_rows = [row for row in compression["rows"]
                  if row["passes_weighted_port_overlap_and_real_relaxation"]]
    census_map = {row_key(row, "compression_orbit_index"): row
                  for row in target_census["rows"]}
    state_map = {row_key(row, "compression_orbit_index"): row
                 for row in target_states["rows"]}
    completion_map = {row_key(row, "compression_orbit_index"): row
                      for row in target_completions["rows"]}
    input_keys = {row_key(row, "orbit_index") for row in input_rows}
    check(len(input_rows) == 249, "compression survivor count is not 249")
    check(len(input_keys) == 249, "compression survivor keys not unique")
    check(input_keys == set(census_map), "249-row census key coverage differs")

    # Discover every group layout from the 249 support rows before enumerating
    # global tuples.  Layout positions are labelled fibre positions.
    layouts = set()
    for row in input_rows:
        supports = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
        deficits = tuple(item["deficit"] for item in row["exceptional_supports"])
        for group in range(7):
            layout = tuple(
                (deficits[index], support.index(group))
                for index, support in enumerate(supports) if group in support
            )
            if layout:
                # Fibre positions are exchangeable in the group-only test.
                # Sorting gives the intrinsic deficit/axis layout catalog.
                layouts.add(tuple(sorted(layout)))
    layout_tables = {layout: LayoutTable(layout, domains) for layout in sorted(layouts)}
    group_rows = []
    for layout in sorted(layouts):
        table = layout_tables[layout]
        group_rows.append({
            "incident_deficit_axis_layout": [list(item) for item in layout],
            "labelled_state_assignments_covered": table.full_assignment_count,
            "unique_signature_rows_checked": len(table.signature_matching_counts),
            "matchable_unique_signatures": sum(
                value > 0 for value in table.signature_matching_counts.values()
            ),
            "matchable_labelled_state_assignments": sum(
                value > 0 for value in table.matching_counts.values()
            ),
            "hall_equals_direct_DFS": table.hall_direct_disagreements == 0,
        })
    group_totals = {
        "support_rows_scanned": len(input_rows),
        "distinct_incident_deficit_axis_layouts": len(layouts),
        "labelled_group_state_assignments_covered": sum(
            row["labelled_state_assignments_covered"] for row in group_rows
        ),
        "unique_signature_rows_checked": sum(
            row["unique_signature_rows_checked"] for row in group_rows
        ),
        "hall_direct_disagreements": sum(
            not row["hall_equals_direct_DFS"] for row in group_rows
        ),
    }
    check(group_totals["distinct_incident_deficit_axis_layouts"] == 49,
          "group layout count is not 49")
    check(group_totals["labelled_group_state_assignments_covered"] == 20476,
          "group assignment coverage is not 20476")
    check(group_totals["unique_signature_rows_checked"] == 4497,
          "unique signature count is not 4497")
    check(group_totals["hall_direct_disagreements"] == 0,
          "Hall/direct matching disagreement")

    STATE_OUTPUT.write_text(json.dumps({
        "model": "independent exhaustive four-vertex fibre-state catalog",
        "edge_subsets_tested": 64,
        "state_counts": {str(d): len(domains[d]) for d in range(5)},
        "deficit_3_single_diagonal_state_indices": [
            state["state_index"] for state in domains[3]
            if state["type"] == "single_diagonal"
        ],
        "deficit_3_single_diagonal_edges": [
            [[*edge] for edge in state["edges"]]
            for state in domains[3] if state["type"] == "single_diagonal"
        ],
        "states": {
            str(deficit): [
                {
                    "state_index": state["state_index"],
                    "type": state["type"],
                    "edges": [[*edge] for edge in state["edges"]],
                    "ports_by_axis": [
                        [[*port] for port in ports]
                        for ports in state["ports_by_axis"]
                    ],
                    "Q": state["Q"],
                }
                for state in domains[deficit]
            ] for deficit in range(5)
        },
        "existing_E74_discovery_source_read_or_imported": False,
    }, indent=2) + "\n", encoding="utf-8")

    GROUP_OUTPUT.write_text(json.dumps({
        "model": "independent closed-Hall versus labelled matching-DFS audit",
        "hall_criterion": {
            "00_and_11": "even total and max same-fibre multiplicity <= half total",
            "01_vs_10": "equal totals and c01[f]+c10[f] <= total for every fibre",
        },
        "totals": group_totals,
        "rows": group_rows,
        "existing_E74_discovery_source_read_or_imported": False,
    }, indent=2) + "\n", encoding="utf-8")

    independent_rows = []
    explicit_feasible_rows = []
    by_partition = defaultdict(lambda: Counter())
    aggregate_state_Q = Counter()
    aggregate_completion_Q = Counter()
    full_total = pruned_total = feasible_total = completion_total = node_total = 0
    order_matches = 0

    for offset, row in enumerate(input_rows):
        key = row_key(row, "orbit_index")
        census_target = census_map[key]
        supports = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
        deficits = tuple(item["deficit"] for item in row["exceptional_supports"])
        check(sum(deficits) == 10, f"row {key}: deficit sum")
        check(row["exceptional_supports"] == census_target["exceptional_supports"],
              f"row {key}: exceptional support list differs")
        ranges = tuple(range(len(domains[deficit])) for deficit in deficits)
        full_product = math.prod(map(len, ranges))
        order = independent_assignment_order(supports, domains, deficits)
        if list(order) == census_target["assignment_order"]:
            order_matches += 1

        group_data = []
        for group in range(7):
            incident = tuple(sorted(
                (index for index, support in enumerate(supports) if group in support),
                key=lambda index: (deficits[index], supports[index].index(group), index),
            ))
            layout = tuple((deficits[index], supports[index].index(group))
                           for index in incident)
            table = layout_tables[layout] if layout else LayoutTable((), domains)
            group_data.append((incident, table))

        assignment = [-1] * len(supports)
        suffix = [1] * (len(order) + 1)
        for depth in range(len(order) - 1, -1, -1):
            suffix[depth] = suffix[depth + 1] * len(ranges[order[depth]])
        feasible = []
        completion_counts = []
        Q_values = []
        group_count_histograms = [Counter() for _ in range(7)]
        pruned = 0
        nodes = 0

        def visit(depth):
            nonlocal pruned, nodes
            if depth == len(order):
                state_tuple = tuple(assignment)
                matching_counts = []
                for group, (incident, table) in enumerate(group_data):
                    restriction = tuple(state_tuple[index] for index in incident)
                    count = table.matching_counts[restriction]
                    assert count > 0
                    matching_counts.append(count)
                    group_count_histograms[group][count] += 1
                completions = math.prod(matching_counts)
                Q = sum(domains[deficit][state_index]["Q"]
                        for deficit, state_index in zip(deficits, state_tuple))
                feasible.append(state_tuple)
                completion_counts.append(completions)
                Q_values.append(Q)
                return
            fibre_index = order[depth]
            for state_index in ranges[fibre_index]:
                nodes += 1
                assignment[fibre_index] = state_index
                allowed = True
                for group in supports[fibre_index]:
                    incident, table = group_data[group]
                    if not table.prefix_allowed(assignment, incident):
                        allowed = False
                        break
                if allowed:
                    visit(depth + 1)
                else:
                    pruned += suffix[depth + 1]
                assignment[fibre_index] = -1

        visit(0)
        feasible_count = len(feasible)
        check(pruned + feasible_count == full_product,
              f"row {key}: independent coverage identity")
        check(full_product == census_target["labelled_fibre_state_assignments_covered"],
              f"row {key}: target full product")
        check(feasible_count == census_target["locally_port_feasible_assignments"],
              f"row {key}: target feasible count")
        check(pruned == census_target["assignments_pruned_in_subtrees"],
              f"row {key}: target pruned count")

        state_Q_hist = Counter(Q_values)
        completion_Q_hist = Counter()
        completion_hist = Counter(completion_counts)
        for Q, count in zip(Q_values, completion_counts):
            completion_Q_hist[Q] += count
        exact_completions = sum(completion_counts)

        if feasible_count:
            check(key in state_map, f"row {key}: absent from target feasible states")
            check(key in completion_map, f"row {key}: absent from target completions")
            state_target = state_map[key]
            completion_target = completion_map[key]
            target_Q = {
                tuple(indices): Q for indices, Q in zip(
                    state_target["feasible_state_indices"],
                    state_target["Q_by_feasible_state"],
                )
            }
            own_Q = {state_tuple: Q for state_tuple, Q in zip(feasible, Q_values)}
            check(set(own_Q) == set(target_Q), f"row {key}: feasible state set")
            check(own_Q == target_Q, f"row {key}: Q reconstruction")
            check(exact_completions == completion_target["exact_overlap_completions"],
                  f"row {key}: exact completion total")
            check(max(completion_counts) ==
                  completion_target["maximum_completions_for_one_state"],
                  f"row {key}: maximum state completions")
            check(histogram_to_json(completion_hist) ==
                  completion_target["completion_count_histogram"],
                  f"row {key}: completion histogram")
            check([histogram_to_json(counter) for counter in group_count_histograms] ==
                  completion_target["group_matching_count_histograms"],
                  f"row {key}: group matching histograms")
            check(histogram_to_json(state_Q_hist) ==
                  completion_target["state_Q_histogram"],
                  f"row {key}: state Q histogram")
            check(histogram_to_json(completion_Q_hist) ==
                  completion_target["completion_Q_histogram"],
                  f"row {key}: completion Q histogram")
            explicit_feasible_rows.append({
                "partition": list(key[0]),
                "compression_orbit_index": key[1],
                "independent_assignment_order": list(order),
                "feasible_state_indices": [list(item) for item in sorted(feasible)],
                "Q_by_sorted_feasible_state": [own_Q[item] for item in sorted(feasible)],
                "completion_count_by_sorted_feasible_state": [
                    completion_counts[feasible.index(item)] for item in sorted(feasible)
                ],
            })
        else:
            check(key not in state_map, f"row {key}: zero row present in target states")
            check(key not in completion_map,
                  f"row {key}: zero row present in target completions")

        aggregate_state_Q.update(state_Q_hist)
        aggregate_completion_Q.update(completion_Q_hist)
        full_total += full_product
        pruned_total += pruned
        feasible_total += feasible_count
        completion_total += exact_completions
        node_total += nodes
        pkey = "+".join(map(str, key[0]))
        part = by_partition[pkey]
        part["support_rows"] += 1
        part["labelled_state_products"] += full_product
        part["feasible_support_rows"] += feasible_count > 0
        part["feasible_states"] += feasible_count
        part["exact_overlap_completions"] += exact_completions

        independent_rows.append({
            "partition": list(key[0]),
            "compression_orbit_index": key[1],
            "support_orbit_size": row["orbit_size"],
            "exceptional_supports": row["exceptional_supports"],
            "independent_assignment_order": list(order),
            "target_assignment_order_matched": list(order) ==
                census_target["assignment_order"],
            "labelled_fibre_state_assignments_covered": full_product,
            "partial_assignment_nodes_tested": nodes,
            "assignments_pruned_in_subtrees": pruned,
            "locally_port_feasible_assignments": feasible_count,
            "coverage_identity_verified": pruned + feasible_count == full_product,
            "exact_overlap_completions": exact_completions,
            "maximum_completions_for_one_state":
                max(completion_counts, default=0),
            "state_Q_histogram": histogram_to_json(state_Q_hist),
            "completion_Q_histogram": histogram_to_json(completion_Q_hist),
        })
        if (offset + 1) % 25 == 0 or offset + 1 == len(input_rows):
            print(json.dumps({
                "rows_completed": offset + 1,
                "full_products": full_total,
                "feasible_states": feasible_total,
                "exact_completions": completion_total,
                "errors": len(errors),
            }), flush=True)

    positive_keys = {row_key(row, "compression_orbit_index")
                     for row in target_states["rows"]}
    check(positive_keys == {row_key(row, "compression_orbit_index")
                            for row in target_completions["rows"]},
          "target feasible/completion positive keys differ")
    check(len(explicit_feasible_rows) == 175, "independent positive support rows")
    check(len(state_map) == 175, "target positive support rows")
    check(full_total == 134371022, "full assignment total")
    check(pruned_total == 134341819, "pruned assignment total")
    check(feasible_total == 29203, "feasible state total")
    check(pruned_total + feasible_total == full_total, "global coverage identity")
    check(completion_total == 25715712, "exact completion total")
    check(aggregate_state_Q == Counter({
        0: 26486, 1: 52, 2: 2346, 4: 230, 6: 79, 8: 8, 10: 2,
    }), "aggregate state Q histogram")
    check(aggregate_completion_Q == Counter({
        0: 19637248, 1: 20480, 2: 4071424, 4: 525312,
        6: 1361920, 8: 32768, 10: 66560,
    }), "aggregate completion Q histogram")
    Q5_completions = sum(value for Q, value in aggregate_completion_Q.items() if Q >= 5)
    check(Q5_completions == 1461248, "Q>=5 completion total")

    FEASIBLE_OUTPUT.write_text(json.dumps({
        "model": "independent explicit E0=74 port-feasible state reconstruction",
        "support_rows": len(explicit_feasible_rows),
        "feasible_state_assignments": feasible_total,
        "exact_overlap_completions": completion_total,
        "rows": explicit_feasible_rows,
        "existing_E74_discovery_source_read_or_imported": False,
    }, indent=2) + "\n", encoding="utf-8")

    result = {
        "model": "independent solver-free E0=74 port census and matching audit",
        "ok": not errors,
        "inputs": {
            path.name: sha256(path) for path in (
                COMPRESSION, TARGET_CENSUS, TARGET_STATES, TARGET_COMPLETIONS
            )
        },
        "method": {
            "state_catalog": "all 64 four-vertex edge subsets",
            "group_feasibility": "closed reciprocal-category Hall test",
            "control": "separate labelled-port perfect-matching DFS",
            "global_enumeration": "independent-order DFS with exact all-subset prefix projections",
            "completion_count": "product of seven exact labelled matching-DFS counts",
            "solver_negative_results_used": False,
            "existing_E74_discovery_source_read_or_imported": False,
        },
        "state_catalog": {
            "deficit_1": len(domains[1]),
            "deficit_2": len(domains[2]),
            "deficit_3": len(domains[3]),
            "deficit_3_single_diagonal_states": 2,
            "deficit_3_single_diagonal_state_indices": [
                state["state_index"] for state in domains[3]
                if state["type"] == "single_diagonal"
            ],
        },
        "group_matching_audit": group_totals,
        "coverage": {
            "input_support_rows": len(input_rows),
            "input_support_orbit_weight": sum(row["orbit_size"] for row in input_rows),
            "labelled_state_assignments_covered": full_total,
            "assignments_pruned_in_subtrees": pruned_total,
            "locally_port_feasible_assignments": feasible_total,
            "coverage_identity_verified": pruned_total + feasible_total == full_total,
            "locally_port_feasible_support_rows": len(explicit_feasible_rows),
            "independent_partial_nodes_tested": node_total,
            "independent_order_matches_target_order": order_matches,
        },
        "exact_overlap_completions": {
            "total": completion_total,
            "state_Q_histogram": histogram_to_json(aggregate_state_Q),
            "completion_Q_histogram": histogram_to_json(aggregate_completion_Q),
            "Q_at_least_5_states": sum(value for Q, value in aggregate_state_Q.items()
                                       if Q >= 5),
            "Q_at_least_5_completions": Q5_completions,
        },
        "by_partition": {
            key: dict(value) for key, value in sorted(by_partition.items())
        },
        "target_exact_matches": {
            "all_249_census_rows": True,
            "all_175_feasible_state_sets_and_Q_values": True,
            "all_175_completion_totals_and_histograms": True,
        },
        "claim_boundary": (
            "Solver-free finite port and exact overlap-matching census only. "
            "No SAT/CP-SAT negative result is used, and no E0=74 existence or "
            "nonexistence conclusion follows from this audit alone."
        ),
        "rows": independent_rows,
        "errors": errors,
    }
    AUDIT_OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": result["ok"],
        "state_catalog": result["state_catalog"],
        "groups": group_totals,
        "coverage": result["coverage"],
        "completions": result["exact_overlap_completions"],
        "error_count": len(errors),
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
