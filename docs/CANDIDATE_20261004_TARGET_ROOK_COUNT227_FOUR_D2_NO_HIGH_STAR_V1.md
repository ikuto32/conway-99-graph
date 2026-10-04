# Candidate: the ordinary-support four-d2 boundary has no high star

Root proposed this central-root bound; Structural independently reconstructed
its complete opposite-node decomposition and pair capacities. Agreement is
not verification. No program, enumeration, solver, import or worker ran, and
all earlier papers remain unchanged.

## Exact statement

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once and let d_T=6-r_T. Suppose R=227, every d_T is0,1 or2,
and exactly four triangles have deficiency2. Suppose every point used by the
sixteen deficiency1 triangles lies in exactly two of them, with support S,
and all four deficiency2 triangles lie in S. Their actual intersection graph
cannot be the four-node star K1,3.

All support conditions are explicit. This does not alone exclude every b4 or
R227. No support-inducedness, uniformity, equitability, automorphism, or
realizability of a counted profile is assumed.

## Actual-label defect geometry

The target has unique triangle per edge, seven triangles through each point,
and231 actual triangles. Distinct triangles meet at most once and cannot
meet pairwise at three different points. Local uncovered-pair defect degree
at triangle T is d_T, since intersecting triangle pairs determine at most
one rook by their cross-pair second common neighbors. Full positive fan
capacity is P>=3r_1+5r_2. D24 gives a16/P20, and selected multiplicity2
gives S24 and r_2<=2 at all its points. Local defect graphs are K2/P3/P4.

Let F be the global labeled defect graph on sixteen degree3 lows and four
degree6 highs. It has36 edges. Any repeated label of an F4 forces a local
four-cycle, impossible in those local graphs. Distinct labels give an actual
induced uncovered square and the corner-triangle inverse is unique. Of2079
target squares,9 per rook are covered exactly once. Hence C4(F)=36 and
total cycle incidence is144.

No defect K3,3 occurs. Repeated grid labels require local degree3 at all
six roots; distinct labels give an induced actual rook, contradicting its
defect pairs. All codegrees are at most3: disjoint high cross edges form
a matching of at most3 with unique completions; intersecting highs require
same-point common partners; a low member has degree3. No F triangle has a
low node. Therefore each low with a low neighbor contributes at most5,
since attaining6 would force a K3,3. An all-high low contributes at most6
and can meet only an independent high triple.

## Center neighbors, pair counts and low exceptions

Label the high star center C and its leaves A,B,D. Its three leaf intersections
are distinct: three highs at an S point violate r_2<=2. At each shared point
the local P4 attaches one low to C and a different low to the leaf. Thus C's
other three neighbors L_C are lows, each having only C as a high neighbor.
Their sole root-point slot is filled by C; meeting another leaf at another
point would make three distinct actual triangle intersections, and meeting
it at the same point would require local degree2 at that low. They are
independent by the same same-bucket/other-bucket argument. Each has two
low-low neighbors, supplying six stubs in total. The full N_F(C) consisting
of A,B,D and L_C is independent.

Let q count lows adjacent to all three leaves. These are exactly the possible
six-cycle low exceptions: any triple containing C and a leaf is not independent.
Let n_AB,n_AD,n_BD count lows adjacent to exactly the corresponding two
leaves and let n2 be their sum. Each leaf pair already has common high C,
so the codegree capacity gives

    n_AB+q<=2, n_AD+q<=2, n_BD+q<=2,
    n2+3q<=6, q<=2.                            (1)

These exact-profile counts do not overlap each other. In particular q is
not counted three times as an exact-pair low.

## Complete opposite-node bound at the center

All other highs are inside N_F(C), whose internal graph is empty, so every
opposite node in a cycle through C is a low outside N_F(C). For such a Z
put I equal to its leaf-high neighbors and x its low-low neighbors in L_C.
It cannot also meet C, since then it would itself be in N_F(C). Its degree3
therefore gives x<=3-I.

For I0 or1, binom(I+x,2)<=3x/2 for x<=3 or2 respectively. For I2,
x<=1 and binom(2+x,2)=1+2x=1+3x/2+x/2. These are the n2 exact-pair
lows. Their x-sum X2 is at most n2. For I3, x0 and the contribution is3,
at each of the q lows. The sum of x over all opposite lows is precisely
the six stubs from L_C. Consequently

    c_C<=3*6/2+n2+X2/2+3q
        <=9+3n2/2+3q
        <=18-3q/2,                            (2)

using (1). The I2 baseline1 is essential and is not silently discarded.

## Three leaf bounds and complete contradiction

Each leaf has one high neighbor C and five low neighbors. The low neighbor
set is independent: same-point low pairs are covered, and different-root-point
intersections are forbidden. No member meets C since its sole root-point
slot is filled by the leaf. Thus its full neighbor set is independent.
For each external opposite node its common-neighbor count l<=3, and the
sum of all l is6+5*3-6=15. Since binom(l,2)<=l at l0..3, every leaf
contributes at most15.

The sixteen lows contribute at most80+q, accounting for every six-cycle
exception. Combining them with the three leaves and center (2) gives

    sum_Z c_Z<=80+q+3*15+18-3q/2
              =143-q/2<144.

This contradicts the exact target incidence. Fractional upper bounds are
safe; no integer rounding or uniform profile is assumed. The star is
therefore impossible under the literal ordinary-support hypotheses.

## Hand controls, overlap and limits

For q0/1/2 the conservative total bound is143,285/2,142, each below144.
Those scalar endpoints are not asserted graph realizations. The pair-capacity
sum counts q three times only in the three common-pair capacities, whereas
its cycle/low-exception contribution is counted once. All six center stubs
are retained; no opposite high is omitted because all highs were inside
the independent center neighbor set.

The local P4 at a shared high point is allowed and used, not rejected as
an invalid local configuration. Extra actual edges on S are not discarded.
The actual label and K3,3 mechanisms overlap earlier papers; the new
center-profile bound is independently reconstructed here. Other topology
or support candidates are comparisons, not logical premises.
This new CANDIDATE needs distinct verification and makes no b4/R227/target,
construction, execution, ledger, Git or publication-status conclusion.
