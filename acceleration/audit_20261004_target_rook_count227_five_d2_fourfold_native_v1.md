# Independent written audit: b5 fourfold support with two outside points

Verification completed **2026-10-04T20:25:05.4030478Z** by Native
(`/root/native_driver`), method `independent_derivation`. Mathematical
producer Structural; no computational executor or worker.

## Exact source and result

Whole paper
`docs/CANDIDATE_20261004_TARGET_ROOK_COUNT227_FIVE_D2_FOURFOLD_SUPPORT_V1.md`,
SHA256 `3d711b5cda4b0b657aed1fcbf21214cfe5c44fef8ae95ae837c34ff731053bfc`,
and whole raw
`acceleration/results/20261004_target_rook_count227_five_d2_fourfold_support_candidate01.json`,
SHA256 `62b71f4a7d088cd68d138b54db320741294173647855a1adcecef3f0b6af3d4b`,
were independently reconstructed. Exact ID
`C-UNRESTRICTED-TARGET-ROOK-COUNT227-FIVE-D2-NO-FOURFOLD-TWO-OUTSIDE-POINTS` r1.

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once by their vertex sets, and put d_T=6-r_T for each actual
triangle. Suppose R=227, every d_T belongs to {0,1,2}, and exactly five actual
triangles have deficiency two. Let S be the vertices used by the deficiency-one
triangles. It is impossible that exactly one S vertex lies in four of those
triangles, every other S vertex lies in exactly two of them, and exactly two
outside-S vertices lie in deficiency-two triangles.

**PASS for this exact conditional k1/h2 branch.** Dependencies are empty;
selected multiplicities and the two outside points are explicit assumptions.
This excludes neither ordinary support/h2 nor b5 or R227 as a whole.
Root's full pointwise outline and Structural's reconstruction are disclosed.
Native's earlier narrower E56/leaf observation is comparison only: this
review does not approve that self-discovered result or use it as a premise.

## Fresh local geometry and the actual two-point fan

The fourteen neighbors of a vertex form a matching by lambda1, giving
seven triangles through each point and231 actual triangles. Triangles
are linear and cannot meet pairwise at three distinct points. Otherwise
their intersection triangle gives an edge a second triangle partner.
Intersecting triangle pairs determine at most one rook by their cross
pairs' fixed second common neighbors. The local graph of uncovered
pairs therefore has degree d_T at T, at every point of T.

Six triangles per rook give total deficiency24 at R227, hence fourteen
D1/five D2/P19. The distinct outer-partner fan injection gives
19>=3r1+5r2: no external actual triangle meets two outer fan points,
by linearity/no-loose-triple geometry. At each of the two outside points
p,q only D2 can be positive. Degree2 requires three roots and the fan
bound allows at most three. Their two3-subsets in five roots intersect
at least once, and at most once by linearity. The five roots are thus

    {p,q,u}, {p,x1,x2}, {p,x3,x4},
             {q,y1,y2}, {q,y3,y4},

with the displayed other points in S. Within each fan its five S neighbors
are distinct. The actual joining root makes p and q adjacent. Lambda1
makes u their sole common neighbor. Their other outside-neighbor subsets,
after removing each other, are therefore disjoint. No type mask or global
triangle-free defect-graph assumption supplies this fact.

## Weighted selected baseline and all internal edges

Let f be the unique selected fourfold point and w half selected incidence.
Then w_f=2, nineteen other S weights are1, and all outside weights0.
The42 selected incidences give |S|20, sumw21, normw23.
Selected triangles give42 distinct edges. At f, four selected roots give
eight distinct selected neighbors. The weighted selected edge sum is
42+8=50. Every other S point has four selected neighbors; the eight
neighbors of f have selected weighted neighbor sum5, the other eleven
sum4, and f itself sum8. Their total is92.

The four leaf D2 edges inside S are distinct from selected edges and
one another, with positive product at least1. Thus E_w=54+z, z>=0,
retaining every extra actual weighted edge. An induced selected support
is not assumed.

The complete target identities imply Q=3I-A+J/9 is PSD, Q^2=7Q,
Qj=0 and AQ=-4Q. Put Y=3Qw=9w-3Aw+7j. Then sumY0, AY=-4Y,
all Y coordinates are ordinary integers1mod3, and

    w^TQw=3*23+21^2/9-2E_w=118-2E_w=10-2z,
    ||Y||^2=63(10-2z)=630-126z.

No indicator-only support21 formula or rejected factor-nine formula is used.

## The peak's ordinary degree correction and integer increments

Let d=deg_S(f)-8>=0. Because all other support weights are1, the actual
weighted neighbor increment K_f equals d. At each S point let K_v>=0
be its weighted increment beyond the selected baseline. The baseline Y
is1 at f and its eight selected neighbors and4 at the other eleven points.
Thus Y_v=B_v-3K_v.

Every non-peak edge contributes2 to sum_S Aw, while a peak edge contributes
3 although twice its weighted product is4. Consequently

    sum_S Aw=2E_w-deg_S(f),
    sum_S K=2(E_w-50)-d=8+2z-d.

The distinction between ordinary peak degree and weighted edge product is
essential. At a baseline-one vertex, (1-3K)^2>=1+3K for integerK>=0;
at baseline4, (4-3K)^2>=16-15K. Apply the weaker-15K bound everywhere,
then restore18K_f=18d at f. The other eight baseline-one vertices can
only increase the lower bound. It follows that

    sum_S Y=53-3(8+2z-d)=29-6z+3d,
    ||Y_S||^2>=185-15(8+2z-d)+18d=65-30z+33d.

All actual edges are counted in these identities; no negative increments
or averaged profiles are permitted.

## Complete remaining77 residue budget

Write the weighted S-neighbor sums at p,q as5+a,5+b, with a,b>=0.
The five known neighbors have weight at least1. Extra peak weight and
every extra actual S neighbor are included in a,b. Hence Y_p=-8-3a,
Y_q=-8-3b. There are99-20-2=77 remaining outside coordinates, with

    sum=-13+6z-3d+3(a+b),
    norm<=437-96z-33d-48(a+b)-9(a^2+b^2).

For integer y1mod3, F(y)=y^2+y-2=9t(t+1)>=0. Their total Delta obeys

    Delta<=270-90z-36d-45(a+b)-9(a^2+b^2)<=270.

This expansion keeps every sign, the77-coordinate constant154, and all
nonnegative parameters z,d,a,b. No earlier edge/range claim is imported.

## Each disjoint fan requires144 residue excess

Every S Y is at most4. At each of the four leaf endpoints of a fan,
the D2 internal edge adds at least1 weighted increment beyond selected
edges and cannot duplicate a D1 edge. Thus its Y<=1. If such an endpoint
is f, its baseline1 only strengthens the inequality; if it is a selected
neighbor of f, that baseline1 also strengthens it. The shared endpoint
u is bounded by4 at any possible peak location.

Let alpha count additional ordinary S neighbors of p besides the five
known ones. Its weighted increment is a, so alpha<=a, not necessarily
equal. In fact alpha=a-1 if f is any S neighbor of p, otherwise alpha=a.
Its S-neighbor Y sum is<=8+4alpha. Equation AY=-4Y requires total
neighbor sum32+12a. After removing q with Y_q=-8-3b, the other outside
neighbors number m=8-alpha<=8 and have sum

    B>=32+12a-(8+4alpha)-(-8-3b)
      =32+12a-4alpha+3b>=32.

If m0 this positive required sum is impossible. Otherwise Cauchy gives

    Delta_p>=B^2/m+B-2m>=32^2/8+32-16=144.

The same holds for q, using its own ordinary extra-neighbor count. Both
subsets belong to the77 remaining outside vertices. They are disjoint
because u in S is already the unique common neighbor of adjacent p,q.
Thus Delta>=144+144=288>270, the exact branch contradiction.

## Twenty-four proof checks and eight hand challenges

The24 proof checks are: target triangle counts/linearity/no-loose triples;
rook uniqueness/local degree; D24/a14/P19; fan injection; each outside
point has three D2 roots; unique shared root/actual p-q edge; distinct
known endpoints/unique common neighbor; support20/weights21/norm23;
selected42/weighted50/eight peak neighbors; baseline5/4/8 and sum92;
E54+z with extras; target Q/eigenvector/scaling; ordinary peak d and K>=0;
sum_S Aw=2E-degS(f); sumK8+2z-d; baseline-one/four integer squares;
internal sum/norm; pair weighted degree and signs; exact remaining77;
complete Delta270 expansion; leaf/shared endpoint bounds at all peak
positions; ordinary alpha<=weighted a; pointwise Cauchy144/zero subset;
disjointness and final288>270 with exact scope.

Hand challenges:

1. A selected baseline graph has weighted E50, peak degree8 and total
   weighted neighbor92, giving sumK0. Dropping the peak correction fails.
2. A new non-peak edge adds2 to sumAw; a new peak edge adds3, product2
   to E and1 to peak degree. Both satisfy2E-degS(f) exactly.
3. All peak positions are retained: joining endpoint u, either fan's leaf,
   another known/extra S neighbor, or a point outside both fans. Peak
   membership makes alpha<a and never invalidates the endpoint bounds.
4. If f is a leaf endpoint, K_f>=1 and its D2 edge partner has the extra
   weight2; these only strengthen the conservative Y<=1 leaf bounds.
5. Eight abstract Y4 values attain sum32/norm128/excess144. A single
   subset does not violate270; two actual disjoint subsets are essential.
6. A zero remaining-neighbor subset is handled before Cauchy. Negative
   residue entries have nonnegative excess and are not assumed absent.
7. The fan subsets are disjoint by lambda1 on the actual p-q triangle,
   not by merely linear high-root incidence or an unqualified pair mask.
8. The old factor-nine outline and Native's narrower leaf/E56 discovery
   receive no gate transfer. The latter is not independently approved by
   its own author; this separate full Root/Structural argument stands alone.

This is32 written checks (24 proof,8 hand); executed/formal/external/
solver/scientific checks are all zero.

## Scope and saved provenance

The weighted necessary and ordinary h1 papers are comparison only. Correct
norm63q, strict ordinary/weighted distinctions and exact actual lambda1
are freshly derived from the target. Shared discovery and bounded archive
overlap are disclosed without novelty or completeness assertions. The
preserved scaling veto is an argument failure, not a REFUTED theorem.

Only selected small metadata reads/hashes and new written artifacts were
made. No mathematical program/import/AST/syntax/backend/worker/census/
solver, ledger parse, Git/index/publication operation or protected edit
occurred. Start/executor times remain null and exact Root acceptance is
null at creation. The explicit k1/h2 branch only is excluded, not k0/h2,
all b5, R227 or target existence. Separate Root review/nextWave47
registration remains pending outside closedWave46 cutoff449.
