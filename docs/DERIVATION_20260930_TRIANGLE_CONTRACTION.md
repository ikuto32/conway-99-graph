# Candidate exact contraction constraints for an actual residual partition

These are conditional necessary identities, pending independent review. Assume
an actual SRG(99,14,1,2) in the identity-cross family and its residual twenty
triangles, whose existence is independently checked in
`AUDIT_20260930_IDENTITY_P_TRIANGLE_PARTITION.md`. Let D be the residual60
adjacency, F the36-by60 core incidence, C the inner36 adjacency, and R the
60-by20 indicator matrix of those **actual** triangles. Write T=FR.

An outside vertex cannot be adjacent to two vertices of a triangle: the edge
between those two vertices would have both the triangle's third vertex and
that outside vertex as common neighbors, violating lambda=1. Thus every
intertriangle block of D is a matching. Each residual vertex has its two
triangle neighbors and six external neighbors in six different triangles.
Consequently

`W = D R - 2R`

is binary, vanishes on a vertex's own triangle, has row sums6 and column
sums18. The matrix `B=R^T W` is symmetric, has diagonal0, entries in{0,1,2,3}
and row sums18. Its p,q entry counts intertriangle edges.

Use R-transpose R=3I and DR=2R+W. Symmetry of D gives

`R^T(D^2+D)R = (DR)^T(DR) + R^T DR = 18I + 5B + W^T W`.

The target's residual equation is `F^T F + D^2 + D = 12I + 2J`.
Sandwiching it by R gives the exact necessary relation

`T^T T + 5B + W^T W = 18I + 18J`.

For p != q, this says `T_p^T T_q + 5 B_pq + (W^T W)_pq = 18`,
where the last term counts vertices outside both triangles adjacent into each.
All terms are nonnegative integers. Thus

`0 <= B_pq <= min(3, floor((18-T_p^T T_q)/5))`, with `sum_q B_pq=18`.

The target mixed equation is `FD=2J-(I+C)F`. Multiplying by R and subtracting
2T gives a second exact necessary relation,

`F W = 6J - (C+3I)T`.

This combines actual residual edges with triangle support sums. It is stronger
data than mere existence of disjoint factor-column triples. The recorded
60-vertex positive control verifies only the contraction algebra and structural
W/B constraints; it provides no F and satisfies no claimed target equation.

The coarse60 cyclic cover is a disjoint-column partition for arbitrary bits,
but there is no justification that a completion must use it as its actual D
triangle partition. Fixing that cover would be an additional restriction.
These formulas therefore justify no current exclusion, general normalization,
new solver run or factor construction. No novelty assertion is made.
