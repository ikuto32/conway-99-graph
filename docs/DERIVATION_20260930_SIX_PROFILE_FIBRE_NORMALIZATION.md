# Global fibre relabelling for the fixed six-exception profile universe

Candidate derivation, pending independent review. This is a statement about labelling a fixed-support construction family. No automorphism of a hypothetical graph is assumed.

Let the three fibres be indexed by `f=0,1,2`, each with coordinate `a=0,...,11`. In the fixed six-prism core all three internal matchings are the same and every cross-fibre matching is the identity. Thus every permutation `p` of the three fibres sends row `(f,a)` to `(p(f),a)` and preserves the literal cubic core `C` and prescribed incidence Gram `G`. Permuting the corresponding three root-triangle vertices preserves the entire 39-vertex core.

Write `P` for the resulting 36-row permutation matrix, with `P[new,old]=1`. If `F` is a 36-by-60 incidence factor, permuting its rows produces `PF`. The coordinate support `L[a,d]=sum_f F[(f,a),d]` is unchanged. Each support group has three identical `L` columns, so these three columns can then be reordered independently. If `Q[old,new]=1` denotes these within-group column permutations, the result is `F'=PFQ`. It has the same raw `L`, row margins and Gram, since `F'F'^T=PGP^T=G`. All column intersections are merely permuted; the closed-core-neighborhood quantities `(I+C)F` are likewise permuted.

For a completed residual graph put `D'=Q^T D Q`. Both residual completion equations transform equivariantly:

`F'D' = P(FD)Q = 2J - F' - C F'`,

`D'^2 + F'^T F' = Q^T(D^2+F^T F)Q = 12I - D' + 2J`.

The full adjacency matrix is conjugated by the permutation acting on the root triangle, the three fibres, and the residual vertices. Consequently the operation preserves any actual target completion and is reversible. This does not assert that the original labelled adjacency is invariant, that a completion exists, or that residual `D` has been found.

For a profile let `delta[a,f,g]` be the count of fibre `f` at coordinate `a` in support group `g`, minus one. Its image has `delta'[a,p(f),g]=delta[a,f,g]`. Exceptional group IDs and their supports are unchanged. Each local triple consists of three distinct words from the 90-word catalogue, sorted by word rank. Apply `p` to every word entry, then sort the three transformed ranks. The saved local column-order map records `Q` explicitly for each triple. This maps a full initial domain bijectively to the full domain of the transformed count signature. Column sorting is a label choice among identical support columns; it is not an extra factor constraint.

For any two group choices, summing their Gram contributions commutes with `P`, while their nine cross-column intersections are permuted by the two local column permutations. Hence both saved pair relations are transported exactly. The maximal arc-consistency fixed point is consequently transported as well. The finite producer census checks every domain, every pair-relation image and every saved fixed-point image rather than assuming those facts from reported aggregate counts.

The frozen population comprises all 984 literal profiles in the independently checked local-domain universe. The code computes all six images and the orbit partition from raw deviations. A representative is the lexicographically smallest profile ID in its orbit. The earlier unreviewed diagnostic of 164 orbits is not an input or pruning premise. The mathematical relabelling argument is separate from the saved AC classifications, which remain subject to their own independent correctness review.
