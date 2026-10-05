# Fibre relabelling of the seven-exception fixed-support family

Candidate derivation, awaiting independent review. This reuses the general
algebra of the previous six-exception normalization and supplies a fresh
finite seven-exception population census. It is not a novelty claim and does
not assume an automorphism of any hypothetical graph.

The fixed six-prism core has rows `(f,a)`, with three fibres and twelve
coordinates. All three internal matchings are identical, and each cross-fibre
matching is the identity. Every permutation `p` of the three fibre labels,
together with the same permutation of the three root-triangle vertices,
preserves the complete 39-vertex core. Its 36-row permutation matrix `P` uses
`P[new,old]=1`. Directly, `PCP^T=C` and `PGP^T=G` for the prescribed core and
factor Gram matrices.

For any binary factor `F`, row relabelling gives `PF`, preserving the fixed
coordinate-support matrix `L[a,d]=sum_f F[(f,a),d]`. Three equal-support columns
may then be reordered independently in each of twenty groups. If `Q[old,new]`
is that column permutation, `F'=PFQ` has exactly the same `L` and Gram, since
`F'F'^T=PGP^T=G`. Every column intersection is merely permuted; the mixed
quantities `(I+C)F` are also permuted. Thus all relevant margins, partial-Gram
bounds, within-group caps and cross-group caps are preserved.

For an actual residual completion let `D'=Q^T D Q`. The equations transform as

`F'D' = P(FD)Q = 2J - F' - C F'`,

`D'^2 + F'^T F' = Q^T(D^2 + F^T F)Q = 12I - D' + 2J`.

The whole adjacency matrix is relabelled by a permutation of its vertices.
Reversibility supplies equivalence of possible completions, not invariance of
one labelled target and not an assertion that any completion exists.

For a literal profile, transform each deviation by
`delta'[a,p(f),g]=delta[a,f,g]`. The seven exceptional group IDs and coordinate
supports are unchanged; a nonzero group deviation cannot become zero. Local
triples consist of three distinct words from the complete 90-word population.
Apply `p` to all word entries and sort the three resulting ranks. The saved
column-order maps specify `Q` for every local triple. Each full initial domain
maps bijectively onto the domain of the transformed count signature; sorting
only relabels equal-support columns.

For two group choices, their summed Gram transforms by `P`, and their nine
cross-column intersections are permuted by the two local column permutations.
Both pair predicates therefore transport exactly. The entire maximal
arc-consistency fixed point transports as well: every support has its image
and inverse image. This covers all 42 directed arcs of each seven-variable
profile, including empty fixed points. The producer checks every stored
relation bitmap and final domain image; those checks are separate from the
independent replay that established the saved AC classifications themselves.

The fresh finite population is all 1,608 hash-bound profiles, not the older
local producer's diagnostic orbit count. The full six-action orbit of each
profile is computed from raw deviations. Since each action is a reversible
relabeling, the union over these literal profiles has a factor or target
completion precisely when the union over one representative per orbit does.
Representatives are selected by lexicographically smallest raw profile ID.
This is an equivalence only within the specified fixed-support profile family;
it establishes no general Conway-99 coverage or existence.
