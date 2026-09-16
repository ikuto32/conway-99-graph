"""Symmetry-aligned BP-seed portfolio for the exact fibre-layer CNF.

Existing independently verified BP solutions are relabelled along every
oriented disjoint-support edge.  A residual scaffold automorphism then moves
their complete u-state to the corresponding representative among the 85 safe
deep branches.  For each covered branch, the lowest fibre-layer-energy seed
sets phases for all 3,486 edge variables and all 10,332 full-AND variables.

Only phase preferences are added: they do not constrain the SAT problem.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import time
from pathlib import Path

from scratch_fibre_layer_sat_strong import CNF_PATH, coordinates, verify_layer
from scratch_fibre_layer_sat_v2_branches import (
    make_specs,
    transform_state,
)
from scratch_general_triangle_portfolio import residual_group, transform_label


BANK_PATH = Path("scratch_fibre_layer_sat_v2_seed_bank.json")
PORTFOLIO_PATH = Path("scratch_fibre_layer_sat_v2_seeded_portfolio.json")
SOLUTION_PATH = Path("scratch_fibre_layer_sat_v2_seeded_solution.json")
SEED_FILES = (
    "scratch_bp_linearized_best.json",
    "scratch_bp_linearized_v2_best.json",
    "scratch_bp_linearized_v5_best.json",
    "scratch_bp_neighborhood16_best.json",
    "scratch_bp_seed.json",
    "scratch_bp_trade_best.json",
    "scratch_bp_trade_v2_best.json",
    "scratch_general_bp_lns_io_best.json",
    "scratch_general_v2_bp_trade_io_best.json",
    "scratch_general_v2_cpsat_trade_io_best.json",
)


def inverse_element(element):
    perm, flips = element
    inverse_perm = [0] * 7
    inverse_flips = [0] * 7
    for source, target in enumerate(perm):
        inverse_perm[target] = source
        inverse_flips[target] = flips[source]
    return tuple(inverse_perm), tuple(inverse_flips)


def state_from_spec(spec):
    graph = frozenset(
        tuple(sorted((tuple(left), tuple(right))))
        for left, right in spec["fibre_edges"]
    )
    partners = tuple(
        sorted((int(symbol), tuple(partner)) for symbol, partner in spec["coordinate_partners"].items())
    )
    return graph, partners


def normalization_element(left_label, right_label):
    perm = [None] * 7
    flips = [0] * 7
    for symbol, target_group in zip(left_label, (0, 1)):
        source_group, bit = divmod(symbol, 2)
        perm[source_group] = target_group
        flips[source_group] = bit
    for symbol, target_group in zip(right_label, (2, 3)):
        source_group, bit = divmod(symbol, 2)
        perm[source_group] = target_group
        flips[source_group] = bit
    remaining_source = [group for group in range(7) if perm[group] is None]
    for source_group, target_group in zip(remaining_source, (4, 5, 6)):
        perm[source_group] = target_group
    assert sorted(perm) == list(range(7))
    return tuple(perm), tuple(flips)


def transform_edges(edges, element, labels, index):
    transformed = set()
    for left, right in edges:
        u = index[transform_label(labels[left], *element)]
        v = index[transform_label(labels[right], *element)]
        transformed.add((u, v) if u < v else (v, u))
    assert len(transformed) == len(edges)
    return transformed


def local_state(edges, labels, index):
    u_label = (0, 2)
    u = index[u_label]
    fibre = {(0, 2), (0, 3), (1, 2), (1, 3)}
    graph = frozenset(
        tuple(sorted((labels[left], labels[right])))
        for left, right in edges
        if labels[left] in fibre and labels[right] in fibre
    )
    neighbours = {
        right if left == u else left
        for left, right in edges
        if left == u or right == u
    }
    partners = []
    for symbol in u_label:
        matches = [labels[vertex] for vertex in neighbours if symbol in labels[vertex]]
        assert len(matches) == 1
        partners.append((symbol, matches[0]))
    return graph, tuple(sorted(partners))


def layer_metrics(edges, labels):
    adjacency = [set() for _ in range(84)]
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    energy = bad = 0
    for support in itertools.combinations(range(7), 2):
        fibre = [
            u for u, label in enumerate(labels)
            if tuple(sorted(symbol // 2 for symbol in label)) == support
        ]
        for u, v in itertools.combinations(fibre, 2):
            target = 2 - len(set(labels[u]).intersection(labels[v]))
            residual = (
                len(adjacency[u].intersection(adjacency[v]))
                + int(v in adjacency[u])
                - target
            )
            energy += residual * residual
            bad += residual != 0
    return energy, bad


def read_outer_edges(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    edges = {
        (left - 16, right - 16)
        for left, right in data["edges"]
        if left >= 16 and right >= 16
    }
    assert len(edges) == 504
    return edges


def build_bank():
    labels, index, variables, edge = coordinates()
    specs, coverage = make_specs()
    by_name = {spec["branch"]: spec for spec in specs}
    group = residual_group(frozenset())

    # Map every one of the 784 labelled states to an orbit representative and
    # an explicit element carrying it to that representative.
    lookup = {}
    for spec in specs:
        representative = state_from_spec(spec)
        for element in group:
            state = transform_state(representative, element)
            lookup[state] = (spec["branch"], inverse_element(element))
    assert len(lookup) == 784

    best = {}
    seed_audit = []
    for seed_path in SEED_FILES:
        original = read_outer_edges(seed_path)
        energy, bad = layer_metrics(original, labels)
        seed_audit.append(
            {"source": seed_path, "outer_edges": len(original), "layer_energy": energy, "layer_bad_pairs": bad}
        )
        for left, right in original:
            left_support = {symbol // 2 for symbol in labels[left]}
            right_support = {symbol // 2 for symbol in labels[right]}
            if left_support.intersection(right_support):
                continue
            for first, second in ((left, right), (right, left)):
                normalized = transform_edges(
                    original,
                    normalization_element(labels[first], labels[second]),
                    labels,
                    index,
                )
                state = local_state(normalized, labels, index)
                branch, to_representative = lookup[state]
                aligned = transform_edges(normalized, to_representative, labels, index)
                positive = {variables[pair] for pair in aligned}
                assumptions = by_name[branch]["assumptions"]
                assert all((literal > 0) == (abs(literal) in positive) for literal in assumptions)
                candidate = {
                    "branch": branch,
                    "source": seed_path,
                    "source_oriented_edge_labels": [list(labels[first]), list(labels[second])],
                    "layer_energy": energy,
                    "layer_bad_pairs": bad,
                    "positive_edge_variables": sorted(positive),
                }
                key = (energy, bad, seed_path)
                if branch not in best or key < best[branch][0]:
                    best[branch] = (key, candidate)

    bank = [best[name][1] for name in sorted(best)]
    result = {
        "model": "symmetry-aligned exact-BP phase bank",
        "phase_only_not_constraints": True,
        "safe_branch_coverage": coverage,
        "seed_audit": seed_audit,
        "covered_branch_count": len(bank),
        "uncovered_branch_count": len(specs) - len(bank),
        "covered_branches": [row["branch"] for row in bank],
        "bank": bank,
    }
    BANK_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def full_phases(positive_edges):
    """Recreate full-AND IDs exactly as the CNF builder assigned them."""
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    labels, _index, variables, edge = coordinates()
    positive = set(positive_edges)
    phases = [variable if variable in positive else -variable for variable in range(1, 3487)]
    pool = IDPool(start_from=3487)
    for support in itertools.combinations(range(7), 2):
        fibre = [
            u for u, label in enumerate(labels)
            if tuple(sorted(symbol // 2 for symbol in label)) == support
        ]
        for u, v in itertools.combinations(fibre, 2):
            terms = [edge(u, v)]
            for w in range(84):
                if w in (u, v):
                    continue
                z = pool.id(("and", u, v, w))
                value = edge(u, w) in positive and edge(v, w) in positive
                phases.append(z if value else -z)
                terms.append(z)
            target = 2 - len(set(labels[u]).intersection(labels[v]))
            CardEnc.atmost(terms, target, vpool=pool, encoding=EncType.seqcounter)
    assert pool.top == 27510
    assert len(phases) == 3486 + 10332
    return phases


def worker(worker_id, cnf_path, rows, conflict_budget, stop_event, out_queue):
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    formula = CNF(from_file=cnf_path)
    loaded = time.monotonic()
    records = []
    with Solver(name="cadical300", bootstrap_with=formula.clauses) as solver:
        previous = {"restarts": 0, "conflicts": 0, "decisions": 0, "propagations": 0}
        for row in rows:
            if stop_event.is_set():
                break
            solver.set_phases(full_phases(row["positive_edge_variables"]))
            before = time.monotonic()
            solver.conf_budget(conflict_budget)
            answer = solver.solve_limited(assumptions=row["assumptions"])
            cumulative = solver.accum_stats()
            delta = {key: cumulative.get(key, 0) - previous.get(key, 0) for key in cumulative}
            previous = cumulative
            model = solver.get_model() if answer is True else None
            records.append(
                {
                    "branch": row["branch"],
                    "seed_source": row["source"],
                    "seed_layer_energy": row["layer_energy"],
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
            "records": records,
        }
    )


def portfolio(conflict_budget, max_parallel):
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    specs = {spec["branch"]: spec for spec in make_specs()[0]}
    rows = []
    for seed in bank["bank"]:
        row = dict(seed)
        row["assumptions"] = specs[row["branch"]]["assumptions"]
        rows.append(row)
    assignments = [rows[offset::max_parallel] for offset in range(max_parallel)]
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

    records = [record for worker_result in worker_results for record in worker_result["records"]]
    verified = None
    for record in records:
        if record["status"] != "SAT":
            continue
        checked = verify_layer(set(record["positive_edge_variables"]))
        record["verification"] = {key: value for key, value in checked.items() if key != "edges"}
        if checked["ok"] and verified is None:
            verified = checked
            SOLUTION_PATH.write_text(json.dumps(checked, indent=2) + "\n", encoding="utf-8")
    result = {
        "model": "exact fibre layer with symmetry-aligned BP phases",
        "phase_only_not_constraints": True,
        "solver": "CaDiCaL 3.0 via PySAT persistent workers",
        "conflict_budget_per_covered_branch": conflict_budget,
        "max_parallel": max_parallel,
        "covered_branch_count": len(rows),
        "status": "SAT" if verified is not None else "UNKNOWN",
        "counts": {
            status: sum(record["status"] == status for record in records)
            for status in ("SAT", "UNSAT", "UNKNOWN")
        },
        "workers": worker_results,
        "records": records,
    }
    PORTFOLIO_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-bank", action="store_true")
    parser.add_argument("--conflicts", type=int, default=0)
    parser.add_argument("--max-parallel", type=int, default=4)
    args = parser.parse_args()
    if args.build_bank:
        result = build_bank()
        print(json.dumps({"covered": result["covered_branch_count"]}), flush=True)
    if args.conflicts > 0:
        result = portfolio(args.conflicts, args.max_parallel)
        print(json.dumps({"status": result["status"], "counts": result["counts"]}), flush=True)
    if not (args.build_bank or args.conflicts > 0):
        parser.error("select an action")


if __name__ == "__main__":
    mp.freeze_support()
    main()
