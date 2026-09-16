"""Independent audit of the E0=78 intermediate-layer seed.

This deliberately does not import any generator, SAT model, or existing
verifier.  It reconstructs labels from the fixed 99-vertex scaffold and
checks the rooted BP equations and all 126 same-support outer-pair equations
directly from the submitted edge list.  It does *not* certify a full SRG.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import hashlib
import itertools
import json
from pathlib import Path


DEFAULT_INPUT = Path("scratch_root_e78_k23_rep6_layer.json")
DEFAULT_OUTPUT = Path("scratch_fibre_layer_sat_v2_root_seed_audit.json")


def classify_four_vertex_graph(vertices: list[int], adjacency: list[set[int]]) -> str:
    local_degrees = sorted(len(adjacency[v].intersection(vertices)) for v in vertices)
    local_edges = sum(local_degrees) // 2
    seen = {vertices[0]}
    todo = deque([vertices[0]])
    while todo:
        u = todo.popleft()
        for v in adjacency[u].intersection(vertices):
            if v not in seen:
                seen.add(v)
                todo.append(v)
    connected = len(seen) == 4
    if connected and local_edges == 4 and local_degrees == [2, 2, 2, 2]:
        return "C4"
    if connected and local_edges == 3 and local_degrees == [1, 1, 2, 2]:
        return "P4"
    return f"other:e{local_edges}:d{','.join(map(str, local_degrees))}:conn{int(connected)}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    source = json.loads(raw)
    listed_edges = source.get("edges", [])

    normalized: list[tuple[int, int]] = []
    malformed = []
    loops = []
    out_of_range = []
    for i, item in enumerate(listed_edges):
        if not (
            isinstance(item, list)
            and len(item) == 2
            and all(isinstance(x, int) and not isinstance(x, bool) for x in item)
        ):
            malformed.append(i)
            continue
        u, v = item
        if u == v:
            loops.append([i, u])
        if not (1 <= u <= 99 and 1 <= v <= 99):
            out_of_range.append([i, u, v])
        normalized.append((min(u, v), max(u, v)))

    duplicates = sorted([list(e) for e, count in Counter(normalized).items() if count != 1])
    edge_set = set(normalized)
    adjacency = [set() for _ in range(100)]
    for u, v in edge_set:
        if 1 <= u <= 99 and 1 <= v <= 99 and u != v:
            adjacency[u].add(v)
            adjacency[v].add(u)

    degree_histogram = Counter(len(adjacency[v]) for v in range(1, 100))

    expected_root_neighbors = set(range(2, 16))
    root_neighbors_ok = adjacency[1] == expected_root_neighbors
    expected_inner_edges = {(2 + 2 * g, 3 + 2 * g) for g in range(7)}
    actual_inner_edges = {
        (u, v) for u, v in edge_set if 2 <= u < v <= 15
    }
    inner_matching_ok = actual_inner_edges == expected_inner_edges

    labels: dict[int, tuple[int, int]] = {}
    bad_outer_inner_degrees = []
    for v in range(16, 100):
        ns = sorted(x - 2 for x in adjacency[v] if 2 <= x <= 15)
        if len(ns) != 2 or ns[0] // 2 == ns[1] // 2:
            bad_outer_inner_degrees.append([v, ns])
        elif len(ns) == 2:
            labels[v] = (ns[0], ns[1])
    expected_labels = {
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    }
    observed_labels = set(labels.values())
    label_bijection_ok = (
        len(labels) == 84
        and len(observed_labels) == 84
        and observed_labels == expected_labels
    )

    outer = set(range(16, 100))
    bp_bad = []
    bp_target_histogram = Counter()
    bp_observed_histogram = Counter()
    if label_bijection_ok:
        for u in range(16, 100):
            own_groups = {s // 2 for s in labels[u]}
            outer_neighbors = adjacency[u].intersection(outer)
            for symbol in range(14):
                observed = sum(symbol in labels[v] for v in outer_neighbors)
                target = 1 if symbol // 2 in own_groups else 2
                bp_target_histogram[target] += 1
                bp_observed_histogram[observed] += 1
                if observed != target:
                    bp_bad.append([u, symbol, observed, target])

    fibres: dict[tuple[int, int], list[int]] = defaultdict(list)
    if label_bijection_ok:
        for u, label in labels.items():
            support = tuple(sorted(s // 2 for s in label))
            fibres[support].append(u)

    same_support_bad = []
    same_support_target_histogram = Counter()
    same_support_outer_value_histogram = Counter()
    same_support_full_value_histogram = Counter()
    fibre_types = Counter()
    exceptional_supports = []
    e0 = 0
    for support in sorted(fibres):
        fibre = sorted(fibres[support])
        if len(fibre) != 4:
            continue
        kind = classify_four_vertex_graph(fibre, adjacency)
        fibre_types[kind] += 1
        if kind == "P4":
            exceptional_supports.append(list(support))
        e0 += sum(v in adjacency[u] for u, v in itertools.combinations(fibre, 2))
        for u, v in itertools.combinations(fibre, 2):
            label_overlap = len(set(labels[u]).intersection(labels[v]))
            target_outer = 2 - label_overlap
            outer_common = len(adjacency[u].intersection(adjacency[v], outer))
            outer_value = outer_common + int(v in adjacency[u])
            full_value = len(adjacency[u].intersection(adjacency[v])) + int(v in adjacency[u])
            same_support_target_histogram[target_outer] += 1
            same_support_outer_value_histogram[outer_value] += 1
            same_support_full_value_histogram[full_value] += 1
            if outer_value != target_outer or full_value != 2:
                same_support_bad.append(
                    [u, v, label_overlap, outer_common, int(v in adjacency[u]), target_outer, full_value]
                )

    residual_histogram = Counter()
    residual_by_pair_class: dict[str, Counter] = defaultdict(Counter)
    energy = 0
    bad_pairs = 0
    max_abs_residual = 0
    for u, v in itertools.combinations(range(1, 100), 2):
        common = len(adjacency[u].intersection(adjacency[v]))
        residual = common + int(v in adjacency[u]) - 2
        residual_histogram[residual] += 1
        energy += residual * residual
        bad_pairs += residual != 0
        max_abs_residual = max(max_abs_residual, abs(residual))
        if u == 1:
            pair_class = "root-other"
        elif u <= 15 and v <= 15:
            pair_class = "inner-inner"
        elif u <= 15 < v:
            pair_class = "inner-outer"
        else:
            su = tuple(sorted(s // 2 for s in labels[u])) if u in labels else ()
            sv = tuple(sorted(s // 2 for s in labels[v])) if v in labels else ()
            pair_class = "outer-same-support" if su == sv else "outer-cross-support"
        residual_by_pair_class[pair_class][residual] += 1

    canonical_text = "".join(f"{u},{v}\n" for u, v in sorted(edge_set)).encode("ascii")
    expected_claims = {
        "edge_count": len(edge_set),
        "energy": energy,
        "recomputed_energy": energy,
        "bad_pairs": bad_pairs,
        "max_abs_residual": max_abs_residual,
        "same_support_bad_total": len(same_support_bad),
        "exceptional_supports": exceptional_supports,
    }
    claims_match = {
        key: (sorted(source[key]) if key == "exceptional_supports" else source[key]) == expected
        for key, expected in expected_claims.items()
        if key in source
    }
    layer_ok = all(
        [
            len(listed_edges) == 693,
            not malformed,
            not loops,
            not out_of_range,
            not duplicates,
            len(edge_set) == 693,
            degree_histogram == Counter({14: 99}),
            root_neighbors_ok,
            inner_matching_ok,
            not bad_outer_inner_degrees,
            label_bijection_ok,
            len(fibres) == 21,
            all(len(vs) == 4 for vs in fibres.values()),
            bp_target_histogram == Counter({1: 336, 2: 840}),
            not bp_bad,
            same_support_target_histogram == Counter({1: 84, 2: 42}),
            not same_support_bad,
            e0 == 78,
            fibre_types == Counter({"C4": 15, "P4": 6}),
            all(claims_match.values()),
        ]
    )
    full_srg_ok = layer_ok and energy == 0 and bad_pairs == 0

    report = {
        "input": str(args.input),
        "input_sha256": hashlib.sha256(raw).hexdigest().upper(),
        "canonical_edge_sha256": hashlib.sha256(canonical_text).hexdigest().upper(),
        "independent_of_generator_and_existing_verifier": True,
        "listed_edge_count": len(listed_edges),
        "unique_edge_count": len(edge_set),
        "malformed_edge_indices": malformed,
        "loops": loops,
        "out_of_range": out_of_range,
        "duplicate_or_reversed_edges": duplicates,
        "degree_histogram": dict(sorted(degree_histogram.items())),
        "root_neighbors_ok": root_neighbors_ok,
        "inner_matching_ok": inner_matching_ok,
        "bad_outer_inner_degrees": bad_outer_inner_degrees,
        "outer_label_bijection_ok": label_bijection_ok,
        "outer_label_count": len(observed_labels),
        "bp_equations_checked": sum(bp_target_histogram.values()),
        "bp_target_histogram": dict(sorted(bp_target_histogram.items())),
        "bp_observed_histogram": dict(sorted(bp_observed_histogram.items())),
        "bp_bad_count": len(bp_bad),
        "bp_bad_examples": bp_bad[:20],
        "same_support_pair_equations_checked": sum(same_support_target_histogram.values()),
        "same_support_target_histogram": dict(sorted(same_support_target_histogram.items())),
        "same_support_outer_value_histogram": dict(sorted(same_support_outer_value_histogram.items())),
        "same_support_full_value_histogram": dict(sorted(same_support_full_value_histogram.items())),
        "same_support_bad_count": len(same_support_bad),
        "same_support_bad_examples": same_support_bad[:20],
        "E0_same_support_outer_edges": e0,
        "fibre_type_histogram": dict(sorted(fibre_types.items())),
        "exceptional_supports": exceptional_supports,
        "full_pair_count": sum(residual_histogram.values()),
        "full_residual_histogram": dict(sorted(residual_histogram.items())),
        "full_residual_histogram_by_class": {
            key: dict(sorted(value.items())) for key, value in sorted(residual_by_pair_class.items())
        },
        "full_srg_energy": energy,
        "full_srg_bad_pairs": bad_pairs,
        "max_abs_residual": max_abs_residual,
        "source_claims_match": claims_match,
        "layer_ok": layer_ok,
        "full_srg_ok": full_srg_ok,
        "claim_boundary": "Exact BP+126 same-support layer seed only; not a full SRG.",
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not layer_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
