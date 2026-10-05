# Candidate: the one-d3, seven-d2 R226 boundary has a restricted nineteen-point profile

Structural derived the attached-root capacity and residue-norm restrictions.
Root challenged the small pair budgets and equality thresholds. This new
written CANDIDATE is a necessary profile, not a whole boundary exclusion.
No previous one-d3 range or b8 result is used. No mathematical program,
import, census, backend or worker ran; previous artifacts remain unchanged.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T. Suppose R=226, every d_T
belongs to {0,1,2,3}, exactly one actual triangle T has deficiency three,
and exactly seven actual triangles have deficiency two. Then T has two
points each incident to exactly three d1 and no d2 triangles, and one point
incident to exactly one d1 and two d2 triangles. The even selected family
O=D1 union {T} consists of fourteen actual triangles, supported on nineteen
actual points: the first two T points each have selected incidence four,
and all seventeen other support points have selected incidence two.
The induced support has exactly42 or43 edges, consisting of the42 selected
triangle edges and at most one further edge. Any further edge joins ordinary
points and avoids the third T point. The two d2 triangles through that third
T point have four distinct outer points, all outside the selected support.

The maxd3/c1/b7 conditions are literal hypotheses. The logical dependency
list is empty; all required facts are reconstructed below. The profile is
not asserted realizable and is not declared impossible. No whole one-d3,
R226 or target exclusion follows.

Summing deficiency gives D=1386-6R=30, hence a13 d1 roots and P21 positive
roots. The local defect graph at an actual point has node degrees d_T,
and r1+r3 is even. Distinct actual triangles meet at most once; three
pairwise-intersecting roots concur, because three distinct intersections
would give a target edge a second common neighbor. Counting outer defect
partners of a positive point fan therefore gives

    P>=3r1+5r2+7r3.                                  (1)

Each external positive root meets at most one outer point of that fan,
by linearity and the actual three-root prohibition. Covered intersections,
separate local components and additional actual edges remain allowed.

## T-point profiles and the selected Gram

At a T point, r1 is positive odd. A bad point has r1one and exactly two
d2 roots, with local sequence(3,2,2,1): T joins all other nodes and the
d2 pair is also joined. A good point has r1three and zero or one d2.
With one d2 its degree sequence(3,2,1,1,1) forces the T-d2 edge, two T-d1
edges and the d2's remaining d1 leaf. Larger r1 has fan at least22>P21.
Let h count bad points and g count good points carrying a d2 root;
0<=h<=3 and0<=g<=3-h. All such cases will be considered.

The selected O has s14 triangles. Let w be half its even point incidence,
K=sum w(w-1), ell=sum(w_u-1)(w_v-1) over selected triangle edges, and H
the weighted sum of every other actual internal edge. Nonzero w>=1,
so all three quantities are nonnegative. The exact expansion with
Q=3I-A+J/9 positive semidefinite is

    q=w^TQw=28-5K-2ell-2H>=0.                        (2)

Each good T point has w2, each bad point w1. Thus K>=2(3-h) and
ell>=binom(3-h,2). All larger selected incidences remain permitted here.
Put Y=3Qw. Then sum Y=0, Y is integer1 mod3 because sum w=21, and

    ||Y||^2=63q.                                     (3)

This is the factor63 normalization, not a factor-seven norm formula.

There are m=2h+g distinct attached d2 roots meeting T. Their2m outer
points are all distinct: same-point attachments cannot meet twice, and
attachments at different T points cannot intersect by the actual loose
triple prohibition. At any such outer point outside the O support S,
there is no d1 or d3 root. Local degree two needs at least three d2
roots, so at least two are unattached. Choosing an unattached pair gives
an injection from these outside points into distinct intersection pairs.

For two unattached roots there is at most one such point; for three,
at most two, since three distinct pair labels would make a forbidden
nonconcurrent actual triple. For four, at most four: five distinct pair
labels contain a diamond, whose two actual triangle triples force all
four roots to concur, contradicting those distinct labels. These are
actual pair-intersection counts, not unproved defect-edge classifications.

An attached root at a bad point has center weight one and contributes
at least0,1,3 to H when0,1,2 outer points are in S. An attached root at
a good point has center weight two and contributes at least0,2,5.
All these are nonselected actual edges, distinct across roots by lambda1.

## h0, h2 and h3 are impossible

At h0, K>=6 and ell>=3 give q<=28-30-6=-8.
At h3, six attached roots and one unattached root leave no possible
outside outer point. All twelve outer points are in S, so H>=18,
and q<=28-36=-8.

At h2,g0, four attached and three unattached roots give eight outer points
of which at most two are outside. At least six are inside, so H>=8:
four partial roots would supply four incidences, and each additional
incidence increases the edge bound by two. The one good T point gives
K>=2. Thus q<=28-10-16=2. A larger K is at least four and would make
q negative, so K2 is forced: there is one peak w2 and every other w1.
At both bad T points the selected weighted neighbor sum is2+1+1+1=5,
and Y has baseline9-15+7=1. Their attached inner outer-neighbor increments
sum at least six. Consequently Y_p+Y_q<=2-3*6=-16 and
Y_p^2+Y_q^2>=128, whereas(3) gives ||Y||^2<=126. Contradiction.

At h2,g1, five attached and two unattached roots leave at most one of
the ten outer points outside S. If all are inside the edge bound is
4*3+5=17. Removing one outside incidence reduces this by at most three,
so H>=14, giving q<=28-10-28=-10. This covers all h2 profiles.

## h1 forces two peaks and the exact support baseline

There are two good T points, so K>=4 and ell>=1. A larger K is at least
six and gives q<0. Hence K4: exactly the two good T points have w2,
and all other support points have w1. Since sum w21, S has19 points,
two peaks and17 ordinary points. The only selected edge joining the two
peaks is their T edge, so ell1 and

    q=6-2H.                                         (4)

The two peaks each have eight selected neighbors, one of which is the
other peak. Their selected weighted neighbor sum is9 and their baseline
Y value is-2. At the bad T point the selected neighbor sum is2+2+1+1=6,
again giving baseline-2. The twelve other selected neighbors of the
peaks are distinct by lambda1 and have baseline1. The four remaining
ordinary support points have baseline4. Thus the exact selected baseline
has three values-2, twelve values1 and four values4:

    sum_S Y_baseline=22, ||Y_baseline||^2_S=88.       (5)

Let zeta count additional actual support edges incident to a peak. There
is no additional peak-peak edge, since that edge is already in T. Every
other additional edge joins ordinary points. Its weight is one, versus
two for a peak edge, so the total weighted neighbor increment on S is
2H-zeta. The sum of increments at the peaks is zeta.

For an integer increment k>=0 and baseline v<=4,
(v-3k)^2>=v^2-15k. At a peak v=-2 the sharper bound is
(v-3k)^2>=v^2+21k. Equations(5) therefore yield

    ||Y||^2_S>=88-30H+51zeta,
    sum_S Y=22-6H+3zeta.                            (6)

There are80 outside coordinates, each integer1 mod3. Such an integer
satisfies y^2+y-2>=0, with equality at1 and-2. Since sum Y=0,

    ||Y||^2_outside>=160+sum_S Y
                       =182-6H+3zeta.              (7)

Combining(3),(4),(6),(7) gives

    378-126H>=270-36H+54zeta,
    90H+54zeta<=108.                                (8)

Thus H<=1 and zeta0. No extra edge touches either peak, and any extra
ordinary edge has weight one. The arithmetic constant is270 and the
remaining allowance108; an unsealed intermediate addition was corrected
before this freeze. No weaker incorrect constant is used as evidence.

If H1 and its edge touched the bad T point p, p's baseline-2 changes
to-5, increasing its square by21; the other ordinary endpoint has
baseline at most4, reducing its square by at most15. Hence the inside
norm is at least94, and the inside sum is16. Equation(7) gives outside
norm at least176. The full norm would be at least270, whereas(3),(4)
give252. Thus no additional support edge touches p.

Any attached root with an outer point in S supplies such an additional
edge at its T point. Bad-center edges have just been excluded; good-center
edges have weight at least two, contradicting H<=1. All attached outer
points must therefore be outside S.

At g1 there are three attached and four unattached roots: six outside
outer points contradict the four-point pair budget. At g2 there are
four attached and three unattached roots: eight points contradict the
two-point budget. Hence g0. Only the two attached roots at the bad T
point remain, with four distinct outer points all outside S.

Their fourteen selected triangles have42 distinct edges. Since zeta0 and
H0/1, the actual induced support has exactly42 or43 edges, with any
additional edge ordinary and avoiding p. This proves every part of the
stated necessary profile without requiring any vertex class to have a
uniform exterior profile.

## Retained boundary and independent review

H0 and H1 remain possible under these necessary inequalities. The outside
residue norm budget does not by itself contradict them: y1/-2 give zero
residue excess, and larger residues can consume the allowed positive
budget. No actual target construction follows from that scalar observation.
The theorem retains arbitrary outside adjacency and covered intersections;
it derives the support incidence and extra-edge bound rather than assuming
selected inducedness. Fan, parity, Gram and residue methods overlap earlier
work, without an archive-novelty claim. A different full written review
must bind this exact statement before VERIFIED or ledger use. R226 and
the target remain unresolved, and no execution or publication change
is claimed.
