# Independent written audit: small ternary residual supports

Discovery producer: ROOT. Independent verifier: Checkpoint.
The source is `docs/CANDIDATE_20261003_TERNARY_SMALL_DEFECT_SUPPORT_V1.md`,
SHA256 d887daf8e80a8751049f472c54f80d7c61abd245a40020ed93c9114d22677ffd.
Its candidate-labelled original bytes remain unchanged. This audit uses exact
integer and finite-field arithmetic on paper; no program, solver, mathematical
fixture or enumeration command was executed. The written support matrices below
are not adjacency realizations. Novelty and external review are not established.

## Exact statement checked

For every symmetric binary zero-diagonal99-by-99 matrix A with exactly14 ones
in each integer row, let r_uv=(A^2)_uv+A_uv-2 for u<v and let F3 be the number
of these unordered residuals not divisible by3. Then F3 belongs to
{0,4} union {6,7,...,4851}. If F3=4, the four nonzero residue pairs form a
simple four-cycle on four vertices, with residues1,2,1,2 in cyclic order.
This is necessary only; no degree14 graph realizing four defects or any other
allowed value is asserted. No adjacent-pair, triangle-incidence, automorphism,
numerical-relaxation or search-coverage premise is used.

## Separate derivation

Start directly from all ordered common-neighbor counts. For a fixed vertex u,
sum_v (A^2)_uv equals sum_w A_uw sum_v A_wv =14*14=196. Symmetry and binary
zero-diagonal entries give (A^2)_uu=sum_w A_uw A_wu=14. Thus, summing only over
the98 other vertices,

 sum_[v!=u] ((A^2)_uv+A_uv-2) = (196-14)+14-2*98 =0.

This computes the complete residual-row sum without relying on an existing
claim, status or the discovery's matrix-vector derivation. The diagonal residual
of A^2-12I+A-2J is14-12-2=0. Symmetry makes each unordered residue a single
shared edge label at its two endpoints. Replace every nonzero residue by a sign:
residue1 has sign+1, residue2 has sign-1, with signs interpreted in GF(3).

Let H have one edge for each nonzero unordered residue, labelled by that sign.
H is simple and loopless. At each vertex the sum of its incident signs is0
over GF(3). An endpoint of one edge would have nonzero sum, so every nonisolated
vertex has degree at least2. At degree2, the signs must be opposite: same signs
sum to+2 or-2, both nonzero. At degree3 the signed integer sum is one of
-3,-1,+1,+3; only-3 or+3 vanish modulo3, so all three signs agree.

Each nontrivial connected component contains at least3 vertices and at least3
edges. Indeed its minimum degree2 implies edges>=vertices, and simplicity on
one or two vertices forbids degree2. Consequently, when0<e=|E(H)|<=5 there is
exactly one nontrivial component. Isolated vertices are excluded from its count v.
The handshaking identity gives2e>=2v, hence v<=e. Simplicity gives e<=v(v-1)/2.
These two bounds classify every small case without selecting representatives by
a target-graph symmetry or using an enumeration catalogue:

* e=1 or2: v<=e<=2, so at most one simple edge is possible. Neither case can
 meet minimum degree2.
* e=3: necessarily v=3 and H is a triangle. Every degree is2. Following an
 edge sign around a cycle, each successive sign is its negative; closing an
 odd cycle requires s=-s. This gives2s=0 in GF(3), impossible for s=+1 or-1.
* e=4: three vertices permit at most3 edges, so v=4. Total degree8 and minimum
 degree2 force every degree2. A connected simple2-regular graph on four vertices
 is C4. The same recursion permits exactly the alternating nonzero signs.
* e=5: v is4 or5. If v=5, degree sum10 forces a connected2-regular C5, excluded
 by the odd-cycle argument. If v=4, the simple graph has all6 possible pairs
 except one: K4-e. Its two degree3 vertices x,y are adjacent. Degree3 forces
 every edge at x to have one sign s and every edge at y to have one sign t.
 Their shared xy edge requires s=t. Either degree2 vertex now has incident sum
 2s, nonzero modulo3, a contradiction. This covers all5-edge simple supports.

There are99*98/2=4851 possible unordered pairs. The exhausted cases rule out
F3=1,2,3,5 and identify the exact necessary4-edge shape and labels. Nothing here
proves realizability of a support by an adjacency matrix, and the argument does
not classify larger supports.

## Written falsification inventory (12 checks, zero executed fixtures)

1. Independently expand the complete off-diagonal row sum as182+14-196=0.
   Degree only modulo3 does not justify the exact integer row calculation.
2. Compute the diagonal using symmetry and binary entries:14-12-2=0. Dropping
   symmetry, simplicity or the zero diagonal leaves this domain proof unavailable.
3. Check that each pair is represented at both endpoints by the same residue.
   An asymmetric directed triangle may have different labels at its endpoints
   and is outside this simple undirected support argument.
4. List the degree2 possibilities(+,+),(+,-),(-,+),(-,-): only the middle two
   have zero sum modulo3. No omitted nonzero term can be silently discarded.
5. List degree3 by the number of+ signs0,1,2,3: sums-3,-1,1,3, so only all-
   or all+ are permitted. Mixed signs cannot repair K4-e.
6. Challenge disconnected supports: every nontrivial component needs at least
   three edges, so two components already need at least6. Two-vertex doubled
   edges would violate simplicity and are not an omitted small case.
7. Checke1/e2 against v<=e and e<=v(v-1)/2, using only nonisolated vertices.
   Including isolated vertices in v would invalidate the classification bound.
8. Traverse both odd cycles C3 and C5: after an odd number of sign reversals,
   the closing edge would have to equal its own negative. Neither nonzero label
   in GF(3) satisfies this equality.
9. Written positive C4: edges12,23,34,41 have residues1,2,1,2. Each complete
   support row sums to3=0 modulo3. The unused95 vertices have zero rows. This
   support matrix is not claimed to be a degree14 adjacency residual.
10. Written K4-e falsification: the shared high-degree edge fixes one sign for
    all five edges; each low-degree row then sums to+2 or-2. There is no second
    degree sequence or disconnected5-edge support left untested by the bounds.
11. Written boundary K4 with all six edges residue1: every row sums to3, so it
    is a valid modular support. This shows the method does not rule out every
    nonzero support; it is not a realized degree14 graph or construction.
12. Delete one edge from either written positive support. In C4 its endpoints
    have support degree1; in K4 its endpoints each retain two residues1. Both
    modifications break a complete row sum. Loops, partial residual sampling,
    or a merely global residue sum cannot replace the row conditions.

## Verdict and limits

VERIFIED within the exact universal necessary scope above by this separate
human-checkable written derivation. The complete list of simple support cases
e<=5 has been challenged. Agreement between agents and finite examples is not
the proof; the row arithmetic and exhaustion argument are the proof.

The proof shares elementary exact row-sum arithmetic with the prior energy and
ternary-exactness notes, but invokes neither theorem as a premise or ledger
dependency. The producer's support reduction supplies the subject being audited;
the verifier independently derives it from the complete CN row sums and signed
handshaking bounds. No discovery code or previous checking implementation was
imported. Formalization, external review, novelty and realizability of four or
larger defects remain unestablished. There is no target graph, general
nonexistence proof, target-wide exclusion, optimizer/cache approval or coverage
percentage. Overall search coverage: UNKNOWN; no validated denominator.
