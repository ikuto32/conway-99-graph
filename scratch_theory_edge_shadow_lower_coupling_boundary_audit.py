"""Independent audit of the edge-shadow lower-coupling boundary."""

from __future__ import annotations

from fractions import Fraction
import gzip
import hashlib
import itertools
import json
import math
import os
from pathlib import Path


SOURCE = Path("scratch_theory_edge_shadow_lower_coupling_boundary.json")
OUTPUT = Path("scratch_theory_edge_shadow_lower_coupling_boundary_audit.json")
COEFFICIENTS = Path(
    "external_conway99_research/attempts/"
    "wave147-alternative-lane/coefficients.json.gz"
)
MARKED = Path(
    "external_conway99_research/attempts/"
    "wave148-marked-order8/marked-rows.json.gz"
)


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def positions(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


def edges_from_mask(mask: int, order: int) -> set[tuple[int, int]]:
    return {edge for bit, edge in enumerate(positions(order)) if (mask >> bit) & 1}


def mask_from_edges(edges: set[tuple[int, int]], order: int) -> int:
    normalized = {tuple(sorted(edge)) for edge in edges}
    return sum(1 << bit for bit, edge in enumerate(positions(order))
               if edge in normalized)


def delete_vertex(mask: int, order: int, deleted: int) -> int:
    vertices = tuple(vertex for vertex in range(order) if vertex != deleted)
    index = {vertex: new for new, vertex in enumerate(vertices)}
    induced = {
        tuple(sorted((index[x], index[y])))
        for x, y in edges_from_mask(mask, order)
        if x != deleted and y != deleted
    }
    return mask_from_edges(induced, order - 1)


def pair_upper(mask: int, order: int) -> bool:
    edges = edges_from_mask(mask, order)
    for x, y in positions(order):
        common = len({
            z for z in range(order) if z not in (x, y)
            and tuple(sorted((x, z))) in edges
            and tuple(sorted((y, z))) in edges
        })
        if common > (1 if (x, y) in edges else 2):
            return False
    return True


def proportional(vector: dict[int, int], target: dict[int, int]) -> bool:
    if set(vector) != set(target) or not vector:
        return False
    index = next(iter(vector))
    scale = Fraction(vector[index], target[index])
    return all(Fraction(vector[key], target[key]) == scale for key in vector)


def main() -> None:
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    assert data["status"] == "EDGE_SHADOW_LOWER_COUPLING_EXACT_BOUNDARY_COMPLETE"
    for path, digest in data["inputs"].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest().upper() == digest

    # Replay frozen coefficient inspection with independent data flow.
    with gzip.open(COEFFICIENTS, "rt", encoding="utf-8") as handle:
        coefficient_data = json.load(handle)
    with gzip.open(MARKED, "rt", encoding="utf-8") as handle:
        marked_data = json.load(handle)
    shadow = json.loads(Path("scratch_theory_root_yyt_order8_shadow.json").read_text())
    total_class_records = 0
    family_checks = {}
    for name in ("ordered_edge", "ordered_nonedge"):
        family = coefficient_data["families"][name]
        records = family["class_coefficients"]
        total_class_records += len(records)
        keys = [(int(record["order"]), int(record["canonical_mask"]))
                for record in records]
        assert len(keys) == 1207 and len(set(keys)) == 1207
        assert {order for order, _ in keys} == {5, 6, 7, 8}
        lookup = {key: index for index, key in enumerate(keys)}
        target = {
            lookup[(8, int(mask))]: int(value)
            for mask, value in shadow["shadow_coefficients"][name][
                "nonzero_order8_coefficients"
            ]
        }
        vectors: dict[tuple[int, int], dict[int, int]] = {}
        for class_index, record in enumerate(records):
            for row, column, value in record["upper_entries"]:
                vectors.setdefault((int(row), int(column)), {})[class_index] = int(value)
        assert not any(proportional(vector, target) for vector in vectors.values())
        stored = data["frozen_resource_inspection"]["families"][name]
        assert stored["class_coefficient_records"] == 1207
        assert stored["nonzero_matrix_entry_vectors"] == len(vectors)
        assert stored["individual_entry_proportional_to_shadow"] is False
        modular = stored["modular_span_check"]
        assert modular["rank_after_appending_shadow"] == modular["entry_span_rank"] + 1
        family_checks[name] = {
            "entries": len(vectors),
            "target_support": len(target),
            "single_entry_exact": False,
        }
    assert total_class_records == 2414
    assert marked_data["class_streams"]["8"]["count"] == 916

    # Independently decode every stored extension mask.  Deleting vertex 6
    # must erase both mate bits and leave one fixed order-eight mask per root
    # relation; all completions retain the induced pair upper bounds.
    quartet_checks = []
    for quartet in data["order9_nonmeasurability_witness"]["quartets"]:
        deleted = set()
        selected_values = []
        for record in quartet["completion_records"]:
            mask = int(record["labelled_order9_mask"])
            assert pair_upper(mask, 9)
            reduced = delete_vertex(mask, 9, 6)
            assert reduced == record["order8_mask_after_deleting_mate"]
            deleted.add(reduced)
            left, right = record["mate_to_source_root_bits"]
            assert record["selected_root_indicators"] == [left, right]
            assert record["selected_pair_indicator"] == left * right
            selected_values.append(left * right)
        assert len(deleted) == 1 and selected_values == [0, 0, 0, 1]
        quartet_checks.append({
            "root_relation": quartet["source_root_relation"],
            "common_order8_mask": next(iter(deleted)),
            "selected_values": selected_values,
        })
    assert {row["root_relation"] for row in quartet_checks} == {"edge", "nonedge"}

    # Selector polynomial truth table.
    expected = {(0, 1): 0, (0, 2): 1, (1, 1): 1}
    for (mate, y), selected in expected.items():
        assert mate * y + math.comb(y, 2) == selected

    # Independent nonedge first moments and endpoint collision split.
    endpoint = data["nonedge_collision_double_count"]["T_zero_integer_marginal"]
    s, d = endpoint["per_nonedge"]["side_roots"], endpoint["per_nonedge"]["diagonal_roots"]
    assert (s, d) == (2, 1)
    ss, sd, dd = 4158 * math.comb(s, 2), 4158 * s * d, 4158 * math.comb(d, 2)
    assert endpoint["collision_by_type"] == {
        "side_side": ss, "side_diagonal": sd,
        "diagonal_diagonal": dd, "total_K_nonedge": ss + sd + dd,
    }
    assert ss + sd + dd == 12474
    assert endpoint["root_group_same_overlap_disjoint"] == [3, 36, 32]
    assert 3 + 36 + 32 == 71 and 2 * 3 + 36 == 42

    # Generic union arities: two flags share only target vertices x,y.
    side_left = {"r", "x", "y", "a", "b", "c"}
    side_right = {"s", "x", "y", "d", "e", "f"}
    diagonal_left = side_left | {"g"}
    diagonal_right = side_right | {"h"}
    assert len(side_left | side_right) == 10
    assert len(side_left | diagonal_right) == 11
    assert len(diagonal_left | diagonal_right) == 12

    boundary = data["frozen_relaxation_boundary"]
    assert boundary["Wave159"]["T"] == boundary["Wave159"]["K_edge"] == 0
    assert boundary["Wave159"]["beta_sum"] == 45738
    assert boundary["H0_and_nonedge_margin"]["eigenvalues"] == [336, 72, 93]
    assert boundary["H0_and_nonedge_margin"]["K_nonedge"] == 12474
    separators = boundary["exact_full_four_root_point_separators"]
    assert {row["root_mask"] for row in separators} == {3, 12}
    assert all(row["strictly_negative"] and int(row["quadratic_value_scaled"]) < 0
               for row in separators)
    assert boundary["point_separation_is_not_a_T_bound"] is True
    assert data["lane_conclusion"]["positive_T_lower_bound_obtained"] is False

    result = {
        "status": "EDGE_SHADOW_LOWER_COUPLING_INDEPENDENT_AUDIT_PASS",
        "input": {str(SOURCE): hashlib.sha256(raw).hexdigest().upper()},
        "all_frozen_input_hashes_verified": True,
        "coefficient_records_replayed": total_class_records,
        "coefficient_family_checks": family_checks,
        "extension_quartets_independently_decoded": quartet_checks,
        "selector_truth_table_verified": True,
        "nonedge_T_zero_margin_verified": True,
        "known_full_four_root_point_separators_verified": 2,
        "generic_nonedge_two_root_union_orders_verified": [10, 11, 12],
        "positive_T_lower_bound": False,
        "scope": (
            "This proves the visibility/arity boundary of the frozen order-eight "
            "lane.  It does not certify feasibility of the endpoint in the full "
            "four-root PSD system or existence of a graph."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "path": str(OUTPUT), "status": result["status"],
        "coefficient_records": total_class_records,
        "quartets": len(quartet_checks), "positive_T": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
