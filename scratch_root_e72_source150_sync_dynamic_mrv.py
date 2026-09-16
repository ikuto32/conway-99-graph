"""Exact MRV traversal wrapper for the source150 synchronized CSP.

This replaces only the block-variable traversal order.  It preserves the
original node-table, pair-upper, state-filter, and leaf-filter predicates.
"""

from __future__ import annotations

import sys

import scratch_theory_e72_source150_synchronized_config_csp as engine


def dynamic_solve(
    base_adjacency, block_rows, node_tables, incident,
    all_config_bits, vertices, node_cap, leaf_filter=None,
    state_filter=None,
):
    assignment = [-1] * len(block_rows)
    nodes = 0
    traversal = []
    static_rank = sorted(
        range(len(block_rows)),
        key=lambda variable: (
            len(block_rows[variable]["options"]),
            len(node_tables[block_rows[variable]["pair"][0]]),
            len(node_tables[block_rows[variable]["pair"][1]]),
            variable,
        ),
    )
    rank = {variable: index for index, variable in enumerate(static_rank)}
    possible_cache = {}

    def possible_bits(fibre, active_bits):
        variables = incident[fibre]
        pattern = tuple(assignment[variable] for variable in variables)
        key = (fibre, pattern, active_bits)
        cached = possible_cache.get(key)
        if cached is not None:
            return cached
        answer = 0
        for choices, bits in node_tables[fibre].items():
            if not bits & active_bits:
                continue
            if all(
                choice < 0 or choice == choices[position]
                for position, choice in enumerate(pattern)
            ):
                answer |= bits
        answer &= active_bits
        possible_cache[key] = answer
        return answer

    def viable_options(variable, active_bits):
        endpoints = block_rows[variable]["pair"]
        answer = []
        for option_index in range(len(block_rows[variable]["options"])):
            assignment[variable] = option_index
            bits = active_bits
            for fibre in endpoints:
                bits = possible_bits(fibre, bits)
                if not bits:
                    break
            if bits:
                answer.append((option_index, bits))
        assignment[variable] = -1
        return answer

    def recurse(depth, adjacency, active_bits):
        nonlocal nodes
        if node_cap and nodes >= node_cap:
            return "UNKNOWN", None
        if state_filter is not None:
            active_bits = state_filter(adjacency, active_bits)
            if not active_bits:
                return "UNSAT", None
        if depth == len(block_rows):
            bits = active_bits if leaf_filter is None else leaf_filter(
                adjacency, active_bits, tuple(assignment)
            )
            return (("SAT", (tuple(assignment), bits)) if bits
                    else ("UNSAT", None))

        best_variable = None
        best_options = None
        best_score = None
        for variable in static_rank:
            if assignment[variable] >= 0:
                continue
            options = viable_options(variable, active_bits)
            if not options:
                return "UNSAT", None
            score = (
                len(options),
                sum(bits.bit_count() for _option, bits in options),
                rank[variable],
            )
            if best_score is None or score < best_score:
                best_variable = variable
                best_options = options
                best_score = score
                if score[0] == 1:
                    break
        variable = best_variable
        traversal.append(variable)
        for option_index, bits in best_options:
            nodes += 1
            if node_cap and nodes > node_cap:
                traversal.pop()
                return "UNKNOWN", None
            assignment[variable] = option_index
            trial = [set(neighbours) for neighbours in adjacency]
            affected = set()
            for left, right in block_rows[variable]["options"][option_index]:
                trial[left].add(right)
                trial[right].add(left)
                affected.add(left)
                affected.add(right)
            if engine.pair_upper_affected(adjacency, trial, affected, vertices):
                status, witness = recurse(depth + 1, trial, bits)
                if status != "UNSAT":
                    assignment[variable] = -1
                    traversal.pop()
                    return status, witness
            assignment[variable] = -1
        traversal.pop()
        return "UNSAT", None

    status, witness = recurse(0, base_adjacency, all_config_bits)
    return status, witness, nodes, static_rank


def main() -> None:
    engine.solve = dynamic_solve
    engine.main()


if __name__ == "__main__":
    main()
