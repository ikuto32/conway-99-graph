# Independent derivation of the triangle-path weight-five lower count

Written by `/root/checkpoint_audit` on 2026-10-03 (Asia/Tokyo). This is a
separate derivation of `/root/structural`'s candidate statement. Finite raw
artifact checking and its calibration are separate; this file launches no
computation and establishes no Conway-99 resolution or novelty claim.

Let G be any finite simple graph such that every adjacent pair has exactly
one common neighbor. Let T be the complete set of its actual triangles,
and let r_v count members of T containing v. Let B have the binary vertex
incidence vectors of T as its columns. Define

    P = sum over t in T, then unordered {u,v} subset t,
        of (r_u - 1)(r_v - 1).

Then the binary image code im(B) contains at least ceil(P/2) distinct words
of weight five. Neither regularity nor a restriction on common neighbors
of nonadjacent vertices is needed for this general statement.

## Counting actual paths

Distinct triangles cannot share an edge: its two triangle completions would
be different common neighbors. Fix a triangle {u,v,r}, an unordered pair
{u,v} of its vertices, another triangle U through u and another triangle V
through v. U cannot meet the central triangle elsewhere, and similarly
for V. U and V cannot coincide, since they would share its edge uv. If
they met at x, then x would be a common neighbor of u and v. The unique
such neighbor is r, whereas U and V cannot contain r. Thus U and V are
disjoint. Write them as {u,a,b} and {v,c,d}; all seven displayed vertices
are different.

Every such choice yields an unordered three-triangle path, with one
central triangle and distinct central intersection vertices. Conversely
the intersection graph of such a path determines its unique central
triangle and the unordered pair of intersection vertices. Thus choices
are counted exactly once by P. The unordered pair {u,v} does not introduce
an extra orientation factor.

## Recovering a path from its image

The binary sum of the three path triangles is supported on
S={a,b,c,d,r}. The edges ab and cd are present. Vertex r is nonadjacent
to each of the other four vertices. For example, if ra were an edge,
then adjacent pair (u,a) would have common neighbors b and r, contradicting
uniqueness. The same reasoning treats b,c,d.

The cross edges between {a,b} and {c,d} form a matching. If a were adjacent
to both c and d, edge cd would have common neighbors v and a. The same
argument bounds the cross degree of each endpoint by one. No hypothesis
about nonadjacent common neighbors is used here.

Consequently the induced graph on S is exactly one of
2K2+K1, P4+K1, C4+K1. The isolated vertex r is unique. On its other four
vertices there are respectively one, one, or two perfect matchings. For
each possible matching, each matched edge has a unique common neighbor
in the whole graph. This reconstructs its actual end triangle uniquely.
The two reconstructed vertices u,v and r determine the central triangle.
Checking distinctness and the stated intersection pattern either rejects
that matching or recovers exactly one unordered path. Thus S has at most
two path preimages. This argument is an inverse, not an assumption that
every weight-five codeword comes from a three-triangle path.

Each path image is an actual word of im(B); grouping P paths into fibers
of size at most two proves the lower bound. Zero paths and isolated graph
vertices cause no exception.

## Target specialization and character normalization

For any hypothetical srg(99,14,1,2), the adjacent-pair hypothesis holds.
Every vertex belongs to seven actual triangles: its fourteen incident
edges are each completed uniquely, and each incident triangle supplies
two of them. Hence there are 99*7/3=231 actual triangles, and

    P = 231*3*(7-1)^2 = 24948,
    |{y in im(B): wt(y)=5}| >= 12474.

For C=ker(B transpose) over GF(2), write A_w for the number of its words
of weight w and M=|C|=1+sum_{w>0} A_w. Orthogonality of binary characters
gives

    sum_{w>=0} A_w K_5(w) = M |{y in im(B): wt(y)=5}|,
    K_5(w) = sum_{s=0}^5 (-1)^s binom(w,s) binom(n-w,5-s),

where out-of-range binomial coefficients are zero. Indeed, summing the
character (-1)^(c dot y) over c in C gives M for y in C perpendicular
=im(B), and zero otherwise; then sum over all five-subsets y.

For any valid lower count L this implies exactly

    sum_{w>0} A_w (L-K_5(w)) <= binom(n,5)-L.

At the target, binom(99,5)=71523144, L=12474, and the positive denominator
is 71510670. Dividing each coefficient by that denominator gives a row
with right side one using exact rational arithmetic. This does not assume
a nonzero kernel, a rank upper bound, or any unverified support-weight
restriction. Existing rank/weight statements remain separate dependencies
if a later encoding uses them.

## Falsification obligations for the separate finite checker

Rook9 must yield eighteen paths, nine distinct path images, and fibers
of size exactly two. This falsifies injectivity. A loose three-triangle
chain supplies a single path and image; a loose four-cycle supplies P4
supports. Full image enumeration on the small fixtures must contain every
path image. Pasch and K7 must be rejected for failing the adjacent-pair
hypothesis; K7's repeated path supports must explicitly falsify extending
the two-preimage statement outside that hypothesis. Raw support, isolated
vertex, induced-edge, matching, completion, fiber, count and formula
corruptions must fail at their designated checking stages. Finite agreement
is calibration and artifact checking, not a replacement for the universal
inverse above.
