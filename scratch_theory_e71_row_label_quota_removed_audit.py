"""Independent scalar obstructions for only the three quota-rejected rows.

No quota DP, LP solver, or research producer is imported.  The six relevant
source-target subset tests are replayed with explicit set adjacency.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from scratch_theory_e71_degree_moment_lp_audit import (
    CATALOG, MINING, SUPPORTS, LABELS, macro_key, reconstruct,
    principal_coordinates, all_raw_domains,
)


QUOTA = Path("scratch_theory_e71_row_label_quota_moment_frontier.json")
SUBSET = Path("scratch_theory_e71_label_subset_moment_frontier.json")
DEPENDENCY = Path("scratch_theory_e71_degree_moment_lp_audit.py")
OUT = Path("scratch_theory_e71_row_label_quota_removed_audit.json")
EXPECTED = {
    (1219, 7, 0): (46, 30, (-2, 2, 1, -4), 3, ((1, 4), (1, 5))),
    (1219, 10, 0): (46, 30, (-2, 2, 1, -4), 3, ((1, 4), (1, 5))),
    (1289, 2, 0): (12, 10, (-4, 3, 3, 2), 1, ((0, 4), (0, 5))),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def selected_subsets(entry, position, target):
    source, local = divmod(position, 4)
    exceptional = {tuple(row["support"]) for row in entry["exceptional_supports"]}
    internal = {frozenset((tuple(a), tuple(b))) for a, b in entry["internal_edges"]}
    edges = {frozenset((0, label + 1)) for label in range(14)}
    edges.update(frozenset((2 * group + 1, 2 * group + 2)) for group in range(7))
    for fibre, offset in ((source, 15), (target, 19)):
        for corner in range(4):
            edges.update(frozenset((offset + corner, label + 1)) for label in LABELS[4 * fibre + corner])
        for a, b in itertools.combinations(range(4), 2):
            left, right = LABELS[4 * fibre + a], LABELS[4 * fibre + b]
            present = ((frozenset((left, right)) in internal) if SUPPORTS[fibre] in exceptional
                       else len(set(left) & set(right)) == 1)
            if present:
                edges.add(frozenset((offset + a, offset + b)))
    x = 15 + local
    accepted = []
    for bits in range(16):
        exposed = edges | {frozenset((x, 19 + j)) for j in range(4) if bits >> j & 1}
        neighbors = [{v for v in range(23) if frozenset((u, v)) in exposed} for u in range(23)]
        if all(len(neighbors[a] & neighbors[b]) <= (1 if frozenset((a, b)) in exposed else 2)
               for a, b in itertools.combinations(range(23), 2)):
            accepted.append(bits)
    return accepted


def main():
    quota, subset, catalog, mining = map(read, (QUOTA, SUBSET, CATALOG, MINING))
    for name, expected in quota["inputs_sha256"].items():
        assert sha(Path(name)) == expected.upper()
    for name, expected in subset["inputs_sha256"].items():
        assert sha(Path(name)) == expected.upper()
    entries = {macro_key(row): row for row in catalog["macro_entries"] if row["signature_stabilizer_canonical"]}
    profiles = {(macro_key(row), row["parameter"]): row for row in mining["profile_rows"]["71"]}
    subset_rows = {(tuple(row["key"]), row["parameter"]): row for row in subset["profiles"]}
    local = {tuple(row["key"]): row for row in subset["local_models"]}
    removed = []
    retained_decisions = 0
    for row in quota["profiles"]:
        key, parameter = tuple(row["key"]), row["parameter"]
        decisions = row["row_decisions"]
        assert len(decisions) == len(subset_rows[key, parameter]["model"]["variables"])
        assert row["retained_variable_indices"] == [i for i, value in enumerate(decisions) if value]
        retained_decisions += sum(decisions)
        removed.extend((key, parameter, index) for index, value in enumerate(decisions) if not value)
    assert len(removed) == 3 and {key for key, _, _ in removed} == set(EXPECTED)
    records = []
    for key, parameter, index in removed:
        expected_index, position, pivot, saturated_label, supports = EXPECTED[key]
        assert parameter == "unique" and index == expected_index
        variable = subset_rows[key, parameter]["model"]["variables"][index]
        assert variable == {"position": position, "pivot": list(pivot)}
        entry, profile = entries[key], profiles[key, parameter]
        _, compression, gram = reconstruct(entry, profile)
        selected, coordinates = principal_coordinates(gram)
        domains = all_raw_domains(compression, selected, coordinates)
        matching = [degrees for residual, degrees in domains[position // 4] if residual == pivot]
        assert len(matching) == 1
        degrees = matching[0]
        assert saturated_label in LABELS[position]
        forced = []
        for support in supports:
            target = SUPPORTS.index(support)
            assert target != position // 4 and degrees[target] == 1
            allowed = selected_subsets(entry, position, target)
            assert allowed == local[key]["allowed_subsets"][position][target]
            singletons = [bits for bits in allowed if bits.bit_count() == 1]
            assert singletons
            labels = [LABELS[4 * target + bits.bit_length() - 1] for bits in singletons]
            assert all(saturated_label in label for label in labels)
            forced.append({"target_support": list(support), "required_degree": 1,
                           "admissible_singleton_bits": singletons,
                           "admissible_neighbor_labels": list(map(list, labels)),
                           "forced_contribution_to_saturated_rootlabel": 1})
        assert len({tuple(item["target_support"]) for item in forced}) == 2
        records.append({
            "key": list(key), "parameter": parameter, "removed_variable_index": index,
            "position": position, "source_label": list(LABELS[position]),
            "pivot": list(pivot), "full_degree_row": list(degrees),
            "adjacent_rootlabel": saturated_label, "allowed_common_neighbors": 1,
            "forced_distinct_common_neighbors": 2, "target_obstructions": forced,
            "scalar_lambda_contradiction": True,
        })
    report = {
        "status": "INDEPENDENT_E71_THREE_REMOVED_ROOTLABEL_ROWS_AUDIT_PASS",
        "research_producer_imported": False, "quota_DP_run": False, "LP_solver_used": False,
        "inputs_sha256": {str(path): sha(path) for path in (QUOTA, SUBSET, CATALOG, MINING, DEPENDENCY)},
        "removed_rows_independently_checked": len(records),
        "partial_23_vertex_subsets_independently_checked": 3 * 2 * 16,
        "retained_row_decisions_not_independently_checked": retained_decisions,
        "new_macro_exclusions_credited": 0,
        "rows": records,
        "scope": "Only the three recorded removed rows. Each has two forced common neighbours on an adjacent rootlabel pair. Retained decisions and reduced LP certificates are not audited here.",
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
