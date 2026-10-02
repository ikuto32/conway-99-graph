# Independent written audit of the conditional incidence-rank lower bound

Verifier: `/root`; discovery author: `/root/structural`. Exact discovery note:
`docs/CANDIDATE_20261003_TRIANGLE_INCIDENCE_GRIESMER_V1.md`, SHA256
`06c72ef3ed8d1f3167336420016e2d0ec86f481ebe97d5910ff154c6a44d9c16`.
This verifies its precise conditional mathematical statement. There is no
target graph, general nonexistence proof, rank upper bound, or novelty claim.

Assume a binary symmetric zero-diagonal99matrix satisfies the integer identity
`A²=12I−A+2J`. Diagonal entries give degree14. Off-diagonal entries give one
common neighbor per edge and two per nonedge. Hence each edge lies in exactly
one triangle. A vertex's14 incident edges are partitioned into seven pairs
by its triangles. There are693 edges and231 triangles. These facts do not
require any graph automorphism or an incidence-rank premise.

Take the ordinary integer characteristic vector `z` of a nonempty support S
of a binary word in `ker(Bᵀ)`. Each triangle contains zero or two vertices of S.
For every vertex in S, exactly seven neighbors are in S; all other seven
neighbors are outside. Thus `7|S|` is twice the number of edges inside S, and
`s=|S|` is even. The all-one word is not in the kernel because every triangle
has odd size, so `0<s<99`. If the kernel is zero, the dimension conclusion is
immediate and the following word analysis is unnecessary.

For the outside vertices write `r_v=(Az)_v`. The cut size is `7s`, so their
sum is `7s`. Multiplying the exact target identity by z on both sides gives
`||Az||²=12s−7s+2s²=5s+2s²`. Its inside coordinates are all7 and contribute
`49s`. The outside squared sum is therefore `2s(s−22)`. The elementary
identity `m sum r_v²−(sum r_v)²=sum_{v<w}(r_v−r_w)²>=0`, for `m=99−s`,
proves Cauchy here without floating point. Substituting the moments and
dividing by the positive integer s gives
`49s<=2(99−s)(s−22)`, equivalent to `(s−36)(2s−121)<=0`.
The real interval is `[36,121/2]`; since s is an even integer, the exact
nonzero weight set is contained in `{36,38,...,60}`.

For completeness I independently checked the general binary code argument.
For a code of dimension t>0 choose a word w of actual minimum nonzero weight d.
Project onto the n−d coordinates where w is zero. Any other nonzero word in
the projection kernel would be supported in those d removed positions, have
weight at least d, and consequently be w itself. The projection kernel thus
has dimension1 and the image has dimension t−1. If a nonzero image has weight b
and a preimage has a ones on supp(w), then its other preimage obtained by adding
w has d−a ones there. Both preimages have weight at least d, so
`b>=d−min(a,d−a)>=ceil(d/2)`. Apply induction to the image, whose actual minimum
distance may be larger than this bound. Monotonicity of integer ceilings and
`ceil(ceil(d/2)/2^i)=ceil(d/2^(i+1))` give
`n>=sum_{i=0}^{t−1}ceil(d/2^i)`. Dimension1 is immediate.
Choosing a nonminimum word would invalidate the one-dimensional kernel step;
the finite controls explicitly reject that tempting replacement.

For the incidence kernel d>=36. If t>=33 the first33 terms already sum to
`36+18+9+5+3+2+27=100`, exceeding99. Thus t<=32. Rank-nullity over GF(2)
then gives `rank(B)>=99−32=67`. This proves the stated conditional lower bound
and nothing about an upper bound. In particular the rejected generic
codomain-isotropy argument cannot supply rank<=72 or a minimum kernel dimension.

The separate executable uses literal integer rook9 matrix products and all16
of its triangle-kernel words, and enumerates all binary subspaces of lengths
0..6 using canonical RREF generators. These finite controls challenge the
critical steps; this written argument establishes the universal quantifiers.
No producer implementation is imported, no hypothetical target is checked,
and a finite code enumeration is not presented as proof of the general bound.

The primary Griesmer paper scan was separately inspected on2026-10-03 JST:
J. H. Griesmer, *A Bound for Error-Correcting Codes*, IBM JRD4(5),1960,
pp532–542, DOI10.1147/rd.45.0532, Section2 recurrence/Theorems1–2,
https://bitsavers.trailing-edge.com/pdf/ibm/IBM_Journal_of_Research_and_Development/045/ibmrd0405M.pdf.
OCR is imperfect; the complete proof above does not depend on it. Archived
weight-interval overlap and lack of a novelty audit remain as disclosed in the
discovery note. This is internal independent derivation, not external review
or proof-assistant verification.
