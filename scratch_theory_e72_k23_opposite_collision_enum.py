"""Solver-free exact enumeration for source-133 regular macros.

The enumerator uses only finite maps between four-element labelled sets.  It
rechecks the H/F load and exceptional-row recurrence, the exact remaining
same-exceptional-fibre common-witness counts, and the induced-pair upper bound
for every exceptional--U pair.  The latter is used through the equivalent
four-point collision rules proved in the companion theory note.

No SAT/SMT package or edge-variable CNF is used.  Target-bottom factors are
enumerated independently and reduced to their six-pair collision signatures;
the three factors are then joined exactly along the six exceptional fibres.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import time
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import scratch_general_e72_source133_hf_exception_csp as hf


INPUT = Path("scratch_general_e72_source133_hf_exception_csp.json")
VERTEX_INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
OUTPUT = Path("scratch_theory_e72_k23_opposite_collision_enum.json")
BOTTOM = hf.BOTTOM
OUTSIDE = hf.OUTSIDE
REGULAR_MACROS = hf.REGULAR_MACROS
PAIR_LOCAL = tuple(itertools.combinations(range(4), 2))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def collision_signature(mapping5, mapping6):
    return tuple(
        int(mapping5[left] == mapping5[right])
        + int(mapping6[left] == mapping6[right])
        for left, right in PAIR_LOCAL
    )


@lru_cache(maxsize=None)
def raw_map_pairs(t5, t6, coefficient, required):
    """All labelled map pairs satisfying loads and an exceptional T row."""

    degree5 = tuple(1 + coefficient * value for value in t5)
    degree6 = tuple(1 + coefficient * value for value in t6)
    answer = []
    for mapping5 in hf.mappings_with_degrees(degree5):
        for mapping6 in hf.mappings_with_degrees(degree6):
            if all(t5[mapping5[x]] + t6[mapping6[x]] == required[x]
                   for x in range(4)):
                answer.append((collision_signature(mapping5, mapping6),
                               mapping5, mapping6))
    return tuple(answer)


def opposite(local):
    # Local order is (00,01,10,11).
    return 3 - local


def side_adjacent(left, right):
    return (left ^ right) in (1, 2)


def eu_factor_ok(maps, witness_refs, overlap_refs):
    """Check every E--U_disjoint row for one target bottom, both outsides."""

    for fibre_index, own_maps in enumerate(maps):
        for local in range(4):
            for outside_index in (1, 2):
                y0 = own_maps[outside_index][local]
                images = tuple(
                    maps[other_fibre][outside_index][other_local]
                    for other_fibre, other_local
                    in witness_refs[fibre_index][local]
                )
                counts = (images.count(0), images.count(1),
                          images.count(2), images.count(3))
                # Pair upper is base(y)+count(y)<=2.  The base is one at
                # y0 and its two C4 neighbours, and zero at opposite(y0).
                for y, count in enumerate(counts):
                    base = int(y == y0 or side_adjacent(y, y0))
                    if base + count > 2:
                        return False
                # This equivalent form is useful as an internal cross-check.
                repeated = [y for y, count in enumerate(counts) if count > 1]
                if repeated and not (
                    len(repeated) == 1
                    and repeated[0] == opposite(y0)
                    and counts[repeated[0]] == 2
                ):
                    raise AssertionError((fibre, local, y0, images))
    # An exceptional vertex whose support overlaps U_i has exactly two
    # exceptional neighbours whose supports are disjoint from U_i.  If their
    # images coincide, the target must use the opposite root-neighbour label
    # in group i; otherwise that E--U pair already has two common neighbours
    # although only one outer common neighbour is available.
    for bottom_bit, references in overlap_refs:
        for outside_index in (1, 2):
            images = tuple(
                maps[fibre_index][outside_index][local]
                for fibre_index, local in references
            )
            if images[0] == images[1] and images[0] // 2 == bottom_bit:
                return False
    return True


def partial_eu_factor_ok(maps, disjoint_rows, overlap_rows):
    """Fast monotone prefix check for only the newly affected rows."""

    for fibre_index, local, references in disjoint_rows:
        own_maps = maps[fibre_index]
        if own_maps is None:
            continue
        for outside_index in (1, 2):
            y0 = own_maps[outside_index][local]
            values = []
            for other_fibre, other_local in references:
                other_maps = maps[other_fibre]
                if other_maps is not None:
                    values.append(other_maps[outside_index][other_local])
            if len(values) >= 2:
                if values[0] == values[1] and values[0] != opposite(y0):
                    return False
                if len(values) == 3:
                    if values[0] == values[2] and values[0] != opposite(y0):
                        return False
                    if values[1] == values[2] and values[1] != opposite(y0):
                        return False
                    if values[0] == values[1] == values[2]:
                        return False
    for bottom_bit, references in overlap_rows:
        first_fibre, first_local = references[0]
        second_fibre, second_local = references[1]
        if maps[first_fibre] is None or maps[second_fibre] is None:
            continue
        for outside_index in (1, 2):
            first = maps[first_fibre][outside_index][first_local]
            second = maps[second_fibre][outside_index][second_local]
            if first == second and first // 2 == bottom_bit:
                return False
    return True


def target_factor(required, adjacency, vertices_by_fibre, fibre_and_local,
                  target_bottom, factor_cache):
    """Union all H/F states, retaining only exact collision signatures."""

    plus, minus = hf.DIRECTION[target_bottom]
    source_fibres = ((0, plus), (1, plus), (0, minus), (1, minus))
    source_rows = []
    for fibre in source_fibres:
        row = tuple(required[(x, target_bottom)]
                    for x in vertices_by_fibre[fibre])
        coefficient = (1 if fibre[0] == 0 else -1) * (
            1 if fibre[1] == plus else -1
        )
        source_rows.append((coefficient, row))

    source_position = {fibre: index
                       for index, fibre in enumerate(source_fibres)}
    witness_refs = []
    for fibre in source_fibres:
        rows = []
        for x in vertices_by_fibre[fibre]:
            witnesses = [
                z for z in adjacency[x]
                if hf.support(VERTICES[z])[1] != target_bottom
            ]
            assert len(witnesses) == 3
            rows.append(tuple(
                (source_position[fibre_and_local[z][0]], fibre_and_local[z][1])
                for z in witnesses
            ))
        witness_refs.append(tuple(rows))
    witness_refs = tuple(witness_refs)
    overlap_refs = []
    for root in (0, 1):
        fibre = (root, target_bottom)
        for x in vertices_by_fibre[fibre]:
            witnesses = [
                z for z in adjacency[x]
                if hf.support(VERTICES[z])[1] != target_bottom
            ]
            assert len(witnesses) == 2
            overlap_refs.append((
                VERTICES[x][1] % 2,
                tuple(
                    (source_position[fibre_and_local[z][0]],
                     fibre_and_local[z][1])
                    for z in witnesses
                ),
            ))
    overlap_refs = tuple(overlap_refs)
    disjoint_by_depth = []
    overlap_by_depth = []
    all_disjoint_rows = tuple(
        (fibre_index, local, witness_refs[fibre_index][local])
        for fibre_index in range(4) for local in range(4)
    )
    for depth in range(4):
        disjoint_by_depth.append(tuple(
            row for row in all_disjoint_rows
            if depth == row[0] or any(depth == ref[0] for ref in row[2])
        ))
        overlap_by_depth.append(tuple(
            row for row in overlap_refs
            if any(depth == ref[0] for ref in row[1])
        ))
    state_key = (tuple(source_rows), witness_refs, overlap_refs)
    if state_key in factor_cache:
        cached = factor_cache[state_key]
        return cached, {
            "cache_hit": True,
            "distinct_signature_factors": len(cached),
        }

    signatures = {}
    dfs_nodes = 0
    raw_products_examined = 0
    eu_feasible_signature_products = 0
    hf_states = 0
    for patterns5, patterns6 in (
        (hf.H_PATTERNS, hf.F_PATTERNS),
        (hf.F_PATTERNS, hf.H_PATTERNS),
    ):
        for t5 in patterns5:
            for t6 in patterns6:
                domains = []
                for coefficient, row in source_rows:
                    domain = raw_map_pairs(t5, t6, coefficient, row)
                    if not domain:
                        break
                    domains.append(domain)
                else:
                    hf_states += 1
                    assigned = [None] * 4

                    def visit(depth):
                        nonlocal dfs_nodes, raw_products_examined
                        nonlocal eu_feasible_signature_products
                        dfs_nodes += 1
                        if depth == len(source_fibres):
                            raw_products_examined += 1
                            maps = tuple(assigned)
                            assert eu_factor_ok(maps, witness_refs, overlap_refs)
                            key = tuple(entry[0] for entry in maps)
                            if key not in signatures:
                                eu_feasible_signature_products += 1
                                signatures[key] = (t5, t6, maps)
                            return
                        for entry in domains[depth]:
                            assigned[depth] = entry
                            if partial_eu_factor_ok(
                                assigned, disjoint_by_depth[depth],
                                overlap_by_depth[depth],
                            ):
                                visit(depth + 1)
                            assigned[depth] = None

                    visit(0)
    answer = tuple(signatures)
    factor_cache[state_key] = answer
    return answer, {
        "cache_hit": False,
        "hf_states": hf_states,
        "dfs_nodes": dfs_nodes,
        "raw_map_products_examined": raw_products_examined,
        "eu_feasible_signature_products": eu_feasible_signature_products,
        "distinct_signature_factors": len(signatures),
    }


def add_signatures(left, right):
    return tuple(a + b for a, b in zip(left, right))


def factors_join(factors, pair_needs):
    """Join target factors through exact same-source-fibre pair counts."""

    positions = {}
    for target in BOTTOM:
        plus, minus = hf.DIRECTION[target]
        source_fibres = ((0, plus), (1, plus), (0, minus), (1, minus))
        positions[target] = {fibre: index
                             for index, fibre in enumerate(source_fibres)}

    relation = {}
    for left, right in itertools.combinations(BOTTOM, 2):
        source_bottom = next(value for value in BOTTOM
                             if value not in (left, right))
        right_index = defaultdict(list)
        for index, signatures in enumerate(factors[right]):
            key = tuple(
                tuple(pair_needs[(root, source_bottom)][p] - signatures[
                    positions[right][(root, source_bottom)]
                ][p] for p in range(6))
                for root in (0, 1)
            )
            if min(itertools.chain.from_iterable(key)) >= 0:
                right_index[key].append(index)
        allowed = defaultdict(list)
        for index, signatures in enumerate(factors[left]):
            key = tuple(
                signatures[positions[left][(root, source_bottom)]]
                for root in (0, 1)
            )
            allowed[index].extend(right_index.get(key, ()))
        relation[(left, right)] = allowed

    relation23 = relation[(2, 3)]
    relation24 = relation[(2, 4)]
    relation34 = relation[(3, 4)]
    count = 0
    witness = None
    for index2, indices3 in relation23.items():
        possible4 = set(relation24.get(index2, ()))
        if not possible4:
            continue
        for index3 in indices3:
            joint4 = possible4.intersection(relation34.get(index3, ()))
            count += len(joint4)
            if witness is None and joint4:
                witness = (index2, index3, next(iter(joint4)))
    return count, witness


def same_fibre_needs(vertices, adjacency, vertices_by_fibre):
    answer = {}
    for fibre, indices in vertices_by_fibre.items():
        values = []
        for left, right in itertools.combinations(indices, 2):
            target = 2 - len(set(vertices[left]) & set(vertices[right]))
            existing = int(right in adjacency[left]) + len(
                adjacency[left] & adjacency[right]
            )
            values.append(target - existing)
        assert min(values) >= 0 and sum(values) == 6
        answer[fibre] = tuple(values)
    return answer


def run(limit=None, start=0, stop=None, output=OUTPUT):
    started = time.monotonic()
    input_document = json.loads(INPUT.read_text(encoding="utf-8"))
    vertex_document = json.loads(VERTEX_INPUT.read_text(encoding="utf-8"))
    global VERTICES
    VERTICES = tuple(tuple(row) for row in vertex_document["vertex_order"])
    pair_positions = tuple(itertools.combinations(range(24), 2))
    vertices_by_fibre = defaultdict(list)
    for x, vertex in enumerate(VERTICES):
        vertices_by_fibre[hf.support(vertex)].append(x)
    vertices_by_fibre = {key: tuple(value)
                         for key, value in vertices_by_fibre.items()}
    fibre_and_local = {}
    for fibre, indices in vertices_by_fibre.items():
        for local, x in enumerate(indices):
            fibre_and_local[x] = (fibre, local)

    records = [record for record in input_document["frontier"]
               if record[3] in REGULAR_MACROS]
    records = records[start:stop]
    if limit is not None:
        records = records[:limit]
    per_macro = defaultdict(Counter)
    controls = []
    survivors = []
    factor_cache = {}
    for number, record in enumerate(records):
        mask = int(record[0], 16)
        adjacency = hf.adjacency_from_mask(24, pair_positions, mask)
        _eps, required, failure = hf.local_q_and_required_sums(
            VERTICES, pair_positions, mask
        )
        assert failure is None
        pair_needs = same_fibre_needs(
            VERTICES, adjacency, vertices_by_fibre
        )
        factors = {}
        factor_stats = {}
        for target in BOTTOM:
            factors[target], factor_stats[target] = target_factor(
                required, adjacency, vertices_by_fibre, fibre_and_local, target,
                factor_cache,
            )
            if not factors[target]:
                break
        if len(factors) == len(BOTTOM) and all(factors.values()):
            join_count, witness = factors_join(factors, pair_needs)
        else:
            join_count, witness = 0, None
        macro = record[3]
        row = per_macro[macro]
        row["input_orbits"] += 1
        row["input_mass"] += record[1]
        row["factor_empty"] += int(any(not factors[x] for x in BOTTOM))
        if join_count:
            row["passing_orbits"] += 1
            row["passing_mass"] += record[1]
            survivors.append([*record[:4], join_count, list(witness)])
        else:
            row["rejected_orbits"] += 1
            row["rejected_mass"] += record[1]
        if len(controls) < 20:
            controls.append({
                "record_number": number,
                "mask_hex": record[0],
                "macro": macro,
                "factor_stats": {str(k): v for k, v in factor_stats.items()},
                "join_count": join_count,
            })
        if (number + 1) % 25 == 0:
            print(number + 1, "survivors", len(survivors),
                  "elapsed", round(time.monotonic() - started, 2), flush=True)

    summary = {
        "input_orbits": len(records),
        "input_mass": sum(record[1] for record in records),
        "passing_orbits": len(survivors),
        "passing_mass": sum(record[1] for record in survivors),
        "rejected_orbits": len(records) - len(survivors),
        "distinct_target_factor_states": len(factor_cache),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "slice_start": start,
        "slice_stop": stop,
    }
    complete = limit is None and start == 0 and stop is None
    if complete:
        assert summary["input_orbits"] == 5_138
        assert summary["input_mass"] == 1_129_056
        assert not survivors
    result = {
        "status": "EXACT_SOLVER_FREE_ENUM_COMPLETE" if complete
                  else "PARTIAL_PROBE_COMPLETE",
        "inputs": {str(INPUT): sha256(INPUT),
                   str(VERTEX_INPUT): sha256(VERTEX_INPUT)},
        "summary": summary,
        "per_macro": {str(key): dict(sorted(value.items()))
                      for key, value in sorted(per_macro.items())},
        "controls": controls,
        "survivors": survivors,
        "checks": {
            "standard_library_only": True,
            "all_HF_t_patterns_enumerated": True,
            "all_four_symbol_exception_to_U_maps_enumerated": True,
            "all_exception_recurrence_rows_exact": True,
            "all_EE_same_pair_deficits_exact": True,
            "all_EU_disjoint_pair_upper_rows_exact": True,
            "all_EU_overlap_pair_upper_rows_exact": True,
            "SAT_or_SMT_used": False,
        },
        "claim_boundary": (
            "Every regular mask in the preceding exact frontier is excluded "
            "by H/F loads, exceptional q recurrence, exact same-fibre pair "
            "deficits, and the opposite-collision form of EU_disjoint pair "
            "upper.  Macro 4 is outside the regular H/F hypothesis."
        ),
    }
    atomic_json(output, result)
    print(json.dumps({"status": result["status"], **summary}, sort_keys=True),
          flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    run(args.limit, args.start, args.stop, args.output)


if __name__ == "__main__":
    main()
