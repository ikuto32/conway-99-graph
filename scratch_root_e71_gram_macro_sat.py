"""Selector-gated exact 99-vertex SAT lift for the E71 Gram macros.

The E71 macro catalog fixes two kinds of local data: every edge inside an
exceptional fibre and the total number of edges in every overlapping pair of
exceptional fibres.  This encoder puts those facts behind one selector per
canonical macro.  The shared formula comes from ``build_shared_cnf`` and
retains every disjoint exceptional block as an exact SAT variable, so this is
an exact lift rather than a local completion heuristic.

One formula is built per canonical support row.  The catalog's support and
state stabilizers justify using its 180 canonical macros in place of the 193
labelled signature products; the recorded orbit coverages are audited here.
No E72 input or output is read or modified.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
import sys
import time

from scratch_general_exact_sat import coordinates, verify
from scratch_incremental_local_exact_sat import build_shared_cnf


PORT = Path("scratch_root_e71_q2_port_feasible_states.json")
CATALOG = Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json")
MANIFEST = Path("scratch_root_e71_gram_macro_sat_manifest.json")
GROUPS = tuple(range(7))
SUPPORTS = tuple(itertools.combinations(GROUPS, 2))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def stable_hash(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def label_support(label) -> tuple[int, int]:
    return tuple(sorted((int(label[0]) // 2, int(label[1]) // 2)))


def load_inputs() -> tuple[dict, dict, dict[int, dict]]:
    port = json.loads(PORT.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    rows = {int(row["source_row_index"]): row for row in port["rows"]}
    assert len(rows) == len(port["rows"])
    return port, catalog, rows


def normalize_internal_edges(entry: dict) -> tuple[tuple[tuple[int, int], tuple[int, int]], ...]:
    answer = []
    for raw_left, raw_right in entry["internal_edges"]:
        left = tuple(sorted(map(int, raw_left)))
        right = tuple(sorted(map(int, raw_right)))
        answer.append(tuple(sorted((left, right))))
    result = tuple(sorted(answer))
    assert len(result) == len(set(result))
    return result


def normalized_overlap_totals(entry: dict) -> tuple[tuple[int, int, int], ...]:
    result = tuple(sorted(
        (min(int(left), int(right)), max(int(left), int(right)), int(target))
        for left, right, target in entry["overlap_block_totals"]
    ))
    assert len(result) == len({(left, right) for left, right, _target in result})
    return result


def branch_fingerprint(entry: dict) -> tuple:
    return normalize_internal_edges(entry), normalized_overlap_totals(entry)


def validate_entry(entry: dict, row: dict, label_index: dict) -> dict:
    source_row_index = int(entry["source_row_index"])
    assert source_row_index == int(row["source_row_index"])
    for key in ("partition", "compression_orbit_index", "support_orbit_size"):
        assert entry[key] == row[key]
    assert entry["exceptional_supports"] == row["exceptional_supports"]
    assert tuple(entry["state_indices"]) in {
        tuple(values) for values in row["feasible_state_indices"]
    }

    exceptional = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
    deficits = tuple(int(item["deficit"]) for item in row["exceptional_supports"])
    internal = normalize_internal_edges(entry)
    by_support = Counter()
    internal_outer_edges = []
    for left, right in internal:
        assert left in label_index and right in label_index and left != right
        support = label_support(left)
        assert support == label_support(right) and support in exceptional
        by_support[support] += 1
        internal_outer_edges.append(tuple(sorted((label_index[left], label_index[right]))))
    assert len(internal_outer_edges) == len(set(internal_outer_edges))
    for support, deficit in zip(exceptional, deficits):
        assert by_support[support] == 4 - deficit
    assert len(internal) == sum(4 - deficit for deficit in deficits)

    overlap = normalized_overlap_totals(entry)
    expected_pairs = {
        (left, right)
        for left, right in itertools.combinations(range(len(exceptional)), 2)
        if set(exceptional[left]) & set(exceptional[right])
    }
    assert {(left, right) for left, right, _target in overlap} == expected_pairs
    assert all(0 <= target <= 16 for _left, _right, target in overlap)

    flattened = []
    choice_product = 1
    assert [int(item["group"]) for item in entry["group_signature_classes"]] == list(GROUPS)
    for group_row in entry["group_signature_classes"]:
        pairs = group_row["fibre_pairs"]
        counts = group_row["block_counts"]
        assert len(pairs) == len(counts)
        choice_product *= int(group_row["matching_choice_count"])
        for pair, count in zip(pairs, counts):
            left, right = sorted(map(int, pair))
            assert group_row["group"] in set(exceptional[left]) & set(exceptional[right])
            flattened.append((left, right, int(count)))
    assert tuple(sorted(flattened)) == overlap
    assert choice_product == int(entry["matching_completion_weight_per_state"])
    assert (
        choice_product * int(entry["state_orbit_size"])
        == int(entry["labelled_state_matching_coverage"])
    )
    assert (
        int(entry["labelled_state_matching_coverage"])
        * int(entry["signature_stabilizer_orbit_size"])
        == int(entry["signature_orbit_labelled_coverage"])
    )
    assert len(entry["signature_stabilizer_canonical_D"]) == len(overlap)
    if entry["signature_stabilizer_canonical"]:
        assert tuple(entry["signature_stabilizer_canonical_D"]) == tuple(
            target for _left, _right, target in overlap
        )
    return {
        "source_row_index": source_row_index,
        "exceptional_fibres": len(exceptional),
        "internal_edges": len(internal),
        "overlap_blocks": len(overlap),
        "fingerprint_sha256": stable_hash(branch_fingerprint(entry)),
    }


def build_manifest() -> dict:
    port, catalog, rows = load_inputs()
    labels, label_index, _variables, _edge = coordinates()
    assert len(labels) == 84
    entries = catalog["macro_entries"]
    canonical = [entry for entry in entries if entry["signature_stabilizer_canonical"]]
    assert len(entries) == catalog["summary"]["Gram_feasible_macro_entries"] == 193
    assert len(canonical) == catalog["summary"]["macro_entries_mod_state_stabilizers"] == 180

    validation = [validate_entry(entry, rows[int(entry["source_row_index"])], label_index)
                  for entry in entries]
    grouped_orbits = defaultdict(list)
    for entry in entries:
        grouped_orbits[(
            int(entry["source_row_index"]),
            int(entry["state_orbit_number"]),
            int(entry["signature_stabilizer_orbit_number"]),
        )].append(entry)
    for orbit_entries in grouped_orbits.values():
        representatives = [item for item in orbit_entries if item["signature_stabilizer_canonical"]]
        assert len(representatives) == 1
        representative = representatives[0]
        assert len(orbit_entries) == int(representative["signature_stabilizer_orbit_size"])
        assert len({int(item["labelled_state_matching_coverage"]) for item in orbit_entries}) == 1
        assert sum(int(item["labelled_state_matching_coverage"]) for item in orbit_entries) == int(
            representative["signature_orbit_labelled_coverage"]
        )

    raw_coverage = sum(int(entry["labelled_state_matching_coverage"]) for entry in entries)
    canonical_coverage = sum(int(entry["signature_orbit_labelled_coverage"]) for entry in canonical)
    expected_coverage = int(catalog["summary"]["labelled_state_matching_coverage"])
    assert raw_coverage == canonical_coverage == expected_coverage == 61_112_320

    raw_by_source = defaultdict(list)
    canonical_by_source = defaultdict(list)
    for entry in entries:
        raw_by_source[int(entry["source_row_index"])].append(entry)
        if entry["signature_stabilizer_canonical"]:
            canonical_by_source[int(entry["source_row_index"])].append(entry)
    assert set(raw_by_source) == set(canonical_by_source)

    source_rows = []
    for source_row_index in sorted(canonical_by_source):
        row = rows[source_row_index]
        raw_source = raw_by_source[source_row_index]
        branches = canonical_by_source[source_row_index]
        fingerprints = [branch_fingerprint(entry) for entry in branches]
        assert len(fingerprints) == len(set(fingerprints))
        # Complete internal assignments plus a complete vector of overlapping
        # block totals make distinct fingerprints mutually inconsistent.
        pairwise_disjoint = True
        for left, right in itertools.combinations(branches, 2):
            left_internal, left_overlap = branch_fingerprint(left)
            right_internal, right_overlap = branch_fingerprint(right)
            assert tuple((a, b) for a, b, _target in left_overlap) == tuple(
                (a, b) for a, b, _target in right_overlap
            )
            if left_internal == right_internal:
                assert any(
                    a[:2] == b[:2] and a[2] != b[2]
                    for a, b in zip(left_overlap, right_overlap)
                )
            else:
                assert set(left_internal) != set(right_internal)
        raw_source_coverage = sum(int(item["labelled_state_matching_coverage"])
                                  for item in raw_source)
        canonical_source_coverage = sum(int(item["signature_orbit_labelled_coverage"])
                                        for item in branches)
        assert raw_source_coverage == canonical_source_coverage
        source_rows.append({
            "source_row_index": source_row_index,
            "partition": row["partition"],
            "compression_orbit_index": row["compression_orbit_index"],
            "exceptional_fibres": len(row["exceptional_supports"]),
            "raw_macro_entries": len(raw_source),
            "canonical_selector_branches": len(branches),
            "labelled_state_matching_coverage": canonical_source_coverage,
            "selector_branch_fingerprints_distinct": True,
            "selector_branches_pairwise_disjoint": pairwise_disjoint,
        })

    # Formula size is driven primarily by the number of exceptional fibres,
    # so use that as the smoke-build priority before selector count/coverage.
    source_rows.sort(key=lambda item: (
        item["exceptional_fibres"], item["canonical_selector_branches"],
        item["labelled_state_matching_coverage"], item["source_row_index"],
    ))
    assert source_rows[0]["source_row_index"] == 694
    q_raw = Counter()
    q_canonical = Counter()
    for entry in entries:
        q_raw[int(entry["Q"])] += int(entry["labelled_state_matching_coverage"])
    for entry in canonical:
        q_canonical[int(entry["Q"])] += int(entry["signature_orbit_labelled_coverage"])
    expected_q = {int(key): int(value) for key, value in catalog["summary"]["Q_histogram"].items()}
    assert dict(q_raw) == dict(q_canonical) == expected_q

    result = {
        "status": "E71_GRAM_MACRO_TO_EXACT_SAT_MANIFEST_PASS",
        "model": "one exact rooted 99-vertex selector CNF per E71 support row",
        "inputs": {
            "port": str(PORT), "port_sha256": sha256(PORT),
            "catalog": str(CATALOG), "catalog_sha256": sha256(CATALOG),
        },
        "catalog_macro_entries": len(entries),
        "canonical_selector_branches": len(canonical),
        "support_specific_exact_cnf_instances": len(source_rows),
        "labelled_state_matching_coverage": canonical_coverage,
        "Q_histogram": {str(key): value for key, value in sorted(q_canonical.items())},
        "raw_to_canonical_signature_orbits": len(grouped_orbits),
        "all_193_entries_validated": len(validation) == 193,
        "all_180_canonical_branches_have_encodable_internal_and_overlap_data": True,
        "raw_and_canonical_coverage_equal": True,
        "canonical_selector_branches_partition_each_support_row": True,
        "minimum_smoke_source": source_rows[0],
        "sources_in_build_priority_order": source_rows,
        "claim_boundary": (
            "Coverage is in the rooted support-orbit convention and is not multiplied "
            "by support_orbit_size. Each support row requires its own exact CNF."
        ),
    }
    atomic_json(MANIFEST, result)
    return result


def select_source(source_row_index: int) -> tuple[dict, list[dict], list[dict], dict]:
    _port, catalog, rows = load_inputs()
    assert source_row_index in rows
    raw = [entry for entry in catalog["macro_entries"]
           if int(entry["source_row_index"]) == source_row_index]
    canonical = [entry for entry in raw if entry["signature_stabilizer_canonical"]]
    assert raw and canonical
    return rows[source_row_index], raw, canonical, catalog


def normalized_source(row: dict, source_row_index: int) -> dict:
    return {
        "input_path": str(PORT),
        "selection": {"source_row_index": source_row_index},
        "support_form": f"E71-source{source_row_index}-Gram-overlap-macro",
        "supports_in_fibre_order": tuple(
            tuple(item["support"]) for item in row["exceptional_supports"]
        ),
        "representatives": [{
            "branch_index": 0,
            "representative_id": "unused-empty-placeholder",
            "orbit_size": 1,
            "present_edges": frozenset(),
        }],
    }


def cnf_audit(path: Path) -> dict:
    declared_variables = declared_clauses = None
    actual_clauses = unit_clauses = maximum_variable = 0
    with path.open("rb") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith(b"c"):
                continue
            if line.startswith(b"p"):
                fields = line.split()
                assert fields[:2] == [b"p", b"cnf"] and len(fields) == 4
                declared_variables, declared_clauses = map(int, fields[2:])
                continue
            literals = tuple(map(int, line.split()))
            assert literals and literals[-1] == 0 and 0 not in literals[:-1]
            body = literals[:-1]
            actual_clauses += 1
            unit_clauses += len(body) == 1
            if body:
                maximum_variable = max(maximum_variable, max(map(abs, body)))
    assert declared_variables is not None
    assert actual_clauses == declared_clauses and maximum_variable <= declared_variables
    return {
        "declared_variables": declared_variables,
        "declared_clauses": declared_clauses,
        "actual_clauses": actual_clauses,
        "unit_clauses": unit_clauses,
        "maximum_variable_seen": maximum_variable,
    }


def build(source_row_index: int) -> dict:
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    manifest = build_manifest()
    row, raw_entries, branches, catalog = select_source(source_row_index)
    labels, label_index, full_variables, _full_edge = coordinates()
    for entry in branches:
        validate_entry(entry, row, label_index)
    source = normalized_source(row, source_row_index)
    clauses, edge, edge_variables, rebuilt_full_variables, unused, shared_meta = build_shared_cnf(source)
    assert rebuilt_full_variables == full_variables
    assert len(unused) == 1 and unused[0]["positive_assumptions"] == 0

    exceptional = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
    fibres = {
        support: tuple(u for u, label in enumerate(labels) if label_support(label) == support)
        for support in SUPPORTS
    }
    assert all(len(vertices) == 4 for vertices in fibres.values())
    selectors = list(range(shared_meta["variables"] + 1,
                           shared_meta["variables"] + 1 + len(branches)))
    assert selectors
    clauses.append(selectors)
    selector_at_most_one_clauses = 0
    for left, right in itertools.combinations(selectors, 2):
        clauses.append([-left, -right])
        selector_at_most_one_clauses += 1
    pool = IDPool(start_from=selectors[-1] + 1)

    branch_rows = []
    seen_fingerprints = set()
    for macro_branch_index, (entry, selector) in enumerate(zip(branches, selectors)):
        before_clauses = len(clauses)
        before_top = pool.top
        chosen_labels = normalize_internal_edges(entry)
        chosen_outer = {
            tuple(sorted((label_index[left], label_index[right])))
            for left, right in chosen_labels
        }
        internal_literals = []
        positive_internal_variables = []
        negative_internal_variables = []
        for support in exceptional:
            for u, v in itertools.combinations(fibres[support], 2):
                variable = edge(u, v)
                assert type(variable) is int and edge_variables[(min(u, v), max(u, v))] == variable
                literal = variable if (min(u, v), max(u, v)) in chosen_outer else -variable
                clauses.append([-selector, literal])
                internal_literals.append(literal)
                (positive_internal_variables if literal > 0 else negative_internal_variables).append(abs(literal))
        assert len(internal_literals) == 6 * len(exceptional)
        assert len(positive_internal_variables) == len(chosen_outer)

        cardinality_clauses = 0
        block_rows = []
        for left_index, right_index, target in normalized_overlap_totals(entry):
            left = exceptional[left_index]
            right = exceptional[right_index]
            block_variables = tuple(
                edge(u, v) for u in fibres[left] for v in fibres[right]
            )
            assert len(block_variables) == len(set(block_variables)) == 16
            assert all(type(value) is int for value in block_variables)
            encoded = CardEnc.equals(
                lits=list(block_variables), bound=target, vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
            clauses.extend([-selector, *clause] for clause in encoded)
            cardinality_clauses += len(encoded)
            block_rows.append({
                "left_exceptional_index": left_index,
                "right_exceptional_index": right_index,
                "left_support": list(left),
                "right_support": list(right),
                "target": target,
                "edge_variables": list(block_variables),
                "encoding_clauses": len(encoded),
            })

        fingerprint = branch_fingerprint(entry)
        fingerprint_hash = stable_hash(fingerprint)
        assert fingerprint_hash not in seen_fingerprints
        seen_fingerprints.add(fingerprint_hash)
        branch_rows.append({
            "macro_branch_index": macro_branch_index,
            "selector": selector,
            "state_orbit_number": entry["state_orbit_number"],
            "signature_stabilizer_orbit_number": entry["signature_stabilizer_orbit_number"],
            "state_indices": entry["state_indices"],
            "Q": entry["Q"],
            "state_orbit_size": entry["state_orbit_size"],
            "signature_stabilizer_orbit_size": entry["signature_stabilizer_orbit_size"],
            "labelled_state_matching_coverage": entry["signature_orbit_labelled_coverage"],
            "branch_fingerprint_sha256": fingerprint_hash,
            "internal_literal_implications": len(internal_literals),
            "positive_internal_edges": len(positive_internal_variables),
            "positive_internal_edge_variables": sorted(positive_internal_variables),
            "negative_internal_edge_variables": sorted(negative_internal_variables),
            "positive_internal_full_edge_variables": sorted(
                full_variables[pair] for pair in chosen_outer
            ),
            "negative_internal_full_edge_variables": sorted(
                full_variables[pair]
                for support in exceptional
                for pair in itertools.combinations(fibres[support], 2)
                if pair not in chosen_outer
            ),
            "overlap_block_cardinality_equalities": len(block_rows),
            "overlap_blocks": block_rows,
            "block_cardinality_encoding_clauses": cardinality_clauses,
            "gated_clauses": len(clauses) - before_clauses,
            "auxiliary_variables": pool.top - before_top,
        })

    # Recheck that every two selectors fix mutually inconsistent macro data.
    for left, right in itertools.combinations(branches, 2):
        li, lo = branch_fingerprint(left)
        ri, ro = branch_fingerprint(right)
        assert li != ri or any(a[2] != b[2] for a, b in zip(lo, ro))

    variables = max(selectors[-1], pool.top)
    cnf_path = Path(f"scratch_root_e71_source{source_row_index}_gram_macro.cnf")
    temporary = cnf_path.with_suffix(cnf_path.suffix + f".{os.getpid()}.tmp")
    with temporary.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {variables} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    temporary.replace(cnf_path)
    audited_cnf = cnf_audit(cnf_path)
    assert audited_cnf["declared_variables"] == variables
    assert audited_cnf["declared_clauses"] == len(clauses)
    audited_cnf["sha256"] = sha256(cnf_path)

    fixed_true_full_variables = []
    for key, full_variable in sorted(full_variables.items()):
        value = edge(*key)
        if value is True:
            fixed_true_full_variables.append(full_variable)
        elif value is False:
            continue
        else:
            assert type(value) is int and edge_variables[key] == value
    assert len(fixed_true_full_variables) == shared_meta["ordinary_c4_fibre_count"] * 4

    raw_coverage = sum(int(item["labelled_state_matching_coverage"]) for item in raw_entries)
    canonical_coverage = sum(int(item["signature_orbit_labelled_coverage"]) for item in branches)
    encoded_coverage = sum(int(item["labelled_state_matching_coverage"]) for item in branch_rows)
    assert raw_coverage == canonical_coverage == encoded_coverage
    manifest_source = next(
        item for item in manifest["sources_in_build_priority_order"]
        if item["source_row_index"] == source_row_index
    )
    assert manifest_source["labelled_state_matching_coverage"] == encoded_coverage
    assert len(branches) == manifest_source["canonical_selector_branches"]

    result = {
        "status": "E71_EXACT_SELECTOR_CNF_BUILD_AUDIT_PASS",
        "model": "exact rooted 99-vertex E71 overlap-Gram macro selector CNF",
        "source_row_index": source_row_index,
        "inputs": {
            "port": str(PORT), "port_sha256": sha256(PORT),
            "catalog": str(CATALOG), "catalog_sha256": sha256(CATALOG),
            "manifest": str(MANIFEST), "manifest_sha256": sha256(MANIFEST),
        },
        "partition": row["partition"],
        "compression_orbit_index": row["compression_orbit_index"],
        "support_orbit_size": row["support_orbit_size"],
        "exceptional_supports": row["exceptional_supports"],
        "raw_macro_entries": len(raw_entries),
        "canonical_selector_branches": len(branch_rows),
        "raw_macro_coverage": raw_coverage,
        "canonical_selector_coverage": canonical_coverage,
        "encoded_selector_coverage": encoded_coverage,
        "coverage_convention": "rooted support representative; support_orbit_size is not multiplied",
        "selector_exactly_one": True,
        "selector_at_least_one_clauses": 1,
        "selector_at_most_one_clauses": selector_at_most_one_clauses,
        "selector_branches_pairwise_disjoint_by_fixed_macro_data": True,
        "shared_exact_cnf_meta": shared_meta,
        "unused_placeholder_assumptions_applied": False,
        "branches": branch_rows,
        "edge_variables": len(edge_variables),
        "fixed_true_full_edge_variables": fixed_true_full_variables,
        "unknown_disjoint_exceptional_blocks_left_to_exact_sat":
            shared_meta["exceptional_exceptional_unrestricted_disjoint_blocks"],
        "cnf": str(cnf_path),
        "cnf_audit": audited_cnf,
        "all_180_catalog_branches_supported_by_this_builder_schema": True,
        "direct_99_vertex_verification_required_on_sat": True,
        "submission_policy": "submission.txt is written only after verify(...)[ok] is true",
        "claim_boundary": (
            "The selector fixes complete exceptional internal states and all overlap "
            "block totals. Disjoint exceptional blocks are not Gram-fixed and remain "
            "variables constrained by the exact BP and all outer-pair equations."
        ),
    }
    build_path = Path(f"scratch_root_e71_source{source_row_index}_gram_macro_build.json")
    atomic_json(build_path, result)
    return result


def translate_sat_model(source_row_index: int, model) -> set[int]:
    row, _raw, _branches, _catalog = select_source(source_row_index)
    source = normalized_source(row, source_row_index)
    _clauses, edge, edge_variables, full_variables, _unused, _meta = build_shared_cnf(source)
    positive_model = {literal for literal in model if literal > 0}
    answer = {
        full_variables[key] for key, variable in edge_variables.items()
        if variable in positive_model
    }
    for key, full_variable in full_variables.items():
        if edge(*key) is True:
            answer.add(full_variable)
    return answer


def write_verified_submission(verification: dict) -> None:
    assert verification["ok"]
    edges = [tuple(map(int, edge)) for edge in verification["edges"]]
    assert len(edges) == len(set(edges)) == 693
    assert all(1 <= left < right <= 99 for left, right in edges)
    target = Path("submission.txt")
    temporary = target.with_suffix(target.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(
        "".join(f"{{{left}, {right}}}\n" for left, right in sorted(edges)),
        encoding="ascii",
    )
    temporary.replace(target)


def solve(source_row_index: int, conflicts: int, per_branch: bool = False) -> dict:
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.formula import CNF
    from pysat.solvers import Solver

    build_doc = build(source_row_index)
    build_path = Path(f"scratch_root_e71_source{source_row_index}_gram_macro_build.json")
    cnf_path = Path(build_doc["cnf"])
    output = Path(
        f"scratch_root_e71_source{source_row_index}_gram_macro_"
        f"{'branches' if per_branch else 'aggregate'}_c{conflicts}.json"
    )
    started = time.monotonic()
    formula = CNF(from_file=str(cnf_path))
    loaded = time.monotonic()
    records = []
    verified_solution = None
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        selected = build_doc["branches"] if per_branch else [None]
        for item in selected:
            assumptions = [int(item["selector"])] if item is not None else []
            before = solver.accum_stats()
            branch_started = time.monotonic()
            if conflicts:
                solver.conf_budget(conflicts)
                answer = solver.solve_limited(assumptions=assumptions, expect_interrupt=True)
            else:
                answer = solver.solve(assumptions=assumptions)
            after = solver.accum_stats()
            status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
            record = {
                "macro_branch_index": item["macro_branch_index"] if item else None,
                "selector": item["selector"] if item else None,
                "coverage": (
                    item["labelled_state_matching_coverage"] if item
                    else build_doc["encoded_selector_coverage"]
                ),
                "status": status,
                "solve_seconds": round(time.monotonic() - branch_started, 6),
                "stats_delta": {
                    key: int(after.get(key, 0)) - int(before.get(key, 0))
                    for key in sorted(set(before) | set(after))
                },
            }
            if answer is False and assumptions:
                record["assumption_core"] = list(solver.get_core() or ())
            elif answer is True:
                positive = translate_sat_model(source_row_index, solver.get_model())
                verification = verify(positive)
                if not verification["ok"]:
                    raise AssertionError("SAT model failed direct 99-vertex verification")
                record["direct_99_vertex_verification"] = {
                    key: value for key, value in verification.items() if key != "edges"
                }
                record["positive_full_edge_variables"] = sorted(positive)
                verified_solution = verification
                write_verified_submission(verification)
            records.append(record)
            if verified_solution is not None:
                break

    all_terminal = len(records) == len(selected) and all(
        item["status"] in ("SAT", "UNSAT") for item in records
    )
    status = (
        "SAT" if verified_solution is not None
        else "UNSAT" if all_terminal and all(item["status"] == "UNSAT" for item in records)
        else "UNKNOWN"
    )
    result = {
        "status": status,
        "model": build_doc["model"],
        "mode": "per_branch" if per_branch else "aggregate",
        "source_row_index": source_row_index,
        "conflict_budget_per_call": conflicts or None,
        "build": str(build_path), "build_sha256": sha256(build_path),
        "cnf": str(cnf_path), "cnf_sha256": sha256(cnf_path),
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "parse_seconds": round(loaded - started, 6),
        "records": records,
        "verified_99_vertex_solution": verified_solution is not None,
        "submission_written": verified_solution is not None,
        "submission_path": "submission.txt" if verified_solution is not None else None,
        "total_selector_coverage": build_doc["encoded_selector_coverage"],
        "formal_proof_certificate": None,
        "claim_boundary": "UNKNOWN is only a bounded smoke result; UNSAT is computational without a checked proof.",
    }
    atomic_json(output, result)
    if verified_solution is not None:
        atomic_json(Path(f"scratch_root_e71_source{source_row_index}_verified_solution.json"),
                    verified_solution)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", action="store_true")
    parser.add_argument("--source-row-index", type=int)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--per-branch", action="store_true")
    parser.add_argument("--conflicts", type=int, default=10_000)
    args = parser.parse_args()
    if args.manifest:
        result = build_manifest()
        print(json.dumps({
            "status": result["status"],
            "raw_macros": result["catalog_macro_entries"],
            "canonical_macros": result["canonical_selector_branches"],
            "sources": result["support_specific_exact_cnf_instances"],
            "coverage": result["labelled_state_matching_coverage"],
            "minimum_smoke_source": result["minimum_smoke_source"]["source_row_index"],
        }, sort_keys=True))
        return
    if args.source_row_index is None:
        parser.error("--source-row-index is required for --build/--solve")
    if args.build:
        result = build(args.source_row_index)
        print(json.dumps({
            "status": result["status"],
            "source_row_index": result["source_row_index"],
            "selectors": result["canonical_selector_branches"],
            "coverage": result["encoded_selector_coverage"],
            "variables": result["cnf_audit"]["declared_variables"],
            "clauses": result["cnf_audit"]["declared_clauses"],
        }, sort_keys=True))
        return
    if args.solve or args.per_branch:
        result = solve(args.source_row_index, args.conflicts, per_branch=args.per_branch)
        print(json.dumps({
            "status": result["status"],
            "source_row_index": result["source_row_index"],
            "mode": result["mode"],
            "coverage": result["total_selector_coverage"],
            "verified": result["verified_99_vertex_solution"],
        }, sort_keys=True))
        return
    parser.error("choose --manifest, --build, --solve, or --per-branch")


if __name__ == "__main__":
    main()
