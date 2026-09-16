"""Independent audit of the conditional E0=74 Q>=5 local/SAT artifacts.

The Q>=5 premise itself (including any external n3 argument) is deliberately
not re-established here.  This checks the finite conditional catalog: local
edge structure, symmetry orbits, matching-completion coverage, normalized SAT
catalog, branch assumptions, shared-CNF structural contract, and recorded
terminal statuses.  No E74 local-expansion discovery implementation is read or
imported.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path

from scratch_e74_independent_port import build_domains


PORT_AUDIT = Path("scratch_e74_independent_port_audit.json")
PORT_STATES = Path("scratch_e74_independent_feasible_states.json")
EXPANSION = Path("scratch_general_e74_q5_local_expansion.json")
REPRESENTATIVES = Path("scratch_general_e74_q5_local_graph_reps.json")
NORMALIZED = Path("scratch_general_e74_q5_incremental_records.json")
SAT = Path("scratch_general_e74_q5_incremental_sat.json")
OUTPUT = Path("scratch_e74_independent_q5_audit.json")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def all_outer_labels():
    return tuple(
        pair for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    )


def graph_from_symbol_edges(raw_edges):
    return frozenset(
        tuple(sorted((tuple(raw_u), tuple(raw_v))))
        for raw_u, raw_v in raw_edges
    )


def transform_graph(graph, vertex_map):
    return frozenset(
        tuple(sorted((vertex_map[u], vertex_map[v]))) for u, v in graph
    )


def main():
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    port_audit = read(PORT_AUDIT)
    port_states = read(PORT_STATES)
    expansion = read(EXPANSION)
    rep_data = read(REPRESENTATIVES)
    normalized = read(NORMALIZED)
    sat = read(SAT)
    domains = build_domains()

    check(port_audit.get("ok") is True, "independent port audit is not ok")
    independent_Q5_states = port_audit["exact_overlap_completions"][
        "Q_at_least_5_states"
    ]
    independent_Q5_completions = port_audit["exact_overlap_completions"][
        "Q_at_least_5_completions"
    ]
    check(independent_Q5_states == 89, "independent Q>=5 state count")
    check(independent_Q5_completions == 1461248,
          "independent Q>=5 completion count")

    summary = expansion["summary"]
    check(expansion.get("status") == "COMPLETE", "expansion not COMPLETE")
    check(expansion.get("Q_condition") == "Q>=5", "expansion Q condition")
    check(summary["support_rows"] == 11, "Q>=5 support rows")
    check(summary["port_feasible_state_assignments"] == independent_Q5_states,
          "Q>=5 state total versus independent port audit")
    check(summary["exact_overlap_completions"] == independent_Q5_completions,
          "Q>=5 completions versus independent port audit")
    check(summary["after_forced_C4_support_BP"] == 16384,
          "final raw local graph count")
    check(summary["nonempty_support_rows"] == 1, "final support row count")
    check(summary["local_graph_orbits"] == 188, "final orbit count")
    check(summary["forced_BP_Q_histogram"] == {"8": 16384},
          "final Q histogram")
    check(sum(row["port_feasible_state_assignments"] for row in expansion["rows"])
          == 89, "row state sum")
    check(sum(row["exact_overlap_completions"] for row in expansion["rows"])
          == 1461248, "row completion sum")
    check(sum(row["after_forced_C4_support_BP"] for row in expansion["rows"])
          == 16384, "row final survivor sum")

    check(rep_data.get("status") == "COMPLETE", "representatives not COMPLETE")
    check(rep_data.get("raw_graphs") == 16384, "representative raw count")
    check(rep_data.get("local_graph_orbits") == 188, "representative orbit count")
    check(len(rep_data["support_rows"]) == 1, "representative support rows")
    support_row = rep_data["support_rows"][0]
    reps = support_row["representatives"]
    check(support_row["partition"] == [2, 2, 2, 2, 1, 1],
          "surviving partition")
    check(support_row["compression_orbit_index"] == 54,
          "surviving compression orbit")
    check(support_row["raw_survivors"] == 16384, "row raw survivor count")
    check(support_row["orbit_count"] == len(reps) == 188,
          "row representative count")
    check(support_row["weighted_stabilizer_order"] == 8,
          "weighted stabilizer declaration")
    check(support_row["symmetry_actions"] == 128,
          "symmetry action declaration")

    exceptional_items = support_row["exceptional_supports"]
    exceptional = tuple(tuple(item["support"]) for item in exceptional_items)
    deficits = tuple(item["deficit"] for item in exceptional_items)
    exceptional_set = frozenset(exceptional)
    deficit_map = {support: deficit for support, deficit in zip(exceptional, deficits)}
    used_groups = tuple(sorted(set().union(*map(set, exceptional))))
    check(used_groups == (0, 1, 2, 3, 4), "used root groups")
    check(deficits == (2, 2, 1, 2, 2, 1), "deficit order")

    # Reconstruct the weighted S7 stabilizer and its faithful action on the 24
    # local vertices, then adjoin every independent sign flip on used groups.
    all_supports = tuple(itertools.combinations(range(7), 2))
    all_deficits = {support: deficit_map.get(support, 0) for support in all_supports}
    stabilizer = []
    for image in itertools.permutations(range(7)):
        if all(
            all_deficits[tuple(sorted((image[a], image[b])))] == all_deficits[(a, b)]
            for a, b in all_supports
        ):
            stabilizer.append(image)
    check(len(stabilizer) == 8, "independent weighted stabilizer order")

    local_vertices = tuple(
        label for support in exceptional for label in (
            (2 * support[0], 2 * support[1]),
            (2 * support[0], 2 * support[1] + 1),
            (2 * support[0] + 1, 2 * support[1]),
            (2 * support[0] + 1, 2 * support[1] + 1),
        )
    )
    check(len(local_vertices) == len(set(local_vertices)) == 24,
          "local vertex catalog")
    actions = {}
    for image in stabilizer:
        for flip_bits in itertools.product((0, 1), repeat=len(used_groups)):
            flips = dict(zip(used_groups, flip_bits))
            mapping = {}
            for label in local_vertices:
                mapped = tuple(sorted(
                    2 * image[symbol // 2]
                    + ((symbol % 2) ^ flips[symbol // 2])
                    for symbol in label
                ))
                mapping[label] = mapped
            action_key = tuple(mapping[label] for label in local_vertices)
            actions.setdefault(action_key, mapping)
    check(len(actions) == 128, "independent faithful symmetry action count")

    # Local state lookup uses the explicit E74 state-index crosswalk established
    # by the independent port audit.
    state_by_edges = {
        deficit: {
            frozenset(state["edges"]): state for state in domains[deficit]
        } for deficit in set(deficits)
    }

    def analyse_graph(graph, full=False):
        local_state_indices = []
        local_Q = 0
        internal_count = 0
        overlap_count = 0
        expected_ports = Counter()
        used_ports = Counter()
        label_to_fibre_vertex = {}
        for fibre_index, (support, deficit) in enumerate(zip(exceptional, deficits)):
            vertices = tuple(
                (2 * support[0] + first, 2 * support[1] + second)
                for first, second in itertools.product((0, 1), repeat=2)
            )
            for vertex_index, label in enumerate(vertices):
                label_to_fibre_vertex[label] = (fibre_index, vertex_index)
            internal_edges = frozenset(
                tuple(sorted((u, v)))
                for u, v in itertools.combinations(range(4), 2)
                if tuple(sorted((vertices[u], vertices[v]))) in graph
            )
            state = state_by_edges[deficit].get(internal_edges)
            check(state is not None, "graph has a non-catalog internal state")
            if state is None:
                return None
            local_state_indices.append(state["state_index"])
            local_Q += state["Q"]
            internal_count += len(internal_edges)
            for axis in (0, 1):
                for vertex, actual, needed in state["ports_by_axis"][axis]:
                    expected_ports[(fibre_index, axis, vertex, actual, needed)] += 1

        for u, v in graph:
            fibre_u, vertex_u = label_to_fibre_vertex[u]
            fibre_v, vertex_v = label_to_fibre_vertex[v]
            support_u, support_v = exceptional[fibre_u], exceptional[fibre_v]
            if fibre_u == fibre_v:
                continue
            check(not set(support_u).isdisjoint(support_v),
                  "local graph contains a disjoint-support edge")
            shared_group = next(iter(set(support_u) & set(support_v)))
            axis_u = support_u.index(shared_group)
            axis_v = support_v.index(shared_group)
            actual_u = (u[axis_u] % 2)
            actual_v = (v[axis_v] % 2)
            used_ports[(fibre_u, axis_u, vertex_u, actual_u, actual_v)] += 1
            used_ports[(fibre_v, axis_v, vertex_v, actual_v, actual_u)] += 1
            overlap_count += 1
        check(expected_ports == used_ports, "overlap edges do not exactly fill ports")
        check(internal_count == 14, "local internal edge count")
        check(overlap_count == 20, "local overlap edge count")
        check(len(graph) == 34, "local total edge count")
        check(local_Q == 8, "local graph Q is not 8")

        if full:
            neighbours = {vertex: set() for vertex in local_vertices}
            for u, v in graph:
                neighbours[u].add(v)
                neighbours[v].add(u)
            for u, v in itertools.combinations(local_vertices, 2):
                target = 2 - len(set(u) & set(v))
                lhs = int(v in neighbours[u]) + len(neighbours[u] & neighbours[v])
                check(lhs <= target, "local induced pair upper bound violated")
            for u in local_vertices:
                own = set(u)
                for symbol in range(14):
                    target = 1 if symbol in own or (symbol ^ 1) in own else 2
                    fixed = sum(symbol in v for v in neighbours[u])
                    check(fixed <= target, "local BP bin capacity violated")
        return tuple(local_state_indices)

    representative_graphs = []
    declared_weights = []
    for index, rep in enumerate(reps):
        graph = graph_from_symbol_edges(rep["edges"])
        check(len(graph) == len(rep["edges"]), f"rep {index}: duplicate edge")
        check(rep["Q"] == 8, f"rep {index}: declared Q")
        analyse_graph(graph, full=True)
        representative_graphs.append(graph)
        declared_weights.append(rep["orbit_size"])

    all_graphs = set()
    raw_state_histogram = Counter()
    orbit_sizes = []
    orbit_intersections = 0
    for index, graph in enumerate(representative_graphs):
        orbit = {
            transform_graph(graph, mapping) for mapping in actions.values()
        }
        orbit_sizes.append(len(orbit))
        check(len(orbit) == declared_weights[index],
              f"rep {index}: independently reconstructed orbit size")
        orbit_intersections += len(all_graphs & orbit)
        new_graphs = orbit - all_graphs
        for transformed in new_graphs:
            state_tuple = analyse_graph(transformed, full=False)
            if state_tuple is not None:
                raw_state_histogram[state_tuple] += 1
        all_graphs.update(orbit)
    check(orbit_intersections == 0, "representative orbits intersect")
    check(len(all_graphs) == 16384, "independent orbit union size")
    check(Counter(orbit_sizes) == Counter({32: 24, 64: 84, 128: 80}),
          "independent orbit-size histogram")
    check(sum(orbit_sizes) == 16384, "independent orbit weight sum")

    # The four independent Q=8 state tuples on this support row have exact
    # matching-completion multiplicities.  Their multiset must be precisely the
    # independently generated symmetry-orbit union above.
    port_row = next(
        row for row in port_states["rows"]
        if row["partition"] == [2, 2, 2, 2, 1, 1]
        and row["compression_orbit_index"] == 54
    )
    expected_raw_state_histogram = Counter()
    for state_tuple, Q, count in zip(
            port_row["feasible_state_indices"],
            port_row["Q_by_sorted_feasible_state"],
            port_row["completion_count_by_sorted_feasible_state"]):
        if Q >= 5:
            expected_raw_state_histogram[tuple(state_tuple)] += count
    check(len(expected_raw_state_histogram) == 4,
          "independent row54 Q>=5 state count")
    check(sum(expected_raw_state_histogram.values()) == 16384,
          "independent row54 Q>=5 completion sum")
    check(raw_state_histogram == expected_raw_state_histogram,
          "orbit union versus independent state/completion multiplicities")

    # Normalize the explicit symbol-labelled reps independently and compare all
    # 188 branches with the SAT input catalog.
    check(normalized.get("status") == "CONDITIONAL_PRIORITY_SUBCASE",
          "normalized conditional status")
    check(normalized.get("support_record_count") == 1,
          "normalized support record count")
    check(normalized.get("local_representative_count") == 188,
          "normalized representative count")
    check(normalized.get("labelled_local_graphs_represented") == 16384,
          "normalized labelled coverage")
    norm_row = normalized["records"][0]
    norm_reps = norm_row["representatives"]
    labels = all_outer_labels()
    label_index = {label: index for index, label in enumerate(labels)}
    check(len(labels) == 84, "outer label count")
    normalized_matches = 0
    for index, (rep, norm) in enumerate(zip(reps, norm_reps)):
        expected_edges = frozenset(
            tuple(sorted((label_index[tuple(u)], label_index[tuple(v)])))
            for u, v in rep["edges"]
        )
        normalized_edges = frozenset(
            tuple(sorted((int(u), int(v))))
            for u, v in norm["present_edges_outer_indices_zero_based"]
        )
        fields_match = (
            norm["representative_id"] == index
            and norm["orbit_size"] == rep["orbit_size"]
            and norm["Q"] == rep["Q"] == 8
            and norm["source_mask_hex"] == rep["mask_hex"]
            and normalized_edges == expected_edges
        )
        check(fields_match, f"normalized rep {index} differs")
        normalized_matches += fields_match
    check(len(norm_reps) == len(reps) == 188, "normalized rep list length")
    check(sum(rep["orbit_size"] for rep in norm_reps) == 16384,
          "normalized orbit weight sum")

    # Independently reconstruct the variable allocation and all 180 complete
    # local assumptions.  Variable allocation precedes auxiliary variables, so
    # a simple increasing counter reproduces the signed assumption words.
    supports84 = tuple(tuple(symbol // 2 for symbol in label) for label in labels)
    signs84 = tuple({symbol // 2: symbol % 2 for symbol in label} for label in labels)
    ordinary = frozenset(set(itertools.combinations(range(7), 2)) - exceptional_set)
    edge_variables = {}
    local_variables = {}
    disjoint_variables = {}
    local_overlap_blocks = set()
    disjoint_blocks = set()
    next_variable = 1
    for u, v in itertools.combinations(range(84), 2):
        A, B = supports84[u], supports84[v]
        local = (
            (A == B and A in exceptional_set)
            or (A != B and bool(set(A) & set(B))
                and A in exceptional_set and B in exceptional_set)
        )
        disjoint = set(A).isdisjoint(B)
        if not (local or disjoint):
            continue
        edge_variables[(u, v)] = next_variable
        if local:
            local_variables[(u, v)] = next_variable
            if A != B:
                local_overlap_blocks.add(tuple(sorted((A, B))))
        else:
            disjoint_variables[(u, v)] = next_variable
            disjoint_blocks.add(tuple(sorted((A, B))))
        next_variable += 1

    check(len(local_variables) == 180, "independent local variable count")
    check(sum(supports84[u] == supports84[v] for u, v in local_variables) == 36,
          "independent local same-fibre variables")
    check(len(local_overlap_blocks) == 9, "independent local overlap blocks")
    check(len(disjoint_variables) == 1680, "independent disjoint variables")
    check(len(disjoint_blocks) == 105, "independent disjoint blocks")
    check(len(edge_variables) == 1860, "independent total edge variables")

    high_high = high_low = low_low = 0
    for A, B in disjoint_blocks:
        if A in ordinary and B in ordinary:
            high_high += 1
        elif A in ordinary or B in ordinary:
            high_low += 1
        else:
            low_low += 1
    structural_contract = {
        "exceptional_fibre_count": 6,
        "ordinary_c4_fibre_count": 15,
        "local_vertex_count": 24,
        "representative_count": 188,
        "local_edge_variables": 180,
        "local_same_edge_variables": 36,
        "local_overlap_blocks": 9,
        "local_overlap_edge_variables": 144,
        "disjoint_edge_variables": 1680,
        "all_edge_variables": 1860,
        "disjoint_blocks": 105,
        "ordinary_ordinary_permutation_blocks": high_high,
        "ordinary_exceptional_one_sided_blocks": high_low,
        "exceptional_exceptional_unrestricted_disjoint_blocks": low_low,
        "exact_one_rows": 4 * high_high,
        "at_most_one_columns": 4 * (high_high + high_low),
        "redundant_support_aggregate_rows": 0,
        "bp_equalities": 1176,
        "outer_pair_equalities": 3486,
        "cardinality_equalities": 4662,
    }
    meta = sat["shared_cnf_meta"]
    for field, value in structural_contract.items():
        check(meta.get(field) == value, f"shared CNF contract {field}")
    check((high_high, high_low, low_low) == (51, 48, 6),
          "independent disjoint block classification")

    def edge_value(u, v):
        if u == v:
            return False
        if u > v:
            u, v = v, u
        if (u, v) in edge_variables:
            return edge_variables[(u, v)]
        A, B = supports84[u], supports84[v]
        if A == B:
            check(A in ordinary, "unrepresented exceptional same edge")
            return sum(signs84[u][g] != signs84[v][g] for g in A) == 1
        check(bool(set(A) & set(B)), "unrepresented disjoint edge")
        return False

    product_variables = direct_terms = constant_terms = 0
    pair_targets = Counter()
    empty_exact_rows = 0
    # All BP target rows have a representable exact cardinality.
    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            expressions = [edge_value(u, v) for v, other in enumerate(labels)
                           if u != v and symbol in other]
            wanted = 1 if symbol in own or (symbol ^ 1) in own else 2
            fixed = sum(value is True for value in expressions)
            variables = sum(type(value) is int for value in expressions)
            empty_exact_rows += not (fixed <= wanted <= fixed + variables)
    for u, v in itertools.combinations(range(84), 2):
        expressions = [edge_value(u, v)]
        for w in range(84):
            if w in (u, v):
                continue
            left, right = edge_value(u, w), edge_value(v, w)
            if left is False or right is False:
                continue
            if left is True and right is True:
                expressions.append(True)
                constant_terms += 1
            elif left is True:
                expressions.append(right)
                direct_terms += 1
            elif right is True:
                expressions.append(left)
                direct_terms += 1
            elif left == right:
                expressions.append(left)
                direct_terms += 1
            else:
                expressions.append((left, right))
                product_variables += 1
        wanted = 2 - len(set(labels[u]) & set(labels[v]))
        pair_targets[wanted] += 1
        fixed = sum(value is True for value in expressions)
        variables = sum(value is not False and value is not True for value in expressions)
        empty_exact_rows += not (fixed <= wanted <= fixed + variables)
    check(product_variables == meta["product_variables"] == 82440,
          "independent product helper count")
    check(direct_terms == meta["direct_product_terms"] == 4800,
          "independent direct product term count")
    check(constant_terms == meta["constant_product_terms"] == 60,
          "independent constant product term count")
    check({str(k): v for k, v in sorted(pair_targets.items())} ==
          meta["pair_target_histogram"], "independent pair target histogram")
    check(empty_exact_rows == meta["empty_clauses_before_assumptions"] == 0,
          "exact-row representability before assumptions")

    sat_records = sat["records"]
    assumption_summaries = meta["branch_assumption_summaries"]
    check(len(sat_records) == len(assumption_summaries) == len(norm_reps) == 188,
          "SAT/assumption/catalog length")
    assumption_hash_matches = 0
    core_subset_matches = 0
    for index, (norm, record, declared) in enumerate(
            zip(norm_reps, sat_records, assumption_summaries)):
        present = frozenset(
            tuple(sorted((int(u), int(v))))
            for u, v in norm["present_edges_outer_indices_zero_based"]
        )
        check(present <= set(local_variables), f"branch {index}: nonlocal present edge")
        assumptions = tuple(
            variable if pair in present else -variable
            for pair, variable in sorted(local_variables.items())
        )
        assumption_hash = hashlib.sha256(
            " ".join(map(str, assumptions)).encode("ascii")
        ).hexdigest().upper()
        expected_fields = {
            "branch_index": index,
            "representative_id": index,
            "orbit_size": norm["orbit_size"],
            "assumption_count": 180,
            "positive_assumptions": 34,
            "negative_assumptions": 146,
            "assumption_sha256": assumption_hash,
        }
        for field, value in expected_fields.items():
            check(record.get(field) == value, f"branch {index}: record {field}")
            check(declared.get(field) == value, f"branch {index}: summary {field}")
        assumption_hash_matches += record.get("assumption_sha256") == assumption_hash
        core = tuple(record.get("assumption_core", ()))
        valid_core = (
            len(core) == record.get("assumption_core_size")
            and sum(value > 0 for value in core) == record.get("assumption_core_positive")
            and sum(value < 0 for value in core) == record.get("assumption_core_negative")
            and set(core) <= set(assumptions)
        )
        check(valid_core, f"branch {index}: assumption core metadata/subset")
        core_subset_matches += valid_core
        check(record.get("status") == record.get("logical_status") == "UNSAT",
              f"branch {index}: terminal status")
        check(record.get("resolution") == "CADICAL",
              f"branch {index}: resolution")
        check(record.get("formal_proof_certificate") is None,
              f"branch {index}: unexpected proof certificate")

    check(sat.get("status") == "UNSAT", "SAT top-level status")
    check(sat.get("checkpoint_complete") is True, "SAT checkpoint incomplete")
    check(sat.get("completed_branch_count") == 188, "SAT completed branches")
    check(sat.get("next_branch_index") is None, "SAT next branch")
    check(sat.get("solver_session_count") == 1, "SAT solver sessions")
    check(sat.get("direct_solver_calls") == 188, "SAT direct calls")
    check(sat.get("direct_solver_unsat_count") == 188, "SAT direct UNSAT count")
    check(sat.get("core_covered_unsat_count") == 0, "SAT core-covered count")
    check(sat.get("unknown_count") == 0, "SAT UNKNOWN count")

    result = {
        "model": "independent audit of conditional E0=74 Q>=5 local/SAT artifacts",
        "ok": not errors,
        "inputs": {
            path.name: sha256(path) for path in (
                PORT_AUDIT, PORT_STATES, EXPANSION, REPRESENTATIVES, NORMALIZED, SAT
            )
        },
        "conditional_scope": {
            "Q_condition": "Q>=5",
            "external_n3_premise_reenacted": False,
            "unconditional_E0_74_claim_permitted": False,
            "warning": normalized.get("premise_warning"),
        },
        "solver_free_counts": {
            "independent_Q_at_least_5_states": independent_Q5_states,
            "independent_Q_at_least_5_matching_completions":
                independent_Q5_completions,
            "final_raw_local_graphs": len(all_graphs),
            "all_final_Q": 8,
            "local_graph_orbits": len(reps),
            "orbit_weight_sum": sum(orbit_sizes),
            "orbit_size_histogram": {
                str(key): value for key, value in sorted(Counter(orbit_sizes).items())
            },
            "faithful_symmetry_actions": len(actions),
            "representative_orbit_intersections": orbit_intersections,
            "raw_state_completion_histogram_matches":
                raw_state_histogram == expected_raw_state_histogram,
        },
        "normalized_catalog": {
            "representatives": len(norm_reps),
            "labelled_local_graphs": sum(rep["orbit_size"] for rep in norm_reps),
            "explicit_edge_mask_Q_weight_matches": normalized_matches,
        },
        "shared_cnf_contract": {
            **structural_contract,
            "product_variables": product_variables,
            "direct_product_terms": direct_terms,
            "constant_product_terms": constant_terms,
            "pair_target_histogram": {
                str(key): value for key, value in sorted(pair_targets.items())
            },
            "empty_exact_rows_before_assumptions": empty_exact_rows,
        },
        "assumption_audit": {
            "branches": len(sat_records),
            "complete_local_literals_per_branch": 180,
            "positive_per_branch": 34,
            "negative_per_branch": 146,
            "independently_recomputed_hashes_matched": assumption_hash_matches,
            "recorded_cores_are_subsets_of_full_branch_assumptions": core_subset_matches,
        },
        "recorded_solver_result": {
            "solver": sat.get("solver"),
            "branches": len(sat_records),
            "solver_terminal_UNSAT": sum(row.get("status") == "UNSAT"
                                           for row in sat_records),
            "SAT": sum(row.get("status") == "SAT" for row in sat_records),
            "UNKNOWN": sum(row.get("status") == "UNKNOWN" for row in sat_records),
            "formal_proof_certificates_checked": 0,
        },
        "claim_boundary": (
            "The 188/188 UNSAT statuses are recorded CaDiCaL terminal results "
            "without independently checked proof certificates.  They apply only "
            "to the externally premised Q>=5 conditional subcase.  This audit "
            "does not reenact the external n3 premise and does not exclude E0=74."
        ),
        "existing_E74_local_expansion_discovery_source_read_or_imported": False,
        "errors": errors,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": result["ok"],
        "solver_free": result["solver_free_counts"],
        "normalized": result["normalized_catalog"],
        "assumptions": result["assumption_audit"],
        "solver": result["recorded_solver_result"],
        "conditional_scope": result["conditional_scope"],
        "error_count": len(errors),
    }, indent=2))


if __name__ == "__main__":
    main()
