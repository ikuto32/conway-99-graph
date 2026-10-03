# Independent written audit: connected small subcubic ternary support

Discovery producer: ROOT. Independent verifier: Checkpoint.
The unchanged source is
`docs/CANDIDATE_20261003_TERNARY_SUBCUBIC_CONNECTED_SUPPORT_V1.md`,
SHA256 2fb3397faabf4670d5c04f5d0e720effb53166aa89b6fe283e2425c275ca8a82.
This is exact written checking, not a computational or sampled-graph argument.
No mathematical command, executable fixture, enumeration or solver was run.

## Exact statement checked

For every 99-by-99 symmetric binary zero-diagonal matrix A with exactly 14 ones
in each integer row, let D=A^2+A-12I-2J and let H be the simple graph of all
nonzero unordered off-diagonal entries of D modulo 3, with isolated vertices
discarded. If H is nonempty and connected, then H cannot simultaneously have
at most 12 vertices and maximum degree at most 3. This is a necessary
residual-support restriction only; it makes no assertion about disconnected
supports, larger supports, support degree at least 4 or target existence.

No prior mathematical claim is used as a premise. All complete-row identities,
support sign rules, outside equations and parity propagation are reproduced
below. Connectivity refers to the whole nonisolated residual support H, not A
and not an arbitrarily chosen support component. H is not prescribed to be an
induced adjacency subgraph. No lambda1, incidence or automorphism is assumed.

## Reconstructed exact identities

Symmetry, binary entries and degree14 give (A^2)_uu=14, so D_uu=0.
For a complete row, sum_v(A^2)_uv=14*14=196. Therefore

 sum_[v!=u] ((A^2)_uv+A_uv-2)=(196-14)+14-2*98=0.

Let r_uv denote the off-diagonal residual. Since CN and adjacency are
nonnegative, r_uv>=-2. If r_uv vanishes modulo 3, this lower bound forces
r_uv>=0: no negative multiple of 3 is at least -2.

Exact regularity and symmetry give AJ=JA=14J. Expanding both AD and DA proves
AD=DA over the integers. Hence AM=MA in GF(3), where M=D modulo 3. Each
nonzero support edge has sign +1 or -1 and complete incident sum zero. A
nonisolated vertex has degree at least two; at degree two its labels are
opposite, and at degree three all three labels are equal. These rules follow
from the complete row congruence, not an assumed sign pattern.

Assume for contradiction that H is nonempty, connected, subcubic and has m<=12
nonisolated vertices S. Every support vertex consequently has degree two or
three. For any z outside S, the z-row of M is zero. The commutator equation
gives x*M[S,S]=0, with x_u=A_zu binary.

At a degree-two column j, whose neighbors are u,v, the equation is
s*x_u-s*x_v=0. It forces equality modulo 3, and binary entries force equality
over the integers. At a degree-three column the equation is
s*(x_u+x_v+x_w)=0. The literal binary sum is between zero and three, so it is
zero or three. Thus all three coordinates equal. In both cases, all support
neighbors of j have the same outside adjacency coordinate.

## Independent parity propagation

The preceding local equality identifies the endpoints of every length-two
walk in H. Successively applying it shows that endpoints of every even-length
walk have equal x coordinates. This statement concerns actual walks, which
may repeat vertices; it does not require an automorphism or a simple path.

If H is connected and bipartite, each walk changes bipartition side at every
step. Thus every same-side path has even length, and no even walk changes side.
The two bipartition sides are exactly the equality classes forced by these
length-two relations.

If H is connected and not bipartite, it contains an odd cycle. Starting at any
vertex u, follow a path to that cycle, traverse the cycle and reverse the path.
This gives an odd closed walk at u. For any vertex v, start with a connecting
u-v path. If it is odd, prefix this odd closed walk to make an even u-v walk;
if it is even, no prefix is needed. Every pair is therefore joined by an even
walk, so all coordinates are equal. This explicitly covers the parity step
rather than assuming all paths between a pair have a fixed parity.

Any two vertices in one such equality class share every outside neighbor.
Each support vertex has at most m-1 internal neighbors and exact total degree
14. Thus every such pair has at least 15-m common outside neighbors and

 r_uv>=13-m.

Internal adjacency among S is arbitrary; the bound already allows all m-1
internal neighbors. Coordinates and common-neighbor counts are complete
literal integers, not floating values or solely field residues.

## Row-budget contradictions

If H is not bipartite, all its vertices belong to one class. Every support
edge uv then has residual at least 13-m>=1. In each nonisolated row at least
two such strictly positive bad residuals occur. Every other residual is good
and nonnegative. The complete integer row sum is positive, contrary to zero.
This proof does not incorrectly declare bad residuals divisible by three.

If H is bipartite, minimum degree two and simplicity require both sides to
have at least two vertices, so m>=4. Choose a vertex u in a larger side P;
p=|P|>=ceil(m/2). All p-1 other vertices of P are good pairs with u and are
outside twins. Their residuals are nonnegative multiples of three, at least
q=3*ceil((13-m)/3). Row u has at most three bad pairs, each at least -2.
Every remaining good pair is nonnegative. Thus its complete sum is at least

 (p-1)*q-6 >= (ceil(m/2)-1)*q-6.

The positivity can be checked independently in three intervals, without
accepting a saved table as a certificate:

* For 4<=m<=6, q=9 and ceil(m/2)-1>=1, giving at least 3.
* For 7<=m<=9, q=6 and ceil(m/2)-1>=3, giving at least 12.
* For 10<=m<=12, q=3 and ceil(m/2)-1>=4, giving at least 6.

Every case is strictly positive. The nine individual source entries are also
checked by direct substitution:

| m | q | exact lower bound |
| --- | --- | --- |
| 4 | 9 | 3 |
| 5 | 9 | 12 |
| 6 | 9 | 12 |
| 7 | 6 | 12 |
| 8 | 6 | 12 |
| 9 | 6 | 18 |
| 10 | 3 | 6 |
| 11 | 3 | 9 |
| 12 | 3 | 9 |

Both connected cases contradict the complete zero row sum. The stated
necessary restriction follows.

## Written falsification inventory (12 checks, zero executed fixtures)

1. Recompute diagonal0 and complete integer row sum0 before modular reduction.
   Degree known only modulo3 or partial row sampling is insufficient.
2. Expand AD and DA separately; require both AJ and JA equal14J.
3. Exhaust degree-two/degree-three signs from complete row sums; no degree-one
   endpoint can survive. The column equations use the same undirected labels.
4. Check both nonzero signs and all degree-three binary sums0,1,2,3: only0/3
   vanish, forcing all coordinates equal. This would fail for weighted entries.
5. In a connected bipartite graph, every same-side path is even and every
   cross-side walk is odd; both sides, not one uniform profile, are retained.
6. An odd cycle yields an odd closed walk at any vertex via a path and its
   reverse; prefixing it flips the parity of a connecting walk. No omitted
   odd-cycle position or path-simple assumption remains.
7. Permit all m-1 internal neighbors when bounding common outside neighbors.
   No residual-support edge is assumed to be an adjacency edge.
8. For nonbipartite m<=12, each bad residual is at least1, while good residuals
   are nonnegative. At least two bad entries make the complete row positive.
9. Bipartite minimum degree two requires both sides of size at least two.
   A larger side exists by counting, without an automorphism or symmetry claim.
10. Allocate the worst -6 budget to three bad pairs and retain every other
    nonnegative good entry. All three grouped bounds and nine literal table
    entries are positive; none is an approximate numerical bound.
11. At support degree four, labels(+,+,-,-) have zero row sum and binary
    coordinates(1,0,1,0) satisfy the column equation without all being equal.
    This written boundary blocks reuse of the degree-three propagation rule.
12. Disconnected H does not give even-walk propagation between components;
    outside means outside the full S. At m=13 the general bound13-m is zero,
    so the strict-positive argument stops. Neither case is declared impossible.

## Verdict and limits

VERIFIED within the exact conditional necessary scope above. The independent
proof uses local binary equations, an explicit even-walk parity argument and
three grouped row-budget intervals, with nine handwritten substitutions.
There are twelve written falsification boundaries and no executable fixture
or graph realization. Agent agreement and finite graph agreement are not the
proof.

Definitions and elementary integer/GF(3) facts are shared with discovery. Prior
small-support/four-/six-defect proofs are context only; this derivation has no
prior mathematical dependency. It does not exclude disconnected supports,
support degree four or more, or support sizes above twelve, and does not
classify graph realizations in those open cases. No target graph or general
nonexistence conclusion, engine approval, formalization, novelty or external
review is claimed. Overall search coverage: UNKNOWN; no validated denominator.
