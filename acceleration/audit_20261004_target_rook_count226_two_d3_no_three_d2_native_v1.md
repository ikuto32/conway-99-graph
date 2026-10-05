# Independent written review: the disjoint R226/maxd3 c2/b3 branch fails

Completed verification2026-10-04T21:49:39.7424049+00:00.
Structural producer; /root/native_driver distinct written verifier. No
mathematical program/import/AST/worker/census/backend/solver. New metadata
time and Root acceptance are separate; historical evidence unchanged.

Whole paper MAXD3_TWO_D3_NO_THREE_D2_BOUNDARY_V1 has SHA
504d0387a68375519cd3b6415dc974a76dc83d19791d88657bf2c9edf42c1420;
rawcandidate01 SHA2d36c30a63fd54c2b22d5b43edbb523757013e1479e94a0eb136dfc57f959ae1.
Exact ID C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-TWO-D3-NO-THREE-D2-BOUNDARY r1.
Literal assumptions are target/R226/maxd3 and exactly two disjoint D3;
the conclusion is only b!=3. Empty logical dependencies are correct.
No pending c2 necessity/intersection/population gate is inherited.

## Actual foundation and weighted h0/h1 branches

Assume b3, name disjoint D3 A,B and D2 X,Y,Z. D30 gives18 D1/P23.
Actual local degrees, r1+r3 parity and fan3r1+5r2+7r3<=23 follow from
triangle edge uniqueness/linearity/no three distinct intersections and
the outer-partner injection. At any A/B point, exactly one D3 occurs;
a bad point r1=1 needs exactly two D2, giving the valid(3,2,2,1) graph.
A third D2 costs25 and fails. Nonbad points have r1>=3.

Select O=D1 union D3, s20. Local degree sum makes O incidences even, with
integer w=half incidence, sum30; larger even incidences remain allowed.
K=sum w(w-1), ell=sum_O_edges(w_u-1)(w_v-1), H=weighted sum of all
other internal support edges are nonnegative. Selected degree4w and
unique actual triangle edges give E_O=3s+4K+ell and norm=3s/2+K.
The target Q=3I-A+J/9 PSD then gives q=70-5K-2ell-2H>=0 exactly.
At six A/B points with h bad, K>=2(6-h). Each central triangle adds at
least binom(3-h_i,2) to ell from its pairs of nonbad points.

h0 gives K12/ell6/q<=-2. h1 gives K10/ell4. Its used D2 pair meets
at the bad point. Any support-external positive point has only D2 roots,
and degree2 needs all three D2 there; this repeats the used pair and is
impossible. Thus all D2 are wholly in the selected support and provide
nine distinct extra actual edges, H>=9. q<=70-50-8-18=-6. No edges are
assumed absent; larger w/ell/H only strengthen these contradictions.

## Complete h2 actual-label bowtie

Three bad points would use all three D2 pairs. Distinct labels are the
forbidden loose triple X/Y/Z. Coinciding pair labels bring all3D2 with
their D3 to one point/fan25. Thus h<=2. At h2, pair names XY and YZ
share Y. Their points cannot lie on the same D3, since Y would meet it
twice. Name p on A and q on B. The actual high graph is exactly triangles
AXY at p and BYZ at q. A/B disjointness, linearity and loose-triple veto
forbid X-B,Z-A,X-Z: a new distinct label is a loose triple; coincidence
at p/q violates actual disjointness or repeats a high pair. No additional
high intersection or covered high edge is silently discarded.

This bowtie has independence number2. A low cannot be a common defect
neighbor of intersecting highs: it would need local degree2. Hence each
low has at most2 independent high neighbors and at least one low neighbor.
Root low-neighbor pools are independent by filled local slots/no loose
triple. F high degrees9,9,6,6,6, low degree3. D30 gives45edges.

Target45 uncovered squares inject into F4. Conversely every F4 either
has four distinct actual labels or is entirely collapsed; no collapsed
one is possible because each high intersection has only three high roots.
Thus45cycles/180incidences. Repeated-label K3,3 forces six local degree>=3
roots but only two exist; distinct grid labels give a forbidden actual
rook. Codegrees<=3 follow from actual disjoint crossmatching/intersecting
common-point locality/low degree3. A low with a low neighbor has<=5cycles,
since equality6 gives K3,3. All18 lows contribute<=90.

## All leaf opposite pools, then the safe middle bound

A has N={X,Y}+7independent lows L_A, with only internal edgeXY. No
internal opposite has two neighbor edges. Each L_A node can have at most
one additional high, B or Z (they meet at q); other high choices meet A
and cannot share a low defect partner. Let m count these second highs.
The LL stub count is14-m. External highs B/Z have one common highY plus
n common lows, n<=2 by codegree3. Their contributions binom(1+n,2)
are<=3n/2, with total n=m. External lows have at most one X/Y neighbor
I0/1 and x L_A neighbors, x<=3-I, giving binom(I+x,2)<=3x/2. Every LL
stub reaches this external low pool, because L_A has no internal edges.
Thus c_A<=3m/2+3(14-m)/2=21. The same proof gives c_B<=21.

For X, N={A,Y}+4lows; analogous second-high choices B/Z intersect atq,
and each external high has common highY. The same complete cancellation
with8-m LLstubs gives c_X<=12, c_Z<=12. High and low external opposites
are separately included here; this is unlike the vetoed b2 V1 omission.

Y has all other4highs and2independent lows L_Y as neighbors. Each L_Y
can have no other high (Y intersects all others), so its two LL edges
give4stubs. Its internal neighbor graph is matching AX/BZ, maximumdegree1,
so no internal opposite. All external opposites are LOW, because all
other highs are already in N(Y). With I high neighbors and x L_Y neighbors,
I<=2. I2 must be one of AB,AZ,XB,XZ, each already sharing highY; codegree3
leaves at most2 common lows per pair, so at most8 I2 opposites. For I0/1,
binom(I+x,2)<=2x. For I2, x<=1 and contribution=1+2x. Therefore
c_Y<=8+2*4=16. This retains every allowed I2/x1 opposite.

Full incidence<=90+21+21+12+12+16=172<180. All h0/1/2 branches fail,
proving b!=3 under the stated conditional hypotheses.

## Falsification and accounting

Thirty-two proof topics: actual triangle/rook deficiency foundations; D30;
a18/P23; local parity; exact fan injection; valid bad profile; no third D2;
selected even family; arbitrary integral w; selected degree4w; edge expansion;
exact quadratic; K lower bound; ell central edge count; h0 negative; h1 used
pair; outside concurrence requirement; h1 H9; h<=2; different A/B bad roots;
all high nonintersections; actual bowtie; high independence2; no commonlow
for intersecting highs; square/collapse scope; K3,3 labels; codegree3;
low90; leaf D3 complete pools; leaf D2 complete pools; middle I2 cap8;
safe16/full172. Twelve failure boundaries: parityD1alone; valid high triangle;
larger selected incidences; H includes arbitrary extraedges; h3 distinct vs
coincident labels; high meeting vs F adjacency; low pools independent;
external high opposites fully included; LL stubs can share opposite nodes;
I2/x1 exact3 not2.5; no unidentified internal opposite; no silent disjointness
or maxd3 inference. These44 checks and three hand h rows are written only.

The rejected middle-high14 outline is explicitly wrong at I2/x1:
binom(3,2)=3>1+3/2. Replacing the coefficient3/2 by2 at the middle root
gives the safe16; there is no extra geometric veto of that permitted case.
This is preserved discovery/correction history, not REFUTED theorem or old
gate transfer. Root shared outlines, Structural reconstructed/corrected,
Native separately derived the whole proof. Prior fan/Gram/cycle overlap is
disclosed, not novelty. Only disjoint c2/b3 is excluded. No full c2/R226/
target exclusion, realization, equitable profile, automorphism, codeword or
archive-absence claim. No ledger parse/protected/Git/index/publication
mutation. Root-reported457 is context only; Root exact acceptance separate.
