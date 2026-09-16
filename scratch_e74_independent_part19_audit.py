"""Independent audit of completed unconditional E0=74 part-19 local rows."""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

from scratch_e74_independent_port import build_domains


EXPANSION = Path("scratch_general_e74_local_expansion_part_19.json")
PORT_STATES = Path("scratch_e74_independent_feasible_states.json")
NORMALIZED = Path("scratch_general_e74_incremental_snapshot_002_records.json")
CATALOG = Path("scratch_e74_independent_part19_fixed_exact_catalog.json")
CHECKPOINT = Path("scratch_e74_independent_part19_fixed_exact_checkpoint.json")
PORTFOLIO = Path("scratch_e74_independent_part19_fixed_exact_portfolio.json")
FIXED_SOURCE = Path("scratch_e74_independent_fixed_sat.py")
OUTPUT = Path("scratch_e74_independent_part19_audit.json")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph_from_edges(raw_edges):
    return frozenset(
        tuple(sorted((tuple(raw_u), tuple(raw_v)))) for raw_u, raw_v in raw_edges
    )


def transform_graph(graph, mapping):
    return frozenset(
        tuple(sorted((mapping[u], mapping[v]))) for u, v in graph
    )


def all_outer_labels():
    return tuple(pair for pair in itertools.combinations(range(14), 2)
                 if pair[0] // 2 != pair[1] // 2)


def main():
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    expansion = read(EXPANSION)
    port_states = read(PORT_STATES)
    normalized = read(NORMALIZED)
    catalog = read(CATALOG)
    checkpoint = read(CHECKPOINT)
    portfolio = read(PORTFOLIO)
    domains = build_domains()

    check(expansion.get("status") == "COMPLETE", "part19 expansion incomplete")
    summary = expansion["summary"]
    check(summary["support_rows"] == 15, "part19 support-row count")
    check(summary["port_feasible_state_assignments"] == 1716,
          "part19 port-state count")
    check(summary["exact_overlap_completions"] == 2599936,
          "part19 completion count")
    check(summary["after_forced_C4_support_BP"] == 8192,
          "part19 final raw count")
    check(summary["nonempty_support_rows"] == 1,
          "part19 final nonempty support rows")
    check(summary["local_graph_orbits"] == 88, "part19 orbit total")
    check(summary["forced_BP_Q_histogram"] == {"0": 4096, "4": 4096},
          "part19 final Q histogram")

    positive_rows = [row for row in expansion["rows"] if row["local_graph_orbits"]]
    check(len(positive_rows) == 1, "part19 positive-row uniqueness")
    row = positive_rows[0]
    reps = row["local_graph_representatives"]
    check(expansion["rows"].index(row) == 13, "part19 source row index")
    check(row["compression_orbit_index"] == 850, "part19 compression orbit")
    check(row["partition"] == [2, 2, 2, 1, 1, 1, 1], "part19 partition")
    check(row["Q_condition"] is None, "part19 unexpectedly conditional")
    check(row["after_forced_C4_support_BP"] == 8192, "row raw count")
    check(row["local_graph_orbits"] == len(reps) == 88, "row orbit count")
    check(row["distinct_local_symmetry_actions"] == 128, "row action count")
    check(row["orbit_size_histogram"] == {"64": 48, "128": 40},
          "declared orbit histogram")

    exceptional_items = row["exceptional_supports"]
    exceptional = tuple(tuple(item["support"]) for item in exceptional_items)
    deficits = tuple(item["deficit"] for item in exceptional_items)
    exceptional_set = frozenset(exceptional)
    deficit_map = dict(zip(exceptional, deficits))
    used_groups = tuple(sorted(set().union(*map(set, exceptional))))
    check(len(exceptional) == 7 and sum(deficits) == 10,
          "exceptional fibre/deficit total")
    check(used_groups == (0, 1, 2, 3, 4, 5), "used group set")

    all_supports = tuple(itertools.combinations(range(7), 2))
    all_deficits = {support: deficit_map.get(support, 0) for support in all_supports}
    stabilizer = []
    for image in itertools.permutations(range(7)):
        if all(all_deficits[tuple(sorted((image[a], image[b])))] ==
               all_deficits[(a, b)] for a, b in all_supports):
            stabilizer.append(image)
    check(len(stabilizer) == row["weighted_stabilizer_order"] == 2,
          "weighted stabilizer order")

    local_vertices = tuple(
        (2 * support[0] + first, 2 * support[1] + second)
        for support in exceptional
        for first, second in itertools.product((0, 1), repeat=2)
    )
    check(len(local_vertices) == len(set(local_vertices)) == 28,
          "local vertex catalog")
    actions = {}
    for image in stabilizer:
        for flip_bits in itertools.product((0, 1), repeat=len(used_groups)):
            flips = dict(zip(used_groups, flip_bits))
            mapping = {
                label: tuple(sorted(
                    2 * image[symbol // 2]
                    + ((symbol % 2) ^ flips[symbol // 2])
                    for symbol in label
                )) for label in local_vertices
            }
            actions.setdefault(tuple(mapping[v] for v in local_vertices), mapping)
    check(len(actions) == 128, "faithful stabilizer/sign-flip actions")

    state_by_edges = {
        deficit: {frozenset(state["edges"]): state for state in domains[deficit]}
        for deficit in set(deficits)
    }
    label_to_fibre_vertex = {}
    fibre_vertices = []
    for fibre_index, support in enumerate(exceptional):
        vertices = tuple(
            (2 * support[0] + first, 2 * support[1] + second)
            for first, second in itertools.product((0, 1), repeat=2)
        )
        fibre_vertices.append(vertices)
        for vertex_index, label in enumerate(vertices):
            label_to_fibre_vertex[label] = (fibre_index, vertex_index)

    feasible_port_row = next(
        item for item in port_states["rows"]
        if item["partition"] == row["partition"]
        and item["compression_orbit_index"] == row["compression_orbit_index"]
    )
    feasible_state_set = {
        tuple(item) for item in feasible_port_row["feasible_state_indices"]
    }
    check(len(feasible_state_set) == row["port_feasible_state_assignments"] == 80,
          "source feasible-state count")

    def analyse_graph(graph, detailed=False):
        expected_ports = Counter()
        used_ports = Counter()
        state_indices = []
        Q = 0
        internal = overlap = 0
        for fibre_index, (support, deficit, vertices) in enumerate(
                zip(exceptional, deficits, fibre_vertices)):
            selected = frozenset(
                tuple(sorted((u, v)))
                for u, v in itertools.combinations(range(4), 2)
                if tuple(sorted((vertices[u], vertices[v]))) in graph
            )
            state = state_by_edges[deficit].get(selected)
            check(state is not None, "non-catalog fibre state")
            if state is None:
                return None, None
            state_indices.append(state["state_index"])
            Q += state["Q"]
            internal += len(selected)
            for axis in (0, 1):
                for vertex, actual, needed in state["ports_by_axis"][axis]:
                    expected_ports[(fibre_index, axis, vertex, actual, needed)] += 1
        for u, v in graph:
            fibre_u, vertex_u = label_to_fibre_vertex[u]
            fibre_v, vertex_v = label_to_fibre_vertex[v]
            if fibre_u == fibre_v:
                continue
            support_u, support_v = exceptional[fibre_u], exceptional[fibre_v]
            check(not set(support_u).isdisjoint(support_v),
                  "disjoint edge in local graph")
            group = next(iter(set(support_u) & set(support_v)))
            axis_u, axis_v = support_u.index(group), support_v.index(group)
            actual_u, actual_v = u[axis_u] % 2, v[axis_v] % 2
            used_ports[(fibre_u, axis_u, vertex_u, actual_u, actual_v)] += 1
            used_ports[(fibre_v, axis_v, vertex_v, actual_v, actual_u)] += 1
            overlap += 1
        check(expected_ports == used_ports, "ports not exactly completed")
        check(internal == 18 and overlap == 20 and len(graph) == 38,
              "local edge decomposition")
        state_tuple = tuple(state_indices)
        check(state_tuple in feasible_state_set, "state tuple not port-feasible")
        if detailed:
            neighbours = {vertex: set() for vertex in local_vertices}
            for u, v in graph:
                neighbours[u].add(v)
                neighbours[v].add(u)
            for u, v in itertools.combinations(local_vertices, 2):
                target = 2 - len(set(u) & set(v))
                lhs = int(v in neighbours[u]) + len(neighbours[u] & neighbours[v])
                check(lhs <= target, "induced local pair upper violated")
            for u in local_vertices:
                own = set(u)
                for symbol in range(14):
                    target = 1 if symbol in own or (symbol ^ 1) in own else 2
                    check(sum(symbol in v for v in neighbours[u]) <= target,
                          "local BP-bin capacity violated")
        return state_tuple, Q

    representative_graphs = []
    for index, rep in enumerate(reps):
        graph = graph_from_edges(rep["edges"])
        check(len(graph) == len(rep["edges"]), f"rep {index}: duplicate edges")
        _state, Q = analyse_graph(graph, detailed=True)
        check(Q == rep["Q"], f"rep {index}: Q differs")
        representative_graphs.append(graph)

    all_graphs = set()
    orbit_sizes = []
    raw_Q = Counter()
    raw_states = Counter()
    intersections = 0
    for index, graph in enumerate(representative_graphs):
        orbit = {transform_graph(graph, mapping) for mapping in actions.values()}
        orbit_sizes.append(len(orbit))
        check(len(orbit) == reps[index]["orbit_size"],
              f"rep {index}: orbit size differs")
        intersections += len(all_graphs & orbit)
        for transformed in orbit - all_graphs:
            state_tuple, Q = analyse_graph(transformed, detailed=False)
            if state_tuple is not None:
                raw_states[state_tuple] += 1
                raw_Q[Q] += 1
        all_graphs.update(orbit)
    check(intersections == 0, "representative orbits intersect")
    check(len(all_graphs) == 8192, "orbit union is not 8192")
    check(sum(orbit_sizes) == 8192, "orbit weight sum")
    check(Counter(orbit_sizes) == Counter({64: 48, 128: 40}),
          "independent orbit histogram")
    check(raw_Q == Counter({0: 4096, 4: 4096}), "independent raw Q histogram")

    normalized_row = next(
        item for item in normalized["records"]
        if item["source_partition_index"] == 19
        and item["source_row_index"] == 13
        and item["compression_orbit_index"] == 850
    )
    norm_reps = normalized_row["representatives"]
    labels = all_outer_labels()
    label_index = {label: index for index, label in enumerate(labels)}
    normalized_matches = 0
    for index, (rep, norm) in enumerate(zip(reps, norm_reps)):
        expected_edges = frozenset(
            tuple(sorted((label_index[tuple(u)], label_index[tuple(v)])))
            for u, v in rep["edges"]
        )
        actual_edges = frozenset(
            tuple(sorted((int(u), int(v))))
            for u, v in norm["present_edges_outer_indices_zero_based"]
        )
        match = (
            norm["representative_id"] == index
            and norm["orbit_size"] == rep["orbit_size"]
            and norm["Q"] == rep["Q"]
            and norm["source_mask_hex"] == rep["mask_hex"]
            and actual_edges == expected_edges
        )
        check(match, f"normalized representative {index}")
        normalized_matches += match
    check(len(norm_reps) == 88, "normalized rep count")
    check(sum(rep["orbit_size"] for rep in norm_reps) == 8192,
          "normalized orbit weight")

    check(catalog["branch_count"] == 88, "fixed catalog branch count")
    check(catalog["covered_labelled_local_graphs"] == 8192,
          "fixed catalog orbit weight")
    check(len(catalog["branches"]) == 88, "fixed catalog branch list")
    for index, branch in enumerate(catalog["branches"]):
        rep = reps[index]
        check(branch["branch_index"] == index, f"catalog branch {index}: index")
        check(branch["source_row_index"] == 13, f"catalog branch {index}: row")
        check(branch["compression_orbit_index"] == 850,
              f"catalog branch {index}: compression orbit")
        check(branch["local_mask_hex"] == rep["mask_hex"],
              f"catalog branch {index}: mask")
        check(branch["local_orbit_size"] == rep["orbit_size"],
              f"catalog branch {index}: weight")
        check(branch["Q"] == rep["Q"], f"catalog branch {index}: Q")

    attempts = checkpoint["attempts"]
    check(checkpoint["catalog_size"] == 88, "checkpoint catalog size")
    check(set(attempts) == {str(index) for index in range(88)},
          "checkpoint branch coverage")
    latest = [attempts[str(index)][-1] for index in range(88)]
    check(all(len(attempts[str(index)]) == 1 for index in range(88)),
          "unexpected retry count")
    check(all(record["status"] == "UNSAT" for record in latest),
          "non-UNSAT terminal record")
    check(all(record["conflict_budget"] == 20000 for record in latest),
          "conflict budget differs")
    check(all(record.get("formal_proof_certificate") is None for record in latest),
          "unexpected proof certificate")

    contract = {
        "exceptional_fibres": 7,
        "ordinary_c4_fibres": 14,
        "fixed_non_disjoint_outer_pairs": 1806,
        "fixed_non_disjoint_true_edges": 94,
        "fixed_non_disjoint_false_edges": 1712,
        "fixed_local_internal_edges": 18,
        "fixed_local_overlap_edges": 20,
        "disjoint_edge_variables": 1680,
        "product_variables": 65520,
        "direct_product_terms": 7520,
        "constant_product_terms": 124,
        "disjoint_blocks": 105,
        "block_types": {
            "ordinary_exceptional": 48,
            "ordinary_ordinary": 46,
            "exceptional_exceptional": 11,
        },
        "ordinary_c4_block_equalities": 560,
        "BP_equalities": 1176,
        "outer_pair_equalities": 3486,
        "cardinality_equalities": 4662,
        "empty_clauses_before_solving": 0,
        "redundant_support_aggregate_rows": 0,
    }
    clause_histogram = Counter()
    variable_histogram = Counter()
    for index, record in enumerate(latest):
        meta = record.get("meta", {})
        for field, value in contract.items():
            check(meta.get(field) == value, f"branch {index}: CNF {field}")
        check(meta.get("branch_index") == index, f"branch {index}: meta index")
        check(meta.get("local_representative_index") == index,
              f"branch {index}: representative index")
        clause_histogram[meta.get("clauses")] += 1
        variable_histogram[meta.get("variables")] += 1
    check(sum(clause_histogram.values()) == 88 and None not in clause_histogram,
          "CNF clause-count coverage")
    check(sum(variable_histogram.values()) == 88 and None not in variable_histogram,
          "CNF variable-count coverage")
    check(portfolio["all_catalog_branches_terminal"] is True,
          "portfolio terminal flag")
    check(portfolio["cumulative_latest_status_counts"] == {"UNSAT": 88},
          "portfolio status summary")

    result = {
        "model": "independent unconditional E0=74 part19 local/fixed-SAT audit",
        "ok": not errors,
        "inputs": {path.name: sha256(path) for path in (
            EXPANSION, PORT_STATES, NORMALIZED, CATALOG, CHECKPOINT,
            PORTFOLIO, FIXED_SOURCE,
        )},
        "scope": {
            "partition_index": 19,
            "source_row_index": 13,
            "compression_orbit_index": 850,
            "conditional_Q_filter_used": False,
            "global_E0_74_catalog_complete": False,
        },
        "local_catalog": {
            "representatives": len(reps),
            "raw_orbit_union": len(all_graphs),
            "orbit_weight_sum": sum(orbit_sizes),
            "orbit_size_histogram": {
                str(key): value for key, value in sorted(Counter(orbit_sizes).items())
            },
            "faithful_symmetry_actions": len(actions),
            "orbit_intersections": intersections,
            "raw_Q_histogram": {
                str(key): value for key, value in sorted(raw_Q.items())
            },
            "distinct_port_state_tuples_in_survivors": len(raw_states),
            "normalized_explicit_edge_mask_Q_weight_matches": normalized_matches,
        },
        "fixed_cnf_contract": contract,
        "CNF_clause_count_histogram": {
            str(key): value for key, value in sorted(clause_histogram.items())
        },
        "CNF_variable_count_histogram": {
            str(key): value for key, value in sorted(variable_histogram.items())
        },
        "solver": {
            "engine": "CaDiCaL 1.9.5 via PySAT",
            "conflict_budget_per_branch": 20000,
            "branches": 88,
            "solver_terminal_UNSAT": 88,
            "SAT": 0,
            "UNKNOWN": 0,
            "maximum_conflicts": max(record["stats"]["conflicts"] for record in latest),
            "maximum_solve_seconds": max(record["solve_seconds"] for record in latest),
            "formal_proof_certificates_checked": 0,
        },
        "part20_extension": {
            "runner": str(FIXED_SOURCE),
            "usage": (
                "--source scratch_general_e74_local_expansion_part_20.json "
                "--tag part20_completed"
            ),
            "discovers_every_nonempty_completed row automatically": True,
        },
        "claim_boundary": (
            "This is an unconditional audit of the completed part19 local row, "
            "not a complete E0=74 census.  The 88 UNSAT answers are solver-terminal "
            "computational results with no independently checked DRAT/LRAT "
            "certificates, so they do not by themselves prove global E0=74 "
            "nonexistence."
        ),
        "existing_E74_local_discovery_source_read_or_imported": False,
        "shared_incremental_solver_required_for_UNSAT_count": False,
        "errors": errors,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": result["ok"],
        "local_catalog": result["local_catalog"],
        "solver": result["solver"],
        "clause_histogram": result["CNF_clause_count_histogram"],
        "error_count": len(errors),
    }, indent=2))


if __name__ == "__main__":
    main()
