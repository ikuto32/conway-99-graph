# Independent written derivation excluding exactly seven D2 triangles at R227

Verification timestamp: 2026-10-04T19:46:24.4949744Z.
Mathematical producer /root/structural; independent verifier /root/native_driver.
Root suggested a follow-up and challenged selected-fan, concurrence and
integer-equality steps. Structural wrote the support15 argument and lemma.
Shared mechanisms are disclosed; agreement supplies no verification.

Exact claim C-UNRESTRICTED-TARGET-ROOK-COUNT227-NO-SEVEN-D2-BOUNDARY r1.
The complete frozen paperfdac5f82b885cb956f7b12b649edc7f5466c12fa055aeb6d02082862dea23f3b
and rawdeb7f20d704d9396667d1a6f36c61546a33944fa1acb64648ea85d1f7dd40283
were read. This is a separate hand reconstruction, with no mathematical
program, source import, AST/syntax check, backend, solver, census, worker,
ledger parse or Git/index/publication mutation. Earlier bytes remain intact.

## Explicit hypotheses and direct local geometry

Take a complete finite simple SRG(99,14,1,2), with R227 actual induced
rook-nine subsets counted once. Define d_T=6-r_T for every actual triangle
T. ASSUME EXPLICITLY every d_T is0,1,2. For contradiction ASSUME exactly
seven triangles have d2. There are no inherited logical dependencies.
No no-D3/population/common-point result is imported from an earlier gate;
those papers are comparison evidence only. Nor is any arbitrary even
ten-triangle selection ruled out merely by the conclusion here.

Each target edge has its unique actual triangle partner. Every vertex
belongs to seven triangles, and different triangles meet at mostonce.
Three cannot meet pairwise at three distinct points: their three intersection
points make an edge have a second triangle partner, violating lambda1.
For an intersecting triangle pair any containing rook is unique, fixed
by its four opposite cross pairs' second common neighbors. At a point,
the simple defect graph on its seven triangles joins pairs lacking a
containing rook and has degree d_T at node T: its r_T covering partners
are distinct. Zero-degree nodes cannot provide defect edges.

The local degree sum is even. Under maxd2, this means the d1 triangles
are an even point-incidence selection. There are231 actual triangles,
six per rook, hence total deficiencyD24. At b7 the d1 count is10 and
total positive countP17.

At a point with r1,r2 positive triangles, all their outer points are
distinct. Each outer point of a di triangle needs i other positive
triangle defect partners. An external triangle meets at mostone outer
point of that entire fan: two within one triangle violate linearity,
two in different fan triangles form forbidden distinct intersections.
Therefore P>=3r1+5r2. This concerns actual points and distinct actual
triangles, retaining all extra target edges and nondefect incidences.

## The separate selected-ten fan forces support15

At a point used by r selected d1 triangles, the2r outer points are
distinct. At each, one selected incidence comes from that fan and even
selected parity requires another. The10-r external selected triangles
can each meet at mostone of those fan outer points. Thus

    10-r>=2r, equivalently10>=3r.

Every used selected point has positive even multiplicity, so r=2. In
particular r4 is excluded by this ten-selection bound, not by P17, whose
positive fan bound alone would permit r1=4,r2=0.

The30 selected incidences therefore use exactly15 distinct actual vertices
S. The ten actual d1 triangles supply30 distinct edges inside S, since
two triangles cannot share an edge. No inducedness of S is assumed; its
actual additional edges remain present and can only increase e(S).

## Every D2 point outside S is an exact triple concurrence

At a point outside S there is no d1 triangle. A d2 node in its local
defect graph needs two different positive partners, so at leastthree d2
triangles occur there. The positive fan bound5r2<=17 permits at mostthree.
Thus exactlythree of the seven d2 triangles meet each of their points
outside S. Local zero nodes cannot substitute for either partner.

Let h count these distinct outside-S points, and t_i count the outside-S
points of the i-th d2 triangle. Each t_i is an ordinary integer0,1,2,3
and counting labelled actual incidences gives sum_i t_i=3h. This is not
a formal fractional point profile or an assumed uniform number of outside
points per triangle.

## Seven-triangle triple-point lemma with actual no-loose-triple geometry

If h=0 the desired h<=3 is immediate. Otherwise fix one counted triple
point p, with its three base d2 triangles. The remaining four d2 triangles
are external. A different counted triple point q belongs to at mostone
base triangle, since two base triangles already share p. It is therefore
either attached, using one base triangle plus two externals, or detached,
using three externals. These are all possibilities because each counted
point has exactlythree d2 incidences.

The external pairs at distinct attached points are disjoint. If one
external triangle U were used at both q,q', equal base roots would give
two intersections of U with that root. Different base roots already meet
at p, so their intersections with U at q,q' would form a forbidden
distinct-intersection triple. This is where no-loose-triple geometry,
not mere linearity, is essential. Onlyfour external triangles exist, so
at mosttwo attached points are possible.

At mostone detached point occurs: two three-subsets of those four externals
share at leasttwo triangles, which would then meet at both detached points.
If two attached points and one detached point all occurred, their disjoint
external pairs would partition the four externals. Any detached three-subset
contains one entire pair. Those two triangles already meet at its attached
point and would meet again at the detached point, violating linearity.
Thus at mosttwo other counted points coexist besides p, proving h<=3.
All these are distinct actual points; uncounted additional intersections
cannot evade the forbidden pair/triple arguments.

## Integer edge terms add at least five distinct actual edges

The i-th d2 triangle has3-t_i actual points in S, supplying choose(3-t_i,2)
internal edges. All such edges are distinct across the seven d2 triangles
and from the30 d1 edges by the unique triangle partner rule. The integer
table is

| t | actual edge term | 2-t | gap |
|---|---:|---:|---:|
|0|3|2|1|
|1|1|1|0|
|2|0|0|0|
|3|0|-1|1|

Consequently sum_i choose(3-t_i,2)>=14-sum_i t_i=14-3h>=5. Equality
requires h3 and no t0/t3, hence five t1 and two t2 from seven terms summing9.
This equality distribution is not assumed impossible by the concurrence
lemma and is not claimed to extend to a complete target.

As an additional check, the exact identity choose(3-t,2)=3-2t+choose(t,2)
gives total21-6h+sum_i choose(t_i,2). At h<=2 the direct lower bound is9,
stronger than needed. At h3 with two t2 and five t1 the total is3+2=5.
Thus the ordinary induced edge count, including arbitrary extra edges, obeys

    e(S)>=30+5=35.                                         (1)

## Full99 upper Gram and its indispensable integer equality rejection

Direct target neighborhood counts give A^2+A=12I+2J and Aj=14j. A is
real symmetric. On j-perpendicular its eigenvalues solve theta^2+theta=12,
hence are3 or-4. Therefore Q=3I-A+J/9 is real positive semidefinite: its
j eigenvalue is3-14+99/9=0 and the others are0 or7. No archive spectral
gate, finite-field rank or new left-code existence is inherited.

For the indicator chi of the fifteen actual points S,

    chi^T Q chi=3*15-2e(S)+15^2/9=70-2e(S).

Positive semidefiniteness gives e(S)<=35. If e35, this quadratic form is
zero and the real symmetric PSD spectral decomposition implies Qchi=0
at ALL99 coordinates. At any of84 outside vertices, the row equation
is -number_of_S_neighbors+15/9=0. It demands an ordinary integer neighbor
count5/3, impossible. Thus the actual integer e(S) is at most34, strictly
contradicting(1). Positivity alone does not supply this strict bound;
the full-target equality equation and ordinary integer interpretation do.

The exact seven-d2 boundary under the explicit maxd2/R227 hypotheses is
excluded. No other R227 population, arbitrary even-ten selection, graph
realization or target existence/nonexistence conclusion follows here.

## Ten hand falsification boundaries

1. Four d1 nodes in a local matching fit the P17 fan12<=17. They fail
   the separate selected10 bound12>10, showing why these two bounds differ.
2. Three triple points can share one base triangle, each with two private
   leaves: the seven-triangle star saturates h3 and no-loose-triple geometry.
3. The chain p:T1,T2,T3; q:T1,T4,T5; r:T2,T6,T7 has two t2 and five t1.
   It obeys linearity/no-loose-triple and attains the five-edge term boundary.
   Private third points complete these triples; no target extension is claimed.
4. Linearity ALONE allows four triple points: use six triangles on all
   pairs of four distinguished points, each with a private third point,
   plus one private triangle. The pair triangles12/13/23 form forbidden
   distinct intersections. Thus linearity alone cannot prove h<=3.
5. Two attached external pairs plus one detached external triple force
   a repeated pair intersection, not merely an abstract overlap count.
6. A t3 triangle supplies zero internal edges while2-t=-1. The inequality
   permits that case; it is not silently removed from the domain.
7. Additional actual edges in S increase e(S); S is never assumed induced
   by only the ten selected triangles and seven high triangles.
8. PSD non-strict edge35 is compatible with zero quadratic value as a
   formal real Gram condition. The ordinary outside-coordinate integer
   neighbor count excludes equality for the complete target.
9. The strictness step uses S15<99 with84 actual outside rows; a full-set
   indicator or a fractional formal incidence model is outside its scope.
10. Maxd2 and b7 are explicit conditions in the contradiction argument.
    Earlier noD3/lower4/noeight/common-point gates supply no premise.

## Thirty-four explicit written proof checks

1. Exact target/R227/maxd2 statement and b7 contradiction scope.
2. Empty logical dependency list; comparisons provide no gate transfer.
3. Actual edge uniqueness, triangle linearity and distinct-intersection rule.
4. Exact local defect degree from intersecting pair-rook uniqueness.
5. Local handshake gives even selected d1 point incidence under maxd2.
6. Triangle/rook double countD24,a10,P17.
7. Actual positive fan3r1+5r2 via distinct external incidence injection.
8. Separate selected10 outer parity requirements.
9. Each external selected triangle meets at mostone fan outer point.
10.10>=3r plus positive even incidence forces r2.
11.30 selected incidences give15 actual vertices.
12. Ten actual triangles supply30 distinct edges, no support-inducedness premise.
13. OutsideS noD1; degree2 needs at leastthree positive high nodes.
14. P17 fan allows at mostthree, giving exact triple incidence.
15. Integer t0..3 and sum t=3h.
16. Fix base triple point; other counted points use at mostone base triangle.
17. Attached points use external pairs, detached points external triples.
18. Shared external at two attached points violates linearity/no-loose-triple.
19. Four external triangles allow at mosttwo disjoint attached pairs.
20. Two detached triples share two actual triangles, impossible.
21. Two attached plus one detached repeats a pair intersection.
22. Hence h<=3 with explicit actual labels.
23. Exact four-value integer edge table and equality gaps.
24. Seven high internal-edge contributions disjoint from each other and low edges.
25. Sum edges>=14-3h>=5 and equality five t1/two t2.
26. Stronger exact identity at h<=2 independently checks the small boundary.
27. Actual e(S)>=35 with arbitrary extra target edges retained.
28. Direct adjacency identity/row sum and real symmetric eigenvalues3/-4.
29. Q PSD on full99, j eigenvalue0 and other eigenvalues0/7.
30. Indicator quadratic70-2e and non-strict bound35.
31. Zero PSD quadratic implies the full vector equationQchi0.
32.84 outside rows would each require integer neighbor count5/3.
33. Strict actual edge upper34 contradicts lower35.
34. Only exact b7 boundary excluded; maxd2 and other populations remain explicit.

Parity/fan/upper-Gram ingredients overlap earlier written records and are
freshly reconstructed here. The seven-triangle no-loose-triple lemma and
full99 integer strictness are stated with their necessary boundaries.
Forty-four hand proof/boundary checks survive, including four integer-term
rows. Zero executed/formal/external verification is asserted. No whole-
archive novelty, registration authority or new computational authorization
follows. Historical evidence, closed Wave46 cutoff and protected state stay
unchanged; Root exact-scope review and next-wave47 registration are separate.
