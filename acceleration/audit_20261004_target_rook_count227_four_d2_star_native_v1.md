# Independent written audit: ordinary b4 high star

Verification completed **2026-10-04T21:11:59.5935406+00:00** by Native
(`/root/native_driver`), method `independent_derivation`. Structural authored
the mathematical candidate; no computational executor or worker exists.

## Exact source and conditional result

Whole frozen paper
`docs/CANDIDATE_20261004_TARGET_ROOK_COUNT227_FOUR_D2_NO_HIGH_STAR_V1.md`,
SHA256 `bc8894fe106db65764dbe8d99fe1d53ec639e325836bea3183b128374242ff85`,
and whole raw
`acceleration/results/20261004_target_rook_count227_four_d2_no_high_star_candidate01.json`,
SHA256 `bd3e599d1067ca96968d1d53c4950d2aa0c47de2cc31da7c070d1fea49613cb1`,
were independently reconstructed. Exact ID
`C-UNRESTRICTED-TARGET-ROOK-COUNT227-FOUR-D2-NO-HIGH-STAR` r1.

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once and let d_T=6-r_T. Suppose R=227, every d_T is0,1 or2,
and exactly four triangles have deficiency2. Suppose every point used by the
sixteen deficiency1 triangles lies in exactly two of them, with support S,
and all four deficiency2 triangles lie in S. Their actual intersection graph
cannot be the four-node star K1,3.

**PASS for this exact star exclusion.** Dependencies are empty. Ordinary
support and wholly-S high roots are hypotheses; no topology or path/cycle
result is inherited. Root shared a central-profile discovery outline and
Structural separately authored the full candidate. Native independently
derives its geometry, profile partition and bounds here. Agreement supplies
no verification. This is not an exclusion of every b4 or R227 population.

## Independent actual-label reconstruction

Lambda1 fixes one triangle per edge; the neighborhood of a point is seven
disjoint edges. Thus there are231 actual triangles, each linear with the
others. Three pairwise meetings at three distinct points would give an edge
two triangle partners and are forbidden. For two triangles meeting at v,
the unique second common neighbors of their four nonadjacent outer cross
pairs determine any rook completion. Those four points are distinct by
lambda1, so the pair admits at most one induced rook. A rook containing T
corresponds to one covered partner at each of its three points, hence local
uncovered degree d_T and global defect degree3d_T.

Each rook has six actual triangles, so sum d=6(231-227)=24. Four d2
roots with no larger deficiency leave16 d1 roots,20 positives. Ordinary
selected incidence2 gives24 support points. The full positive fan at a
point with r1 lows and r2 highs uses at least3r1+5r2 roots: outside
partners counted at the two outer points cannot serve two concurrent
roots, by triangle linearity and the forbidden loose triple. At every
high point r1=2, so20>=6+5r2 implies r2<=2.

Local positive graphs are therefore K2, P3, or P4 with degrees(2,2,1,1).
In P4 the high-high edge is forced and its two low attachments differ.
Thus actual high intersections are defects, and the three center-leaf
intersection labels in an actual star are distinct. All relevant local
graphs lack a four-cycle.

F has16 degree3 low nodes,4 degree6 high nodes and36 edges. Any repeated
point label on an F four-cycle propagates concurrency of all four roots,
requiring a local four-cycle; this is absent. Distinct labels give an
actual induced square because either diagonal edge would have two common
neighbors and violate lambda1. Its edge triangles invert this map. A rook
covering a corner pair contains the opposite corner fixed by mu2 and
therefore the entire square; the corner pair fixes at most one rook.
Covered squares have all corners covered and uncovered squares all
defects. Hence all4158 nonadjacent pairs give2079 squares by two diagonals,
each rook covers9 once, and C4(F)=2079-9*227=36. Required node-cycle
incidence is144.

For a defect K3,3 any repeated grid label makes three roots concurrent
and propagates all six to that point, requiring local degree3 contrary
to maxd2. Nine distinct labels give the actual nine-point rook from row
and column triangles; any additional nonrook edge would have two grid
common neighbors. Its pairs cannot be defects. Both label cases exclude
K3,3. Disjoint highs have a matching of at most3 actual cross edges with
unique triangle completions. Intersecting highs have common defect
partners only at their intersection; the local P4 has none. All pairs
with a low have codegree<=3 from that low's degree, so every F codegree
is<=3.

No F triangle contains a low: different labels form a forbidden loose
actual triple, and concurrent labels need low local degree2 instead of1.
A low has at most6 cycles from three neighbor pairs and codegree3. With
a low neighbor, equality6 forces that neighbor's entire three-node
neighborhood to be shared with both others, making K3,3. Such lows have
at most5. All-high lows can have6 only when their high triple is independent.
In a star the only independent high triple is the three leaves. These
exceptions will be counted once, not removed or silently bounded by5.

## Center's complete independent neighbor set

Write C for the high center and A,B,D for its leaves. At each of the
three distinct shared points, local P4 supplies one low attached to C
and a different low attached to the leaf. Thus C has exactly three low
neighbors L_C besides its leaves. Each member of L_C has only C as a
high neighbor: at the same point its local degree1 slot is filled by C,
and another-point intersection with a leaf would make a loose triple.
These three lows are distinct and independent; same-point lows would
have their pair covered, while different-point intersections are forbidden.
Consequently each member of L_C has exactly two low-low neighbors,
giving six low-low stubs.

The leaves are mutually nonadjacent, and no low in L_C is adjacent to
one of them. Thus the complete six-node N_F(C) is independent. All other
high roots are in this set. Every cycle through C has an opposite node
outside C and N(C), and that node must be a low. No high or internal
opposite is omitted.

## Exact-pair profiles and triple profiles are distinct

Let q be the number of lows adjacent to all three leaves. Let n_AB,
n_AD,n_BD count lows adjacent to exactly the named pair of leaves, and
n2 their sum. The exact-pair sets are disjoint from one another and from
the all-three set. For any leaf pair, the common high C already consumes
one of its three codegree slots. The other common neighbors can be only
the n_pair lows and q triple lows, so

    n_AB+q<=2, n_AD+q<=2, n_BD+q<=2,
    n2+3q<=6, 0<=q<=2.

Here q is counted three times in the sum of the three pair capacities,
but once in its actual profile and cycle count. Neither exact-pair nor
triple-profile lows can be in L_C, whose members have only C as a high.

## Center bound from all opposite lows

For every opposite low Z let I be its number of leaf-high neighbors and
x the number of its low-low neighbors in L_C. Z is not adjacent to C,
and degree3 gives x<=3-I. All six L_C low-low stubs end at opposite
lows, because L_C is independent and they cannot end at a high. Thus
sum_Z x=6 exactly, without asserting uniform distribution.

At I0 or1, binom(I+x,2)<=3x/2. At I2, x0/1 gives1+2x, equal to
3x/2+1+x/2. There are exactly n2 such lows; their x total X2<=n2.
At I3, x0 and the contribution is3 for each of q lows. This exhaustive
partition yields

    c_C<=9+n2+X2/2+3q
        <=9+3n2/2+3q
        <=18-3q/2.

In particular the I2/x0 baseline1 is included. The maximum6 low-cycle
exceptions were not subtracted here and will enter the whole sum next.

## Leaves, low exceptions and complete contradiction

A leaf has one high neighbor C and five low neighbors. Its low neighbor
set is independent by the same same-point covered/different-point loose
argument. None of those lows is also adjacent to C: at their root point
their one local slot is already the leaf, or a different intersection
would be loose. Thus its full six-neighbor set is independent. For every
external opposite node let l be its common-neighbor count, at most3.
The sum of l is6+5*3-6=15; binom(l,2)<=l gives each leaf c<=15,
including both other high opposites when present.

Exactly q lows have an all-high independent triple of neighbors, namely
the three leaves. All remaining lows have a low neighbor. Their complete
contribution is at most5(16-q)+6q=80+q. Adding all20 F nodes gives

    sum_T c_T<=80+q+45+18-3q/2
              =143-q/2<144.

This contradicts the actual square incidence. The proof treats every
allowed q and every profile/stub distribution; it does not assert that
the scalar bounds are realized or round fractions incorrectly.

## Thirty proof checks and ten written falsification controls

The30 proof checks are: unique triangle/231; linearity/no-loose triples;
rook-pair uniqueness; local/global deficiency; D24/a16/P20; ordinaryS24;
fan/r2<=2; K2/P3/P4; actual HH=defect/distinct center labels; F36;
label-collapse exclusion; square faithfulness/inverse;2079/9/36/144;
K3,3 repeated labels; K3,3 distinct grid; all codegrees; no low F
triangle; low5/6 exception; center three low attachments; center-low
high profiles; independent N(C); six stubs/high opposites; exact-pair
versus triple partition; three pair capacities; exhaustive I/x cases;
X2 and center18-3q/2; leaf neighbor independence; leaf15;
complete low80+q;143-q/2 contradiction with literal scope.

Ten hand controls:

1. Local P4 at a shared high point is allowed, not a forbidden C4:
   the lows attach to different highs and each retains degree1.
2. A repeated square label would need four roots at one point; the
   fan and ordinary-support local list remove it. A general defect
   graph with collapsed cycles is not silently equated to actual squares.
3. A central low with another leaf high neighbor fails either its
   same-point degree1 or the no-loose actual-intersection law. An
   arbitrary graph's high profile cannot replace that actual geometry.
4. For I2/x0 the opposite contributes1; for I2/x1 it contributes3.
   Keeping only3x/2 would undercount by1 or3/2.
5. I3 has x0 and contributes3. Counting it in n2 as well would duplicate
   its profile; it enters three pair capacities but one center term.
6. q0/1/2 allows n2<=6/3/0 and center<=18,33/2,15.
   These are conservative scalar endpoints, not graph constructions.
7. Corresponding full upper bounds are143,285/2,142, allbelow144.
   Fractional inequalities are retained without any realizability claim.
8. A low adjacent to all three leaves is a possible six-cycle exception;
   setting the complete low bound80 for q>0 would be unjustified.
9. The three central low nodes have six stubs regardless of q; no
   high opposite exists at the center, while generic leaf15 includes
   its possible high opposites rather than dropping them.
10. A path/cycle high graph has independence number2 and a different
    root partition. This star-only gate does not approve those branches
    or infer ordinary support from unrestricted b4 hypotheses.

This is40 written checks (30 proof,10 hand); executed, formal, external,
solver and scientific checks are zero. Small source/metadata reads and
selected hashes only. Shared actual-label mechanisms and discovery
origins are disclosed, but every required lemma here is rederived with
empty dependencies. No mathematical program/import/AST/syntax/backend,
census, worker, ledger parse, Git/index/publication or protected mutation
occurred. Start/executor fields and Root exact new acceptance are null
at creation. Only the literal ordinary-support star is excluded; target
resolution NONE and overall scientific coverage UNKNOWN are retained.
