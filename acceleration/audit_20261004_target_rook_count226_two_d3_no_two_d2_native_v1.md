# Independent written review: disjoint D3 / b2 branch

Completed written verification: 2026-10-04T22:01:57.9291347+00:00.
Producer: /root/structural. Different author verifier: /root/native_driver.
Method: independent_derivation. Computational executor: null. Outcome: PASS.
Claim C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-TWO-D3-NO-TWO-D2-BOUNDARY r1.
Paper docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD3_TWO_D3_NO_TWO_D2_BOUNDARY_V1.md
SHA256 c2dcb60409b9ad42e4baaf1aad0e42ab3b04e887fdc212ecb0863ad993b74069.
Raw acceleration/results/20261004_target_rook_count226_maxd3_two_d3_no_two_d2_boundary_candidate01.json
SHA256 547d64b978304c37c6a8f5feb2ee70978a4cb2108cf58f6dcbb6f6f660138d2f.
The exact statement, assumptions, empty logical dependencies and original
pending nulls are retained in the bound report. This disjoint branch does not
inherit the repaired intersecting-branch gate.

## Independently reconstructed starting facts

Unique triangle partners in the target give231 actual triangles, pairwise
intersection at most one point, and no three pairwise intersections at three
distinct points. A point has seven actual incident triangles. The local rook
partner bijection gives local defect degree d_T and global degree3d_T.
At R226, deficiency mass is30. Assume the two D3 triangles A,B are disjoint
and b2 with D2 roots X,Y. Then a20 and P24. The local simple graph gives
r1+r3 even, and injection of the two outer partner sets gives the actual fan
bound3r1+5r2+7r3<=24. No arbitrary profile is substituted for actual labels.

On A/B, a bad point has r1=1. Degree three needs both X,Y, giving the valid
local profile(3,2,2,1). There cannot be two such points because X/Y would share
twice. All other A/B points have r1>=3. This proves the complete h0/h1 split.

## No bad point: strict positive Gram energy and actual intersections

Select O=D1 union D3, s22. The local degree sum makes its incidences even;
w is half the incidence, with sum w33 and arbitrary integer weights on support
S. For K=sum w(w-1), ell=sum selected edges(w_u-1)(w_v-1), and H the weighted
sum of every other actual internal support edge, unique triangle edges give
E_selected=66+4K+ell and ||w||^2=33+K. Target adjacency obeys
A^2=12I-A+2J, so Q=3I-A+J/9 has Q^2=7Q and is PSD. Direct substitution gives
q=w^TQw=88-5K-2ell-2H>=0, retaining all larger incidence and added edges.

At h0, the six distinct A/B points have w>=2, hence K>=12 and ell>=6 from
the six selected edges in A,B. Every D2 root is wholly in S: an outside point
has no odd-deficiency root, so its positive local degree-two graph would need
at least three D2 vertices, but only X,Y exist. Let t count their actual
intersections with A/B. Each has at most two, with weights at least two there.
The three weighted edges of a D2 triangle contribute at least3,5,8 for zero,
one,two such points. Thus H>=6+2t and q<=4-4t.

If q=0, Q^2=7Q implies Qw=0. Each coordinate of Qw is the integer
3w_v-(Aw)_v plus33/9=11/3, with fractional part2/3, so none can be zero.
Therefore q>0 and t>=1 is impossible. X,Y are actually disjoint from A,B;
this stronger actual intersection conclusion cannot be weakened to absence
of a defect edge when describing the proof.

## Cycle facts reconstructed without a pending theorem

Nonadjacent target pairs give2079 actual induced squares. A rook has nine and
a square has at most one containing rook by unique edge triangles. Hence at
R226 there are45 uncovered squares. Their edge triangles give injective F4s
with distinct corner labels. Conversely any F4 with adjacent labels coinciding
has all four triangles concurrent, by linearity and the loose-triple prohibition.
Such a local four-cycle requires four high roots. A,B are disjoint, so it cannot
occur here. Distinct-label F4s give their actual uncovered square; extra square
diagonals would violate lambda1. Thus C4(F)=45 and total cycle incidence180.
The lower180 alone is enough for all ensuing contradictions.

F has no K3,3: a repeated grid label propagates to six concurrent roots of
local degree at least three, but only A,B have deficiency3. All-distinct labels
give an actual induced rook whose defect edges contradict it. Pair codegrees
are at most3: a pair including a low has degree3 cap; disjoint high triangles
have an actual cross-edge matching and at most three transversal common roots;
intersecting highs' common roots must be concurrent at their unique point.

No low belongs to an F triangle. A low with a low neighbor has cycle count
at most5; equality6 would force a K3,3 using that neighbor's degree-three set.
Only a low whose three neighbors are independent highs may add1 to this bound.
There are at most3 for each high triple by pair codegree. This is an upper
bound on exceptions, not an asserted exact population.

In the high topologies below, N_F(Z) has an empty internal graph or one edge.
No internal opposite then has two internal edges. All unspecified low-neighbor
edges are forbidden by filled local slots or the actual loose-triple veto.
For external opposite codegree l<=3, choose(l,2)<=l. The exact remaining stub
sum is B_Z=sum_(N(Z))deg-deg(Z)-2e(N(Z)), giving c_Z<=B_Z. If B_Z is not
divisible by3, equality would require every nonzero l=3, impossible, hence
c_Z<=B_Z-1. This formula includes external high and low opposites.

At h0, A,B each have nine independent low neighbors, yielding18 each. If X,Y
have no F edge, their six lows yield12 each; four independent high triples
allow at most12 low exceptions. Total100+12+36+24=172<180. If XY is an F edge,
each has five lows plus the degree-six other root, yielding15 each; only two
independent high triples remain, allowing6 exceptions. Total100+6+36+30=172.
A covered actual X/Y intersection with no F edge remains inside the first safe
case. Actual intersection is never silently identified with defect adjacency.

## One bad point: complete high topologies and opposite pools

Let it be on A, with high triangle AXY and one low leaf at A. B can meet at
most one of X,Y: two distinct intersections would make the loose triple BXY;
coincident intersections force a second X/Y meeting or A/B meeting. If B meets
X, local parity plus degree three needs at least three D1 roots. Five D1 gives
fan27>24. Therefore the exact(3,2,1,1,1) profile forces the BX defect edge.
This gives just triangle+isolated B or triangle+pendant BX. Their high
independence number is2, so all twenty lows have a low neighbor and total<=100.

For the isolated case A has seven lows plus X6,Y6 and one internal XY edge:
B_A=22 so c_A<=21. X,Y have four lows plus high degrees9/6 and one internal
edge: B=19 so each<=18. Isolated B<=18. Complete total175<180.

For the pendant case the generic bounds are A21,X24,Y18,B21. The generic
total184 is insufficient, so Y must be decomposed, not dropped from the sum.
Its neighbors are A,X and four independent lows L_Y, with internal AX edge.
A low in L_Y cannot also meet A or X: it already meets Y at their common
point, and no D1 has local degree two. Its only possible second high is B.
Let n be their number. Y,B already have common high X, so codegree cap3 gives
n<=2. The L_Y nodes have8-n remaining LL stubs.

The external HIGH opposite B has common high X and n lows, contributing
choose(1+n,2)<=3n/2. An external LOW opposite has I0/1 high neighbors among
A,X (these highs intersect), and x neighbors in L_Y; its degree3 gives
choose(I+x,2)<=3x/2. Sum x=8-n because L_Y is independent. Internal AX gives
zero opposite contributions. Thus c_Y<=3n/2+3(8-n)/2=12. Every opposite pool
is included, explicitly including B; complete total100+21+24+12+21=178<180.
Both h0 and h1 are now rejected, proving exactly the literal b2 exclusion.

## Independent checks and failure boundaries

Thirty-six proof checks on paper:
1.231 actual triangles; 2. linearity; 3. loose-triple prohibition;
4. local defect degrees; 5. D30/a20/P24; 6. parity/fan injection;
7. exact bad profile; 8. at most one bad point; 9. h0/h1 coverage;
10. even O incidence; 11. integer weight and sum33; 12. selected-edge identity;
13. Q^2=7Q/PSD; 14. q identity; 15. six-point K and ell bounds;
16. wholly-S D2 proof; 17. weighted edge costs3/5/8;
18. q<=4-4t; 19. q0 impliesQw0; 20. fractional11/3 contradiction;
21. actual D3-D2 disjointness; 22. square/rook45 count;
23. collapsed-label exclusion; 24. F4 incidence180;
25. both K3,3 label cases; 26. codegree3;
27. low5 and exception counts; 28. complete high stub formula;
29. nondivisible B correction; 30. h0 both172 totals;
31. h1 exact triangle/pendant topologies; 32. isolated175;
33. pendant generic184 insufficient; 34. n<=2 and8-n LL stubs;
35. B external-high contribution plus all low/internal pools;
36. refined Y12 and178 contradiction.

Twelve failure/boundary challenges on paper:
1. q>=0 alone does not remove t1; strict q>0 uses the literal fraction.
2. Changing sumw to a multiple9 would invalidate that fraction argument.
3. Incidence six or greater is retained in K, not clipped.
4. Added support edges stay in H and can only decrease q.
5. Actual covered XY intersection remains distinct from an F edge.
6. A collapsed four-cycle would invalidate faithful equality; disjoint A/B
   excludes it and the injection lower bound would still suffice.
7. Low exceptions are allowed at h0, not silently removed.
8. A valid local high triangle/pendant is not rejected as triangle-free.
9. Generic pendant184 does not prove the theorem without the Y refinement.
10. n0/n1/n2 all satisfy the exact high/LL cancellation to12.
11. External B cannot be omitted or counted inside the LL pool.
12. No inferred disjointness/maxd3, full c2, R226 or target exclusion follows.

Total48 written checks; all executed/formal/external/solver counts zero.

## Scope and provenance

Root shared strict-zero and small-topology outlines; Structural authored the
whole candidate. Native independently reconstructed all identities, actual
intersection cases and complete opposite pools. Shared agreement is not
verification; no independent discovery or novelty is claimed. No preceding
R226 claim or repaired intersecting-b2 gate is a premise; dependencies empty.
The explicit D3-disjointness/maxd3 assumptions remain literal, and neither c2
as a whole nor R226 nor target is excluded here. UNKNOWN/NONE remains the
global scope. Original bytes, pending nulls and timestamps are preserved.
No mathematical program/import/AST/backend/worker/census/solver, ledger parse
or Git/index/publication/protected mutation occurred. Root-reported457 is
context only; metadata creation and future Root exact acceptance are separate.
