"""Solver-free independent exclusion of abelian Cayley 99-graphs.

This does not import the SAT implementation.  It first proves the necessary
doubling closure of an inverse-closed partial difference set and then
enumerates every union of doubling orbits having seven inverse pairs.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from pathlib import Path


SAT_AUDIT = Path("scratch_root_abelian_cayley_sat.json")
OUTPUT = Path("scratch_root_abelian_cayley_independent.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def elements(moduli):
    return tuple(itertools.product(*(range(m) for m in moduli)))


def plus(a, b, moduli):
    return tuple((a[i] + b[i]) % moduli[i] for i in range(len(moduli)))


def minus(a, b, moduli):
    return tuple((a[i] - b[i]) % moduli[i] for i in range(len(moduli)))


def opposite(a, moduli):
    return tuple((-a[i]) % moduli[i] for i in range(len(moduli)))


def pair_partition(moduli):
    zero = (0,) * len(moduli)
    unseen = set(elements(moduli)) - {zero}
    pairs = []
    while unseen:
        a = min(unseen)
        pair = frozenset((a, opposite(a, moduli)))
        assert len(pair) == 2 and pair <= unseen
        pairs.append(pair)
        unseen -= pair
    pairs.sort(key=lambda pair: tuple(sorted(pair)))
    assert len(pairs) == 49
    return tuple(pairs)


def doubling_orbits(moduli, pairs):
    pair_index = {a: i for i, pair in enumerate(pairs) for a in pair}
    unseen = set(range(49))
    orbits = []
    while unseen:
        start = min(unseen)
        orbit = []
        current = start
        while current not in orbit:
            orbit.append(current)
            representative = min(pairs[current])
            current = pair_index[plus(representative, representative, moduli)]
        assert current == start
        unseen -= set(orbit)
        orbits.append(tuple(orbit))
    assert sum(map(len, orbits)) == 49
    return tuple(orbits)


def invariant_selections(orbits, target_size=7):
    answers = []

    def visit(position, remaining, selected):
        if remaining == 0:
            answers.append(tuple(sorted(selected)))
            return
        if position == len(orbits) or remaining < 0:
            return
        if sum(len(orbit) for orbit in orbits[position:]) < remaining:
            return
        visit(position + 1, remaining, selected)
        orbit = orbits[position]
        if len(orbit) <= remaining:
            visit(position + 1, remaining - len(orbit), selected + orbit)

    visit(0, target_size, ())
    assert len(answers) == len(set(answers))
    return tuple(answers)


def difference_test(moduli, pairs, selected):
    group = elements(moduli)
    zero = (0,) * len(moduli)
    connection = frozenset(a for i in selected for a in pairs[i])
    assert len(connection) == 14 and zero not in connection
    counts = {target: 0 for target in group if target != zero}
    for a in connection:
        for b in connection:
            if a != b:
                counts[minus(a, b, moduli)] += 1
    bad = []
    correct = 0
    for target, count in counts.items():
        expected = 1 if target in connection else 2
        if count == expected:
            correct += 1
        else:
            bad.append((target, count, expected))
    return correct, tuple(bad)


def audit_group(name, moduli):
    pairs = pair_partition(moduli)
    orbits = doubling_orbits(moduli, pairs)
    selections = invariant_selections(orbits)
    rows = []
    correct_histogram = {}
    for selected in selections:
        correct, bad = difference_test(moduli, pairs, selected)
        correct_histogram[str(correct)] = correct_histogram.get(str(correct), 0) + 1
        rows.append({
            "selected_pair_indices": list(selected),
            "correct_nonzero_targets": correct,
            "violating_nonzero_targets": len(bad),
            "first_violation": None if not bad else {
                "target": list(bad[0][0]),
                "actual": bad[0][1],
                "expected": bad[0][2],
            },
        })
    return {
        "group": name,
        "moduli": list(moduli),
        "inverse_pairs": len(pairs),
        "doubling_orbit_sizes_on_inverse_pairs": sorted(map(len, orbits)),
        "doubling_invariant_selections_of_7_pairs": len(selections),
        "difference_set_solutions": sum(
            row["violating_nonzero_targets"] == 0 for row in rows
        ),
        "correct_target_histogram": correct_histogram,
        "candidate_rows": rows,
    }


def main():
    groups = (
        ("cyclic_Z99", (99,)),
        ("noncyclic_Z3xZ3xZ11", (3, 3, 11)),
    )
    audits = [audit_group(name, moduli) for name, moduli in groups]
    assert [row["doubling_invariant_selections_of_7_pairs"] for row in audits] == [0, 54]
    assert all(row["difference_set_solutions"] == 0 for row in audits)
    sat = json.loads(SAT_AUDIT.read_text(encoding="utf-8"))
    sat_statuses = {row["group"]: row["status"] for row in sat["results"]}
    assert sat_statuses == {name: "UNSAT" for name, _ in groups}
    result = {
        "status": "INDEPENDENT_SOLVER_FREE_EXCLUSION_VERIFIED",
        "scope": "all undirected Cayley graphs on groups of order 99",
        "doubling_closure_lemma": (
            "For t in inverse-closed D, the required single ordered representation "
            "t=a-b is acted on by (a,b)->(-b,-a). Odd cardinality forces its "
            "unique fixed point a=-b, hence t=2a with a in D. Thus D is invariant "
            "under multiplication by 2."
        ),
        "classification": (
            "Sylow counts give n_11 dividing 9 with n_11=1 mod 11, hence n_11=1; "
            "and n_3 dividing 11 with n_3=1 mod 3, hence n_3=1. The two normal "
            "Sylow subgroups commute. Every group of order 99 is therefore abelian, "
            "with its order-9 subgroup either Z9 or Z3 x Z3; the two group types are "
            "Z99 and Z3 x Z3 x Z11."
        ),
        "groups": audits,
        "independent_sat_crosscheck": {
            "path": str(SAT_AUDIT),
            "sha256": sha256(SAT_AUDIT),
            "statuses": sat_statuses,
        },
        "claim_boundary": (
            "No Cayley candidate on any group of order 99 exists. This does not "
            "exclude arbitrary non-Cayley Conway 99-graphs."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "status": result["status"],
        "invariant_candidates": {
            row["group"]: row["doubling_invariant_selections_of_7_pairs"]
            for row in audits
        },
        "solutions": {row["group"]: row["difference_set_solutions"] for row in audits},
    }, sort_keys=True))


if __name__ == "__main__":
    main()
