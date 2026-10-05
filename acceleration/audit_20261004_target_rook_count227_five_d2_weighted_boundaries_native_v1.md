# Independent written audit: b5 weighted necessary boundaries at R227

Verification completed: **2026-10-04T20:14:52.2756669Z**.
Reviewer Native (`/root/native_driver`); mathematical producer Structural.
Method `independent_derivation`, with no computational executor or worker.

## Frozen statement and exact result

Whole source reviewed:
`docs/CANDIDATE_20261004_TARGET_ROOK_COUNT227_FIVE_D2_WEIGHTED_SUPPORT_BOUNDARIES_V1.md`,
SHA256 `72b1b152a9551efb31e7ff98e9c06ae49587a031dbb6d226b64e5b5d7dd5cbee`;
raw candidate
`acceleration/results/20261004_target_rook_count227_five_d2_weighted_support_boundaries_candidate01.json`,
SHA256 `eacf26e07eb2d0a77dc3f4c7b69f37ad277aaf0a1140f001df5930248bfe6e0b`.
Exact identity:
`C-UNRESTRICTED-TARGET-ROOK-COUNT227-FIVE-D2-WEIGHTED-SUPPORT-BOUNDARIES` r1.

For every complete finite simple SRG(99,14,1,2), count actual induced
nine-vertex rook subsets once by vertex sets and let d_T=6-r_T. Suppose
R=227, every d_T is0,1 or2, and exactly five triangles have deficiency2.
There are fourteen deficiency1 triangles. Let S be their support, k their
fourfold-incidence point count, h the number of outside-S points on
deficiency2 triangles, w half the deficiency1 point incidence and E_w
the actual weighted edge sum. Selected multiplicities are2 or4. Exactly
one necessary case occurs: k0/h1 with |S|21,e(S)51 or52 and its outside
point S-degree6..8 or6..7 respectively; k0/h2 with |S|21,e(S)46..53 and
shared-one-root triple fans; or k1/h2 with |S|20,shared-one-root triple
fans,w2 at its unique fourfold point and E_w54,55 or56. In the last case,
if the fourfold point is the joining root's only S point, E_w54 or55.
No surviving case is asserted realizable and this does not exclude b5 or R227.

**PASS for this frozen necessary-condition statement.** All cases and
literal ranges are independently reconstructed below. Logical dependencies
are empty. The target/maxd2/b5 assumptions remain explicit. Root suggested
the weighted support; Structural authored the exact refinements. Shared
discovery and their agreement do not constitute this verification.

This audit does not adopt subsequent stronger neighbor-sum outlines as
premises or silently strengthen the frozen statement. Any new obstruction
or Native-discovered refinement needs a separately bound proof and a
different-author challenge. The current claim asserts necessary boundaries,
not feasibility of any listed boundary.

## Reconstructed target geometry and weighted selection

Lambda1 makes the induced neighborhood of each vertex a matching on14
points, hence seven actual triangles through each point and231 overall.
Triangles are linear. Three actual triangles cannot have three distinct
pair intersections, since those points themselves make a triangle and
give an edge a second triangle partner.

Two triangles through a point determine at most one rook: each of their
four nonadjacent outer cross pairs has the point and one fixed second
common neighbor, fixing all nine possible rook vertices. A rook through
triangle T supplies at each point of T one distinct covered triangle
partner. Therefore the local graph of uncovered pairs has degree d_T
at T. Its handshake gives even D1 incidence at each point. A D0 triangle
cannot serve as a defect partner.

Each induced rook has six actual row/column triangles, so total deficiency
is6(231-R)=24. The assumed five D2 leave fourteen D1 and P=19 positive
triangles. At a point with r1 D1 and r2 D2 roots, their outer points are
distinct. Each root of deficiency m needs m external positive partners
at each of its two outer points. An external actual triangle cannot meet
two outer fan points: same-root repetition violates linearity and
different-root repetition violates the no-loose-triple geometry. This
injection yields19>=3r1+5r2.

The selected fourteen D1 family has a separate injection. At a point
with selected incidence r, each of its2r outer points needs another
selected triangle to repair parity. Each external selected triangle
can cover at most one, giving14>=3r. Thus used multiplicities are2 or4.
There are42 selected incidences. If k points have multiplicity4, the
support has21-k points, weights are1 on21-2k points and2 on k points,
and

    sum w=21,  sum w^2=21+2k.

Selected triangles supply42 distinct ordinary actual edges, with
arbitrary other target edges on S still retained.

## Complete five-D2 outside-point table

Outside S there are no D1. A D2 local degree2 needs at least three
positive roots, while19>=5r2 gives at most three. Each outside point
on D2 is exactly a triple concurrence. Fix one with three base roots;
two external roots remain. Another triple point uses at most one base
root by linearity. It cannot be detached, since there are only two
external roots. It must use both external roots; there cannot be two
such additional points because those two roots would meet twice.
Consequently h<=2. For five roots this last bound can already be
obtained from linearity; the actual no-loose-triple property is still
needed for the preceding fan injections.

Two distinct triple points have at most one common root. Since their
two3-subsets lie in a five-root set, they have at least one. Thus h2
shares exactly one root and uses all five roots. The full table is

| h | Outside-point counts t_i | D2 ordinary internal edges H |
|---|---|---:|
| 0 | 0,0,0,0,0 | 15 |
| 1 | 1,1,1,0,0 | 9 |
| 2 | 2,1,1,1,1 | 4 |

Each entry comes from sum C(3-t_i,2); these edges are distinct from
the42 selected ones by lambda1. In h2 the joining root has p,q and
one S point; the other two roots at each outside point have two S
points each. This supplies five distinct S neighbors at each, not six.

## Weighted edge identity and the strictly positive Gram

From A^2+A=12I+2J and Aj=14j, the real symmetric target A has roots
3 and-4 on j-perp. Hence Q=3I-A+J/9 is PSD, Qj=0 and Q^2=7Q.
For q=w^TQw,

    q=3(21+2k)+21^2/9-2E_w=112+6k-2E_w.

An edge with weights1/2 has product1 plus one per fourfold endpoint,
and one additional if both are fourfold. Every fourfold point belongs
to four selected triangles and has eight distinct selected incident
edges. If l counts selected edges with two fourfold endpoints, the
selected weighted edge sum is exactly42+8k+l. The distinct D2 internal
edges each have weight product at least1. All other edges are included
in E_w with nonnegative product. Thus

    q <= 28-10k-2l-2H.

The quadratic form is strictly positive. If q0, PSD gives Qw=0, but
each coordinate is3w_v-(Aw)_v+7/3, an integer plus7/3, so none can
vanish. This is the full ordinary integer boundary, not a fractional
Gram construction. For k>=2 even H4 makes the upper bound<=0; k1/h0
or h1 also fails; k0/h0 gives-2. Exactly the possible pairs k0/h1,
k0/h2 and k1/h2 remain. The weight2 point is retained in the last pair.

## Correct integral scaling and every h2 edge range

Set Y=3Qw, not an unscaled indicator surrogate. Then

    Y=9w-3Aw+7j,  sumY=0,  ||Y||^2=63q,
    every coordinate Y is1 modulo3.

For y=1+3z with integer z,

    y^2+y-2=9z(z+1)>=0.

Summing yields norm>=198. The excess at-8 is64-8-2=54, and at-11
is121-11-2=108; it increases for more negative entries in that residue
class. At h2 the two outside weighted neighbor sums are at least5,
so their Y entries are<=-8 and norm>=198+54+54=306.

For k0, w is the actual indicator and E_w=e(S). H4 supplies e>=46,
while norm=126(56-e)>=306 implies e<=53. For k1, the edge bound gives
q<=10, q is a positive even integer, and63q>=306 gives q>=6. Thus
q=6,8,10, or E_w=(118-q)/2=56,55,54. If the weight2 point is the
joining root's only S point, it neighbors both outside points and their
weighted sums are>=6. Each Y is then<=-11, giving norm>=414 and
the even lower q>=8, hence E_w54/55. No other fourfold location is
assumed in the frozen statement.

## Complete k0/h1 edge/neighbor refinement

Here the support has21 unit-weight points. Three D2 share the outside
point p and the other two D2 are wholly in S. Their ordinary internal
edges total9, so write e=51+z with nonnegative integer z. Each S point
has four distinct selected neighbors. With K_v=deg_S(v)-4>=0,

    sum_S K=18+2z,  Y_v=4-3K_v.

Two wholly-S D2 roots force sum K(K-1)>=12: if disjoint, their six
points each have K>=2. If they share one point, its K>=4 and the other
four points K>=2 give12+8=20 instead. Their edges are distinct by
lambda1. Extra target edges never reduce these increments. Therefore

    sum_S K^2>=30+2z,
    ||Y_S||^2>=336-24(18+2z)+9(30+2z)=174-30z,
    sum_S Y=84-3(18+2z)=30-6z.

At p the three roots give six distinct S neighbors. Write deg_S(p)=6+a
with a>=0, so Y_p=-11-3a. There are78 outside points and77 excluding p.
Their sum is-19+6z+3a. Applying y^2>=2-y to these77 entries gives
their norm>=173-6z-3a. Adding p and the S lower norm yields

    ||Y||^2>=468-36z+63a+9a^2.

Its exact value is630-126z, giving the necessary inequality

    162-90z-63a-9a^2>=0.

For z>=2 it is negative already at a0. The complete surviving integer
table is

| z | a | Margin | e(S) | deg_S(p) |
|---|---|---:|---:|---:|
| 0 | 0 | 162 | 51 | 6 |
| 0 | 1 | 90 | 51 | 7 |
| 0 | 2 | 0 | 51 | 8 |
| 1 | 0 | 72 | 52 | 6 |
| 1 | 1 | 0 | 52 | 7 |

These are exactly the candidate's e51/52 and degree6..8/6..7 ranges.
Zero margins remain necessary boundaries and are not asserted realizable.

## Written controls and scope falsification

The32 proof checks cover: (1) seven vertex triangles; (2) total231;
(3) local defect degree/rook uniqueness; (4) D1 parity; (5) D24/a14/P19;
(6) positive fan; (7) selected fourteen fan; (8) weights/support/norm;
(9) outside degree-three concurrence; (10) h<=2; (11) complete h table;
(12) h2 shared root/five neighbors; (13) A/Q identities; (14) q formula;
(15) weighted selected42+8k+l; (16) distinct D2 lower H;
(17) strict q; (18) only three k/h pairs; (19) Y scaling/residue;
(20) norm floor198; (21) -8/-11 excess54/108;
(22) k0/h2 range46..53; (23) k1/h2 q6/8/10 and E54/55/56;
(24) joining weight2 refinement; (25) k0/h1 baseline e51+z;
(26) internal increment sum/Y; (27) wholly-S roots excess12/20;
(28) S norm174-30z/sum30-6z; (29) p degree/exact77 coordinates;
(30) remaining residue norm/total468 bound;
(31) necessary inequality162-90z-63a-9a^2;
(32) all five integer rows and necessary-only scope.

Ten hand boundaries were challenged:

1. The h2 partial fan A={p,q,x}, B/C through p and D/E through q with
   private outer points has five S neighbors each and exactly four
   internal D2 edges. No target extension is claimed.
2. A fourfold selected point has weight2 and eight selected edges, so
   neither its contribution nor the k1/h2 support20 may be replaced
   with the unit-weight support21 formulas.
3. Sixty-six coordinates1 and thirty-three coordinates-2 attain sum0
   and norm198; the residue floor alone cannot forbid such a scalar vector.
4. Direct evaluations at-8/-11 give54/108 excess. The earlier six-neighbor
   count would be invalid on h2 and incorrectly strengthen the bound.
5. A fractional formal Gram equality does not bypass integer-plus7/3
   strictness; ordinary target weights are integral.
6. Two wholly-S roots sharing a point strengthen the increment excess
   from12 to20; the weaker12 bound retains both disjoint/shared cases.
7. At z0/a2, six K2, six K1, nine K0 inside and47 outside1/30 outside-2,
   with p=-17, give norm174+167+289=630 and sum0. At z1/a1, six K2,
   eight K1, seven K0 inside and48 outside1/29 outside-2, with p=-14,
   give144+164+196=504 and sum0. These scalar equality counts fit;
   they are not themselves graph constructions or obstructions.
8. Negative residue entries such as-2 have zero excess and remain
   allowed. No positivity of Y or uniform vertex values is assumed.
9. l counts only selected edges, while E_w includes every actual edge;
   additional weighted incidences and ordinary degree increments cannot
   be discarded or double-counted with selected/D2 edges.
10. The factor-nine failure is preserved separately. The present statement
    uses correctly scaled Y3Qw, empty dependencies and explicit maxd2/b5;
    it does not prove b5 impossible, a listed boundary feasible, or R227 excluded.

This is42 written checks (32 proof plus10 boundaries), three outside-table
rows and five integer boundary rows. Executed/formal/external/solver: zero.

## Failed outline, provenance and limits

The unchanged scaling receipt
`acceleration/results/20261004_target_rook_count227_five_d2_scaling_outline_veto01.json`,
SHA256 `59638497433f0601414a2e335d4ae2f01bac5681c96b1535d4ca0b46a7ec3e5b`,
records a message-only argument failure before any b5 paper or gate.
For 9Qchi its norm is81*7*(3n+n^2/9-2e), which equals
63(27n+n^2-18e), not7 times the latter bracket. The missing factor9
invalidated the old fourfold rejection. Nothing here transfers that
argument, mutates the receipt, or calls its theorem REFUTED.

The earlier b6/b7/noD3 papers are bounded comparison evidence only.
Parity/fan/Gram overlap is disclosed, without archive-completeness or
novelty claims. Subsequent stronger k0/h1 or k1/h2 outlines and a Native
edge refinement have not been incorporated into this exact r1 proof or
treated as independent approval of Native's own discovery.

Only small selected metadata reads/hashes and new audit/report/binding
writes occurred. No mathematical program, source import, AST/syntax check,
backend, worker, solver, census, ledger parse, Git/index/publication operation
or protected edit occurred. No start/worker time is invented. Root exact
new-statement acceptance is null at creation. This necessary-condition
claim is outside the closed Wave46 cutoff449 and pending separate Root
review/nextWave47 registration. Target status stays UNKNOWN.
