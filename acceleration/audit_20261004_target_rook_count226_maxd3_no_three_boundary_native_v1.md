# Independent written review: the R226/maxd3 c3 boundary fails

Completed verification 2026-10-04T21:40:23.9735048+00:00.
Producer /root/structural; distinct written verifier /root/native_driver.
No mathematical program, import, AST, census, backend, solver or worker ran.
All candidate/rejected-outline/earlier proof bytes are preserved. Sealing
time and any Root acceptance are distinct from this completed derivation.

## Literal object and self-contained scope

I whole-read
docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD3_NO_THREE_D3_BOUNDARY_V1.md,
SHA27686ffa7e5d775bdef8bf24ad33a40c18a21c656f88dd2777debc6c7d4be5f8,
and rawcandidate01 SHA
220f3640a089436dcf41caf2fce7297efef24f72d5053fc99e88b1ae68b5cfb8.
Exact r1 ID C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-NO-THREE-D3-BOUNDARY.
Its literal assumptions are complete finite simple target, actual R226 and
all actual deficiencies0..3; it concludes only c is not3. Empty dependencies
are correct: I reconstruct all needed fan, pair and Gram arguments here.
The separately sealed upper3 and population-upper3 statements are not premises.

Every target edge has one triangle partner; there are231 triangles; actual
triangles are linear and have no three distinct pairwise intersections.
Covered intersecting pairs have unique rook completions, so local defect
degree is d_T and D=6(231-R)=30. With c3, a=21-2b, P=24-b and integer
b lies0..10. Local parity r1+r3 even and actual fan3r1+5r2+7r3<=P follow
by counting focal roots and their two outer sets of defect partners. An
external triangle cannot hit two fan outerpoints by linearity/lambda1.

## Reconstruct actual disjoint roots and exceptional-point capacity

Two local D3 with r1=0 require at least two D2/fan24 but b>=2 givesP<=22.
At r1=2/r2=0, (3,3,1,1) is nongraphical; any D2 raises fan to25; r1>=4
costs26. Three D3 require odd r1: minimum(3,3,3,1) is nongraphical and
any additional node costs at least29. Thus the three actual D3 triangles
are pairwise disjoint; S3 has nine distinct actual points.

At each of these points r1 is odd. A bad point has r1=1 and requires two
D2/fan20; three D2 cost25>P. Every other point has r1>=3. Hence
h=0 at b0/1; h<=1 at b2; h<=3 at b3; h<=6 at b4; h=0 at b>=5
because P<=19. At b2/3/4 every bad point contains a D2 pair, and one
pair cannot meet at two points. The valid(3,2,2,1) pattern is not rejected.

Let t_L count S3 points in each D1 triangle. Then sum t>=27-2h.
Disjoint D3 triangles have a cross-edge matching of size<=3 by lambda1;
each cross edge has its unique completion. Therefore sum binom(t,2)<=9
over all D1, one contribution per pair of distinct central roots. A D1
cannot have two points of the same central root. Since binom(t,2)>=t-1
also at t0, a>=18-2h. Arbitrary t multiplicities, including0/3, remain.

## Exact weighted identity permits every larger even incidence

Select O=D1 union D3, s=a+3=24-2b. Local degree sum makes its incidence
m_v even at every point. Set w_v=m_v/2 on S,0 outside. It is integral;
sum w=3s/2. No upper incidence2/4 bound is assumed. Define
K=sum w(w-1), ell=sum_selected_edges(w_u-1)(w_v-1), and H=sum_other
internal_S_edges w_u*w_v. All are nonnegative integers. Unique actual
triangle partners make all3s selected edges distinct. Their selected degree
at v is2m_v=4w_v. Expanding the weighted edge product gives exactly
E_selected=3s+4K+ell, while squared norm=3s/2+K.

Independently deriving Q=3I-A+J/9 PSD from A²=12I-A+2J/Aj14j yields
q=wQw=3(3s/2+K)-2(3s+4K+ell+H)+(3s/2)²/9
=s(s-6)/4-5K-2ell-2H>=0.
The coefficient of K is-5, not a guessed projector scale. All other target
edges stay in H, so selected inducedness is not a hidden premise.
At each nonbad S3 point, m>=4/w>=2, so K>=2(9-h). Higher even incidences
only strengthen this bound; they cannot invalidate the identity.

## Every integer b is excluded

At b0, s24/h0 implies K>=18. Nine central D3 edges have both endpoint
weights>=2, contributing at least9 to ell. D1 edges joining two S3 points
add at least sum binom(t,2)>=sum t-a>=27-21=6. These edges are distinct
from the central ones by lambda1. Hence ell>=15 and q<=108-90-30=-12.
This is a strict edge argument, not a speculative equality realization.

For b1, s22/constant88/h0/K18 gives q<=-2. For b2,
s20/constant70/h<=1/K>=16 gives q<=-10. For b3,
s18/constant54/h<=3/K>=12 gives q<=-6. Nonnegative ell,H and larger
incidences cannot rescue any case.

For b5..10, P<=19 forbids bad points. The pair moment forces a>=18,
but a=21-2b<=11. This includes b10/a1, not merely a small-b sample.

At b4, a13/s16/P20. Pair moment gives13>=18-2h, so h>=3, while h<=6.
Thus K>=6. Outside S there is no odd-deficiency triangle. A positive
local root is D2 and needs at least three D2 nodes for degree2. At an
outside four-root point every D2 pair is already intersecting there, so
no bad S3 point can contain any D2 pair; h would be0, contradiction.
Therefore any outside positive point contains exactly three D2. At mostone
exists: two triples from four roots share a pair, which would meet twice.

If no outside point occurs, every D2 is wholly-S and contributes its full
three edges. If one occurs, three roots have at least two S points (one
internal edge each); the fourth is wholly-S (three edges). In either case
there are at least6 distinct actual internal edges outside O. Their weights
are>=1 and none can coincide with an O edge, so H>=6. Consequently
q<=40-5*6-2*6=-2. No outside concurrence or extra internal edge is removed
without proof; no incidence cap elsewhere in S is used.

The complete table is b0/-12, b1/-2, b2/-10, b3/-6, b4/-2, and
b5..10/a>=18 against a<=11. Thus exactly c3 fails, at the literal maxd3
and actual R226 only. This proof uses no faithful F4 census, so arbitrary
collapsed cycles at other populations need not be guessed absent.

## Written checklist, failed shortcuts and limits

Thirty-four proof checks: actual triangle count; unique edge partners;
linearity; no loose triple; rook-pair/local-degree definition; D30; a formula;
P formula; all b domain; local parity; actual fan; two-D3 disjointness cases;
three-D3 minimum failure; bad point fan; exactly two D2 at a bad point;
all five h regimes; D2-pair linearity; all t including0/3; actual crossmatching;
pair moment9; a lower bound; selected even family; integral unrestricted w;
sum weights; selected degrees4w; exact edge expansion; exact squared norm;
independent PSD; full quadratic identity; K at central points; strict b0 ell;
negative b1..3; complete b>=5; b4 outside count and H6 contradiction.

Twelve written failure/boundary challenges: D1-alone parity fails at the valid
bad pattern; nongraphical minima do not veto the valid bad pattern; abstract
linear triples alone do not imply the actual matching cap; t0 contributes
validly; selected incidences6 or more remain allowed; edge products include
both linear terms exactly once; ell does not double-count central/low edges;
q depends on all actual extra edges through H; the b0 tentative equality
argument is unnecessary; h>=3 is proved before outside fourfold exclusion;
two outside triples share a repeated actual pair; maxd3/population-upper3
gates cannot be silently inherited. None falsified the literal statement.
These46 checks and eleven integer b cases are hand-written, not a census.

The producer's disclosed rejected shortcut asserting only selected incidences
two/four is not adopted; no old outline is a verification gate or REFUTED
unrelated theorem. Root shared discovery and Structural independently refined
the strict ell bound; Native independently reconstructed the complete new
proof. Prior fan/matching/Gram overlap is disclosed, not novelty.
PASS for c!=3 only. This record does not itself supply c<=3, maxd3, R226
or target exclusion, realization, equity, automorphism or codeword existence.
Original pending/null/scope fields remain preserved. No ledger parse,
protected/Git/index/publication mutation or mathematical execution occurred.
Root-reported457 is metadata context only. Root acceptance and any registry
action remain separate.
