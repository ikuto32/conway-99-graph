# Independent written audit of outside-type pair and triple caps

Verifier: `/root/native_driver`. Discovery/proof producer: `/root/checkpoint_audit`;
ROOT proposed the tightening direction. I read the entire candidate
`docs/CANDIDATE_20261003_EXTERNAL_TYPE_PAIR_AND_TRIPLE_CAPS_V1.md`, SHA256
`f7aefb0628c9da0741f0c8f43b444a30e5d5042eb60c1db23735f024286125a4`,
then reconstructed the argument below independently. No mathematical program,
optimizer, producer/checker import, graph enumeration or formal-proof tool was
used. This is a written mathematical review, not a new model or certificate gate.

## Exact reviewed population and conclusion

The candidate assumes a finite simple undirected graph of order 99, regular
degree 14, with exactly one common neighbor for each distinct adjacent pair
and exactly two for each distinct nonadjacent pair. For any subset S, let
X = V(G) minus S, T(x) = N_G(x) intersect S for x in X, and let n_T count
outside vertices of exact type T. The following conclusions survive review:

* For distinct x,y in X, the intersection of their types has size at most two,
  and at most one if xy is an edge. Size exactly two forces a nonedge and no
  common neighbor in X.
* An exact type T of size at least three occurs at most once. For distinct
  types T,U with intersection size at least three, n_T + n_U is at most one.
  If T=U, the conclusion is n_T at most one, not a double-counted sum.
* For every three-element Q subset S, the sum of n_T over types containing Q
  is at most one. When S has 17 vertices this gives exactly 680 labelled
  necessary inequalities.

The proof below actually only needs the distinct-pair common-neighbor upper
bounds. The claim-bound report retains the candidate's stated 99/14 population;
it does not silently change its scope to that stronger generalization.

## Independent reconstruction

Fix distinct exterior vertices x and y. A vertex u in S belongs to both T(x)
and T(y) precisely when it is adjacent to both x and y. Thus the identity

    T(x) intersect T(y) = (N_G(x) intersect N_G(y)) intersect S

is a bijective identification of the support portion of this particular
pair's common-neighbor set. Simplicity and distinctness ensure this is the
ordinary distinct-pair common-neighbor count, not a diagonal degree count.
The complete set has size one for an edge and two for a nonedge. Taking its
support portion proves the respective upper bounds. If that portion has
size two, an edge is impossible. In the nonedge case it already exhausts
the complete two-element common-neighbor set, so its complement in X is empty.

The exact types partition X: each outside vertex belongs to exactly one
type class. If two different outside vertices had types sharing any three
specified vertices, those three vertices would lie in their common-neighbor
set, contradicting the established upper bound of two. In particular, two
vertices in one type class of size at least three are impossible. For distinct
T,U with intersection at least three, each class separately has size at most
one and both cannot be occupied; hence their total multiplicity is at most
one. This accounts separately for equal and unequal type indices.

Now fix a literal three-set Q. The sum over exact type classes containing Q
counts, once each, exactly the exterior vertices adjacent to every member of
Q. If that count exceeded one, choose two distinct counted exterior vertices.
They would share the three members of Q, giving the same contradiction. This
proves each inequality directly without deriving it from fractional variables,
pairwise incompatibility graphs or an optimization result.

Finally the number of unordered three-subsets of a 17-set is
17*16*15/(3*2*1) = 680. This is a counting identity, not an executed census
of 680 rows or an assertion that all of those rows are independent.

## Literal boundary checks and attempted falsifications

1. In the 3-by-3 rook graph, vertices are ordered pairs (i,j) with i,j in
   {0,1,2}, and adjacency means sharing exactly one coordinate. Adjacent pairs
   have one common neighbor (the remaining point of their row or column);
   nonadjacent pairs have the two opposite corners. This is a small valid
   example for the proof's weaker upper-bound assumptions, not a Conway-99
   construction or a computational fixture.
2. Take S={(0,0),(1,1)}, x=(0,1), y=(1,0). Both exterior types equal S;
   their overlap is two, x and y are nonadjacent, and their full common set is
   exactly S. Thus size-two types can have multiplicity two and a two-set Q
   cannot replace the required three-set.
3. Take S={(0,2)}, x=(0,0), y=(0,1). The adjacent exterior pair has type
   overlap one, saturating the edge cap. In fact n_S=4, from (0,0),(0,1),
   (1,2),(2,2), so a singleton type is not capped at one by this lemma.
4. Take S={(0,1),(0,2),(1,0)}. Only (0,0) among exterior rook vertices is
   adjacent to all three. The triple sum is one, so its inequality can be tight.
   The other exterior vertices are (1,1),(1,2),(2,0),(2,1),(2,2); each misses
   at least one of the three points. These written lists do not assert target
   order or degree.
5. With S empty the triple population is empty; with X empty all multiplicities
   and sums are zero. Nothing in the proof requires S to be a proper nonempty
   induced configuration. The graph on S need not be reconstructed at all.
6. Taking x=y would instead give the size of T(x), which can exceed two.
   The explicit distinctness premise is essential. Likewise the type-class
   equality case must not count n_T twice.
7. A K2,3 with its size-three part chosen as S has two exterior vertices
   sharing three support neighbors and deliberately violates the nonedge CN2
   hypothesis. Adding their edge deliberately violates the edge CN1 bound.
   These are failures of the assumptions, not counterexamples to the lemma.
8. Nonnegative fractional assignments need not represent actual vertices.
   On a five-set {a,b,c,d,e}, assign one half to each of
   {a,b,c,d}, {a,b,c,e}, {a,b,d,e} and zero to every other type. Every triple
   sum is at most one because no triple lies in all three types, while any
   two of the three types intersect in three points. Their total 3/2 violates
   the actual at-most-one bound for this entire incompatibility clique. This
   demonstrates that the 680 triple inequalities need not encode all clique
   constraints or the convex hull of realizable vectors. It makes no claim
   about satisfying the fixed17 moment equations.

## Fractional scope, provenance and result

Every triple inequality is linear, with zero/one coefficients and right-hand
side one. It holds for each actual integer type vector, so it holds for any
convex combination of such vectors with the same labelled coordinate universe.
It can therefore be added soundly to a necessary nonnegative rational
relaxation. It does not force every fractional vector to be realizable or
integral, and it does not encode exterior adjacency. The edge-specific pair
bound is conditional on an actual edge; it supplies no decision about unknown
outside edges merely from an overlap of zero or one.

I found no counterexample or proof gap in the exact candidate statement.
The mathematical outcome is PASS for the stated necessary bounds only.
There is no new fixed17 enumeration, exact primal read, infeasibility result,
family exclusion, target resolution, novelty claim, external review or formal
verification. There are zero executed mathematical controls. Shared origins
are disclosed above; the set identification and counted-pair contradiction
here are the separate Native derivation. No prior computational gate is used
as a proof premise and no ledger/index/Git file is changed.
