"""Explore exact-BP graphs by the smallest incidence-circuit trades.

The 84 outer vertices are the edges of K_{2,2,...,2} on the fourteen
root-neighbour symbols.  A four-term relation

    [a,b] + [c,d] = [a,d] + [c,b]

is a circuit of the 14 by 84 symbol-incidence matrix.  Given two disjoint
circuits, the outer product of their signed incidence vectors is a
sixteen-cell trade: eight present edges can be exchanged for the other
eight while preserving every row of B P = P A_0 exactly.

This script exhaustively finds currently applicable trades and best-first
searches their connected component.  Every saved incumbent is independently
rescored on all 4,851 vertex pairs; it is never promoted to submission.txt.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import itertools
import json
import time
from pathlib import Path


N, INNER, OUTER_OFFSET, OUTER = 99, 14, 15, 84


def canon(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


LABELS = [
    pair
    for pair in itertools.combinations(range(INNER), 2)
    if pair[0] // 2 != pair[1] // 2
]
LABEL_INDEX = {label: i for i, label in enumerate(LABELS)}
assert len(LABELS) == OUTER


def scaffold() -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()
    for symbol in range(INNER):
        result.add((0, 1 + symbol))
    for group in range(7):
        result.add((1 + 2 * group, 2 + 2 * group))
    for u, (a, b) in enumerate(LABELS):
        result.add(canon(OUTER_OFFSET + u, 1 + a))
        result.add(canon(OUTER_OFFSET + u, 1 + b))
    assert len(result) == 189
    return result


SCAFFOLD = scaffold()


def incidence_circuits() -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Return every primitive four-entry +/-1 rectangle, modulo sign."""
    result: dict[
        tuple[tuple[int, int], tuple[int, int]],
        tuple[tuple[int, int], tuple[int, int]],
    ] = {}
    for left_symbols in itertools.combinations(range(INNER), 2):
        for right_symbols in itertools.combinations(range(INNER), 2):
            if left_symbols >= right_symbols:
                continue
            if any(a // 2 == b // 2 for a in left_symbols for b in right_symbols):
                continue
            a, c = left_symbols
            b, d = right_symbols
            plus = tuple(sorted((
                LABEL_INDEX[tuple(sorted((a, b)))],
                LABEL_INDEX[tuple(sorted((c, d)))],
            )))
            minus = tuple(sorted((
                LABEL_INDEX[tuple(sorted((a, d)))],
                LABEL_INDEX[tuple(sorted((c, b)))],
            )))
            if len(set(plus + minus)) != 4:
                continue
            key = min((plus, minus), (minus, plus))
            result[key] = key
    circuits = sorted(result)
    assert len(circuits) == 2121
    return circuits


CIRCUITS = incidence_circuits()
ORIENTED_CIRCUIT = {}
for circuit_index, (plus, minus) in enumerate(CIRCUITS):
    assert (plus, minus) not in ORIENTED_CIRCUIT
    assert (minus, plus) not in ORIENTED_CIRCUIT
    ORIENTED_CIRCUIT[plus, minus] = (circuit_index, plus, minus)
    ORIENTED_CIRCUIT[minus, plus] = (circuit_index, minus, plus)


def read_graph(path: str) -> set[tuple[int, int]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    edges = {canon(int(u) - 1, int(v) - 1) for u, v in payload["edges"]}
    if len(edges) != 693 or not SCAFFOLD <= edges:
        raise ValueError("input is not a 693-edge graph containing the rooted scaffold")
    mutable = {(u - OUTER_OFFSET, v - OUTER_OFFSET) for u, v in edges if u >= OUTER_OFFSET}
    if len(mutable) != 504:
        raise ValueError("input does not have exactly 504 outer edges")
    return mutable


def full_metrics(mutable: set[tuple[int, int]]) -> dict[str, object]:
    edges = SCAFFOLD | {
        (OUTER_OFFSET + u, OUTER_OFFSET + v) for u, v in mutable
    }
    adjacency = [0] * N
    degrees = [0] * N
    for u, v in edges:
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
        degrees[u] += 1
        degrees[v] += 1
    energy = io_energy = bad_pairs = 0
    residual_histogram: dict[int, int] = {}
    for u in range(N):
        for v in range(u + 1, N):
            common = (adjacency[u] & adjacency[v]).bit_count()
            residual = common + int(bool(adjacency[u] & (1 << v))) - 2
            energy += residual * residual
            if u < OUTER_OFFSET <= v:
                io_energy += residual * residual
            bad_pairs += residual != 0
            residual_histogram[residual] = residual_histogram.get(residual, 0) + 1
    return {
        "energy": energy,
        "recomputed_energy": energy,
        "io_energy": io_energy,
        "oo_energy": energy - io_energy,
        "bad_pairs": bad_pairs,
        "max_abs_residual": max(abs(r) for r in residual_histogram),
        "residual_histogram": {
            str(r): count for r, count in sorted(residual_histogram.items()) if count
        },
        "edge_count": len(edges),
        "degree_histogram": {
            str(d): degrees.count(d) for d in sorted(set(degrees))
        },
        "edges": [[u + 1, v + 1] for u, v in sorted(edges)],
    }


def state_key(mutable: set[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(mutable))


def state_digest(key: tuple[tuple[int, int], ...]) -> str:
    raw = ";".join(f"{u},{v}" for u, v in key).encode("ascii")
    return hashlib.sha256(raw).hexdigest().upper()


def local_adjacency(mutable: set[tuple[int, int]]) -> list[set[int]]:
    adjacency = [set() for _ in range(OUTER)]
    for u, v in mutable:
        adjacency[u].add(v)
        adjacency[v].add(u)
    return adjacency


def trade_edges(
    left_plus: tuple[int, int],
    left_minus: tuple[int, int],
    right_plus: tuple[int, int],
    right_minus: tuple[int, int],
) -> tuple[frozenset[tuple[int, int]], frozenset[tuple[int, int]]]:
    present = frozenset(
        canon(u, v)
        for left, right in ((left_plus, right_plus), (left_minus, right_minus))
        for u in left
        for v in right
    )
    absent = frozenset(
        canon(u, v)
        for left, right in ((left_plus, right_minus), (left_minus, right_plus))
        for u in left
        for v in right
    )
    return present, absent


def applicable_trades(mutable: set[tuple[int, int]]) -> list[frozenset[tuple[int, int]]]:
    """Find all exact 8-for-8 circuit trades without scanning 2.2M pairs."""
    adjacency = local_adjacency(mutable)
    found: set[frozenset[tuple[int, int]]] = set()
    for left_index, (left_plus, left_minus) in enumerate(CIRCUITS):
        plus_common = adjacency[left_plus[0]] & adjacency[left_plus[1]]
        minus_common = adjacency[left_minus[0]] & adjacency[left_minus[1]]
        if len(plus_common) < 2 or len(minus_common) < 2:
            continue
        for right_plus in itertools.combinations(sorted(plus_common), 2):
            for right_minus in itertools.combinations(sorted(minus_common), 2):
                oriented = ORIENTED_CIRCUIT.get((right_plus, right_minus))
                if oriented is None:
                    continue
                right_index, rp, rm = oriented
                if right_index <= left_index:
                    continue
                if set(left_plus + left_minus) & set(rp + rm):
                    continue
                present, absent = trade_edges(left_plus, left_minus, rp, rm)
                if len(present) != 8 or len(absent) != 8 or present & absent:
                    continue
                if present <= mutable and not (absent & mutable):
                    found.add(present | absent)
    return sorted(found, key=lambda move: tuple(sorted(move)))


def assert_exact_bp(metrics: dict[str, object]) -> None:
    if metrics["edge_count"] != 693:
        raise AssertionError(metrics["edge_count"])
    if metrics["io_energy"] != 0:
        raise AssertionError(("BP violation", metrics["io_energy"]))
    if metrics["degree_histogram"] != {"14": 99}:
        raise AssertionError(metrics["degree_histogram"])


def save_best(
    path: str,
    mutable: set[tuple[int, int]],
    metrics: dict[str, object],
    input_path: str,
    visited: int,
    depth: int,
    move_count: int,
) -> None:
    payload = dict(metrics)
    payload.update({
        "method": "best-first exact-BP incidence-circuit walk",
        "input": input_path,
        "incidence_circuit_count": len(CIRCUITS),
        "visited_state_count_at_save": visited,
        "depth": depth,
        "last_state_applicable_trade_count": move_count,
        "valid": metrics["energy"] == 0,
    })
    Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--max-states", type=int, default=500)
    parser.add_argument("--seconds", type=float, default=120.0)
    args = parser.parse_args()

    initial = read_graph(args.input)
    initial_metrics = full_metrics(initial)
    assert_exact_bp(initial_metrics)
    initial_key = state_key(initial)
    queue: list[tuple[int, int, tuple[tuple[int, int], ...]]] = [
        (int(initial_metrics["energy"]), 0, initial_key)
    ]
    seen = {state_digest(initial_key)}
    best = set(initial)
    best_metrics = initial_metrics
    best_depth = 0
    expanded = 0
    serial = 1
    started = time.monotonic()
    degree_histogram: dict[int, int] = {}

    while queue and expanded < args.max_states and time.monotonic() - started < args.seconds:
        _priority, depth, key = heapq.heappop(queue)
        current = set(key)
        moves = applicable_trades(current)
        degree_histogram[len(moves)] = degree_histogram.get(len(moves), 0) + 1
        expanded += 1
        print(json.dumps({
            "expanded": expanded,
            "depth": depth,
            "queue": len(queue),
            "moves": len(moves),
            "best_energy": best_metrics["energy"],
            "elapsed": round(time.monotonic() - started, 3),
        }), flush=True)
        for move in moves:
            candidate = current ^ set(move)
            candidate_key = state_key(candidate)
            digest = state_digest(candidate_key)
            if digest in seen:
                continue
            seen.add(digest)
            candidate_metrics = full_metrics(candidate)
            assert_exact_bp(candidate_metrics)
            candidate_depth = depth + 1
            heapq.heappush(
                queue,
                (int(candidate_metrics["energy"]), candidate_depth, candidate_key),
            )
            serial += 1
            if candidate_metrics["energy"] < best_metrics["energy"]:
                best = candidate
                best_metrics = candidate_metrics
                best_depth = candidate_depth
                save_best(
                    args.output, best, best_metrics, args.input,
                    len(seen), best_depth, len(moves),
                )
                print(json.dumps({
                    "improved": best_metrics["energy"],
                    "bad_pairs": best_metrics["bad_pairs"],
                    "depth": best_depth,
                    "seen": len(seen),
                }), flush=True)
                if best_metrics["energy"] == 0:
                    queue.clear()
                    break

    if not Path(args.output).exists() or best_metrics["energy"] == initial_metrics["energy"]:
        save_best(args.output, best, best_metrics, args.input, len(seen), best_depth, 0)
    summary = {
        "status": "SAT" if best_metrics["energy"] == 0 else "SEARCH_EXHAUSTED" if not queue else "LIMIT_REACHED",
        "input": args.input,
        "output": args.output,
        "initial_energy": initial_metrics["energy"],
        "best_energy": best_metrics["energy"],
        "best_bad_pairs": best_metrics["bad_pairs"],
        "expanded_states": expanded,
        "seen_states": len(seen),
        "remaining_queue": len(queue),
        "best_depth": best_depth,
        "applicable_trade_count_histogram": {
            str(k): v for k, v in sorted(degree_histogram.items())
        },
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
