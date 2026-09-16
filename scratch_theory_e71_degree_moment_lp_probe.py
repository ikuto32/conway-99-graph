"""Convex degree-moment discovery on frozen profiles, never completions.

Floating LP statuses are diagnostic only.  An exclusion is credited only
when a rationalized Farkas multiplier passes an exact integer check.
"""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools as it
import json
import math
import os
from pathlib import Path
import time

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
from scipy.optimize import linprog
import scratch_theory_e71_projector_transport_frontier_audit as base


OUTPUT = Path("scratch_theory_e71_degree_moment_lp_probe.json")


def raw_domains(c, k4):
    basis, pivots = base.reduced(k4)
    dimension = len(pivots)
    denominator = math.lcm(*(v.denominator for row in basis for v in row))
    columns = [tuple(int(basis[i][j] * denominator) for i in range(dimension))
               for j in range(21)]
    domains = []
    for source in range(21):
        rows = []
        for degrees in it.product(range(5), repeat=dimension):
            v = tuple(4 * degree - c[source][p] for degree, p in zip(degrees, pivots))
            r = tuple(sum(a * b for a, b in zip(v, col)) for col in columns)
            if any(x % denominator for x in r):
                continue
            numerators = tuple(x // denominator + c[source][i] for i, x in enumerate(r))
            if any(x % 4 or not 0 <= x <= 16 for x in numerators):
                continue
            if sum(numerators) != 48:
                continue
            rows.append({"pivot": v, "degree": tuple(x // 4 for x in numerators)})
        assert len({r["pivot"] for r in rows}) == len(rows)
        domains.append(rows)
    return pivots, domains


def model(entry, profile):
    exceptional, c, z, k4 = base.compression(entry, profile)
    pivots, domains = raw_domains(c, k4)
    labels = {label: i for i, label in enumerate(base.LABELS)}
    internal = [[0] * 4 for _ in range(21)]
    for left, right in entry["internal_edges"]:
        x, y = labels[tuple(left)], labels[tuple(right)]
        assert x // 4 == y // 4
        internal[x // 4][x % 4] += 1
        internal[y // 4][y % 4] += 1
    for source in range(21):
        if source not in exceptional:
            internal[source] = [2] * 4
        assert sum(internal[source]) == c[source][source]
    moment_pairs = tuple(it.combinations_with_replacement(range(len(pivots)), 2))
    groups = [(source, degree, count) for source in range(21)
              for degree, count in sorted(Counter(internal[source]).items())]
    columns = []
    variables = []
    for group, (source, degree, _) in enumerate(groups):
        for record in domains[source]:
            if record["degree"][source] != degree:
                continue
            v = record["pivot"]
            column = [int(i == group) for i in range(len(groups))]
            column += [v[j] if i == source else 0
                       for i in range(21) for j in range(len(pivots))]
            column += [v[i] * v[j] for i, j in moment_pairs]
            columns.append(column)
            variables.append({"source": source, "internal_degree": degree, "pivot": list(v)})
    target = [count for _, _, count in groups] + [0] * (21 * len(pivots))
    target += [4 * k4[pivots[i]][pivots[j]] for i, j in moment_pairs]
    matrix = list(map(list, zip(*columns)))
    assert len(matrix) == len(target)
    return matrix, target, {
        "pivot_supports": [list(base.SUPPORTS[p]) for p in pivots],
        "rank_K4": len(pivots), "raw_row_patterns": sum(map(len, domains)),
        "groups": groups, "variables": variables, "moment_pairs": moment_pairs,
        "matrix_sha256": hashlib.sha256(json.dumps([matrix, target], separators=(",", ":")).encode()).hexdigest(),
    }


def farkas(matrix, target):
    array = np.asarray(matrix, dtype=float)
    answer = linprog(np.asarray(target, dtype=float), A_ub=-array.T,
                     b_ub=np.zeros(array.shape[1]), bounds=(-1, 1), method="highs")
    if not answer.success or answer.fun >= -1e-7:
        return None
    for cap in (1000, 100000, 10000000):
        rational = [Fraction(float(v)).limit_denominator(cap) for v in answer.x]
        denominator = math.lcm(*(v.denominator for v in rational))
        vector = [int(v * denominator) for v in rational]
        divisor = math.gcd(*vector)
        vector = [v // divisor for v in vector]
        slacks = [sum(a * b for a, b in zip(vector, column)) for column in zip(*matrix)]
        separation = sum(a * b for a, b in zip(vector, target))
        if min(slacks, default=0) >= 0 and separation < 0:
            return {"integer_multiplier": vector, "min_column_slack": min(slacks, default=0),
                    "target_pairing": separation, "rationalization_cap": cap,
                    "exact_integer_check_pass": True}
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-frozen", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    started = time.monotonic()
    catalog, mining, kernel = map(base.read, (base.CATALOG, base.MINING, base.KERNEL))
    entries = {base.key(r): r for r in catalog["macro_entries"] if r["signature_stabilizer_canonical"]}
    profiles = {(base.key(r), r["parameter"]): r for r in mining["profile_rows"]["71"]}
    keys = {(694, 0, 0), (694, 1, 0), (724, 1, 0)}
    tasks = [(tuple(r["key"]), p["parameter"], r["coverage"])
             for r in kernel["rows"] if r["macro_passes_some_full_Gram_profile_kernel_port_CSP"]
             and (args.all_frozen or tuple(r["key"]) in keys)
             for p in r["profiles"] if p["passes_kernel_port_CSP"]]
    records = []
    for key, parameter, coverage in tasks:
        matrix, target, metadata = model(entries[key], profiles[(key, parameter)])
        primal = linprog(np.zeros(len(matrix[0])), A_eq=np.asarray(matrix, dtype=float),
                         b_eq=np.asarray(target, dtype=float), bounds=(0, None), method="highs")
        certificate = farkas(matrix, target) if primal.status == 2 else None
        record = {"key": list(key), "parameter": parameter, "coverage": coverage,
                  "equations": len(matrix), "variables": len(matrix[0]),
                  "LP_status": int(primal.status),
                  "exactly_certified_infeasible": certificate is not None,
                  "certificate": certificate, "model": metadata}
        records.append(record)
        print(json.dumps({k: v for k, v in record.items() if k not in ("model", "certificate")}), flush=True)
    result = {
        "status": "FROZEN_DEGREE_MOMENT_LP_DISCOVERY_COMPLETE",
        "scope": "Frozen profiles only; nonnegative row weights, fibre first moments and global second moment; no graph completion.",
        "all_frozen_profiles_requested": args.all_frozen,
        "inputs_sha256": {str(p): base.sha(p) for p in (base.CATALOG, base.MINING, base.KERNEL, Path(base.__file__))},
        "profiles": records,
        "profile_count": len(records),
        "exact_infeasible_profiles": sum(r["exactly_certified_infeasible"] for r in records),
        "requires_independent_audit_before_inventory_credit": True,
        "pointwise_E0_lower_bound": None, "local_completions_enumerated": 0,
        "elapsed_seconds": time.monotonic() - started,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "profiles"}), flush=True)


if __name__ == "__main__":
    main()
