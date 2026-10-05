# Independent written audit: the literal one-d3 R226/maxd3 b8 boundary

Completed independent verification: 2026-10-04T22:29:26.2279984Z.
Verifier: /root/native_driver. Mathematical producer: /root/structural.
Method: independent_derivation. No computational executor or worker.

Paper: docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD3_SINGLE_D3_NO_EIGHT_D2_V1.md,
SHA256 c837df53fdc78ba4da4ea1cd247bbf1b66446c8468cc0ca5b76f88b177fd23aa.
Raw candidate: acceleration/results/20261004_target_rook_count226_maxd3_single_d3_no_eight_d2_candidate01.json,
SHA256 0334264a9b8a51cd450cb9a8fa715c6ee0eb93c8cfb8ba1e8e530ac578b79d9f.
Exact ID: C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-SINGLE-D3-NO-EIGHT-D2-BOUNDARY r1.

The whole proof survives independent derivation and attempted falsification.
Written PASS is restricted to b!=8 under its exact maxd3/one-d3/R226
hypotheses. No one-d3 lane, R226 or target exclusion follows from this
audit alone. The logical dependency list is empty.

## Exact statement and shared-origin disclosure

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle T.
Suppose R=226, every d_T belongs to {0,1,2,3}, and exactly one actual
triangle has deficiency three. The number b of actual deficiency-two
triangles is not eight.

Structural produced the attached-root/equality-coordinate argument. Root
challenged its exact injection and equality thresholds. Native reconstructed
all actual labels, local profiles, the diamond concurrency bound, and the
zero-Gram coordinate contradiction. Earlier fan/parity/Gram overlap is
disclosed; shared agreement is not an independent derivation or gate.

## Target geometry and the exact local profiles

There are 231 actual triangles, because the 693 target edges each have
one triangle completion. At every vertex the seven incident triangles
partition fourteen outer neighbors. Distinct triangles meet at most once.
Three pairwise-intersecting actual triangles must concur: three distinct
intersection points would form a triangle giving one target edge a second
common neighbor.

For two intersecting triangles in an actual rook, their common point and
four outer points determine the four remaining grid points: each cross
nonadjacent pair has the common point as one neighbor and mu=2 fixes its
second. Hence their containing rook is unique, conditional on existence.
At a point, each rook containing a triangle gives exactly one covered
partner. The local graph of pairs in no rook therefore has degree d_T.
Zero-deficiency nodes are isolated. Summing triangle/rook incidences gives
sum d_T=1386-6R=30.

Assume b=8. With the sole d3 root T, this yields a=11, P=20. Local odd
degrees are d1 and d3, so r1+r3 is even. A positive fan at a point requires
its focal roots and two sets of their outer defect partners. External
triangles cannot meet two outer points of this whole fan: same-root points
violate linearity and different-root points give a nonconcurrent triple.
Thus

    P >= 3r1+5r2+7r3.

At a T point, r3=1 and r1 is positive odd. If r1=1, degree three requires
r2>=2; the fan permits exactly two. Its local degree sequence (3,2,2,1)
is forced: T joins both d2 roots and the d1 root; the d2 pair is joined.
Call this bad. If r1=3, the fan weight is sixteen and no d2 root fits;
T joins its three d1 leaves. Call this good. r1>=5 would need at least
22 positive roots. At bad points the fan already uses all twenty positives;
at good points no extra positive component is available. This treats all
three actual T points without an assumed profile or automorphism.

## Weighted identity with every incidence and extra edge retained

Select all eleven d1 triangles and T, so s=12. Their actual point incidence
is even. Write w for half of it, K=sum w(w-1), ell=sum(w_u-1)(w_v-1) over
selected edges, and H for the weighted sum of all other actual internal
edges. Nonzero weights are positive integers and K,ell,H>=0; weights larger
than two are not discarded. The selected weighted edge sum is 3s+4K+ell,
the total weight 3s/2, and the squared norm 3s/2+K.

The complete SRG identities A^2=12I-A+2J and A j=14j give
Q=3I-A+J/9 and Q^2=7Q. Thus q=w^TQw=||Qw||^2/7>=0 and

    q=s(s-6)/4-5K-2ell-2H=18-5K-2ell-2H.

Let h count bad T points. Good points have w=2; bad points w=1.
Consequently K>=2(3-h) and ell>=binom(3-h,2) from T's own edges.
h=0 gives q<=-18; h=1 gives q<=-4. These branches are impossible even
with arbitrary additional selected incidences or actual edges.

## Actual attached labels and the outside pair injection

At each bad T point there are two attached d2 roots. They are all distinct:
a root cannot meet T twice. Two at the same point cannot share a second
point; two at different T points cannot meet because that would form a
nonconcurrent triple with T. Their 4h outer points are therefore all
distinct and outside T. No other d2 root meets T.

If one outer point lies outside the selected support S, it has no d1 or
d3 root and at most one attached root. The attached node has degree two,
so the point contains at least two unattached d2 roots. Choose one pair
of those roots for that point. Different outer points must receive different
pairs, since actual triangles cannot meet twice. The injected pairs are
actual intersection pairs, not necessarily edges of the defect graph.

An attached triangle has its T point of weight one in S. If zero, one or
two outer points are in S, its nonselected weighted contribution to H is
at least zero, one or three. These edges are genuinely nonselected: an
edge belongs to its unique completing actual triangle, and this attached
root is not in the selection. Edges of different attached roots are
distinct. No assumption of induced S or equal attached profiles is needed.

## h2: retain the equality, then reject its exact bad coordinate

There are four attached and four unattached roots, with eight distinct
outer points. Five outside outer points would inject five distinct pair
edges into the intersection graph of the four unattached triangles. Such
a graph contains a diamond. Its two triangle triples are concurrent, and
the shared root pair has only one actual intersection, so all four roots
concur. All the five injected pair labels would then be the same point,
contradicting their distinct labels. In particular the argument is valid
even if an intersection is covered by a rook. It does not use an abstract
defect-graph triangle-free assumption. Four outside points are still allowed
by this bound; lowering it to three would be unjustified.

Thus at least four outer points lie in S and H>=4. There is one good
T point, giving K>=2. PSD and the exact formula force

    0 <= q <= 18-10-8 = 0,
    K=2, ell=0, H=4, Qw=0.

The good point accounts for all of K=2. Every other support point has
weight one; the good point alone has weight two. Since sum w=18,

    Aw=3w+2j.

The constant two is integral; integrality does not reject q=0.
At a bad T point p, its two selected triangles are T and its one d1
root. Their four other points are distinct. T's other two have weights
two and one. The d1 root's two others have weight one each: it meets T
only at p, and the good T point is the sole peak. Therefore the known
selected neighbor weight sum is 2+1+1+1=5. The equation at w_p=1 requires
exactly five. It leaves no additional edge from p to a positive support
point.

But at least four attached outer points lie in S. Any such point gives
an edge from its bad T point to a new support neighbor. It is not one of
the four selected neighbors: otherwise the edge would be in both a
selected and an attached actual triangle, contradicting its unique
completion. Its positive weight exceeds the already saturated value five.
This independently contradicts Qw=0. Equality is rejected pointwise,
not by a false assertion of strict positivity for all nonempty selections.

## h3 and exhaustiveness

With h=3 there are six attached roots, two unattached roots and twelve
distinct outer points. Every outside one requires the same unattached
pair. Their intersection is unique, so at most one can be outside S.
At least eleven are inside. Across six roots each with two outer points,
this requires at least five roots with both inside and the remaining root
with at least one inside. Hence H>=5*3+1=16. The exact identity gives
q<=18-32=-14. All twelve inside, larger weights or further actual edges
strengthen this contradiction. The four integer h cases are exhaustive,
which proves only the declared b8 exclusion.

## Written proof-check record: 30 checks, zero executions

1. Unique triangle completions give 231 actual triangles.
2. Seven incident triangles have distinct outer pairs.
3. Linearity and the nonconcurrent-triple prohibition follow from lambda=1.
4. Conditional intersecting-pair rook uniqueness follows from mu=2.
5. Local defect degree equals d_T and zero-degree partners are absent.
6. Actual triangle/rook mass gives D=30.
7. b8 with one d3 root gives a11 and P20.
8. Local odd-degree parity is r1+r3 even.
9. Whole-fan external partner labels are distinct.
10. Positive fan inequality has exact coefficients 3,5,7.
11. r1=1 forces the exact (3,2,2,1) bad profile.
12. r1=3 forces the good three-leaf star.
13. r1>=5 and all extra local components are excluded by P20.
14. Selected O has twelve roots and even actual incidence.
15. Exact weighted norms and selected edge expansion retain larger incidence.
16. Complete target Q^2=7Q yields q=||Qw||^2/7.
17. Exact q=18-5K-2ell-2H includes all extra internal edges.
18. T's good points give K and ell lower bounds.
19. h0 and h1 have the exact -18 and -4 contradictions.
20. Attached roots and their 4h outer point labels are all distinct.
21. At outside outer points at least two unattached roots are required.
22. Actual pair injection is injective across distinct outside points.
23. Attached internal contributions have lower bounds 0,1,3.
24. Five pairs on four actual roots force diamond concurrency.
25. h2 outside capacity four gives H>=4 and only q=0.
26. Exact equality forces K2, ell0, H4 and the unique good-point peak.
27. Qw=0 gives the integral coordinate equation Aw=3w+2j.
28. Selected bad-point neighbor sum five exactly saturates that equation.
29. An inside attached outer point is a genuine additional support neighbor.
30. h3 outside capacity one gives H>=16 and q<=-14; h coverage is exhaustive.

## Written falsification/boundary record: 12 challenges

1. Maximum deficiency three is assumed, not inferred from another paper.
2. The earlier c1 necessary range is not a logical premise.
3. All r1 odd profiles are examined before good/bad naming.
4. Arbitrary selected incidence four and greater is retained until equality.
5. The h2 pair graph includes covered actual intersections.
6. A four-cycle on four unattached roots does not force concurrency or capacity three.
7. Diamond concurrence needs actual root labels, not just an abstract graph.
8. Roots at different T points cannot share an outer label.
9. sum w/9=2 is integral, so no generic strict-positivity shortcut is used.
10. The sole good peak cannot also lie on a bad point's d1 triangle.
11. Extra attached edges are distinguished from unique selected edge completions.
12. The h3 count permits mixed outer profiles and all further actual edges.

There are 42 written checks and no computational/formal/external checks or
solver calls. Only small documentary reads, four selected file hashes and
append-only metadata use tools. No mathematical program, import, worker,
enumeration, ledger parse/write, Git/index or publication mutation occurred.
Root-reported live467 is context only. Original scopes, timestamps, pending
nulls and historical bytes are preserved. Root's exact new acceptance and
registration require separate later actions.
