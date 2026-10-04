# Independent written audit: one-minority ternary circuits have weight at least 28

Verifier: `/root/checkpoint_audit`. Producer: `/root`. This is a complete
written reconstruction and attempted falsification of the literal candidate
`C-UNRESTRICTED-TARGET-TERNARY-ONE-MINORITY-CIRCUIT-LOWER28`, revision 1.
No matrix program, enumeration, solver, symbolic computation, formal proof or
external review was executed. The candidate and raw candidate remain unchanged.
Root supplied the discovery and its proposed argument; this audit independently
checks the deductions rather than treating that proposal as approval.

The precise inputs are:

- `docs/CANDIDATE_20261004_ONE_MINORITY_TERNARY_CIRCUIT_LOWER28_V1.md`, SHA256
  `e2b8bf6b2908c22cd16fc28705ba5e203758b4180628f14d8b0524f0fd200f79`.
- `acceleration/results/20261004_one_minority_ternary_circuit_lower28_candidate01.json`,
  SHA256 `1e269c18a0fe77f8ad3343dc7783ca2028984965449262d01d5692886cff1c90`.

The conclusion below is the exact conditional theorem in those inputs. In
particular, no assertion that an arbitrary target must possess such a circuit
is used. The older lower bound 25 remains true and is only strengthened here.

## Local incidence and the circuit rank constraint

Let the hypothetical target have adjacency A, degree 14, adjacent common
neighbor count 1 and nonadjacent count 2. For a vertex v, each vertex in N(v)
has exactly one neighbor inside N(v): it is the unique common neighbor of that
vertex and v. Thus the 14 neighbors are partitioned into seven edges, and v
lies in exactly seven actual triangles. Two distinct actual triangles cannot
share an edge, because its endpoints would then have two common neighbors.
Consequently the selected degree of a point with d selected incidences is 2d.

Write B for the three points of the unique minority triangle and M for the
other used points. At b in B, the GF(3) row equation is d_plus-1=0. Since
d_plus+1 is at most seven, a used minority point has total incidence 2 or 5.
At a point outside B the row equation is d_plus=0, and its positive selected
incidence is 3 or 6. This uses the actual triangle cap, not a presumed bound
on the selected support or an integer equality in place of a GF(3) equation.

Let h count incidence-5 minority points, and t count incidence-6 points of M.
The baseline sum of incidences is 3n-3, with each exceptional point adding 3.
Hence 3w=3n-3+3h+3t and n=w+1-h-t. A circuit on w nonzero columns has
GF(3) rank w-1. Its columns lie in the codimension-one zero-coordinate-sum
subspace of GF(3)^n, because each triangle column sums to 3=0. Therefore
w-1<=n-1, or w<=n. It follows that h+t<=1, giving exactly these patterns:

- n=w+1: all three minority incidences 2 and all other incidences 3;
- n=w: one minority incidence 5, the other two 2, all others 3;
- n=w: all minority incidences 2, one other incidence 6, all others 3.

Restriction to the n used rows does not alter column rank, because all other
rows are zero. There is no symmetry, connectivity or uniqueness-of-target
premise hidden in this rank comparison.

Each minority point needs a majority triangle. These three majority triangles
are distinct: a majority triangle containing two points of B would share their
edge with the minority triangle. Thus w>=4. In the n=w+1 pattern, each b has
exactly one majority triangle and exactly two selected neighbors in M. These
six neighbors are pairwise distinct. A point of M adjacent to two points of B
would be a second common neighbor of their edge, in addition to the third
point of B. This argument concerns actual adjacency; it applies whether those
adjacencies are selected or extra. Since |M|=w-2, this pattern has w>=8.

## Gram norm reconstructed from the target identity

Set G=27I-9A+J. The target has A^2=12I-A+2J, AJ=JA=14J and J^2=99J.
Expanding gives G^2=1701I-567A+63J=63G. Symmetry therefore gives
x^T G x=||Gx||^2/63>=0. For an actual vertex set X of size m,

    F_X=m^2+27m-18e(X),
    (G chi_X)_v=m+27-9deg_X(v)  for v in X,
    sum_{v in X}(m+27-9deg_X(v))^2 <= 63F_X.

The last inequality merely drops the nonnegative squares at vertices outside
X. All induced extra edges must be included in e(X) and the inside degrees.
For disjoint M and B, PSD also gives the exact two-indicator Cauchy inequality
F_M F_B >= (chi_M^T G chi_B)^2. No floating approximation or rank inference
from a small principal matrix is involved.

## Excluding every weight below 28

First consider either n=w pattern. There are exactly 3w selected edges,
since the w distinct triangles share no edge. With E extra induced edges,
F_S=w(w-27)-18E. For 4<=w<=26 this is negative. At w=27 it is at most zero;
PSD requires E=0 and F_S=0. At least two minority points have incidence 2,
hence induced degree 4 when E=0. Their inside coordinate is 54-36=18.
This contradicts ||G chi_S||^2=63F_S=0. Allowing E>0 cannot help, since
it makes the scalar negative before a degree argument is needed.

For the n=w+1 pattern, the selected edge counts within B, between B and M,
and within M are respectively 3, 6 and 3w-9. Let a be the number of extra
induced edges within M. With m=w-2, expansion gives

    F_M=(w-2)^2+27(w-2)-18(3w-9+a)
       =w^2-31w+112-18a.

For w=8 and w=26, the polynomial before subtracting 18a is respectively
-72 and -18. Convexity places every intermediate value below the chord
joining those endpoints, which is strictly negative. Thus every integer 8<=w<=26
is excluded. This and the earlier geometric w>=8 covers the entire pattern.

At w=27, |M|=25 and F_M=4-18a. Since a is a nonnegative integer, PSD forces
a=0. Each point of M has selected degree 6 in S. The six distinct selected
neighbors of B lose one edge on restriction to M and so have degree 5 there;
the other 19 have degree 6. There are no extra M edges, so these are the
actual M degrees. Their retained norm is

    6(52-45)^2+19(52-54)^2 = 294+76 = 370,

whereas 63F_M=252. Extra B-M edges do not alter either these induced-M
degrees or F_M. They only change some discarded coordinates outside M.
This specifically falsifies the possible objection that adding B-M edges
could cure the weight-27 contradiction.

Together, the rank-classified cases exclude every possible w<=27.

## Excluding both n=w patterns at weight 28

Now n=w=28 gives F_S=28-18E, so E is 0 or 1. At E=0 the selected incidence
patterns give the following inside degrees and norm values, calculated anew:

    one incidence-5 minority:
      one degree 10, two degree 4, 25 degree 6;
      (-35)^2+2(19)^2+25(1)^2 = 1225+722+25 = 1972;

    one incidence-6 majority:
      one degree 12, three degree 4, 24 degree 6;
      (-53)^2+3(19)^2+24(1)^2 = 2809+1083+24 = 3916.

Both exceed 63*28=1764. For E=1, adding the sole extra edge changes a
degree-r endpoint's squared contribution by

    (55-9(r+1))^2-(55-9r)^2 = 162r-909.

For the only original degree classes this is -261 at r=4, +63 at r=6,
+711 at r=10 and +1035 at r=12. Every degree-4 point here lies in B.
Two such points already have their minority-triangle edge, so an extra
edge cannot have two degree-4 endpoints. Thus its total change is at least
-261+63=-198. This lower bound deliberately permits possible endpoint pairs
even if additional target constraints would forbid them, which only makes
the exclusion weaker and therefore sound. No valid extra-edge endpoint is
discarded. The new norms are at least 1774 and 3718, respectively, whereas
63F_S=63*10=630. Hence neither n=w pattern survives at w=28.

The remaining pattern has n=29, all three minority incidences 2 and all
other 26 incidences 3. This is a necessary incidence description only;
the argument constructs no circuit or target with those data.

## The additional majority-edge and cross-edge boundary

For the surviving pattern at w=28, M has 26 points and selected edge count
75. Thus F_M=26^2+27*26-18(75+a)=28-18a, forcing a<=1. The minority set
is an actual triangle, so F_B=9+81-54=36 and it has no extra inside edge.
Let b count additional B-M edges beyond the selected six. The disjoint
indicator cross product is 26*3-9(6+b)=24-9b. If a=1, then F_M=10 and PSD
requires (24-9b)^2<=360. For b=0 the square is 576; for b=1,2,3,4 it is
225,36,9,144; for b=5 it is 441, and for every b>=5 it increases further.
Therefore precisely the nonnegative integer edge counts allowed by this
necessary inequality are b=1,2,3,4.

This is an inclusive endpoint condition. It neither proves these counts
are realizable nor says the actual induced graph has no other structure.
When a=0, the proof retains the corresponding inequality without adding
an unrequested stronger theorem or a completion assertion.

## Falsification outcome and boundaries

No material gap was found in the exact stated proof. The vulnerable steps
were explicitly checked: triangle incidence cap 7; unique-edge geometry;
GF(3) rather than integer row balance; circuit rank rather than arbitrary
dependence rank; every h+t pattern; disjointness of all six neighbors;
actual induced extras in both Gram scalars; independence of the M norm
from B-M extras; prohibition of a two-degree-4 extra edge; the worst-case
endpoint decrease; and the inclusive integer b boundary.

The sole dependency is `C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS`, revision 1.
The target polynomial/degree identities are explicit conditional premises.
This audit supplies no target existence or nonexistence result, no statement
that a one-minority circuit must exist, no circuit upper bound, no selected
incidence pattern uniqueness at larger weight, and no unrestricted circuit
classification. It preserves the prior lower25 claim and every input byte.

Outcome: PASS for the exact candidate statement and scope by independent
written derivation. Mathematical program executions: 0. Formal proofs: 0.
External reviews: 0. Ledger/index/Git mutations: 0.
