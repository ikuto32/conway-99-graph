"""Exact unrestricted-rooted SAT portfolio for the E0=80 fibre branch.

The rigorous compression audit leaves 17 C4 fibres and four P4 fibres.  The
exceptional supports form a group-cycle, normalized here to
(01,12,23,30).  This script regenerates all 128 locally viable induced
16-vertex graphs, quotients them by the full effective residual scaffold
group D8 semidirect C2^4, and applies one representative per orbit as
assumptions to scratch_general_exact.cnf.

The base CNF remains the complete unrestricted rooted model.  Therefore an
UNSAT result for every audited orbit representative eliminates E0=80; an
UNKNOWN result makes no claim.  This script never writes submission.txt.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import queue
import time
from pathlib import Path

from scratch_general_e80_local_audit import (
    ADJACENT,
    LABELS as LOCAL_LABELS,
    OPPOSITE,
    SUPPORTS,
    add_matching,
    fibre_data,
    necessary_checks,
)
from scratch_general_exact_sat import CNF_PATH, coordinates, verify, worker


RESULT_PATH = Path("scratch_general_e80_exact_portfolio.json")
BUILD_PATH = Path("scratch_general_e80_exact_build.json")
EXCEPTIONAL_SUPPORTS = frozenset(tuple(sorted(support)) for support in SUPPORTS)


def survivor_graphs():
    graphs = set()
    descriptors = {}
    for orientations in itertools.product(range(4), repeat=4):
        base_edges = set()
        endpoints = []
        centres = []
        for fibre, missing in enumerate(orientations):
            local_edges, local_endpoints, local_centres = fibre_data(fibre, missing)
            base_edges |= local_edges
            endpoints.append(local_endpoints)
            centres.append(local_centres)
        for matching_bits in itertools.product((0, 1), repeat=6):
            edges = set(base_edges)
            for bit, (left, right) in zip(matching_bits[:4], ADJACENT):
                add_matching(edges, endpoints[left], endpoints[right], bit)
            for bit, (left, right) in zip(matching_bits[4:], OPPOSITE):
                add_matching(edges, centres[left], centres[right], bit)
            ok, _reason = necessary_checks(edges)
            if not ok:
                continue
            graph = frozenset(edges)
            graphs.add(graph)
            descriptors.setdefault(
                graph,
                {"orientations": orientations, "matching_bits": matching_bits},
            )
    assert len(graphs) == 128
    return graphs, descriptors


def residual_transforms():
    cycle_edges = EXCEPTIONAL_SUPPORTS
    group_permutations = []
    for image in itertools.permutations(range(4)):
        transformed = {
            tuple(sorted((image[g], image[h]))) for g, h in cycle_edges
        }
        if transformed == cycle_edges:
            group_permutations.append(image)
    assert len(group_permutations) == 8

    transforms = []
    label_index = {label: i for i, label in enumerate(LOCAL_LABELS)}
    for permutation in group_permutations:
        for flips in itertools.product((0, 1), repeat=4):
            vertex_image = []
            for label in LOCAL_LABELS:
                changed = []
                for symbol in label:
                    group, bit = divmod(symbol, 2)
                    changed.append(2 * permutation[group] + (bit ^ flips[group]))
                vertex_image.append(label_index[tuple(sorted(changed))])
            transforms.append(tuple(vertex_image))
    assert len(set(transforms)) == 128
    return tuple(sorted(set(transforms)))


def transform_graph(graph, transform):
    return frozenset(
        tuple(sorted((transform[u], transform[v]))) for u, v in graph
    )


def graph_orbits(graphs):
    transforms = residual_transforms()
    unseen = set(graphs)
    orbits = []
    while unseen:
        representative = min(unseen, key=lambda graph: tuple(sorted(graph)))
        orbit = {transform_graph(representative, transform) for transform in transforms}
        assert orbit <= graphs
        unseen -= orbit
        orbits.append((representative, orbit))
    assert set().union(*(orbit for _representative, orbit in orbits)) == graphs
    return orbits, transforms


def global_assumptions(local_graph):
    labels, index, variables, edge = coordinates()
    local_global = [index[label] for label in LOCAL_LABELS]
    local_pairs = {
        tuple(sorted((local_global[u], local_global[v]))): (u, v)
        for u, v in itertools.combinations(range(16), 2)
    }
    units = []

    # Completely specify the induced graph on the four exceptional fibres.
    for global_pair, local_pair in local_pairs.items():
        identifier = edge(*global_pair)
        units.append(identifier if tuple(sorted(local_pair)) in local_graph else -identifier)

    # Every other fibre is exactly C4: all Hamming-one sides and no diagonals.
    for support in itertools.combinations(range(7), 2):
        if support in EXCEPTIONAL_SUPPORTS:
            continue
        fibre = [
            index[tuple(sorted((2 * support[0] + a, 2 * support[1] + b)))]
            for a, b in itertools.product((0, 1), repeat=2)
        ]
        bits = tuple(itertools.product((0, 1), repeat=2))
        for u, v in itertools.combinations(range(4), 2):
            identifier = edge(fibre[u], fibre[v])
            side = sum(bits[u][i] != bits[v][i] for i in (0, 1)) == 1
            units.append(identifier if side else -identifier)

    assert len(units) == 120 + 17 * 6
    assert len({abs(unit) for unit in units}) == len(units)
    return units


def build():
    graphs, descriptors = survivor_graphs()
    orbits, transforms = graph_orbits(graphs)
    rows = []
    covered = set()
    for number, (representative, orbit) in enumerate(orbits):
        covered |= orbit
        rows.append(
            {
                "branch": f"e80_o{number:02d}",
                "orbit_size": len(orbit),
                "descriptor": descriptors[representative],
                "local_edges": sorted(representative),
                "assumptions": global_assumptions(representative),
            }
        )
    assert covered == graphs and sum(row["orbit_size"] for row in rows) == 128
    result = {
        "model": "exact E0=80 branch of unrestricted rooted CNF",
        "base_cnf": str(CNF_PATH),
        "normalized_exceptional_supports": sorted(EXCEPTIONAL_SUPPORTS),
        "raw_local_survivors": len(graphs),
        "effective_residual_group_size": len(transforms),
        "orbit_count": len(rows),
        "orbit_sizes": [row["orbit_size"] for row in rows],
        "coverage_exact": True,
        "assumptions_per_branch": len(rows[0]["assumptions"]),
        "branches": rows,
    }
    BUILD_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def solve(seconds, max_parallel):
    meta = build()
    context = mp.get_context("spawn")
    records = {}
    verified = None
    branches = meta["branches"]
    for offset in range(0, len(branches), max_parallel):
        batch = branches[offset : offset + max_parallel]
        out_queue = context.Queue()
        processes = {}
        for row in batch:
            name = row["branch"]
            process = context.Process(
                target=worker,
                args=(name, str(CNF_PATH.resolve()), row["assumptions"], out_queue),
                name=name,
            )
            process.start()
            processes[name] = process
        deadline = time.monotonic() + seconds
        while not all(name in records for name in processes):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                record = out_queue.get(timeout=min(1.0, remaining))
            except queue.Empty:
                continue
            records[record["branch"]] = record
            if record["status"] == "SAT":
                verified = verify(set(record["positive_edge_variables"]))
                record["verification"] = {k: v for k, v in verified.items() if k != "edges"}
                break
        for name, process in processes.items():
            if process.is_alive():
                process.terminate()
                process.join(10)
            else:
                process.join()
            records.setdefault(
                name,
                {
                    "branch": name,
                    "status": "UNKNOWN",
                    "wall_limit_seconds": seconds,
                    "exit_code_after_termination": process.exitcode,
                },
            )
        if verified and verified.get("ok"):
            break

    for row in branches:
        records.setdefault(row["branch"], {"branch": row["branch"], "status": "NOT_RUN_AFTER_SAT"})
    ordered = [records[row["branch"]] for row in branches]
    status = (
        "SAT" if verified and verified.get("ok")
        else "UNSAT" if all(row["status"] == "UNSAT" for row in ordered)
        else "UNKNOWN"
    )
    result = {
        "model": meta["model"],
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "seconds_per_parallel_batch": seconds,
        "max_parallel": max_parallel,
        "coverage_exact": meta["coverage_exact"],
        "orbit_count": meta["orbit_count"],
        "status": status,
        "records": ordered,
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("--seconds", type=float, default=0.0)
    parser.add_argument("--max-parallel", type=int, default=4)
    args = parser.parse_args()
    if args.seconds > 0:
        result = solve(args.seconds, min(4, max(1, args.max_parallel)))
        print(json.dumps({
            "status": result["status"],
            "counts": {
                status: sum(row["status"] == status for row in result["records"])
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
        }), flush=True)
    else:
        meta = build()
        print(json.dumps({
            "raw_local_survivors": meta["raw_local_survivors"],
            "effective_residual_group_size": meta["effective_residual_group_size"],
            "orbit_count": meta["orbit_count"],
            "orbit_sizes": meta["orbit_sizes"],
            "assumptions_per_branch": meta["assumptions_per_branch"],
        }), flush=True)


if __name__ == "__main__":
    mp.freeze_support()
    main()
