"""Exact-label local neighbour subsets plus the residual degree-moment cone.

Each local test has root+14 neighbours+two known four-vertex fibres.
Only one inter-fibre adjacency row is assigned (16 choices).  Other cross
edges remain unknown; treating their pair cap as two is a safe relaxation.
No overlap product or local graph completion is enumerated.
"""

import argparse
from collections import Counter
import hashlib
import itertools as it
import json
from pathlib import Path
import time

import scratch_theory_e71_degree_moment_lp_probe as lp


OUTPUT = Path("scratch_theory_e71_label_subset_moment_probe.json")
INVENTORY = Path("scratch_root_e71_theory_frontier_before_label_subset.json")


def internal_blocks(entry):
    exceptional = {tuple(row["support"]) for row in entry["exceptional_supports"]}
    selected = {frozenset((tuple(a), tuple(b))) for a, b in entry["internal_edges"]}
    blocks = []
    for source, support in enumerate(lp.base.SUPPORTS):
        block = [[0] * 4 for _ in range(4)]
        for i, j in it.combinations(range(4), 2):
            a, b = lp.base.LABELS[4 * source + i], lp.base.LABELS[4 * source + j]
            present = frozenset((a, b)) in selected if support in exceptional else bool(set(a) & set(b))
            block[i][j] = block[j][i] = int(present)
        blocks.append(block)
    return blocks


def subset_domains(entry):
    blocks = internal_blocks(entry)
    allowed = [[None] * 21 for _ in range(84)]
    counters = Counter()
    pairs = tuple(it.combinations(range(23), 2))
    for source in range(21):
        for target in range(21):
            if source == target:
                for local in range(4):
                    row = sum(1 << j for j in range(4) if blocks[source][local][j])
                    allowed[4 * source + local][target] = (row,)
                continue
            graph = [0] * 23

            def add(a, b):
                graph[a] |= 1 << b
                graph[b] |= 1 << a

            for a in range(1, 15):
                add(0, a)
            for a in range(7):
                add(1 + 2 * a, 2 + 2 * a)
            for fibre, offset in ((source, 15), (target, 19)):
                for local in range(4):
                    for rootlabel in lp.base.LABELS[4 * fibre + local]:
                        add(offset + local, rootlabel + 1)
                for i, j in it.combinations(range(4), 2):
                    if blocks[fibre][i][j]:
                        add(offset + i, offset + j)
            assert all((graph[a] & graph[b]).bit_count() <= (1 if graph[a] >> b & 1 else 2)
                       for a, b in pairs)
            for local in range(4):
                x = 15 + local
                choices = []
                for bits in range(16):
                    trial = graph[:]
                    for j in range(4):
                        if bits >> j & 1:
                            trial[x] |= 1 << (19 + j)
                            trial[19 + j] |= 1 << x
                    counters["partial_23_vertex_rows_tested"] += 1
                    if all((trial[a] & trial[b]).bit_count() <= (1 if trial[a] >> b & 1 else 2)
                           for a, b in pairs):
                        choices.append(bits)
                assert choices and choices[0] == 0
                allowed[4 * source + local][target] = tuple(choices)
                counters["partial_rows_retained"] += len(choices)
    assert counters["partial_23_vertex_rows_tested"] == 26880
    return blocks, allowed, dict(counters)


def model(entry, profile, local_data):
    _, c, _, k4 = lp.base.compression(entry, profile)
    pivots, domains = lp.raw_domains(c, k4)
    blocks, subsets, counters = local_data
    allowed_degrees = [[{bits.bit_count() for bits in row} for row in target] for target in subsets]
    pairs = tuple(it.combinations_with_replacement(range(len(pivots)), 2))
    columns, variables = [], []
    raw_position_count = retained_count = 0
    domains_by_position = []
    for x in range(84):
        source, local = divmod(x, 4)
        assert sum(map(sum, blocks[source])) == c[source][source]
        choices = []
        for row in domains[source]:
            if row["degree"][source] != sum(blocks[source][local]):
                continue
            raw_position_count += 1
            if any(degree not in allowed_degrees[x][target] for target, degree in enumerate(row["degree"])):
                continue
            retained_count += 1
            v = row["pivot"]
            choices.append(list(v))
            column = [int(i == x) for i in range(84)]
            column += [v[j] if fibre == source else 0
                       for fibre in range(21) for j in range(len(pivots))]
            column += [v[i] * v[j] for i, j in pairs]
            columns.append(column)
            variables.append({"position": x, "pivot": list(v)})
        domains_by_position.append(choices)
    assert columns
    matrix = list(map(list, zip(*columns)))
    target = [1] * 84 + [0] * (21 * len(pivots))
    target += [4 * k4[pivots[i]][pivots[j]] for i, j in pairs]
    return matrix, target, {
        "rank_K4": len(pivots), "pivot_supports": [list(lp.base.SUPPORTS[i]) for i in pivots],
        "raw_row_patterns": sum(map(len, domains)),
        "raw_internal_degree_position_rows": raw_position_count,
        "retained_position_rows": retained_count,
        "empty_positions": [i for i, row in enumerate(domains_by_position) if not row],
        "domains_by_position": domains_by_position, "variables": variables,
        "matrix_sha256": hashlib.sha256(json.dumps([matrix, target], separators=(",", ":")).encode()).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-remaining", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    started = time.monotonic()
    catalog, mining, inventory = map(lp.base.read, (lp.base.CATALOG, lp.base.MINING, INVENTORY))
    entries = {lp.base.key(row): row for row in catalog["macro_entries"] if row["signature_stabilizer_canonical"]}
    selected = {tuple(row) for row in inventory["remaining_keys"]} if args.all_remaining else {
        (170, 0, 0), (724, 1, 0), (2378, 1, 0)}
    profiles = [row for row in mining["profile_rows"]["71"] if lp.base.key(row) in selected]
    cache, records, local_records = {}, [], []
    for profile in profiles:
        key = lp.base.key(profile)
        if key not in cache:
            cache[key] = subset_domains(entries[key])
            local_records.append({"key": list(key), "allowed_subsets": cache[key][1], "counts": cache[key][2]})
        matrix, target, metadata = model(entries[key], profile, cache[key])
        answer = lp.linprog(lp.np.zeros(len(matrix[0])), A_eq=lp.np.asarray(matrix, dtype=float),
                            b_eq=lp.np.asarray(target, dtype=float), bounds=(0, None), method="highs")
        certificate = lp.farkas(matrix, target) if answer.status == 2 else None
        row = {"key": list(key), "parameter": profile["parameter"], "coverage": profile["coverage"],
               "LP_status": int(answer.status), "exact_integer_certificate": certificate,
               "model": metadata}
        records.append(row)
        print(json.dumps({"key": row["key"], "parameter": row["parameter"],
                          "raw_position_rows": metadata["raw_internal_degree_position_rows"],
                          "retained_position_rows": metadata["retained_position_rows"],
                          "empty_positions": metadata["empty_positions"],
                          "exact_infeasible": certificate is not None}), flush=True)
    result = {
        "status": "E71_EXACT_LABEL_SUBSET_MOMENT_PROBE_COMPLETE",
        "all_remaining_requested": args.all_remaining,
        "inputs_sha256": {str(p): lp.base.sha(p) for p in (lp.base.CATALOG, lp.base.MINING, INVENTORY, Path(lp.__file__))},
        "profiles": records, "local_models": local_records,
        "profiles_tested": len(records), "macros_tested": len(cache),
        "exact_infeasible_profiles": sum(row["exact_integer_certificate"] is not None for row in records),
        "full_local_completions_enumerated": 0,
        "requires_independent_audit_before_inventory_credit": True,
        "pointwise_E0_lower_bound": None,
        "elapsed_seconds": time.monotonic() - started,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in ("profiles", "local_models")}), flush=True)


if __name__ == "__main__":
    main()
