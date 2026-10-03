# Independent edge kernel and rectangle proof

The frozen complete necessary ordered-edge rooted6 operator M has1099rows and
394columns. Its exact raw geometry/necessity was independently reconstructed in
the pinned prior audit. Here independently compute392nonzero echelon pivots
modulo the prime1009 using sparse incremental row elimination. Every elimination
is an invertible row operation over the field; a nonzero392minor establishes
rational rank at least392. The two raw integral kernel vectors K0,K1 satisfy
every homogeneous equation exactly and have identity entries at free columns
382,393. They are independent over Q, so rational rank is at most392. Thus rank
equals392 and nullity equals2, without using the old conditional full-rank result.

Derive o from the saved exact primal p by o=p-p382K0-p393K1 and check Mo=r and
o382=o393=0. Every rational solution is uniquely o+sK0+tK1; s,t are actual
coordinates. The primitive coordinate forms include s,t,12-s,6-t. Hence
nonnegative vectors require0<=s<=12,0<=t<=6. Every394coordinate form is checked
nonnegative at(0,0),(0,6),(12,0),(12,6). Each point of the rectangle is a convex
combination of those corners using weights from X=s/12,Y=t/6, so all coordinates
are nonnegative on it. The literal coordinate witnesses prove reverse inclusion.

The origin and basis are integral, so every integer pair in that rectangle
gives a nonnegative integer solution. Conversely any integer solution has
integer s,t because these are two of its entries. Thus exactly13*7=91full
integer vectors comprise the entire domain. The checker enumerates all91,
checks all394coordinates and all1099raw equations at each, and rejects points
beyond all four facets using negative-coordinate witnesses.

Columns382,393 correspond respectively to canonical rooted masks8025,15541.
Each raw graph has two disjoint triangles with a perfect matching between them.
The ordered adjacent roots occupy one triangle edge in8025 and one matching edge
in15541. Canonicalization permutes only the four free labels; it asserts no
nontrivial automorphism of a hypothetical target.

These are necessary local flag-count solutions. No graph realization, target
exclusion, existence/nonexistence, prism-free premise, novelty or target-wide
coverage follows from rank/domain completeness.
