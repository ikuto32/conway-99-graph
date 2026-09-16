"""Second-level exact SAT portfolio for the unrestricted rooted model.

This reuses scratch_general_exact.cnf.  After its safe normalization of the
disjoint-support edge u={0,2} -- v={4,6}, that edge has a unique outer common
neighbour w.  The three labels in this all-outer triangle are pairwise
symbol-disjoint.  For each of the four viable same-support patterns at u, we
enumerate (rather than guess) the residual scaffold group, compute all its
orbits on possible w, and launch one complete branch per orbit.

The orbit enumeration is mechanically checked for coverage.  No branch can
remove a labelled solution modulo the already-used scaffold automorphisms.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import queue
import time
from pathlib import Path

from scratch_general_exact_sat import (
    BRANCHES,
    BUILD_PATH,
    CNF_PATH,
    coordinates,
    verify,
    worker,
)


RESULT_PATH = Path("scratch_general_triangle_portfolio.json")
VIABLE_BASES = ("a0", "a1_complement", "a1_cross", "a2_crosses")


def transform_label(label: tuple[int, int], perm, flips) -> tuple[int, int]:
    image = []
    for symbol in label:
        group, bit = divmod(symbol, 2)
        image.append(2 * perm[group] + (bit ^ flips[group]))
    return tuple(sorted(image))


def residual_group(pattern: frozenset[tuple[int, int]]):
    u = (0, 2)
    v = (4, 6)
    elements = []
    for image_u_groups in ((0, 1), (1, 0)):
        for image_v_groups in ((2, 3), (3, 2)):
            for remaining in itertools.permutations((4, 5, 6)):
                perm = image_u_groups + image_v_groups + remaining
                for tail_flips in itertools.product((0, 1), repeat=3):
                    flips = (0, 0, 0, 0) + tail_flips
                    assert transform_label(u, perm, flips) == u
                    assert transform_label(v, perm, flips) == v
                    image_pattern = frozenset(
                        transform_label(label, perm, flips) for label in pattern
                    )
                    if image_pattern == pattern:
                        elements.append((perm, flips))
    assert elements
    return elements


def branch_specs():
    labels, index, _variables, edge = coordinates()
    u_label, v_label = (0, 2), (4, 6)
    u, v = index[u_label], index[v_label]
    x, y, complement = (0, 3), (1, 2), (1, 3)
    patterns = {
        "a0": frozenset(),
        "a1_complement": frozenset((complement,)),
        "a1_cross": frozenset((x,)),
        "a2_crosses": frozenset((x, y)),
    }
    candidates = {
        label
        for label in labels
        if set(label).isdisjoint(set(u_label).union(v_label))
    }
    assert len(candidates) == 42

    meta = json.loads(BUILD_PATH.read_text(encoding="utf-8"))
    specs = []
    coverage = {}
    for base in VIABLE_BASES:
        group = residual_group(patterns[base])
        unseen = set(candidates)
        orbits = []
        while unseen:
            seed = min(unseen)
            orbit = {transform_label(seed, perm, flips) for perm, flips in group}
            assert orbit <= candidates
            unseen -= orbit
            orbits.append(sorted(orbit))
        assert set().union(*(set(orbit) for orbit in orbits)) == candidates
        coverage[base] = {
            "residual_group_size": len(group),
            "candidate_count": len(candidates),
            "orbit_count": len(orbits),
            "orbits": orbits,
        }
        for orbit_number, orbit in enumerate(orbits):
            w_label = tuple(orbit[0])
            w = index[w_label]
            assumptions = list(meta["branch_units"][base])
            assumptions.extend((edge(u, w), edge(v, w)))
            specs.append(
                {
                    "branch": f"{base}__w{w_label[0]}_{w_label[1]}",
                    "base": base,
                    "w_label": list(w_label),
                    "orbit_size": len(orbit),
                    "assumptions": assumptions,
                }
            )
    return specs, coverage


def run(seconds: float, max_parallel: int) -> dict[str, object]:
    specs, coverage = branch_specs()
    context = mp.get_context("spawn")
    records: dict[str, dict[str, object]] = {}
    verified = None
    for offset in range(0, len(specs), max_parallel):
        batch = specs[offset : offset + max_parallel]
        out_queue = context.Queue()
        processes = {}
        for spec in batch:
            name = str(spec["branch"])
            process = context.Process(
                target=worker,
                args=(name, str(CNF_PATH.resolve()), spec["assumptions"], out_queue),
                name=f"triangle-{name}",
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
            name = str(record["branch"])
            records[name] = record
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
            if name not in records:
                records[name] = {
                    "branch": name,
                    "status": "UNKNOWN",
                    "wall_limit_seconds": seconds,
                    "exit_code_after_termination": process.exitcode,
                }
        if verified and verified["ok"]:
            break

    # Branches after an early verified SAT need no solver status.
    for spec in specs:
        name = str(spec["branch"])
        records.setdefault(name, {"branch": name, "status": "NOT_RUN_AFTER_SAT"})

    ordered = [records[str(spec["branch"])] for spec in specs]
    if verified and verified["ok"]:
        Path("scratch_general_triangle_solution.json").write_text(
            json.dumps(verified, indent=2) + "\n", encoding="utf-8"
        )
    summary = {
        "model": "exact unrestricted rooted CNF with normalized edge triangle",
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "wall_limit_seconds_per_parallel_branch": seconds,
        "max_parallel": max_parallel,
        "branches_exhaustive": True,
        "branch_count": len(specs),
        "coverage": coverage,
        "status": (
            "SAT" if any(row["status"] == "SAT" for row in ordered)
            else "UNSAT" if all(row["status"] == "UNSAT" for row in ordered)
            else "UNKNOWN"
        ),
        "records": ordered,
    }
    RESULT_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=180.0)
    parser.add_argument("--max-parallel", type=int, default=4)
    parser.add_argument("--describe", action="store_true")
    args = parser.parse_args()
    specs, coverage = branch_specs()
    print(
        json.dumps(
            {
                "branches": len(specs),
                "per_base": {base: row["orbit_count"] for base, row in coverage.items()},
                "coverage": coverage if args.describe else None,
            }
        ),
        flush=True,
    )
    if args.seconds > 0:
        result = run(args.seconds, args.max_parallel)
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "counts": {
                        status: sum(row["status"] == status for row in result["records"])
                        for status in ("SAT", "UNSAT", "UNKNOWN")
                    },
                }
            ),
            flush=True,
        )


if __name__ == "__main__":
    mp.freeze_support()
    main()
