"""Independent structural and DIMACS audit for the fibre-layer SAT run."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from scratch_fibre_layer_sat_strong import branch_units, coordinates


def main():
    labels, index, variables, edge = coordinates()
    fibres = {}
    for u, label in enumerate(labels):
        support = tuple(sorted(symbol // 2 for symbol in label))
        fibres.setdefault(support, []).append(u)
    assert len(fibres) == 21 and all(len(fibre) == 4 for fibre in fibres.values())

    target_histogram = {1: 0, 2: 0}
    for fibre in fibres.values():
        for u, v in itertools.combinations(fibre, 2):
            target_histogram[2 - len(set(labels[u]).intersection(labels[v]))] += 1
    assert target_histogram == {1: 84, 2: 42}

    # Enumerate the three same-fibre incidences at normalized u and retain
    # only assignments compatible with the two mate-symbol target-one quotas.
    allowed = []
    for x, y, diagonal in itertools.product((0, 1), repeat=3):
        if x + diagonal <= 1 and y + diagonal <= 1:
            allowed.append((x, y, diagonal))
    assert set(allowed) == {(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1)}
    canonical_allowed = [
        {"bits_x_y_diagonal": list(bits), "branch": branch}
        for bits, branch in (
            ((0, 0, 0), "a0"),
            ((1, 0, 0), "a1_cross"),
            ((0, 1, 0), "a1_cross_under_coordinate_swap"),
            ((1, 1, 0), "a2_crosses"),
            ((0, 0, 1), "a1_complement"),
        )
    ]

    meta = json.loads(Path("scratch_fibre_layer_sat_strong_build.json").read_text(encoding="utf-8"))
    cnf = Path("scratch_fibre_layer_sat_strong.cnf")
    digest = hashlib.sha256(cnf.read_bytes()).hexdigest().upper()
    with cnf.open("r", encoding="ascii") as handle:
        header = handle.readline().split()
        clause_lines = 0
        maximum_variable = 0
        for line in handle:
            values = [int(value) for value in line.split()]
            assert values and values[-1] == 0
            clause_lines += 1
            maximum_variable = max(maximum_variable, *(abs(value) for value in values[:-1]))
    assert header[:2] == ["p", "cnf"]
    assert int(header[2]) == meta["variables"] == maximum_variable
    assert int(header[3]) == meta["clauses"] == clause_lines
    assert digest == meta["cnf_sha256"]
    assert branch_units(index, edge) == meta["branch_units"]

    portfolio = json.loads(Path("scratch_fibre_layer_sat_strong_portfolio.json").read_text(encoding="utf-8"))
    statuses = {row["branch"]: row["status"] for row in portfolio["records"]}
    assert statuses == {
        "a0": "UNKNOWN",
        "a1_complement": "UNKNOWN",
        "a1_cross": "UNKNOWN",
        "a2_crosses": "UNKNOWN",
        "a2_mixed": "UNSAT",
    }
    result = {
        "ok": True,
        "cnf": {
            "variables": meta["variables"],
            "clauses": meta["clauses"],
            "actual_clause_lines": clause_lines,
            "maximum_variable": maximum_variable,
            "sha256": digest,
        },
        "fibre_count": len(fibres),
        "same_support_pair_count": sum(len(list(itertools.combinations(fibre, 2))) for fibre in fibres.values()),
        "target_histogram": target_histogram,
        "allowed_incident_patterns": canonical_allowed,
        "portfolio_statuses": statuses,
        "submission_exists": Path("submission.txt").exists(),
    }
    Path("scratch_fibre_layer_sat_audit.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
