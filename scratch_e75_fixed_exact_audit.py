"""Audit the independent E0=75 fixed-local catalog and terminal SAT sweep."""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

from scratch_general_exact_sat import coordinates


SOURCE = Path("scratch_general_e75_local_graph_reps.json")
SOURCE_AUDIT = Path("scratch_general_e75_reps_check.json")
SHARED_CATALOG = Path("scratch_general_e75_incremental_records.json")
SHARED_SWEEP = Path("scratch_e75_incremental_sweep.json")
CATALOG = Path("scratch_e75_fixed_exact_catalog.json")
CHECKPOINT = Path("scratch_e75_fixed_exact_checkpoint.json")
PORTFOLIO = Path("scratch_e75_fixed_exact_portfolio.json")
MODEL_SOURCE = Path("scratch_e75_fixed_exact_sat.py")
OUTPUT = Path("scratch_e75_fixed_exact_audit.json")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    source = read(SOURCE)
    source_audit = read(SOURCE_AUDIT)
    shared = read(SHARED_CATALOG)
    shared_sweep = read(SHARED_SWEEP)
    catalog = read(CATALOG)
    checkpoint = read(CHECKPOINT)
    portfolio = read(PORTFOLIO)

    check(source_audit.get("status") == "VERIFIED", "source audit not VERIFIED")
    check(source_audit.get("support_rows_checked") == 6, "source audit row count")
    check(source_audit.get("orbits_checked") == 352, "source audit orbit count")
    check(source_audit.get("raw_graphs_checked") == 110592, "source audit raw count")
    check(source.get("status") == "COMPLETE", "source catalog not COMPLETE")
    check(source.get("local_graph_orbits") == 352, "source orbit count")
    check(source.get("raw_graphs") == 110592, "source raw count")

    labels, label_index, _full_variables, _full_edge = coordinates()
    supports = tuple(tuple(symbol // 2 for symbol in label) for label in labels)
    support_list = tuple(itertools.combinations(range(7), 2))

    independent = {}
    independent_order = []
    row_orbit_counts = []
    row_raw_counts = []
    local_invariant_counts = Counter()
    for row_index, row in enumerate(source["support_rows"]):
        deficits = {
            tuple(item["support"]): item["deficit"]
            for item in row["exceptional_supports"]
        }
        exceptional = frozenset(deficits)
        check(sum(deficits.values()) == 9, f"row {row_index}: deficit sum")
        check(len(exceptional) in (8, 9), f"row {row_index}: exceptional count")
        row_orbit_counts.append(len(row["representatives"]))
        row_raw_counts.append(sum(rep["orbit_size"] for rep in row["representatives"]))
        for rep_index, rep in enumerate(row["representatives"]):
            key = (
                tuple(row["partition"]),
                row["compression_orbit_index"],
                rep["mask_hex"],
            )
            check(key not in independent, f"duplicate independent cross-key {key}")
            edges = set()
            internal = Counter()
            overlap = 0
            for raw_u, raw_v in rep["edges"]:
                u = label_index[tuple(raw_u)]
                v = label_index[tuple(raw_v)]
                pair = tuple(sorted((u, v)))
                check(u != v, f"branch {len(independent_order)}: loop")
                check(pair not in edges, f"branch {len(independent_order)}: duplicate edge")
                edges.add(pair)
                A, B = supports[u], supports[v]
                check(A in exceptional and B in exceptional,
                      f"branch {len(independent_order)}: edge outside exceptional fibres")
                if A == B:
                    internal[A] += 1
                else:
                    check(not set(A).isdisjoint(B),
                          f"branch {len(independent_order)}: disjoint local edge")
                    overlap += 1
            for support, deficit in deficits.items():
                check(internal[support] == 4 - deficit,
                      f"branch {len(independent_order)}: fibre internal edge count")
            check(overlap == 18, f"branch {len(independent_order)}: overlap != 18")
            check(len(edges) == len(rep["edges"]),
                  f"branch {len(independent_order)}: edge cardinality")
            independent[key] = {
                "source_row_index": row_index,
                "representative_index": rep_index,
                "orbit_size": rep["orbit_size"],
                "edges": frozenset(edges),
                "exceptional_count": len(exceptional),
                "internal": sum(internal.values()),
                "overlap": overlap,
                "deficits": deficits,
            }
            independent_order.append(key)
            local_invariant_counts[(len(exceptional), sum(internal.values()), overlap)] += 1

    check(row_orbit_counts == [128, 64, 64, 32, 24, 40], "source row orbit split")
    check(row_raw_counts == [8192, 8192, 4096, 8192, 65536, 16384],
          "source row raw split")
    check(len(independent) == 352, "independent key count")
    check(sum(item["orbit_size"] for item in independent.values()) == 110592,
          "independent orbit weight sum")

    # Cross-check the independent symbol-label source against the normalized
    # catalog consumed by the shared incremental implementation.  The key is
    # intrinsic: partition, compression orbit, and canonical local mask.
    shared_map = {}
    shared_row_counts = []
    shared_raw_counts = []
    for row_index, row in enumerate(shared["records"]):
        shared_row_counts.append(len(row["representatives"]))
        shared_raw_counts.append(sum(rep["orbit_size"] for rep in row["representatives"]))
        check(row["source_row_index"] == row_index, f"shared row {row_index}: source index")
        for rep_index, rep in enumerate(row["representatives"]):
            key = (
                tuple(row["partition"]),
                row["compression_orbit_index"],
                rep["source_mask_hex"],
            )
            check(key not in shared_map, f"duplicate shared cross-key {key}")
            edges = frozenset(
                tuple(sorted((int(raw[0]), int(raw[1]))))
                for raw in rep["present_edges_outer_indices_zero_based"]
            )
            check(rep["representative_id"] == rep_index,
                  f"shared row {row_index} representative id")
            shared_map[key] = {
                "source_row_index": row_index,
                "representative_index": rep_index,
                "orbit_size": rep["orbit_size"],
                "edges": edges,
            }
    check(set(independent) == set(shared_map), "shared/independent cross-key sets differ")
    cross_key_matches = 0
    local_edge_matches = 0
    orbit_weight_matches = 0
    for key, own in independent.items():
        other = shared_map.get(key)
        if other is None:
            continue
        cross_key_matches += 1
        if own["edges"] == other["edges"]:
            local_edge_matches += 1
        else:
            errors.append(f"local edges differ for {key}")
        if own["orbit_size"] == other["orbit_size"]:
            orbit_weight_matches += 1
        else:
            errors.append(f"orbit weight differs for {key}")
    check(shared_row_counts == row_orbit_counts, "shared row orbit split")
    check(shared_raw_counts == row_raw_counts, "shared row raw split")
    check(cross_key_matches == 352, "cross-key match count")
    check(local_edge_matches == 352, "local edge match count")
    check(orbit_weight_matches == 352, "orbit weight match count")

    # Check the compact catalog preserves the same branch order and weights.
    catalog_branches = catalog["branches"]
    check(catalog.get("branch_count") == 352, "fixed catalog count")
    check(catalog.get("covered_labelled_local_graphs") == 110592,
          "fixed catalog raw coverage")
    check(len(catalog_branches) == 352, "fixed catalog branch list")
    for index, branch in enumerate(catalog_branches):
        key = independent_order[index]
        own = independent[key]
        check(branch["branch_index"] == index, f"catalog branch {index}: index")
        check(branch["source_row_index"] == own["source_row_index"],
              f"catalog branch {index}: source row")
        check(branch["local_representative_index"] == own["representative_index"],
              f"catalog branch {index}: representative index")
        check(branch["local_mask_hex"] == key[2], f"catalog branch {index}: mask")
        check(branch["local_orbit_size"] == own["orbit_size"],
              f"catalog branch {index}: orbit weight")
        check(branch["local_edge_count"] == len(own["edges"]),
              f"catalog branch {index}: edge count")

    attempts = checkpoint.get("attempts", {})
    check(checkpoint.get("catalog_size") == 352, "checkpoint catalog size")
    check(set(attempts) == {str(index) for index in range(352)},
          "checkpoint branch coverage")
    all_attempts = [attempt for history in attempts.values() for attempt in history]
    first_attempts = [attempts[str(index)][0] for index in range(352)]
    retry_attempts = [attempts[str(index)][1] for index in range(352)
                      if len(attempts[str(index)]) == 2]
    check(all(len(history) in (1, 2) for history in attempts.values()),
          "unexpected attempt multiplicity")
    check(len(all_attempts) == 450, "total attempt count")
    check(Counter(item["status"] for item in first_attempts) ==
          Counter({"UNSAT": 254, "UNKNOWN": 98}), "first pass statuses")
    check(all(item["conflict_budget"] == 20000 for item in first_attempts),
          "first pass conflict budget")
    check(len(retry_attempts) == 98, "retry count")
    check(all(item["status"] == "UNSAT" for item in retry_attempts),
          "retry status")
    check(all(item["conflict_budget"] == 200000 for item in retry_attempts),
          "retry conflict budget")
    check(all(attempts[str(index)][0]["status"] == "UNKNOWN"
              for index in range(352) if len(attempts[str(index)]) == 2),
          "retried a non-UNKNOWN branch")

    latest = [attempts[str(index)][-1] for index in range(352)]
    check(all(item["status"] == "UNSAT" for item in latest), "latest statuses")
    check(not any(item["status"].startswith("SAT") for item in all_attempts),
          "SAT status occurred")
    check(all(item.get("formal_proof_certificate") is None for item in all_attempts),
          "unexpected proof certificate field")

    for index, record in enumerate(latest):
        meta = record.get("meta") or {}
        key = independent_order[index]
        own = independent[key]
        exceptional = frozenset(own["deficits"])
        high = frozenset(set(support_list) - set(exceptional))
        block_types = Counter()
        for A, B in itertools.combinations(support_list, 2):
            if not set(A).isdisjoint(B):
                continue
            if A in high and B in high:
                block_types["high_high"] += 1
            elif A in high or B in high:
                block_types["high_low"] += 1
            else:
                block_types["low_low"] += 1
        forced_rows = 8 * block_types["high_high"] + 4 * block_types["high_low"]
        expected = {
            "branch_index": index,
            "source_row_index": own["source_row_index"],
            "local_representative_index": own["representative_index"],
            "local_orbit_size": own["orbit_size"],
            "exceptional_fibres": own["exceptional_count"],
            "ordinary_c4_fibres": 21 - own["exceptional_count"],
            "total_incident_deficit": 9,
            "fixed_local_internal_edges": own["internal"],
            "fixed_local_overlap_edges": 18,
            "edge_variables": 1680,
            "product_variables": 65520,
            "disjoint_blocks": 105,
            "ordinary_c4_block_equalities": forced_rows,
            "BP_equalities": 1176,
            "outer_pair_equalities": 3486,
            "cardinality_equalities": 4662,
            "redundant_support_aggregate_rows": 0,
        }
        for field, value in expected.items():
            check(meta.get(field) == value, f"branch {index}: meta {field}")
        check(meta.get("block_types") == dict(block_types),
              f"branch {index}: block types")
        check(meta.get("variables", 0) > 0 and meta.get("clauses", 0) > 0,
              f"branch {index}: empty CNF")

    check(portfolio.get("all_352_terminal") is True, "portfolio terminal flag")
    check(portfolio.get("cumulative_latest_count") == 352,
          "portfolio cumulative count")
    check(portfolio.get("cumulative_latest_status_counts") == {"UNSAT": 352},
          "portfolio cumulative status")
    check(portfolio.get("invocation_status_counts") == {"UNSAT": 98},
          "portfolio retry status")
    check(portfolio.get("proof_status") ==
          "no independently checked UNSAT certificates", "portfolio proof boundary")

    check(shared.get("local_representative_count") == 352,
          "shared catalog representative count")
    check(shared.get("labelled_local_graphs_represented") == 110592,
          "shared catalog raw coverage")
    check(shared_sweep.get("status") == "UNSAT", "shared sweep status")
    check(shared_sweep.get("completed_representative_count") == 352,
          "shared sweep completed count")
    check(all(row.get("unknown_count") == 0 and row.get("sat_count") == 0
              for row in shared_sweep["records"]), "shared sweep SAT/UNKNOWN")

    result = {
        "model": "audit of independent E0=75 fixed-local exact SAT portfolio",
        "ok": not errors,
        "inputs": {
            path.name: sha256(path)
            for path in (
                SOURCE, SOURCE_AUDIT, SHARED_CATALOG, SHARED_SWEEP,
                CATALOG, CHECKPOINT, PORTFOLIO, MODEL_SOURCE,
            )
        },
        "catalog": {
            "support_rows": 6,
            "row_orbit_counts": row_orbit_counts,
            "row_labelled_counts": row_raw_counts,
            "local_graph_orbits": len(independent),
            "labelled_local_graphs_covered": sum(
                item["orbit_size"] for item in independent.values()
            ),
            "local_invariant_histogram": {
                f"exceptional={key[0]},internal={key[1]},overlap={key[2]}": value
                for key, value in sorted(local_invariant_counts.items())
            },
        },
        "shared_incremental_catalog_crosscheck": {
            "catalog": str(SHARED_CATALOG),
            "intrinsic_cross_key": [
                "partition", "compression_orbit_index", "canonical_local_mask_hex"
            ],
            "cross_keys_matched": cross_key_matches,
            "local_edge_lists_matched": local_edge_matches,
            "orbit_weights_matched": orbit_weight_matches,
            "row_orbit_counts_match": shared_row_counts == row_orbit_counts,
            "row_labelled_counts_match": shared_raw_counts == row_raw_counts,
        },
        "cnf_contract": {
            "fresh_fixed_local_cnf_per_branch": True,
            "disjoint_edge_variables_per_branch": 1680,
            "product_equivalences_per_branch": 65520,
            "BP_equalities_per_branch": 1176,
            "outer_pair_equalities_per_branch": 3486,
            "redundant_support_aggregate_rows": 0,
            "ordinary_c4_block_policy": {
                "high_high": "both directions",
                "high_low": "high side only",
                "low_low": "none",
            },
        },
        "solver": {
            "engine": portfolio.get("solver"),
            "first_pass": {"conflict_budget": 20000, "UNSAT": 254, "UNKNOWN": 98},
            "second_pass_unknown_only": {
                "conflict_budget": 200000, "attempted": 98,
                "UNSAT": 98, "UNKNOWN": 0, "SAT": 0,
            },
            "latest_terminal": {"UNSAT": 352, "UNKNOWN": 0, "SAT": 0},
            "total_attempts": len(all_attempts),
            "formal_proof_certificates_checked": 0,
        },
        "independent_vs_shared_terminal_agreement": {
            "independent": "352/352 solver-terminal UNSAT",
            "shared_incremental": "352/352 covered UNSAT",
            "agree": shared_sweep.get("status") == "UNSAT",
        },
        "claim_boundary": (
            "This is exhaustive catalog coverage plus solver-terminal UNSAT agreement. "
            "No DRAT/LRAT proof certificates were generated or independently checked, "
            "so it is a reproducible finite computation, not a certificate-backed proof."
        ),
        "errors": errors,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": result["ok"],
        "crosscheck": result["shared_incremental_catalog_crosscheck"],
        "solver": result["solver"],
        "error_count": len(errors),
    }, indent=2))


if __name__ == "__main__":
    main()
