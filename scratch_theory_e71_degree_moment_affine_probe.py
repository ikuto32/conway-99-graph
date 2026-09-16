"""Affine quadratic-moment support test on the frozen 140 E71 profiles.

Only raw one-vertex degree rows are generated. No quartet, overlap, matching,
binary-block, or local-graph products are enumerated.
"""

from collections import Counter
from fractions import Fraction
import hashlib
import itertools as it
import json
import math
from pathlib import Path
import time

import scratch_theory_e71_projector_transport_frontier_audit as base


OUTPUT = Path("scratch_theory_e71_degree_moment_affine_probe.json")


def primitive(vector):
    scale = math.lcm(*(v.denominator for v in vector))
    values = [int(v * scale) for v in vector]
    divisor = math.gcd(*values)
    values = [v // divisor for v in values]
    if next(v for v in values if v) < 0:
        values = [-v for v in values]
    return tuple(values)


def raw_domains(c, k4):
    basis, pivots = base.reduced(k4)
    dimension = len(pivots)
    scale = math.lcm(*(v.denominator for row in basis for v in row))
    columns = tuple(tuple(int(row[j] * scale) for row in basis) for j in range(21))
    pairs = tuple(it.combinations_with_replacement(range(dimension), 2))
    domains = []
    for source in range(21):
        patterns = []
        for pivot_degrees in it.product(range(5), repeat=dimension):
            pivot_values = tuple(4 * d - c[source][p] for d, p in zip(pivot_degrees, pivots))
            degrees = []
            for j, col in enumerate(columns):
                numerator = base.dot(pivot_values, col) + c[source][j] * scale
                if numerator % (4 * scale) or not 0 <= numerator <= 16 * scale:
                    break
                degrees.append(numerator // (4 * scale))
            else:
                if sum(degrees) == 12:
                    patterns.append({"degree_self": degrees[source],
                                     "pivot": pivot_values,
                                     "moment": tuple(pivot_values[i] * pivot_values[j] for i, j in pairs)})
        assert len({p["pivot"] for p in patterns}) == len(patterns)
        domains.append(patterns)
    return pivots, pairs, domains


def internal_degrees(entry):
    exceptional = {tuple(row["support"]) for row in entry["exceptional_supports"]}
    labels = {label: i for i, label in enumerate(base.LABELS)}
    values = [[0] * 4 if support in exceptional else [2] * 4 for support in base.SUPPORTS]
    for left, right in entry["internal_edges"]:
        x, y = labels[tuple(left)], labels[tuple(right)]
        assert x // 4 == y // 4 and base.SUPPORTS[x // 4] in exceptional
        values[x // 4][x % 4] += 1
        values[y // 4][y % 4] += 1
    return values


def analyze(entry, profile):
    _, c, _, k4 = base.compression(entry, profile)
    pivots, pairs, domains = raw_domains(c, k4)
    degrees = internal_degrees(entry)
    width = len(pairs)
    baseline = [0] * width
    differences = set()
    position_domains = []
    empty_positions = []
    for source, domain in enumerate(domains):
        assert sum(degrees[source]) == c[source][source]
        for local, degree in enumerate(degrees[source]):
            options = tuple(sorted({p["moment"] for p in domain if p["degree_self"] == degree}))
            position_domains.append(options)
            if not options:
                empty_positions.append([source, local])
                continue
            initial = options[0]
            baseline = [a + b for a, b in zip(baseline, initial)]
            differences.update(tuple(a - b for a, b in zip(option, initial)) for option in options)
    target = tuple(4 * k4[pivots[i]][pivots[j]] for i, j in pairs)
    gap = tuple(a - b for a, b in zip(target, baseline))
    difference_rows = sorted(differences - {(0,) * width})
    if difference_rows:
        span, span_pivots = base.reduced(difference_rows)
    else:
        span, span_pivots = [], ()
    certificate = None
    for free in range(width):
        if free in span_pivots:
            continue
        vector = [Fraction(int(i == free)) for i in range(width)]
        for row, pivot in zip(span, span_pivots):
            vector[pivot] = -row[free]
        coeff = primitive(vector)
        assert all(base.dot(coeff, row) == 0 for row in difference_rows)
        if base.dot(coeff, gap):
            values = []
            for domain in position_domains:
                value_set = {base.dot(coeff, option) for option in domain}
                assert len(value_set) == 1
                values.append(next(iter(value_set)))
            forced, required = sum(values), base.dot(coeff, target)
            assert forced != required
            certificate = {"upper_triangle_coefficients": list(coeff),
                           "forced_per_exact_position": values,
                           "forced_sum": forced, "Gram_required_sum": required,
                           "gap": required - forced}
            break
    return {"parameter": profile["parameter"], "K4_rank": len(pivots),
            "raw_row_patterns": sum(map(len, domains)), "pivot_indices": list(pivots),
            "pivot_supports": [list(base.SUPPORTS[i]) for i in pivots],
            "moment_coordinates": [list(pair) for pair in pairs],
            "moment_dimension": width, "difference_span_rank": len(span_pivots),
            "affine_codimension": width - len(span_pivots),
            "position_domain_sizes": list(map(len, position_domains)),
            "empty_positions": empty_positions, "target": list(target), "baseline_sum": baseline,
            "affine_inconsistent": bool(empty_positions or certificate is not None),
            "certificate": certificate,
            "position_domains_sha256": hashlib.sha256(json.dumps(position_domains).encode()).hexdigest().upper()}


def main():
    started = time.monotonic()
    catalog, mining, kernel = map(base.read, (base.CATALOG, base.MINING, base.KERNEL))
    entries = {base.key(row): row for row in catalog["macro_entries"] if row["signature_stabilizer_canonical"]}
    profiles = {(base.key(row), row["parameter"]): row for row in mining["profile_rows"]["71"]}
    retained = [row for row in kernel["rows"] if row["macro_passes_some_full_Gram_profile_kernel_port_CSP"]]
    assert len(retained) == 132
    results = []
    summary = Counter()
    for index, macro in enumerate(retained, 1):
        key = tuple(macro["key"])
        tested = []
        for profile in macro["profiles"]:
            if profile["passes_kernel_port_CSP"]:
                result = analyze(entries[key], profiles[(key, profile["parameter"])])
                tested.append(result)
                summary["profiles_tested"] += 1
                summary["raw_rows"] += result["raw_row_patterns"]
                summary["profiles_rejected"] += int(result["affine_inconsistent"])
        rejected = all(p["affine_inconsistent"] for p in tested)
        assert tested
        summary["macros_tested"] += 1
        summary["coverage_tested"] += macro["coverage"]
        summary["macros_rejected"] += int(rejected)
        summary["coverage_rejected"] += macro["coverage"] * int(rejected)
        results.append({"key": list(key), "coverage": macro["coverage"],
                        "profiles": tested, "macro_rejected": rejected})
        if index % 20 == 0:
            print(json.dumps({"processed_macros": index, "rejected_macros": summary["macros_rejected"],
                              "elapsed_seconds": round(time.monotonic() - started, 2)}), flush=True)
    assert summary["profiles_tested"] == 140 and summary["raw_rows"] == 23137
    result = {"status": "E71_DEGREE_MOMENT_AFFINE_FRONTIER_COMPLETE",
              "inputs_sha256": {str(p): base.sha(p) for p in (base.CATALOG, base.MINING, base.KERNEL, Path(base.__file__))},
              "scope": "The frozen 132 macros and their 140 kernel-port-passing profiles; raw one-vertex row domains and affine quadratic moment support only.",
              "summary": dict(summary), "rows": results,
              "elapsed_seconds": round(time.monotonic() - started, 3),
              "claim_boundary": "Each certificate is a necessary scalar moment contradiction; no overlap, quartet or local graph completion is enumerated. Macro exclusions require every retained profile to contradict, together with prior frozen profile coverage.",
              "submission_txt_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": result["summary"],
                      "elapsed_seconds": result["elapsed_seconds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
