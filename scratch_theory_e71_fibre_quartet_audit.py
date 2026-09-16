"""Independent exact scalar certificate for the two source694 E71 macros.

No producer/helper module is imported.  The proof uses all raw degree rows,
not the row-norm filter, the quartet PSD test, or the moment dynamic program.
"""

from fractions import Fraction as F
import hashlib
import itertools as it
import json
from pathlib import Path


CATALOG = Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json")
MINING = Path("scratch_theory_e71_e72_e0_moment_mining.json")
KERNEL = Path("scratch_theory_e71_equitable_kernel_port_census.json")
PROBE = Path("scratch_theory_e71_fibre_quartet_probe.json")
PRODUCER = Path("scratch_theory_e71_fibre_quartet_probe.py")
OUTPUT = Path("scratch_theory_e71_fibre_quartet_audit.json")
SUPPORTS = tuple(it.combinations(range(7), 2))
TARGETS = ((694, 0, 0), (694, 1, 0))


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def key(row):
    return tuple(int(row[field]) for field in ("source_row_index", "state_orbit_number", "signature_stabilizer_orbit_number"))


def times(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
            for i in range(len(a))]


def build(entry, profile):
    ex = [SUPPORTS.index(tuple(item["support"])) for item in entry["exceptional_supports"]]
    c0 = [[8 if i == j else (4 if set(a).isdisjoint(b) else 0)
           for j, b in enumerate(SUPPORTS)] for i, a in enumerate(SUPPORTS)]
    c = [row[:] for row in c0]
    for i, item in zip(ex, entry["exceptional_supports"]):
        c[i][i] = 2 * (4 - int(item["deficit"]))
    overlaps = {(min(a, b), max(a, b)): value for a, b, value in entry["overlap_block_totals"]}
    disjoint = {(min(a, b), max(a, b)): value for a, b, value in profile["disjoint_D"]}
    for a, b in it.combinations(range(len(ex)), 2):
        i, j = ex[a], ex[b]
        values = disjoint if set(SUPPORTS[i]).isdisjoint(SUPPORTS[j]) else overlaps
        c[i][j] = c[j][i] = int(values[(a, b)])
    assert all(sum(row) == 48 for row in c)
    z = [[c0[i][j] - c[i][j] for j in range(21)] for i in range(21)]
    z2, c2 = times(z, z), times(c, c)
    k = [[28 * z[i][j] - z2[i][j] for j in range(21)] for i in range(21)]
    assert k == [[192 * int(i == j) + 128 - 4 * c[i][j]
                  - 32 * len(set(SUPPORTS[i]) & set(SUPPORTS[j])) - c2[i][j]
                  for j in range(21)] for i in range(21)]
    return ex, c, k


def ordinary_degree_theorem():
    """Four-vertex triangle-free graphs with four edges are all 2-regular."""
    pairs = tuple(it.combinations(range(4), 2))
    retained = []
    for chosen in it.combinations(pairs, 4):
        edges = set(chosen)
        if any(all(pair in edges for pair in it.combinations(triple, 2))
               for triple in it.combinations(range(4), 3)):
            continue
        degrees = [sum(v in edge for edge in edges) for v in range(4)]
        assert degrees == [2, 2, 2, 2]
        retained.append(chosen)
    assert len(retained) == 3
    # Any triple of the four exact-label corners contains two corners sharing
    # a root-neighbour label. A triangle would give that adjacent pair both
    # the shared root neighbour and the third triangle corner, violating λ=1.
    corners = ((0, 2), (0, 3), (1, 2), (1, 3))
    assert all(any(set(a) & set(b) for a, b in it.combinations(triple, 2))
               for triple in it.combinations(corners, 3))
    return len(retained)


def check(entry, profile, stored):
    exceptional, c, k = build(entry, profile)
    pivot = (SUPPORTS.index((0, 3)), SUPPORTS.index((0, 4)))
    h = [[k[i][j] for j in pivot] for i in pivot]
    assert h == [[46, -23], [-23, 36]]
    determinant = h[0][0] * h[1][1] - h[0][1] * h[1][0]
    assert h[0][0] > 0 and determinant > 0
    inverse = [[F(h[1][1], determinant), F(-h[0][1], determinant)],
               [F(-h[1][0], determinant), F(h[0][0], determinant)]]
    coordinates = times(inverse, [k[i] for i in pivot])
    assert times([[row[i] for i in pivot] for row in k], coordinates) == k
    # The non-singular 2x2 principal submatrix and exact factorization prove
    # rank(K4)=2 and make each row uniquely determined by its pivot entries.
    all_patterns = []
    for source in range(21):
        domain = []
        for d_a, d_b in it.product(range(5), repeat=2):
            a, b = 4 * d_a - c[source][pivot[0]], 4 * d_b - c[source][pivot[1]]
            residual = [a * coordinates[0][i] + b * coordinates[1][i] for i in range(21)]
            if any(v.denominator != 1 for v in residual):
                continue
            degrees = [(v + c[source][i]) / 4 for i, v in enumerate(residual)]
            if any(v.denominator != 1 or not 0 <= v <= 4 for v in degrees) or sum(degrees) != 12:
                continue
            domain.append({"residual": list(map(int, residual)), "degrees": list(map(int, degrees)),
                           "a": a, "b": b, "Phi": b * (a + b)})
        all_patterns.append(domain)
    assert sum(map(len, all_patterns)) == stored["single_row_raw"] == 50
    labels = [(2 * a + p, 2 * b + q) for a, b in SUPPORTS for p, q in it.product((0, 1), repeat=2)]
    label_index = {label: i for i, label in enumerate(labels)}
    internal = [[0] * 4 for _ in range(21)]
    for left, right in entry["internal_edges"]:
        x, y = label_index[tuple(left)], label_index[tuple(right)]
        assert x // 4 == y // 4 and x // 4 in exceptional
        internal[x // 4][x % 4] += 1
        internal[y // 4][y % 4] += 1
    for source in range(21):
        if source not in exceptional:
            assert c[source][source] == 8
            internal[source] = [2] * 4
        assert sum(internal[source]) == c[source][source]
    values = []
    domain_counts = []
    for source, domain in enumerate(all_patterns):
        local_values, local_counts = [], []
        for required_degree in internal[source]:
            candidates = [r for r in domain if r["degrees"][source] == required_degree]
            observed = sorted({r["Phi"] for r in candidates})
            assert len(observed) == 1
            local_values.append(observed)
            local_counts.append(len(candidates))
        values.append(local_values)
        domain_counts.append(local_counts)
    scalar = stored["scalar_certificate"]
    assert values == scalar["raw_row_position_value_domains"]
    assert domain_counts == [row["candidate_rows_by_local"] for row in stored["fibre_records"]]
    assert values[pivot[0]] == [[-1], [3], [-1], [3]]
    assert all(v == [0] for source, fibre in enumerate(values) if source != pivot[0] for v in fibre)
    forced = sum(v[0] for fibre in values for v in fibre)
    required = 4 * (k[pivot[0]][pivot[1]] + k[pivot[1]][pivot[1]])
    assert forced == scalar["forced_total"] == 4
    assert required == scalar["Gram_required_total"] == 52
    assert forced != required
    assert not scalar["uses_projector_row_filters"] and not scalar["uses_quartet_PSD"] and not scalar["uses_fibre_zero_sum"]
    return {"key": list(key(entry)), "parameter": profile["parameter"],
            "coverage": int(entry["signature_orbit_labelled_coverage"]),
            "raw_degree_rows_checked": sum(map(len, all_patterns)),
            "exact_label_positions_checked": 84, "rank_K4": 2,
            "K4_principal_block": h, "pivot_supports": [[0, 3], [0, 4]],
            "forced_scalar_total": forced, "Gram_required_scalar_total": required,
            "contradiction": True, "row_norm_or_quartet_filter_used": False,
            "raw_domains_sha256": hashlib.sha256(json.dumps(all_patterns, sort_keys=True).encode()).hexdigest().upper()}


def main():
    ordinary_count = ordinary_degree_theorem()
    catalog, mining, kernel, probe = map(read, (CATALOG, MINING, KERNEL, PROBE))
    for path, wanted in probe["inputs_sha256"].items():
        assert sha(Path(path)) == wanted, path
    entries = {key(row): row for row in catalog["macro_entries"] if row["signature_stabilizer_canonical"]}
    profiles = {target: [row for row in mining["profile_rows"]["71"] if key(row) == target] for target in TARGETS}
    stored = {tuple(row["key"]): row for row in probe["rows"]}
    retained = {tuple(row["key"]): row for row in kernel["rows"]
                if row["macro_passes_some_full_Gram_profile_kernel_port_CSP"]}
    results = []
    for target in TARGETS:
        assert len(profiles[target]) == 1 and len(retained[target]["profiles"]) == 1
        assert retained[target]["profiles"][0]["passes_kernel_port_CSP"]
        row = check(entries[target], profiles[target][0], stored[target])
        assert row["coverage"] == retained[target]["coverage"] == profiles[target][0]["coverage"]
        results.append(row)
    coverage = sum(row["coverage"] for row in results)
    assert coverage == 786432
    result = {"status": "INDEPENDENT_E71_FIBRE_QUARTET_SOURCE694_SCALAR_AUDIT_PASS",
              "producer_imported": False,
              "inputs_sha256": {str(p): sha(p) for p in (CATALOG, MINING, KERNEL, PRODUCER, PROBE)},
              "ordinary_four_edge_triangle_free_graphs_checked": ordinary_count,
              "rows": results, "excluded_macros": 2, "excluded_labelled_coverage": coverage,
              "proof": "Every raw rank-two degree row matching the fixed internal degree has Phi(a,b)=b(a+b) fixed at its exact label. Summing these values gives4, whereas R^TR=4K4 requires52.",
              "scope": "Only (694,0,0) and (694,1,0). Each has one frozen full-Gram profile. No overlap/matching or local graph product is generated. The optional quartet/DP diagnostics are not needed or independently credited by this scalar audit.",
              "submission_txt_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
