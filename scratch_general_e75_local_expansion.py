"""Exact local overlap expansion, filters, and weighted orbits for E0=75."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path

import scratch_general_e75_port_audit as port75
import scratch_general_e79_compression_audit as compression_base
import scratch_general_e79_local_audit as local79
from scratch_general_e78_local_ports_all import group_matchings


PORT_PATH = Path("scratch_general_e75_port_audit.json")
COUNT_PATH = Path("scratch_general_e75_local_completion_counts.json")
OUTPUT_PATH = Path("scratch_general_e75_local_expansion.json")
REP_PATH = Path("scratch_general_e75_local_graph_reps.json")
MODEL_E0 = 75
EXPECTED_SUPPORT_ROWS = 50
EXPECTED_STATE_ASSIGNMENTS = 2380
EXPECTED_OVERLAP_EDGES = 18
EXPECTED_COMPLETIONS = 676864
MIN_Q = None


def part_path(partition_index):
    return Path(f"scratch_general_e75_local_expansion_part_{partition_index:02d}.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def fibre_variant(support, deficit, state_index):
    state = port75.FIBRE_STATES[deficit][state_index]
    bit_rows = tuple(itertools.product((0, 1), repeat=2))
    vertices = tuple(local79.vertex_label(support, bits) for bits in bit_rows)
    internal = frozenset(
        tuple(sorted((vertices[left], vertices[right])))
        for left, right in state["edges"]
    )
    neighbours = local79.neighbour_sets(vertices, internal)
    ports = []
    for vertex in vertices:
        for group in support:
            counts = Counter(
                symbol % 2
                for other in neighbours[vertex]
                for symbol in other
                if symbol // 2 == group
            )
            assert all(counts[sign] <= 1 for sign in (0, 1))
            for sign in (0, 1):
                if counts[sign] == 0:
                    ports.append((vertex, group, sign))
    assert len(ports) == 4 * deficit
    return {
        "vertices": vertices,
        "internal": internal,
        "ports": tuple(ports),
        "type": state["type"],
        "state_index": state_index,
    }


def build_forced_c4_profiles(supports):
    """Precompute every support-level disjoint z profile for one row."""
    answer = []
    for support in supports:
        disjoint = tuple(
            index
            for index, other in enumerate(supports)
            if not set(support) & set(other)
        )
        external_groups = tuple(group for group in local79.GROUPS if group not in support)
        t = tuple(
            sum(group in supports[index] for index in disjoint)
            for group in external_groups
        )
        feasible_profiles = {}
        for a in range(3):
            required = len(disjoint) + a - 2
            profiles = set()
            if required >= 0:
                for values in itertools.product(range(5), repeat=len(disjoint)):
                    if sum(values) != required:
                        continue
                    profiles.add(
                        tuple(
                            sum(
                                value
                                for value, index in zip(values, disjoint)
                                if group in supports[index]
                            )
                            for group in external_groups
                        )
                    )
            feasible_profiles[a] = profiles
        answer.append(
            {
                "external_groups": external_groups,
                "target": t,
                "feasible_profiles": feasible_profiles,
            }
        )
    return tuple(answer)


def forced_c4_support_bp_fast(supports, oriented, graph, profiles):
    """Exact support-aggregate BP feasibility using cached z profiles."""
    support_of = {
        vertex: support
        for support, data in zip(supports, oriented)
        for vertex in data["vertices"]
    }
    neighbours = local79.neighbour_sets(tuple(support_of), graph)
    internal_edges = frozenset(edge for data in oriented for edge in data["internal"])
    for fibre_index, (support, data) in enumerate(zip(supports, oriented)):
        profile = profiles[fibre_index]
        external_groups = profile["external_groups"]
        t = profile["target"]
        feasible_profiles = profile["feasible_profiles"]
        for vertex in data["vertices"]:
            a = sum(
                tuple(sorted((vertex, other))) in internal_edges
                for other in data["vertices"]
                if other != vertex
            )
            overlap_neighbours = tuple(
                other
                for other in neighbours[vertex]
                if support_of[other] != support
                and bool(set(support) & set(support_of[other]))
            )
            s = len(overlap_neighbours)
            assert 2 * a + s == 4
            wanted = tuple(
                target
                - sum(group in support_of[other] for other in overlap_neighbours)
                for group, target in zip(external_groups, t)
            )
            if min(wanted, default=0) < 0 or wanted not in feasible_profiles[a]:
                return False
    return True


def vertices_and_masks(supports):
    vertices = tuple(
        sorted(
            local79.vertex_label(support, bits)
            for support in supports
            for bits in itertools.product((0, 1), repeat=2)
        )
    )
    pair_positions = tuple(itertools.combinations(range(len(vertices)), 2))
    pair_index = {pair: bit for bit, pair in enumerate(pair_positions)}
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}

    def mask_of(edges):
        mask = 0
        for left, right in edges:
            pair = tuple(sorted((vertex_index[left], vertex_index[right])))
            mask |= 1 << pair_index[pair]
        return mask

    def edges_of(mask):
        edges = []
        work = mask
        while work:
            low = work & -work
            left, right = pair_positions[low.bit_length() - 1]
            edges.append([list(vertices[left]), list(vertices[right])])
            work ^= low
        return edges

    return vertices, pair_positions, pair_index, mask_of, edges_of


def weighted_vertex_actions(supports, deficits, vertices, expected_stabilizer):
    weight = dict(zip(supports, deficits))
    used = sorted(set().union(*map(set, supports)))
    index = {vertex: position for position, vertex in enumerate(vertices)}
    preserving = []
    for permutation in compression_base.ALL_GROUP_PERMUTATIONS:
        image_weight = {
            local79.apply_group_perm(support, permutation): deficit
            for support, deficit in weight.items()
        }
        if image_weight == weight:
            preserving.append(permutation)
    assert len(preserving) == expected_stabilizer
    actions = set()
    for permutation in preserving:
        for bits in itertools.product((0, 1), repeat=len(used)):
            flips = dict(zip(used, bits))
            action = []
            for vertex in vertices:
                mapped = tuple(
                    sorted(
                        2 * permutation[symbol // 2]
                        + ((symbol % 2) ^ flips.get(symbol // 2, 0))
                        for symbol in vertex
                    )
                )
                action.append(index[mapped])
            actions.add(tuple(action))
    expected_actions = (
        expected_stabilizer // math.factorial(7 - len(used)) * 2 ** len(used)
    )
    assert len(actions) == expected_actions
    return tuple(sorted(actions)), len(preserving), len(used)


def orbit_representatives(
    supports, deficits, expected_stabilizer, graph_masks, q_by_mask=None
):
    vertices, pair_positions, pair_index, _mask_of, edges_of = vertices_and_masks(supports)
    actions, full_stabilizer, used_groups = weighted_vertex_actions(
        supports, deficits, vertices, expected_stabilizer
    )

    def transform(mask, action):
        answer = 0
        work = mask
        while work:
            low = work & -work
            left, right = pair_positions[low.bit_length() - 1]
            image_pair = tuple(sorted((action[left], action[right])))
            answer |= 1 << pair_index[image_pair]
            work ^= low
        return answer

    graph_set = set(graph_masks)
    assert len(graph_set) == len(graph_masks), "duplicate labelled local graphs"
    remaining = set(graph_set)
    representatives = []
    while remaining:
        seed = min(remaining)
        orbit = {transform(seed, action) for action in actions}
        assert orbit <= graph_set, "weighted symmetry closure failure"
        assert seed == min(orbit)
        q_value = None
        if q_by_mask is not None:
            q_values = {q_by_mask[image] for image in orbit}
            assert len(q_values) == 1, "Q is not invariant under local symmetry"
            q_value = next(iter(q_values))
        remaining.difference_update(orbit)
        record = {
            "mask_hex": hex(seed),
            "orbit_size": len(orbit),
            "edges": edges_of(seed),
        }
        if q_value is not None:
            record["Q"] = q_value
        representatives.append(record)
    assert sum(row["orbit_size"] for row in representatives) == len(graph_set)
    return representatives, len(actions), full_stabilizer, used_groups


def row_key(row):
    return tuple(sorted(row["partition"], reverse=True)), row["compression_orbit_index"]


def assignment_diagonal_count(exceptional, state_indices):
    diagonal_pairs = {frozenset((0, 3)), frozenset((1, 2))}
    return sum(
        frozenset(edge) in diagonal_pairs
        for item, state_index in zip(exceptional, state_indices)
        for edge in port75.FIBRE_STATES[item["deficit"]][state_index]["edges"]
    )


def selected_count(count_row, histogram_key):
    if MIN_Q is None:
        if histogram_key == "completion_Q_histogram":
            return count_row["exact_overlap_completions"]
        return count_row["port_feasible_state_assignments"]
    return sum(
        value
        for key, value in count_row[histogram_key].items()
        if int(key) >= MIN_Q
    )


def audit_row(source, expected_completions):
    supports = tuple(tuple(item["support"]) for item in source["exceptional_supports"])
    deficits = tuple(item["deficit"] for item in source["exceptional_supports"])
    vertices, _pairs, _pair_index, mask_of, _edges_of = vertices_and_masks(supports)
    fibre_of = {
        local79.vertex_label(support, bits): index
        for index, support in enumerate(supports)
        for bits in itertools.product((0, 1), repeat=2)
    }
    forced_profiles = build_forced_c4_profiles(supports)
    completions = 0
    spectral = 0
    pair_upper = 0
    forced_bp = 0
    actual_square_histogram = Counter()
    spectral_square_histogram = Counter()
    pair_square_histogram = Counter()
    forced_square_histogram = Counter()
    state_q_histogram = Counter()
    completion_q_histogram = Counter()
    spectral_q_histogram = Counter()
    pair_q_histogram = Counter()
    forced_q_histogram = Counter()
    forced_masks = []
    q_by_mask = {}
    old_bp_direct_controls = 0
    for state_indices in source["feasible_state_indices"]:
        q_value = assignment_diagonal_count(source["exceptional_supports"], state_indices)
        if MIN_Q is not None and q_value < MIN_Q:
            continue
        state_q_histogram[q_value] += 1
        oriented = tuple(
            fibre_variant(support, deficit, state_index)
            for support, deficit, state_index in zip(supports, deficits, state_indices)
        )
        by_group = tuple(group_matchings(oriented, group) for group in local79.GROUPS)
        product_count = math.prod(len(choices) for choices in by_group)
        assert product_count
        completion_q_histogram[q_value] += product_count
        internal = frozenset(edge for data in oriented for edge in data["internal"])
        for selected in itertools.product(*by_group):
            completions += 1
            overlap = frozenset(edge for group_edges in selected for edge in group_edges)
            assert len(overlap) == EXPECTED_OVERLAP_EDGES
            block_counts = Counter(
                tuple(sorted((fibre_of[left], fibre_of[right])))
                for left, right in overlap
            )
            m2 = sum(value * value for value in block_counts.values())
            actual_square_histogram[m2] += 1
            if m2 + Fraction(source["disjoint_continuous_minimum"]) > source[
                "joint_square_budget"
            ]:
                continue
            spectral += 1
            spectral_q_histogram[q_value] += 1
            spectral_square_histogram[m2] += 1
            graph = internal | overlap
            if not local79.induced_pair_upper(vertices, graph):
                continue
            pair_upper += 1
            pair_q_histogram[q_value] += 1
            pair_square_histogram[m2] += 1
            fast = forced_c4_support_bp_fast(supports, oriented, graph, forced_profiles)
            if not fast:
                continue
            if old_bp_direct_controls == 0:
                assert local79.induced_pair_upper(vertices, graph)
                from scratch_general_e78_local_ports_all import forced_c4_support_bp_feasible

                assert forced_c4_support_bp_feasible(supports, oriented, graph)
                old_bp_direct_controls += 1
            forced_bp += 1
            forced_q_histogram[q_value] += 1
            forced_square_histogram[m2] += 1
            graph_mask = mask_of(graph)
            if graph_mask in q_by_mask:
                assert q_by_mask[graph_mask] == q_value
            else:
                q_by_mask[graph_mask] = q_value
            forced_masks.append(graph_mask)
    assert completions == expected_completions
    representatives = []
    action_count = None
    full_stabilizer = source["weighted_stabilizer_order"]
    used_groups = len(set().union(*map(set, supports)))
    if forced_masks:
        representatives, action_count, full_stabilizer, used_groups = orbit_representatives(
            supports,
            deficits,
            source["weighted_stabilizer_order"],
            forced_masks,
            q_by_mask,
        )
    return {
        "partition": source["partition"],
        "compression_orbit_index": source["compression_orbit_index"],
        "support_orbit_size": source["support_orbit_size"],
        "weighted_stabilizer_order": full_stabilizer,
        "used_root_groups": used_groups,
        "exceptional_supports": source["exceptional_supports"],
        "input_port_feasible_state_assignments": source["locally_port_feasible_assignments"],
        "port_feasible_state_assignments": sum(state_q_histogram.values()),
        "Q_condition": None if MIN_Q is None else f"Q>={MIN_Q}",
        "state_Q_histogram": {
            str(key): value for key, value in sorted(state_q_histogram.items())
        },
        "exact_overlap_completions": completions,
        "completion_Q_histogram": {
            str(key): value for key, value in sorted(completion_q_histogram.items())
        },
        "actual_overlap_square_histogram": {
            str(key): value for key, value in sorted(actual_square_histogram.items())
        },
        "after_exact_real_spectral_bound": spectral,
        "spectral_Q_histogram": {
            str(key): value for key, value in sorted(spectral_q_histogram.items())
        },
        "spectral_overlap_square_histogram": {
            str(key): value for key, value in sorted(spectral_square_histogram.items())
        },
        "after_induced_pair_upper": pair_upper,
        "pair_Q_histogram": {
            str(key): value for key, value in sorted(pair_q_histogram.items())
        },
        "pair_overlap_square_histogram": {
            str(key): value for key, value in sorted(pair_square_histogram.items())
        },
        "after_forced_C4_support_BP": forced_bp,
        "forced_BP_Q_histogram": {
            str(key): value for key, value in sorted(forced_q_histogram.items())
        },
        "forced_BP_overlap_square_histogram": {
            str(key): value for key, value in sorted(forced_square_histogram.items())
        },
        "old_forced_BP_direct_controls": old_bp_direct_controls,
        "distinct_local_symmetry_actions": action_count,
        "local_graph_orbits": len(representatives),
        "orbit_size_histogram": {
            str(key): value
            for key, value in sorted(
                Counter(row["orbit_size"] for row in representatives).items()
            )
        },
        "local_graph_representatives": representatives,
    }


def input_rows():
    port = json.loads(PORT_PATH.read_text(encoding="utf-8"))
    counts = json.loads(COUNT_PATH.read_text(encoding="utf-8"))
    rows = [row for row in port["rows"] if row["locally_port_feasible_assignments"]]
    count_map = {row_key(row): row for row in counts["rows"]}
    assert len(count_map) == len(rows)
    if MIN_Q is not None:
        rows = [
            row for row in rows
            if selected_count(count_map[row_key(row)], "completion_Q_histogram")
        ]
    assert len(rows) == EXPECTED_SUPPORT_ROWS
    partition_index = {
        tuple(part["partition"]): part["partition_index"] for part in port["by_partition"]
    }
    grouped = {}
    for row in rows:
        index = partition_index[tuple(row["partition"])]
        grouped.setdefault(index, []).append((row, count_map[row_key(row)]))
    return port, grouped


def summarize(rows):
    histogram_names = (
        "state_Q_histogram",
        "completion_Q_histogram",
        "spectral_Q_histogram",
        "pair_Q_histogram",
        "forced_BP_Q_histogram",
    )
    q_histograms = {name: Counter() for name in histogram_names}
    for row in rows:
        for name in histogram_names:
            q_histograms[name].update(
                {int(key): value for key, value in row[name].items()}
            )
    return {
        "support_rows": len(rows),
        "port_feasible_state_assignments": sum(
            row["port_feasible_state_assignments"] for row in rows
        ),
        "exact_overlap_completions": sum(row["exact_overlap_completions"] for row in rows),
        "after_exact_real_spectral_bound": sum(
            row["after_exact_real_spectral_bound"] for row in rows
        ),
        "after_induced_pair_upper": sum(row["after_induced_pair_upper"] for row in rows),
        "after_forced_C4_support_BP": sum(
            row["after_forced_C4_support_BP"] for row in rows
        ),
        "nonempty_support_rows": sum(row["after_forced_C4_support_BP"] > 0 for row in rows),
        "local_graph_orbits": sum(row["local_graph_orbits"] for row in rows),
        **{
            name: {str(key): value for key, value in sorted(histogram.items())}
            for name, histogram in q_histograms.items()
        },
    }


def run_partition(partition_index, force=False):
    _port, grouped = input_rows()
    rows_in = grouped.get(partition_index, [])
    path = part_path(partition_index)
    if path.exists() and not force:
        result = json.loads(path.read_text(encoding="utf-8"))
        if result["status"] == "COMPLETE":
            print(json.dumps({"phase": "resume", "partition_index": partition_index, "status": "COMPLETE"}), flush=True)
            return result
        completed = {row["compression_orbit_index"] for row in result["rows"]}
    else:
        result = {
            "status": "EXPANDING",
            "model": f"checkpointed exact E0={MODEL_E0} local overlap expansion",
            "partition_index": partition_index,
            "partition": rows_in[0][0]["partition"] if rows_in else None,
            "rows": [],
        }
        completed = set()
        atomic_json(path, result)
    for offset, (source, count_row) in enumerate(rows_in):
        if source["compression_orbit_index"] in completed:
            continue
        record = audit_row(
            source, selected_count(count_row, "completion_Q_histogram")
        )
        result["rows"].append(record)
        result["summary"] = summarize(result["rows"])
        atomic_json(path, result)
        print(
            json.dumps(
                {
                    "partition_index": partition_index,
                    "offset": offset,
                    "compression_orbit_index": record["compression_orbit_index"],
                    "completions": record["exact_overlap_completions"],
                    "spectral": record["after_exact_real_spectral_bound"],
                    "pair": record["after_induced_pair_upper"],
                    "BP": record["after_forced_C4_support_BP"],
                    "orbits": record["local_graph_orbits"],
                }
            ),
            flush=True,
        )
    assert len(result["rows"]) == len(rows_in)
    result["status"] = "COMPLETE"
    result["summary"] = summarize(result["rows"])
    atomic_json(path, result)
    return result


def merge():
    _port, grouped = input_rows()
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
        "model": f"solver-free exact E0={MODEL_E0} local overlap expansion and weighted orbits",
        "inputs": [str(PORT_PATH), str(COUNT_PATH)],
        "coverage": (
            f"all exact overlap completions of all {EXPECTED_STATE_ASSIGNMENTS} "
            f"port-feasible labelled fibre states on all {EXPECTED_SUPPORT_ROWS} support rows"
        ),
        "Q_condition": None if MIN_Q is None else f"Q>={MIN_Q}",
        "filter_order": [
            "actual overlap square plus exact-real disjoint least-norm bound",
            "induced exceptional-low-vertex pair upper bound",
            "ordinary-C4 forced support-aggregate BP feasibility",
        ],
        "symmetry": (
            "weighted support->deficit stabilizer times every used-group bit flip; "
            "closure, graph uniqueness, canonical minimum, and orbit-size sums asserted"
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
    }
    assert result["summary"]["support_rows"] == EXPECTED_SUPPORT_ROWS
    assert result["summary"]["port_feasible_state_assignments"] == EXPECTED_STATE_ASSIGNMENTS
    assert result["summary"]["exact_overlap_completions"] == EXPECTED_COMPLETIONS
    atomic_json(OUTPUT_PATH, result)
    rep_result = {
        "status": "COMPLETE",
        "model": f"canonical explicit E0={MODEL_E0} local graph representatives",
        "input": str(OUTPUT_PATH),
        "vertex_label": (
            "a low vertex is [2*g_a+bit_a,2*g_b+bit_b] on support {g_a,g_b}"
        ),
        "symmetry": result["symmetry"],
        "raw_graphs": result["summary"]["after_forced_C4_support_BP"],
        "local_graph_orbits": result["summary"]["local_graph_orbits"],
        "support_rows": [
            {
                "partition": row["partition"],
                "compression_orbit_index": row["compression_orbit_index"],
                "exceptional_supports": row["exceptional_supports"],
                "weighted_stabilizer_order": row["weighted_stabilizer_order"],
                "used_root_groups": row["used_root_groups"],
                "symmetry_actions": row["distinct_local_symmetry_actions"],
                "raw_survivors": row["after_forced_C4_support_BP"],
                "orbit_count": row["local_graph_orbits"],
                "orbit_size_histogram": row["orbit_size_histogram"],
                "representatives": row["local_graph_representatives"],
            }
            for row in rows
            if row["after_forced_C4_support_BP"]
        ],
    }
    assert sum(row["raw_survivors"] for row in rep_result["support_rows"]) == rep_result[
        "raw_graphs"
    ]
    assert sum(row["orbit_count"] for row in rep_result["support_rows"]) == rep_result[
        "local_graph_orbits"
    ]
    atomic_json(REP_PATH, rep_result)
    print(json.dumps({"status": result["status"], **result["summary"]}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition-index", type=int)
    parser.add_argument("--partition-indices", type=str)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    selected = sum(
        (
            args.partition_index is not None,
            args.partition_indices is not None,
            args.all,
            args.merge,
        )
    )
    if selected != 1:
        parser.error("choose exactly one mode")
    if args.partition_index is not None:
        run_partition(args.partition_index, args.force)
    elif args.partition_indices is not None:
        for index in (int(value) for value in args.partition_indices.split(",")):
            run_partition(index, args.force)
    elif args.all:
        _port, grouped = input_rows()
        for index in sorted(grouped):
            run_partition(index, args.force)
    else:
        merge()


if __name__ == "__main__":
    main()
