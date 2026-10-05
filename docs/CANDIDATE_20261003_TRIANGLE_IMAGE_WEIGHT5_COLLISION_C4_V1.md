# Candidate strengthening of the triangle-image weight-five count

Discovery author: `/root/structural`. Recorded: 2026-10-02T21:57:44+00:00.
Status: CANDIDATE, pending independent written derivation and complete finite
controls. This file records no new optimizer run, claim registration or target
resolution. Novelty is UNKNOWN.

Let G be a finite simple graph in which every adjacent vertex pair has exactly
one common neighbor. Let B have one column for every actual triangle, and let
D be its binary column space. Let P count unordered sets of three distinct
triangles whose triangle-intersection graph is a path, with the two intersections
at distinct points of its middle triangle. Let C4(G) count induced four-vertex
sets that form a cycle. Let N5 count all weight-five words of D.

The proposed statement is

`N5 >= max(ceil(P/2), P-C4(G))`.

For a target graph srg(99,14,1,2), it implies the sharper necessary count

`N5 >= 24948-2079 = 22869`.

The existing weight-five path proof is reused as an explicit premise:
`acceleration/audit_20261003_triangle_image_weight5_v1_proof.md`, SHA256
`8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee`,
independently checked in
`acceleration/results/20261003_independent_review/weight5_full02/summary.json`,
SHA256 `dedb5c3affcfd0edb98a1d97ebdc973290b53b67ecbb76f3d78135b2bea688f2`.
Those immutable records establish the prior statement, not this strengthening.

## Candidate collision argument

Each path can be written
`{p,a,b}, {p,q,r}, {q,c,d}`. Its XOR support is
`{a,b,r,c,d}`. The previous lambda-one argument gives exactly one isolated
vertex r in the induced support graph. The other four vertices have their two
endpoint edges, and any cross edges form a matching. Their induced graph is
therefore 2K2, P4 or C4. Every path inverse corresponds to a perfect matching
on these four vertices; edge completion determines its deleted intersection
points, and their central edge completion determines r. There are at most two
path preimages of a support.

Let X be the number of distinct weight-five support words produced by paths,
and let Z count those with exactly two path preimages. Then `P=X+Z`, hence
`X=P-Z`. A support with two preimages has two distinct perfect matchings on its
four nonisolated vertices; it therefore contains an induced C4.

Map every such double-preimage support to this four-set. This map is injective.
Indeed, fix an induced C4. Choose either of its two perfect matchings. Each
matching edge has one unique triangle completion, fixing the two deleted
intersection points p,q. If this matching comes from an actual path, p and q
are adjacent and their edge has one unique triangle completion r. Thus r is
fixed by the C4 and that matching. Any double-preimage support mapped to the
C4 must use this same matching and this same r. It is the same five-set.
Consequently `Z<=C4(G)`, `X>=P-C4(G)`, and `N5>=X` gives the new bound.
The earlier `X>=ceil(P/2)` remains valid and can be stronger for some graphs.

This injection counts support words, not selected inverse paths or labelled
cycles. A support cannot choose a different isolated vertex: the induced
support graph has exactly one. Existence of a central edge or equality of the
two matching reconstructions is not assumed for every C4; these are necessary
conditions only for a C4 that actually receives a double-preimage support.

## Target C4 count

For srg(99,14,1,2), a nonadjacent pair u,v has exactly two common neighbors p,q.
They are nonadjacent: otherwise their edge would have both u and v as common
neighbors, contradicting lambda=1. Hence these four vertices induce a C4.
Conversely every induced C4 has exactly two opposite nonadjacent pairs, and
mu=2 makes their common-neighbor pairs uniquely the other two vertices.
There are `99*(99-1-14)/2=4158` unordered nonadjacent pairs, giving exactly
`C4(G)=4158/2=2079` induced four-set cycles. This is a double count, not a
canonical search or an automorphism assumption.

The prior path count is `P=3*231*(7-1)^2=24948`. These statements give the
candidate lower count 22869. A zero triangle-incidence kernel is allowed.

## Character consequence and proposed controls

Let C=ker(B^T), M=|C|, and A_w count its weight-w words. For the candidate
target count, the same binary character identity gives

`sum_(w>0) A_w*(22869-K5(w)) <= binom(99,5)-22869 = 71500275`,

where `K5(w)=sum_s (-1)^s binom(w,s) binom(99-w,5-s)`. This is conditional
on a target graph and on independent establishment of the new count. No new
LP row, certificate, code dimension or rank conclusion is approved by this note.

Before a changed guide, proposed controls are complete actual triangle/path/
support fibers plus all induced four-set cycles on the earlier seven small
adjacency fixtures. In rook9, P=18, C4=9 and N5=9 should saturate the new count.
In the loose path, P=1 and C4=0 should saturate it. Every double support must
have its exact injected C4, and no two double supports may share it. Preserve
fixtures with C4s that have no double support. Missing lambda-one premises,
changed central completions, wrong C4 counts, wrong fibers and a many-to-one
collision mapping must be rejected at precise stages. The earlier K7 raw
threefold support remains a scope counterexample.
