"""Third-level safe symmetry branches for the 17 live general SAT cases.

For each normalized triangle ``u-v-w``, choose the smaller exact symbol ``s``
in the label of ``w``.  BP says that ``w`` has a unique outer neighbour whose
label contains ``s``.  The subgroup preserving the existing branch and fixing
both ``w`` and ``s`` acts on the eleven candidates.  Branching on its orbits
is exhaustive and disjoint for that coordinate matching partner.

The script can screen branches by unit propagation or run a bounded
CaDiCaL-3.0 conflict portfolio.  SAT edge assignments are independently
expanded and checked; ``submission.txt`` is never written here.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import queue
import time
from pathlib import Path

from scratch_general_exact_sat import coordinates, verify
from scratch_general_triangle_portfolio import (
    branch_specs,
    residual_group,
    transform_label,
)


DESCRIBE_PATH = Path("scratch_general_sat_deep_branches.json")
SCREEN_PATH = Path("scratch_general_sat_deep_screen.json")
PORTFOLIO_PATH = Path("scratch_general_sat_deep_portfolio.json")
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


def make_specs():
    labels, index, _variables, edge = coordinates()
    prior = json.loads(Path("scratch_general_triangle_portfolio.json").read_text(encoding="utf-8"))
    prior_status = {row["branch"]: row["status"] for row in prior["records"]}
    parents = [spec for spec in branch_specs()[0] if prior_status.get(spec["branch"]) == "UNKNOWN"]
    assert len(parents) == 17

    specs = []
    coverage = {}
    for parent in parents:
        w_label = tuple(parent["w_label"])
        w = index[w_label]
        symbol = min(w_label)
        group = [
            element
            for element in residual_group(PATTERNS[parent["base"]])
            if transform_label(w_label, *element) == w_label
            and transform_symbol(symbol, element) == symbol
        ]
        candidates = {
            label for label in labels if label != w_label and symbol in label
        }
        assert len(candidates) == 11
        unseen = set(candidates)
        orbits = []
        while unseen:
            seed = min(unseen)
            orbit = {
                transform_label(seed, *element)
                for element in group
            }
            assert orbit <= candidates
            unseen -= orbit
            orbits.append(sorted(orbit))
        assert set().union(*(set(orbit) for orbit in orbits)) == candidates

        coverage[parent["branch"]] = {
            "fixed_symbol": symbol,
            "stabilizer_size": len(group),
            "candidate_count": len(candidates),
            "orbit_count": len(orbits),
            "orbits": orbits,
        }
        for number, orbit in enumerate(orbits):
            representative = tuple(orbit[0])
            assumptions = list(parent["assumptions"])
            assumptions.append(edge(w, index[representative]))
            specs.append(
                {
                    "branch": f"{parent['branch']}__m{symbol}_{representative[0]}_{representative[1]}",
                    "parent": parent["branch"],
                    "base": parent["base"],
                    "w_label": list(w_label),
                    "fixed_symbol": symbol,
                    "matching_partner": list(representative),
                    "orbit_size": len(orbit),
                    "assumptions": assumptions,
                }
            )
    assert len(specs) == 98
    return specs, coverage


def describe():
    specs, coverage = make_specs()
    result = {
        "model": "safe coordinate-matching partner branches below 17 live triangle branches",
        "parent_branch_count": len(coverage),
        "branch_count": len(specs),
        "branches_exhaustive": True,
        "proof": (
            "BP gives a unique matching partner containing the fixed exact symbol; "
            "the enumerated stabilizer orbits cover all eleven candidates"
        ),
        "coverage": coverage,
        "specs": specs,
    }
    DESCRIBE_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
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


def worker(cnf_path, spec, conflict_budget, out_queue):
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    formula = CNF(from_file=cnf_path)
    loaded = time.monotonic()
    with Solver(name="cadical300", bootstrap_with=formula.clauses) as solver:
        solver.conf_budget(conflict_budget)
        answer = solver.solve_limited(assumptions=spec["assumptions"])
        model = solver.get_model() if answer is True else None
        stats = solver.accum_stats()
    out_queue.put(
        {
            "branch": spec["branch"],
            "parent": spec["parent"],
            "status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
            "load_seconds": round(loaded - started, 3),
            "solve_seconds": round(time.monotonic() - loaded, 3),
            "conflict_budget": conflict_budget,
            "stats": stats,
            "positive_edge_variables": [lit for lit in model if 0 < lit <= 3486] if model else [],
        }
    )


def portfolio(cnf_path, conflict_budget, max_parallel, only_live, output_path):
    specs, coverage = make_specs()
    if only_live and SCREEN_PATH.exists():
        prior = json.loads(SCREEN_PATH.read_text(encoding="utf-8"))
        live_names = {row["branch"] for row in prior["records"] if row["status"] == "LIVE"}
        specs = [spec for spec in specs if spec["branch"] in live_names]

    context = mp.get_context("spawn")
    records = {}
    verified = None
    for offset in range(0, len(specs), max_parallel):
        batch = specs[offset : offset + max_parallel]
        out_queue = context.Queue()
        processes = {}
        for spec in batch:
            process = context.Process(
                target=worker,
                args=(str(Path(cnf_path).resolve()), spec, conflict_budget, out_queue),
            )
            process.start()
            processes[spec["branch"]] = process
        for _ in batch:
            try:
                row = out_queue.get(timeout=3600)
            except queue.Empty:
                break
            records[row["branch"]] = row
            if row["status"] == "SAT":
                checked = verify(set(row["positive_edge_variables"]))
                row["verification"] = {k: v for k, v in checked.items() if k != "edges"}
                if checked["ok"]:
                    verified = checked
        for name, process in processes.items():
            process.join(10)
            if process.is_alive():
                process.terminate()
                process.join(10)
            records.setdefault(name, {"branch": name, "status": "WORKER_FAILURE", "exit_code": process.exitcode})
        if verified is not None:
            break

    ordered = [records.get(spec["branch"], {"branch": spec["branch"], "status": "NOT_RUN_AFTER_SAT"}) for spec in specs]
    result = {
        "cnf": cnf_path,
        "solver": "CaDiCaL 3.0 via PySAT",
        "conflict_budget_per_branch": conflict_budget,
        "max_parallel": max_parallel,
        "branches_exhaustive_below_live_parents": True,
        "branch_count": len(specs),
        "coverage": coverage,
        "status": "SAT" if verified is not None else "UNSAT" if all(r["status"] == "UNSAT" for r in ordered) else "UNKNOWN",
        "records": ordered,
    }
    Path(output_path).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if verified is not None:
        Path("scratch_general_sat_deep_solution.json").write_text(json.dumps(verified, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("--screen")
    parser.add_argument("--portfolio")
    parser.add_argument("--conflicts", type=int, default=0)
    parser.add_argument("--max-parallel", type=int, default=2)
    parser.add_argument("--only-live", action="store_true")
    parser.add_argument("--output", default=str(PORTFOLIO_PATH))
    args = parser.parse_args()
    if args.describe:
        row = describe()
        print(json.dumps({"branch_count": row["branch_count"]}), flush=True)
    if args.screen:
        row = screen(args.screen)
        print(json.dumps(row["counts"]), flush=True)
    if args.portfolio:
        if args.conflicts <= 0:
            parser.error("--portfolio requires --conflicts")
        row = portfolio(
            args.portfolio, args.conflicts, args.max_parallel, args.only_live, args.output
        )
        print(json.dumps({"status": row["status"], "branch_count": row["branch_count"]}), flush=True)
    if not (args.describe or args.screen or args.portfolio):
        parser.error("select an action")


if __name__ == "__main__":
    mp.freeze_support()
    main()
