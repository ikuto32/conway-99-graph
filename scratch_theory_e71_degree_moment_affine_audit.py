"""Producer-independent replay of all frozen E71 affine moment decisions."""

from collections import Counter
from fractions import Fraction as F
import hashlib
import itertools as it
import json
import math
from pathlib import Path
import time


CATALOG = Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json")
MINING = Path("scratch_theory_e71_e72_e0_moment_mining.json")
KERNEL = Path("scratch_theory_e71_equitable_kernel_port_census.json")
PRODUCER = Path("scratch_theory_e71_degree_moment_affine_probe.py")
PROBE = Path("scratch_theory_e71_degree_moment_affine_probe.json")
OUTPUT = Path("scratch_theory_e71_degree_moment_affine_audit.json")
SUPPORTS = tuple(it.combinations(range(7), 2))


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def key(row):
    return tuple(int(row[x]) for x in ("source_row_index", "state_orbit_number", "signature_stabilizer_orbit_number"))


def multiply(a, b):
    columns = tuple(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in columns] for row in a]


def inverse(matrix):
    n = len(matrix)
    a = [[F(v) for v in row] + [F(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        selected = next(i for i in range(col, n) if a[i][col])
        a[col], a[selected] = a[selected], a[col]
        scale = a[col][col]
        a[col] = [v / scale for v in a[col]]
        for row in range(n):
            if row != col:
                factor = a[row][col]
                a[row] = [x - factor * y for x, y in zip(a[row], a[col])]
    return [row[n:] for row in a]


def echelon(vectors):
    basis = {}
    for vector in vectors:
        row = list(map(F, vector))
        for pivot in sorted(basis):
            factor = row[pivot]
            if factor:
                row = [a - factor * b for a, b in zip(row, basis[pivot])]
        first = next((i for i, v in enumerate(row) if v), None)
        if first is not None:
            scale = row[first]
            basis[first] = [v / scale for v in row]
    return basis


def is_in_span(vector, basis):
    row = list(map(F, vector))
    for pivot in sorted(basis):
        factor = row[pivot]
        row = [a - factor * b for a, b in zip(row, basis[pivot])]
    return not any(row)


def compression(entry, profile):
    ex = [SUPPORTS.index(tuple(item["support"])) for item in entry["exceptional_supports"]]
    c0 = [[8 if i == j else (4 if set(a).isdisjoint(b) else 0)
           for j, b in enumerate(SUPPORTS)] for i, a in enumerate(SUPPORTS)]
    c = [row[:] for row in c0]
    for i, item in zip(ex, entry["exceptional_supports"]):
        c[i][i] -= 2 * int(item["deficit"])
    for table in (entry["overlap_block_totals"], profile["disjoint_D"]):
        for a, b, v in table:
            c[ex[a]][ex[b]] = c[ex[b]][ex[a]] = int(v)
    assert all(sum(row) == 48 for row in c)
    z = [[c0[i][j] - c[i][j] for j in range(21)] for i in range(21)]
    z2, c2 = multiply(z, z), multiply(c, c)
    k = [[28 * z[i][j] - z2[i][j] for j in range(21)] for i in range(21)]
    assert k == [[192 * int(i == j) + 128 - 4 * c[i][j] - c2[i][j]
                  - 32 * len(set(SUPPORTS[i]) & set(SUPPORTS[j])) for j in range(21)] for i in range(21)]
    return ex, c, k


def position_degrees(entry, exceptional, c):
    labels = [(2 * a + p, 2 * b + q) for a, b in SUPPORTS for p, q in it.product((0, 1), repeat=2)]
    index = {label: i for i, label in enumerate(labels)}
    degrees = [[0] * 4 if i in exceptional else [2] * 4 for i in range(21)]
    for left, right in entry["internal_edges"]:
        x, y = index[tuple(left)], index[tuple(right)]
        assert x // 4 == y // 4 and x // 4 in exceptional
        degrees[x // 4][x % 4] += 1
        degrees[y // 4][y % 4] += 1
    assert all(sum(degrees[i]) == c[i][i] for i in range(21))
    return degrees


def replay(entry, source, stored):
    exceptional, c, k = compression(entry, source)
    pivots = tuple(stored["pivot_indices"])
    rank = len(echelon(k))
    assert len(pivots) == rank == stored["K4_rank"]
    minor = [[k[i][j] for j in pivots] for i in pivots]
    # Reconstruct from principal columns instead of using the producer RREF.
    coordinates = multiply(inverse(minor), [k[i] for i in pivots])
    assert multiply([[row[i] for i in pivots] for row in k], coordinates) == k
    scale = math.lcm(*(v.denominator for row in coordinates for v in row))
    transform = [[int(v * scale) for v in row] for row in coordinates]
    upper = tuple(it.combinations_with_replacement(range(rank), 2))
    assert stored["moment_coordinates"] == list(map(list, upper))
    degrees = position_degrees(entry, exceptional, c)
    position_domains = []
    pattern_count = 0
    for source_fibre in range(21):
        by_degree = {}
        values = [range(-c[source_fibre][p], 17 - c[source_fibre][p], 4) for p in pivots]
        for pivot_values in it.product(*values):
            residual_scaled = [sum(pivot_values[i] * transform[i][j] for i in range(rank)) for j in range(21)]
            degree_numerators = [v + c[source_fibre][j] * scale for j, v in enumerate(residual_scaled)]
            if any(v < 0 or v > 16 * scale or v % (4 * scale) for v in degree_numerators):
                continue
            if sum(degree_numerators) != 48 * scale:
                continue
            pattern_count += 1
            own_degree = degree_numerators[source_fibre] // (4 * scale)
            moment = tuple(pivot_values[i] * pivot_values[j] for i, j in upper)
            by_degree.setdefault(own_degree, set()).add(moment)
        position_domains.extend(tuple(sorted(by_degree.get(degree, ()))) for degree in degrees[source_fibre])
    assert pattern_count == stored["raw_row_patterns"]
    assert list(map(len, position_domains)) == stored["position_domain_sizes"]
    digest = hashlib.sha256(json.dumps(position_domains).encode()).hexdigest().upper()
    assert digest == stored["position_domains_sha256"]
    assert all(position_domains)
    target = tuple(4 * k[pivots[i]][pivots[j]] for i, j in upper)
    baseline = tuple(sum(domain[0][i] for domain in position_domains) for i in range(len(upper)))
    assert list(target) == stored["target"] and list(baseline) == stored["baseline_sum"]
    differences = {tuple(a - b for a, b in zip(option, domain[0]))
                   for domain in position_domains for option in domain}
    span = echelon(differences)
    assert len(span) == stored["difference_span_rank"]
    assert len(upper) - len(span) == stored["affine_codimension"]
    gap = tuple(a - b for a, b in zip(target, baseline))
    inconsistent = not is_in_span(gap, span)
    assert inconsistent == stored["affine_inconsistent"]
    certificate = stored["certificate"]
    if inconsistent:
        assert certificate is not None
        coeff = tuple(certificate["upper_triangle_coefficients"])
        values = []
        for domain in position_domains:
            exact_values = {sum(a * b for a, b in zip(coeff, option)) for option in domain}
            assert len(exact_values) == 1
            values.append(next(iter(exact_values)))
        required = sum(a * b for a, b in zip(coeff, target))
        forced = sum(values)
        assert values == certificate["forced_per_exact_position"]
        assert forced == certificate["forced_sum"]
        assert required == certificate["Gram_required_sum"]
        assert required - forced == certificate["gap"] != 0
    else:
        assert certificate is None
    return {"parameter": stored["parameter"], "raw_rows": pattern_count,
            "affine_inconsistent": inconsistent, "position_domain_hash_verified": True,
            "certificate": certificate}


def main():
    start = time.monotonic()
    catalog, mining, kernel, probe = map(read, (CATALOG, MINING, KERNEL, PROBE))
    assert probe["status"] == "E71_DEGREE_MOMENT_AFFINE_FRONTIER_COMPLETE"
    for path, wanted in probe["inputs_sha256"].items():
        assert sha(Path(path)) == wanted, path
    entries = {key(row): row for row in catalog["macro_entries"] if row["signature_stabilizer_canonical"]}
    profiles = {(key(row), row["parameter"]): row for row in mining["profile_rows"]["71"]}
    retained = {tuple(row["key"]): row for row in kernel["rows"] if row["macro_passes_some_full_Gram_profile_kernel_port_CSP"]}
    records = {tuple(row["key"]): row for row in probe["rows"]}
    assert len(records) == len(probe["rows"]) == 132 and records.keys() == retained.keys()
    summary = Counter()
    verified = []
    for number, (macro_key, record) in enumerate(records.items(), 1):
        expected = sorted(p["parameter"] for p in retained[macro_key]["profiles"] if p["passes_kernel_port_CSP"])
        assert expected == sorted(p["parameter"] for p in record["profiles"])
        checked = []
        for p in record["profiles"]:
            result = replay(entries[macro_key], profiles[(macro_key, p["parameter"])], p)
            checked.append(result)
            summary["profiles_tested"] += 1
            summary["raw_rows"] += result["raw_rows"]
            summary["profiles_rejected"] += int(result["affine_inconsistent"])
        assert record["coverage"] == retained[macro_key]["coverage"] == int(entries[macro_key]["signature_orbit_labelled_coverage"])
        rejected = bool(checked) and all(p["affine_inconsistent"] for p in checked)
        assert rejected == record["macro_rejected"]
        summary["macros_tested"] += 1
        summary["coverage_tested"] += record["coverage"]
        summary["macros_rejected"] += int(rejected)
        summary["coverage_rejected"] += record["coverage"] * int(rejected)
        verified.append({"key": list(macro_key), "coverage": record["coverage"],
                         "macro_rejected": rejected, "profiles": checked})
        if number % 20 == 0:
            print(json.dumps({"macros_replayed": number, "elapsed_seconds": round(time.monotonic() - start, 2)}), flush=True)
    assert dict(summary) == probe["summary"]
    assert summary["profiles_tested"] == 140 and summary["profiles_rejected"] == 4
    result = {"status": "INDEPENDENT_E71_DEGREE_MOMENT_AFFINE_AUDIT_PASS", "producer_imported": False,
              "inputs_sha256": {str(p): sha(p) for p in (CATALOG, MINING, KERNEL, PRODUCER, PROBE)},
              "verified_summary": dict(summary), "rows": verified,
              "method": "Independent principal-column inverse raw-row reconstruction, all position-domain hashes, incremental exact echelon affine-membership replay, and pointwise verification of every scalar certificate.",
              "scope": "The frozen 132-macro/140-profile frontier only. Three macros are excluded by four rational scalar certificates. No claim that passing affine moment domains form graphs.",
              "elapsed_seconds": round(time.monotonic() - start, 3), "submission_txt_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": dict(summary), "elapsed_seconds": result["elapsed_seconds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
