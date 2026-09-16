"""Clean-room audit of the small-motif meaning of E0=S+D.

This file deliberately does not import any project discovery/enumeration code.
It reconstructs the relevant graphs from explicit edge lists, canonicalizes
them under every vertex permutation, and checks the rooted-flag and deletion-
incidence multiplicities used in the first-moment identity.

It is a finite arithmetic/combinatorial audit, not a formal proof and not a
construction (or nonexistence proof) of srg(99,14,1,2).
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, permutations
import json
import os
from pathlib import Path
from typing import Iterable, Sequence


TEX_SOURCE = Path("scratch_reimbayev_2608_19410_source/The_Subgraphs_of_Order_Seven.tex")
FIGURE_SOURCE = Path("scratch_reimbayev_2608_19410_source/figure_1.png")
OUTPUT_JSON = Path("scratch_root_e0_motif_first_moment_audit.json")
OUTPUT_MD = Path("scratch_root_e0_motif_first_moment_audit.md")

N = 99
K = 14
Edge = tuple[int, int]
Graph = frozenset[Edge]


def norm_edge(left: int, right: int) -> Edge:
    assert left != right
    return (left, right) if left < right else (right, left)


def graph(edges: Iterable[tuple[int, int]]) -> Graph:
    answer = frozenset(norm_edge(left, right) for left, right in edges)
    assert len(answer) == len(tuple(edges)) if isinstance(edges, Sequence) else True
    return answer


def vertices_of(order: int) -> range:
    return range(order)


def edge_order(order: int) -> tuple[Edge, ...]:
    return tuple(combinations(vertices_of(order), 2))


def edge_mask(edges: Graph, order: int) -> int:
    positions = {edge: index for index, edge in enumerate(edge_order(order))}
    assert all(0 <= left < right < order for left, right in edges)
    return sum(1 << positions[edge] for edge in edges)


def relabel(edges: Graph, permutation: Sequence[int]) -> Graph:
    return frozenset(norm_edge(permutation[left], permutation[right]) for left, right in edges)


def canonical_mask(edges: Graph, order: int) -> int:
    return min(edge_mask(relabel(edges, permutation), order) for permutation in permutations(vertices_of(order)))


def isomorphism_witness(source: Graph, target: Graph, order: int) -> tuple[int, ...] | None:
    for permutation in permutations(vertices_of(order)):
        if relabel(source, permutation) == target:
            return permutation
    return None


def automorphism_count(edges: Graph, order: int) -> int:
    return sum(relabel(edges, permutation) == edges for permutation in permutations(vertices_of(order)))


def neighbors(edges: Graph, vertex: int, universe: Iterable[int]) -> frozenset[int]:
    return frozenset(
        other for other in universe
        if other != vertex and norm_edge(vertex, other) in edges
    )


def degrees(edges: Graph, order: int) -> tuple[int, ...]:
    return tuple(len(neighbors(edges, vertex, vertices_of(order))) for vertex in vertices_of(order))


def triangle_sets(edges: Graph, universe: Iterable[int]) -> tuple[tuple[int, int, int], ...]:
    verts = tuple(universe)
    return tuple(
        triple for triple in combinations(verts, 3)
        if all(norm_edge(left, right) in edges for left, right in combinations(triple, 2))
    )


def induced(edges: Graph, kept: Iterable[int]) -> Graph:
    kept_set = frozenset(kept)
    return frozenset(edge for edge in edges if edge[0] in kept_set and edge[1] in kept_set)


def compact_induced(edges: Graph, kept: Iterable[int]) -> Graph:
    kept_tuple = tuple(sorted(kept))
    compact = {old: new for new, old in enumerate(kept_tuple)}
    return frozenset((compact[left], compact[right]) for left, right in induced(edges, kept_tuple))


def locally_admissible(edges: Graph, order: int) -> bool:
    """Necessary induced condition: common-neighbor counts never exceed lambda/mu."""
    universe = tuple(vertices_of(order))
    rows = tuple(neighbors(edges, vertex, universe) for vertex in universe)
    for left, right in combinations(universe, 2):
        common = len(rows[left] & rows[right])
        ceiling = 1 if norm_edge(left, right) in edges else 2
        if common > ceiling:
            return False
    return True


def support_common(edges: Graph, root: int, point: int, order: int) -> frozenset[int]:
    universe = tuple(vertices_of(order))
    return neighbors(edges, root, universe) & neighbors(edges, point, universe)


def is_side_flag(edges: Graph, order: int, root: int, left: int, right: int) -> bool:
    """Recognize the induced six-vertex flag made by one fibre-side edge."""
    if order != 6 or root in (left, right):
        return False
    if norm_edge(left, right) not in edges:
        return False
    if norm_edge(root, left) in edges or norm_edge(root, right) in edges:
        return False
    support_left = support_common(edges, root, left, order)
    support_right = support_common(edges, root, right, order)
    if len(support_left) != 2 or len(support_right) != 2:
        return False
    if len(support_left & support_right) != 1:
        return False
    support_union = support_left | support_right
    if len(support_union) != 3:
        return False
    if neighbors(edges, root, vertices_of(order)) != support_union:
        return False
    if neighbors(edges, left, vertices_of(order)) != support_left | {right}:
        return False
    if neighbors(edges, right, vertices_of(order)) != support_right | {left}:
        return False
    left_only = next(iter(support_left - support_right))
    right_only = next(iter(support_right - support_left))
    support_edges = induced(edges, support_union)
    return support_edges == frozenset({norm_edge(left_only, right_only)})


def is_diagonal_flag(edges: Graph, order: int, root: int, left: int, right: int) -> bool:
    """Recognize the induced seven-vertex flag made by one fibre diagonal."""
    if order != 7 or root in (left, right):
        return False
    if norm_edge(left, right) not in edges:
        return False
    if norm_edge(root, left) in edges or norm_edge(root, right) in edges:
        return False
    support_left = support_common(edges, root, left, order)
    support_right = support_common(edges, root, right, order)
    if len(support_left) != 2 or len(support_right) != 2 or support_left & support_right:
        return False
    support_union = support_left | support_right
    if len(support_union) != 4:
        return False
    if neighbors(edges, root, vertices_of(order)) != support_union:
        return False
    if neighbors(edges, left, vertices_of(order)) != support_left | {right}:
        return False
    if neighbors(edges, right, vertices_of(order)) != support_right | {left}:
        return False
    if induced(edges, support_left) or induced(edges, support_right):
        return False
    cross = tuple(
        norm_edge(a, b) for a in support_left for b in support_right
        if norm_edge(a, b) in edges
    )
    cross_degrees = Counter(vertex for edge in cross for vertex in edge)
    return len(cross) == 2 and set(cross_degrees.values()) == {1} and set(cross_degrees) == set(support_union)


def rooted_flag_count(edges: Graph, order: int, predicate) -> int:
    return sum(
        predicate(edges, order, root, left, right)
        for root in vertices_of(order)
        for left, right in combinations(vertices_of(order), 2)
    )


def cycle_edges(order: int) -> Graph:
    return frozenset(norm_edge(vertex, (vertex + 1) % order) for vertex in vertices_of(order))


# Explicit, independent graph transcriptions.
PRISM = graph([
    (0, 1), (1, 2), (0, 2),
    (3, 4), (4, 5), (3, 5),
    (0, 3), (1, 4), (2, 5),
])

# Roles: 0=root, 1=x, 2=y, supports A={3,4}, B={5,6}.
H_DELTA = graph([
    (0, 3), (0, 4), (0, 5), (0, 6),
    (1, 2), (1, 3), (1, 4), (2, 5), (2, 6),
    (3, 5), (4, 6),
])

# Visual transcription of panel Z_2 in figure_1.png: outer C6, its opposite
# chord, and a centre joined to two adjacent top and two adjacent bottom nodes.
Z2_DRAWING = graph([
    (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5),
    (2, 5),
    (0, 6), (1, 6), (3, 6), (4, 6),
])

# Hamiltonian-panel transcriptions use a perimeter C7 and list extra chords.
H18_DRAWING = cycle_edges(7) | graph([(6, 1), (5, 2), (0, 4), (0, 3)])
H11_DRAWING = cycle_edges(7) | graph([(0, 2), (0, 5), (1, 4)])

# The six-vertex types used in the incidence derivation.  N3 is two disjoint
# triangles joined by an independent pair of cross edges.  N4 is written in
# its least-mask labelling (mask 1916 under the convention below).
N3_GRAPH = graph([
    (0, 1), (0, 2), (1, 2),
    (3, 4), (3, 5), (4, 5),
    (0, 3), (1, 4),
])
N4_GRAPH = graph([
    (0, 3), (0, 4), (0, 5),
    (1, 2), (1, 3), (1, 5),
    (2, 3), (2, 4),
])


def special_n4_edges(edges: Graph) -> tuple[Edge, ...]:
    """Edges from a degree-2 vertex to a vertex of N4's unique triangle."""
    assert len(edges) == 8
    degree = degrees(edges, 6)
    triangles = triangle_sets(edges, vertices_of(6))
    assert len(triangles) == 1
    triangle = frozenset(triangles[0])
    answer = []
    for left, right in sorted(edges):
        if degree[left] == 2 and degree[right] == 3 and right in triangle:
            answer.append((left, right))
        elif degree[right] == 2 and degree[left] == 3 and left in triangle:
            answer.append((left, right))
    return tuple(answer)


def extension_patterns() -> list[dict[str, object]]:
    """All locally admissible common-neighbor attachments at special N4 edges."""
    masks = {
        canonical_mask(H11_DRAWING, 7): "Hamiltonian H11",
        canonical_mask(H18_DRAWING, 7): "Z2/Hamiltonian H18",
    }
    rows: list[dict[str, object]] = []
    for special in special_n4_edges(N4_GRAPH):
        choices = []
        for size in range(7):
            for attached in combinations(vertices_of(6), size):
                if not set(special) <= set(attached):
                    continue
                extended = N4_GRAPH | frozenset(norm_edge(6, vertex) for vertex in attached)
                if not locally_admissible(extended, 7):
                    continue
                mask = canonical_mask(extended, 7)
                assert mask in masks, (special, attached, mask)
                choices.append({
                    "attached_N4_vertices": list(attached),
                    "canonical_mask": mask,
                    "type": masks[mask],
                })
        assert len(choices) == 2
        assert {choice["type"] for choice in choices} == {
            "Hamiltonian H11", "Z2/Hamiltonian H18"
        }
        rows.append({"special_edge": list(special), "allowed_attachments": choices})
    return rows


def deletion_flags(edges: Graph, expected_n4_mask: int) -> list[dict[str, object]]:
    answer = []
    for deleted in vertices_of(7):
        kept = tuple(vertex for vertex in vertices_of(7) if vertex != deleted)
        compact = compact_induced(edges, kept)
        if canonical_mask(compact, 6) != expected_n4_mask:
            continue
        # Find a concrete N4->card isomorphism and verify that the deleted
        # vertex is the external common neighbor of a special N4 edge.
        target_vertices = tuple(sorted(kept))
        target_index = {old: new for new, old in enumerate(target_vertices)}
        inverse_index = {new: old for old, new in target_index.items()}
        witnesses = []
        for permutation in permutations(vertices_of(6)):
            if relabel(N4_GRAPH, permutation) != compact:
                continue
            for special in special_n4_edges(N4_GRAPH):
                card_left = inverse_index[permutation[special[0]]]
                card_right = inverse_index[permutation[special[1]]]
                if norm_edge(deleted, card_left) in edges and norm_edge(deleted, card_right) in edges:
                    witnesses.append({
                        "N4_special_edge": list(special),
                        "image_edge": [card_left, card_right],
                    })
        assert witnesses
        answer.append({
            "deleted_vertex": deleted,
            "card_canonical_mask": expected_n4_mask,
            "witness": witnesses[0],
        })
    return answer


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    expected_masks = {
        "N3": 5941,
        "N4": 1916,
        "Hamiltonian_H11": 48756,
        "Z2_H18_HDelta": 120568,
    }
    observed_masks = {
        "N3": canonical_mask(N3_GRAPH, 6),
        "N4": canonical_mask(N4_GRAPH, 6),
        "Hamiltonian_H11": canonical_mask(H11_DRAWING, 7),
        "Z2_drawing": canonical_mask(Z2_DRAWING, 7),
        "H18_drawing": canonical_mask(H18_DRAWING, 7),
        "HDelta": canonical_mask(H_DELTA, 7),
    }
    assert observed_masks["N3"] == expected_masks["N3"]
    assert observed_masks["N4"] == expected_masks["N4"]
    assert observed_masks["Hamiltonian_H11"] == expected_masks["Hamiltonian_H11"]
    assert {
        observed_masks["Z2_drawing"],
        observed_masks["H18_drawing"],
        observed_masks["HDelta"],
    } == {expected_masks["Z2_H18_HDelta"]}

    delta_to_h18 = isomorphism_witness(H_DELTA, H18_DRAWING, 7)
    z2_to_delta = isomorphism_witness(Z2_DRAWING, H_DELTA, 7)
    assert delta_to_h18 is not None and z2_to_delta is not None

    side_flags = rooted_flag_count(PRISM, 6, is_side_flag)
    diagonal_flags = rooted_flag_count(H_DELTA, 7, is_diagonal_flag)
    assert side_flags == 6
    assert diagonal_flags == 1
    assert rooted_flag_count(PRISM, 6, is_diagonal_flag) == 0
    assert rooted_flag_count(H_DELTA, 7, is_side_flag) == 0

    prism_aut = automorphism_count(PRISM, 6)
    delta_aut = automorphism_count(H_DELTA, 7)
    assert prism_aut == 12
    assert delta_aut == 4

    special = special_n4_edges(N4_GRAPH)
    assert special == ((1, 5), (2, 4))
    extensions = extension_patterns()
    h11_deletions = deletion_flags(H11_DRAWING, expected_masks["N4"])
    h18_deletions = deletion_flags(H18_DRAWING, expected_masks["N4"])
    assert len(h11_deletions) == 1
    assert len(h18_deletions) == 4

    # Algebraic replay of the standard six-vertex double counts:
    # 6*n1+n4 = nk(k-2)/2 and 3*n1+n3 = nk(k-2)/4.
    # Doubling the second and subtracting the first gives n4=2*n3.
    rhs_five = Fraction(N * K * (K - 2), 2)
    rhs_six_twice = 2 * Fraction(N * K * (K - 2), 4)
    assert rhs_five == rhs_six_twice == 8316

    # The independent N4 flag census gives 2*n4=h11+4*h18 in the
    # Hamiltonian-table notation.  Because Z2 and H18 are the same graph,
    # this cross-checks the all-seven source formula z2=n3-z11/4.  We do NOT
    # identify the graph indexed Z11 with the graph indexed H11: the two
    # source tables use different index conventions.  Their frequencies are
    # forced equal after identifying z2=h18 and comparing the two equations.
    derived_z2 = (Fraction(0), Fraction(1), Fraction(-1, 4))
    normalized_tex = "".join(TEX_SOURCE.read_text(encoding="utf-8").split())
    source_formula = r"z_2=&n_3-\frac{z_{11}}{4},\\"
    assert source_formula in normalized_tex

    base = Fraction(N * K * (K - 2), 4)
    assert base == 4158
    # P=(base-n3)/3, so 6P=2*base-2*n3.  Adding z2 yields:
    e0_affine = (2 * base, Fraction(-1), Fraction(-1, 4))
    assert e0_affine == (8316, -1, Fraction(-1, 4))

    result = {
        "status": "E0_MOTIF_FIRST_MOMENT_AUDIT_PASS",
        "scope": (
            "Clean-room finite graph/isomorphism audit of the side and diagonal "
            "motifs, the N4 extension coefficients, and the resulting E0 first moment."
        ),
        "mask_convention": {
            "edge_order": "(0,1),(0,2),...,(n-2,n-1)",
            "bit_rule": "bit i is one iff edge i is present",
            "canonical_rule": "least integer mask over all vertex permutations",
        },
        "source_binding": {
            "all_seven_tex": str(TEX_SOURCE),
            "all_seven_tex_sha256": sha256(TEX_SOURCE),
            "all_seven_figure_1": str(FIGURE_SOURCE),
            "all_seven_figure_1_sha256": sha256(FIGURE_SOURCE),
            "exact_formula_literal_found": source_formula,
            "formula_affine_coefficients_constant_n3_z11": [
                str(value) for value in derived_z2
            ],
            "note": (
                "The graph drawings are manually transcribed as explicit edge lists; "
                "the PNG itself is not machine-vectorized by this audit."
            ),
        },
        "canonical_crosscheck": {
            "expected_masks": expected_masks,
            "observed_masks": observed_masks,
            "HDelta_to_H18_vertex_permutation": list(delta_to_h18),
            "Z2_drawing_to_HDelta_vertex_permutation": list(z2_to_delta),
            "identification": "HDelta = all-seven Z2 = Hamiltonian H18",
        },
        "motifs": {
            "triangular_prism": {
                "order": 6,
                "edge_count": len(PRISM),
                "degree_multiset": sorted(degrees(PRISM, 6)),
                "automorphism_order": prism_aut,
                "rooted_side_flags": side_flags,
                "rooted_diagonal_flags": 0,
                "unlabelled_coefficient_in_sum_S": 6,
                "labelled_embedding_coefficient_in_sum_S": "1/2",
            },
            "HDelta_Z2_H18": {
                "order": 7,
                "edge_count": len(H_DELTA),
                "degree_multiset": sorted(degrees(H_DELTA, 7)),
                "automorphism_order": delta_aut,
                "rooted_side_flags": 0,
                "rooted_diagonal_flags": diagonal_flags,
                "unlabelled_coefficient_in_sum_D": 1,
                "labelled_embedding_coefficient_in_sum_D": "1/4",
            },
        },
        "hamiltonian_incidence_crosscheck": {
            "N3_canonical_mask": observed_masks["N3"],
            "N3_description": "two disjoint triangles plus an independent two-edge cross matching",
            "N4_canonical_mask": observed_masks["N4"],
            "N4_degree_multiset": sorted(degrees(N4_GRAPH, 6)),
            "N4_triangle_count": len(triangle_sets(N4_GRAPH, vertices_of(6))),
            "N4_special_edges": [list(edge) for edge in special],
            "special_edge_definition": (
                "edge from a degree-2 vertex to a degree-3 vertex in N4's unique triangle"
            ),
            "locally_admissible_extensions": extensions,
            "Hamiltonian_H11_N4_deletion_flags": h11_deletions,
            "Z2_H18_N4_deletion_flags": h18_deletions,
            "six_vertex_double_counts": [
                "6*n1+n4=n*k*(k-2)/2",
                "3*n1+n3=n*k*(k-2)/4",
                "therefore n4=2*n3",
            ],
            "hamiltonian_seven_vertex_flag_identity": "2*n4=h11+4*h18",
            "hamiltonian_conclusion": "h18=n3-h11/4",
            "all_seven_source_conclusion": "z2=n3-z11/4",
            "cross_table_bridge": (
                "Z2 and H18 are isomorphic, hence z2=h18; comparison forces "
                "the numerical frequency equality z11=h11. This is not a graph-index identification."
            ),
        },
        "E0_first_moment": {
            "definitions": "E0(r)=S(r)+D(r)",
            "side_identity": "sum_r S(r)=6*P",
            "prism_identity": "P=(4158-n3)/3",
            "diagonal_identity": "sum_r D(r)=z2",
            "z2_identity": "z2=n3-z11/4",
            "conclusion": "sum_r E0(r)=8316-n3-z11/4",
            "affine_coefficients_constant_n3_z11": [str(value) for value in e0_affine],
            "frequency_convention": "P,n3,n4,z2,z11 count unlabelled induced vertex subsets",
            "labelled_embedding_translation": {
                "sum_S": "inj(prism)/2 because |Aut(prism)|=12",
                "sum_D": "inj(HDelta)/4 because |Aut(HDelta)|=4",
            },
        },
        "E0_second_moment": {
            "exact_flag_expansion": (
                "sum_r E0(r)^2 = T + 2*sum_r[binom(S(r),2)+S(r)D(r)+binom(D(r),2)], "
                "where T=sum_r E0(r)"
            ),
            "balanced_integer_lower_bound": (
                "If T=99*q+s with 0<=s<99, then sum_r E0(r)^2 >= "
                "(99-s)q^2+s(q+1)^2 = ceil(T^2/99)."
            ),
            "substitution": "T=8316-n3-z11/4",
            "closure_warning": (
                "Pairs of two rooted fibre-edge flags can span as many as 13 vertices. "
                "The direct square expansion therefore is not a linear 6/7-vertex motif count; "
                "an indirect reduction would require additional identities and is not claimed here."
            ),
        },
        "limitations": [
            "The side/prism identity and P=(4158-n3)/3 are prerequisite SRG double counts.",
            "The two displayed six-vertex equations are replayed algebraically; this file does not enumerate an ambient 99-vertex graph.",
            "Manual figure transcription is checked by canonical masks, not extracted automatically from raster pixels.",
            "Hamiltonian H11 and all-seven Z11 are distinct table labels and are not asserted to be isomorphic.",
            "This is not a machine-checked formal proof.",
            "No srg(99,14,1,2) is constructed or excluded; Conway's 99-graph status remains UNKNOWN.",
        ],
    }

    markdown = f"""# E0 small-motif first-moment audit

Status: **{result['status']}**.

This is a clean-room finite audit: it imports no project discovery code.  It
starts from explicit edge lists and enumerates every permutation of six or
seven vertices.  Frequencies count **unlabelled induced vertex subsets**.

## Conventions and graph identification

Edges are ordered lexicographically `(0,1),(0,2),...`; the canonical mask is
the least mask under all vertex permutations.  Three independent
transcriptions have the same canonical mask:

```text
diagonal flag HDelta     {observed_masks['HDelta']}
all-seven panel Z2       {observed_masks['Z2_drawing']}
Hamiltonian panel H18    {observed_masks['H18_drawing']}
```

Thus `HDelta = Z2 = H18`, with canonical mask **120568**.  It has 11 edges,
degree multiset `(3,3,3,3,3,3,4)`, and automorphism group order 4.  The unique
degree-4 vertex is the root, its two non-neighbours form the unique diagonal
edge, so every induced copy supplies exactly one `(root, diagonal)` flag.

## Side and diagonal coefficients

For a side edge `xy`, the supports of `x,y` at root `r` share one vertex; the
two remaining support vertices are the endpoints of one root-neighbourhood
matching edge.  The six forced vertices induce a triangular prism.  Conversely
every choice of one of a prism's six vertices as root recovers exactly one
side flag.  Exhaustive rooted-role checking gives

```text
sum_r S(r) = 6 P.
```

For a diagonal edge the two size-two supports are complementary and their
four root-neighbours induce a perfect matching.  Together with `r,x,y` this
is exactly HDelta, and the unique-root argument gives

```text
sum_r D(r) = z2.
```

In labelled-injective conventions these become `sum S=inj(prism)/2` and
`sum D=inj(HDelta)/4`, since the automorphism orders are 12 and 4.

## Independent origin of the quarter coefficient

Use the six-vertex type N4 of canonical mask 1916.  It has one triangle and
exactly two distinguished edges: an edge from a degree-2 vertex to a
degree-3 vertex in that triangle.  Such an edge has no common neighbour
inside N4, so lambda=1 supplies one unique external common neighbour.

For each distinguished edge, exhaustive checking of all 64 attachment
subsets under the induced lambda/mu upper bounds leaves exactly two patterns:
one Hamiltonian-H11 pattern and one Hamiltonian-H18 pattern.  Conversely H11
has one N4 deletion flag and H18 has four.  Double counting therefore gives

```text
2 n4 = h11 + 4 h18.                                 (1)
```

The standard six-vertex counts

```text
6 n1+n4 = n*k*(k-2)/2,
3 n1+n3 = n*k*(k-2)/4
```

give `n4=2n3` by doubling the second and subtracting the first.  Substitution
in (1) independently recovers the Hamiltonian-table relation

```text
h18 = n3-h11/4.
```

The all-seven table uses `Z` indices, not `H` indices.  Its hashed TeX input
independently states `z2=n3-z11/4`.  Since the graph transcriptions prove
`Z2=H18`, their frequencies satisfy `z2=h18`; comparison also yields the
numerical frequency equality `z11=h11`.  No assertion that the two graphs
indexed `Z11` and `H11` are isomorphic is used here.

## First moment

With the already established prism identity `P=(4158-n3)/3`, we obtain

```text
sum_r E0(r)
 = 6P+z2
 = 8316-n3-z11/4.                                  (2)
```

This corrects the old, quarantined `sum E0=6P` claim: the missing term is
precisely the induced-Z2 count.

## Second moment boundary

Writing `T` for (2), the exact flag expansion is

```text
sum_r E0(r)^2
 = T + 2 sum_r [C(S(r),2)+S(r)D(r)+C(D(r),2)].
```

Hence, if `T=99q+s`, `0<=s<99`, integrality gives the sharp mean-only bound

```text
sum_r E0(r)^2 >= (99-s)q^2+s(q+1)^2 = ceil(T^2/99).
```

The pair terms can span up to 13 vertices, so the direct square expansion does
not close using only six- and seven-vertex motif frequencies.  This does not
rule out a further indirect SRG identity; none is asserted here.

## Boundary

This is an executable finite audit, not a formal proof.  It neither constructs
nor excludes `srg(99,14,1,2)`; Conway's 99-graph problem remains **UNKNOWN**.
"""

    atomic_write(OUTPUT_JSON, json.dumps(result, indent=2) + "\n")
    atomic_write(OUTPUT_MD, markdown)
    print(json.dumps({
        "status": result["status"],
        "json": str(OUTPUT_JSON),
        "markdown": str(OUTPUT_MD),
        "canonical_HDelta_Z2_H18": observed_masks["HDelta"],
        "side_flags_per_prism": side_flags,
        "diagonal_flags_per_HDelta": diagonal_flags,
        "N4_deletion_multiplicities_H11_H18": [len(h11_deletions), len(h18_deletions)],
        "sum_E0": result["E0_first_moment"]["conclusion"],
    }, indent=2))


if __name__ == "__main__":
    main()
