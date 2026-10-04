# Candidate: the ordinary-support four-d2 boundary has no high path or cycle

Root proposed the inner-root opposite-node decompositions. Structural
independently reconstructed both, including all actual labels and high/low
possibilities. The C4 derivation was also obtained independently before Root's
same outline arrived. Shared discovery is disclosed; agreement is not a gate.
No program, enumeration, solver, import or worker ran. Older bytes are preserved.

## Exact statement

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once and let d_T=6-r_T. Suppose R=227, every d_T is0,1 or2,
and exactly four triangles have deficiency2. Suppose every point used by the
sixteen deficiency1 triangles lies in exactly two of them, with support S,
and all four deficiency2 triangles lie in S. Their actual intersection graph
cannot be P4 or C4.

The ordinary support and wholly-S conditions are explicit hypotheses. This
does not exclude every b4 population or R227 by itself. No induced selected
support, uniform profile, equitability, automorphism or realizability is assumed.

## Exact target defect geometry

The target has231 actual triangles, unique triangle per edge, seven per point.
Distinct triangles meet at most once; pairwise meeting at three distinct
points would give an edge two triangle partners. At a point the local defect
graph of uncovered triangle pairs has node degree d_T: each covered partner
corresponds to one unique induced rook, fixed by cross-pair second common
neighbors. The positive fan gives P>=3r_1+5r_2. Here D24 fixes a16/P20,
S24, and r_1=2 at every high point, so r_2<=2. Local graphs are K2, P3 or
P4. No local four-cycle occurs. A high intersection has the P4 degree
sequence(2,2,1,1), hence its high-high edge is a defect.

The global labeled defect graph F has sixteen low nodes of degree3, four high
nodes of degree6 and36 edges. A repeated point label of an F4 forces all four
roots at one point, impossible by those local graphs. Distinct labels form
an induced actual square, and its corner pairs are defects exactly when it
is uncovered by a rook. The inverse corner-triangle map is unique. There
are2079 target squares and9 per rook, with at most one rook per square,
so C4(F)=36 and its total node incidence is144.

A defect K3,3 with repeated labels requires all six roots at one point with
local degree3, impossible under maxd2. Distinct grid labels instead form an
actual induced rook; extra grid edges violate lambda1, and its covered pairs
cannot be defects. Thus no K3,3 occurs. All F codegrees are at most3:
disjoint high cross edges form a matching of at most3 with unique completions;
intersecting highs can have common F neighbors only at their common point;
and any pair with a low member uses its degree3.

No F triangle contains a low node, by the distinct-intersection rule and its
local degree1. A low with a low neighbor has at most5 cycles: attaining6
would force that neighbor's three-node neighborhood inside the two other
neighbor sets, making K3,3. An all-high low neighbor triple must be independent
in the high graph. Both P4 and C4 have independence number2, so every low
has a low neighbor and contributes at most5, for total80.

At any high root T, its low neighbor set is independent. Two lows at the
same root point have their own pair covered, while those at different root
points cannot intersect by the forbidden three distinct intersections.
No low in that set meets another high intersecting T: at the same point its
local slot is filled by T, and at another point the intersection is forbidden.
The high neighbor graph is also empty for P4/C4. Thus the full neighbor set
is independent and every opposite node of a cycle lies outside it and T.
Writing l_O=|N_F(O) intersect N_F(T)|<=3, generic counting gives c_T<=sum l_O.
In particular a P4 endpoint with one high and five low neighbors has c<=15.

## P4: each inner high has at most15 cycles

Label the highs A-B-C-D. Let n_AC and n_BD count low common neighbors of
the indicated disjoint high pairs. They already have common highs B and C
respectively, so n_AC,n_BD<=2.

For B, N_F(B) is A,C and four lows L_B. Each member of L_B has high profile
B or BD, since it cannot meet the intersecting A or C. The total low-low
stubs from L_B are8-n_BD. No stub stays inside its independent set.
The only opposite high is D, with l=1+n_BD, giving at most3n_BD/2 cycles
because n_BD0..2.

For each opposite low Z put I=|N_F(Z) intersect {A,C}| and x equal to its
low-low neighbors in L_B. If I0, x<=3 and binom(x,2)<=3x/2. If I1,
x<=2 and binom(1+x,2)<=3x/2. I2 occurs at precisely n_AC lows; each has
x<=1 and binom(2+x,2)=1+2x=1+3x/2+x/2. Summing x counts the8-n_BD
stubs. Summing x over the I2 lows, called X, gives X<=n_AC. Thus

    c_B<=3n_BD/2+3(8-n_BD)/2+n_AC+X/2
        <=12+3n_AC/2<=15.

The exact symmetric argument gives c_C<=15. Both endpoints have generic
bound15. The complete incidence is therefore at most80+4*15=140<144,
contradicting the target count. No opposite high or low was omitted.

## C4: every high has at most15 cycles

Label the highs A-B-C-D-A. The opposite high pairs AC and BD already have
two common highs, so n_AC,n_BD<=1. For A, its four-low neighbor set L_A
has high profiles A or AC and low-low stubs8-n_AC. The only opposite high
C contributes binom(2+n_AC,2)=1+2n_AC for n_AC0/1.

For opposite lows use I=|N_F(Z) intersect {B,D}| and x its neighbors in
L_A. The I0/I1 bounds are3x/2 as above. I2 occurs at n_BD lows, with
x<=1, adding at most n_BD+X/2 beyond that bound, where X<=n_BD. Hence

    c_A<=1+2n_AC+3(8-n_AC)/2+n_BD+X/2
        <=13+n_AC/2+3n_BD/2<=15.

The argument at each other high merely interchanges the two opposite-pair
counts. All four have bound15, again giving80+60=140<144.

## Hand boundaries, overlap and limits

The I2/x1 term is exactly3; replacing it by3x/2 alone would omit its
baseline cycle and be invalid. The additional1+x/2 is retained. P4 n2
and C4 n1 boundaries are not assumed realized or uniform. At I0/x3 the
3x/2 bound is conservative. All stubs end at opposite lows because the
root low sets are independent, and the listed opposite high is counted
separately.

The square, K3,3 and codegree mechanisms overlap earlier work and are
reconstructed for these literal labels. The new improvement is the complete
inner/opposite-root bound15 rather than the generic18. The ordinary-support
topology candidate is comparison, not a logical premise: this paper explicitly
assumes its support conditions and treats only the stated two high graphs.
This new CANDIDATE needs distinct verification. It neither excludes the star
nor b4/R227 as a whole, and changes no ledger, Git or publication selection.
