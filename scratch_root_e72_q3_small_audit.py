"""Independent audit of the completed small E72,Q>=3 local/SAT snapshot.

This audit deliberately leaves the eleven larger/unfinished partition classes
out of scope.  It checks the global port/count census, all arithmetic and
orbit identities in the eleven completed local-expansion parts, reconstructs
and validates every surviving representative from its edge list, rebuilds the
three support-specific exact CNFs and all complete assumption vectors, and
binds the sole initial UNKNOWN to its deeper terminal CaDiCaL run.

The solver answers are computational evidence.  No DRAT/LRAT proof is claimed.
"""

from __future__ import annotations

import copy
import gc
import hashlib
import itertools
import json
import math
import os
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import scratch_general_e72_q3_local_expansion as e72_expansion
import scratch_general_e79_local_audit as local79
from scratch_general_exact_sat import coordinates
from scratch_general_e78_local_ports_all import (
    forced_c4_support_bp_feasible,
    group_matchings,
)
from scratch_incremental_local_exact_sat import build_shared_cnf, normalize_source


PORT = Path("scratch_general_e72_q3_port_feasible_states.json")
COUNTS = Path("scratch_general_e72_q3_local_completion_counts.json")
NORMALIZED = Path("scratch_general_e72_q3_incremental_small_records.json")
DEEP_INPUT = Path("scratch_general_e72_q3_unknown_branch2_record.json")
DEEP_CHECKPOINT = Path("scratch_general_e72_q3_unknown_branch2_c200000.json")
MERGED_CHECKPOINT = Path("scratch_general_e72_q3_small_record00_sat_merged.json")
OUTPUT = Path("scratch_root_e72_q3_small_audit.json")
SUMMARY = Path("scratch_root_e72_q3_small_audit.md")

PARTITIONS = (10, 12, 15, 17, 18, 19, 20, 22, 23, 24, 25)
CHECKPOINTS = (
    Path("scratch_general_e72_q3_small_record00_sat.json"),
    Path("scratch_general_e72_q3_small_record01_sat.json"),
    Path("scratch_general_e72_q3_small_record02_sat.json"),
)
EXPECTED_GLOBAL_COUNTS = (377, 15586, 1018392576)
EXPECTED_SMALL_TOTALS = (68, 2140, 6926336, 6926336, 1714856, 24576, 3, 584)
EXPECTED_INITIAL_SAT = (553, 30, 1, 0)
FIBRE_BITS = tuple(itertools.product((0, 1), repeat=2))
FIBRE_DIAGONALS = frozenset(
    pair
    for pair in itertools.combinations(range(4), 2)
    if all(FIBRE_BITS[pair[0]][axis] != FIBRE_BITS[pair[1]][axis]
           for axis in (0, 1))
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def int_counter(raw: dict) -> Counter:
    return Counter({int(key): int(value) for key, value in raw.items()})


def json_counter(counter: Counter) -> dict:
    return {str(key): value for key, value in sorted(counter.items()) if value}


def json_normalized(value):
    """Apply JSON's key/string normalization before stored/rebuilt comparison."""
    return json.loads(json.dumps(value))


def row_key(row: dict) -> tuple:
    return tuple(sorted(map(int, row["partition"]), reverse=True)), int(
        row["compression_orbit_index"]
    )


def clauses_sha256(clauses: list[list[int]]) -> str:
    """Hash clauses in deterministic DIMACS-line order (without a header)."""
    digest = hashlib.sha256()
    for clause in clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    return digest.hexdigest().upper()


def summarize_count_rows(rows: list[dict]) -> dict:
    state_q = Counter()
    completion_q = Counter()
    for row in rows:
        state_q.update(int_counter(row["state_Q_histogram"]))
        completion_q.update(int_counter(row["completion_Q_histogram"]))
    return {
        "support_rows": len(rows),
        "port_feasible_state_assignments": sum(
            int(row["port_feasible_state_assignments"]) for row in rows
        ),
        "exact_overlap_completions": sum(
            int(row["exact_overlap_completions"]) for row in rows
        ),
        "maximum_per_support_row": max(
            (int(row["exact_overlap_completions"]) for row in rows), default=0
        ),
        "state_Q_histogram": json_counter(state_q),
        "completion_Q_histogram": json_counter(completion_q),
        "conditional_priority_Q_at_least_5_states": sum(
            value for q, value in state_q.items() if q >= 5
        ),
        "conditional_priority_Q_at_least_5_completions": sum(
            value for q, value in completion_q.items() if q >= 5
        ),
    }


def summarize_expansion_rows(rows: list[dict]) -> dict:
    histogram_names = (
        "state_Q_histogram",
        "completion_Q_histogram",
        "spectral_Q_histogram",
        "pair_Q_histogram",
        "forced_BP_Q_histogram",
    )
    histograms = {name: Counter() for name in histogram_names}
    for row in rows:
        for name in histogram_names:
            histograms[name].update(int_counter(row[name]))
    return {
        "support_rows": len(rows),
        "port_feasible_state_assignments": sum(
            int(row["port_feasible_state_assignments"]) for row in rows
        ),
        "exact_overlap_completions": sum(
            int(row["exact_overlap_completions"]) for row in rows
        ),
        "after_exact_real_spectral_bound": sum(
            int(row["after_exact_real_spectral_bound"]) for row in rows
        ),
        "after_induced_pair_upper": sum(
            int(row["after_induced_pair_upper"]) for row in rows
        ),
        "after_forced_C4_support_BP": sum(
            int(row["after_forced_C4_support_BP"]) for row in rows
        ),
        "nonempty_support_rows": sum(
            int(row["after_forced_C4_support_BP"]) > 0 for row in rows
        ),
        "local_graph_orbits": sum(int(row["local_graph_orbits"]) for row in rows),
        **{name: json_counter(histogram) for name, histogram in histograms.items()},
    }


def masks_and_actions(supports, deficits, vertices):
    """Rebuild the full faithful residual action without producer helpers."""
    pair_positions = tuple(itertools.combinations(range(len(vertices)), 2))
    pair_index = {pair: bit for bit, pair in enumerate(pair_positions)}
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}

    def graph_mask(graph):
        mask = 0
        for left, right in graph:
            pair = tuple(sorted((vertex_index[left], vertex_index[right])))
            mask |= 1 << pair_index[pair]
        return mask

    weight = dict(zip(supports, deficits))
    used = sorted(set().union(*map(set, supports)))
    actions = set()
    preserving = 0
    for permutation in itertools.permutations(range(7)):
        image_weight = {
            tuple(sorted((permutation[a], permutation[b]))): deficit
            for (a, b), deficit in weight.items()
        }
        if image_weight != weight:
            continue
        preserving += 1
        for flip_bits in itertools.product((0, 1), repeat=len(used)):
            flips = dict(zip(used, flip_bits))
            action = []
            for vertex in vertices:
                image = tuple(
                    sorted(
                        2 * permutation[symbol // 2]
                        + ((symbol % 2) ^ flips.get(symbol // 2, 0))
                        for symbol in vertex
                    )
                )
                action.append(vertex_index[image])
            actions.add(tuple(action))

    def image_masks(graph):
        mask = graph_mask(graph)
        images = set()
        for action in actions:
            work = mask
            image = 0
            while work:
                low = work & -work
                left, right = pair_positions[low.bit_length() - 1]
                image_pair = tuple(sorted((action[left], action[right])))
                image |= 1 << pair_index[image_pair]
                work ^= low
            images.add(image)
        return mask, images

    return graph_mask, image_masks, len(actions), preserving, len(used)


def audit_counts(port: dict, counts: dict) -> dict:
    assert port["status"] == "COMPLETE"
    assert counts["status"] == "COMPLETE"
    assert counts["input"] == str(PORT)
    observed_global = (
        int(counts["summary"]["support_rows"]),
        int(counts["summary"]["port_feasible_state_assignments"]),
        int(counts["summary"]["exact_overlap_completions"]),
    )
    assert observed_global == EXPECTED_GLOBAL_COUNTS
    assert int(port["summary"]["support_rows"]) == EXPECTED_GLOBAL_COUNTS[0]
    assert int(port["summary"]["feasible_state_assignments"]) == EXPECTED_GLOBAL_COUNTS[1]

    port_rows = {row_key(row): row for row in port["rows"]}
    count_rows = {row_key(row): row for row in counts["rows"]}
    assert len(port_rows) == len(count_rows) == EXPECTED_GLOBAL_COUNTS[0]
    assert set(port_rows) == set(count_rows)
    for key, row in count_rows.items():
        source = port_rows[key]
        states = int(row["port_feasible_state_assignments"])
        assert states == int(source["locally_port_feasible_assignments"])
        assert states == len(source["feasible_state_indices"])
        assert int_counter(row["state_Q_histogram"]) == int_counter(
            source["feasible_Q_histogram"]
        )
        completion_hist = int_counter(row["completion_count_histogram"])
        assert sum(completion_hist.values()) == states
        assert sum(count * multiplicity for count, multiplicity in completion_hist.items()) == int(
            row["exact_overlap_completions"]
        )
        assert max(completion_hist, default=0) == int(row["maximum_completions_for_one_state"])
        assert sum(int_counter(row["completion_Q_histogram"]).values()) == int(
            row["exact_overlap_completions"]
        )
        assert sum(int_counter(row["state_Q_histogram"]).values()) == states
        assert all(
            sum(int_counter(histogram).values()) == states
            for histogram in row["group_matching_count_histograms"]
        )
        control = row["first_state_count_control"]
        assert control["state_indices"] == source["feasible_state_indices"][0]
        assert math.prod(control["exact_matching_counts_by_group"]) == int(
            control["completion_product"]
        )
        state_q = int_counter(row["state_Q_histogram"])
        completion_q = int_counter(row["completion_Q_histogram"])
        assert int(row["conditional_priority_Q_at_least_5_states"]) == sum(
            value for q, value in state_q.items() if q >= 5
        )
        assert int(row["conditional_priority_Q_at_least_5_completions"]) == sum(
            value for q, value in completion_q.items() if q >= 5
        )

    assert summarize_count_rows(list(count_rows.values())) == counts["summary"]
    grouped = defaultdict(list)
    for row in counts["rows"]:
        grouped[tuple(row["partition"])].append(row)
    part_hashes = []
    for part in counts["by_partition"]:
        rows = grouped[tuple(part["partition"])]
        expected = {
            key: value for key, value in part.items()
            if key not in ("partition_index", "partition", "artifact")
        }
        assert summarize_count_rows(rows) == expected
        artifact = Path(part["artifact"])
        document = json.loads(artifact.read_text(encoding="utf-8"))
        assert document["status"] == "COMPLETE"
        assert document["partition_index"] == part["partition_index"]
        assert document["partition"] == part["partition"]
        assert document["summary"] == expected
        assert document["rows"] == rows
        part_hashes.append({
            "partition_index": part["partition_index"],
            "path": str(artifact),
            "sha256": sha256(artifact),
        })
    return {
        "support_rows": observed_global[0],
        "port_feasible_state_assignments": observed_global[1],
        "exact_overlap_completions": observed_global[2],
        "state_Q_histogram": counts["summary"]["state_Q_histogram"],
        "completion_Q_histogram": counts["summary"]["completion_Q_histogram"],
        "count_partitions_checked": len(part_hashes),
        "count_partition_artifacts": part_hashes,
    }


def audit_expansion_parts(counts: dict) -> tuple[dict, list[dict], dict]:
    count_rows = {row_key(row): row for row in counts["rows"]}
    all_rows = []
    parts = []
    row_locations = {}
    for partition_index in PARTITIONS:
        path = Path(f"scratch_general_e72_q3_local_expansion_part_{partition_index:02d}.json")
        document = json.loads(path.read_text(encoding="utf-8"))
        assert document["status"] == "COMPLETE"
        assert document["partition_index"] == partition_index
        assert document["summary"] == summarize_expansion_rows(document["rows"])
        for source_row_index, row in enumerate(document["rows"]):
            key = row_key(row)
            assert key in count_rows and key not in row_locations
            count = count_rows[key]
            assert row["exceptional_supports"] == count["exceptional_supports"]
            assert row["partition"] == count["partition"]
            assert row["support_orbit_size"] == count["support_orbit_size"]
            assert row["weighted_stabilizer_order"] == count["weighted_stabilizer_order"]
            assert row["input_port_feasible_state_assignments"] == count[
                "port_feasible_state_assignments"
            ]
            assert row["port_feasible_state_assignments"] == count[
                "port_feasible_state_assignments"
            ]
            assert row["state_Q_histogram"] == count["state_Q_histogram"]
            assert row["exact_overlap_completions"] == count["exact_overlap_completions"]
            assert row["completion_Q_histogram"] == count["completion_Q_histogram"]
            stages = (
                int(row["exact_overlap_completions"]),
                int(row["after_exact_real_spectral_bound"]),
                int(row["after_induced_pair_upper"]),
                int(row["after_forced_C4_support_BP"]),
            )
            assert stages[0] >= stages[1] >= stages[2] >= stages[3]
            assert sum(int_counter(row["actual_overlap_square_histogram"]).values()) == stages[0]
            assert sum(int_counter(row["spectral_Q_histogram"]).values()) == stages[1]
            assert sum(int_counter(row["spectral_overlap_square_histogram"]).values()) == stages[1]
            assert sum(int_counter(row["pair_Q_histogram"]).values()) == stages[2]
            assert sum(int_counter(row["pair_overlap_square_histogram"]).values()) == stages[2]
            assert sum(int_counter(row["forced_BP_Q_histogram"]).values()) == stages[3]
            assert sum(int_counter(row["forced_BP_overlap_square_histogram"]).values()) == stages[3]
            assert int(row["local_graph_orbits"]) == len(row["local_graph_representatives"])
            orbit_hist = int_counter(row["orbit_size_histogram"])
            assert sum(orbit_hist.values()) == int(row["local_graph_orbits"])
            assert sum(size * multiplicity for size, multiplicity in orbit_hist.items()) == stages[3]
            assert sum(int(rep["orbit_size"]) for rep in row["local_graph_representatives"]) == stages[3]
            assert int(row["old_forced_BP_direct_controls"]) == int(stages[3] > 0)
            row_locations[key] = (partition_index, source_row_index, row, path)
        all_rows.extend(document["rows"])
        parts.append({
            "partition_index": partition_index,
            "path": str(path),
            "sha256": sha256(path),
            **document["summary"],
        })

    totals = summarize_expansion_rows(all_rows)
    observed = tuple(totals[key] for key in (
        "support_rows", "port_feasible_state_assignments", "exact_overlap_completions",
        "after_exact_real_spectral_bound", "after_induced_pair_upper",
        "after_forced_C4_support_BP", "nonempty_support_rows", "local_graph_orbits",
    ))
    assert observed == EXPECTED_SMALL_TOTALS
    return totals, parts, row_locations


def audit_representatives(port: dict, normalized: dict, row_locations: dict) -> dict:
    e72_expansion.configure()
    expansion = e72_expansion.generic
    labels, label_index, _variables, _edge = coordinates()
    port_rows = {row_key(row): row for row in port["rows"]}
    surviving = [
        location for location in row_locations.values()
        if int(location[2]["after_forced_C4_support_BP"]) > 0
    ]
    assert normalized["status"] == "E72_QGE3_PARTIAL_SNAPSHOT"
    assert all(row["status"] == "COMPLETE" for row in normalized["input_status"])
    assert [row["partition_index"] for row in normalized["input_status"]] == list(PARTITIONS)
    assert len(surviving) == normalized["support_record_count"] == 3
    assert normalized["local_representative_count"] == 584
    assert normalized["labelled_local_graphs_represented"] == 24576

    checked_rows = []
    total_orbits = 0
    total_raw = 0
    all_canonical_keys = set()
    normalized_by_source = {
        (int(record["source_partition_index"]), int(record["source_row_index"])): record
        for record in normalized["records"]
    }
    assert len(normalized_by_source) == 3

    for partition_index, source_row_index, row, source_path in sorted(surviving):
        norm = normalized_by_source[(partition_index, source_row_index)]
        assert norm["source_artifact"] == str(source_path)
        assert norm["compression_orbit_index"] == row["compression_orbit_index"]
        assert norm["partition"] == row["partition"]
        assert norm["local_graph_count"] == row["after_forced_C4_support_BP"]
        assert norm["orbit_count_direct"] == row["local_graph_orbits"]
        assert norm["orbit_sizes"] == [
            rep["orbit_size"] for rep in row["local_graph_representatives"]
        ]
        assert norm["Q_histogram"] == row["forced_BP_Q_histogram"]

        supports = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
        deficits = tuple(int(item["deficit"]) for item in row["exceptional_supports"])
        assert sum(deficits) == 12
        assert norm["supports_in_fibre_order"] == [list(value) for value in supports]
        assert norm["deficits_in_support_order"] == list(deficits)
        vertices = tuple(sorted(
            local79.vertex_label(support, bits)
            for support in supports for bits in FIBRE_BITS
        ))
        expected_outer_vertices = {
            index for index, label in enumerate(labels)
            if tuple(sorted((label[0] // 2, label[1] // 2))) in set(supports)
        }
        assert {item["outer_index_zero_based"] for item in norm["local_vertex_order"]} == expected_outer_vertices
        graph_mask, image_masks, action_count, preserving, used_groups = masks_and_actions(
            supports, deficits, vertices
        )
        assert preserving == row["weighted_stabilizer_order"]
        assert action_count == row["distinct_local_symmetry_actions"]
        assert action_count == preserving // math.factorial(7 - used_groups) * 2 ** used_groups
        profiles = expansion.build_forced_c4_profiles(supports)
        port_row = port_rows[row_key(row)]
        canonical_seen = set()
        orbit_union = set()
        orbit_hist = Counter()
        q_raw = Counter()
        square_raw = Counter()

        assert len(norm["representatives"]) == len(row["local_graph_representatives"])
        for representative_index, (representative, norm_rep) in enumerate(zip(
            row["local_graph_representatives"], norm["representatives"]
        )):
            assert norm_rep["representative_id"] == representative_index
            assert norm_rep["source_mask_hex"] == representative["mask_hex"]
            assert norm_rep["orbit_size"] == representative["orbit_size"]
            assert norm_rep["Q"] == representative["Q"]
            graph = frozenset(
                tuple(sorted((tuple(left), tuple(right))))
                for left, right in representative["edges"]
            )
            assert len(graph) == len(representative["edges"])
            assert all(left in vertices and right in vertices for left, right in graph)
            expected_index_edges = {
                tuple(sorted((label_index[left], label_index[right]))) for left, right in graph
            }
            assert expected_index_edges == {
                tuple(edge) for edge in norm_rep["present_edges_outer_indices_zero_based"]
            }

            oriented = []
            q_value = 0
            for support, deficit in zip(supports, deficits):
                fibre_vertices = frozenset(
                    local79.vertex_label(support, bits) for bits in FIBRE_BITS
                )
                internal = frozenset(
                    edge for edge in graph
                    if edge[0] in fibre_vertices and edge[1] in fibre_vertices
                )
                candidates = [
                    expansion.fibre_variant(support, deficit, state_index)
                    for state_index in range(len(expansion.port75.FIBRE_STATES[deficit]))
                    if expansion.fibre_variant(support, deficit, state_index)["internal"] == internal
                ]
                assert len(candidates) == 1
                oriented.append(candidates[0])
                state = expansion.port75.FIBRE_STATES[deficit][candidates[0]["state_index"]]
                q_value += sum(tuple(edge) in FIBRE_DIAGONALS for edge in state["edges"])
            oriented = tuple(oriented)
            assert q_value == representative["Q"] >= 3
            internal = frozenset(edge for data in oriented for edge in data["internal"])
            overlap = graph - internal
            assert len(internal) == 4 * len(supports) - 12
            assert len(overlap) == 24
            support_of = {
                vertex: support
                for support, data in zip(supports, oriented)
                for vertex in data["vertices"]
            }
            assigned = set()
            for group in range(7):
                group_edges = frozenset(
                    edge for edge in overlap
                    if group in set(support_of[edge[0]]) & set(support_of[edge[1]])
                )
                assert group_edges in group_matchings(oriented, group)
                assigned.update(group_edges)
            assert assigned == set(overlap)
            assert local79.induced_pair_upper(vertices, graph)
            assert forced_c4_support_bp_feasible(supports, oriented, graph)
            assert expansion.forced_c4_support_bp_fast(supports, oriented, graph, profiles)
            fibre_of = {
                vertex: index
                for index, data in enumerate(oriented) for vertex in data["vertices"]
            }
            blocks = Counter(
                tuple(sorted((fibre_of[left], fibre_of[right]))) for left, right in overlap
            )
            m2 = sum(value * value for value in blocks.values())
            assert m2 + Fraction(port_row["disjoint_continuous_minimum"]) <= int(
                port_row["joint_square_budget"]
            )
            mask, images = image_masks(graph)
            assert mask == graph_mask(graph) == int(representative["mask_hex"], 16)
            assert mask == min(images)
            assert len(images) == int(representative["orbit_size"])
            assert mask not in canonical_seen
            assert not (orbit_union & images)
            canonical_seen.add(mask)
            orbit_union.update(images)
            orbit_hist[len(images)] += 1
            q_raw[q_value] += len(images)
            square_raw[m2] += len(images)
            intrinsic = (tuple(sorted(deficits, reverse=True)), row["compression_orbit_index"], mask)
            assert intrinsic not in all_canonical_keys
            all_canonical_keys.add(intrinsic)

        raw = len(orbit_union)
        assert raw == int(row["after_forced_C4_support_BP"])
        assert len(canonical_seen) == int(row["local_graph_orbits"])
        assert json_counter(orbit_hist) == row["orbit_size_histogram"]
        assert json_counter(q_raw) == row["forced_BP_Q_histogram"]
        assert json_counter(square_raw) == row["forced_BP_overlap_square_histogram"]
        total_raw += raw
        total_orbits += len(canonical_seen)
        checked_rows.append({
            "partition_index": partition_index,
            "source_row_index": source_row_index,
            "compression_orbit_index": row["compression_orbit_index"],
            "representatives": len(canonical_seen),
            "raw_graphs": raw,
            "symmetry_actions": action_count,
            "orbit_size_histogram": json_counter(orbit_hist),
            "Q_histogram": json_counter(q_raw),
            "overlap_square_histogram": json_counter(square_raw),
        })

    assert total_orbits == 584
    assert total_raw == 24576
    return {
        "support_records": len(checked_rows),
        "representatives": total_orbits,
        "labelled_local_graphs": total_raw,
        "checks": [
            "edge-list uniqueness and normalized outer-index equality",
            "unique fibre-state reconstruction and exact 24-edge port matchings",
            "induced-pair upper bound",
            "forced ordinary-C4 support BP by original and optimized routines",
            "exact-real spectral inequality",
            "full residual-action canonicality, disjointness, and orbit weights",
        ],
        "rows": checked_rows,
    }


def audit_checkpoint(path: Path, record_index: int, normalized: dict) -> tuple[dict, dict]:
    source = normalize_source(NORMALIZED, record_index)
    clauses, _edge, _variables, _full, branches, meta = build_shared_cnf(source)
    cnf_hash = clauses_sha256(clauses)
    checkpoint = json.loads(path.read_text(encoding="utf-8"))
    assert checkpoint["checkpoint_complete"] is True
    assert checkpoint["input"] == str(NORMALIZED)
    assert checkpoint["input_selection"] == source["selection"]
    assert checkpoint["shared_cnf_meta"] == json_normalized(meta)
    assert checkpoint["conflict_budget_per_branch"] == 20000
    assert checkpoint["reference_portfolios"] == []
    assert checkpoint["all_available_reference_statuses_match"] is None
    assert len(checkpoint["records"]) == len(branches)
    assert [row["branch_index"] for row in checkpoint["records"]] == list(range(len(branches)))
    assert meta["bp_equalities"] == 1176
    assert meta["outer_pair_equalities"] == 3486
    assert meta["disjoint_blocks"] == 105
    assert meta["disjoint_edge_variables"] == 1680
    assert meta["redundant_support_aggregate_rows"] == 0
    assert meta["empty_clauses_before_assumptions"] == 0

    branch_by_index = {branch["branch_index"]: branch for branch in branches}
    record_by_index = {record["branch_index"]: record for record in checkpoint["records"]}
    status_counts = Counter()
    for record in checkpoint["records"]:
        branch = branch_by_index[record["branch_index"]]
        representative = normalized["records"][record_index]["representatives"][record["branch_index"]]
        assumptions = frozenset(branch["assumptions"])
        assert record["representative_id"] == representative["representative_id"]
        assert record["orbit_size"] == representative["orbit_size"]
        assert record["assumption_sha256"] == branch["assumption_sha256"]
        assert record["assumption_count"] == len(assumptions) == meta["local_edge_variables"]
        assert record["positive_assumptions"] == len(
            representative["present_edges_outer_indices_zero_based"]
        )
        assert record["positive_assumptions"] + record["negative_assumptions"] == len(assumptions)
        assert record.get("formal_proof_certificate") is None
        status_counts[record["status"]] += 1
        if record["status"] == "UNSAT":
            assert record["logical_status"] == "UNSAT"
            assert record["resolution"] == "CADICAL"
            core = frozenset(record["assumption_core"])
            assert core and core <= assumptions
            assert record["assumption_core_size"] == len(core)
            assert record["incremental_stats_delta"]["conflicts"] <= 20002
        elif record["status"] == "COVERED_UNSAT":
            assert record["logical_status"] == "UNSAT"
            assert record["resolution"] == "ASSUMPTION_CORE_CONTAINMENT"
            cover_index = int(record["covered_by_branch_index"])
            assert cover_index < record["branch_index"]
            cover = record_by_index[cover_index]
            core = frozenset(record["assumption_core"])
            assert cover["logical_status"] == "UNSAT"
            assert core == frozenset(cover["assumption_core"])
            assert core and core <= assumptions
            assert record["core_containment_checked"] is True
        elif record["status"] == "UNKNOWN":
            assert record["logical_status"] == "UNKNOWN"
            assert record["resolution"] == "CADICAL"
            assert "assumption_core" not in record
            assert record["incremental_stats_delta"]["conflicts"] <= 20002
        else:
            raise AssertionError(f"unexpected initial branch status: {record['status']}")

    direct = status_counts["UNSAT"]
    covered = status_counts["COVERED_UNSAT"]
    unknown = status_counts["UNKNOWN"]
    sat = status_counts["SAT"]
    assert checkpoint["direct_solver_unsat_count"] == direct
    assert checkpoint["core_covered_unsat_count"] == covered
    assert checkpoint["unknown_count"] == unknown
    assert checkpoint["direct_solver_calls"] == direct + unknown + sat
    assert sum(record["orbit_size"] for record in checkpoint["records"]) == normalized[
        "records"
    ][record_index]["local_graph_count"]
    kept_branch_assumptions = (
        {
            branch["branch_index"]: tuple(branch["assumptions"])
            for branch in branches
        }
        if record_index == 0 else None
    )
    del clauses, branches
    gc.collect()
    return ({
        "record_index": record_index,
        "path": str(path),
        "sha256": sha256(path),
        "support_form": source["support_form"],
        "representatives": len(checkpoint["records"]),
        "labelled_local_graphs": normalized["records"][record_index]["local_graph_count"],
        "direct_unsat": direct,
        "core_covered_unsat": covered,
        "unknown": unknown,
        "sat": sat,
        "variables": meta["variables"],
        "clauses": meta["clauses"],
        "cnf_dimacs_body_sha256": cnf_hash,
    }, {
        "source": source,
        "meta": meta,
        "checkpoint": checkpoint,
        "branch_summaries": meta["branch_assumption_summaries"],
        "cnf_hash": cnf_hash,
        "branch_assumptions": kept_branch_assumptions,
    })


def audit_deep_and_merge(initial_context: dict) -> dict:
    # Rebuild the singleton input separately: variable numbering and every
    # shared clause must agree with record 0, while its sole assumption vector
    # must equal original branch 2.
    source = normalize_source(DEEP_INPUT, 0)
    clauses, _edge, _variables, _full, branches, meta = build_shared_cnf(source)
    assert len(branches) == 1
    cnf_hash = clauses_sha256(clauses)
    assert cnf_hash == initial_context["cnf_hash"]
    logical_meta_keys = (
        "exceptional_supports", "exceptional_fibre_count", "ordinary_c4_fibre_count",
        "local_vertex_count", "local_edge_variables", "local_same_edge_variables",
        "local_overlap_blocks", "local_overlap_edge_variables", "disjoint_edge_variables",
        "all_edge_variables", "disjoint_blocks", "ordinary_ordinary_permutation_blocks",
        "ordinary_exceptional_one_sided_blocks",
        "exceptional_exceptional_unrestricted_disjoint_blocks", "exact_one_rows",
        "at_most_one_columns", "redundant_support_aggregate_rows", "bp_equalities",
        "outer_pair_equalities", "pair_target_histogram", "product_variables",
        "direct_product_terms", "constant_product_terms", "cardinality_equalities",
        "empty_clauses_before_assumptions", "variables", "clauses",
    )
    assert all(meta[key] == initial_context["meta"][key] for key in logical_meta_keys)
    original_summary = initial_context["branch_summaries"][2]
    deep_branch = branches[0]
    original_assumptions = frozenset(initial_context["branch_assumptions"][2])
    deep_assumptions = frozenset(deep_branch["assumptions"])
    assert deep_assumptions == original_assumptions
    assert deep_branch["assumption_sha256"] == original_summary["assumption_sha256"]
    assert deep_branch["assumption_count"] == original_summary["assumption_count"]
    assert deep_branch["positive_assumptions"] == original_summary["positive_assumptions"]
    assert deep_branch["negative_assumptions"] == original_summary["negative_assumptions"]
    assert deep_branch["orbit_size"] == original_summary["orbit_size"]

    checkpoint = json.loads(DEEP_CHECKPOINT.read_text(encoding="utf-8"))
    assert checkpoint["status"] == "UNSAT"
    assert checkpoint["checkpoint_complete"] is True
    assert checkpoint["conflict_budget_per_branch"] == 200000
    assert checkpoint["input"] == str(DEEP_INPUT)
    assert checkpoint["input_selection"] == source["selection"]
    assert checkpoint["shared_cnf_meta"] == json_normalized(meta)
    assert len(checkpoint["records"]) == 1
    record = checkpoint["records"][0]
    assert record["status"] == record["logical_status"] == "UNSAT"
    assert record["resolution"] == "CADICAL"
    assert record["assumption_sha256"] == deep_branch["assumption_sha256"]
    core = frozenset(record["assumption_core"])
    assert core and core <= deep_assumptions
    assert record["assumption_core_size"] == len(core)
    assert record["formal_proof_certificate"] is None
    assert record["incremental_stats_delta"]["conflicts"] <= 200002

    initial = copy.deepcopy(initial_context["checkpoint"])
    old = initial["records"][2]
    assert old["status"] == "UNKNOWN"
    assert old["assumption_sha256"] == record["assumption_sha256"]
    replacement = copy.deepcopy(record)
    replacement["branch_index"] = old["branch_index"]
    replacement["representative_id"] = old["representative_id"]
    replacement["orbit_size"] = old["orbit_size"]
    replacement["merged_deep_source_branch_index"] = record["branch_index"]
    replacement["merged_deep_checkpoint"] = str(DEEP_CHECKPOINT)
    initial["records"][2] = replacement
    initial["model"] = "merged terminal E0=72,Q>=3 small-record-0 computational checkpoint"
    initial["status"] = "UNSAT"
    initial["unknown_count"] = 0
    initial["direct_solver_unsat_count"] = sum(
        row["status"] == "UNSAT" for row in initial["records"]
    )
    initial["core_covered_unsat_count"] = sum(
        row["status"] == "COVERED_UNSAT" for row in initial["records"]
    )
    initial["direct_solver_calls"] = sum(
        row["resolution"] == "CADICAL" for row in initial["records"]
    )
    initial["actual_solver_calls_across_merged_runs"] = (
        initial_context["checkpoint"]["direct_solver_calls"] + checkpoint["direct_solver_calls"]
    )
    initial["solver_session_count"] = (
        initial_context["checkpoint"]["solver_session_count"]
        + checkpoint["solver_session_count"]
    )
    initial["build_seconds"] = round(
        float(initial_context["checkpoint"]["build_seconds"])
        + float(checkpoint["build_seconds"]), 6
    )
    initial["solver_load_seconds"] = round(
        float(initial_context["checkpoint"]["solver_load_seconds"])
        + float(checkpoint["solver_load_seconds"]), 6
    )
    initial["conflict_budget_per_branch"] = None
    initial["conflict_budget_schedule"] = {
        "initial_all_branches": 20000,
        "replacement_branch_2_deep_run": 200000,
    }
    initial["merge_provenance"] = {
        "initial_checkpoint": str(CHECKPOINTS[0]),
        "initial_checkpoint_sha256": sha256(CHECKPOINTS[0]),
        "deep_subset_input": str(DEEP_INPUT),
        "deep_subset_input_sha256": sha256(DEEP_INPUT),
        "deep_checkpoint": str(DEEP_CHECKPOINT),
        "deep_checkpoint_sha256": sha256(DEEP_CHECKPOINT),
        "shared_cnf_dimacs_body_sha256": cnf_hash,
        "replaced_original_branch_index": 2,
        "identical_assumption_sha256": record["assumption_sha256"],
    }
    initial["claim_boundary"] = (
        "This merge is logically exact because the shared CNF and complete branch-2 "
        "assumption vector were rebuilt identically. CaDiCaL UNSAT has no emitted "
        "independently checked DRAT/LRAT certificate."
    )
    assert len(initial["records"]) == 224
    assert [row["branch_index"] for row in initial["records"]] == list(range(224))
    assert all(row["logical_status"] == "UNSAT" for row in initial["records"])
    assert initial["direct_solver_unsat_count"] == 223
    assert initial["core_covered_unsat_count"] == 1
    assert initial["direct_solver_calls"] == 223
    assert initial["actual_solver_calls_across_merged_runs"] == 224
    atomic_json(MERGED_CHECKPOINT, initial)
    del clauses, branches
    gc.collect()
    return {
        "path": str(DEEP_CHECKPOINT),
        "sha256": sha256(DEEP_CHECKPOINT),
        "status": record["status"],
        "original_branch_index": 2,
        "deep_input_branch_index": 0,
        "assumption_sha256": record["assumption_sha256"],
        "assumption_count": record["assumption_count"],
        "assumption_core_size": record["assumption_core_size"],
        "conflict_budget": checkpoint["conflict_budget_per_branch"],
        "solve_seconds": record["solve_seconds"],
        "shared_cnf_dimacs_body_sha256": cnf_hash,
        "shared_cnf_identical_to_initial_record_0": True,
        "complete_assumption_vector_identical_to_initial_branch_2": True,
        "merged_checkpoint": str(MERGED_CHECKPOINT),
        "merged_checkpoint_sha256": sha256(MERGED_CHECKPOINT),
    }


def main() -> None:
    port = json.loads(PORT.read_text(encoding="utf-8"))
    counts = json.loads(COUNTS.read_text(encoding="utf-8"))
    normalized = json.loads(NORMALIZED.read_text(encoding="utf-8"))

    count_audit = audit_counts(port, counts)
    small_totals, partition_audits, row_locations = audit_expansion_parts(counts)
    representative_audit = audit_representatives(port, normalized, row_locations)

    checkpoint_audits = []
    contexts = []
    for record_index, path in enumerate(CHECKPOINTS):
        audit, context = audit_checkpoint(path, record_index, normalized)
        checkpoint_audits.append(audit)
        contexts.append(context)
    initial_totals = {
        "direct_unsat": sum(row["direct_unsat"] for row in checkpoint_audits),
        "core_covered_unsat": sum(row["core_covered_unsat"] for row in checkpoint_audits),
        "unknown": sum(row["unknown"] for row in checkpoint_audits),
        "sat": sum(row["sat"] for row in checkpoint_audits),
    }
    assert tuple(initial_totals[key] for key in (
        "direct_unsat", "core_covered_unsat", "unknown", "sat"
    )) == EXPECTED_INITIAL_SAT
    assert sum(initial_totals.values()) == 584
    assert initial_totals["direct_unsat"] + initial_totals["core_covered_unsat"] == 583

    deep_audit = audit_deep_and_merge(contexts[0])
    merged = json.loads(MERGED_CHECKPOINT.read_text(encoding="utf-8"))
    merged_totals = {
        "support_records": 3,
        "representatives": sum(row["representatives"] for row in checkpoint_audits),
        "labelled_local_graphs": sum(row["labelled_local_graphs"] for row in checkpoint_audits),
        "direct_unsat": initial_totals["direct_unsat"] + 1,
        "core_covered_unsat": initial_totals["core_covered_unsat"],
        "unknown": initial_totals["unknown"] - 1,
        "sat": initial_totals["sat"],
    }
    assert merged_totals == {
        "support_records": 3,
        "representatives": 584,
        "labelled_local_graphs": 24576,
        "direct_unsat": 554,
        "core_covered_unsat": 30,
        "unknown": 0,
        "sat": 0,
    }
    assert merged["status"] == "UNSAT" and merged["unknown_count"] == 0

    input_paths = [PORT, COUNTS, NORMALIZED, *CHECKPOINTS, DEEP_INPUT, DEEP_CHECKPOINT]
    result = {
        "status": "AUDIT_PASS",
        "model": "independent E0=72,Q>=3 completed-small-partition local and SAT audit",
        "scope": {
            "completed_partition_indices": list(PARTITIONS),
            "excluded_partition_indices": [27, 28, 29, 30, 31],
            "scope_is_partial_E72_branch": True,
        },
        "inputs": [
            {"path": str(path), "sha256": sha256(path)} for path in input_paths
        ],
        "global_count_audit": count_audit,
        "small_partition_totals": small_totals,
        "partition_audits": partition_audits,
        "representative_audit": representative_audit,
        "initial_sat": {
            "checkpoints": checkpoint_audits,
            "totals": initial_totals,
            "terminal_representatives": 583,
        },
        "deep_replacement": deep_audit,
        "merged_sat_totals": merged_totals,
        "all_584_representatives_computationally_unsat": True,
        "ok": True,
        "claim_boundary": (
            "This establishes a hash-bound, rebuilt computational exclusion of the "
            "584 representatives in the eleven listed completed partitions only. "
            "It neither covers the remaining E72 partitions nor supplies independently "
            "checked DRAT/LRAT certificates for the CaDiCaL UNSAT answers."
        ),
    }
    atomic_json(OUTPUT, result)

    lines = [
        "# E72 Q>=3 completed-small-partition audit",
        "",
        "Status: **AUDIT_PASS**.",
        "",
        "## Exact local coverage",
        "",
        "| partitions | rows | states | completions | spectral | pair | forced BP | reps |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
        f"| {len(PARTITIONS)} | {small_totals['support_rows']} | "
        f"{small_totals['port_feasible_state_assignments']} | "
        f"{small_totals['exact_overlap_completions']} | "
        f"{small_totals['after_exact_real_spectral_bound']} | "
        f"{small_totals['after_induced_pair_upper']} | "
        f"{small_totals['after_forced_C4_support_BP']} | "
        f"{small_totals['local_graph_orbits']} |",
        "",
        "All 584 stored edge-list representatives were reconstructed; their port "
        "matchings, pair upper bound, forced-C4 BP tests, spectral inequality, and "
        "full residual-symmetry orbits were independently checked. The three surviving "
        "support rows represent exactly 24,576 labelled local graphs.",
        "",
        "## Exact-SAT coverage",
        "",
        "| source | representatives | direct UNSAT | core-covered | UNKNOWN |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in checkpoint_audits:
        lines.append(
            f"| initial record {row['record_index']} | {row['representatives']} | "
            f"{row['direct_unsat']} | {row['core_covered_unsat']} | {row['unknown']} |"
        )
    lines.extend([
        f"| deep replacement for record 0 branch 2 | 1 | 1 | 0 | 0 |",
        "",
        "The initial runs terminally covered 583 representatives. The sole UNKNOWN "
        "has the same rebuilt shared-CNF hash and complete-assumption hash as the "
        "200,000-conflict deep run, which terminated UNSAT. Thus all 584 are "
        "computationally UNSAT (554 direct and 30 exact core containments).",
        "",
        f"Merged checkpoint: `{MERGED_CHECKPOINT}`.",
        "",
        "## Boundary",
        "",
        "No DRAT/LRAT certificate was emitted or independently checked. This is a "
        "reproducible computational exclusion for the eleven listed partitions, not a "
        "formal proof and not a complete exclusion of the E72 branch.",
        "",
    ])
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "global_counts": EXPECTED_GLOBAL_COUNTS,
        "small_totals": EXPECTED_SMALL_TOTALS,
        "initial_terminal": 583,
        "deep_terminal": 1,
        **merged_totals,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
