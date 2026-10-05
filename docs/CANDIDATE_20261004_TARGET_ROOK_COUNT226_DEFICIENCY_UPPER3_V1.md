# Candidate: at R226 every triangle deficiency is at most three

Root supplied the odd-deficiency capacity outline and the six remaining
population cases. Structural independently reconstructed every parity,
point-label, norm and cycle step below. This is a new CANDIDATE statement,
pending a different written challenge. The earlier deficiency-four necessary
paper is preserved. No mathematical program, enumeration, solver, import or
worker ran; no ledger, Git or publication record changes.

## Exact statement and explicit inherited premises

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle. If
R=226, then every d_T belongs to {0,1,2,3}.

Use these exact r1 statements:

* C-UNRESTRICTED-TARGET-ROOK-DEFICIENCY-STRICT-SECOND-NEIGHBOR-BOUND:
  nonzero maximum m at R<231 satisfies D>=6m+6. Here D=30 gives m<=4.
* C-UNRESTRICTED-TARGET-ROOK-COUNT226-DEFICIENCY4-BOUNDARIES: if a d4
  root exists at R226, there is exactly one, a=26-2b-3c,
  3<=b+2c<=6, and its three positive point graphs are pure K1,4 with four
  d1 leaves. The d4 root is disjoint from all d2/d3 roots.

The second statement is separately frozen and still awaiting independent
verification at this preparation time. Its scope is used literally, without
assuming its surviving scalar possibilities are realizable. The present
proof does not use any pending R227 exclusion. It excludes d4 at the stated
count; it does not exclude R226 or resolve the target.

## Odd-deficiency capacity leaves exactly six scalar pairs

Assume a d4 root T exists. Let O be the actual triangles with odd positive
deficiency: O=D1 union D3. Its size is

    s=a+c=26-2b-2c.

At each actual point, the sum of the local defect degrees is even. Thus the
number of O triangles through that point is even; this includes d3 roots,
and makes no false assertion that the d1 subfamily alone is even.

At each of the three points of T there are exactly four d1 roots. The twelve
roots are distinct, since an actual triangle cannot contain two points of T.
Their twenty-four outer points are all distinct. Two outer points in the
same fan bucket cannot coincide by triangle linearity. A common outer point
between different buckets at adjacent central points v,w would be a second
common neighbor of v,w besides the third point of T, contrary to lambda1.

Each central point has O incidence four; every one of the twenty-four outer
points has positive even O incidence at least two. Therefore

    3s >= 3*4+24*2 = 60,
    s>=20, and b+c<=3.                         (1)

Combine (1) with 3<=b+2c<=6. The complete hand intersection is

    (b,c) = (3,0),(2,1),(1,2),(0,3),(1,1),(0,2). (2)

No count of unlisted actual graphs or a numerical search is involved.

## Three cases have exact support and a norm contradiction

First take (b,c)=(3,0),(2,1), or (1,2). Then b+c=3 and s=20, so equality
holds in the incidence bound. The selected support S has precisely the
three central points of T, each O incidence four, and the twenty-four
outer points, each incidence two. There are no other selected points or
larger selected incidences. Put w equal to half the O incidence: w is two
at the central points and one at the twenty-four outer points. Consequently

    |S|=27, sum w=30, and ||w||^2=36.

Each outer point is adjacent to exactly one central point. Its own fan
provides one; a second central adjacency contradicts lambda1 on the central
edge. All twelve O roots through central points are d1 roots, and no other
O root contains a central point. The twenty O triangles contribute selected
weighted edge sum 12*5+8*3=84: a root with one weight-two point contributes
2+2+1=5, and a root with all weights one contributes three. All actual
triangle edges are distinct by lambda1. The three edges of T add twelve,
so the known weighted sum is96.

Before adding the edges of T, selected weighted neighbor sums are eight at
each central point and five at each outer point. The latter has two O
triangles and exactly one central neighbor, with all four selected neighbors
distinct. Define the target upper Gram projector

    Q=3I-A+J/9, Q^2=7Q, Qj=0, Q positive semidefinite,
    Y=3Qw=9w-3Aw+10j.

These identities follow directly from A^2=12I-A+2J and Aj=14j.
Before the edges of T the support values of Y are all four. The T edges
increase the weighted neighbor sum by four at each central point; thus the
known-edge values are minus eight there and four at the twenty-four others.
Their squared norm is576 and their sum72.

Let z be the weighted sum of all additional actual edges internal to S.
It is a nonnegative integer. Such an edge contributes w_u*w_v to z and
w_u+w_v to the unweighted sum of additional weighted neighbor increments.
Because both weights belong to {1,2}, w_u+w_v<=2*w_u*w_v. If t_v is the
additional weighted neighbor increment at v, then sum_S t_v<=2z. Every
initial support value y is at most four, so for integer t>=0,

    (y-3t)^2-y^2 >= -15t.

The actual support values consequently satisfy

    sum_S Y>=72-6z, ||Y_S||^2>=576-30z.        (3)

All99 entries of Y are integers congruent to one modulo three, and sum Y=0.
For any such integer y, y^2+y-2>=0. On the seventy-two outside points this
gives

    ||Y_out||^2 >=144-sum_out Y
                 =144+sum_S Y >=216-6z.

Together with (3), the total norm is at least792-36z. On the other hand,
the complete actual weighted edge sum is96+z, so

    w^T Qw=3*36+30^2/9-2(96+z)=16-2z,
    ||Y||^2=9 w^T Q^2 w=63(16-2z)=1008-126z.

Comparison forces 90z<=216, hence z<=2.

Every d2 root supplies additional internal edges. At a point outside S,
no d1/d3 root occurs and T is wholly in S. A positive local root there must
therefore be d2. Its degree two requires at least three local d2 nodes. If
b is one or two, this is impossible, and each d2 root is wholly in S. If
b is three, an outside point contains all three d2 roots; there can be at
most one such point because two would give two roots a repeated pair of
intersection points. Each d2 root then has at least two points in S and
supplies an internal edge. These edges are distinct from O/T and each other
by lambda1, and each has weight at least one. In all three cases z>=3,
contradicting z<=2. Arbitrary additional actual edges were counted in z,
not assumed absent.

## The exact cycle method for the other three cases

Use the actual positive defect graph F: its nodes are positive-deficiency
triangles; an edge is an uncovered local rook pair, labeled by the actual
intersection point. A deficiency-i node has degree3i. At R226 its45 edges
and the target's45 uncovered squares must give180 cycle incidences whenever
the square-to-F4 map is faithful.

Here are the needed local and converse checks, rather than an assumed
globally triangle-free F. A collapsed F4 at one actual point requires four
roots of local defect degree at least two. None of the cases below has
such a profile. A repeated-label K3,3 grid requires six roots of local
degree at least three, again unavailable. A distinct-label grid produces
an actual induced rook-nine; the extra edges are forbidden by lambda1/mu2,
so it contradicts the designated defect edges. Thus F has no K3,3 and the
actual square/F4 correspondence is faithful.

Every codegree is at most three. For disjoint high triangles their cross
edges form a matching of at most three with unique completions. Intersecting
highs have common defect neighbors only at their shared point. Low nodes
have degree three. At a high root, its low neighbors have their sole local
defect slots filled by the root; they cannot intersect each other across
different root points without violating lambda1. The only internal edges
among a high root's neighbors are any explicitly retained high-high edge.

For a root with degree d and neighbor set N, put

    B=sum_{x in N}deg_F(x)-d-2e_F(N).

The outside-opposite decomposition gives c_root<=B because its codegrees
l are at most three and binom(l,2)<=l. For a low node with a low neighbor,
the stronger bound c_low<=5 holds: six requires all three pair codegrees
to equal three and produces K3,3. An all-high low can contribute six, but
its three highs must be independent. Their number is bounded below case
by case. These bounds preserve all actual intersection labels and extra
edges; no uniform profile or automorphism is assumed.

### (b,c)=(0,3)

Here a=17 and P=21. No two d3 roots intersect. At a point containing two,
parity makes r1 even and fan14+3r1<=21 gives r1<=2. The degree sequence
(3,3,1,1) at r1=2 is nongraphical; r1=0 has too few nodes for degree three.
Three d3 roots require odd r1>=1 and fan at least24. At a point containing
one d3, parity requires odd r1; degree three needs r1>=3 and fan7+3r1<=21
forces exactly three. Thus all d3 points are pure three-leaf stars, and
the d4 is separately disjoint from them by the inherited boundary.

F has four pairwise disjoint highs, of degrees12,9,9,9, and seventeen lows.
The high bounds are24,18,18,18. At most twelve lows have three high
neighbors: for each of the four high triples there are at most three
common lows by the pair codegree bound. Therefore the complete incidence
upper bound is

    17*5+12+24+3*18=175<180.                  (4)

The twelve is an upper bound, not a claimed realizable intersection pattern.

### (b,c)=(1,1)

Here a=21 and P=24; the d4 is isolated from the d2 and d3. If those two
highs are disjoint, their bounds12 and18 together with24 at the d4 give54.
The twenty-one lows contribute at most105+3, hence162<180.

If d2 and d3 meet, the local parity, degree and fan bounds require degree
sequence(3,2,1,1,1): the high-high edge is present, two low leaves belong
to d3 and one to d2. For if the high-high edge indicator is x and low-low
edge count y, high-degree minus low-degree gives x-y=1. Their root neighbor
sets have eight lows plus the degree-six high, and five lows plus the
degree-nine high respectively, with no internal neighbor edge. Hence B21
and B18; d4 contributes24. No all-high low exists since the three highs
are not independent. The total is

    21*5+24+21+18=168<180.                   (5)

No low-low local edge or omitted branch is silently removed.

### (b,c)=(0,2)

Here a=20 and P=23. The two d3 roots are disjoint: an intersection requires
even r1, fan14+3r1<=23 and the same failed(3,3,1,1) degree sequence;
r1=4 would need26. They are also disjoint from the d4. Each d3 root has
nine independent defect-neighbor lows and B18, regardless of any separate
low-low component at a point. The d4 has B24. At most three all-high low
exceptions occur. Thus

    20*5+3+24+2*18=163<180.                  (6)

Each case has faithful45 cycles and hence must have180 incidences, so
(4)-(6) contradict the complete target requirements.

## Coverage, falsification boundaries and pending status

All six pairs in (2) have now been contradicted. Thus the inherited d4
necessity cannot occur. Strict mass had already limited the maximum to
four, proving the exact stated upper-three conclusion at R226.

The proof explicitly retains the parity of d1+d3 rather than d1 alone.
The valid local(4,2,2,1,1) profile belongs to the earlier necessary proof,
where its complete incidence is179, not to a false local nongraphical
veto. The present six-case reduction does not invoke it again. The support
norm factor is63 for Y=3Qw, not seven; all seventy-two outside entries are
included. The distinct central twenty-four-point claim was checked using
lambda1 on the actual central edge, and the b3 outside point uses triangle
linearity rather than an equitable quotient. All further actual edges enter
the nonnegative integer z. A codegree cap or K3,3 assertion is used only
with the literal root population and label checks given above.

This conditional result makes no rank/codeword-existence claim, does not
exclude R226, and does not resolve the SRG(99,14,1,2) question. The current
publication cutoff is unchanged. The necessity and present full proof
require separate exact written gates; none is inferred from Root's outline
agreement or from prior R227 approvals. The bounded overlap comparison is
the one disclosed by the preserved necessary paper, not a new whole-archive
or novelty assertion.
