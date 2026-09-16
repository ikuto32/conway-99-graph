"""Enumerate safe quotient symmetry branches for the C2 case."""

from __future__ import annotations

import itertools
import json


V = [(i, j, r) for i in range(7) for j in range(i + 1, 7) for r in range(2)]
IDX = {x: k for k, x in enumerate(V)}


def image(x: int, perm: tuple[int, ...], flips: tuple[int, ...]) -> int:
    i, j, r = V[x]
    a, b = perm[i], perm[j]
    return IDX[(min(a, b), max(a, b), r ^ flips[i] ^ flips[j])]


def transformations():
    # Quotient by the ineffective all-groups flip: fix flip[6]=0.
    for p in itertools.permutations(range(7)):
        for bits in range(64):
            f = tuple((bits >> i) & 1 for i in range(6)) + (0,)
            yield p, f


def orbit_partition(items: set[int], transformations_list) -> list[list[int]]:
    unseen = set(items)
    result = []
    while unseen:
        x = min(unseen)
        orb = {image(x, p, f) for p, f in transformations_list}
        assert orb <= items
        result.append(sorted(orb))
        unseen -= orb
    return result


def main() -> None:
    x0 = IDX[(0, 1, 0)]
    mates = {
        "same": IDX[(0, 1, 1)],
        "overlap": IDX[(0, 2, 0)],
        "disjoint": IDX[(2, 3, 0)],
    }
    all_transforms = list(transformations())
    assert len(all_transforms) == 322_560
    output = {}
    for kind, y0 in mates.items():
        first = {x0, y0}
        stab_edge = [
            (p, f) for p, f in all_transforms
            if {image(x0, p, f), image(y0, p, f)} == first
        ]
        remaining = set(range(42)) - first
        vertex_orbits = orbit_partition(remaining, stab_edge)
        # Choose a representative z from the smallest vertex orbit, then branch
        # on the orbits of its possible mate under the point stabilizer.
        z0 = vertex_orbits[0][0]
        stab_z = [(p, f) for p, f in stab_edge if image(z0, p, f) == z0]
        mate_orbits = orbit_partition(remaining - {z0}, stab_z)
        output[kind] = {
            "first": [V[x0], V[y0]],
            "stabilizer_size": len(stab_edge),
            "remaining_vertex_orbits": [
                {"size": len(o), "representative": V[o[0]]} for o in vertex_orbits
            ],
            "chosen_z": V[z0],
            "point_stabilizer_size": len(stab_z),
            "mate_orbits": [
                {"size": len(o), "representative": V[o[0]]} for o in mate_orbits
            ],
        }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
