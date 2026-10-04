# Candidate: the ordinary-support five-d2 branch cannot have one outside point

This separate written exclusion strengthens only one branch of the previous
weighted-support candidate. Structural and Root separately obtained its
outside-neighbor eigenvector norm obstruction; Root supplied the remaining-
vector delta form, which is independently reconstructed below. Agreement is
not independent verification. No mathematical program, enumeration, import,
backend or worker ran. All previous candidates remain unchanged.

## Exact statement

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once by their vertex sets and put d_T=6-r_T for each actual
triangle. Suppose R=227, every d_T belongs to {0,1,2}, and exactly five actual
triangles have deficiency two. Suppose further that every vertex used by
the deficiency-one triangles lies in exactly two of them. Let S be that
selected vertex support. It is impossible that exactly one outside-S vertex
lies in any deficiency-two triangle.

The selected multiplicity-two condition and one-outside-point boundary are
explicit hypotheses, not inherited from the unreviewed weighted-support
descendant. The claim does not exclude the two-outside-point branch, the
fourfold-support branch, b5 or R227. No automorphism, equitable partition,
uniform profile or induced selected-support assumption is used.

## Exact target geometry and the boundary counts

There are231 actual triangles, each point lies in seven, and each edge
belongs to exactly one. Distinct actual triangles meet at most once. Three
cannot meet pairwise at three distinct points: those three points would
give one edge a second triangle partner.

Two intersecting triangles determine at most one induced rook, via their
four cross pairs' fixed second common neighbors. The local defect graph
at a point therefore has degree d_T at its triangle T: every rook containing
T supplies one distinct covered partner there. The positive fan injection
gives P>=3r_1+5r_2, since an external positive triangle can meet at most
one outer point of the entire fan, by the preceding geometric facts.

The global deficiency sum is6(231-R)=24. At the stated b5 boundary there
are fourteen d1 triangles and P=19 positive triangles. Their multiplicity-
two support has21 actual vertices and42 distinct known edges. Each S point
has four distinct neighbors in S supplied by its two d1 triangles.

Write p for the sole outside-S point on any d2 triangle. Degree two in
its local defect graph requires at least three incident d2 roots, and
P19>=5r_2 permits at most three. Thus exactly three d2 triangles pass
through p. Each has its other two vertices in S, and these six points
are distinct by linearity. The other two d2 triangles are wholly inside S.
Their nine internal edges are distinct from the42 d1 edges and each other
by unique actual triangle partners. Consequently

    e(S)=51+z,  z>=0.

All additional actual edges are included in z. They are never deleted to
make a proposed support induced.

## Correctly scaled target eigenvector and internal norm

The target matrix Q=3I-A+J/9 is positive semidefinite, Q^2=7Q and Qj=0,
from A^2+A=12I+2J and row sum14. Put Y=3Qchi_S. Then Y is an ordinary
integer vector of sum zero; every coordinate is1 modulo3:

    Y_v=16-3deg_S(v) inside S,
    Y_v=7-3deg_S(v) outside S,
    AY=-4Y,  ||Y||^2=630-126z.                  (1)

The factor3 is essential: ||3Qchi||^2=9*7*chi^TQchi, with
chi^TQchi=112-2e(S). No rejected factor-nine outline is used.

For v in S let k_v=deg_S(v)-4, a nonnegative integer increment beyond
the four known d1 neighbors. Then

    sum_S k_v=18+2z,  Y_v=4-3k_v,
    sum_S Y_v=30-6z.

The two wholly-S d2 triangles force sum_S k_v(k_v-1)>=12. If disjoint,
their six points each have k_v>=2. If they meet once, the shared point
has k_v>=4 and four other points have k_v>=2, giving at least20 instead.
No d2 edge can duplicate a d1 edge; extra actual edges cannot decrease
the increments. Direct expansion therefore gives

    sum_S Y_v^2>=174-30z.                       (2)

Let deg_S(p)=6+a. Its six known S neighbors show a>=0, and degree14
gives a<=8. Its value is Y_p=-11-3a. The other77 outside entries sum
-19+6z+3a. Combining (1),(2) with Y_p^2 gives their squared norm at most
335-96z-66a-9a^2.

For those77 entries define

    delta=sum (Y_v^2+Y_v-2).

Since an integer y=1+3t obeys y^2+y-2=9t(t+1)>=0, every summand is
nonnegative. The preceding exact sums give the upper bound

    delta<=162-90z-63a-9a^2<=162.               (3)

No degree range from the older weighted-support candidate is assumed.

## The eigenvector equation requires more delta on p's outside neighbors

The six S neighbors from the three d2 roots each have k_v>=1, due to
that root's additional internal edge, so each has Y_v<=1. The other a
neighbors in S, if any, each have Y_v<=4 since k_v>=0. Equation AY=-4Y
at p requires its neighbor sum to be44+12a. Hence its outside neighbors,
a subset of those77 remaining vertices, number m=8-a and have sum B with

    B>=44+12a-(6+4a)=38+8a.                    (4)

If a8, m0 yet (4) requires a positive sum, immediately impossible. If
a<=7, m is positive and at most8; B is at least38. Ordinary Cauchy gives
for this subset of m vertices

    sum (Y_v^2+Y_v-2)
      >=B^2/m+B-2m
      >=38^2/8+38-16=405/2.

Every other remaining entry contributes a nonnegative summand to delta.
Thus delta>=405/2>162, contradicting (3). This proves the exact boundary
exclusion with all actual shared endpoints and additional edges retained.

## Hand controls, overlap and limits

The six known S endpoints of the p fan are distinct because its three
actual triangles meet only at p. Two wholly-S d2 roots may intersect;
the bound includes that case and only becomes stronger. No extra S
neighbor of p is assumed to avoid those roots or any selected triangle.

For eight abstract residue-one integers with sum38, six values4 and two
values7 give norm194 and excess194+38-16=216. This is consistent with
the weaker Cauchy floor405/2; it is not a target construction. The gap to
162 is strict, and no equality or uniform neighbor profile is needed.

The scalar delta uses only outside neighbors of p, disjoint from S and
p itself. No internal increment is counted twice in its lower bound.
The ordinary eigenvector equation AY=-4Y is the essential new step:
global sum and norm inequalities alone left the earlier e51/52 cases.

The parity/fan/Q components and the earlier two-wholly-S increment bound
are disclosed shared ingredients. Their earlier verification does not
approve this new pointwise contradiction. All definitions are reconstructed
and the selected multiplicity-two and h1 conditions remain literal. This
CANDIDATE awaits a different author, lies outside the frozen publication
cutoff, and does not resolve b5, R227 or Conway99.
