# Independent written review: disjoint D3 roots exclude b4 through b6

Completed written verification: 2026-10-04T22:01:57.9291347+00:00.
Producer: /root/structural. Different author verifier: /root/native_driver.
Method: independent_derivation. Computational executor: null. Outcome: PASS.
Claim C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-TWO-D3-NO-FOUR-THROUGH-SIX-D2-BOUNDARY r1.
Paper docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD3_TWO_D3_NO_FOUR_THROUGH_SIX_D2_V1.md
SHA256 b1431c80962d0a8b65dd12d9fdf5f2a2ad057261954d38757b735cff48b5861d.
Raw acceleration/results/20261004_target_rook_count226_maxd3_two_d3_no_four_through_six_d2_candidate01.json
SHA256 da7620d4e2d7f1eaf028accb60335fead8cfc7dfd8982e53706ae63f7c6b4b4c.
The exact literal statement, assumptions, empty dependencies and producer-time
pending nulls are retained by the bound report. This is a whole new derivation.

## Actual target geometry and weighted identity

For a complete finite simple SRG(99,14,1,2), each edge has one triangle partner;
there are231 actual triangles. Distinct actual triangles meet at most once.
Three pairwise intersections at distinct points would give a second triangle
partner on an edge and are impossible. Seven triangles pass through each point.
The rook-partner bijection makes the local positive defect degrees d_T, and
the global deficiency sum is6(231-R)=30 at R226. Thus with two D3 roots A,B,
a=24-2b and P=26-b. Disjointness is a hypothesis, not a deduction here.

At a point the simple local degree graph gives r1+r3 even. Injecting the two
outer partner sets of every local positive root gives3r1+5r2+7r3<=P: a repeated
external triangle would violate linearity or the actual loose-triple prohibition.
For b4..6, P<=22. On A/B, a bad point has r1=1. Degree three needs at least
two D2 roots, while three D2 roots give fan25>P. Hence its exact positive
profile is(3,2,2,1), a valid high triangle plus its D1 leaf. At every other
point on A/B, r1>=3 by parity and the degree-three requirement.

The adjacency identity is A_target^2=12I-A_target+2J. Therefore
Q=3I-A_target+J/9 obeys Q^2=7Q and is positive semidefinite: for every real w,
7w^TQw=||Qw||^2. These facts use only the full target hypotheses.
Select O=D1 union D3 and S its actual point support. Its incidences are even,
so w is half their incidence, an integer supported on S. Write s=|O|=26-2b,
K=sum w(w-1), ell=sum over selected triangle edges of(w_u-1)(w_v-1), and
H for the weighted sum of all other actual internal support edges. These are
nonnegative integers, with arbitrary larger even incidence retained.

Since each selected point belongs to2w triangles, expansion of each triangle
edge's w_u*w_v gives E_selected=3s+4K+ell. Indeed the constant terms give3s;
the linear terms at each point are4w(w-1); the quadratic terms are ell.
Also sum w=3s/2 and ||w||^2=3s/2+K. Substitution in w^TQw gives the exact
identity q=s(s-6)/4-5K-2ell-2H>=0. No selected inducedness is assumed.

## Independent actual-label bad-component derivation

Put a simple edge between the two actual D2 roots at each bad point; color it
A or B. Linearity makes the graph J simple. Each color is a matching because
a D2 triangle meets A or B at most once and each bad point has exactly two
D2 roots. Thus max degree is2 and edges alternate colors.

An A-B-A three-edge path X1-X2-X3-X4 would have actual labels p,q,r on A,B,A.
p and r are distinct: equality would make X2,X3 share that point and q.
q differs from both because A,B are disjoint. Then A,X2,X3 meet pairwise at
p,r,q, which is the forbidden loose actual triple. The B-A-B orientation
has the same actual contradiction. Every longer path and every proper
alternating cycle contains a three-edge path; odd cycles cannot be properly
two-edge-colored. Therefore the full components are singleton, K2 or P3.
P3 itself is retained and not confused with the forbidden three-edge path.
This implies h=|E(J)|<=floor(2b/3), namely2,3,4 for b4,5,6.

For the chosen support S, an outside point contains no D1/D3 selected root.
Its positive local roots are therefore D2 and require a simple degree-two graph
on at least three vertices. Two roots in the same K2 component already meet at
its label in S. For endpoints X,Z of a P3 X-Y-Z, an intersection away from the
two distinct labels produces a loose triple X,Y,Z, and an intersection at either
label makes two roots share twice. Thus at an outside point there is at most
one D2 from each component. Two components cannot supply the required three.

J has b-h components. At maximal h in these ranges there are exactly two:
b4/h2 has two K2 or P3+singleton, b5/h3 has P3+K2, b6/h4 has two P3.
Only in these rows are all D2 triangles proved wholly in S. Their distinct
actual triangle edges are different from the O edges and have positive integer
endpoint weights. They force H>=3b. All further actual edges remain in H.

## Complete seven-row check, reconstructed independently

There are six distinct points on A,B. At each nonbad point selected incidence
is at least four, so its contribution to K is at least2. Hence K>=2(6-h).
If h_A,h_B divide h between the two roots, their selected triangle edges give
ell>=choose(3-h_A,2)+choose(3-h_B,2). This is6 at h0,4 at h1, at least2 for
h<=2, at least1 for h3, and safely0 for h4. All these are lower bounds; extra
selected incidence or support edges can only strengthen the contradiction.

| b | bad count | constant s(s-6)/4 | K lower | ell lower | H lower | q upper |
|---:|---|---:|---:|---:|---:|---:|
|4|0|54|12|6|0|-18|
|4|1|54|10|4|0|-4|
|4|2|54|8|2|12|-14|
|5|0..2|40|8|2|0|-4|
|5|3|40|6|1|15|-22|
|6|0..3|28|6|0|0|-2|
|6|4|28|4|0|18|-28|

Each row is strictly negative, contradicting q>=0. This excludes precisely
b4/b5/b6 under the stated R226/maxd3/disjoint-c2 assumptions.

## Independent checks and failure boundaries

Thirty proof checks on paper:
1. Unique triangles231; 2. linearity; 3. actual loose-triple veto;
4. seven local triangles; 5. local defect degrees; 6. mass30;
7. a24-2b/P26-b; 8. local parity; 9. fan injection; 10. bad r1=1;
11. exact two-D2 bad profile; 12. nonbad r1>=3; 13. simple J;
14. each color matching; 15. distinct p/q/r path labels;
16. actual A-X2-X3 contradiction; 17. all cycle/path components;
18. h bounds2/3/4; 19. retained P3; 20. P3 endpoints disjoint;
21. outside degree-two needs three roots; 22. two-component maximal cases;
23. H>=3b only there; 24. Q^2=7Q and PSD; 25. even selected incidence;
26. integer K/ell/H; 27. E_selected identity; 28. exact q identity;
29. six-point K and central ell bounds; 30. all seven negative rows.

Ten failure/boundary challenges on paper:
1. An abstract colored P4 is possible but these actual labels are impossible.
2. A properly colored C4 is rejected through a contained actual P4, not a
   false generic assertion about even-incidence systems.
3. A two-edge P3 remains valid and its endpoints must be disjoint.
4. Outside selected support is not excluded in nonmaximal-h rows.
5. A covered actual intersection still enforces linearity of bad components.
6. Selected incidence six or higher remains in K and ell.
7. Additional actual support edges remain in H rather than being deleted.
8. H>=3b requires wholly-S D2 triangles and distinct actual triangle edges.
9. A nonnegative or zero q row would not suffice; all seven here are negative.
10. No intersecting c2, full c2, R226 or target exclusion is asserted.

Total40 written checks; all executed/formal/external/solver counts zero.

## Scope and provenance

Structural authored the full candidate; Root and Structural shared the
actual-label component outline. Native independently reconstructed the whole
argument and seven exact rows. Agreement is not verification and no independent
discovery or novelty is claimed. Logical dependencies are empty; no pending
upper3, population or intersecting-branch gate is used. All old bytes and producer
pending nulls remain unchanged. Verification time is separate from metadata
creation. Scientific coverage UNKNOWN; target resolution NONE. No program,
import/AST/backend/worker/census, ledger parsing, Git/index/publication/protected
mutation occurred. Root-reported457 is context only.
