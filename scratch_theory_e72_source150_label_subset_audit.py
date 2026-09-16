"""Independent six-profile positive audit; no research producer or solver.

Local domains use the prior independent common-neighbour delta audit. Quotas
are rechecked by direct seven-coordinate convolution over all 21 target fibres,
not the producer's exceptional/ordinary split. All six local models are replayed.
"""

from fractions import Fraction as F
import hashlib
import itertools as it
import json
from pathlib import Path
import time

import scratch_theory_e71_degree_moment_lp_audit as exact
import scratch_theory_e71_label_subset_moment_audit as partial

CERT = Path("scratch_theory_e72_source150_label_subset_probe.json")
CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
FROZEN = Path("scratch_theory_e72_source150_degree_moment_applicability.json")
OUTPUT = Path("scratch_theory_e72_source150_label_subset_audit.json")
WANTED = {(150, 0, 3), (150, 1, 0), (150, 3, 3), (150, 9, 0), (150, 10, 0), (150, 11, 0)}


def quota_all_targets(position, degrees, subsets):
    support = exact.SUPPORTS[position // 4]
    quota = tuple(1 if group in support else 2 for group in range(7))
    assert tuple(sum(degrees[target] for target in range(21) if group in exact.SUPPORTS[target]) for group in range(7)) == tuple(2 * value for value in quota)
    states = {(0,) * 7}
    maximum = 1
    for target in range(21):
        increments = set()
        for bits in subsets[target]:
            if bits.bit_count() != degrees[target]:
                continue
            increments.add(tuple(sum(2 * group in exact.LABELS[4 * target + corner] for corner in range(4) if bits >> corner & 1) for group in range(7)))
        assert increments
        next_states = set()
        for state in states:
            for increment in increments:
                value = tuple(a + b for a, b in zip(state, increment))
                if all(a <= b for a, b in zip(value, quota)):
                    next_states.add(value)
        states = next_states
        maximum = max(maximum, len(states))
        assert len(states) <= 972
    return quota in states, maximum


def reconstruct_model(entry, profile, stored, blocks, subsets):
    exceptional, compression, gram = exact.reconstruct(entry, profile)
    pivots, coordinates = exact.principal_coordinates(gram)
    raw = exact.all_raw_domains(compression, pivots, coordinates)
    internal = exact.internal_degrees(entry, exceptional, compression)
    assert len(pivots) == 2
    pairs = tuple(it.combinations_with_replacement(range(2), 2))
    degree_sets = [[{bits.bit_count() for bits in choices} for choices in row] for row in subsets]
    columns, variables, domains, degree_rows = [], [], [], []
    raw_position_count = 0
    for position in range(84):
        source, corner = divmod(position, 4)
        assert internal[source][corner] == sum(corner in edge for edge in blocks[source])
        accepted = []
        for pivot, degrees in raw[source]:
            if degrees[source] != internal[source][corner]:
                continue
            raw_position_count += 1
            if any(degree not in degree_sets[position][target] for target, degree in enumerate(degrees)):
                continue
            accepted.append(list(pivot))
            column = [0] * 129
            column[position] = 1
            column[84 + 2 * source:86 + 2 * source] = pivot
            column[126:] = [pivot[a] * pivot[b] for a, b in pairs]
            columns.append(column)
            variables.append({"position": position, "pivot": list(pivot)})
            degree_rows.append(degrees)
        domains.append(accepted)
    matrix = list(map(list, zip(*columns)))
    target = [1] * 84 + [0] * 42 + [4 * gram[pivots[a]][pivots[b]] for a, b in pairs]
    digest = hashlib.sha256(json.dumps([matrix, target], separators=(",", ":")).encode()).hexdigest()
    metadata = {"rank_K4": 2, "pivot_supports": [list(exact.SUPPORTS[i]) for i in pivots],
                "raw_row_patterns": sum(map(len, raw)), "raw_internal_degree_position_rows": raw_position_count,
                "retained_position_rows": len(variables), "empty_positions": [i for i, row in enumerate(domains) if not row],
                "domains_by_position": domains, "variables": variables, "matrix_sha256": digest}
    assert metadata == stored["model"]
    principal = [[4 * gram[a][b] for b in pivots] for a in pivots]
    lifted = exact.product(exact.product(list(zip(*coordinates)), principal), coordinates)
    assert lifted == [[4 * value for value in row] for row in gram]
    return matrix, target, variables, degree_rows


def primal(matrix, target, record):
    digest = hashlib.sha256(json.dumps([matrix, target], separators=(",", ":")).encode()).hexdigest()
    assert digest == record["matrix_sha256"]
    assert record["exact_integer_certificate"] is None
    assert record["exact_feasible_witness"] is not None
    weights = [F(0)] * len(matrix[0])
    seen = set()
    for index, value in record["exact_feasible_witness"]["nonzero_weights"]:
        assert index not in seen and 0 <= index < len(weights)
        seen.add(index)
        weights[index] = F(value)
        assert weights[index] > 0
    assert [sum(a * b for a, b in zip(row, weights)) for row in matrix] == target
    return len(seen)


def main():
    started = time.monotonic()
    certificate, frozen, catalog, mining = map(exact.read, (CERT, FROZEN, CATALOG, exact.MINING))
    for path, digest in certificate["inputs_sha256"].items():
        assert exact.sha(Path(path)) == digest, path
    assert {tuple(row["key"]) for row in frozen["rows"]} == WANTED
    assert len(certificate["rows"]) == len(certificate["local_models"]) == 6
    assert {tuple(row["key"]) for row in certificate["rows"]} == WANTED
    entries = {exact.macro_key(row): row for row in catalog["macro_entries"] if row["signature_stabilizer_canonical"]}
    profiles = {(exact.macro_key(row), row["parameter"]): row for row in mining["profile_rows"]["72"] if exact.macro_key(row) in WANTED}
    assert len(profiles) == 6
    local_models = {tuple(row["key"]): row for row in certificate["local_models"]}
    exact.ordinary_internal_theorem()
    exact.fibre_incidence_geometry()
    rows = []
    for stored in certificate["rows"]:
        key = tuple(stored["key"])
        entry, profile = entries[key], profiles[(key, stored["parameter"])]
        assert stored["coverage"] == int(entry["signature_orbit_labelled_coverage"])
        blocks, subsets, local_stats = partial.local_domains(entry, local_models[key])
        matrix, target, variables, degree_rows = reconstruct_model(entry, profile, stored, blocks, subsets)
        decisions, max_states = [], 0
        for variable, degree_row in zip(variables, degree_rows):
            position = variable["position"]
            accepted, maximum = quota_all_targets(position, degree_row, subsets[position])
            decisions.append(accepted)
            max_states = max(max_states, maximum)
        keep = [i for i, accepted in enumerate(decisions) if accepted]
        assert decisions == stored["quota_row_decisions"]
        assert keep == stored["quota_retained_variable_indices"]
        assert len(keep) == len(variables) == 132
        subset_weights = primal(matrix, target, stored["subset"])
        reduced = [[row[i] for i in keep] for row in matrix]
        quota_weights = primal(reduced, target, stored["quota"])
        rows.append({"key": list(key), "parameter": profile["parameter"], "coverage": stored["coverage"],
                     **local_stats, "all_position_domains_independently_reconstructed": True,
                     "raw_subset_quota_position_rows": 132, "all_quota_decisions_independently_replayed": True,
                     "direct_all_target_quota_DP_max_states": max_states,
                     "subset_positive_rational_weights": subset_weights,
                     "quota_positive_rational_weights": quota_weights,
                     "exact_both_primal_witnesses_pass": True, "full_21_coordinate_Gram_lift_pass": True})
        print(json.dumps({"key": list(key), "independent_local_subset_checks": local_stats["partial_rows_checked"],
                          "independent_quota_rows": len(keep), "exact_both_primal_witnesses_pass": True}), flush=True)
    assert sum(row["coverage"] for row in rows) == 40960
    result = {"status": "INDEPENDENT_E72_SOURCE150_LABEL_SUBSET_QUOTA_POSITIVE_AUDIT_PASS",
              "research_producer_imported": False, "solver_used": False,
              "inputs_sha256": {str(path): exact.sha(path) for path in (CERT, FROZEN, CATALOG, exact.MINING, Path(exact.__file__), Path(partial.__file__))},
              "rows": rows, "fully_audited_local_models": 6,
              "independent_23_vertex_partial_rows_checked": sum(row["partial_rows_checked"] for row in rows),
              "independent_quota_decisions_checked": 792,
              "exact_positive_subset_profiles": 6, "exact_positive_quota_profiles": 6,
              "new_excluded_coverage": 0,
              "scope": "All six frozen source150 compressed profiles only. Every local subset table is replayed by the independent common-neighbour delta formula, every raw actual-position domain is reconstructed, every quota decision is replayed by direct all-target convolution, and both rational moment witnesses satisfy every equality and nonnegativity. These are convex macro-level controls, not graph completions or fixed-overlap-branch feasibility claims.",
              "elapsed_seconds": time.monotonic() - started, "submission_txt_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in ("inputs_sha256", "rows")}, sort_keys=True))


if __name__ == "__main__":
    main()
