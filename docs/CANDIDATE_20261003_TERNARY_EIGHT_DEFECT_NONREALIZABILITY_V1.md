# Eight ternary defects are impossible: candidate argument

Prepared by `/root`, 2026-10-03T05:58:00+00:00. SOURCE_ONLY mathematical
argument, CANDIDATE pending a different author's independent derivation.
No computational enumeration, graph construction, or external review is claimed.

## Exact statement and dependency

For every symmetric binary 99 by 99 matrix A with zero diagonal and exactly
14 ones in each row, let F3 count the unordered pairs whose integer residual
r_uv = (A^2)_uv + A_uv - 2 is nonzero modulo 3. Then F3 is not 8.
This statement alone neither excludes F3=0 nor asserts realizability of any
other defect count. It assumes no triangle decomposition or automorphism.

The sole used result is the independently written and checked connected
subcubic support restriction: a nonempty connected whole residual support
cannot have both at most 12 vertices and maximum degree at most 3.
Its intended claim is
`C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-RESTRICTION r1`,
relation `uses_result`; registration is pending at preparation time.
Its binding is
`acceleration/results/20261003_independent_review/ternary_subcubic_connected_support01/claim_binding_schema2.json`,
SHA256 `562676e3af281e33384265824f9e115dfce27cca498b94f3b46cd0100346edd3`.
This uses the exact whole-connected-support theorem, not a component-wise
extension of it.

## A binary boundary obstruction

Let D be A^2+A-12I-2J reduced modulo 3 and H its nonzero off-diagonal support.
Then D is symmetric, its diagonal and row sums are zero, and AD=DA.
The last assertion follows over the integers from regularity AJ=JA=14J.
At a degree-2 vertex of H its two incident nonzero labels are opposite; at
a degree-3 vertex all three labels are equal. Labels are represented by +1,-1.
Every vertex of H has degree at least 2.

Write S for all vertices incident to H, m=|S|. For any z outside S, D's row z
is zero, hence every row u in S obeys sum_v D_uv A_vz=0. A degree-2 row forces
its two neighbors to have equal binary adjacency to z. A degree-3 row forces
all three neighbors to have equal adjacency to z: the sum of three binary
entries is 0 modulo 3 precisely when they are all 0 or all 1.

Suppose distinct u,v in S are not joined in H and these equations force
A_uz=A_vz for every z outside S. They have at least 15-m common neighbors
outside S, since each has at most m-1 neighbors in S and total degree 14.
Thus their good residual r_uv, a nonnegative multiple of 3, is at least
3 ceil((13-m)/3). In row u the sum of all residuals is zero. Every bad
residual is at least -2 and every good residual is nonnegative, so the sum
of good residuals in that row is at most 2 deg_H(u).
Consequently such a good forced twin pair is impossible when
3 ceil((13-m)/3) > 2 deg_H(u).
For m<=6 the left side is at least 9, excluding degrees at most 4;
for m<=8 it is at least 6, excluding degree 2.

## Complete eight-edge reduction

Assume F3=8. Each nonempty component of H has at least four edges: minimum
degree is 2, and the only three-edge possibility is a triangle, whose
alternating nonzero labels violate a degree-2 row. Therefore a disconnected
H consists of two four-cycles. In either cycle the opposite vertices form
a good forced twin pair of degree 2. Here m=8, contradicting the boundary
obstruction. Hence H is connected.

Now 5<=m<=8. If H is subcubic, the pinned whole-support theorem excludes it.
For a non-subcubic H the degree sum is 16. At m=7 its degree sequence is
(4,2,2,2,2,2,2); at m=6 the only possibilities are
(5,3,2,2,2,2), (4,4,2,2,2,2), and (4,3,3,2,2,2).
At m=5, H is K5 with two edges removed. These cases exhaust all possibilities:
minimum degree 2 gives the degree-excess total 16-2m, and simplicity bounds
each degree by m-1. At m=8 all degrees are 2, already excluded as subcubic.

### Five vertices

If the two missing edges are disjoint, the four degree-3 vertices force all
eight labels equal; the degree-4 vertex would then have sum 4t, nonzero
modulo 3. If the missing edges share vertex a, its degree is 2. Call its
neighbors d,e; the two remaining vertices b,c have degree 3. Their shared
edge forces the five labels bc,bd,be,cd,ce equal to t. Put ad=s, ae=-s,
de=q. The d,e rows respectively give s+2t+q=0 and -s+2t+q=0. Subtracting
forces 2s=0, impossible for a nonzero label.

### Seven vertices

The unique degree-4 vertex a is the common vertex of two cycles; all other
vertices have degree 2. To justify this classification, H has no bridge:
the number of edges crossing any cut is even because every degree is even.
Removing a leaves two paths, each with two of its four former neighbors as
endpoints, and no detached cycle because H is connected. The two cycle
lengths are at least 3 and add to 8, hence are (3,5) or (4,4).
For (3,5), the degree-2 equations along each odd cycle force all its binary
boundary entries equal, including a; hence all seven vertices are forced
twins. A degree-2 vertex has a good pair among the six other vertices,
contradicting the boundary bound 6>4. For (4,4), the two vertices next to
a on either four-cycle are a degree-2 good forced twin pair, with the same
contradiction. No degree-4 binary propagation rule is assumed.

### Six vertices: degrees (5,3,2,2,2,2)

The degree-5 vertex a is universal. Removing it leaves degree sequence
(2,1,1,1,1), so the remaining graph is P3 plus K2. Let b be the P3 center,
c,d its leaves, and e,f the K2. The degree-3 row b forces equal binary
entries at a,c,d; the degree-2 rows c,d force a=b, and rows e,f force
a=f and a=e, respectively. Thus all six boundary entries are equal.
Any degree-2 vertex has a good forced twin pair, contradicting 9>4.

### Six vertices: degrees (4,4,2,2,2,2)

Call the high vertices a,b. If they are nonadjacent in H, then H is K2,4:
each high vertex is joined to all four low vertices. Every low row forces
a=b. This high-vertex pair is good and forced, contradicting 9>8.

If a,b are adjacent, each misses one low vertex. The missed vertices must
be different: if both miss x, the complement induced on the four low
vertices would have degrees (1,3,3,3), which is impossible. Call their
respective missed vertices x,y, and the remaining lows z,w. The low induced
complement has degrees (2,2,3,3), so is K4 minus xy. Thus H has exactly
ab, ay, az, aw, bx, bz, bw, xy.
The degree-2 rows x,y,z,w respectively force b=y, a=x, a=b, a=b.
Hence a,b,x,y have equal binary boundary entries. The good pair a,x has
endpoint x of degree 2, contradicting 9>4. This does not assume the two
degree-4 rows themselves force binary equality.

### Six vertices: degrees (4,3,3,2,2,2)

Let a have degree 4, b,c degree 3, and d,e,f degree 2. Its one nonneighbor
is either high or low.

If its nonneighbor is c, H-a has degrees (3,2,1,1,1). It must be the
five-vertex tree whose degree-3 center c is joined to b and two leaves d,e,
while b is joined to leaf f. Indeed a disconnected five-vertex four-edge
graph with these degrees cannot exist: the only cycle possibility would
be a triangle plus one edge, giving different degrees.
The degree-3 rows b,c make bc,cd,ce,bf,ba equal to t. Degree-2 rows d,e,f
make ad,ae,af equal to -t. The a row is t-3t=-2t, nonzero modulo 3.

If its nonneighbor is f, H-a has degrees (2,2,2,1,1); it is P5 or C3+P2.
The path endpoints are d,e and its internal vertices are b,c,f. If f is
the middle vertex, the path is d-b-f-c-e. The degree-3 rows b,c force
a=d=f=e, while row f forces b=c and row d forces a=b. All six boundary
entries are equal, so a degree-2 good twin pair contradicts 9>4.
If f is next to an endpoint, relabel the path d-f-b-c-e. The degree-3 rows
b,c force ab,bf,bc,ac,ce equal to t. The degree-2 rows f,d,e force df=-t,
ad=t, ae=-t; the a row is 2t, nonzero modulo 3.
Finally in C3+P2 the triangle is b,c,f. The b,c rows force bf=cf=t,
contradicting the degree-2 row f. This completes the classification.

Every eight-edge support is excluded. The proposed conclusion is F3!=8.

## Verification requirements and limits

A verifier should independently enumerate the degree cases and five-vertex
residual graphs, test both binary-forcing and signed-row steps, and scrutinize
the whole-support/component distinction. No producer code or floating-point
result is evidence. Failure cases include a degree-4 balanced row on its own,
which does not force its four binary entries equal. The proof uses only
degree-2/3 equality rows and the specific listed graphs.

No claim is made about F3=9, a general nonzero defect lower bound without its
other pinned premises, novelty, formal proof, graph realizability, or
nonexistence of srg(99,14,1,2). The original candidate bytes must be retained
if any error is found; a correction requires a new version and fresh review.
