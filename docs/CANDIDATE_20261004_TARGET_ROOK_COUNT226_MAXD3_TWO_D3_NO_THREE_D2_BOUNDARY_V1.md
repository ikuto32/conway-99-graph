# Candidate: the disjoint two-d3 lane at R226 cannot have three d2 roots

Root supplied the small-bad-point norm and two-fan cycle outlines.
Structural independently reconstructed the full actual-label bowtie,
opposite-cycle decomposition and weighted identity. The proposed middle
high bound fourteen is corrected to sixteen below; the contradiction is
still strict. This written CANDIDATE needs a different full challenge.
No mathematical program, enumeration, import, solver or worker ran.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T. Suppose R=226, every d_T is
in {0,1,2,3}, exactly two actual triangles have deficiency three, those
two triangles are disjoint, and b counts deficiency-two triangles. Then
b is not three.

These hypotheses are literal and no pending R226 result is promoted to a
premise. The logical dependency list is empty. No complete two-d3 or R226
exclusion follows from this statement alone.

Assume b3. Name the d3 roots A,B and the d2 roots X,Y,Z. There are eighteen
d1 roots, P23. At a point the local degrees are the deficiencies, r1+r3
is even, and the actual positive fan has 3r1+5r2+7r3<=23. At each of the
six A/B points there is one d3. A bad point means r1=1; degree three
then requires exactly two d2 roots, with the valid local(3,2,2,1) graph.
Every other A/B point has r1>=3. A third d2 at a bad point needs fan25,
so is impossible.

The fan bound follows by the actual outer-partner injection: an external
positive triangle meets only one outer point of the entire focal fan,
by linearity and the lambda1 prohibition on three actual triangles
meeting pairwise at distinct points. No equitability or automorphism is
assumed.

## The weighted proof rejects zero or one bad point

Select O=D1 union D3. Its point incidences are even by the local degree
sum; put w equal to half the incidence, zero off its support S. Here
s=|O|=20, sum w=30. Write K=sum w(w-1), and let ell be the sum of
(w_u-1)(w_v-1) over selected O edges. Let H be the weighted sum of every
actual internal S edge not belonging to O. All are nonnegative integers.
Unique actual triangle edges give

    E_selected=3s+4K+ell,
    0<=q=w^T(3I-A+J/9)w=70-5K-2ell-2H.       (1)

This expansion permits arbitrary larger selected incidence and all extra
edges. At each nonbad A/B point w>=2. With h bad points,
K>=2(6-h), and the two selected d3 triangles give
ell>=sum_i binom(3-h_i,2), where h_i counts their bad points.

At h0, K>=12 and ell>=6, so q<=-2. At h1, K>=10 and ell>=4. The used
d2 pair at the bad point cannot meet again at an outside point. Every
outside positive point would require all three d2 roots for local degree
two, including that already-intersecting pair. Thus there are no outside
d2 points, all three roots are wholly in S and H>=9. Equation (1) gives
q<=70-50-8-18=-6. Both cases are impossible.

## Exactly two bad points force the actual high bowtie

Three bad points are impossible. They would use the three d2 pairs. If
their three labels were distinct, X,Y,Z would be three actual triangles
pairwise meeting at distinct points, violating lambda1. Coincidence of
two pair labels forces all three d2 roots there, needing fan25 with its
d3. Hence h<=2.

At h2, the two used pairs share one d2 root, name them XY and YZ.
They belong to different A/B roots, because a common d2 root cannot meet
one actual d3 triangle at two points. Name their distinct points p on A,
q on B. All other high intersections are forbidden: X-B, Z-A or X-Z
would produce a distinct-intersection triangle with Y; coincidence at p
or q instead violates A/B disjointness or triangle linearity. Therefore
the actual high intersection/defect graph is exactly the two triangles
AXY at p and BYZ at q, sharing Y.

Its independent sets have size at most two. Consequently no d1 root can
have three high defect neighbors. A common low neighbor of an intersecting
high pair would itself need local degree at least two; no such low exists.

## Actual-square incidence and low bound

Let F be the global positive defect graph, its edges labeled by actual
intersection points. It has45 edges and the target has45 uncovered
squares. No collapsed F4 occurs: p,q have only three high roots, and
the preceding intersection argument leaves no other high intersection.
Four distinct F4 labels give their actual uncovered induced square, and
the inverse uses its four edge triangles. Thus C4(F)=45, incidence180.

F has no K3,3. A repeated grid label would put all six roots at one
point with local degree at least three, unavailable with only two d3
roots. Nine distinct labels give an actual induced rook, contradicting
the designated defects. All codegrees are at most three: disjoint actual
high triangles have at most three cross-matching completions; intersecting
highs have only their one third local high; any low has degree three.

Every low has a low neighbor because the high bowtie has no independent
triple. Six cycles through a low with a low neighbor force K3,3; hence
all eighteen lows contribute at most90 cycle incidences.

## The four leaf-high bounds retain every opposite node

A has high neighbors X,Y and seven low neighbors L_A, independent by
filled local low slots and the distinct-intersection prohibition. Each
L_A low can have at most one second high neighbor, either B or Z; these
two intersect at q. Let m count those second-high incidences, so the total
LL stubs from L_A are14-m. For each external high B or Z its common high
neighbor with A is Y, and its additional common lows n are at most two
by codegree three. Its cycle contribution binom(1+n,2)<=3n/2; these n
sum to m. An external low opposite has at most one X/Y neighbor because
X,Y intersect, and x LL neighbors in L_A. With I0/1 and x<=3-I,
binom(I+x,2)<=3x/2. Hence c_A<=3m/2+3(14-m)/2=21.

There is no internal opposite contribution: the neighbor graph has only
the XY edge, of internal maximum degree one. The same proof gives c_B<=21.
For X or Z, the analogous low pool has four nodes and LL stubs8-m; its
two external high opposites again have I1 and additional n<=2. The same
cancellation gives c_X,c_Z<=12. No high or low opposite is omitted.

## The common middle high needs a safe bound sixteen

Y has high neighbors A,X,B,Z and two independent low neighbors L_Y.
Those lows have only high Y and exactly two LL edges each, giving four
LL stubs. The internal neighbor graph consists of AX and BZ, a matching,
so contributes no internal opposite. All external opposites are low.

For such a low W let I count its neighbors in {A,X,B,Z} and x its LL
neighbors in L_Y. Here I<=2, and I2 must use one of AB,AZ,XB,XZ.
Each of those pairs already has high common neighbor Y, so codegree
three leaves at most two common lows. Thus at most eight opposite lows
have I2. For I0/1, binom(I+x,2)<=2x. For I2, x<=1 and
binom(2+x,2)=1+2x. Therefore

    c_Y<=8+2*4=16.                            (2)

The earlier outline's fourteen is not used: I2/x1 contributes three,
which exceeds 1+3x/2. No unsupported geometric veto removes that case.
All four LL stubs remain in the safe bound (2).

The complete incidence is at most

    90+2*21+2*12+16=172<180,

contradicting the required count. Thus h2 also fails; all possible h0..2
have been excluded and b3 is impossible under the stated hypotheses.

## Scope and review boundary

The positive local(3,2,2,1) graph and its actual high triangles are
retained. The cycle proof is only applied after excluding collapsed
four-label behavior by actual high intersections. The norm identity
uses all internal extra edges and arbitrary selected incidences. The
middle-high14-to16 correction is an explicit preserved outline boundary,
not a rewrite of an accepted proof.

Earlier fan, weighted Gram and cycle components overlap. The new exact
scope is the disjoint c2/b3 branch at R226/maxd3; no novelty, archive
absence, realization or broader exclusion is claimed. A different author
must challenge this full paper before any VERIFIED/ledger use. No
publication or protected-state mutation occurs.
