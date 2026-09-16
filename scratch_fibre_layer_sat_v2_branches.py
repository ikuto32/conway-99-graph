"""Safe deep orbit branches for the BP + 126-fibre-equation SAT layer.

After fixing the WLOG disjoint-support edge u={0,2}--v={4,6}, this script
fixes (1) the complete six-edge graph in u's four-vertex support fibre and
(2) u's unique coordinate-matching partner for each exact symbol 0 and 2.
The 784 locally BP-compatible labelled states collapse to 85 orbits under
the full stabilizer of u and v.  No unproved E0 bound is used.

The persistent-worker portfolio loads the CNF once per process and keeps
only globally valid learned clauses between assumption branches.  Any SAT
model is independently checked by the layer verifier.  This script never
writes submission.txt.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import time
from pathlib import Path

from scratch_fibre_layer_sat_strong import CNF_PATH, coordinates, verify_layer
from scratch_general_triangle_portfolio import residual_group, transform_label


DESCRIPTION_PATH = Path("scratch_fibre_layer_sat_v2_branches.json")
SCREEN_PATH = Path("scratch_fibre_layer_sat_v2_screen.json")
PORTFOLIO_PATH = Path("scratch_fibre_layer_sat_v2_portfolio.json")
SOLUTION_PATH = Path("scratch_fibre_layer_sat_v2_solution.json")


def transform_symbol(symbol, element):
    perm, flips = element
    group, bit = divmod(symbol, 2)
    return 2 * perm[group] + (bit ^ flips[group])


def canonical_fibre_edge(left, right):
    return tuple(sorted((left, right)))


def transform_state(state, element):
    graph, partners = state
    image_graph = frozenset(
        canonical_fibre_edge(
            transform_label(left, *element), transform_label(right, *element)
        )
        for left, right in graph
    )
    image_partners = tuple(
        sorted(
            (
                transform_symbol(symbol, element),
                transform_label(partner, *element),
            )
            for symbol, partner in partners
        )
    )
    return image_graph, image_partners


def make_specs():
    labels, index, _variables, edge = coordinates()
    u_label, v_label = (0, 2), (4, 6)
    u, v = index[u_label], index[v_label]
    fibre_labels = ((0, 2), (0, 3), (1, 2), (1, 3))
    fibre_edges = tuple(
        canonical_fibre_edge(left, right)
        for left, right in itertools.combinations(fibre_labels, 2)
    )

    local_graphs = []
    for bits in itertools.product((0, 1), repeat=6):
        graph = frozenset(
            fibre_edges[position]
            for position, selected in enumerate(bits)
            if selected
        )
        compatible = True
        for own in fibre_labels:
            own_groups = {symbol // 2 for symbol in own}
            for symbol in range(4):
                if symbol // 2 not in own_groups:
                    continue
                local_count = sum(
                    symbol in other
                    for pair in graph
                    if own in pair
                    for other in pair
                    if other != own
                )
                if local_count > 1:
                    compatible = False
        if compatible:
            local_graphs.append(graph)
    assert len(local_graphs) == 19

    labelled_states = set()
    for graph in local_graphs:
        options = []
        for symbol in u_label:
            local = [
                other
                for pair in graph
                if u_label in pair
                for other in pair
                if other != u_label and symbol in other
            ]
            assert len(local) <= 1
            if local:
                options.append(local)
            else:
                outside = [
                    label
                    for label in labels
                    if label not in fibre_labels and symbol in label
                ]
                assert len(outside) == 10
                options.append(outside)
        for left, right in itertools.product(*options):
            labelled_states.add(
                (graph, tuple(sorted(((0, left), (2, right)))))
            )
    assert len(labelled_states) == 784

    stabilizer = residual_group(frozenset())
    assert len(stabilizer) == 192
    unseen = set(labelled_states)
    orbits = []
    while unseen:
        seed = min(unseen, key=repr)
        orbit = {transform_state(seed, element) for element in stabilizer}
        assert orbit <= labelled_states
        unseen -= orbit
        orbits.append(sorted(orbit, key=repr))
    assert len(orbits) == 85
    assert set().union(*(set(orbit) for orbit in orbits)) == labelled_states

    fixed_edge = edge(u, v)
    specs = []
    for number, orbit in enumerate(orbits):
        graph, partners = orbit[0]
        assumptions = [fixed_edge]
        for left, right in fibre_edges:
            literal = edge(index[left], index[right])
            assumptions.append(literal if (left, right) in graph else -literal)
        for _symbol, partner in partners:
            assumptions.append(edge(u, index[partner]))
        assumption_set = set(assumptions)
        assert not any(-literal in assumption_set for literal in assumption_set)
        assumptions = sorted(assumption_set, key=lambda literal: (abs(literal), literal < 0))
        specs.append(
            {
                "branch": f"orbit_{number:02d}",
                "orbit_size": len(orbit),
                "fibre_edges": [[list(left), list(right)] for left, right in sorted(graph)],
                "coordinate_partners": {
                    str(symbol): list(partner) for symbol, partner in partners
                },
                "assumptions": assumptions,
            }
        )
    return specs, {
        "fixed_u": list(u_label),
        "fixed_v": list(v_label),
        "stabilizer_size": len(stabilizer),
        "locally_compatible_fibre_graphs": len(local_graphs),
        "labelled_states": len(labelled_states),
        "orbit_count": len(orbits),
        "orbit_size_histogram": {
            str(size): sum(len(orbit) == size for orbit in orbits)
            for size in sorted({len(orbit) for orbit in orbits})
        },
    }


def describe():
    specs, coverage = make_specs()
    result = {
        "model": "safe full-u-fibre plus coordinate-partner orbit branches",
        "cnf": str(CNF_PATH),
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


def worker(
    worker_id, cnf_path, specs, conflict_budget, use_bp_phases, stop_event, out_queue
):
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    formula = CNF(from_file=cnf_path)
    loaded = time.monotonic()
    records = []
    previous = {"restarts": 0, "conflicts": 0, "decisions": 0, "propagations": 0}
    bp_solver = None
    if use_bp_phases:
        bp_formula = CNF(from_file=str(Path("scratch_bp_seed.cnf").resolve()))
        bp_solver = Solver(name="cadical300", bootstrap_with=bp_formula.clauses)
    with Solver(name="cadical300", bootstrap_with=formula.clauses) as solver:
        for spec in specs:
            if stop_event.is_set():
                break
            before = time.monotonic()
            bp_stats = None
            if bp_solver is not None:
                bp_answer = bp_solver.solve(assumptions=spec["assumptions"])
                bp_stats = bp_solver.accum_stats()
                if not bp_answer:
                    records.append(
                        {
                            "branch": spec["branch"],
                            "status": "UNSAT_BP_SUBMODEL",
                            "solve_seconds": round(time.monotonic() - before, 3),
                            "bp_stats_cumulative": bp_stats,
                        }
                    )
                    continue
                bp_model = bp_solver.get_model()
                solver.set_phases(
                    [literal for literal in bp_model if 0 < abs(literal) <= 3486]
                )
            solver.conf_budget(conflict_budget)
            answer = solver.solve_limited(assumptions=spec["assumptions"])
            cumulative = solver.accum_stats()
            delta = {
                key: cumulative.get(key, 0) - previous.get(key, 0)
                for key in cumulative
            }
            previous = cumulative
            model = solver.get_model() if answer is True else None
            records.append(
                {
                    "branch": spec["branch"],
                    "status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
                    "solve_seconds": round(time.monotonic() - before, 3),
                    "stats_delta": delta,
                    "bp_phase_seeded": use_bp_phases,
                    "bp_stats_cumulative": bp_stats,
                    "positive_edge_variables": [
                        literal for literal in model if 0 < literal <= 3486
                    ] if model else [],
                }
            )
            if answer is True:
                stop_event.set()
                break
    if bp_solver is not None:
        bp_solver.delete()
    out_queue.put(
        {
            "worker": worker_id,
            "load_seconds": round(loaded - started, 3),
            "wall_seconds": round(time.monotonic() - started, 3),
            "records": records,
        }
    )


def portfolio(conflict_budget, max_parallel, output_path, use_bp_phases):
    specs, coverage = make_specs()
    screen_result = json.loads(SCREEN_PATH.read_text(encoding="utf-8"))
    propagation_unsat = {
        row["branch"]
        for row in screen_result["records"]
        if row["status"] == "UNSAT_BY_PROPAGATION"
    }
    live_specs = [spec for spec in specs if spec["branch"] not in propagation_unsat]
    assignments = [live_specs[offset::max_parallel] for offset in range(max_parallel)]
    context = mp.get_context("spawn")
    stop_event = context.Event()
    out_queue = context.Queue()
    processes = []
    for worker_id, assignment in enumerate(assignments):
        process = context.Process(
            target=worker,
            args=(
                worker_id,
                str(CNF_PATH.resolve()),
                assignment,
                conflict_budget,
                use_bp_phases,
                stop_event,
                out_queue,
            ),
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
        row["verification"] = {
            key: value for key, value in checked.items() if key != "edges"
        }
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
        "model": "exact fibre layer with safe 85-orbit deep decomposition",
        "cnf": str(CNF_PATH),
        "solver": "CaDiCaL 3.0 via PySAT persistent workers",
        "conflict_budget_per_branch": conflict_budget,
        "max_parallel": max_parallel,
        "bp_phase_seeded": use_bp_phases,
        "branches_exhaustive": True,
        "coverage": coverage,
        "status": "SAT" if verified is not None else "UNSAT" if all(row["status"].startswith("UNSAT") for row in ordered) else "UNKNOWN",
        "counts": {
            status: sum(row["status"] == status for row in ordered)
            for status in (
                "SAT", "UNSAT", "UNSAT_BP_SUBMODEL", "UNSAT_BY_PROPAGATION",
                "UNKNOWN", "NOT_RUN_AFTER_SAT"
            )
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
    parser.add_argument("--bp-phases", action="store_true")
    args = parser.parse_args()
    if args.describe:
        result = describe()
        print(json.dumps(result["coverage"], sort_keys=True), flush=True)
    if args.screen:
        result = screen()
        print(json.dumps(result["counts"]), flush=True)
    if args.conflicts > 0:
        if not 1 <= args.max_parallel <= 4:
            parser.error("--max-parallel must be 1..4")
        result = portfolio(
            args.conflicts, args.max_parallel, args.output, args.bp_phases
        )
        print(json.dumps({"status": result["status"], "counts": result["counts"]}), flush=True)
    if not (args.describe or args.screen or args.conflicts > 0):
        parser.error("select an action")


if __name__ == "__main__":
    mp.freeze_support()
    main()
