# Candidate: one minority triangle requires at least28 circuit triangles

Root discovery; CANDIDATE, independent derivation pending. No computation or
formal/external review. This strengthens a lower bound and excludes no complete
unrestricted target on its own. It does not force a one-minority circuit.

For every hypothetical srg(99,14,1,2), let C be the point-by-triangle incidence
matrix of a GF(3) circuit of distinct actual triangles. Suppose its unique
nonzero dependence, scaled globally, has exactly one coefficient−1 and w−1
coefficients+1. Let B be the three vertices of the minority triangle and S the
n used vertices. Then w≥28. If w=28, n=29; in the selected edge union the three
vertices in B lie on two selected triangles each and the other26 vertices on
three each. For M=S\B, at most one induced edge is outside the selected union.
If there is exactly one such edge within M, there are between one and four
additional induced edges between B and M.

Stable proposed claim: C-UNRESTRICTED-TARGET-TERNARY-ONE-MINORITY-CIRCUIT-LOWER28 r1.
Basis DERIVED; proposed dependency C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS r1.
The previous minority-count lower bound25 remains true; it is weaker, not refuted.

## Geometry and the two possible support sizes

Degree14 and λ=1 partition the neighbors of each target vertex into seven
disjoint edges, hence that vertex belongs to exactly seven actual triangles.
Distinct triangles share at most one vertex and no edge. For a used vertex,
let d be its number of selected incidences. At a minority vertex, the GF(3)
dependence gives d+=1 mod3; total d=d++1≤7, so d is2 or5. At other used
vertices, d is3 or6. Write h for the number of minority vertices having d=5
and t for the number of other vertices having d=6. Summing incidences gives

    3w=3n−3+3h+3t, hence n=w+1−h−t.

Circuit rank is w−1. Every column has sum3=0 in GF(3), so rank C≤n−1,
and w≤n. Consequently h+t≤1. Either:

* A: n=w+1, all three minority incidences2, every other incidence3;
* B: n=w, one minority incidence5, two minority incidences2, all others3;
* C: n=w, all three minority incidences2, one other incidence6, all others3.

Every minority vertex needs a majority triangle. Those three triangles are
distinct, since sharing two minority vertices would reuse an edge; thus w≥4.
No target automorphism is assumed.

## Exact Gram inequalities

Use G=27I−9A+J. The target identity gives G²=63G. Symmetry makes G positive
semidefinite. For any actual vertex set X of size m, with e(X) induced edges,

    F_X=χ_XᵀGχ_X=m²+27m−18e(X)≥0,
    Σ(v∈X)(m+27−9deg_X(v))²≤63F_X.

The latter keeps only inside coordinates of the exact identity
||Gχ_X||²=63F_X. Extra induced edges always remain in e(X) and the degrees.

## Excluding w≤27

In cases B/C, n=w and e(S)≥3w, so F_S≤w²−27w. This is negative for
4≤w≤26. At w=27, positivity forces no extra induced edge and F_S=0.
There is a minority vertex of selected degree4 (in fact at least two).
Its coordinate in Gχ_S is54−36=18, contradicting ||Gχ_S||²=0.

In case A, each minority vertex has precisely two majority neighbors in the
selected union. All six are distinct: a major vertex adjacent to two minority
vertices would be an extra common neighbor of an edge of the minority triangle,
whose required unique common neighbor is already the third minority vertex.
Thus M has m=w−2≥6 and w≥8. The selected union has3w edges: three within B
and six between B and M, leaving3w−9 within M. If a is the number of extra
induced edges within M,

    F_M=w²−31w+112−18a.

The polynomial is convex. At w=8 it is−72 and at w=26 it is−18, hence it
is negative throughout8≤w≤26 even before subtracting18a. At w=27,
m=25 and F_M=4−18a, so a=0. The six major neighbors of B have degree5
within M, and the other19 vertices degree6. Therefore the inside square sum is

    6·(52−45)²+19·(52−54)²=370 > 63·4=252.

This excludes w=27 without discarding extra edges between B and M. Together
the three cases establish w≥28.

## At w=28, cases B/C are still impossible

For n=w=28, write E for all extra induced edges in S. Then
F_S=28−18E≥0, hence E is0 or1. With E=0, the inside square sums are:

* B: one degree10, two degree4,25 degree6:
  (55−90)²+2(55−36)²+25(55−54)²=1972;
* C: one degree12, three degree4,24 degree6:
  (55−108)²+3(55−36)²+24(55−54)²=3916.

Both exceed63·28=1764. Adding one edge changes the contribution at an endpoint
of former degree r by162r−909: this is−261 at r=4,63 at r=6,711 at r=10,
and1035 at r=12. An extra edge cannot join two degree4 vertices, since all
degree4 vertices here are minority vertices already joined by their triangle.
The total decrease is therefore at most198. The resulting sums are at least
1774 or3718, still above63·(28−18)=630. This covers every single extra edge,
without claiming which edges would pass the other target constraints.

Thus only case A is possible at w=28, with n=29 and the stated selected
incidences. For M of size26, e(M)=75+a and F_M=28−18a, hence a≤1.

## Exact additional boundary when a=1

Let b be the number of extra induced edges between B and M. The minority
triangle is complete, so there are no extra edges within B. Its Gram norm is
χ_BᵀGχ_B=3²+27·3−18·3=36. The cross product is

    χ_MᵀGχ_B=26·3−9(6+b)=24−9b.

The2×2 Gram of these two indicator vectors must be positive semidefinite:

    36F_M−(24−9b)²≥0.

When a=1, F_M=10. For nonnegative integer b, |24−9b|²≤360 holds exactly
for b=1,2,3,4. These are necessary edge-count conditions, not realizations.
At a=0 the theorem does not impose a sharper boundary than the recorded
inequality; no absent-edge or completion assertion follows.

## Scope and verification request

Independently rederive the circuit support identity, the rank bound w≤n,
all selected-degree patterns, the six distinct majority neighbors, each exact
Gram calculation, and the treatment of every possible extra-edge endpoint.
Attempt to falsify the use of a minority triangle's preexisting common neighbor
and the case-A w=27 bound when extra B–M edges are present. No finite simulation,
numerical approximation, rank computation, claimed graph or solver result is
evidence here. This is a universal conditional theorem about one circuit;
there is no theorem that every target must contain a circuit of this sign form.
