"""Solver-free full exceptional-pair refinement of source-133 survivors.

The first-stage four-point map enumerator leaves only a small collection of
regular masks.  This script repeats the explicit four-element map enumeration
for those masks, now retaining every exceptional-pair collision profile.  It
then imposes the pair upper bound on all exceptional pairs, while keeping the
same-fibre deficits exact.  It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

import scratch_general_e72_source133_hf_exception_csp as hf
import scratch_theory_e72_k23_opposite_collision_enum as first


SHARDS = tuple(Path(
    f"scratch_theory_e72_k23_opposite_collision_enum_shard_{index}.json"
) for index in range(8))
VERTEX_INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
OUTPUT = Path("scratch_theory_e72_k23_ee_cross_enum.json")
PAIR_POSITIONS = tuple(itertools.combinations(range(24), 2))
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIR_POSITIONS)}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def all_pair_needs(vertices, adjacency):
    return tuple(
        2 - len(set(vertices[left]) & set(vertices[right]))
        - int(right in adjacency[left])
        - len(adjacency[left] & adjacency[right])
        for left, right in PAIR_POSITIONS
    )


def target_full_factor(required, adjacency, vertices_by_fibre,
                       fibre_and_local, target_bottom, pair_needs,
                       retain_maps=False, enforce_within_uu=False):
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
                if hf.support(first.VERTICES[z])[1] != target_bottom
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
                if hf.support(first.VERTICES[z])[1] != target_bottom
            ]
            assert len(witnesses) == 2
            overlap_refs.append((
                first.VERTICES[x][1] % 2,
                tuple(
                    (source_position[fibre_and_local[z][0]],
                     fibre_and_local[z][1]) for z in witnesses
                ),
            ))
    overlap_refs = tuple(overlap_refs)
    all_disjoint_rows = tuple(
        (fibre_index, local, witness_refs[fibre_index][local])
        for fibre_index in range(4) for local in range(4)
    )
    disjoint_by_depth = []
    overlap_by_depth = []
    for depth in range(4):
        disjoint_by_depth.append(tuple(
            row for row in all_disjoint_rows
            if depth == row[0] or any(depth == ref[0] for ref in row[2])
        ))
        overlap_by_depth.append(tuple(
            row for row in overlap_refs
            if any(depth == ref[0] for ref in row[1])
        ))

    source_globals = tuple(
        x for fibre in source_fibres for x in vertices_by_fibre[fibre]
    )
    source_slot = {
        x: (source_position[fibre_and_local[x][0]], fibre_and_local[x][1])
        for x in source_globals
    }
    profiles = defaultdict(set) if retain_maps else set()
    stats = Counter()
    for patterns5, patterns6 in (
        (hf.H_PATTERNS, hf.F_PATTERNS),
        (hf.F_PATTERNS, hf.H_PATTERNS),
    ):
        for t5 in patterns5:
            for t6 in patterns6:
                domains = []
                for coefficient, row in source_rows:
                    domain = first.raw_map_pairs(t5, t6, coefficient, row)
                    if not domain:
                        break
                    domains.append(domain)
                else:
                    stats["hf_states"] += 1
                    assigned = [None] * 4

                    def visit(depth):
                        stats["dfs_nodes"] += 1
                        if depth == 4:
                            stats["eu_map_products"] += 1
                            values = []
                            same_by_source = []
                            for fibre_index in range(4):
                                same_by_source.append(assigned[fibre_index][0])
                            for left, right in PAIR_POSITIONS:
                                if left not in source_slot or right not in source_slot:
                                    values.append(0)
                                    continue
                                lf, ll = source_slot[left]
                                rf, rl = source_slot[right]
                                value = (
                                    int(assigned[lf][1][ll] == assigned[rf][1][rl])
                                    + int(assigned[lf][2][ll] == assigned[rf][2][rl])
                                )
                                values.append(value)
                            if any(value > bound for value, bound
                                   in zip(values, pair_needs)):
                                stats["single_factor_EE_upper_reject"] += 1
                                return
                            if enforce_within_uu:
                                counts = [[0] * 4 for _ in range(4)]
                                for entry in assigned:
                                    for local in range(4):
                                        counts[entry[1][local]][entry[2][local]] += 1
                                if any(
                                    counts[left][right]
                                    > (1 if left // 2 == right // 2 else 2)
                                    for left in range(4) for right in range(4)
                                ):
                                    stats["within_target_UU_overlap_reject"] += 1
                                    return
                            key = (tuple(same_by_source), bytes(values))
                            if retain_maps:
                                profiles[key].add(tuple(
                                    (entry[1], entry[2]) for entry in assigned
                                ))
                            else:
                                profiles.add(key)
                            return
                        for entry in domains[depth]:
                            assigned[depth] = entry
                            if first.partial_eu_factor_ok(
                                assigned, disjoint_by_depth[depth],
                                overlap_by_depth[depth],
                            ):
                                visit(depth + 1)
                            assigned[depth] = None

                    visit(0)
    stats["distinct_full_profiles"] = len(profiles)
    if retain_maps:
        stats["distinct_explicit_map_configurations"] = sum(
            len(rows) for rows in profiles.values()
        )
        return {
            key: tuple(sorted(rows))
            for key, rows in sorted(profiles.items())
        }, dict(stats)
    return tuple(sorted(profiles)), dict(stats)


def full_join(factors, pair_needs):
    positions = {}
    for target in hf.BOTTOM:
        plus, minus = hf.DIRECTION[target]
        fibres = ((0, plus), (1, plus), (0, minus), (1, minus))
        positions[target] = {fibre: index for index, fibre in enumerate(fibres)}

    relation = {}
    for left, right in itertools.combinations(hf.BOTTOM, 2):
        source_bottom = next(value for value in hf.BOTTOM
                             if value not in (left, right))
        right_index = defaultdict(list)
        for index, (same, profile) in enumerate(factors[right]):
            needed_left = []
            for root in (0, 1):
                fibre = (root, source_bottom)
                global_indices = VERTICES_BY_FIBRE[fibre]
                row = []
                for x, y in itertools.combinations(global_indices, 2):
                    bit = PAIR_INDEX[tuple(sorted((x, y)))]
                    row.append(pair_needs[bit] - profile[bit])
                needed_left.append(tuple(row))
            if min(itertools.chain.from_iterable(needed_left)) >= 0:
                right_index[tuple(needed_left)].append(index)
        allowed = defaultdict(list)
        for index, (same, _profile) in enumerate(factors[left]):
            key = tuple(same[positions[left][(root, source_bottom)]]
                        for root in (0, 1))
            allowed[index].extend(right_index.get(key, ()))
        relation[(left, right)] = allowed

    count = 0
    witness = None
    for index2, indices3 in relation[(2, 3)].items():
        indices4_from2 = relation[(2, 4)].get(index2, ())
        if not indices4_from2:
            continue
        profile2 = factors[2][index2][1]
        for index3 in indices3:
            allowed4 = set(indices4_from2).intersection(
                relation[(3, 4)].get(index3, ())
            )
            if not allowed4:
                continue
            profile3 = factors[3][index3][1]
            partial = bytes(a + b for a, b in zip(profile2, profile3))
            if any(value > bound for value, bound
                   in zip(partial, pair_needs)):
                continue
            for index4 in allowed4:
                profile4 = factors[4][index4][1]
                if any(a + b > bound for a, b, bound
                       in zip(partial, profile4, pair_needs)):
                    continue
                count += 1
                if witness is None:
                    witness = (index2, index3, index4)
    return count, witness


def load_survivors(mask_hex=None):
    if mask_hex is not None:
        source = json.loads(Path(
            "scratch_general_e72_source133_hf_exception_csp.json"
        ).read_text(encoding="utf-8"))["frontier"]
        return [next(row for row in source if row[0] == mask_hex)]
    records = []
    for path in SHARDS:
        document = json.loads(path.read_text(encoding="utf-8"))
        records.extend(document["survivors"])
    return records


def run(mask_hex=None):
    started = time.monotonic()
    global VERTICES_BY_FIBRE
    first.VERTICES = tuple(tuple(row) for row in json.loads(
        VERTEX_INPUT.read_text(encoding="utf-8")
    )["vertex_order"])
    vertices_by_fibre = defaultdict(list)
    for x, vertex in enumerate(first.VERTICES):
        vertices_by_fibre[hf.support(vertex)].append(x)
    VERTICES_BY_FIBRE = {key: tuple(value)
                         for key, value in vertices_by_fibre.items()}
    fibre_and_local = {}
    for fibre, indices in VERTICES_BY_FIBRE.items():
        for local, x in enumerate(indices):
            fibre_and_local[x] = (fibre, local)

    records = load_survivors(mask_hex)
    survivors = []
    rows = []
    per_macro = defaultdict(Counter)
    for number, record in enumerate(records):
        mask = int(record[0], 16)
        adjacency = hf.adjacency_from_mask(24, PAIR_POSITIONS, mask)
        _eps, required, failure = hf.local_q_and_required_sums(
            first.VERTICES, PAIR_POSITIONS, mask
        )
        assert failure is None
        pair_needs = all_pair_needs(first.VERTICES, adjacency)
        factors = {}
        stats = {}
        for target in hf.BOTTOM:
            factors[target], stats[target] = target_full_factor(
                required, adjacency, VERTICES_BY_FIBRE, fibre_and_local,
                target, pair_needs,
            )
            if not factors[target]:
                break
        if len(factors) == 3 and all(factors.values()):
            count, witness = full_join(factors, pair_needs)
        else:
            count, witness = 0, None
        macro = record[3]
        per_macro[macro]["input_orbits"] += 1
        per_macro[macro]["input_mass"] += record[1]
        per_macro[macro]["passing_orbits"] += int(bool(count))
        per_macro[macro]["passing_mass"] += record[1] * int(bool(count))
        if count:
            survivors.append([*record[:4], count, list(witness)])
        rows.append({
            "record_number": number, "mask_hex": record[0], "macro": macro,
            "target_stats": {str(key): value for key, value in stats.items()},
            "join_count": count,
        })
        print(number + 1, record[3], count, flush=True)
    if mask_hex is None:
        assert len(records) == 81
        assert sum(row[1] for row in records) == 9_952
        assert len(survivors) == 1
        assert sum(row[1] for row in survivors) == 16
    result = {
        "status": "EXACT_SOLVER_FREE_EE_CROSS_ENUM_COMPLETE",
        "input_orbits": len(records),
        "input_mass": sum(row[1] for row in records),
        "passing_orbits": len(survivors),
        "passing_mass": sum(row[1] for row in survivors),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "inputs": ({str(path): sha256(path) for path in SHARDS}
                   if mask_hex is None else {"explicit_mask": mask_hex}),
        "per_macro": {str(key): dict(sorted(value.items()))
                      for key, value in sorted(per_macro.items())},
        "rows": rows,
        "survivors": survivors,
        "checks": {
            "standard_library_only": True,
            "all_explicit_map_products_enumerated": True,
            "all_EU_pair_upper_rows_inherited": True,
            "all_EE_same_pair_deficits_exact": True,
            "all_EE_cross_pair_upper_rows_exact": True,
            "SAT_or_SMT_used": False,
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "status", "input_orbits", "passing_orbits", "elapsed_seconds"
    )}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mask")
    args = parser.parse_args()
    run(args.mask)


if __name__ == "__main__":
    main()
