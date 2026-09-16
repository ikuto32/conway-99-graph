"""Exhaustive fourth-level branches fixing both coordinate partners of w.

Below each of the 17 live normalized triangle branches, BP supplies exactly
one matching partner for each of the two exact symbols in w's label.  The
full residual stabilizer (including a possible swap of those two symbols)
acts on the 11x11 assignments.  Orbit representatives give 559 exhaustive
branches.  This file constructs and propagation-screens them only.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from scratch_general_exact_sat import coordinates
from scratch_general_triangle_portfolio import branch_specs, residual_group, transform_label


DESCRIPTION_PATH = Path("scratch_general_sat_two_matchings.json")
SCREEN_PATH = Path("scratch_general_sat_two_matchings_screen.json")
PATTERNS = {
    "a0": frozenset(),
    "a1_complement": frozenset(((1, 3),)),
    "a1_cross": frozenset(((0, 3),)),
    "a2_crosses": frozenset(((0, 3), (1, 2))),
}


def transform_symbol(symbol, element):
    perm, flips = element
    group, bit = divmod(symbol, 2)
    return 2 * perm[group] + (bit ^ flips[group])


def transform_state(state, element):
    return tuple(
        sorted(
            (transform_symbol(symbol, element), transform_label(label, *element))
            for symbol, label in state
        )
    )


def make_specs():
    labels, index, _variables, edge = coordinates()
    prior = json.loads(Path("scratch_general_triangle_portfolio.json").read_text(encoding="utf-8"))
    status = {row["branch"]: row["status"] for row in prior["records"]}
    parents = [spec for spec in branch_specs()[0] if status.get(spec["branch"]) == "UNKNOWN"]
    assert len(parents) == 17
    specs, coverage = [], {}
    for parent in parents:
        w_label = tuple(parent["w_label"])
        w = index[w_label]
        s, t = w_label
        group = [
            element
            for element in residual_group(PATTERNS[parent["base"]])
            if transform_label(w_label, *element) == w_label
        ]
        candidates_s = [label for label in labels if label != w_label and s in label]
        candidates_t = [label for label in labels if label != w_label and t in label]
        assert len(candidates_s) == len(candidates_t) == 11
        states = {
            tuple(sorted(((s, left), (t, right))))
            for left in candidates_s
            for right in candidates_t
        }
        assert len(states) == 121
        unseen, orbits = set(states), []
        while unseen:
            seed = min(unseen)
            orbit = {transform_state(seed, element) for element in group}
            assert orbit <= states
            unseen -= orbit
            orbits.append(sorted(orbit))
        assert set().union(*(set(orbit) for orbit in orbits)) == states
        coverage[parent["branch"]] = {
            "stabilizer_size": len(group),
            "assignment_count": 121,
            "orbit_count": len(orbits),
            "orbit_sizes": [len(orbit) for orbit in orbits],
        }
        for number, orbit in enumerate(orbits):
            representative = orbit[0]
            partner_by_symbol = dict(representative)
            left, right = partner_by_symbol[s], partner_by_symbol[t]
            assumptions = list(parent["assumptions"])
            assumptions.extend((edge(w, index[left]), edge(w, index[right])))
            specs.append(
                {
                    "branch": f"{parent['branch']}__mm{number}",
                    "parent": parent["branch"],
                    "w_label": list(w_label),
                    "partners": {str(s): list(left), str(t): list(right)},
                    "orbit_size": len(orbit),
                    "assumptions": assumptions,
                }
            )
    assert len(specs) == 559
    return specs, coverage


def describe():
    specs, coverage = make_specs()
    result = {
        "model": "both coordinate-matching partners below 17 live triangle branches",
        "parent_branch_count": len(coverage),
        "branch_count": len(specs),
        "branches_exhaustive": True,
        "coverage": coverage,
        "specs": specs,
    }
    DESCRIPTION_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def screen(cnf_path):
    from pysat.formula import CNF
    from pysat.solvers import Solver

    specs, coverage = make_specs()
    started = time.monotonic()
    formula = CNF(from_file=cnf_path)
    loaded = time.monotonic()
    records = []
    with Solver(name="cadical300", bootstrap_with=formula.clauses) as solver:
        for spec in specs:
            ok, propagated = solver.propagate(assumptions=spec["assumptions"])
            records.append(
                {
                    "branch": spec["branch"],
                    "parent": spec["parent"],
                    "status": "LIVE" if ok else "UNSAT_BY_PROPAGATION",
                    "propagated_literal_count": len(propagated),
                }
            )
    result = {
        "cnf": cnf_path,
        "solver": "CaDiCaL 3.0 via PySAT propagate",
        "load_seconds": round(loaded - started, 3),
        "screen_seconds": round(time.monotonic() - loaded, 3),
        "branches_exhaustive": True,
        "branch_count": len(specs),
        "counts": {
            status: sum(row["status"] == status for row in records)
            for status in ("LIVE", "UNSAT_BY_PROPAGATION")
        },
        "coverage": coverage,
        "records": records,
    }
    SCREEN_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("--screen")
    args = parser.parse_args()
    if args.describe:
        result = describe()
        print(json.dumps({"branch_count": result["branch_count"]}), flush=True)
    if args.screen:
        result = screen(args.screen)
        print(json.dumps(result["counts"]), flush=True)
    if not (args.describe or args.screen):
        parser.error("select an action")


if __name__ == "__main__":
    main()
