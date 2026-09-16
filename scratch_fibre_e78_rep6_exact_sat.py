"""Exact SAT lift of the fixed E0=78 K2,3/orbit-3 representative-6 branch.

The rooted 99-vertex scaffold is fixed.  Every outer edge between supports
that overlap is fixed by the audited local representative; the only primary
variables are the 1,680 edges between disjoint two-group supports.  BP and
all 3,486 outer-pair equations are imposed as *equalities*.  Every nonlinear
wedge gets a full Tseitin AND equivalence.

This is one labelled local subbranch, not an exhaustive E0=78 search.  A SAT
answer is expanded and checked on all 4,851 graph pairs.  This script never
writes submission.txt.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
import multiprocessing as mp
import queue
import time
from pathlib import Path


PREFIX = "scratch_fibre_e78_rep6_exact"
CNF_PATH = Path(f"{PREFIX}.cnf")
BUILD_PATH = Path(f"{PREFIX}_build.json")
MAP_PATH = Path(f"{PREFIX}_map.json")
PORTFOLIO_PATH = Path(f"{PREFIX}_portfolio.json")
SOLUTION_PATH = Path(f"{PREFIX}_solution.json")
PROOF_PATH = Path(f"{PREFIX}_unsat.drat")
DEFAULT_SEED = Path("scratch_root_e78_k23_rep6_energy_best.json")
LOCAL_REPS = Path("scratch_general_e78_local_reps.json")


def canon(u: int, v: int) -> tuple[int, int]:
    assert u != v
    return (u, v) if u < v else (v, u)


def coordinates() -> tuple[list[tuple[int, int]], dict[tuple[int, int], int]]:
    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    index = {label: u for u, label in enumerate(labels)}
    assert len(labels) == len(index) == 84
    return labels, index


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_fixed_structure(seed_path: Path) -> dict[str, object]:
    labels, _index = coordinates()
    supports = [tuple(sorted((a // 2, b // 2))) for a, b in labels]
    all_supports = tuple(itertools.combinations(range(7), 2))
    fibres = {
        support: tuple(u for u, value in enumerate(supports) if value == support)
        for support in all_supports
    }
    assert all(len(fibre) == 4 for fibre in fibres.values())

    reps_source = json.loads(LOCAL_REPS.read_text(encoding="utf-8"))
    record = next(
        row
        for row in reps_source["records"]
        if row["support_form"] == "K2,3" and row["compression_orbit_index"] == 3
    )
    rep = next(row for row in record["representatives"] if row["representative_id"] == 6)
    exceptional = {tuple(item) for item in record["supports_in_fibre_order"]}
    local_present = {
        canon(*pair) for pair in rep["present_edges_outer_indices_zero_based"]
    }
    assert len(exceptional) == 6
    assert len(local_present) == 30
    assert all(set(supports[u]).intersection(supports[v]) for u, v in local_present)

    ordinary = set(all_supports) - exceptional
    expected_fixed_present: set[tuple[int, int]] = set()
    fixed_absent: set[tuple[int, int]] = set()
    variable_pairs: list[tuple[int, int]] = []
    for u, v in itertools.combinations(range(84), 2):
        pair = (u, v)
        if set(supports[u]).isdisjoint(supports[v]):
            variable_pairs.append(pair)
            continue
        if supports[u] == supports[v] and supports[u] in ordinary:
            present = len(set(labels[u]).intersection(labels[v])) == 1
        else:
            present = pair in local_present
        (expected_fixed_present if present else fixed_absent).add(pair)

    assert len(variable_pairs) == 1680
    assert len(expected_fixed_present) == 90
    assert len(expected_fixed_present) + len(fixed_absent) + len(variable_pairs) == 3486

    seed_source = json.loads(seed_path.read_text(encoding="utf-8"))
    graph_edges = {canon(int(u), int(v)) for u, v in seed_source["edges"]}
    assert len(graph_edges) == len(seed_source["edges"]) == 693
    seed_outer = {
        (u - 16, v - 16)
        for u, v in graph_edges
        if 16 <= u < v <= 99
    }
    observed_fixed_present = {
        pair
        for pair in seed_outer
        if not set(supports[pair[0]]).isdisjoint(supports[pair[1]])
    }
    assert observed_fixed_present == expected_fixed_present
    seed_variable_present = seed_outer.intersection(variable_pairs)
    assert len(seed_outer) == 504
    assert len(seed_variable_present) == 414
    assert seed_source.get("orbit") == 3
    assert seed_source.get("local_representative") == 6
    assert {tuple(x) for x in seed_source["exceptional_supports"]} == exceptional

    return {
        "labels": labels,
        "supports": supports,
        "fibres": fibres,
        "all_supports": all_supports,
        "exceptional": exceptional,
        "ordinary": ordinary,
        "fixed_present": expected_fixed_present,
        "fixed_absent": fixed_absent,
        "variable_pairs": variable_pairs,
        "seed_variable_present": seed_variable_present,
        "seed_source": seed_source,
        "representative": rep,
    }


def direct_exact_one(clauses: list[list[int]], lits: list[int]) -> None:
    assert len(lits) == 4 and len(set(lits)) == 4
    clauses.append(lits[:])
    clauses.extend([-a, -b] for a, b in itertools.combinations(lits, 2))


def build_cnf(seed_path: Path) -> dict[str, object]:
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    data = load_fixed_structure(seed_path)
    labels = data["labels"]
    supports = data["supports"]
    fibres = data["fibres"]
    all_supports = data["all_supports"]
    exceptional = data["exceptional"]
    ordinary = data["ordinary"]
    fixed_present = data["fixed_present"]
    variable_pairs = data["variable_pairs"]
    seed_present = data["seed_variable_present"]

    pool = IDPool(start_from=1)
    edge_variables = {
        pair: pool.id(("edge", pair[0], pair[1])) for pair in variable_pairs
    }
    assert pool.top == 1680

    def edge(u: int, v: int) -> bool | int:
        pair = canon(u, v)
        if pair in edge_variables:
            return edge_variables[pair]
        return pair in fixed_present

    clauses: list[list[int]] = []
    exact_stats: dict[str, Counter] = {
        "bp": Counter(),
        "outer_pair": Counter(),
    }

    def add_exact(expressions: list[bool | int], wanted: int, family: str) -> None:
        fixed = sum(value is True for value in expressions)
        lits = [value for value in expressions if type(value) is int]
        assert not any(value is not True and value is not False and type(value) is not int for value in expressions)
        assert len(lits) == len(set(lits))
        target = wanted - fixed
        exact_stats[family][f"wanted_{wanted}"] += 1
        exact_stats[family][f"fixed_true_{fixed}"] += 1
        exact_stats[family][f"remaining_target_{target}"] += 1
        exact_stats[family][f"remaining_lits_{len(lits)}"] += 1
        if target < 0 or target > len(lits):
            clauses.append([])
        elif target == 0:
            clauses.extend([[-literal] for literal in lits])
        elif target == len(lits):
            clauses.extend([[literal] for literal in lits])
        else:
            clauses.extend(
                CardEnc.equals(
                    lits=lits,
                    bound=target,
                    vpool=pool,
                    encoding=EncType.seqcounter,
                ).clauses
            )

    # Safe redundant block consequences.  A C4 fibre has no outside vertex
    # adjacent to two of its vertices.  The BP/degree sums then give a
    # permutation between two disjoint C4 fibres and exactly one C4 neighbour
    # for each vertex of a disjoint P4 fibre.  The converse row constraint in
    # a C4--P4 block is intentionally NOT added.
    block_histogram = Counter()
    redundant_exact_one = 0
    for A, B in itertools.combinations(all_supports, 2):
        if not set(A).isdisjoint(B):
            continue
        if A in ordinary and B in ordinary:
            block_histogram["C4-C4"] += 1
            for u in fibres[A]:
                direct_exact_one(clauses, [edge_variables[canon(u, v)] for v in fibres[B]])
                redundant_exact_one += 1
            for v in fibres[B]:
                direct_exact_one(clauses, [edge_variables[canon(u, v)] for u in fibres[A]])
                redundant_exact_one += 1
        elif (A in ordinary) != (B in ordinary):
            block_histogram["C4-P4"] += 1
            high, low = (A, B) if A in ordinary else (B, A)
            for v in fibres[low]:
                direct_exact_one(clauses, [edge_variables[canon(u, v)] for u in fibres[high]])
                redundant_exact_one += 1
        else:
            block_histogram["P4-P4"] += 1
    assert block_histogram == Counter({"C4-C4": 51, "C4-P4": 48, "P4-P4": 6})
    assert redundant_exact_one == 600

    # Assert independently that the phase seed obeys every redundancy.
    for A, B in itertools.combinations(all_supports, 2):
        if not set(A).isdisjoint(B):
            continue
        if A in ordinary and B in ordinary:
            assert all(sum(canon(u, v) in seed_present for v in fibres[B]) == 1 for u in fibres[A])
            assert all(sum(canon(u, v) in seed_present for u in fibres[A]) == 1 for v in fibres[B])
        elif (A in ordinary) != (B in ordinary):
            high, low = (A, B) if A in ordinary else (B, A)
            assert all(sum(canon(u, v) in seed_present for u in fibres[high]) == 1 for v in fibres[low])

    # Rooted incidence equations BP=PA0.
    bp_target_histogram = Counter()
    for u, label in enumerate(labels):
        own_groups = {symbol // 2 for symbol in label}
        for symbol in range(14):
            expressions = [
                edge(u, v)
                for v, other in enumerate(labels)
                if u != v and symbol in other
            ]
            target = 1 if symbol // 2 in own_groups else 2
            bp_target_histogram[target] += 1
            add_exact(expressions, target, "bp")
    assert bp_target_histogram == Counter({2: 840, 1: 336})

    seed_edge_phases = [
        identifier if pair in seed_present else -identifier
        for pair, identifier in edge_variables.items()
    ]
    seed_product_phases: list[int] = []
    product_variables = 0
    direct_product_terms = 0
    constant_product_terms = 0
    omitted_false_products = 0
    target_histogram = Counter()

    def seed_value(expression: bool | int) -> bool:
        if expression is True or expression is False:
            return expression
        pair = variable_by_id[expression]
        return pair in seed_present

    variable_by_id = {identifier: pair for pair, identifier in edge_variables.items()}
    assert len(variable_by_id) == 1680

    # Every outer-pair SRG equation, including the 126 same-support pairs.
    for u, v in itertools.combinations(range(84), 2):
        expressions: list[bool | int] = [edge(u, v)]
        for w in range(84):
            if w in (u, v):
                continue
            a, b = edge(u, w), edge(v, w)
            if a is False or b is False:
                omitted_false_products += 1
            elif a is True and b is True:
                expressions.append(True)
                constant_product_terms += 1
            elif a is True:
                expressions.append(b)
                direct_product_terms += 1
            elif b is True:
                expressions.append(a)
                direct_product_terms += 1
            else:
                assert type(a) is int and type(b) is int and a != b
                z = pool.id(("and", u, v, w))
                clauses.extend(([-a, -b, z], [a, -z], [b, -z]))
                expressions.append(z)
                value = seed_value(a) and seed_value(b)
                seed_product_phases.append(z if value else -z)
                product_variables += 1
        target = 2 - len(set(labels[u]).intersection(labels[v]))
        target_histogram[target] += 1
        add_exact(expressions, target, "outer_pair")
    assert target_histogram == Counter({2: 2562, 1: 924})
    assert product_variables == len(seed_product_phases)

    # Seed is a valid BP+same-support layer assignment but is not expected to
    # satisfy cross-support equations.  Check the first half directly here.
    seed_bp_bad = 0
    for u, label in enumerate(labels):
        own_groups = {symbol // 2 for symbol in label}
        for symbol in range(14):
            value = sum(
                seed_value(edge(u, v))
                for v, other in enumerate(labels)
                if u != v and symbol in other
            )
            target = 1 if symbol // 2 in own_groups else 2
            seed_bp_bad += value != target
    seed_same_support_bad = 0
    for A in all_supports:
        for u, v in itertools.combinations(fibres[A], 2):
            value = int(seed_value(edge(u, v)))
            value += sum(
                seed_value(edge(u, w)) and seed_value(edge(v, w))
                for w in range(84)
                if w not in (u, v)
            )
            target = 2 - len(set(labels[u]).intersection(labels[v]))
            seed_same_support_bad += value != target
    assert seed_bp_bad == seed_same_support_bad == 0

    with CNF_PATH.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {pool.top} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")

    map_data = {
        "edge_variables": [
            [identifier, u, v]
            for (u, v), identifier in sorted(edge_variables.items(), key=lambda row: row[1])
        ],
        "fixed_present_outer_edges": [list(pair) for pair in sorted(fixed_present)],
        "seed_edge_phases": seed_edge_phases,
        "seed_product_phases": seed_product_phases,
    }
    MAP_PATH.write_text(json.dumps(map_data, separators=(",", ":")) + "\n", encoding="utf-8")

    meta = {
        "model": "full exact fixed E0=78 K2,3 orbit3 representative6 rooted branch",
        "coverage_boundary": "one audited labelled local representative subbranch only",
        "seed_path": str(seed_path),
        "seed_sha256": file_sha256(seed_path),
        "seed_reported_energy": data["seed_source"].get("energy"),
        "seed_reported_bad_pairs": data["seed_source"].get("bad_pairs"),
        "local_representatives_path": str(LOCAL_REPS),
        "local_representatives_sha256": file_sha256(LOCAL_REPS),
        "compression_orbit_index": 3,
        "local_representative": 6,
        "representative_orbit_size": data["representative"]["orbit_size"],
        "exceptional_supports": [list(x) for x in sorted(exceptional)],
        "ordinary_C4_fibres": len(ordinary),
        "exceptional_P4_fibres": len(exceptional),
        "fixed_present_outer_edges": len(fixed_present),
        "fixed_absent_outer_edges": len(data["fixed_absent"]),
        "variable_disjoint_support_edges": len(edge_variables),
        "seed_present_variable_edges": len(seed_present),
        "redundant_block_histogram": dict(sorted(block_histogram.items())),
        "redundant_exact_one_constraints": redundant_exact_one,
        "unsafe_C4_to_P4_row_constraints_added": False,
        "bp_equations": 1176,
        "bp_target_histogram": dict(sorted(bp_target_histogram.items())),
        "outer_pair_equations": 3486,
        "outer_pair_target_histogram": dict(sorted(target_histogram.items())),
        "same_support_pair_equations_included": 126,
        "cross_support_pair_equations_included": 3360,
        "every_pair_constraint_is_equality": True,
        "full_tseitin_AND_equivalences": True,
        "product_variables": product_variables,
        "direct_product_terms": direct_product_terms,
        "constant_product_terms": constant_product_terms,
        "omitted_false_products": omitted_false_products,
        "seed_BP_bad": seed_bp_bad,
        "seed_same_support_bad": seed_same_support_bad,
        "primary_plus_aux_variables": pool.top,
        "clauses": len(clauses),
        "exact_constraint_stats": {
            family: dict(sorted(stats.items())) for family, stats in exact_stats.items()
        },
        "cnf_path": str(CNF_PATH),
        "cnf_sha256": file_sha256(CNF_PATH),
        "map_path": str(MAP_PATH),
        "map_sha256": file_sha256(MAP_PATH),
    }
    BUILD_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def phase_for_strategy(strategy: str, map_data: dict[str, object]) -> list[int]:
    edges = list(map_data["seed_edge_phases"])
    products = list(map_data["seed_product_phases"])
    if strategy == "seed_full":
        return edges + products
    if strategy == "seed_edges":
        return edges
    if strategy == "seed_positive":
        return [lit for lit in edges + products if lit > 0]
    if strategy == "default":
        return []
    raise ValueError(strategy)


def solver_worker(
    worker_id: int,
    solver_name: str,
    strategy: str,
    with_proof: bool,
    cnf_path: str,
    map_path: str,
    out_queue,
) -> None:
    try:
        from pysat.formula import CNF
        from pysat.solvers import Solver

        started = time.monotonic()
        formula = CNF(from_file=cnf_path)
        loaded = time.monotonic()
        map_data = json.loads(Path(map_path).read_text(encoding="utf-8"))
        phases = phase_for_strategy(strategy, map_data)
        with Solver(
            name=solver_name,
            bootstrap_with=formula.clauses,
            with_proof=with_proof,
        ) as solver:
            del formula
            if phases:
                solver.set_phases(phases)
            solved_started = time.monotonic()
            answer = solver.solve()
            solved = time.monotonic()
            model = solver.get_model() if answer else None
            stats = solver.accum_stats()
            proof_record = None
            if answer is False and with_proof:
                proof = solver.get_proof()
                if proof:
                    PROOF_PATH.write_text("\n".join(proof) + "\n", encoding="ascii")
                    proof_record = {
                        "path": str(PROOF_PATH),
                        "lines": len(proof),
                        "sha256": file_sha256(PROOF_PATH),
                        "independently_checked": False,
                    }
        edge_ids = {row[0] for row in map_data["edge_variables"]}
        positive_edge_ids = sorted(lit for lit in model or [] if lit > 0 and lit in edge_ids)
        out_queue.put({
            "worker_id": worker_id,
            "solver": solver_name,
            "phase_strategy": strategy,
            "proof_enabled": with_proof,
            "status": "SAT" if answer is True else "UNSAT",
            "load_seconds": round(loaded - started, 3),
            "solve_seconds": round(solved - solved_started, 3),
            "wall_seconds": round(solved - started, 3),
            "stats": stats,
            "proof": proof_record,
            "positive_edge_variable_ids": positive_edge_ids,
        })
    except BaseException as error:
        out_queue.put({
            "worker_id": worker_id,
            "solver": solver_name,
            "phase_strategy": strategy,
            "status": "ERROR",
            "error_type": type(error).__name__,
            "error": str(error),
        })


def expand_and_verify(positive_edge_ids: list[int]) -> dict[str, object]:
    """Expand a SAT model and independently check every 99-vertex pair."""
    labels, _index = coordinates()
    map_data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    selected_ids = set(positive_edge_ids)
    outer_edges = {tuple(row) for row in map_data["fixed_present_outer_edges"]}
    for identifier, u, v in map_data["edge_variables"]:
        if identifier in selected_ids:
            outer_edges.add((u, v))

    adjacency = [set() for _ in range(99)]

    def add(u: int, v: int) -> None:
        assert u != v and v not in adjacency[u]
        adjacency[u].add(v)
        adjacency[v].add(u)

    for symbol in range(14):
        add(0, 1 + symbol)
    for group in range(7):
        add(1 + 2 * group, 2 + 2 * group)
    for u, (a, b) in enumerate(labels):
        add(15 + u, 1 + a)
        add(15 + u, 1 + b)
    for u, v in outer_edges:
        add(15 + u, 15 + v)

    degree_histogram = Counter(len(row) for row in adjacency)
    residual_histogram = Counter()
    energy = 0
    bad_pairs = []
    for u, v in itertools.combinations(range(99), 2):
        common = len(adjacency[u].intersection(adjacency[v]))
        residual = common + int(v in adjacency[u]) - 2
        residual_histogram[residual] += 1
        energy += residual * residual
        if residual:
            bad_pairs.append([u + 1, v + 1, common, int(v in adjacency[u]), residual])
    graph_edges = [
        [u + 1, v + 1]
        for u in range(99)
        for v in adjacency[u]
        if u < v
    ]
    fixed_structure = load_fixed_structure(Path(json.loads(BUILD_PATH.read_text(encoding="utf-8"))["seed_path"]))
    observed_outer = {(u - 16, v - 16) for u, v in map(tuple, graph_edges) if u >= 16}
    observed_fixed = {
        pair
        for pair in observed_outer
        if not set(fixed_structure["supports"][pair[0]]).isdisjoint(
            fixed_structure["supports"][pair[1]]
        )
    }
    structure_ok = observed_fixed == fixed_structure["fixed_present"]
    ok = (
        len(graph_edges) == 693
        and degree_histogram == Counter({14: 99})
        and not bad_pairs
        and energy == 0
        and structure_ok
    )
    canonical = "".join(f"{u},{v}\n" for u, v in graph_edges).encode("ascii")
    return {
        "ok": ok,
        "edge_count": len(graph_edges),
        "degree_histogram": dict(sorted(degree_histogram.items())),
        "pairs_checked": sum(residual_histogram.values()),
        "residual_histogram": dict(sorted(residual_histogram.items())),
        "energy": energy,
        "bad_pair_count": len(bad_pairs),
        "bad_pair_examples": bad_pairs[:20],
        "fixed_rep6_structure_ok": structure_ok,
        "canonical_edge_sha256": hashlib.sha256(canonical).hexdigest().upper(),
        "edges": graph_edges,
    }


def run_portfolio(seconds: float, max_parallel: int) -> dict[str, object]:
    strategies = [
        # The edge-only phase was fastest in the first portfolio.  Keep the
        # corresponding CaDiCaL 1.9.5 run proof-enabled so a repeated UNSAT
        # result emits a DRAT trace.
        ("cadical195", "seed_edges", True),
        ("cadical300", "seed_edges", False),
        ("cadical195", "seed_full", False),
        ("cadical300", "default", False),
    ][:max_parallel]
    context = mp.get_context("spawn")
    out_queue = context.Queue()
    processes = {}
    for worker_id, (solver_name, strategy, with_proof) in enumerate(strategies):
        process = context.Process(
            target=solver_worker,
            args=(
                worker_id,
                solver_name,
                strategy,
                with_proof,
                str(CNF_PATH.resolve()),
                str(MAP_PATH.resolve()),
                out_queue,
            ),
            name=f"e78-rep6-{worker_id}",
        )
        process.start()
        processes[worker_id] = process

    records: dict[int, dict[str, object]] = {}
    deadline = time.monotonic() + seconds
    terminal = None
    while len(records) < len(processes):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            record = out_queue.get(timeout=min(1.0, remaining))
        except queue.Empty:
            continue
        worker_id = int(record["worker_id"])
        records[worker_id] = record
        if record["status"] in ("SAT", "UNSAT"):
            terminal = record["status"]
            break

    for worker_id, process in processes.items():
        if process.is_alive():
            process.terminate()
            process.join(10)
        else:
            process.join()
        records.setdefault(worker_id, {
            "worker_id": worker_id,
            "solver": strategies[worker_id][0],
            "phase_strategy": strategies[worker_id][1],
            "proof_enabled": strategies[worker_id][2],
            "status": "UNKNOWN",
            "wall_limit_seconds": seconds,
            "exit_code_after_termination": process.exitcode,
        })

    ordered = [records[i] for i in range(len(processes))]
    verified = None
    for record in ordered:
        if record["status"] == "SAT":
            verified = expand_and_verify(record["positive_edge_variable_ids"])
            record["independent_verification"] = {
                key: value for key, value in verified.items() if key != "edges"
            }
            if verified["ok"]:
                SOLUTION_PATH.write_text(json.dumps(verified, indent=2) + "\n", encoding="utf-8")
            else:
                record["status"] = "SAT_INVALID_MODEL"
            break

    if verified is not None and verified["ok"]:
        status = "SAT"
    elif any(row["status"] == "UNSAT" for row in ordered):
        status = "UNSAT"
    else:
        status = "UNKNOWN"
    result = {
        "model": "full exact fixed E0=78 K2,3 orbit3 representative6 branch",
        "coverage_boundary": "one audited labelled local representative subbranch only",
        "status": status,
        "wall_limit_seconds": seconds,
        "max_parallel_solver_processes": len(processes),
        "terminal_solver_answer_seen": terminal,
        "cnf_path": str(CNF_PATH),
        "cnf_sha256": file_sha256(CNF_PATH),
        "build_path": str(BUILD_PATH),
        "build_sha256": file_sha256(BUILD_PATH),
        "records": ordered,
    }
    PORTFOLIO_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--seconds", type=float, default=120.0)
    parser.add_argument("--max-parallel", type=int, default=4)
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--reuse-build", action="store_true")
    args = parser.parse_args()
    if not args.reuse_build:
        meta = build_cnf(args.seed)
        print(json.dumps({
            "built": True,
            "variables": meta["primary_plus_aux_variables"],
            "clauses": meta["clauses"],
            "products": meta["product_variables"],
            "cnf_sha256": meta["cnf_sha256"],
        }), flush=True)
    if args.build_only:
        return
    result = run_portfolio(args.seconds, min(4, max(1, args.max_parallel)))
    print(json.dumps({
        "status": result["status"],
        "counts": dict(Counter(row["status"] for row in result["records"])),
        "portfolio_path": str(PORTFOLIO_PATH),
    }), flush=True)


if __name__ == "__main__":
    mp.freeze_support()
    main()
