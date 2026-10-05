# Independent necessity audit for unrestricted rooted-eight rows

Verifier: `/root/checkpoint_audit`. Producer: `/root/structural`.
This written argument defines the checking scope; it is not approval of a raw
operator until the exact catalogue and every coefficient/RHS pass the separate
artifact reconstructions. No optimizer, target graph or exclusion is asserted.

Fix an actual ordered nonedge `(u,v)` of a hypothetical SRG(99,14,1,2).
For each order h, `x[h,F]` counts unordered `(h-2)`-subsets of the remaining97
vertices inducing the rooted flag F. Root0 and root1 are fixed separately.
Changing the free labels represents the same flag; it neither divides the
subset count by an automorphism order nor assumes any automorphism of the
99-vertex graph. Every induced flag satisfies the local common-neighbor caps.
The independently complete rooted7 catalogue and all128 possible neighborhoods
of an eighth vertex therefore cover every rooted8 flag. A qualifying prism is
retained. Canonical minima/disjointness and all354560 augmentations must be
checked against the exact output, not inferred from the producer or controls.

For a rooted7 flag H and an orbit O of marked vertices under the finite
automorphism group of H fixing both roots, count pairs `(S,w)` with S inducing
H, w outside S, and w adjacent to a marked vertex. Summing over S gives
`sum_{a in O}(14-deg_H(a))*x[7,H]`. Regrouping by the induced rooted8 subset K
gives its coefficient: for every free vertex deleted from K, transport O to
the remaining copy of H and count adjacencies from the deleted vertex to O.
For marked pairs use the same double count with factor
`sum_{a,b in O}(mu_or_lambda(a,b)-CN_H(a,b))`, and count a deleted vertex
adjacent to both marked endpoints. Unmarked deletion instead has factor92.
Total rooted8 count is `binomial(97,6)`. All are exact integer equations.

Two isomorphisms to the canonical H differ by an automorphism of H fixing
the roots. Its action preserves the entire orbit O, so the summed coefficient
is unchanged. The checker additionally enumerates every such isomorphism for
every deleted free vertex and tests literal equality. This finite invariance
belongs to the coordinate system; it is no symmetry premise about the target.

For rooted5 flags F,G, multiply the counts of unordered free triples. This
counts ordered pairs of triples. If F differs from G, grouping in the upper
pair `{F,G}` counts both orientations, so the RHS is `2*c_F*c_G`; on the
diagonal it is `c_F^2`. Classify each pair by its union, of rooted order5..8.
The independent reconstruction chooses the intersection of size8-h and the
private first subset of sizeh-5; the private second subset is its complement.
This is a bijection with all ordered triple pairs having that exact union,
with populations1,12,30,20 at orders5,6,7,8. It includes every overlap.

At order5 only the equal-triple diagonal collision occurs, with contribution
`c_F`. At order6 substitute the separately verified unrestricted rooted6
affine vector `x6=origin+c*basisC+a*basisA+b*basisB` on its456 order-six
coordinates (the full necessary system has567 coordinates across orders2..6).
Subtract each contribution from the constant,c,a,b RHS. In particular the
prism-count basis contribution must remain; the finite audit independently
finds a genuine nonzero coefficient6 for the pair `(0,0)`. The order7 and8
union coefficients remain variables. The universal rooted5 counts and the
entire unrestricted rooted7 prefix are reused by exact artifact/dependency
pins; they are not newly derived by this audit.

Thus the fully checked extension/product equations are necessary at every
actual ordered nonedge. The primary `(c,a,b)` may vary by the actual pair, as
may every inherited secondary edge/nonedge aggregate. No prism absence,
common secondary profile or fixed old rational witness is used. Nonnegative
integer count solutions do not imply graph realization. Finite rook/Petersen
controls and numerical guide results cannot establish target existence or
nonexistence. The final exact scope requires full raw equality of the newly
saved catalogue/operator, separate from these written identities.
