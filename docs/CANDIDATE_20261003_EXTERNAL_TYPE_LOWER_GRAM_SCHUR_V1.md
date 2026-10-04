# Corrected lower-Gram exterior-type test and its one-type redundancy

Status: **SOURCE_ONLY CANDIDATE**, requiring separate written verification.
The proposed exterior-type Schur test originated with `/root`; the corrected
shift and the derivation below were reconstructed by `/root/structural`.
The one-type redundancy statement is a separate Structural discovery.
No fixed 472-type inverse, pair evaluation, enumeration, numerical spectrum,
solver, executable fixture or formal checking has run for this note. Neither
author approves their own discovery. No target conclusion or novelty is claimed.

## 1. Correct the shift before using the proposed test

Let A be the complete real adjacency matrix of a hypothetical simple graph
with parameters (99,14,1,2). Then

    A 1 = 14 1,             A^2 + A = 12 I + 2 J.

On the orthogonal complement of 1, the symmetric matrix A has eigenvalues
3 and -4. Their multiplicities follow from dimension and trace:

    f + g = 98,             14 + 3 f - 4 g = 0,
    f = 54,                 g = 44.

Consequently the original Root proposal that A+3I is positive semidefinite
is an incorrect spectral consequence: its spectrum is 17, 6^54, (-1)^44.
The corrected matrix is

    Q = A + 4 I,            spectrum(Q) = 18, 7^54, 0^44,
    Q >= 0,                 rank(Q) = 55.

This corrects the mathematical premise before any pruning or computation.
It is not a proof that the target exists or does not exist. In particular a
small selected-triangle graph may have H+3I positive definite without making
the full target A+3I positive semidefinite.

## 2. Exact single-type and pair-type necessary conditions

Fix a set U of m vertices of the hypothetical target, and let H=A[U,U] be
the **complete induced** adjacency on U. Assume K=H+4I is positive definite.
For each exterior vertex z write its binary neighborhood type on U as
t_z=A[U,z]. With T the matrix of these columns and A_out the actual exterior
adjacency, block Gaussian congruence gives

    Q = [[K, T], [T^T, 4 I + A_out]],
    S = 4 I + A_out - T^T K^(-1) T >= 0,
    rank(S) = 55 - m.

For any occurring type t, the one-by-one principal condition is

    q(t) = t^T K^(-1) t <= 4.

For two **distinct** exterior vertices of types t,u, let a be their actual
adjacency, a in {0,1}. The two-by-two principal condition is exactly

    q(t) <= 4,    q(u) <= 4,
    (a - t^T K^(-1) u)^2 <= (4-q(t))(4-q(u)).

This includes two distinct vertices of the same type. If neither choice of
a satisfies the inequality, those two types cannot occur together; if exactly
one choice satisfies it, their adjacency is forced by this necessary test.
Equality is allowed. These are exact rational comparisons when H is integral
and K invertible; no floating rounding criterion is part of the statement.

For m=17 the full Schur matrix has size 82 and rank 38. Passing every one- and
two-by-two test does not certify that whole matrix is positive semidefinite,
has that rank, has binary exterior adjacency, or completes the target. The
tests do not construct an exterior graph or prove an integer moment solution.

If K is singular, merely writing K^(-1) is invalid. The necessary block
conditions first require K positive semidefinite and every column of T in
range(K). Then a generalized-inverse Schur complement is available, with
rank(Q)=rank(K)+rank(S). That singular case is outside the positive-definite
test just stated and has not been implemented here.

The induced hypothesis is essential. Replacing H by a selected-triangle
subgraph that omits actual edges within U need not give a principal block of
Q. Such an occurrence must use its complete induced H, including all added
edges, before any of these conditions can be applied.

## 3. Single-type redundancy for the selected seventeen-point base

Consider a finite simple base H that is exactly the edge union of a linear
collection of selected triangles on 17 points. Assume its selected incidence
degrees are 3 at two points s,t and 2 at the other fifteen points; s,t are
adjacent on a selected triangle; and every edge of H already has its unique
common neighbor inside H. These are explicit geometry hypotheses, not an
assertion that an arbitrary target contains this base or that the selected
triangles exhaust its induced graph.

Let B0 be the ordinary 0/1 point-by-selected-triangle incidence matrix and
let d denote those selected incidence degrees. Linearity gives the exact
integer identity

    H = B0 B0^T - diag(d),
    K = H+4I = B0 B0^T + D,
    D = diag(4-d) = diag(1 at s,t; 2 elsewhere).

Thus K is positive definite and K >= D > 0, so K^(-1) <= D^(-1).
For a binary type t supported on k points, containing c of {s,t},

    q(t) <= t^T D^(-1) t = (k+c)/2.

The inequality is strict for nonempty t. For completeness, the exact inverse
identity is

    K^(-1) = D^(-1)
      - D^(-1) B0 (I+B0^T D^(-1) B0)^(-1) B0^T D^(-1).

The middle matrix is positive definite. Every base point lies in a selected
triangle, and a nonempty nonnegative t gives B0^T D^(-1)t nonzero. Hence the
subtracted quadratic form is strictly positive. This argument uses no
computed inverse or spectrum of a particular labelled base.

Now suppose this exact H is induced in the target and t occurs outside it.
Because each edge's one common neighbor is already inside H, t cannot contain
both ends of any base edge. In particular c<=1 because s,t are adjacent.
The target neighborhood of the exterior vertex is seven disjoint edges:
each of its fourteen neighbors has precisely one neighbor in that
neighborhood by lambda=1. An independent subset of that neighborhood has
size at most seven. Since H[t] is independent, k<=7. Therefore

    t nonempty  =>  q(t) < (k+c)/2 <= 4,
    t empty     =>  q(t) = 0.

Every type obeying the already stated independent-set and capacity restrictions
passes the single-type q<=4 test. This is a universal redundancy statement
under the exact base hypotheses; it requires no enumeration of the saved
472 types. It does **not** imply that the pair-type inequalities are redundant.
Their information content for the fixed model remains unknown here.

For the standard family labelling, the two selected-degree-3 points are 0,1,
and they are adjacent on (0,1,2). The proof does not treat them as nonadjacent.
It also applies to any relabelling satisfying the explicit same hypotheses.
The current 5184 producer outputs remain candidate finite data pending the
different-author full replay; this paper does not turn them into a gate.

## 4. Archive overlap and current scope

The shifted target Gram and Schur mechanism are historical, not new here:

* `docs/AUDIT_20260930_TARGET_MODULAR_RANKS.md`, SHA256
  `c819ec41287a1a5394d84e2031b6cd2ba564ed8c9771082363dc46ad11a894ed`,
  gives the target roots and multiplicities used above.
* `docs/DERIVATION_20260930_TRIANGLE39_GRAM_SOS.md`, SHA256
  `1dead12449d33270d3adca585fc44616d4865bfe8fbe9532b7412861cbd544fb`,
  already gives A+4I positivity, global rank55 and a core redundancy result.
* `acceleration/theory_20260930_closed28_lower_gram_redundancy.md`, SHA256
  `2b998ef3fbdc32c4b53ddf705f36ad65c46b8645ef5773c0dca6bf1673f5acd6`,
  already uses an exact inverse and a two-by-two Schur complement. The current
  accepted claim C-CLOSED-TWO-NEIGHBORHOOD-LOWER-GRAM-REDUNDANCY revision2
  remains its own conditional closed-neighborhood result.
* `acceleration/audit_20260930_rook_orbit_gram.py`, SHA256
  `5c66e7c81c4bdddebe92cf0cabd552f096e6932959449e982acaf8e7ed44b5db`,
  contains the polynomial projection proof of the lower target Gram; it was
  read as source, not imported or executed for this note.
* `docs/CANDIDATE_20261003_SEVENTEEN_POINT_EXTERNAL_NEIGHBOR_MOMENTS_V1.md`,
  SHA256 `70ef6392e86c6b9a3c9c6eac9b5d72abb9ea25741d3649282f66ac200bb93349`,
  records the independent-type capacity and a different exterior-moment Gram.
* The original seventeen-point circuit note, SHA256
  `f6f9e883b577d6969eafaac9239c37d637804786a08a6b5e676cebe0208e576b`,
  proves local H+3I positivity under selected incidence degrees at most three;
  this does not repair the incorrect full-target A+3I premise.

The archive search and selected whole-source reads establish these overlaps,
not exhaustive absence of other prior Schur tests. No new rank bound is
claimed. The one-type redundancy proof is the separately stated candidate
consequence in section3 and has not yet received a different-author audit.

## 5. Written falsification boundaries and outstanding checks

The following are handwritten logical checks, with zero executable controls:

1. The target -4 eigenspace makes the original shift3 premise fail.
2. Local positivity of H+3I is distinguished from full-target positivity.
3. Omitting induced edges invalidates the principal-block substitution.
4. A singular K requires a range condition before generalized inversion.
5. The single empty type has q=0 and must not be discarded.
6. Two distinct exterior vertices may have the same type and either adjacency.
7. A vanishing diagonal slack forces the relevant pair Schur entry to vanish.
8. Pairwise conditions alone do not certify the full Schur matrix or its rank.
9. For a nonempty binary type the Woodbury correction is strictly positive.
10. The capacity7 conclusion uses an independent type; it is not copied to an
    edge-added base containing an unsaturated internal edge.
11. Both centers are adjacent, so the exact base forbids a type containing both.
12. The one-type proof neither evaluates actual472 pairs nor excludes a target.

Any future pair-type computation needs frozen exact source and type universe,
positive/corrupt controls, independent verification, declared output criteria
and a separately authorized bounded invocation. None is authorized here.
