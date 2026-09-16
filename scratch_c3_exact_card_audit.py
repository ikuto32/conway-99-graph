"""Exhaustive audit of repeated literals in PySAT sequential counters.

scratch_c3_exact_sat.py represents a small positive integer coefficient by
repeating a Boolean literal as multiple counter inputs.  This checks all
weighted sums with up to four variables, weights 1..5, and attainable bounds
0..sum(weights), comparing SAT under every fixed input assignment with the
intended arithmetic equality.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


def main() -> None:
    cases = 0
    assignments = 0
    for nvars in range(1, 5):
        variables = list(range(1, nvars + 1))
        for weights in itertools.product(range(1, 6), repeat=nvars):
            lits = [v for v, weight in zip(variables, weights) for _ in range(weight)]
            for bound in range(sum(weights) + 1):
                cnf = CardEnc.equals(
                    lits=lits, bound=bound, top_id=nvars,
                    encoding=EncType.seqcounter)
                with Solver(name="cadical195", bootstrap_with=cnf.clauses) as solver:
                    for values in itertools.product(range(2), repeat=nvars):
                        assumptions = [v if value else -v for v, value in zip(variables, values)]
                        observed = solver.solve(assumptions=assumptions)
                        total = sum(w * value for w, value in zip(weights, values))
                        expected = total == bound
                        assert observed == expected, (weights, bound, values, observed, expected)
                        assignments += 1
                upper = CardEnc.atmost(
                    lits=lits, bound=bound, top_id=nvars,
                    encoding=EncType.seqcounter)
                with Solver(name="cadical195", bootstrap_with=upper.clauses) as solver:
                    for values in itertools.product(range(2), repeat=nvars):
                        assumptions = [v if value else -v for v, value in zip(variables, values)]
                        observed = solver.solve(assumptions=assumptions)
                        total = sum(w * value for w, value in zip(weights, values))
                        expected = total <= bound
                        assert observed == expected, ("atmost", weights, bound, values, observed, expected)
                        assignments += 1
                cases += 1
    result = {"cases": cases, "fixed_assignments": assignments, "ok": True}
    Path("scratch_c3_exact_card_audit.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result)


if __name__ == "__main__":
    main()
