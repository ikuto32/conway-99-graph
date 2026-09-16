"""Enumerate the six forced 2x2 blocks and test source-133 E^2 moments.

This is a computational cross-check for the analytic K_{2,3} reductions,
not a premise of their proof.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path


INPUT = Path("scratch_general_e72_q3_fast_expansion_part_27.json")
OUTPUT = Path("scratch_theory_e72_k23_exception_moment_probe.json")
EXCEPTIONAL_SUPPORTS = ((0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4))
FIBRE_INDEX = {support: index for index, support in enumerate(EXCEPTIONAL_SUPPORTS)}


def vid(label):
    left, right = label
    support = tuple(sorted((left // 2, right // 2)))
    fibre = FIBRE_INDEX[support]
    bits = (left % 2, right % 2)
    local = 2 * bits[0] + bits[1]
    return 4 * fibre + local


def target(f, g):
    if (f < 3) == (g < 3):
        return 8
    return 8 if f % 3 == g % 3 else 12


def moments(adjacency):
    result = {}
    for f, g in itertools.combinations(range(6), 2):
        total = 0
        for x in range(24):
            nf = sum(y // 4 == f for y in adjacency[x])
            ng = sum(y // 4 == g for y in adjacency[x])
            total += nf * ng
        result[(f, g)] = total
    return result


def main():
    raw = INPUT.read_bytes()
    data = json.loads(raw)
    assert data["partition_index"] == 27
    row = data["rows"][0]
    assert row["compression_orbit_index"] == 0
    reps = row["local_graph_representatives"]
    counts = Counter()
    weighted = Counter()
    first_pass = {}
    regular_reps = 0
    for rep_index, rep in enumerate(reps):
        # Macro 4 is the sole nonregular state orbit and is kept outside this
        # regular-branch probe.
        adjacency0 = [set() for _ in range(24)]
        for left, right in rep["edges"]:
            x, y = vid(left), vid(right)
            adjacency0[x].add(y)
            adjacency0[y].add(x)
        if any(sum(y // 4 == x // 4 for y in adjacency0[x]) != 1
               for x in range(24)):
            continue
        # The pointwise A/B and per-bottom-group equations force one
        # same-side and one vertical overlap neighbour at every vertex.
        overlap_profile_ok = True
        for x in range(24):
            f = x // 4
            same = sum(y // 4 != f and (y // 4 < 3) == (f < 3)
                       for y in adjacency0[x])
            vertical = sum(y // 4 == (f + 3 if f < 3 else f - 3)
                           for y in adjacency0[x])
            if (same, vertical) != (1, 1):
                overlap_profile_ok = False
                break
        if not overlap_profile_ok:
            continue
        regular_reps += 1
        same_target = {}
        for x in range(24):
            f = x // 4
            candidates = [y // 4 for y in adjacency0[x]
                          if y // 4 != f and (y // 4 < 3) == (f < 3)]
            assert len(candidates) == 1
            same_target[x] = candidates[0] % 3

        blocks = []
        for i in range(3):
            for k in range(3):
                if i == k:
                    continue
                j = 3 - i - k
                left = [4 * i + local for local in range(4)
                        if same_target[4 * i + local] == j]
                right = [4 * (3 + k) + local for local in range(4)
                         if same_target[4 * (3 + k) + local] == j]
                assert len(left) == len(right) == 2
                blocks.append((i, k, tuple(left), tuple(right)))
        assert len(blocks) == 6

        pass_count = 0
        histogram = Counter()
        for choices in itertools.product((0, 1), repeat=6):
            adjacency = [set(neighbours) for neighbours in adjacency0]
            for choice, (_i, _k, left, right) in zip(choices, blocks):
                ordered_right = right if choice == 0 else right[::-1]
                for x, y in zip(left, ordered_right):
                    adjacency[x].add(y)
                    adjacency[y].add(x)
            assert all(len(neighbours) == 4 for neighbours in adjacency)
            profile = moments(adjacency)
            failures = tuple((pair, value, target(*pair))
                             for pair, value in profile.items()
                             if value != target(*pair))
            histogram[len(failures)] += 1
            if not failures:
                pass_count += 1
                if str(rep["Q"]) not in first_pass:
                    first_pass[str(rep["Q"])] = {
                        "representative_index": rep_index,
                        "choices": list(choices),
                        "moments": {str(pair): value for pair, value in profile.items()},
                    }
        counts[(rep["Q"], pass_count)] += 1
        weighted[(rep["Q"], pass_count)] += int(rep["orbit_size"])

    assert 0 < regular_reps <= 8004
    result = {
        "status": "EXACT_REGULAR_EXCEPTION_MOMENT_ENUMERATION_COMPLETE",
        "input": str(INPUT),
        "input_sha256": hashlib.sha256(raw).hexdigest().upper(),
        "regular_overlap_orbits": regular_reps,
        "missing_blocks_per_overlap_graph": 6,
        "completions_per_overlap_graph": 64,
        "target_exception_witness_moments": {
            "same_side": 8,
            "vertical": 8,
            "cross_disjoint": 12,
        },
        "orbit_count_by_(Q,passing_completions)": {
            str(key): value for key, value in sorted(counts.items())
        },
        "labelled_overlap_mass_by_(Q,passing_completions)": {
            str(key): value for key, value in sorted(weighted.items())
        },
        "total_representative_completions": regular_reps * 64,
        "total_passing_representative_completions": sum(
            orbit_count * key[1] for key, orbit_count in counts.items()
        ),
        "first_passing_controls": first_pass,
        "claim_boundary": (
            "Enumerates exceptional induced-graph block completions and their "
            "compressed A_E^2 moments only; no full-graph exclusion claim."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(OUTPUT), **result}, sort_keys=True))


if __name__ == "__main__":
    main()
