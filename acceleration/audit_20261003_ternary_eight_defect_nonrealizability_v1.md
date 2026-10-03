# Independent written derivation: eight ternary defects

Verifier: `/root/checkpoint_audit`. Producer: `/root`. This is a written
mathematical audit of frozen candidate fc885e399684ed41e1dba848474a19a392b5becddc27420769a5011d7570ecba.
No mathematical program, graph construction or executable fixture was run.

Exact statement: For every symmetric binary 99 by 99 matrix A with zero
diagonal and exactly 14 ones in each row, if F3 is the number of unordered
pairs u<v for which r_uv=(A^2)_uv+A_uv-2 is nonzero modulo3, then F3 is not8.
This excludes only this defect count; it does not exclude F3=0 or resolve the
target. No lambda, triangle, prism or automorphism premise is used.

The sole imported result is
C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-RESTRICTION r1,
uses_result, binding562676e3af281e33384265824f9e115dfce27cca498b94f3b46cd0100346edd3.
Its scope is the entire nonempty connected residual support with at most12
vertices and maximum degree3. I previously verified that result; this shared
verifier/component is disclosed. It is used only after whole-support
connectedness is established. The lower45/spanning99 results are not used.

## Identities and a separate boundary lemma

Set D=A^2+A-12I-2J over the integers, and M=D modulo3. Regularity implies
AJ=JA=14J, hence AD=DA. The diagonal of D is14-12-2=0. For a row, the
off-diagonal sum is(14^2-14)+14-2*98=0. Thus M is symmetric with zero
diagonal and zero row sums. Write H for its nonzero off-diagonal support and
S for every vertex incident to H. Under F3=8, H has exactly8 edges and
degree sum16. Each nonisolated degree is at least2 because a single nonzero
entry cannot have row sum0 modulo3. At degree2 the two labels are opposite;
at degree3 they are equal. These assertions enumerate the two possible
nonzero field labels1,-1, not graph realizations.

For z outside S, M's column z is zero. Commutation gives
0=(AM)_uz=(MA)_uz=sum_v M_uv A_vz. A degree2 row therefore equates its two
neighbors' binary adjacency entries at z. A degree3 row equates all three:
their sum is divisible by3 precisely when all are0 or all are1. No such
inference is made from a degree4 row, which can have two labels of each sign.

If u,v are H-nonadjacent and forced to have the same outside adjacency,
let m=|S|. Each has at least14-(m-1)=15-m neighbors outside S. Their common
neighbor count is therefore at least15-m and their integer residual is at
least13-m. As an H-good pair, its residual is divisible by3, so
r_uv>=3*ceil((13-m)/3). Every good residual is nonnegative: its possible
integer lower bound is-2, so a multiple of3 cannot be negative. Every bad
residual is at least-2. A row u consequently has total good residual at most
2*deg_H(u). For m<=6 a forced good pair gives at least9, impossible at an
endpoint of degree<=4. For m=7 or8 it gives at least6, impossible at a
degree2 endpoint. This lemma uses no assumption about A inside S; a possible
A_uv=1 or extra internal common neighbors only increases the lower bound.

## Complete support reduction

A connected component has at least3 edges by simplicity and minimum
degree2. The only3-edge possibility is C3, whose degree2 equations require
alternating signs around an odd cycle and are inconsistent. Therefore every
component has at least4 edges. If H is disconnected, it has exactly two
4-edge components, each C4. Opposite vertices on a C4 have identical
outside adjacency by its degree2 rows and are a good degree2 pair. Here
m=8, so the boundary lemma contradicts6>4. Thus the entire H is connected.

Its vertex count is5<=m<=8 (four vertices have at most6 edges). A subcubic
whole support is excluded by the sole imported restriction, since m<=8.
For the remainder, minimum degree2 and sum16 exhaust the possibilities:
m=7 has(4,2,2,2,2,2,2); m=6 has(5,3,2,2,2,2),
(4,4,2,2,2,2) or(4,3,3,2,2,2); m=5 is K5 with two missing edges.
At m=8 all degrees2. A degree>=5 at m=7, or any unlisted excess at m=6,
would exceed the available excess16-2m; m=5 follows the literal complement
of two edges. No numerical support enumeration is required.

### Five vertices: the two complementary two-edge shapes

If the missing edges are disjoint, four vertices have degree3 and the fifth
degree4. The four degree3 rows are linked by their common existing edges,
forcing all8 nonzero labels equal t. The last row then sums to4t=t, a
contradiction. If they meet at a, a has degree2, b,c degree3 and d,e degree4.
The b,c rows force bc,bd,be,cd,ce=t. Write ad=s,ae=-s,de=q. The d,e sums
are s+2t+q and -s+2t+q. Their difference2s cannot vanish. These exhaust
two-edge simple complements, irrespective of the actual A adjacencies.

### Seven vertices: connected all-even support

The single degree4 vertex a is joined to two cycles sharing only a. To see
this without assuming a particular drawing, deleting a leaves four degree1
endpoints and degree2 interior vertices. Connectivity excludes a detached
cycle, so the remainder is exactly two paths; each closes through a. The
cycle lengths are at least3 and sum8, leaving(3,5) and(4,4).
For(3,5), the degree2 rows on the triangle force all three boundary entries
equal. On the5-cycle a-d-e-f-g-a they give a=e, d=f, e=g, f=a, forcing all
five equal. All seven entries thus agree, and any degree2 vertex has a good
twin pair. For(4,4), the two neighbors b,d of a on one cycle a-b-c-d-a are
equated by row c and are H-nonadjacent degree2 vertices. Both cases violate
the m=7 lower6 versus rowbudget4. No degree4 propagation was used.

### Six vertices with a universal high vertex

For(5,3,2,2,2,2), deleting universal a gives degrees(2,1,1,1,1), hence P3
plus K2. Write P3 as c-b-d and K2 as e-f. Row b equates a,c,d; rows c,d
equate a,b; rows e,f equate a,f and a,e. All six outside adjacency entries
are equal, yielding a good degree2 pair and contradiction9>4.

### Six vertices with two degree4 vertices

Call them a,b. If H-nonadjacent, both join all four lows: H=K2,4. Every
low row equates a,b; the good high pair violates9>8. If adjacent, they each
miss one low. They cannot miss the same x: x would require two low neighbors
while each other low has exhausted its degree on a,b. If a misses x and b
misses y, the low graph is exactly edge xy. The support is
ab,ay,az,aw,bx,bz,bw,xy. Low rows give b=y, a=x and a=b. Therefore the
H-good pair a,x is forced equal, and endpoint x has degree2:9>4.

### Six vertices with degrees4,3,3,2,2,2

Let a have degree4, b,c degree3 and d,e,f degree2. The unique H-nonneighbor
of a is either a high vertex or a low vertex.

If it is c, H-a has degrees(3,2,1,1,1). A connected5-vertex4-edge graph
with these degrees is the tree with edges cb,cd,ce,bf. It cannot be
disconnected: the only cycle at four edges with no isolated vertex would be
C3 plus K2, whose degrees differ. Rows b,c force ba,bf,bc,cd,ce=t. Low rows
give ad=ae=af=-t, so row a sums to t-3t=-2t!=0.

If the nonneighbor is f, H-a has degrees(2,2,2,1,1). Its components are P5
or C3+P2: a connected version is the path; otherwise a cycle must use the
three degree2 vertices and the remaining degree1 pair is an edge. P5 has
endpoints d,e; exchanging b,c and reversing the path leaves two positions
for f. If f is central, d-b-f-c-e, rows b,c give a=d=f=e, row f gives b=c,
and row d gives a=b. All six entries agree, contradicting9>4. If f is next
to an endpoint, d-f-b-c-e, rows b,c give ab=bf=bc=ac=ce=t. Rows f,d,e then
give df=-t,ad=t,ae=-t, so row a sums to2t!=0. In C3+P2, the triangle is
b,c,f; rows b,c force bf=cf=t, inconsistent with row f's degree2 sum2t.

This exhausts all cases and proves the exact claim F3!=8.

## Written falsification boundaries and disclosure

Fourteen written checks were considered: twoC4; disjoint-missing-edge K5;
shared-missing-edge K5; cycles3+5; cycles4+4; universal5 P3+K2; K2,4;
adjacent degree4 pair; the high-nonneighbor tree; low-nonneighbor P5 central;
low-nonneighbor P5 near-end; C3+P2; the whole-support subcubic branch; and a
balanced degree4 row which by itself does not imply equality. The last is
an explicit guard against an invalid strengthening, not an excluded modular
support. These are paper deductions, zero executed fixtures and zero actual
graph realizations. The proof distinguishes H support edges from binary A
edges throughout and applies the imported theorem only to the entire
connected H. Disconnected support was excluded by the fresh boundary lemma.

No formal prover, external human review, peer review, novelty audit, F3=9
exclusion or target-resolution claim is made. Candidate bytes remain
unchanged; a failed future scrutiny must produce a new record rather than
rewrite this evidence. Checkpoint's ordinary metadata/registrar authorship is
separate from this independent mathematical review of ROOT's discovery.
