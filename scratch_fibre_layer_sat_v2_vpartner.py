"""Fourth-level exact fibre-layer branches fixing one coordinate partner of v.

Starting from the 85 safe u-state orbit representatives, fix the unique
neighbour of v={4,6} whose label contains exact symbol 4.  Orbits are taken
under the genuine residual stabilizer of each u-state and symbol 4.  The 525
resulting branches are exhaustive; no global E0 assumption is used.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import time
from pathlib import Path

from scratch_fibre_layer_sat_strong import CNF_PATH, coordinates, verify_layer
from scratch_fibre_layer_sat_v2_branches import (
    make_specs as make_base_specs,
    transform_state,
    transform_symbol,
)
from scratch_general_triangle_portfolio import residual_group, transform_label


DESCRIPTION_PATH = Path("scratch_fibre_layer_sat_v2_vpartner_branches.json")
SCREEN_PATH = Path("scratch_fibre_layer_sat_v2_vpartner_screen.json")
PORTFOLIO_PATH = Path("scratch_fibre_layer_sat_v2_vpartner_portfolio.json")
SOLUTION_PATH = Path("scratch_fibre_layer_sat_v2_vpartner_solution.json")


def state_from_spec(spec):
    graph = frozenset(
        tuple(sorted((tuple(left), tuple(right))))
        for left, right in spec["fibre_edges"]
    )
    partners = tuple(
        sorted((int(symbol), tuple(partner)) for symbol, partner in spec["coordinate_partners"].items())
    )
    return graph, partners


def make_specs():
    labels, index, _variables, edge = coordinates()
    base_specs, base_coverage = make_base_specs()
    group = residual_group(frozenset())
    v_label = (4, 6)
    v = index[v_label]
    candidates = [label for label in labels if label != v_label and 4 in label]
    assert len(candidates) == 11

    specs, coverage = [], {}
    for base in base_specs:
        state = state_from_spec(base)
        stabilizer = [
            element
            for element in group
            if transform_state(state, element) == state
            and transform_symbol(4, element) == 4
        ]
        assert stabilizer
        unseen, orbits = set(candidates), []
        while unseen:
            seed = min(unseen)
            orbit = {transform_label(seed, *element) for element in stabilizer}
            assert orbit <= set(candidates)
            unseen -= orbit
            orbits.append(sorted(orbit))
        assert set().union(*(set(orbit) for orbit in orbits)) == set(candidates)
        coverage[base["branch"]] = {
            "residual_stabilizer_fixing_symbol_4": len(stabilizer),
            "candidate_count": len(candidates),
            "orbit_count": len(orbits),
            "orbit_sizes": [len(orbit) for orbit in orbits],
        }
        for number, orbit in enumerate(orbits):
            partner = orbit[0]
            assumptions = sorted(
                set(base["assumptions"] + [edge(v, index[partner])]),
                key=lambda literal: (abs(literal), literal < 0),
            )
            assert not any(-literal in assumptions for literal in assumptions)
            specs.append(
                {
                    "branch": f"{base['branch']}__v4_{number:02d}",
                    "parent": base["branch"],
                    "v_symbol_4_partner": list(partner),
                    "orbit_size": len(orbit),
                    "assumptions": assumptions,
                }
            )
    assert len(specs) == 525
    return specs, {
        "base_coverage": base_coverage,
        "base_orbits": len(base_specs),
        "v_partner_orbits": len(specs),
        "v_symbol": 4,
        "candidates_per_base": len(candidates),
        "residual_coverage": coverage,
    }


def describe():
    specs, coverage = make_specs()
    result = {
        "model": "safe v-coordinate partner branches below 85 u-state orbits",
        "branches_exhaustive": True,
        "coverage": coverage,
        "specs": specs,
    }
    DESCRIPTION_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def screen():
    from pysat.formula import CNF
    from pysat.solvers import Solver

    specs, coverage = make_specs()
    started = time.monotonic()
    formula = CNF(from_file=str(CNF_PATH))
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
        "cnf": str(CNF_PATH),
        "solver": "CaDiCaL 3.0 via PySAT propagate",
        "branches_exhaustive": True,
        "coverage": coverage,
        "load_seconds": round(loaded - started, 3),
        "screen_seconds": round(time.monotonic() - loaded, 3),
        "counts": {
            status: sum(row["status"] == status for row in records)
            for status in ("LIVE", "UNSAT_BY_PROPAGATION")
        },
        "records": records,
    }
    SCREEN_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def worker(worker_id, cnf_path, specs, conflict_budget, stop_event, out_queue):
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    formula = CNF(from_file=cnf_path)
    loaded = time.monotonic()
    rows = []
    previous = {"restarts": 0, "conflicts": 0, "decisions": 0, "propagations": 0}
    with Solver(name="cadical300", bootstrap_with=formula.clauses) as solver:
        for spec in specs:
            if stop_event.is_set():
                break
            before = time.monotonic()
            solver.conf_budget(conflict_budget)
            answer = solver.solve_limited(assumptions=spec["assumptions"])
            cumulative = solver.accum_stats()
            delta = {key: cumulative.get(key, 0) - previous.get(key, 0) for key in cumulative}
            previous = cumulative
            model = solver.get_model() if answer is True else None
            rows.append(
                {
                    "branch": spec["branch"],
                    "parent": spec["parent"],
                    "status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
                    "solve_seconds": round(time.monotonic() - before, 3),
                    "stats_delta": delta,
                    "positive_edge_variables": [literal for literal in model if 0 < literal <= 3486] if model else [],
                }
            )
            if answer is True:
                stop_event.set()
                break
    out_queue.put(
        {
            "worker": worker_id,
            "load_seconds": round(loaded - started, 3),
            "wall_seconds": round(time.monotonic() - started, 3),
            "records": rows,
        }
    )


def portfolio(conflict_budget, max_parallel, output_path):
    specs, coverage = make_specs()
    screened = json.loads(SCREEN_PATH.read_text(encoding="utf-8"))
    propagation_unsat = {
        row["branch"] for row in screened["records"]
        if row["status"] == "UNSAT_BY_PROPAGATION"
    }
    live = [spec for spec in specs if spec["branch"] not in propagation_unsat]
    assignments = [live[offset::max_parallel] for offset in range(max_parallel)]
    context = mp.get_context("spawn")
    stop_event = context.Event()
    out_queue = context.Queue()
    processes = []
    for worker_id, assignment in enumerate(assignments):
        process = context.Process(
            target=worker,
            args=(worker_id, str(CNF_PATH.resolve()), assignment, conflict_budget, stop_event, out_queue),
        )
        process.start()
        processes.append(process)
    worker_results = [out_queue.get(timeout=7200) for _ in processes]
    for process in processes:
        process.join(10)
        if process.is_alive():
            process.terminate()
            process.join(10)

    records = {
        row["branch"]: row
        for worker_result in worker_results
        for row in worker_result["records"]
    }
    verified = None
    for row in records.values():
        if row["status"] != "SAT":
            continue
        checked = verify_layer(set(row["positive_edge_variables"]))
        row["verification"] = {key: value for key, value in checked.items() if key != "edges"}
        if checked["ok"] and verified is None:
            verified = checked
            SOLUTION_PATH.write_text(json.dumps(checked, indent=2) + "\n", encoding="utf-8")

    ordered = []
    for spec in specs:
        name = spec["branch"]
        if name in propagation_unsat:
            ordered.append({"branch": name, "status": "UNSAT_BY_PROPAGATION"})
        elif name in records:
            ordered.append(records[name])
        else:
            ordered.append({"branch": name, "status": "NOT_RUN_AFTER_SAT"})
    result = {
        "model": "exact fibre layer with safe u-state and v-partner orbits",
        "solver": "CaDiCaL 3.0 via PySAT persistent workers",
        "conflict_budget_per_branch": conflict_budget,
        "max_parallel": max_parallel,
        "branches_exhaustive": True,
        "coverage": coverage,
        "status": "SAT" if verified is not None else "UNSAT" if all(row["status"].startswith("UNSAT") for row in ordered) else "UNKNOWN",
        "counts": {
            status: sum(row["status"] == status for row in ordered)
            for status in ("SAT", "UNSAT", "UNSAT_BY_PROPAGATION", "UNKNOWN", "NOT_RUN_AFTER_SAT")
        },
        "workers": worker_results,
        "records": ordered,
    }
    Path(output_path).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("--screen", action="store_true")
    parser.add_argument("--conflicts", type=int, default=0)
    parser.add_argument("--max-parallel", type=int, default=4)
    parser.add_argument("--output", default=str(PORTFOLIO_PATH))
    args = parser.parse_args()
    if args.describe:
        result = describe()
        print(json.dumps({"branches": len(result["specs"])}), flush=True)
    if args.screen:
        result = screen()
        print(json.dumps(result["counts"]), flush=True)
    if args.conflicts > 0:
        result = portfolio(args.conflicts, args.max_parallel, args.output)
        print(json.dumps({"status": result["status"], "counts": result["counts"]}), flush=True)
    if not (args.describe or args.screen or args.conflicts > 0):
        parser.error("select an action")


if __name__ == "__main__":
    mp.freeze_support()
    main()
