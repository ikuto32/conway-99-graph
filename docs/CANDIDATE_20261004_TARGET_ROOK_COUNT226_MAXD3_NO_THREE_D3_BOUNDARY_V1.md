# Candidate: at R226 and max deficiency three, exactly three d3 roots are impossible

Root supplied the even odd-deficiency-family outline. Structural independently
challenged its local coverage, weighted-edge identity, exceptional-point
count and all integer b cases. The proof below removes an unnecessary
two/four-incidence assertion and gives a stricter direct b0 contradiction.
This is a new written CANDIDATE, pending a different full review. No
mathematical program, enumeration, import, solver or worker ran. All earlier
R226 papers and publication records remain unchanged.

## Exact statement and literal scope

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle.
Suppose R=226 and every d_T belongs to {0,1,2,3}. Then the number of actual
triangles with deficiency three is not three.

Maximum deficiency three is an explicit hypothesis. No pending upper-three
or population-upper-three gate is used as a logical premise. The necessary
fan, parity, selected-edge and target Gram identities are derived below;
the logical dependency list is empty. This is not an exclusion of R226,
not a realization claim and not a target resolution.

Assume for contradiction c=3. Write a,b for the d1,d2 populations. Then

    a=21-2b, P=a+b+3=24-b, 0<=b<=10.          (1)

## The three d3 roots are disjoint and bad points are controlled

At a point, the simple local defect graph has degrees equal to the incident
deficiencies. Therefore r1+r3 is even, and the actual positive fan gives

    3r1+5r2+7r3<=P.                            (2)

Each external positive triangle meets at most one fan outer point: same-
root repetition violates linearity, while different-root repetition gives
three actual triangles pairwise meeting at distinct points and violates
lambda1. Counting the roots and their two outer sets of defect partners
proves (2), without uniform neighborhoods or an automorphism assumption.

Two d3 roots at one point require even r1. At r1=0, at least two d2 roots
are needed for degree three, giving fan24 but b>=2 and P<=22. At r1=2,
r2=0 the sequence(3,3,1,1) is nongraphical; any r2 adds fan at least25.
At r1>=4 the fan is at least26. Three d3 roots require odd r1: the minimum
sequence(3,3,3,1) is nongraphical, while any further node gives fan at least29.
Hence the three actual d3 triangles are pairwise disjoint.

Let S3 be their nine actual points. Each has precisely one d3 root, so r1
is odd. If r1=1, degree three needs r2>=2 and fan at least20. Call this a
bad point. Every other point of S3 has r1>=3. When b0/1 there are no bad
points. When b2 there is at most one, because its two d2 roots cannot meet
at two actual points. When b3 there are at most three, one per unordered
d2 pair. When b4 there are at most six. A bad point at these b values has
exactly two d2 roots: a third would give fan25>P. When b>=5, P<=19 and no
bad point is allowed at all. The valid bad local graph(3,2,2,1) is retained.

For each d1 triangle L let t_L be its number of S3 points. Then

    sum_L t_L>=27-2h,                          (3)

where h counts bad points. Also

    sum_L binom(t_L,2)<=9.                     (4)

Indeed any two of the disjoint d3 roots have at most three cross edges,
forming a matching; each such edge has one actual triangle completion.
There are three root pairs. The count in (4) is of their actual common d1
triangles, without assuming each low triangle has the same t_L. Because
binom(t,2)>=t-1 also at t0, (3)-(4) imply a>=18-2h.

## Exact weighted selected-family identity

Let O be D1 union D3, all odd positive-deficiency triangles. Its size is
s=a+3=24-2b. At every actual vertex its incidence m_v is even by the local
degree sum. On its support S put w_v=m_v/2, a positive integer, and put
w_v=0 elsewhere. Thus sum w=3s/2. Define

    K=sum_v w_v(w_v-1),
    ell=sum_{uv a selected O edge}(w_u-1)(w_v-1),
    H=sum_{uv an internal S edge not in O} w_u*w_v.

All are nonnegative integers. Each selected edge belongs to its unique
actual O triangle. Expanding w_u*w_v=(1+(w_u-1))(1+(w_v-1)) in every
selected triangle gives the exact identity

    E_selected=3s+4K+ell.                      (5)

The linear terms sum to 2 sum_v m_v(w_v-1)=4K. Further actual internal
edges are included in H. Since ||w||^2=3s/2+K, the target positive
semidefinite Q=3I-A+J/9 yields

    0<=q=w^T Qw=s(s-6)/4-5K-2ell-2H.         (6)

No selected inducedness assumption removes H. Selected incidences larger
than four are allowed and only increase K. In particular there is no
unsupported assertion that every selected point has incidence two or four.

At every nonbad S3 point, m_v=r1+1>=4 and w_v>=2, contributing at least
two to K. Thus

    K>=2(9-h).                                (7)

## Cases b1, b2 and b3

Drop the nonnegative ell,H terms in (6). The exact bad-point bounds and
(7) give

| b | s | s(s-6)/4 | h upper bound | K lower bound | q upper bound |
|---:|---:|---:|---:|---:|---:|
|1|22|88|0|18|-2|
|2|20|70|1|16|-10|
|3|18|54|3|12|-6|

All contradict q>=0. Additional actual edges or larger incidences cannot
repair a negative upper bound.

## Case b0: a strict selected-edge contradiction

Here s24, h0, a21 and K>=18. The three d3 triangles have all nine points
of weight at least two, so their nine edges contribute at least nine to
ell. The d1 triangles contribute at least sum_L binom(t_L,2): each edge
between two S3 points has both w-1 factors at least one. These selected
edges are distinct from the central d3 edges and each other. By (3) and
binom(t,2)>=t-1,

    ell>=9+(27-a)=15.

Equation (6) therefore gives q<=108-90-30=-12, impossible. This avoids
any unproved equality realization or an assumption of a nonconstant code.

## Case b>=5: the actual pair moment suffices

There are no bad points because P<=19. Equations (3)-(4) force a>=18.
But (1) gives a<=11 when b>=5. This contradicts every integer b5 through10,
including the endpoint a1. There is no unexamined large-b branch.

## Case b4: four d2 roots force too many internal edges

Here a13, s16 and P20. Equations (3)-(4) give 14-2h<=9, so h>=3; the
actual pair bound also gives h<=6. Therefore (7) gives K>=6.

At a point outside the selected support S, no odd-deficiency root occurs.
All positive local roots are d2. Any such point needs at least three d2
nodes for local degree two, and with b4 it uses three or four of them.
If all four roots meet at an outside point, every d2 pair already intersects
there. No bad S3 point can contain a d2 pair, so h=0, contrary to h>=3.
Hence no four-root outside point occurs.

There is at most one outside point containing three d2 roots: two triples
drawn from four share at least two actual roots, which would have two
common vertices. At zero outside points all four d2 triangles are wholly
in S. At one, three have two S points and the fourth has all three. Thus
they provide at least three single internal edges plus one internal
triangle, for six actual edges outside O. Their weights are at least one,
and all edges are distinct by lambda1. Consequently H>=6.

Equation (6) now gives q<=40-30-12=-2, impossible. This reasoning permits
six or more selected incidences away from S3; it only uses the valid lower
bound K>=6. No equitable local profile or inferred absence of extra edges
is invoked.

## Exhaustive conclusion and preserved boundaries

The b0, b1..3, b4 and b5..10 cases exhaust (1). Therefore exactly three
d3 triangles are impossible under the literal maxd3/R226 hypotheses.

The proof keeps parity on D1 union D3, not on D1 alone. The true local
(3,2,2,1) graph supplies the explicitly bounded bad point. The weighted
identity (5) is an equality over all selected triangle edges; all other
internal target edges remain in H. The possible four-d2 outside point is
excluded using the independently forced h>=3, not assumed away. The
repeated-intersection veto applies to actual triangles and actual points.

The rejected outline's stronger assertion of only two/four selected
incidences is not required or adopted. The b0 equality outline is replaced
by the strict ell>=15 edge bound; no original proof bytes are overwritten.
These revisions are disclosed independent hand refinements, not an
independent verification gate for the new theorem.

Fan/parity, cross-triangle matching moments and weighted target-upper-Gram
methods overlap prior papers. The new exact scope is exclusion of c3 at
R226/maxd3. No novelty, whole-archive coverage, R226 exclusion, graph
construction, nonconstant codeword existence or target resolution is
claimed. This paper is outside the current publication cutoff and awaits
a different-author exact written challenge before any VERIFIED use.
