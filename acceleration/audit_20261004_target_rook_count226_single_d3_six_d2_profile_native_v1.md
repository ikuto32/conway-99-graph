# Independent written audit: the literal R226 one-d3/six-d2 profile

Completed independent verification: 2026-10-04T23:05:34.8274842+00:00.
Verifier: /root/native_driver. Mathematical producer: /root/structural.
Method: independent_derivation. No mathematical worker or program executed.

The whole frozen paper and the complete raw claim were read:

- docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD3_SINGLE_D3_SIX_D2_PROFILE_V1.md,
  dc40b2a3aecf6709a14b3a9d88ded6dfddc596d7fdc65a6faabf15fd7daa4a5c.
- acceleration/results/20261004_target_rook_count226_maxd3_single_d3_six_d2_profile_candidate01.json,
  3209080c5e6d41892e0af54cc93c1fbce0c0c1df98a0bb3f0ea9f6e932e2410a.

PASS is recommended for exactly its revision1 conditional statement. Maxd3,
R226, one d3 and six d2 roots are hypotheses. At most one T point is bad;
the h0 branch has the stated four-cell equality and component consequences.
The h1 branch, the entire one-d3 lane, R226 and the target remain unresolved.
The empty dependency list is justified by reconstruction from the complete
SRG hypotheses here, not by transferring earlier profile approvals.

Root's per-center capacity, eigenvector and equality outlines were shared.
Structural produced and challenged the frozen proof and containing-rook
argument. Native used separate Gram/norm and actual-label reconstruction,
including a pre-freeze different norm route for h2/g0, and then challenged
the precise frozen AY route. Shared mechanisms do not imply independent
discovery. No novelty claim or broad archive survey is made: the fan,
weighted Gram and historical prism-cell overlap is expressly retained.

## Foundations and exact selected expansion

1. SRG multiplication gives A^2=12I-A+2J and Aj=14j. On the orthogonal
   complement of j its roots are3 and-4. Thus Q=3I-A+J/9 is positive
   semidefinite, Qj=0, Q^2=7Q and AQ=-4Q.
2. Every target edge belongs to its unique triangle, by lambda1. The
   fourteen neighbors of a point therefore form seven disjoint edges.
   There are693 edges and231 actual triangles.
3. For two intersecting triangles, a containing rook, if one exists, is
   determined by their four outer-pair second common neighbors. Mu2 gives
   uniqueness conditional on containment; existence is not inferred.
4. At each point a rook on an incident triangle covers exactly one of its
   six other incident-triangle partners. Uniqueness makes the local defect
   degree exactly6-r_U=d_U. A degree-zero root has no defect partners.
5. Summing degrees of this actual local graph makes the odd-degree roots
   even in number at each actual point. Hence D1 union {T} has even
   incidence, including arbitrary intersections and extra actual edges.
6. Three pairwise-intersecting distinct triangles must concur. Otherwise
   their three distinct intersections form a triangle, adding a second
   common neighbor to an edge already in its original actual triangle.
7. An external root can meet at most one outer point of a whole fan:
   twice on one root violates linearity; once on two fan roots gives the
   forbidden nonconcurrent triple. The two outer points of each positive
   fan root require d_U distinct external partners. Counting yields
   P>=3r1+5r2+7r3, without imposing disjoint defect components.
8. Each rook contains six actual triangles. Thus sum d=6*231-6R=30.
   With c1/b6 the d1 population is15 and the positive population is22.
9. At a T point r1 is odd. The fan bound and simple local degree sequence
   leave exactly B=(r1,r2)=(1,2), G0=(3,0), G1=(3,1), F=(5,0).
10. B has T adjacent to the two d2 roots and its d1, and the d2 pair
    adjacent. G1 has T joined to its d2 and two d1 leaves; that d2 joins
    the remaining d1. F really has T's three-leaf star plus a separate
    d1-d1 edge. This permitted local component is not omitted.
11. The16 selected triangles give W=sum w=24 for half-incidence w.
    Every supported w is a positive integer; no incidence upper bound
    has yet been assumed. Put K=sum w(w-1), ell the selected excess-product
    sum and H the weighted sum on all other actual internal edges.
12. Selected edges are distinct. Writing each weight as1+(w-1), their
    weighted sum is3s+4K+ell: selected incidence2w supplies the4K term.
    Since ||w||^2=W+K and W^2/9=64, direct expansion gives
    q=wQw=40-5K-2ell-2H.
13. If q=0, positive semidefiniteness forces Qw=0. There is an outside
    point because |S|<=W=24<99; there Aw would have to equal W/9=8/3,
    contradicting its integer value. Thus q>0, not merely q>=0.
14. Y=3Qw=9w-3Aw+8j is integer2 mod3, has sum0, obeys AY=-4Y and
    has squared norm9wQ^2w=63q. The factor63 is essential.

## Actual attached-root capacities and focal exclusions

15. Attached d2 roots at different T centers and all their outer points
    are distinct. Repetition within one fan violates linearity; between
    centers it forms a nonconcurrent triple with T.
16. An attached outer point outside S lies on no d1 or T. Its local
    defect degree two therefore requires two other d2 roots. Neither
    partner can be attached: same-fan reuse violates linearity/loose
    concurrence and different-fan reuse supplies another CN to a T edge.
17. At one fan center each unattached root meets at most one outer point;
    k outside points require2k distinct unattached roots. Two distinct
    outside points cannot use the same unattached pair. With only two
    unattached roots at most one attached outer point is outside globally.
18. A weight-one centered d2 root with0/1/2 inner outer points contributes
    at least0/1/3 to H. A weight-two center contributes0/2/5. Every counted
    edge is nonselected and distinct by unique actual triangles.
19. If F coexists with a good T point, their weights3/2 give K>=8 and
    ell>=2 already on T, so q<=-4. Two F points only increase K.
20. The remaining F/B/B case has four attached and two unattached roots.
    Each bad center has at most one of its four outer points outside;
    its attached pair contributes H>=4. Hence H>=8, K>=6 and q<=-6.
    Its separate low-low local defect edge is retained throughout.
21. In h2/G0 at least seven of the eight attached outer points are inner,
    giving H>=10. K>=4 would make q<=0. Therefore K=2, with just the good
    T point r of weight two and every other supported weight one; ell=0.
22. Choose p with all four attached outer points inner; at the other bad
    center q at least three are inner. Before these d2 edges, all three T
    coordinates and the six ordinary selected neighbors of r have Y=2;
    other supported ordinary coordinates have Y=5. Further edges can
    only decrease these upper bounds.
23. The eight distinct forced S neighbors of p are r, q, the two ordinary
    points in its selected d1, and its four attached outer points. Their
    Y sum is at most2-7+10-4=1. Each attached outer point receives two
    distinct extra unit-weight neighbors, so indeed has Y<=-1.
24. If p has a further S neighbors, their weights are one (r is already
    included) and Y<=5. Its exact weighted degree gives Y_p=-10-3a.
    Its remaining6-a exterior neighbors have Y<=5 because they see p.
    Hence (AY)_p<=1+5a+5(6-a)=31, whereas -4Y_p>=40: contradiction.
    Arbitrary further supported and exterior edges are not discarded.
25. In h2/G1 there are five attached roots and one unattached root. Every
    attached outer point is inner, giving H>=4*3+5=17. Together with
    K>=2, this gives q<=-4. This separately covers the good attachment.
26. In h3 all six roots are attached; all twelve distinct outer points
    are inner and H>=18. K>=2 makes q negative, so K=0, |S|=24 and ell=0.
27. Put H=18+z. Positivity gives z=0 or1. After the forced d2 edges the
    inside Y coordinates are3 copies of-7,12 of-1,9 of5, with norm384.
    Each further edge decreases two coordinates by3; for a current
    coordinate <=5 the squared-norm change is >=-21. Thus inside norm
    >=384-42z, larger than the entire norm252-126z. This proves h<=1.

## The h0 equality, derived cells and containing rooks

28. Three good T points give K>=6 and ell>=3. K is even; K>=8 makes q
    negative. Thus precisely the three T points have weight two and the
    other eighteen support points weight one: S21, K6, ell3, q=4-2H.
29. The nine central selected d1 roots produce eighteen distinct ordinary
    points, by linearity and lambda1 on T edges. The other six d1 roots
    partition those points. Each ordinary point sees exactly one T point.
30. Each outer actual triangle is rainbow in those three T colors, since
    two adjacent points with the same T neighbor would have a second CN.
    Each central matching edge joins equal T colors. Baseline Y is-4 on
    T and2 on Bs, with inside sum24 and norm120.
31. Let d count nonselected S edges at T. Total weighted neighbor
    increment is2H-d, its T portion d. The integer square bounds at
    baseline2 and-4 are respectively -3k and33k. Consequently inside
    norm>=120-6H+39d and inside sum=24-6H+3d.
32. For each of78 exterior integers2 mod3, y^2-y-2>=0, with equality
    only at-1 or2. SumY0 makes exterior norm>=132+6H-3d. Total norm
    >=252+36d versus252-126H forces H=d=0 and all exterior equality.
33. The exterior sum-24 and78 coordinates give18 values2 and60 values-1.
    Name them Bo and C. H0 makes the actual S graph exactly48 selected
    edges, rather than assuming inducedness before the equality.
34. A T point has selected-neighbor Y sum4 and must have total16; its
    other six neighbors therefore all have value2 and belong to Bo.
    These three Bo neighbor sets are distinct by lambda1 on T.
35. A Bs point has one T and three Bs neighbors with Y sum2. Its ten
    exterior neighbors must sum-10, so all belong to C and Bs-Bo=0.
36. At Bo, Y=8-3Aw=2 implies weighted S-degree2. Since Bo has no Bs
    edges, it sees exactly one T point. AY gives Bo degree3 and C degree10.
    At C, weighted S-degree3 and no T neighbor give Bs degree3; AY gives
    Bo degree3 and C degree8. This independently reproduces all four rows
    [2,6,6,0], [1,3,0,10], [1,0,3,10], [0,3,3,8].
37. There are r_T=3 actual containing rooks. Their six exterior points
    form connected prisms and must lie wholly in Bs or wholly in Bo,
    since those cells have no cross edges. At G0 none of its Bs central
    triangles is covered with T; at G1 exactly one is. Thus the number
    of Bs rooks equals the G1 indicator at each T point. Mixed indicators
    are impossible; only all-zero or all-one remains at this stage.
38. Distinct rooks on T have disjoint exterior sets. A shared point has
    a unique T neighbor and its unique local triangle; conditional pair
    uniqueness would then make the two rooks identical. A Bo prism is
    saturated in its cubic induced cell and hence a whole component.
39. If all indicators are one, one Bs prism and two Bo prism components
    occur. The six remaining Bo points still induce a simple cubic graph.
    A cubic six-vertex graph with an actual triangle is a prism: its
    three distinct exterior neighbors must form the other triangle.
    If triangle-free, its neighbor triple is independent and the two
    remaining points must join all three, giving K3,3. Mu2 rejects K3,3.
40. In the remaining prism each triangle is rainbow in T colors.
    Nonadjacent prism vertices already have two prism common neighbors,
    so cannot share a T neighbor; therefore equal colors are precisely
    matching pairs. Adding T gives an actual induced fourth rook, not
    merely a candidate abstract embedding. This contradicts r_T=3.
41. All G1 indicators are zero; all good d2 attachments vanish. The three
    containing rooks give three disjoint cubic prism components covering
    all eighteen Bo vertices, with each T-plus-prism an actual rook.
42. Each Bs component contains whole outer triangles. If it has r such
    triangles, every color has r vertices and their central matching
    stays inside the component, so r is even. A two-triangle component
    is a cubic six-vertex prism and would give a forbidden Bs rook.
    Six triangles cannot split into even component sizes all >=4.
    Therefore Bs is connected cubic18. No simple contracted graph,
    connectedness assumption or three-cross-edge shortcut is used.

## Eighteen explicit failure and scope challenges

43. A seven-node local defect graph allows the F star plus a separate
    low-low component. Removing it from the initial list would leave a
    genuine coverage gap; the separate K/H proof is necessary.
44. The P22 fan allows G1; the earlier P21 dichotomy cannot be imported.
45. Even selected incidence can exceed four. Only the exact nonnegative
    K/ell/H inequalities force the weights used in each later branch.
46. The h2/G0 good point gives K2, not K4. Assuming K4 initially would
    bypass the real survivor; the AY31<40 contradiction handles it.
47. At an attached exterior point d0 roots cannot act as defect partners.
    Without exclusion from S, d1/T partners would be possible, so the
    exterior-support hypothesis must be retained in the capacity step.
48. Pair reuse across distinct exterior points violates linearity, while
    same-center fan reuse needs the actual concurrent-triple argument.
    A count of abstract unlabeled pairs alone would not justify the proof.
49. Attached roots at different T centers cannot be conflated: actual T
    edges already have their sole triangle CN. This also guards all inner
    H edge counts and the eight distinct forced neighbors in h2/G0.
50. Extra edges at p change its exact Y and its residual neighbor count
    together. Treating a as additional edges without reducing6-a would
    give a different inequality. The frozen bound handles both exactly.
51. Current Y coordinates may become negative under extra edges; the
    h3 norm estimate remains valid because the square increment lower
    bound holds for every current Y<=5, not just the initial values.
52. Factor63 in ||Y||^2=63q and integer residue2 mod3 were checked;
    using an unscaled Q norm or ordinary integer residue would fail.
53. q=0 is rejected here because24/9 is nonintegral at an outside point.
    This is a lane-specific argument, not a general prohibition on Q zero.
54. The h0 derivation does not presume S induced: H includes every other
    actual internal edge and the norm forces H0. Nor are the cell rows
    assumed equitable before they follow from equality and AY.
55. At h0, mixed G0/G1 indicators are explicitly tested and eliminated
    through actual containing rooks; zero attachments are not assumed.
56. A six-point cubic K3,3 is an abstract alternative, but violates the
    target mu2. A prism is promoted to a T rook only after checking its
    actual T-color matching and all induced edges.
57. Distinct actual rook vertex sets cannot be counted twice; conditional
    pair uniqueness supplies disjoint prism sets and the fourth-rook
    contradiction. No assertion that arbitrary pairs have rooks is used.
58. The contracted six-triangle Bs graph might have multiple edges.
    Connectedness instead uses actual component/color-matching parity;
    two cross matches are never asserted to force a third.
59. The h1 branch, its good attachments and arbitrary other adjacency
    remain. This necessary theorem neither constructs nor excludes either
    surviving branch, the one-d3 lane, R226 or a complete target graph.
60. Empty declared dependencies, raw pending nulls and the original
    candidate time are preserved. No earlier profile gate, shared outline,
    numerical search or later narrower result serves as this new gate.

There are42 written proof checks and18 written failure/scope challenges,
60 total; zero executed controls, formal checks, external checks, imports,
mathematical programs, workers, backend calls, censuses or enumerations.
Small file read/hash/metadata operations authenticate the exact documentary
packet only. No ledger/Git/index/protected/publication mutation occurred.
Root-reported467 is context, not a new protected-state observation. A new
Root exact-statement acceptance and any registration remain separate.
