"""Generic complete-local-assumption harness for the universal exact CNF.

This program is deliberately separate from the support-specific incremental
and fixed-local encoders.  It independently reconstructs the 84 outer labels,
the first 3,486 universal edge variables, and the complete signed assignment
to all 1,806 *non-disjoint-support* outer edges represented by a normalized
local-graph catalogue.

An imported UNSAT assumption core is used only if

* it was obtained from the byte-identical baseline CNF, and
* every signed literal in the core occurs in the new complete assignment.

Otherwise the branch is sent to the same incremental CaDiCaL instance.  This
script never writes ``submission.txt``.  UNSAT results are computational: it
does not emit or independently check proof certificates.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time


DEFAULT_BASE = Path("scratch_general_exact.cnf")
DEFAULT_META = Path("scratch_general_exact_build.json")
PINNED_BASE_SHA256 = (
    "91D22E62625E1221DD46B819E89494DB8141DD4DDC9A06F13B9ABDB530B83242"
)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def text_sha256(values) -> str:
    return hashlib.sha256(" ".join(map(str, values)).encode("ascii")).hexdigest().upper()


def literal_set_sha256(values) -> str:
    ordered = sorted(set(map(int, values)), key=lambda value: (abs(value), value < 0))
    return text_sha256(ordered)


def atomic_write_json(path: Path, document) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def independent_coordinates():
    """Reconstruct the universal coordinates without importing another encoder."""
    labels = tuple(
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    )
    label_index = {label: index for index, label in enumerate(labels)}
    pairs = tuple(itertools.combinations(range(84), 2))
    variables = {pair: identifier for identifier, pair in enumerate(pairs, 1)}
    supports = tuple(tuple(symbol // 2 for symbol in label) for label in labels)
    assert len(labels) == 84 and len(label_index) == 84
    assert len(variables) == 3486
    assert all(left < right for left, right in supports)
    return labels, label_index, variables, supports


def coordinate_sha256() -> str:
    labels, _label_index, variables, supports = independent_coordinates()
    rows = []
    for (u, v), identifier in variables.items():
        rows.append(
            f"{identifier}:{u},{v}:{labels[u][0]},{labels[u][1]}:"
            f"{labels[v][0]},{labels[v][1]}:{supports[u][0]},{supports[u][1]}:"
            f"{supports[v][0]},{supports[v][1]}"
        )
    return hashlib.sha256("\n".join(rows).encode("ascii")).hexdigest().upper()


def _select_raw_records(document):
    if "records" in document:
        return list(document["records"]), "records"
    if "record" in document:
        return [document["record"]], "record"
    required = {"supports_in_fibre_order", "local_vertex_order", "representatives"}
    if required <= set(document):
        return [document], "direct"
    raise ValueError("catalogue is not in the normalized local-representative schema")


def _edge_from_labels(raw_edge, label_index):
    if len(raw_edge) != 2:
        raise ValueError(f"local edge does not have two endpoints: {raw_edge!r}")
    endpoints = []
    for raw_label in raw_edge:
        label = tuple(map(int, raw_label))
        if label not in label_index:
            raise ValueError(f"unknown outer label {label}")
        endpoints.append(label_index[label])
    return tuple(sorted(endpoints))


def independent_normalize_catalog(path: Path):
    """Read only the explicit normalized schema, failing closed on ambiguity."""
    document = json.loads(path.read_text(encoding="utf-8"))
    raw_records, container = _select_raw_records(document)
    labels, label_index, _variables, supports_by_vertex = independent_coordinates()
    all_supports = frozenset(itertools.combinations(range(7), 2))
    records = []
    global_index = 0
    for record_index, raw in enumerate(raw_records):
        required = {"supports_in_fibre_order", "local_vertex_order", "representatives"}
        missing = required - set(raw)
        if missing:
            raise ValueError(f"record {record_index} lacks {sorted(missing)}")
        exceptional = tuple(
            tuple(sorted(map(int, support)))
            for support in raw["supports_in_fibre_order"]
        )
        if not exceptional or len(exceptional) != len(set(exceptional)):
            raise ValueError(f"record {record_index}: exceptional supports not distinct")
        if any(support not in all_supports for support in exceptional):
            raise ValueError(f"record {record_index}: invalid exceptional support")
        exceptional_set = frozenset(exceptional)
        expected_vertices = {
            vertex
            for vertex, support in enumerate(supports_by_vertex)
            if support in exceptional_set
        }
        supplied_vertices = set()
        for item in raw["local_vertex_order"]:
            vertex = int(item["outer_index_zero_based"])
            if not 0 <= vertex < 84:
                raise ValueError(f"record {record_index}: outer index out of range")
            if tuple(map(int, item["symbol_label"])) != labels[vertex]:
                raise ValueError(f"record {record_index}: label/index mismatch at {vertex}")
            supplied_vertices.add(vertex)
        if supplied_vertices != expected_vertices:
            raise ValueError(
                f"record {record_index}: local_vertex_order is not the exceptional union"
            )

        representatives = []
        for representative_index, raw_rep in enumerate(raw["representatives"]):
            if "present_edges_outer_indices_zero_based" in raw_rep:
                edges = [
                    tuple(sorted(map(int, edge)))
                    for edge in raw_rep["present_edges_outer_indices_zero_based"]
                ]
            elif "local_graph_edges" in raw_rep:
                edges = [
                    _edge_from_labels(edge, label_index)
                    for edge in raw_rep["local_graph_edges"]
                ]
            else:
                raise ValueError(
                    f"record {record_index} representative {representative_index}: "
                    "no unambiguous supported edge field"
                )
            edge_set = frozenset(edges)
            if len(edge_set) != len(edges) or any(u == v for u, v in edges):
                raise ValueError(
                    f"record {record_index} representative {representative_index}: "
                    "duplicate edge or loop"
                )
            for u, v in edge_set:
                if not (0 <= u < v < 84):
                    raise ValueError("local edge endpoint is outside 0..83")
                left, right = supports_by_vertex[u], supports_by_vertex[v]
                if left not in exceptional_set or right not in exceptional_set:
                    raise ValueError("local edge has an endpoint outside exceptional fibres")
                if set(left).isdisjoint(right):
                    raise ValueError("local graph must not contain a disjoint-support edge")
            representatives.append({
                "record_index": record_index,
                "representative_index": representative_index,
                "global_representative_index": global_index,
                "representative_id": raw_rep.get(
                    "representative_id", raw_rep.get("representative_index", representative_index)
                ),
                "orbit_size": raw_rep.get(
                    "orbit_size", raw_rep.get("multiplicity_in_enumeration")
                ),
                "present_edges": edge_set,
            })
            global_index += 1
        if not representatives:
            raise ValueError(f"record {record_index}: empty representative list")
        records.append({
            "record_index": record_index,
            "support_form": raw.get("support_form"),
            "exceptional_supports": exceptional,
            "representatives": representatives,
        })
    return {
        "container": container,
        "catalogue_sha256": file_sha256(path),
        "record_count": len(records),
        "representative_count": global_index,
        "records": records,
    }


def complete_signed_assignment(record, representative):
    """Return one literal for every non-disjoint-support baseline edge."""
    labels, _label_index, variables, supports_by_vertex = independent_coordinates()
    exceptional = frozenset(record["exceptional_supports"])
    present = representative["present_edges"]
    literals = []
    positive_pairs = set()
    kinds = Counter()
    for (u, v), identifier in variables.items():
        left, right = supports_by_vertex[u], supports_by_vertex[v]
        if set(left).isdisjoint(right):
            continue
        if left == right:
            kinds["same_variables"] += 1
            if left in exceptional:
                value = (u, v) in present
                if value:
                    kinds["positive_exceptional_same"] += 1
            else:
                # The four sign choices in an ordinary fibre induce C4:
                # two vertices are adjacent exactly when their symbol labels meet.
                value = bool(set(labels[u]).intersection(labels[v]))
                if value:
                    kinds["positive_ordinary_c4_side"] += 1
        else:
            kinds["overlap_variables"] += 1
            if left in exceptional and right in exceptional:
                value = (u, v) in present
                if value:
                    kinds["positive_exceptional_overlap"] += 1
            else:
                value = False
        literals.append(identifier if value else -identifier)
        if value:
            positive_pairs.add((u, v))
    literal_set = frozenset(literals)
    if len(literals) != 1806 or len({abs(value) for value in literals}) != 1806:
        raise AssertionError("complete assignment must contain 1,806 distinct variables")
    if kinds["same_variables"] != 126 or kinds["overlap_variables"] != 1680:
        raise AssertionError("unexpected non-disjoint variable partition")
    if not present <= positive_pairs:
        # This also catches an edge that was syntactically local but is outside
        # the candidate semantics used by the complete assignment.
        raise ValueError("representative has a present edge omitted by assignment semantics")
    return {
        "record_index": representative["record_index"],
        "representative_index": representative["representative_index"],
        "global_representative_index": representative["global_representative_index"],
        "representative_id": representative["representative_id"],
        "orbit_size": representative["orbit_size"],
        "literals": tuple(literals),
        "literal_set": literal_set,
        "assumption_sha256": text_sha256(literals),
        "assumption_literal_set_sha256": literal_set_sha256(literals),
        "positive_assumptions": sum(value > 0 for value in literals),
        "negative_assumptions": sum(value < 0 for value in literals),
        "assignment_kind_counts": dict(sorted(kinds.items())),
    }


def enumerate_assignments(catalogue):
    assignments = []
    for record in catalogue["records"]:
        for representative in record["representatives"]:
            assignments.append(complete_signed_assignment(record, representative))
    if len(assignments) != catalogue["representative_count"]:
        raise AssertionError("representative enumeration count changed")
    if len({row["assumption_sha256"] for row in assignments}) != len(assignments):
        raise ValueError("catalogue contains duplicate complete signed assignments")
    return assignments


def audit_baseline(base: Path, meta_path: Path):
    actual_sha = file_sha256(base)
    if actual_sha != PINNED_BASE_SHA256:
        raise ValueError(
            f"baseline hash {actual_sha} differs from pinned {PINNED_BASE_SHA256}"
        )
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("cnf_sha256") != actual_sha:
        raise ValueError("baseline metadata hash does not match CNF")
    with base.open("r", encoding="ascii") as handle:
        header = handle.readline().split()
    if header[:2] != ["p", "cnf"] or len(header) != 4:
        raise ValueError("invalid DIMACS header")
    variables, clauses = map(int, header[2:])
    if (variables, clauses) != (meta.get("variables"), meta.get("clauses")):
        raise ValueError("DIMACS header does not match baseline metadata")
    if meta.get("edge_variables") != 3486:
        raise ValueError("baseline does not declare the required 3,486 edge variables")
    if meta.get("bp_constraints") != 1176 or meta.get("outer_pair_constraints") != 3486:
        raise ValueError("baseline structural equation counts differ")
    return {
        "path": str(base),
        "sha256": actual_sha,
        "metadata_path": str(meta_path),
        "metadata_sha256": file_sha256(meta_path),
        "header_variables": variables,
        "header_clauses": clauses,
        "outer_edge_variables": 3486,
        "coordinate_sha256": coordinate_sha256(),
    }


def _core_rows_from_document(document):
    if "selected" in document:
        return document["selected"]
    if "results" in document:
        values = document["results"]
        return list(values.values()) if isinstance(values, dict) else list(values)
    if "core_literals" in document:
        return [document]
    raise ValueError("core file has no supported core-bearing record collection")


def load_portable_cores(paths, expected_base_sha):
    cores = []
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        declared = document.get("base_cnf_sha256")
        if declared is None and isinstance(document.get("baseline"), dict):
            declared = document["baseline"].get("sha256")
        if declared != expected_base_sha:
            raise ValueError(f"core file {path} is not tied to the exact baseline hash")
        for row_index, row in enumerate(_core_rows_from_document(document)):
            if row.get("status") not in ("UNSAT", "COVERED_UNSAT"):
                continue
            raw = row.get("core_literals")
            if not raw:
                # A covered record need not repeat its covering core.
                continue
            literals = tuple(map(int, raw))
            literal_set = frozenset(literals)
            if len(literal_set) != len(literals):
                raise ValueError(f"duplicate literal in core {path}:{row_index}")
            variables = [abs(value) for value in literals]
            if len(variables) != len(set(variables)):
                raise ValueError(f"opposite signs or duplicate variable in core {path}:{row_index}")
            if any(not 1 <= variable <= 3486 for variable in variables):
                raise ValueError(f"non-edge assumption literal in core {path}:{row_index}")
            cores.append({
                "literals": literal_set,
                "literal_set_sha256": literal_set_sha256(literals),
                "size": len(literals),
                "source": {
                    "file": str(path),
                    "file_sha256": file_sha256(path),
                    "row_index": row_index,
                    "record_index": row.get("record_index"),
                    "representative_index": row.get("representative_index"),
                    "global_representative_index": row.get(
                        "global_representative_index"
                    ),
                    "reported_core_sha256": row.get("core_sha256"),
                },
            })
    unique = {}
    for core in cores:
        unique.setdefault(core["literal_set_sha256"], core)
    return sorted(unique.values(), key=lambda core: (core["size"], core["literal_set_sha256"]))


def _parse_key(raw):
    pieces = raw.split(":")
    if len(pieces) != 2:
        raise argparse.ArgumentTypeError("selection must be RECORD:REPRESENTATIVE")
    try:
        return tuple(map(int, pieces))
    except ValueError as error:
        raise argparse.ArgumentTypeError("selection components must be integers") from error


def _public_assignment(row):
    return {
        key: value
        for key, value in row.items()
        if key not in ("literals", "literal_set")
    }


def _new_document(baseline, catalogue_path, catalogue, args):
    return {
        "model": "generic universal exact-CNF complete-local-assumption harness",
        "baseline": baseline,
        "base_cnf_sha256": baseline["sha256"],
        "catalogue": {
            "path": str(catalogue_path),
            "sha256": catalogue["catalogue_sha256"],
            "container": catalogue["container"],
            "record_count": catalogue["record_count"],
            "representative_count": catalogue["representative_count"],
        },
        "generator": {
            "independent_of_shared_and_fixed_local_encoders": True,
            "complete_signed_assumptions": 1806,
            "same_support_variables": 126,
            "overlap_support_variables": 1680,
            "unassigned_disjoint_support_variables": 1680,
            "coordinate_sha256": baseline["coordinate_sha256"],
        },
        "conflict_budget_per_direct_solve": args.conflicts,
        "screen_only": args.screen_only,
        "portable_core_rule": (
            "Reuse only for this exact baseline SHA-256 and only when the target "
            "complete signed assignment contains every signed core literal."
        ),
        "formal_proof_certificates": None,
        "results": {},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-cnf", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--base-meta", type=Path, default=DEFAULT_META)
    parser.add_argument("--core-file", type=Path, action="append", default=[])
    parser.add_argument("--select", type=_parse_key, action="append")
    parser.add_argument("--start-global", type=int, default=0)
    parser.add_argument("--end-global", type=int)
    parser.add_argument("--conflicts", type=int, default=200_000)
    parser.add_argument("--screen-only", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.conflicts < 0:
        parser.error("--conflicts must be nonnegative")

    started = time.monotonic()
    baseline = audit_baseline(args.base_cnf, args.base_meta)
    catalogue = independent_normalize_catalog(args.input)
    assignments = enumerate_assignments(catalogue)
    keys = {(row["record_index"], row["representative_index"]): row for row in assignments}
    if args.select:
        missing = sorted(set(args.select) - set(keys))
        if missing:
            parser.error(f"unknown selections: {missing}")
        selected = [keys[key] for key in args.select]
    else:
        end = len(assignments) if args.end_global is None else args.end_global
        selected = [
            row for row in assignments
            if args.start_global <= row["global_representative_index"] < end
        ]

    if args.output.exists():
        if not args.resume:
            parser.error("output exists; use --resume or choose a new output")
        result = json.loads(args.output.read_text(encoding="utf-8"))
        if result.get("base_cnf_sha256") != baseline["sha256"]:
            raise ValueError("checkpoint baseline hash changed")
        if result.get("catalogue", {}).get("sha256") != catalogue["catalogue_sha256"]:
            raise ValueError("checkpoint catalogue hash changed")
        if result.get("generator", {}).get("coordinate_sha256") != coordinate_sha256():
            raise ValueError("checkpoint coordinate map changed")
    else:
        result = _new_document(baseline, args.input, catalogue, args)

    imported_cores = load_portable_cores(args.core_file, baseline["sha256"])
    # Direct cores already saved in this exact checkpoint are also reusable.
    checkpoint_core_path = args.output if args.output.exists() else None
    if checkpoint_core_path is not None:
        imported_cores.extend(load_portable_cores([checkpoint_core_path], baseline["sha256"]))
    by_core_hash = {core["literal_set_sha256"]: core for core in imported_cores}
    cores = sorted(by_core_hash.values(), key=lambda core: (core["size"], core["literal_set_sha256"]))

    terminal = {"SAT", "SAT_INVALID", "UNSAT", "COVERED_UNSAT"}
    pending = [
        row for row in selected
        if result["results"].get(
            f"r{row['record_index']}:b{row['representative_index']}", {}
        ).get("status") not in terminal
    ]

    # Screen before loading the 30 MB formula and 1.6 M clauses.
    direct_pending = []
    for assignment in pending:
        key = f"r{assignment['record_index']}:b{assignment['representative_index']}"
        covering = next(
            (core for core in cores if core["literals"] <= assignment["literal_set"]),
            None,
        )
        if covering is not None:
            row = _public_assignment(assignment)
            row.update({
                "status": "COVERED_UNSAT",
                "cover_core_literal_set_sha256": covering["literal_set_sha256"],
                "cover_core_size": covering["size"],
                "cover_source": covering["source"],
                "formal_proof_certificate": None,
            })
            result["results"][key] = row
            atomic_write_json(args.output, result)
        elif args.screen_only:
            row = _public_assignment(assignment)
            row.update({
                "status": "NOT_CORE_COVERED",
                "portable_cores_tested": len(cores),
            })
            result["results"][key] = row
            atomic_write_json(args.output, result)
        else:
            direct_pending.append(assignment)

    if direct_pending:
        dependency_root = str(Path(".deps").resolve())
        if dependency_root not in sys.path:
            sys.path.insert(0, dependency_root)
        from pysat.formula import CNF
        from pysat.solvers import Solver

        formula_started = time.monotonic()
        formula = CNF(from_file=str(args.base_cnf))
        with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
            result["baseline_load_seconds"] = round(time.monotonic() - formula_started, 6)
            del formula
            for assignment in direct_pending:
                key = f"r{assignment['record_index']}:b{assignment['representative_index']}"
                # Cores learned earlier in this invocation may now cover the row.
                covering = next(
                    (core for core in cores if core["literals"] <= assignment["literal_set"]),
                    None,
                )
                row = _public_assignment(assignment)
                if covering is not None:
                    row.update({
                        "status": "COVERED_UNSAT",
                        "cover_core_literal_set_sha256": covering["literal_set_sha256"],
                        "cover_core_size": covering["size"],
                        "cover_source": covering["source"],
                        "formal_proof_certificate": None,
                    })
                else:
                    before = solver.accum_stats()
                    solve_started = time.monotonic()
                    if args.conflicts:
                        solver.conf_budget(args.conflicts)
                        answer = solver.solve_limited(
                            assumptions=list(assignment["literals"]), expect_interrupt=True
                        )
                    else:
                        answer = solver.solve(assumptions=list(assignment["literals"]))
                    after = solver.accum_stats()
                    status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
                    row.update({
                        "status": status,
                        "solve_seconds": round(time.monotonic() - solve_started, 6),
                        "stats_delta": {
                            name: after.get(name, 0) - before.get(name, 0)
                            for name in sorted(set(before) | set(after))
                        },
                        "formal_proof_certificate": None,
                    })
                    if answer is False:
                        raw_core = tuple(map(int, solver.get_core() or ()))
                        if not raw_core or not frozenset(raw_core) <= assignment["literal_set"]:
                            raise AssertionError("solver returned an invalid assumption core")
                        core_hash = literal_set_sha256(raw_core)
                        row.update({
                            "core_size": len(raw_core),
                            "core_literals": list(raw_core),
                            "core_literal_set_sha256": core_hash,
                        })
                        core = {
                            "literals": frozenset(raw_core),
                            "literal_set_sha256": core_hash,
                            "size": len(raw_core),
                            "source": {
                                "file": str(args.output),
                                "record_index": assignment["record_index"],
                                "representative_index": assignment["representative_index"],
                                "global_representative_index": assignment[
                                    "global_representative_index"
                                ],
                            },
                        }
                        cores.append(core)
                        cores.sort(key=lambda item: (item["size"], item["literal_set_sha256"]))
                    elif answer is True:
                        from scratch_general_exact_sat import verify

                        positive = {
                            literal
                            for literal in solver.get_model()
                            if 0 < literal <= 3486
                        }
                        checked = verify(positive)
                        row["verification"] = {
                            name: value for name, value in checked.items() if name != "edges"
                        }
                        if not checked.get("ok"):
                            row["status"] = "SAT_INVALID"
                        else:
                            solution_path = args.output.with_name(
                                args.output.stem + "_verified_solution.json"
                            )
                            atomic_write_json(solution_path, checked)
                            row["verified_solution_path"] = str(solution_path)
                result["results"][key] = row
                result["last_update_unix"] = time.time()
                atomic_write_json(args.output, result)
                print(json.dumps({
                    "key": key,
                    "status": row["status"],
                    "conflicts": row.get("stats_delta", {}).get("conflicts"),
                    "core_size": row.get("core_size"),
                }, sort_keys=True), flush=True)
                if row["status"] in ("SAT", "SAT_INVALID"):
                    break

    statuses = Counter(row["status"] for row in result["results"].values())
    result["status_counts"] = dict(sorted(statuses.items()))
    result["selected_this_invocation"] = len(selected)
    result["portable_core_count_loaded_or_learned"] = len(cores)
    result["wall_seconds_last_invocation"] = round(time.monotonic() - started, 6)
    atomic_write_json(args.output, result)
    print(json.dumps({
        "output": str(args.output),
        "status_counts": result["status_counts"],
        "wall_seconds": result["wall_seconds_last_invocation"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
