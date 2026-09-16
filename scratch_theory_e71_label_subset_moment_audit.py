"""Independent partial-graph/Farkas audit of newly certified E71 macros.

The degree-space routines come only from the standalone prior independent
audit. No research producer or its base is imported and no LP solver is used.
The local test uses an explicit common-neighbour delta formula, not the
producer's trial adjacency bitsets.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

from scratch_theory_e71_degree_moment_lp_audit import (
    CATALOG, MINING, SUPPORTS, LABELS, macro_key, reconstruct,
    principal_coordinates, all_raw_domains, ordinary_internal_theorem,
    fibre_incidence_geometry,
)


CERT = Path("scratch_theory_e71_label_subset_moment_frontier.json")
INVENTORY = Path("scratch_root_e71_theory_frontier_before_label_subset.json")
DEPENDENCY = Path("scratch_theory_e71_degree_moment_lp_audit.py")
OUT = Path("scratch_theory_e71_label_subset_moment_audit.json")
PAIRS = tuple(itertools.combinations(range(23), 2))


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def fixed_blocks(entry):
    exceptional = {tuple(item["support"]) for item in entry["exceptional_supports"]}
    supplied = {frozenset((tuple(a), tuple(b))) for a, b in entry["internal_edges"]}
    assert len(supplied) == len(entry["internal_edges"])
    blocks = []
    for fibre, support in enumerate(SUPPORTS):
        edges = set()
        for a, b in itertools.combinations(range(4), 2):
            left, right = LABELS[4 * fibre + a], LABELS[4 * fibre + b]
            if ((frozenset((left, right)) in supplied) if support in exceptional
                else len(set(left) & set(right)) == 1):
                edges.add((a, b))
        blocks.append(edges)
    return blocks


def local_domains(entry, stored):
    blocks = fixed_blocks(entry)
    result = [[None] * 21 for _ in range(84)]
    tested = retained = 0
    for source in range(21):
        for target in range(21):
            if source == target:
                for local in range(4):
                    neighbors = {b if a == local else a for a, b in blocks[source] if local in (a, b)}
                    result[4 * source + local][target] = [sum(1 << v for v in neighbors)]
                continue
            adjacency = [set() for _ in range(23)]

            def add(a, b):
                adjacency[a].add(b)
                adjacency[b].add(a)

            for label in range(14):
                add(0, label + 1)
            for group in range(7):
                add(2 * group + 1, 2 * group + 2)
            for fibre, offset in ((source, 15), (target, 19)):
                for local in range(4):
                    for label in LABELS[4 * fibre + local]:
                        add(offset + local, label + 1)
                for a, b in blocks[fibre]:
                    add(offset + a, offset + b)
            common = {pair: len(adjacency[pair[0]] & adjacency[pair[1]]) for pair in PAIRS}
            caps = {pair: 1 if pair[1] in adjacency[pair[0]] else 2 for pair in PAIRS}
            assert all(common[pair] <= caps[pair] for pair in PAIRS)
            for local in range(4):
                x = 15 + local
                before = adjacency[x]
                accepted = []
                for bits in range(16):
                    target_neighbors = {19 + j for j in range(4) if bits >> j & 1}
                    after = before | target_neighbors
                    tested += 1
                    valid = True
                    for a, b in PAIRS:
                        lower = common[(a, b)]
                        cap = caps[(a, b)]
                        if a == x or b == x:
                            other = b if a == x else a
                            lower += len(target_neighbors & adjacency[other])
                            if other in target_neighbors:
                                cap = 1
                        else:
                            lower += int(a in after and b in after) - int(a in before and b in before)
                        if lower > cap:
                            valid = False
                            break
                    if valid:
                        accepted.append(bits)
                assert accepted and accepted[0] == 0
                result[4 * source + local][target] = accepted
                retained += len(accepted)
    assert tested == 26880
    assert result == stored["allowed_subsets"]
    assert stored["counts"] == {"partial_23_vertex_rows_tested": tested,
                                "partial_rows_retained": retained}
    return blocks, result, {"partial_rows_checked": tested, "partial_rows_retained": retained}


def check_profile(entry, profile, stored, blocks, subsets):
    _, compression, gram = reconstruct(entry, profile)
    selected, coordinates = principal_coordinates(gram)
    raw = all_raw_domains(compression, selected, coordinates)
    rank = len(selected)
    moment_pairs = tuple(itertools.combinations_with_replacement(range(rank), 2))
    degrees_allowed = [[{bits.bit_count() for bits in choices} for choices in row] for row in subsets]
    columns, variables, domains = [], [], []
    raw_count = 0
    for position in range(84):
        source, local = divmod(position, 4)
        own_degree = sum(local in edge for edge in blocks[source])
        assert sum(sum(v in edge for edge in blocks[source]) for v in range(4)) == compression[source][source]
        accepted = []
        for pivot, degree_row in raw[source]:
            if degree_row[source] != own_degree:
                continue
            raw_count += 1
            if any(degree not in degrees_allowed[position][target]
                   for target, degree in enumerate(degree_row)):
                continue
            accepted.append(list(pivot))
            column = [0] * (84 + 21 * rank + len(moment_pairs))
            column[position] = 1
            for axis in range(rank):
                column[84 + source * rank + axis] = pivot[axis]
            for offset, (a, b) in enumerate(moment_pairs):
                column[84 + 21 * rank + offset] = pivot[a] * pivot[b]
            columns.append(column)
            variables.append({"position": position, "pivot": list(pivot)})
        domains.append(accepted)
    assert columns
    matrix = list(map(list, zip(*columns)))
    target = [1] * 84 + [0] * (21 * rank)
    target.extend(4 * gram[selected[a]][selected[b]] for a, b in moment_pairs)
    digest = hashlib.sha256(json.dumps([matrix, target], separators=(",", ":")).encode()).hexdigest()
    metadata = stored["model"]
    assert metadata["rank_K4"] == rank
    assert metadata["pivot_supports"] == [list(SUPPORTS[index]) for index in selected]
    assert metadata["raw_row_patterns"] == sum(map(len, raw))
    assert metadata["raw_internal_degree_position_rows"] == raw_count
    assert metadata["retained_position_rows"] == len(columns)
    assert metadata["empty_positions"] == [position for position, values in enumerate(domains) if not values]
    assert metadata["domains_by_position"] == domains
    assert metadata["variables"] == variables and metadata["matrix_sha256"] == digest
    certificate = stored["exact_integer_certificate"]
    assert certificate is not None
    multiplier = certificate["integer_multiplier"]
    assert len(multiplier) == len(target) and all(type(value) is int for value in multiplier)
    slacks = [sum(a * b for a, b in zip(multiplier, column)) for column in columns]
    pairing = sum(a * b for a, b in zip(multiplier, target))
    assert min(slacks) >= 0 and pairing < 0
    assert min(slacks) == certificate["min_column_slack"]
    assert pairing == certificate["target_pairing"]
    assert certificate["exact_integer_check_pass"] is True
    return {"key": list(macro_key(entry)), "parameter": profile["parameter"],
            "rank_K4": rank, "raw_degree_rows": sum(map(len, raw)),
            "raw_position_rows": raw_count, "retained_position_rows": len(columns),
            "equations": len(target), "matrix_sha256": digest,
            "minimum_column_slack": min(slacks), "target_pairing": pairing,
            "independent_Farkas_pass": True}


def main():
    started = time.monotonic()
    certificate, catalog, mining, inventory = map(read, (CERT, CATALOG, MINING, INVENTORY))
    for name, expected in certificate["inputs_sha256"].items():
        assert sha(Path(name)) == expected.upper(), name
    assert certificate["all_remaining_requested"] is True
    ordinary_internal_theorem()
    fibre_incidence_geometry()
    entries = {macro_key(row): row for row in catalog["macro_entries"] if row["signature_stabilizer_canonical"]}
    selected = {tuple(key) for key in inventory["remaining_keys"]}
    assert len(selected) == len(inventory["remaining_keys"]) == 65
    full_profiles = defaultdict(dict)
    for profile in mining["profile_rows"]["71"]:
        key = macro_key(profile)
        if key in selected:
            assert profile["parameter"] not in full_profiles[key]
            full_profiles[key][profile["parameter"]] = profile
    assert set(full_profiles) == selected
    stored_profiles = {(tuple(row["key"]), row["parameter"]): row for row in certificate["profiles"]}
    expected_profiles = {(key, parameter) for key, profiles in full_profiles.items() for parameter in profiles}
    assert len(stored_profiles) == len(certificate["profiles"]) == certificate["profiles_tested"] == 71
    assert set(stored_profiles) == expected_profiles
    local_models = {tuple(row["key"]): row for row in certificate["local_models"]}
    assert len(local_models) == len(certificate["local_models"]) == certificate["macros_tested"] == 65
    assert set(local_models) == selected
    for (key, parameter), row in stored_profiles.items():
        assert row["coverage"] == full_profiles[key][parameter]["coverage"] == entries[key]["signature_orbit_labelled_coverage"]
    certified_tasks = {(key, parameter) for (key, parameter), row in stored_profiles.items()
                       if row["exact_integer_certificate"] is not None}
    assert len(certified_tasks) == certificate["exact_infeasible_profiles"] == 8
    certified_keys = {key for key, _ in certified_tasks}
    assert len(certified_keys) == 6
    audit_profiles, audit_macros = [], []
    for key in sorted(certified_keys):
        assert all((key, parameter) in certified_tasks for parameter in full_profiles[key])
        blocks, subsets, local_stats = local_domains(entries[key], local_models[key])
        for parameter, profile in full_profiles[key].items():
            audit_profiles.append(check_profile(entries[key], profile, stored_profiles[(key, parameter)], blocks, subsets))
        audit_macros.append({"key": list(key), "coverage": int(entries[key]["signature_orbit_labelled_coverage"]),
                             "full_Gram_profile_parameters": list(full_profiles[key]), **local_stats})
        print(json.dumps({"audited_macro": list(key), "profiles": len(full_profiles[key]), **local_stats}), flush=True)
    excluded_coverage = sum(row["coverage"] for row in audit_macros)
    assert excluded_coverage == 360448
    result = {
        "status": "INDEPENDENT_E71_LABEL_SUBSET_MOMENT_AUDIT_PASS",
        "research_producer_imported": False,
        "independent_degree_audit_dependency": str(DEPENDENCY),
        "LP_solver_used": False,
        "inputs_sha256": {str(path): sha(path) for path in (CERT, CATALOG, MINING, INVENTORY, DEPENDENCY)},
        "all_producer_input_hashes_match": True,
        "complete_input_manifest_macros": 65, "complete_input_manifest_profiles": 71,
        "local_models_independently_audited": len(audit_macros),
        "other_local_models_unaudited": 65 - len(audit_macros),
        "single_row_partial_graph_checks": sum(row["partial_rows_checked"] for row in audit_macros),
        "exact_profile_certificates_checked": len(audit_profiles),
        "excluded_macros": len(audit_macros), "excluded_labelled_coverage": excluded_coverage,
        "every_full_Gram_profile_directly_certified_for_each_excluded_macro": True,
        "macro_rows": audit_macros, "profile_rows": audit_profiles,
        "graph_completions_enumerated": 0, "pointwise_E0_lower_bound": None,
        "scope": "Only the6 listed new macros are certified; all other local subset models and feasible LP statuses remain unaudited here.",
        "elapsed_seconds": time.monotonic() - started,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in ("macro_rows", "profile_rows")}, indent=2))


if __name__ == "__main__":
    main()
