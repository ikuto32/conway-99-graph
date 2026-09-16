"""Independent exact replay of the frozen E71 single-row frontier filters.

No research producer is imported.  This checker reconstructs compression
matrices and every integral row from the frozen catalog/profile JSON.  It
uses RREF row coordinates, an exact inverse on principal range coordinates,
and a degree-indexed dynamic program for the residual-projector intervals.
It does not generate overlap completions, local graphs, or order-eight types.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction as F
import hashlib
import itertools as it
import json
import math
from pathlib import Path
import time


PREFIX = "scratch_theory_e71_projector_transport_frontier"
PRODUCER = Path(PREFIX + ".py")
CERTIFICATE = Path(PREFIX + ".json")
OUTPUT = Path(PREFIX + "_audit.json")
CATALOG = Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json")
MINING = Path("scratch_theory_e71_e72_e0_moment_mining.json")
KERNEL = Path("scratch_theory_e71_equitable_kernel_port_census.json")
KERNEL_AUDIT = Path("scratch_theory_e71_equitable_kernel_port_census_audit.json")
SOURCE724 = Path("scratch_theory_e71_source724_multiblock_transport_audit.json")
SUPPORTS = tuple(it.combinations(range(7), 2))
LABELS = tuple((2 * a + p, 2 * b + q)
               for a, b in SUPPORTS for p, q in it.product((0, 1), repeat=2))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def key(row):
    return tuple(int(row[name]) for name in (
        "source_row_index", "state_orbit_number", "signature_stabilizer_orbit_number"))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def multiply(a, b):
    cols = tuple(zip(*b))
    return [[dot(row, col) for col in cols] for row in a]


def reduced(matrix):
    a = [list(map(F, row)) for row in matrix]
    pivots = []
    for col in range(len(a[0])):
        p = next((i for i in range(len(pivots), len(a)) if a[i][col]), None)
        if p is None:
            continue
        row = len(pivots)
        a[row], a[p] = a[p], a[row]
        scale = a[row][col]
        a[row] = [v / scale for v in a[row]]
        for i in range(len(a)):
            if i != row and a[i][col]:
                factor = a[i][col]
                a[i] = [u - factor * v for u, v in zip(a[i], a[row])]
        pivots.append(col)
        if len(pivots) == len(a):
            break
    return a[:len(pivots)], tuple(pivots)


def inverse(matrix):
    n = len(matrix)
    a = [list(map(F, row)) + [F(i == j) for j in range(n)]
         for i, row in enumerate(matrix)]
    r, pivots = reduced(a)
    assert pivots == tuple(range(n))
    return [row[n:] for row in r]


def range_form(matrix):
    """A generalized-inverse quadratic form, with PSD and range checks."""
    basis, pivots = reduced(matrix)
    minor = [[matrix[i][j] for j in pivots] for i in pivots]
    # Exact Schur-complement LDL certificate: all principal pivots positive.
    work = [list(map(F, row)) for row in minor]
    for i in range(len(work)):
        assert work[i][i] > 0
        for j in range(i + 1, len(work)):
            for k in range(i + 1, len(work)):
                work[j][k] -= work[j][i] * work[i][k] / work[i][i]
    inv = inverse(minor)
    assert multiply(minor, basis) == [list(map(F, matrix[i])) for i in pivots]
    assert multiply([[row[i] for i in pivots] for row in matrix], basis) == matrix

    def coordinates(vector):
        values = tuple(vector[i] for i in pivots)
        assert [dot(values, col) for col in zip(*basis)] == list(vector)
        return values, tuple(dot(row, values) for row in inv)

    return pivots, coordinates


def geometry_audit():
    h = []
    pure4 = []
    relation_counts = [[None] * 21 for _ in range(21)]
    for x, left in enumerate(LABELS):
        hr, er = [], []
        for y, right in enumerate(LABELS):
            q = len(set(left) & set(right))
            d = sum((v ^ 1) in right for v in left)
            hv = 100 if x == y else 2 - 11 * q - d
            ev = 40 if x == y else 4 - 6 * q - 2 * d
            assert 2 * (3 * hv + 12 * (2 - q - d)) == 15 * ev
            hr.append(hv)
            er.append(ev)
        h.append(hr)
        pure4.append(er)
    assert multiply(h, h) == [[120 * v for v in row] for row in h]
    assert sum(h[i][i] for i in range(84)) == 70 * 120
    for source in range(21):
        for target in range(21):
            histograms = []
            for local in range(4):
                x = 4 * source + local
                values = [pure4[x][4 * target + pos] for pos in range(4)
                          if 4 * target + pos != x]
                histograms.append(tuple(sorted(Counter(values).items())))
                c0 = 8 if source == target else (
                    0 if set(SUPPORTS[source]) & set(SUPPORTS[target]) else 4)
                assert sum(pure4[x][4 * target + pos] for pos in range(4)) == 4 * c0
            assert len(set(histograms)) == 1
            relation_counts[source][target] = histograms[0]
    # Coarse unsigned-incidence kernel projector, built from the 7x7 Gram.
    incidence = [[int(v in support) for support in SUPPORTS] for v in range(7)]
    inc_gram = multiply(incidence, list(zip(*incidence)))
    assert inc_gram == [[5 * int(i == j) + 1 for j in range(7)] for i in range(7)]
    orthogonal = multiply(multiply(list(zip(*incidence)), inverse(inc_gram)), incidence)
    cycle = [[F(i == j) - orthogonal[i][j] for j in range(21)] for i in range(21)]
    assert multiply(cycle, cycle) == cycle
    assert sum(cycle[i][i] for i in range(21)) == 14
    return relation_counts, cycle


def compression(entry, profile):
    exceptional = tuple(tuple(row["support"]) for row in entry["exceptional_supports"])
    indexes = tuple(SUPPORTS.index(support) for support in exceptional)
    c0 = [[8 if i == j else (0 if set(a) & set(b) else 4)
           for j, b in enumerate(SUPPORTS)] for i, a in enumerate(SUPPORTS)]
    c = [row[:] for row in c0]
    for index, record in zip(indexes, entry["exceptional_supports"]):
        c[index][index] -= 2 * int(record["deficit"])
    for records in (entry["overlap_block_totals"], profile["disjoint_D"]):
        for local_a, local_b, value in records:
            a, b = indexes[local_a], indexes[local_b]
            c[a][b] = c[b][a] = int(value)
    assert all(sum(row) == 48 for row in c)
    z = [[c0[i][j] - c[i][j] for j in range(21)] for i in range(21)]
    z2, c2 = multiply(z, z), multiply(c, c)
    k4 = [[28 * z[i][j] - z2[i][j] for j in range(21)] for i in range(21)]
    assert k4 == [[192 * int(i == j) + 128 - 4 * c[i][j]
                   - 32 * len(set(SUPPORTS[i]) & set(SUPPORTS[j])) - c2[i][j]
                   for j in range(21)] for i in range(21)]
    assert all(k4[i][j] == 0 for i in range(21) for j in range(21)
               if i not in indexes or j not in indexes)
    return indexes, c, z, k4


def domains_from_rref(indexes, c, z, k4, cycle):
    basis, pivots = reduced([[k4[i][j] for j in indexes] for i in indexes])
    assert len(pivots) == len(reduced(k4)[1])
    global_pivots = tuple(indexes[i] for i in pivots)
    zp, z_coords = range_form(z)
    d = [[28 * cycle[i][j] - z[i][j] for j in range(21)] for i in range(21)]
    dp, d_coords = range_form(d)
    range_form(k4)
    patterns, domains = [], []
    stats = Counter()
    max_minus = max_plus = F(0)
    for source in range(21):
        ids = []
        for pivot_degrees in it.product(range(5), repeat=len(pivots)):
            residual_values = tuple(4 * degree - c[source][target]
                                    for degree, target in zip(pivot_degrees, global_pivots))
            rr = [dot(residual_values, col) for col in zip(*basis)]
            if any(value.denominator != 1 for value in rr):
                continue
            residual = [0] * 21
            for target, value in zip(indexes, rr):
                residual[target] = int(value)
            numerators = [value + base for value, base in zip(residual, c[source])]
            if any(value % 4 or not 0 <= value <= 16 for value in numerators):
                continue
            degrees = tuple(value // 4 for value in numerators)
            if sum(degrees) != 12:
                continue
            s = tuple(z[source][i] - residual[i] for i in range(21))
            t = tuple(d[source][i] + residual[i] for i in range(21))
            sp, sc = z_coords(s)
            tp, tc = d_coords(t)
            minus, plus = dot(sp, sc), dot(tp, tc)
            stats["minus4_leverage_rejected"] += int(minus > 40)
            stats["plus3_leverage_rejected"] += int(plus > F(160, 3))
            max_minus, max_plus = max(max_minus, minus), max(max_plus, plus)
            uid = len(patterns)
            patterns.append({"uid": uid, "source": source, "index": len(ids),
                             "r": tuple(residual), "pivot": residual_values,
                             "degree": degrees, "sp": sp, "sc": sc,
                             "g": 40 - minus, "leverage_ok": minus <= 40 and plus <= F(160, 3)})
            ids.append(uid)
        assert len({patterns[i]["r"] for i in ids}) == len(ids)
        domains.append(tuple(ids))
    scale = math.lcm(*(value.denominator for pattern in patterns for value in pattern["sc"]))
    for pattern in patterns:
        pattern["sc_int"] = tuple(int(value * scale) for value in pattern["sc"])
        pattern["g_int"] = int(pattern["g"] * scale)
        assert pattern["g_int"] == pattern["g"] * scale
    forms = [[dot(p["sp"], q["sc_int"]) for q in patterns] for p in patterns]
    assert forms == list(map(list, zip(*forms)))
    stats["Z_rank"] = len(zp)
    stats["raw_row_patterns"] = len(patterns)
    stats["maximum_minus4_leverage"] = int(max_minus) if max_minus.denominator == 1 else str(max_minus)
    stats["maximum_plus3_leverage"] = int(max_plus) if max_plus.denominator == 1 else str(max_plus)
    return patterns, domains, forms, global_pivots, scale, dict(stats)


def zero_sum_failures(patterns, domains, active):
    failures = []
    for source, domain in enumerate(domains):
        residuals = [patterns[i]["r"] for i in domain if i in active]
        pair_sums = {tuple(a + b for a, b in zip(x, y))
                     for x, y in it.combinations_with_replacement(residuals, 2)}
        if not any(tuple(-v for v in row) in pair_sums for row in pair_sums):
            failures.append(list(SUPPORTS[source]))
    return failures


def transport(c, k4, patterns, domains, active, pivots, separators):
    dimension = len(pivots)
    directions = tuple(values for values in it.product((-1, 0, 1), repeat=dimension)
                       if any(values) and next(v for v in values if v) > 0)
    rounds = []
    while all(any(i in active for i in domain) for domain in domains):
        extrema = []
        for domain in domains:
            vectors = [patterns[i]["pivot"] for i in domain if i in active]
            extrema.append([(min(dot(d, v) for v in vectors), max(dot(d, v) for v in vectors))
                            for d in directions])
        rejected = []
        for uid in sorted(active):
            pattern = patterns[uid]
            source = pattern["source"]
            rhs = [k4[source][p] - sum(pattern["r"][i] * (c[i][p] + 4 * int(i == p))
                                      for i in range(21)) for p in pivots]
            separator = None
            if any(value % 4 for value in rhs):
                separator = {"kind": "nonintegral_rhs", "rhs": rhs}
            else:
                target = tuple(v // 4 for v in rhs)
                for j, direction in enumerate(directions):
                    wanted = dot(direction, target)
                    low = sum(pattern["degree"][i] * extrema[i][j][0] for i in range(21))
                    high = sum(pattern["degree"][i] * extrema[i][j][1] for i in range(21))
                    if not low <= wanted <= high:
                        separator = {"kind": "support_interval", "direction": list(direction),
                                     "target": wanted, "interval": [low, high]}
                        break
            if separator is not None:
                rejected.append(uid)
                separators[uid] = {"source_support": list(SUPPORTS[source]),
                                   "pattern_index": pattern["index"], **separator}
        if not rejected:
            break
        rounds.append(len(rejected))
        active.difference_update(rejected)
    return len(directions), rounds


def rownorm(patterns, domains, active, forms, scale, relations, pair_minors):
    removed = 0
    first = None
    while all(any(i in active for i in domain) for domain in domains):
        rejected = []
        for uid in sorted(active):
            p = patterns[uid]
            lower = upper = 0
            feasible = True
            for target, domain in enumerate(domains):
                options = []
                for base, multiplicity in relations[p["source"]][target]:
                    endpoints = []
                    for edge in (0, 1):
                        values = []
                        for other in domain:
                            if other not in active:
                                continue
                            numerator = (base - 16 * edge) * scale - forms[uid][other]
                            square = numerator * numerator
                            if pair_minors and square > p["g_int"] * patterns[other]["g_int"]:
                                continue
                            values.append(square)
                        endpoints.append(None if not values else (min(values), max(values)))
                    options.extend([endpoints] * multiplicity)
                # Min/max dynamic programming over exactly the prescribed degree.
                frontier = {0: (0, 0)}
                for endpoints in options:
                    nxt = {}
                    for degree, (lo, hi) in frontier.items():
                        for edge, bound in enumerate(endpoints):
                            if bound is None:
                                continue
                            total = degree + edge
                            a, b = lo + bound[0], hi + bound[1]
                            if total in nxt:
                                a, b = min(a, nxt[total][0]), max(b, nxt[total][1])
                            nxt[total] = (a, b)
                    frontier = nxt
                bound = frontier.get(p["degree"][target])
                if bound is None:
                    feasible = False
                    break
                lower += bound[0]
                upper += bound[1]
            wanted = 112 * p["g_int"] * scale - p["g_int"] ** 2
            if not feasible or not lower <= wanted <= upper:
                rejected.append(uid)
                if first is None:
                    first = {"source_support": list(SUPPORTS[p["source"]]),
                             "pattern_index": p["index"], "source_local": 0,
                             "target_scaled_by_Z_denominator_squared": wanted,
                             "interval": [lower, upper] if feasible else None,
                             "Z_form_denominator": scale, "pair_minors_used": pair_minors}
        if not rejected:
            break
        removed += len(rejected)
        active.difference_update(rejected)
    return removed, first


def replay(entry, profile, relations, cycle):
    indexes, c, z, k4 = compression(entry, profile)
    patterns, domains, forms, pivots, scale, summary = domains_from_rref(indexes, c, z, k4, cycle)
    active = {p["uid"] for p in patterns if p["leverage_ok"]}
    summary["patterns_after_leverage"] = len(active)
    summary["leverage_zero_sum_empty_fibres"] = zero_sum_failures(patterns, domains, active)
    iterations, separators = [], {}
    for pair_minors in (False, True):
        count = 0
        first = None
        while True:
            num_directions, rounds = transport(c, k4, patterns, domains, active, pivots, separators)
            iterations.extend(rounds)
            removed, witness = rownorm(patterns, domains, active, forms, scale, relations, pair_minors)
            count += removed
            if first is None:
                first = witness
            if not rounds and not removed:
                break
        name = "pair" if pair_minors else "unfiltered"
        summary[f"rownorm_{name}_rejected"] = count
        summary[f"rownorm_{name}_removed_local_assignments"] = 4 * count
        summary[f"first_rownorm_{name}_separator"] = first
        if not pair_minors:
            summary["patterns_after_rownorm_unfiltered"] = len(active)
    summary.update({
        "parameter": profile["parameter"], "transport_directions": num_directions,
        "transport_iterations": iterations, "transport_rejected": sum(iterations),
        "patterns_after_transport": len(active),
        "transport_empty_fibres": [list(SUPPORTS[i]) for i, domain in enumerate(domains)
                                   if not any(uid in active for uid in domain)],
        "transport_zero_sum_empty_fibres": zero_sum_failures(patterns, domains, active),
        "first_transport_separator": separators[min(separators)] if separators else None,
    })
    summary["profile_rejected_by_row_domain"] = bool(
        summary["leverage_zero_sum_empty_fibres"] or summary["transport_zero_sum_empty_fibres"])
    digest = hashlib.sha256(json.dumps([
        {"source": p["source"], "residual": p["r"], "degrees": p["degree"]}
        for p in patterns if p["uid"] in active], separators=(",", ":")).encode()).hexdigest().upper()
    return summary, digest


def main():
    started = time.monotonic()
    certificate, catalog, mining, kernel, prior, ka = map(read, (
        CERTIFICATE, CATALOG, MINING, KERNEL, SOURCE724, KERNEL_AUDIT))
    assert certificate["status"] == "EXACT_E71_PROJECTOR_TRANSPORT_FRONTIER_COMPLETE"
    for path, wanted in certificate["inputs_sha256"].items():
        assert sha(Path(path)) == wanted, path
    assert prior["status"] == "INDEPENDENT_SOURCE724_MULTIBLOCK_TRANSPORT_AUDIT_PASS"
    for path, wanted in prior["inputs_sha256"].items():
        assert sha(Path(path)) == wanted, path
    assert ka["status"] == "INDEPENDENT_E71_KERNEL_PORT_CENSUS_MANIFEST_AUDIT_PASS"
    for path, wanted in ka["inputs"].items():
        assert sha(Path(path)) == wanted, path
    entries = {key(row): row for row in catalog["macro_entries"] if row["signature_stabilizer_canonical"]}
    profiles = {(key(row), row["parameter"]): row for row in mining["profile_rows"]["71"]}
    retained = {tuple(row["key"]): row for row in kernel["rows"]
                if row["macro_passes_some_full_Gram_profile_kernel_port_CSP"]}
    stored = {tuple(row["key"]): row for row in certificate["rows"]}
    assert len(stored) == len(certificate["rows"]) == len(retained) == 132
    assert stored.keys() == retained.keys()
    relations, cycle = geometry_audit()
    verified = []
    counters = Counter()
    for position, (macro_key, record) in enumerate(stored.items(), 1):
        entry, source = entries[macro_key], retained[macro_key]
        assert record["coverage"] == source["coverage"] == int(entry["signature_orbit_labelled_coverage"])
        assert record["Q"] == source["Q"] == int(entry["Q"])
        parameters = [p["parameter"] for p in source["profiles"] if p["passes_kernel_port_CSP"]]
        assert len(set(parameters)) == len(parameters)
        assert sorted(parameters) == sorted(p["parameter"] for p in record["profiles"])
        for p in record["profiles"]:
            replayed, digest = replay(entry, profiles[(macro_key, p["parameter"])], relations, cycle)
            assert replayed == p, (macro_key, p["parameter"], {
                name: (p.get(name), replayed.get(name)) for name in p.keys() | replayed.keys()
                if p.get(name) != replayed.get(name)})
            verified.append({"key": list(macro_key), "parameter": p["parameter"],
                             "final_row_domain_sha256": digest, "replayed": True})
            counters["profiles_tested"] += 1
            counters["raw_row_patterns"] += p["raw_row_patterns"]
            for old, new in (
                ("minus4_leverage_rejected", "minus4_leverage_rejected_patterns"),
                ("plus3_leverage_rejected", "plus3_leverage_rejected_patterns"),
                ("transport_rejected", "transport_rejected_patterns"),
                ("rownorm_unfiltered_rejected", "rownorm_unfiltered_rejected_patterns"),
                ("rownorm_unfiltered_removed_local_assignments", "rownorm_unfiltered_removed_local_assignments"),
                ("rownorm_pair_rejected", "rownorm_pair_rejected_patterns"),
                ("rownorm_pair_removed_local_assignments", "rownorm_pair_removed_local_assignments"),
                ("profile_rejected_by_row_domain", "profiles_rejected_by_row_domain"),
            ):
                counters[new] += int(p[old])
        row_rejected = bool(record["profiles"]) and all(p["profile_rejected_by_row_domain"] for p in record["profiles"])
        prior_rejected = macro_key == (724, 1, 0)
        assert record["row_domain_rejected"] == row_rejected
        assert record["source724_exact_exclusion"] == prior_rejected
        assert record["excluded_by_union"] == (row_rejected or prior_rejected)
        counters["macros_tested"] += 1
        counters["coverage_tested"] += record["coverage"]
        for prefix, flag in (("row_domain_rejected", row_rejected), ("source724_exact", prior_rejected)):
            counters[prefix + "_macros"] += int(flag)
            counters[prefix + "_coverage"] += record["coverage"] * int(flag)
        counters["excluded_macros_union"] += int(row_rejected or prior_rejected)
        counters["excluded_coverage_union"] += record["coverage"] * int(row_rejected or prior_rejected)
        if position % 10 == 0:
            print(json.dumps({"macros_replayed": position, "profiles_replayed": len(verified),
                              "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
    assert dict(counters) == certificate["summary"]
    assert certificate["submission_txt_written"] is False
    result = {
        "status": "INDEPENDENT_E71_PROJECTOR_TRANSPORT_FRONTIER_AUDIT_PASS",
        "producer_imported": False,
        "inputs_sha256": {str(p): sha(p) for p in (
            PRODUCER, CERTIFICATE, CATALOG, MINING, KERNEL, KERNEL_AUDIT, SOURCE724)},
        "verified_summary": dict(counters),
        "geometry": {"labelled_positions_checked": 84, "ordered_fibre_pairs_checked": 441,
                     "local_positions_per_fibre_checked": 4,
                     "cycle_projector_idempotence": True, "corrected_s_equals_Z_row_minus_R": True},
        "replay": {"all_profile_fields_equal": True, "rational_arithmetic": True,
                   "row_domains_reconstructed_without_producer": True,
                   "single_row_repetition_relaxation": True,
                   "all_local_positions_equivalent_by_verified_relation_multisets": True},
        "dependencies": "Kernel-port-passing frontier is frozen input, not a re-proof of its earlier CSP exclusions. Source724 exclusion is inherited only after rechecking all recorded input hashes.",
        "claim_boundary": "No new macro is excluded. The 140 relaxed profiles all survive; only the previously audited (724,1,0) exclusion is carried into the union. No E71-wide exclusion or positive E0 lower bound follows.",
        "profiles": verified,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "submission_txt_written": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": dict(counters),
                      "elapsed_seconds": result["elapsed_seconds"]}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
