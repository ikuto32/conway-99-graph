"""Independent mechanical audit of the general SAT v2 artifacts."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from scratch_general_sat_deep_branches import make_specs as make_one_partner_specs
from scratch_general_sat_two_matchings import make_specs as make_two_partner_specs
from scratch_general_sat_v2 import add_atleast_two_linear, coordinates


class TinyPool:
    def __init__(self, top):
        self.top = top
        self.ids = {}

    def id(self, key):
        if key not in self.ids:
            self.top += 1
            self.ids[key] = self.top
        return self.ids[key]


def clause_satisfied(clause, values):
    return any(values[lit] if lit > 0 else not values[-lit] for lit in clause)


def threshold_audit():
    rows = []
    for size in range(2, 7):
        clauses = []
        pool = TinyPool(size)
        add_atleast_two_linear(clauses, list(range(1, size + 1)), pool, (99, size))
        auxiliary_count = pool.top - size
        checked = 0
        for inputs in itertools.product((False, True), repeat=size):
            satisfiable = False
            for auxiliary in itertools.product((False, True), repeat=auxiliary_count):
                values = (False,) + inputs + auxiliary
                if all(clause_satisfied(clause, values) for clause in clauses):
                    satisfiable = True
                    break
            assert satisfiable == (sum(inputs) >= 2)
            checked += 1
        rows.append(
            {
                "input_count": size,
                "auxiliary_count": auxiliary_count,
                "assignments_checked": checked,
                "ok": True,
            }
        )
    return rows


def triangle_counts():
    labels = coordinates()[0]
    sets = [set(label) for label in labels]
    allowed = sum(
        sets[u].isdisjoint(sets[v])
        and sets[u].isdisjoint(sets[w])
        and sets[v].isdisjoint(sets[w])
        for u, v, w in itertools.combinations(range(84), 3)
    )
    histogram = {}
    for u, v in itertools.combinations(range(84), 2):
        if not sets[u].isdisjoint(sets[v]):
            continue
        count = sum(
            sets[w].isdisjoint(sets[u]) and sets[w].isdisjoint(sets[v])
            for w in range(84)
            if w not in (u, v)
        )
        histogram[count] = histogram.get(count, 0) + 1
    assert allowed == 35560 and histogram == {40: 42, 41: 840, 42: 1680}
    return {"allowed_triples": allowed, "forbidden_triples": 95284 - allowed, "pair_histogram": histogram}


def cnf_audit(path, metadata_path):
    meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    with Path(path).open("rb") as handle:
        header = handle.readline().decode("ascii").strip().split()
    assert header[:2] == ["p", "cnf"]
    variables, clauses = map(int, header[2:])
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()
    assert variables == meta["variables"] and clauses == meta["clauses"]
    assert digest == meta["cnf_sha256"]
    return {"path": path, "variables": variables, "clauses": clauses, "sha256": digest, "ok": True}


def main():
    one_specs, one_coverage = make_one_partner_specs()
    two_specs, two_coverage = make_two_partner_specs()
    assert len(one_specs) == 98 and len(one_coverage) == 17
    assert len(two_specs) == 559 and len(two_coverage) == 17
    one_screen = json.loads(Path("scratch_general_sat_deep_screen.json").read_text(encoding="utf-8"))
    two_screen = json.loads(Path("scratch_general_sat_two_matchings_screen.json").read_text(encoding="utf-8"))
    assert one_screen["counts"] == {"LIVE": 91, "UNSAT_BY_PROPAGATION": 7}
    assert two_screen["counts"] == {"LIVE": 445, "UNSAT_BY_PROPAGATION": 114}
    result = {
        "threshold_circuit_exhaustive_small_audit": threshold_audit(),
        "triangle_enumeration": triangle_counts(),
        "cnfs": [
            cnf_audit("scratch_general_sat_v2.cnf", "scratch_general_sat_v2_build.json"),
            cnf_audit("scratch_general_sat_hybrid.cnf", "scratch_general_sat_hybrid_build.json"),
            cnf_audit("scratch_general_sat_triangles.cnf", "scratch_general_sat_triangles_build.json"),
        ],
        "branch_audit": {
            "live_triangle_parents": 17,
            "one_partner_orbits": len(one_specs),
            "one_partner_propagation": one_screen["counts"],
            "two_partner_orbits": len(two_specs),
            "two_partner_propagation": two_screen["counts"],
        },
        "submission_exists": Path("submission.txt").exists(),
        "ok": True,
    }
    Path("scratch_general_sat_v2_audit.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
