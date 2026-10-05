# Candidate: the five-d2 branch cannot have one fourfold selected point and two outside points

This separate conditional exclusion is Root's pointwise weighted-neighbor
outline, reconstructed and challenged here by Structural. The selected-edge
weights, ordinary degrees, integer increments and two outside-neighbor sets
are distinguished explicitly. Native separately obtained a narrower leaf-root
boundary at weighted edge sum56; that shared comparison is not independent
verification of this larger claim. All earlier frozen papers remain unchanged.
No mathematical program, solver, enumeration, import or worker ran.

## Exact statement

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once by their vertex sets, and put d_T=6-r_T for each actual
triangle. Suppose R=227, every d_T belongs to {0,1,2}, and exactly five actual
triangles have deficiency two. Let S be the vertices used by the deficiency-one
triangles. It is impossible that exactly one S vertex lies in four of those
triangles, every other S vertex lies in exactly two of them, and exactly two
outside-S vertices lie in deficiency-two triangles.

The selected multiplicities and number of outside points are literal
hypotheses. This claim does not alone exclude all b5 or R227. It does not
assume a uniform neighbor profile, an equitable partition, an automorphism,
an induced selected-support graph or realizability of any scalar pattern.

## Triangle geometry and the two outside vertices

The target has231 actual triangles, seven through each point, and exactly one
triangle through each edge. Distinct triangles meet at most once. Three actual
triangles cannot meet pairwise at three distinct points: those three points
would make an actual edge have two triangle partners. These observations
retain arbitrary additional actual edges.

The usual local deficiency graph at a point has degree d_T at each triangle T:
its seven incident triangles have six possible partners, and each induced rook
containing T covers one distinct partner. Two intersecting actual triangles
determine at most one induced rook, by their fixed cross-pair second common
neighbors. An external positive triangle meets at most one outer point of an
entire positive fan. Thus a point with r_1 incident d1 and r_2 incident d2
triangles requires P>=3r_1+5r_2 distinct positive triangles.

The total deficiency is6(231-R)=24. Hence b5 gives fourteen d1 triangles
and P=19. At an outside-S point only d2 triangles can have positive
deficiency. A degree-two local vertex needs at least three incident d2 roots,
whereas19>=5r_2 allows at most three. Therefore each of the stated two
outside points p,q lies on exactly three d2 triangles. Their two sets of
three roots must share one root because only five roots exist. They cannot
share two roots by triangle linearity. All five d2 roots are used, and have
the form

    {p,q,u}, {p,x1,x2}, {p,x3,x4},
             {q,y1,y2}, {q,y3,y4},

with all displayed u,x_i,y_i in S. Within each p or q fan these five S
neighbors are distinct. Also p and q are adjacent, and their unique common
neighbor is u, by lambda1. In particular every other neighbor of p is
disjoint from every other neighbor of q.

## Weighted selected support and exact Gram identities

Write f for the single selected fourfold point and let w be half the d1 point
incidence. Then w_f=2, w_v=1 on the other S vertices, and w=0 outside S.
The42 selected point incidences give

    |S|=20,  sum w=21,  ||w||^2=23.

The fourteen selected triangles give42 distinct edges. At f four selected
triangles give eight distinct selected neighbors. Each other S point is in
two selected triangles and has four selected neighbors. The eight selected
neighbors of f have selected weighted neighbor sum5; the other eleven S
points have selected weighted neighbor sum4. At f that sum is8.
The actual weighted internal edge sum is

    E=sum_{v<t,A_vt=1} w_v*w_t=54+z, z>=0.       (1)

Indeed the selected weighted edge sum is42+8=50. The four d2 leaf-root
internal edges are distinct from all selected edges and each other, and have
positive integer weights. They supply at least4. All additional actual
edges remain in E; no edge is discarded because it is inconvenient.

Use the complete target matrix

    Q=3I-A+J/9, Q^2=7Q, Qj=0, AQ=-4Q.

It is PSD from the target spectrum14,3,-4. Put Y=3Qw=9w-3Aw+7j.
Then Y is an ordinary integer vector, every coordinate is1mod3, sumY=0,
AY=-4Y, and

    w^TQw=118-2E=10-2z,
    ||Y||^2=63(10-2z)=630-126z.                 (2)

This uses the correct factor63. Neither an unreviewed factor-nine outline
nor a transferred gate supplies (2).

## Internal increments, including the peak's ordinary degree

Let d=deg_S(f)-8>=0. Because every other S weight is1, this is exactly
the weighted-neighbor increment at f. At any S point define K_v>=0 to be
the actual weighted-neighbor increment beyond its selected-edge baseline.
Write B_v=1 at f and its eight selected neighbors, and B_v=4 at the other
eleven selected vertices. Then

    Y_v=B_v-3K_v,  K_f=d.

Summing weighted neighbors over S counts each ordinary non-peak edge twice,
and each peak edge with weight3 rather than twice its edge weight2. Hence

    sum_S Aw=2E-deg_S(f),
    sum_S K_v=2(E-50)-d=8+2z-d.                 (3)

The selected baseline is sum_S Aw=92=2*50-8. For integer K>=0,
(1-3K)^2>=1+3K and (4-3K)^2>=16-15K.
Using -15K on every point, with an extra18d at f, is a valid lower bound;
the other eight baseline-one points can only strengthen it. Consequently

    sum_S Y_v=29-6z+3d,
    sum_S Y_v^2>=185-15(8+2z-d)+18d
                    =65-30z+33d.              (4)

No negative increments, averaged vertex profiles or copied type partition
are hidden in this summation.

## The remaining77 entries have residue excess at most270

Let the weighted S-neighbor sums of p,q be5+a,5+b respectively, with
a,b>=0. Each has five known S neighbors of weight at least1; a or b also
includes a possible peak weight and every additional actual S neighbor.
Their Y values are

    Y_p=-8-3a, Y_q=-8-3b.

The remaining77 outside entries have sum -13+6z-3d+3(a+b).
Combining (2),(4) and the two displayed squares gives their norm at most

    437-96z-33d-48(a+b)-9(a^2+b^2).

For these77 entries define Delta=sum(Y_v^2+Y_v-2). Every summand is
nonnegative: y=1+3t gives y^2+y-2=9t(t+1)>=0 for integer t. Therefore

    Delta<=270-90z-36d-45(a+b)-9(a^2+b^2)
          <=270.                               (5)

The count77 is99 minus20 support points minus p and q.

## Each outside fan needs at least144 excess on disjoint vertices

Every S value is at most4 by its selected baseline and nonnegative
increments. At each leaf-root endpoint x_i or y_i, that root's internal
S edge contributes at least one weighted increment beyond its selected
edges. Such an edge cannot be a selected d1 edge by unique triangle
partners. Hence each of these four endpoints has Y<=1. This remains true
if an endpoint is f or is already a selected neighbor of f.
The shared endpoint u has Y<=4.

Let alpha be the number of other ordinary S neighbors of p. Since their
weights are at least1 and the known five S-neighbor weights sum at least5,
alpha<=a. Its S-neighbor Y sum is at most8+4alpha. Equation AY=-4Y at p
requires sum over all its neighbors32+12a. After removing those S neighbors
and the outside neighbor q, its remaining outside-neighbor subset has

    m_p=8-alpha<=8,
    B_p>=32+12a-(8+4alpha)-(-8-3b)
         =32+12a-4alpha+3b>=32.                (6)

If m_p=0, (6) is already impossible. Otherwise ordinary Cauchy gives

    Delta_p>=B_p^2/m_p+B_p-2m_p
           >=32^2/8+32-16=144.                 (7)

The same calculation at q gives Delta_q>=144, using its own number of
additional ordinary S neighbors and b. These two subsets are contained
in the same remaining77 entries and are disjoint: a common point would
be a second common neighbor of the adjacent actual vertices p,q, besides
u. Therefore Delta>=Delta_p+Delta_q>=288, contradicting (5).

This proves the exact fourfold/two-outside-point boundary exclusion.

## Falsification controls, overlap and limits

Eight abstract values4 have sum32 and residue excess144. Thus the scalar
bound in (7) cannot be strengthened just by claiming nonuniformity; the
contradiction genuinely uses two disjoint subsets and budget270.

The ordinary count alpha is not set equal to weighted increment a. If the
peak belongs to the known fan, its extra weight is included in a and only
strengthens alpha<=a. If it is an additional S neighbor, its weight2 again
strengthens that inequality. The peak can be u, an x_i, a y_i, or another S
point without changing any bound.

The two outside points are adjacent because their root families share an
actual triangle, not because a type pair mask is assumed. The disjointness
uses exactly lambda1; no global triangle-free defect-graph assertion is made.

The sumK identity includes every extra actual edge and counts peak edges
once through the explicit correction deg_S(f). An abstract baseline weighted
graph with E50 and degree8 at f has sumK0, providing the constant check92.

This statement is narrower than excluding b5. It does not cover a support
with no fourfold point, a different outside count, or R227 as a whole.
Previous necessary conditions and Native's narrower E56 leaf refinement
remain comparison evidence. This new CANDIDATE awaits distinct written
verification and remains outside the frozen publication cutoff.
