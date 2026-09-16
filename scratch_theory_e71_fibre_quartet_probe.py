"""Small degree-row quartet probe, not an E71 local-completion census."""

from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

import scratch_theory_e71_projector_transport_frontier_audit as rows


OUTPUT = Path("scratch_theory_e71_fibre_quartet_probe.json")
TARGETS = ((694, 0, 0), (694, 1, 0))


def determinant(matrix):
    if not matrix:
        return 1
    if len(matrix) == 1:
        return matrix[0][0]
    return sum((-1) ** j * matrix[0][j] * determinant([
        row[:j] + row[j + 1:] for row in matrix[1:]]) for j in range(len(matrix)))


def psd_minor(matrix):
    for size in range(1, len(matrix) + 1):
        for subset in itertools.combinations(range(len(matrix)), size):
            value = determinant([[matrix[i][j] for j in subset] for i in subset])
            if value < 0:
                return False, {"indices": list(subset), "determinant": int(value)}
    return True, None


def gram(rows4):
    return tuple(sum(row[i] * row[j] for row in rows4)
                 for i in range(len(rows4[0])) for j in range(i, len(rows4[0])))


def unpack(values, dimension):
    matrix = [[0] * dimension for _ in range(dimension)]
    for value, (i, j) in zip(values, itertools.combinations_with_replacement(range(dimension), 2)):
        matrix[i][j] = matrix[j][i] = value
    return matrix


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def single_row_frontier(entry, profile, relations, cycle):
    indexes, c, z, k4 = rows.compression(entry, profile)
    patterns, domains, forms, pivots, scale, stats = rows.domains_from_rref(indexes, c, z, k4, cycle)
    active = {p["uid"] for p in patterns if p["leverage_ok"]}
    separators = {}
    for pair in (False, True):
        while True:
            _, rounds = rows.transport(c, k4, patterns, domains, active, pivots, separators)
            removed, _ = rows.rownorm(patterns, domains, active, forms, scale, relations, pair)
            if not rounds and not removed:
                break
    return indexes, c, z, k4, patterns, domains, forms, pivots, scale, active, stats


def adjacency_blocks(entry):
    known = {frozenset((tuple(left), tuple(right))) for left, right in entry["internal_edges"]}
    exceptional = {tuple(item["support"]) for item in entry["exceptional_supports"]}
    blocks = []
    for source, support in enumerate(rows.SUPPORTS):
        block = [[0] * 4 for _ in range(4)]
        for i, j in itertools.combinations(range(4), 2):
            left, right = rows.LABELS[4 * source + i], rows.LABELS[4 * source + j]
            if support in exceptional:
                edge = frozenset((left, right)) in known
            else:
                # The ordinary fibre has four edges. Its two nonedges must be
                # diagonals: a nonedge sharing an exact label would have the
                # two internal C4 common neighbours plus that root neighbour.
                edge = len(set(left) & set(right)) == 1
            block[i][j] = block[j][i] = int(edge)
        blocks.append(block)
    return blocks


def probe(entry, profile, relations, cycle):
    indexes, c, z, k4, patterns, domains, forms, pivots, scale, active, stats = single_row_frontier(entry, profile, relations, cycle)
    dimension = len(pivots)
    target = tuple(4 * k4[i][j] for i, j in itertools.combinations_with_replacement(pivots, 2))
    blocks = adjacency_blocks(entry)
    all_quartets = []
    records = []
    scalar_position_domains = []
    for source, block in enumerate(blocks):
        assert sum(map(sum, block)) == c[source][source]
        candidate_ids = [tuple(uid for uid in domains[source] if uid in active
                               and patterns[uid]["degree"][source] == sum(block[local]))
                         for local in range(4)]
        raw_candidate_ids = [tuple(uid for uid in domains[source]
                                   if patterns[uid]["degree"][source] == sum(block[local]))
                             for local in range(4)]
        assert raw_candidate_ids == candidate_ids
        scalar_position_domains.append([
            sorted({patterns[uid]["pivot"][1] * sum(patterns[uid]["pivot"])
                    for uid in domain}) for domain in raw_candidate_ids])
        right_pairs = defaultdict(list)
        for a, b in itertools.product(candidate_ids[2], candidate_ids[3]):
            right_pairs[add(patterns[a]["r"], patterns[b]["r"])].append((a, b))
        quartets = []
        counts = Counter()
        for a, b in itertools.product(candidate_ids[0], candidate_ids[1]):
            wanted = tuple(-v for v in add(patterns[a]["r"], patterns[b]["r"]))
            for cc, dd in right_pairs[wanted]:
                chosen = (a, b, cc, dd)
                counts["zero_sum_internal_degree_quartets"] += 1
                gp = gram([patterns[uid]["pivot"] for uid in chosen])
                budget_ok, budget_minor = psd_minor(unpack(subtract(target, gp), dimension))
                g4 = []
                for i, uid in enumerate(chosen):
                    row = []
                    for j, vid in enumerate(chosen):
                        if i == j:
                            value = patterns[uid]["g_int"]
                        else:
                            x, y = rows.LABELS[4 * source + i], rows.LABELS[4 * source + j]
                            q = len(set(x) & set(y))
                            d = sum((v ^ 1) in y for v in x)
                            value = (4 - 6 * q - 2 * d - 16 * block[i][j]) * scale - forms[uid][vid]
                        row.append(value)
                    g4.append(row)
                assert all(sum(row) == 0 for row in g4)
                quartet_ok, minor = psd_minor(g4)
                counts["Gram_budget_pass"] += int(budget_ok)
                counts["projector_quartet_pass"] += int(quartet_ok)
                counts["both_pass"] += int(budget_ok and quartet_ok)
                counts["Gram_budget_pass_projector_fail"] += int(budget_ok and not quartet_ok)
                quartets.append({"selected_pattern_indices": [patterns[i]["index"] for i in chosen],
                                 "selected_uids": list(chosen), "pivot_gram": list(gp),
                                 "Gram_budget_pass": budget_ok, "projector_quartet_pass": quartet_ok,
                                 "projector_negative_minor": minor,
                                 "scaled_G4_fibre": g4})
        all_quartets.append(quartets)
        records.append({"support": list(rows.SUPPORTS[source]), "counts": dict(counts),
                        "candidate_rows_by_local": list(map(len, candidate_ids)),
                        "distinct_Gram_contributions": len({tuple(q["pivot_gram"]) for q in quartets}),
                        "quartets": quartets})

    # Matrix-moment feasibility only: retain one representative per partial
    # pivot Gram sum. No matching, overlap, or binary-block completion is made.
    layers = [{(0,) * len(target): None}]
    for fibre in all_quartets:
        contributions = {}
        for q in fibre:
            if q["Gram_budget_pass"]:
                contributions.setdefault(tuple(q["pivot_gram"]), q)
        next_layer = {}
        for partial in layers[-1]:
            for contribution, q in contributions.items():
                updated = add(partial, contribution)
                if updated in next_layer:
                    continue
                if psd_minor(unpack(subtract(target, updated), dimension))[0]:
                    next_layer[updated] = (partial, q)
        assert len(next_layer) <= 200000, "bounded moment DP exceeded cap"
        layers.append(next_layer)
    global_gram = target in layers[-1]
    chosen_global = []
    if global_gram:
        remaining = target
        for index in reversed(range(21)):
            previous, q = layers[index + 1][remaining]
            chosen_global.append(q)
            remaining = previous
        chosen_global.reverse()
    # A bad quartet with an identical Gram contribution may replace a
    # witnessed fibre without changing any full 21-coordinate Gram entry.
    counterexample = None
    if global_gram:
        for source, chosen in enumerate(chosen_global):
            bad = next((q for q in all_quartets[source]
                        if q["pivot_gram"] == chosen["pivot_gram"] and not q["projector_quartet_pass"]), None)
            if bad is not None:
                modified = [bad if i == source else q for i, q in enumerate(chosen_global)]
                residual = [patterns[uid]["r"] for q in modified for uid in q["selected_uids"]]
                assert rows.multiply(list(zip(*residual)), residual) == [[4 * v for v in row] for row in k4]
                counterexample = {"failed_fibre": list(rows.SUPPORTS[source]),
                                  "all_fibre_pattern_indices": [q["selected_pattern_indices"] for q in modified],
                                  "full_RtR_equals_4K4": True, "negative_minor": bad["projector_negative_minor"],
                                  "scaled_G4_fibre": bad["scaled_G4_fibre"], "scale": scale}
                break
    return {"key": list(rows.key(entry)), "parameter": profile["parameter"],
            "single_row_raw": stats["raw_row_patterns"], "single_row_final": len(active),
            "pivot_supports": [list(rows.SUPPORTS[i]) for i in pivots],
            "target_pivot_gram": list(target), "Z_form_denominator": scale,
            "fibre_records": records,
            "matrix_Gram_DP_states_by_depth": list(map(len, layers)),
            "matrix_Gram_feasible": global_gram,
            "raw_internal_degree_domains_equal_filtered_domains": True,
            "scalar_certificate": {
                "form": "Phi(a,b)=a*b+b*b, a=R_(0,3), b=R_(0,4)",
                "raw_row_position_value_domains": scalar_position_domains,
                "every_domain_singleton": all(len(v) == 1 for f in scalar_position_domains for v in f),
                "forced_total": sum(v[0] for f in scalar_position_domains for v in f),
                "Gram_required_total": target[1] + target[2],
                "uses_projector_row_filters": False,
                "uses_quartet_PSD": False,
                "uses_fibre_zero_sum": False},
            "counterexample_to_implication_from_full_Gram": counterexample,
            "fibres_with_no_projector_quartet": [r["support"] for r in records if not r["counts"].get("projector_quartet_pass", 0)]}


def main():
    catalog, mining = rows.read(rows.CATALOG), rows.read(rows.MINING)
    relations, cycle = rows.geometry_audit()
    entries = {rows.key(r): r for r in catalog["macro_entries"] if r["signature_stabilizer_canonical"]}
    profiles = {rows.key(r): r for r in mining["profile_rows"]["71"] if rows.key(r) in TARGETS}
    results = [probe(entries[key], profiles[key], relations, cycle) for key in TARGETS]
    result = {"status": "E71_FIBRE_QUARTET_SMALL_PROBE_COMPLETE",
              "inputs_sha256": {str(p): rows.sha(p) for p in (rows.CATALOG, rows.MINING, Path(rows.__file__))},
              "scope": "Two source694 macros only. Independent per-fibre quartets and compressed matrix-moment DP; no local graph completion or E71 census.",
              "rows": results, "submission_txt_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "rows": [{
        "key": r["key"], "matrix_Gram_feasible": r["matrix_Gram_feasible"],
        "new_quartet_constraint_not_implied_by_full_Gram": r["counterexample_to_implication_from_full_Gram"] is not None,
        "empty_fibres": r["fibres_with_no_projector_quartet"],
        "max_DP_states": max(r["matrix_Gram_DP_states_by_depth"])} for r in results]}, sort_keys=True))


if __name__ == "__main__":
    main()
