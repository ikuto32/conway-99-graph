"""Enumerate the exact source133 pointwise-balance disjoint completions.

For the four regular (matching) state macros, the root pair-constant mode
forces p=v=z=1 at every exceptional vertex.  More generally, including the
nonregular fifth macro, a vertex of internal degree ``a`` satisfies

    p_j + z_j = 1  (j is either complementary bottom index),
    p = v = 2-a,   z = a.

Thus every one of the six disjoint A_i--B_k blocks has prescribed two-vertex
sets on both shores and exactly the two perfect matchings of a 2 by 2 graph.
This script enumerates their 2^6 joint products, checks the realized forced-BP
profile and induced-pair upper bound, and quotients surviving completions by
the exact stabilizer of each already-canonical local representative.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

import scratch_general_e79_local_audit as local79
from scratch_general_e72_q3_fast_expansion import RowGeometry
from scratch_general_e72_q3_disjoint_gram_filter import row_geometry
from scratch_general_e72_source248_local_probe import (
    PairUpperState,
    normal_edge,
    vertex_profiles,
)


INPUT_PATH = Path("scratch_general_e72_q3_gram_fast_expansion_part_27_orbit_000.json")
MACRO_PATH = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
THEORY_PATH = Path("scratch_theory_e72_k23_balance_audit.json")
BALANCE_CROSSCHECK_PATH = Path("scratch_general_e72_source133_balance_crosscheck.json")
OUTPUT_PATH = Path("scratch_general_e72_source133_pointwise_completion.json")
SOURCE_ROW_INDEX = 133
BOTTOM = (2, 3, 4)


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def internal_key(edges, fibre_of):
    return frozenset(
        edge for edge in edges if fibre_of[edge[0]] == fibre_of[edge[1]]
    )


def side(support):
    return 1 if support[0] == 0 else -1


def edge_mask(geometry: RowGeometry, index_edges) -> int:
    answer = 0
    for left, right in index_edges:
        pair = (left, right) if left < right else (right, left)
        answer |= 1 << geometry.pair_index[pair]
    return answer


def direct_pair_upper(geometry: RowGeometry, mask: int) -> bool:
    edges = geometry.labelled_edges(mask)
    return local79.induced_pair_upper(geometry.vertices, edges)


def compile_pointwise_blocks(
    geometry,
    supports,
    vertices_by_fibre,
    fibre_of,
    base_edges,
    macro_number,
):
    """Return two choices for every disjoint block, or an exact failure."""

    support_to_fibre = {support: i for i, support in enumerate(supports)}
    neighbours = local79.neighbour_sets(geometry.vertices, base_edges)
    z_target = {}
    vertex_rows = []
    regular = macro_number != 4
    for fibre, (support, fibre_vertices) in enumerate(zip(supports, vertices_by_fibre)):
        root, bottom = support
        assert root in (0, 1) and bottom in BOTTOM
        other_root = 1 - root
        vertical = support_to_fibre[(other_root, bottom)]
        complements = tuple(value for value in BOTTOM if value != bottom)
        for vertex in fibre_vertices:
            a = sum(fibre_of[other] == fibre for other in neighbours[vertex])
            p_by_bottom = {
                value: sum(
                    fibre_of[other] == support_to_fibre[(root, value)]
                    for other in neighbours[vertex]
                )
                for value in complements
            }
            vertical_degree = sum(
                fibre_of[other] == vertical for other in neighbours[vertex]
            )
            expected_pv = 2 - a
            conditions = (
                all(value in (0, 1) for value in p_by_bottom.values())
                and sum(p_by_bottom.values()) == expected_pv
                and vertical_degree == expected_pv
            )
            if regular:
                conditions = conditions and a == expected_pv == 1
            if not conditions:
                return None, {
                    "status": "POINTWISE_SUPPORT_IDENTITY_FAILURE",
                    "fibre": fibre,
                    "vertex": list(vertex),
                    "internal_degree_a": a,
                    "p_by_bottom": p_by_bottom,
                    "vertical_degree": vertical_degree,
                    "expected_p_equals_v": expected_pv,
                }
            for value in complements:
                disjoint_fibre = support_to_fibre[(other_root, value)]
                z_target[(vertex, disjoint_fibre)] = 1 - p_by_bottom[value]
            z = sum(z_target[(vertex, support_to_fibre[(other_root, value)])]
                    for value in complements)
            assert z == a
            vertex_rows.append(
                {
                    "vertex": vertex,
                    "a": a,
                    "p": sum(p_by_bottom.values()),
                    "v": vertical_degree,
                    "z": z,
                }
            )

    blocks = []
    third_index_checks = 0
    for left_bottom in BOTTOM:
        left = support_to_fibre[(0, left_bottom)]
        for right_bottom in BOTTOM:
            if left_bottom == right_bottom:
                continue
            right = support_to_fibre[(1, right_bottom)]
            left_shore = tuple(
                vertex
                for vertex in vertices_by_fibre[left]
                if z_target[(vertex, right)] == 1
            )
            right_shore = tuple(
                vertex
                for vertex in vertices_by_fibre[right]
                if z_target[(vertex, left)] == 1
            )
            if len(left_shore) != 2 or len(right_shore) != 2:
                return None, {
                    "status": "DISJOINT_BLOCK_SHORE_SIZE_FAILURE",
                    "block": [left, right],
                    "left_shore_size": len(left_shore),
                    "right_shore_size": len(right_shore),
                }
            if regular:
                third = next(
                    value
                    for value in BOTTOM
                    if value not in (left_bottom, right_bottom)
                )
                left_third = support_to_fibre[(0, third)]
                right_third = support_to_fibre[(1, third)]
                assert left_shore == tuple(
                    vertex
                    for vertex in vertices_by_fibre[left]
                    if any(fibre_of[other] == left_third for other in neighbours[vertex])
                )
                assert right_shore == tuple(
                    vertex
                    for vertex in vertices_by_fibre[right]
                    if any(fibre_of[other] == right_third for other in neighbours[vertex])
                )
                third_index_checks += 2
            choices = []
            for permutation in ((0, 1), (1, 0)):
                labelled = tuple(
                    normal_edge(left_shore[i], right_shore[permutation[i]])
                    for i in range(2)
                )
                indexed = tuple(
                    (
                        geometry.vertex_index[edge[0]],
                        geometry.vertex_index[edge[1]],
                    )
                    for edge in labelled
                )
                choices.append(
                    {
                        "edges": indexed,
                        "mask": edge_mask(geometry, indexed),
                    }
                )
            assert choices[0]["mask"] != choices[1]["mask"]
            blocks.append(
                {
                    "fibres": (left, right),
                    "left_shore": left_shore,
                    "right_shore": right_shore,
                    "choices": tuple(choices),
                }
            )
    assert len(blocks) == 6
    assert not regular or third_index_checks == 12
    return tuple(blocks), {
        "status": "POINTWISE_BLOCKS_COMPILED",
        "regular_matching_macro": regular,
        "vertex_(a,p,v,z)_histogram": {
            str(key): value
            for key, value in sorted(
                Counter((row["a"], row["p"], row["v"], row["z"])
                        for row in vertex_rows).items()
            )
        },
        "third_index_subset_equalities_checked": third_index_checks,
    }


def realized_bp_ok(
    supports,
    vertices_by_fibre,
    fibre_of,
    profiles,
    component,
    extra_edges,
):
    degrees = Counter()
    for left, right in extra_edges:
        f, g = fibre_of[left], fibre_of[right]
        degrees[(left, g)] += 1
        degrees[(right, f)] += 1
    for fibre, fibre_vertices in enumerate(vertices_by_fibre):
        disjoint = tuple(
            other
            for other in range(len(supports))
            if not (set(supports[fibre]) & set(supports[other]))
        )
        for vertex in fibre_vertices:
            row = [0] * len(disjoint)
            for other in disjoint:
                position = component[(vertex, other)]
                row[position] = degrees[(vertex, other)]
            if tuple(row) not in profiles[vertex]:
                return False
    return True


def enumerate_pair_survivors(
    geometry,
    base_edges,
    base_mask,
    blocks,
):
    state = PairUpperState(geometry.vertices, base_edges)
    survivors = set()
    nodes = 0

    def visit(depth, extra_mask):
        nonlocal nodes
        nodes += 1
        if depth == len(blocks):
            full_mask = base_mask | extra_mask
            assert full_mask not in survivors
            survivors.add(full_mask)
            return
        for choice in blocks[depth]["choices"]:
            trail = state.apply_edges(choice["edges"])
            if trail is None:
                continue
            visit(depth + 1, extra_mask | choice["mask"])
            state.rollback(trail)

    visit(0, 0)
    return survivors, nodes


def quotient_under_base_stabilizer(
    geometry,
    base_mask,
    base_orbit_size,
    survivor_masks,
    macro_number,
    q,
):
    stabilizer = tuple(
        action_index
        for action_index in range(len(geometry.actions))
        if geometry.transform(base_mask, action_index) == base_mask
    )
    assert len(geometry.actions) == base_orbit_size * len(stabilizer)
    remaining = set(survivor_masks)
    records = []
    while remaining:
        seed = min(remaining)
        orbit = {
            geometry.transform(seed, action_index) for action_index in stabilizer
        }
        assert orbit <= survivor_masks
        records.append(
            {
                "mask_hex": hex(seed),
                "base_mask_hex": hex(base_mask),
                "disjoint_mask_hex": hex(seed ^ base_mask),
                "orbit_size": base_orbit_size * len(orbit),
                "completion_orbit_size_under_base_stabilizer": len(orbit),
                "state_macro_number": macro_number,
                "Q": q,
            }
        )
        remaining.difference_update(orbit)
    assert sum(record["orbit_size"] for record in records) == (
        base_orbit_size * len(survivor_masks)
    )
    return records


def verify_completed_mask(
    geometry,
    supports,
    fibre_of,
    mask,
):
    assert direct_pair_upper(geometry, mask)
    edges = geometry.labelled_edges(mask)
    neighbours = local79.neighbour_sets(geometry.vertices, edges)
    for vertex in geometry.vertices:
        h = sum(side(supports[fibre_of[other]]) for other in neighbours[vertex])
        assert h == 0


def run(limit=None) -> None:
    document = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    macro_document = json.loads(MACRO_PATH.read_text(encoding="utf-8"))
    theory = json.loads(THEORY_PATH.read_text(encoding="utf-8"))
    earlier_balance = json.loads(BALANCE_CROSSCHECK_PATH.read_text(encoding="utf-8"))
    assert document["status"] == "COMPLETE"
    assert theory["status"] == "EXACT_SUPPORT_ARITHMETIC_VERIFIED"
    row = document["rows"][0]
    geometry = RowGeometry(row)
    supports, vertices_by_fibre, fibre_of, _ = row_geometry(row)
    assert tuple(geometry.vertices) == tuple(sorted(fibre_of))
    macro_rows = [
        entry
        for entry in macro_document["macro_entries"]
        if entry["source_row_index"] == SOURCE_ROW_INDEX
    ]
    assert len(macro_rows) == 5
    macro_by_internal = {
        frozenset(normal_edge(left, right) for left, right in entry["internal_edges"]): entry
        for entry in macro_rows
    }
    assert len(macro_by_internal) == 5

    representatives = row["local_graph_representatives"]
    if limit is not None:
        representatives = representatives[:limit]
    per_macro = defaultdict(Counter)
    base_results = []
    completed_records = []
    completed_canonical_masks = set()
    total_search_nodes = 0
    for number, representative in enumerate(representatives):
        base_edges = frozenset(
            normal_edge(left, right) for left, right in representative["edges"]
        )
        base_mask = geometry.mask_of(base_edges)
        assert hex(base_mask) == representative["mask_hex"]
        macro = macro_by_internal[internal_key(base_edges, fibre_of)]
        macro_number = macro["state_orbit_number"]
        assert macro["Q"] == representative["Q"]
        stats = per_macro[macro_number]
        mass = representative["orbit_size"]
        stats["input_base_orbits"] += 1
        stats["input_base_raw_mass"] += mass

        blocks, detail = compile_pointwise_blocks(
            geometry,
            supports,
            vertices_by_fibre,
            fibre_of,
            base_edges,
            macro_number,
        )
        if blocks is None:
            stats["support_identity_failure_base_orbits"] += 1
            stats["support_identity_failure_base_raw_mass"] += mass
            base_results.append(
                {
                    "representative_number": number,
                    "base_mask_hex": representative["mask_hex"],
                    "base_orbit_size": mass,
                    "state_macro_number": macro_number,
                    "Q": representative["Q"],
                    "compile_detail": detail,
                    "candidate_completions": 0,
                    "after_realized_forced_BP": 0,
                    "after_induced_pair_upper": 0,
                    "completed_graph_orbits": 0,
                }
            )
            continue
        stats["support_identity_compatible_base_orbits"] += 1
        stats["support_identity_compatible_base_raw_mass"] += mass
        assert all(len(block["choices"]) == 2 for block in blocks)
        candidate_count = 1 << len(blocks)
        assert candidate_count == 64
        stats["candidate_completions_on_base_representatives"] += candidate_count
        stats["candidate_labelled_mass"] += mass * candidate_count

        profiles, component = vertex_profiles(
            supports, vertices_by_fibre, fibre_of, base_edges
        )
        # The pointwise rule fixes degrees, so realized BP is independent of
        # which of the two matchings is chosen inside each block.
        sample_extra = frozenset(
            normal_edge(
                geometry.vertices[left], geometry.vertices[right]
            )
            for block in blocks
            for left, right in block["choices"][0]["edges"]
        )
        bp_ok = realized_bp_ok(
            supports,
            vertices_by_fibre,
            fibre_of,
            profiles,
            component,
            sample_extra,
        )
        if not bp_ok:
            stats["realized_BP_failure_base_orbits"] += 1
            stats["realized_BP_failure_base_raw_mass"] += mass
            base_results.append(
                {
                    "representative_number": number,
                    "base_mask_hex": representative["mask_hex"],
                    "base_orbit_size": mass,
                    "state_macro_number": macro_number,
                    "Q": representative["Q"],
                    "compile_detail": detail,
                    "candidate_completions": candidate_count,
                    "after_realized_forced_BP": 0,
                    "after_induced_pair_upper": 0,
                    "completed_graph_orbits": 0,
                }
            )
            continue
        stats["after_realized_forced_BP_on_base_representatives"] += candidate_count
        stats["after_realized_forced_BP_labelled_mass"] += mass * candidate_count

        survivor_masks, search_nodes = enumerate_pair_survivors(
            geometry, base_edges, base_mask, blocks
        )
        total_search_nodes += search_nodes
        stats["after_induced_pair_upper_on_base_representatives"] += len(survivor_masks)
        stats["after_induced_pair_upper_labelled_mass"] += mass * len(survivor_masks)
        if survivor_masks:
            stats["nonempty_base_orbits"] += 1
            stats["nonempty_base_raw_mass"] += mass
        else:
            stats["empty_base_orbits"] += 1
            stats["empty_base_raw_mass"] += mass
        records = quotient_under_base_stabilizer(
            geometry,
            base_mask,
            mass,
            survivor_masks,
            macro_number,
            representative["Q"],
        )
        for record in records:
            mask = int(record["mask_hex"], 16)
            assert mask not in completed_canonical_masks
            completed_canonical_masks.add(mask)
            verify_completed_mask(geometry, supports, fibre_of, mask)
        completed_records.extend(records)
        stats["completed_graph_orbits"] += len(records)
        base_results.append(
            {
                "representative_number": number,
                "base_mask_hex": representative["mask_hex"],
                "base_orbit_size": mass,
                "state_macro_number": macro_number,
                "Q": representative["Q"],
                "compile_detail": detail,
                "candidate_completions": candidate_count,
                "after_realized_forced_BP": candidate_count,
                "after_induced_pair_upper": len(survivor_masks),
                "completed_graph_orbits": len(records),
                "pair_search_nodes": search_nodes,
            }
        )

    macro_summary = []
    for macro in sorted(macro_rows, key=lambda entry: entry["state_orbit_number"]):
        number = macro["state_orbit_number"]
        macro_summary.append(
            {
                "state_macro_number": number,
                "state_indices": macro["state_indices"],
                "Q": macro["Q"],
                "base_macro_labelled_coverage": macro[
                    "signature_orbit_labelled_coverage"
                ],
                **dict(per_macro[number]),
            }
        )

    nonempty_base = {
        row["base_mask_hex"]
        for row in base_results
        if row["after_induced_pair_upper"]
    }
    earlier_nonempty = {
        row["mask_hex"]
        for row in earlier_balance["representatives"][: len(base_results)]
        if row["balance_plus_pair_upper_completion_exists"]
    }
    assert nonempty_base == earlier_nonempty
    completed_q_mass = Counter()
    completed_q_orbits = Counter()
    for record in completed_records:
        completed_q_mass[record["Q"]] += record["orbit_size"]
        completed_q_orbits[record["Q"]] += 1
    summary = {
        "state_macros_checked": sum(bool(per_macro[number]) for number in range(5)),
        "input_base_graph_orbits": len(base_results),
        "input_base_raw_mass": sum(row["base_orbit_size"] for row in base_results),
        "support_identity_failure_base_orbits": sum(
            row.get("support_identity_failure_base_orbits", 0) for row in macro_summary
        ),
        "support_identity_compatible_base_orbits": sum(
            row.get("support_identity_compatible_base_orbits", 0) for row in macro_summary
        ),
        "candidate_completions_on_base_representatives": sum(
            row.get("candidate_completions_on_base_representatives", 0)
            for row in macro_summary
        ),
        "candidate_labelled_mass": sum(
            row.get("candidate_labelled_mass", 0) for row in macro_summary
        ),
        "after_realized_forced_BP_on_base_representatives": sum(
            row.get("after_realized_forced_BP_on_base_representatives", 0)
            for row in macro_summary
        ),
        "after_realized_forced_BP_labelled_mass": sum(
            row.get("after_realized_forced_BP_labelled_mass", 0)
            for row in macro_summary
        ),
        "after_induced_pair_upper_on_base_representatives": sum(
            row.get("after_induced_pair_upper_on_base_representatives", 0)
            for row in macro_summary
        ),
        "after_induced_pair_upper_labelled_mass": sum(
            row.get("after_induced_pair_upper_labelled_mass", 0)
            for row in macro_summary
        ),
        "nonempty_base_orbits": sum(
            row.get("nonempty_base_orbits", 0) for row in macro_summary
        ),
        "empty_base_orbits": sum(
            row.get("empty_base_orbits", 0) for row in macro_summary
        ),
        "nonempty_base_raw_mass": sum(
            row["base_orbit_size"]
            for row in base_results
            if row["after_induced_pair_upper"]
        ),
        "completed_graph_orbits": len(completed_records),
        "completed_graph_orbit_mass": sum(
            row["orbit_size"] for row in completed_records
        ),
        "completed_graph_Q_mass_histogram": {
            str(q): value for q, value in sorted(completed_q_mass.items())
        },
        "completed_graph_Q_orbit_histogram": {
            str(q): value for q, value in sorted(completed_q_orbits.items())
        },
        "completed_graph_orbit_size_histogram": {
            str(size): count
            for size, count in sorted(
                Counter(record["orbit_size"] for record in completed_records).items()
            )
        },
        "pair_search_nodes": total_search_nodes,
        "all_two_to_the_six_products_exhaustively_processed": True,
        "all_survivor_sets_closed_under_base_stabilizers": True,
        "all_completed_orbit_representatives_directly_rechecked": True,
        "nonempty_base_set_matches_independent_general_balance_DFS": True,
    }
    assert summary["completed_graph_orbit_mass"] == summary[
        "after_induced_pair_upper_labelled_mass"
    ]
    complete = limit is None
    if complete:
        assert summary["state_macros_checked"] == 5
        assert summary["input_base_graph_orbits"] == 8_060
        assert summary["input_base_raw_mass"] == 2_502_656
        assert sum(row["input_base_orbits"] for row in macro_summary) == 8_060
        assert sum(row["input_base_raw_mass"] for row in macro_summary) == 2_502_656
        assert summary["candidate_completions_on_base_representatives"] == 8_060 * 64
        assert summary["after_realized_forced_BP_on_base_representatives"] == 8_060 * 64

    result = {
        "status": "COMPLETE" if complete else "PARTIAL_PROBE",
        "scope": (
            "source133 exact p_j+z_j=1 disjoint completions, realized BP, "
            "induced-pair upper, and stabilizer quotient"
        ),
        "inputs": {
            str(path): sha256(path)
            for path in (INPUT_PATH, MACRO_PATH, THEORY_PATH, BALANCE_CROSSCHECK_PATH)
        },
        "source_row_index": SOURCE_ROW_INDEX,
        "partition_index": 27,
        "compression_orbit_index": 0,
        "exceptional_support_order": [list(support) for support in supports],
        "vertex_order_for_masks": [list(vertex) for vertex in geometry.vertices],
        "summary": summary,
        "macro_summary": macro_summary,
        "base_representatives": base_results,
        "completed_graph_representatives": sorted(
            completed_records, key=lambda row: int(row["mask_hex"], 16)
        ),
        "representative_convention": (
            "minimum already-canonical base local graph, then minimum completed "
            "mask under its exact base-graph stabilizer"
        ),
        "claim_boundary": (
            "These are explicit exceptional-layer completions only.  The "
            "remaining ordinary-fibre edges and the full 99-vertex SRG are not "
            "constructed."
        ),
    }
    atomic_json(OUTPUT_PATH, result)
    print(json.dumps({"status": result["status"], **summary}), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    run(args.limit)


if __name__ == "__main__":
    main()
