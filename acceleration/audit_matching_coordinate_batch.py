"""Audit positive whole-matching certificates and their labeled-family union.

The numerical zero diagnostics remain unresolved. No solver is run, and no
producer/model-builder is imported. Existing audits may be reused only through
equal candidate, matrix and certificate bytes plus verified source hashes.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from math import comb, factorial
from pathlib import Path
import time

from audit_certificate import full_graph, require
from audit_matching_farkas import audit


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def family_partition(candidate):
    graph, _ = full_graph(candidate)
    labels = [{s - 1 for s in graph[u + 15] if 1 <= s <= 14} for u in range(84)]
    require(all(len(row) == 2 and len({s // 2 for s in row}) == 2 for row in labels),
            "Expected two distinct root-group labels per outer vertex")
    supports = [{s // 2 for s in row} for row in labels]
    coordinates = [(g, k) for g in range(7) for k in ("same_0", "same_1", "cross")]
    domains = {coordinate: set() for coordinate in coordinates}
    for u, v in combinations(range(84), 2):
        shared = supports[u] & supports[v]
        if len(shared) != 1:
            continue
        g = next(iter(shared))
        a = next(s % 2 for s in labels[u] if s // 2 == g)
        b = next(s % 2 for s in labels[v] if s // 2 == g)
        domains[g, "cross" if a != b else f"same_{a}"].add((u, v))
    combined = set()
    for edges in domains.values():
        require(not combined & edges, "Allowed matching edge domains overlap")
        combined.update(edges)
    require(len(combined) == 1680, "Wrong full allowed overlap edge-domain size")
    base = {(u, v) for u, v in combinations(range(84), 2) if v + 15 in graph[u + 15]}
    require(len(base) == 168 and base <= combined, "Base K is not a partition of the matching domains")
    checked = []
    for (g, kind), edges in domains.items():
        vertices = {u for e in edges for u in e}
        chosen = base & edges
        expected_vertices = 24 if kind == "cross" else 12
        require(len(vertices) == expected_vertices and len(edges) == 5 * expected_vertices,
                "Wrong matching coordinate domain size")
        require(Counter(u for e in chosen for u in e) == Counter({u: 1 for u in vertices}),
                "Base coordinate is not a perfect matching")
        # Independently check the forbidden boards that give the two counts.
        if kind == "cross":
            left = {u for u in vertices if 2 * g in labels[u]}
            right = vertices - left
            require(len(left) == len(right) == 12, "Wrong bipartition")
            expected_edges = {(min(u, v), max(u, v)) for u in left for v in right
                              if supports[u] & supports[v] == {g}}
        else:
            expected_edges = {(u, v) for u, v in combinations(sorted(vertices), 2)
                              if supports[u] != supports[v]}
        require(edges == expected_edges, "Forbidden-board identity failed")
        for other_group in set(range(7)) - {g}:
            fibre = {u for u in vertices if other_group in supports[u]}
            require(len(fibre) == (4 if kind == "cross" else 2), "Wrong forbidden fibre size")
            if kind == "cross":
                require(len(fibre & left) == len(fibre & right) == 2, "Wrong K2,2 forbidden block")
        checked.append(dict(root_group=g, matching_class=kind, allowed_edges=len(edges),
                            base_matching_edges=len(chosen), vertices=len(vertices)))
    # Inclusion-exclusion over six forbidden same-fibre edges for same-sign.
    same_count = sum((-1) ** k * comb(6, k) * factorial(12 - 2 * k) //
                     (2 ** (6 - k) * factorial(6 - k)) for k in range(7))
    # For cross, six disjoint forbidden K2,2 boards: rook polynomial
    # (1 + 4t + 2t^2)^6, followed by ordinary permutation inclusion-exclusion.
    rook = [1]
    for _ in range(6):
        after = [0] * (len(rook) + 2)
        for i, a in enumerate(rook):
            for j, b in enumerate((1, 4, 2)):
                after[i + j] += a * b
        rook = after
    cross_count = sum((-1) ** k * a * factorial(12 - k) for k, a in enumerate(rook))
    require(same_count == 6040 and cross_count == 59245120, "Unexpected exact family counts")
    return dict(coordinates=checked, allowed_edge_domains_pairwise_disjoint=True,
                allowed_domain_union_edges=len(combined), base_edges_partitioned=len(base),
                same_sign_count=same_count, cross_count=cross_count, cross_forbidden_rook_coefficients=rook,
                intersection_proof="Every family fixes all edge domains except its own; two distinct-coordinate families can therefore share only the unchanged base K. Each family contains that base K.")


def run(candidate_path, summary_path, out_path, reuse_paths):
    require(not out_path.exists(), "Preserve existing batch audit")
    started = time.perf_counter()
    summary = json.loads(summary_path.read_bytes())
    require(summary["status"] == "BOUNDED_21_MATCHING_COORDINATE_LP_SWEEP_FINISHED", "Nonterminal sweep")
    bindings = {}

    def bind(path, expected=None):
        path = Path(path)
        actual = digest(path)
        require(expected is None or actual == expected, "Changed dependency: " + str(path))
        bindings[str(path)] = actual
        return actual

    candidate_sha = bind(candidate_path)
    bind(summary_path)
    for mapping in (summary["inputs_sha256"], summary["outputs_sha256"]):
        for path, expected in mapping.items():
            bind(path, expected)
    source_dir = Path(__file__).parent
    audit_sha = bind(source_dir / "audit_matching_farkas.py")
    graph_sha = bind(source_dir / "audit_certificate.py")
    bind(Path(__file__))
    prior = []
    for path in reuse_paths:
        bind(path)
        report = json.loads(path.read_bytes())
        require(report["status"] == "INDEPENDENT_WHOLE_MATCHING_MATRIX_AND_INTEGER_FARKAS_AUDIT_PASS"
                and report["auditor_sha256"] == audit_sha and report["graph_auditor_sha256"] == graph_sha,
                "Reused audit status/source mismatch")
        for name, expected in report["inputs_sha256"].items():
            bind(name, expected)
        prior.append((path, report))
    records = summary["records"]
    coords = [(r["root_group"], r["matching_class"]) for r in records]
    expected_coords = {(g, k) for g in range(7) for k in ("same_0", "same_1", "cross")}
    require(len(coords) == 21 and set(coords) == expected_coords, "Missing/duplicate matching coordinate")
    results = []
    for record in records:
        coordinate = record["root_group"], record["matching_class"]
        matrix_path, result_path = Path(record["matrix_path"]), Path(record["result_path"])
        matrix_sha = bind(matrix_path, record["matrix_sha256"])
        bind(result_path, record["result_sha256"])
        matrix, numeric = (json.loads(p.read_bytes()) for p in (matrix_path, result_path))
        require((matrix["root_group"], matrix["matching_class"]) == coordinate and
                (numeric["root_group"], numeric["matching_class"]) == coordinate,
                "Coordinate provenance mismatch")
        require(numeric["matrix_sha256"] == matrix_sha and numeric["numeric_objective"] == record["numeric_objective"],
                "Recorded numerical diagnostic differs from source")
        require(any(Path(name).resolve() == candidate_path.resolve() and value == candidate_sha
                    for name, value in matrix["inputs_sha256"].items()), "Different base candidate")
        for name, value in matrix["inputs_sha256"].items():
            bind(name, value)
        item = dict(root_group=coordinate[0], matching_class=coordinate[1],
                    numeric_classification=record["classification"], numeric_objective=record["numeric_objective"],
                    matrix_path=str(matrix_path), matrix_sha256=matrix_sha,
                    result_path=str(result_path), result_sha256=digest(result_path))
        if record["classification"] == "NUMERICALLY_POSITIVE":
            certificate_path = Path(record["certificate_path"])
            cert_sha = bind(certificate_path, record["certificate_sha256"])
            matching_prior = [(p, r) for p, r in prior if
                              set(r["inputs_sha256"].values()) == {candidate_sha, matrix_sha, cert_sha}]
            if matching_prior:
                audit_path, report = matching_prior[0]
                reused = True
            else:
                audit_path = out_path.parent / f"group_{coordinate[0]}_{coordinate[1]}_independent_audit.json"
                require(not audit_path.exists(), "Preserve prior coordinate audit")
                report = audit(candidate_path, matrix_path, certificate_path)
                with audit_path.open("x", encoding="utf-8") as stream:
                    stream.write(json.dumps(report, indent=2) + "\n")
                reused = False
            require((report["root_group"], report["matching_class"]) == coordinate and
                    report["contradiction_margin"] == record["integer_contradiction_margin"],
                    "Audited coordinate/margin mismatch")
            item.update(status="EXACT_ONE_COORDINATE_EXCLUSION", certificate_path=str(certificate_path),
                        certificate_sha256=cert_sha, audit_path=str(audit_path), audit_sha256=bind(audit_path),
                        reused_byte_identical_prior_certificate_audit=reused,
                        contradiction_margin=report["contradiction_margin"],
                        allowed_binary_matchings_before_partial_caps=report["allowed_binary_matchings_before_partial_caps"])
        else:
            require(record["classification"] in ("NUMERICALLY_ZERO", "CAPPED_OR_UNRESOLVED"), "Unknown classification")
            item.update(status="NO_EXACT_EXCLUSION_OR_FEASIBILITY_CLAIM", numerical_semantics_independently_proved=False)
        results.append(item)
    partition = family_partition(json.loads(candidate_path.read_bytes()))
    proved = [r for r in results if r["status"] == "EXACT_ONE_COORDINATE_EXCLUSION"]
    counts = Counter("cross" if r["matching_class"] == "cross" else "same_sign" for r in proved)
    for item in proved:
        expected = partition["cross_count" if item["matching_class"] == "cross" else "same_sign_count"]
        require(item["allowed_binary_matchings_before_partial_caps"] == expected, "Family count disagreement")
    union = 1 + sum(item["allowed_binary_matchings_before_partial_caps"] - 1 for item in proved) if proved else 0
    report = dict(status="INDEPENDENT_POSITIVE_MATCHING_COORDINATE_BATCH_AND_FAMILY_UNION_AUDIT_PASS",
                  inputs_sha256=bindings, candidate_sha256=candidate_sha, records=results,
                  coordinates_in_numerical_sweep=len(records), exact_excluded_coordinates=len(proved),
                  exact_same_sign_families=counts["same_sign"], exact_cross_families=counts["cross"],
                  numeric_only_unresolved_coordinates=len(records)-len(proved),
                  new_independent_matrix_and_integer_audits=sum(not r["reused_byte_identical_prior_certificate_audit"] for r in proved),
                  reused_byte_identical_certificate_audits=sum(r["reused_byte_identical_prior_certificate_audit"] for r in proved),
                  independently_verified_coordinate_partition=partition,
                  labeled_overlap_patterns_excluded_in_proven_union=union,
                  union_count_formula="1 + n_same*(6040-1) + n_cross*(59245120-1), when at least one family is proved",
                  union_count_includes_support_allowed_patterns_before_partial_caps=True,
                  simultaneous_changes_to_multiple_coordinates_covered=False,
                  no_global_E0_or_Conway_nonexistence_claim=True,
                  no_numerical_zero_is_claimed_exactly_feasible=True,
                  no_phase1_local_minimality_claim=True,
                  elapsed_seconds=time.perf_counter()-started,
                  scope="Exact labeled-family union around this one base K only. Other20 coordinates are fixed separately for each certificate. Counts include patterns already invalid under partial caps; this is not an orbit count or global search coverage.")
    with out_path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--reuse-audit", type=Path, action="append", default=[])
    args = parser.parse_args()
    result = run(args.candidate, args.summary, args.out, args.reuse_audit)
    print(json.dumps({k: v for k, v in result.items() if k not in ("inputs_sha256", "records", "independently_verified_coordinate_partition")}, indent=2))


if __name__ == "__main__":
    main()
