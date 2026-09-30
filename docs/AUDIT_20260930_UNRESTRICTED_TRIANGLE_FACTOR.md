# Independent universal triangle-factor review

Reviewed claim: C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION, revision 1.
The producer derivation is the separately authored
DERIVATION_20260930_UNRESTRICTED_TRIANGLE_FACTOR.md. The checking script imports
no producer or previous graph-construction code. Universal coverage follows
from the argument below; finite controls only check the implementation.

Let A be symmetric, binary and zero diagonal and satisfy the target identity.
Its diagonal gives degree 14. Its off-diagonal entries give one common
neighbour for an edge and two for a nonedge. Choose any edge; its unique
common neighbour supplies a triangle T. Every vertex outside T is adjacent
to at most one member of T, since each edge of T already has its unique
common neighbour inside T. Consequently the neighbours of the three root
vertices outside T are three disjoint sets Ai of size 12, and the remaining
60 vertices Y have no neighbour in T. This does not select a special kind
of triangle or assume anything about graph automorphisms.

For x in Ai, the common neighbours of x and its root ti lie exactly among
x's neighbours in Ai, so there is exactly one. The undirected Ai block is
therefore a perfect matching. For j different from i, x and tj are
nonadjacent; ti is one common neighbour, and their other common neighbours
are exactly x's neighbours in Aj. There is exactly one. Applying this at
both ends gives perfect matchings between every pair of fibres. Each x has
four neighbours in the 39-vertex core and ten in Y. The nonedge ti--y has
exactly two common neighbours, all in Ai. Hence each incidence column has
two entries in each fibre, and each y has six known neighbours and residual
degree eight.

List the six matching pairs in A0 and label their two endpoints consecutively.
This fixes M0 to xor1. Label A1 and A2 by their unique neighbours in A0.
These three independent coordinate choices make cross blocks 01 and 02
identities. The remaining two internal matchings are arbitrary fixed-point-free
involutions, and cross block 12 is an arbitrary permutation P, with row in A1
and column in A2. The reverse block is P transpose. These operations only
relabel the given target; no permutation is required to preserve its edges
while keeping the original labels. In particular P need not be symmetric,
fixed-point-free or commuting with either matching. No prism restriction is
introduced.

Each Y vertex specifies a two-subset of A0. A matched pair in A0 cannot occur:
it already has root t0 as its unique common neighbour. A nonmatched pair has
one common core neighbour, t0. Distinct matching neighbours within A0 and
the injective cross matchings prevent any other core common neighbour. Its
required second common neighbour is therefore exactly one member of Y.
Thus the 60 columns of C0 are exactly the 60 nonmatching two-subsets, without
repetition. Relabel Y by their lexicographic pair names. This is compatible
with all earlier coordinate choices and does not restrict the other two
incidence blocks.

For X=A0 union A1 union A2, its adjacency C is the stated 3 by 3 block matrix
with M0,M1,M2 on the diagonal, identity blocks 01 and 02, P in block 12 and
P transpose in block 21. A vertex in X has one root neighbour; root-neighbour
contributions to X-by-X common counts are RR transpose, the three diagonal
all-ones blocks. The exact X-by-X identity therefore yields

    FF transpose = 12I - C - C squared + 2J - RR transpose.

The diagonal blocks of C squared are 3I. The off-diagonal blocks 01,02,12
are respectively M0+M1+P transpose, M0+M2+P, and I+M1 P+P M2. Subtracting
C gives exactly the producer's four displayed Gram formulas, including
the P transpose in G01 and P in G02. Symmetry gives the reverse blocks.
This multiplication uses only matching/permutation types; it never swaps
noncommuting products. The audit checks the formulas independently against
literal common-neighbour counts in a reconstructed 39-vertex graph.

For x in X and y in Y, the currently known common neighbours are exactly
(CF)[x,y]. The required total plus the known adjacency F[x,y] is two, so
(I+C)F<=2J is necessary. Two distinct Y vertices have known common neighbours
(F transpose F)[y,z], so this is at most two. If their eventual residual
edge is present the stronger cap is one; intersection two consequently
forces that edge absent. No implication from abstract Gram to these extra
inequalities is asserted.

Conversely, binary F and matching/permutation data satisfying these margins,
Gram equations and two kinds of inequalities define the stated partial
99-vertex graph, with every Y--Y off-diagonal entry unknown. The fixed T--T
and T--X counts follow from the matching structure. T--Y counts are the
fibre-column margins. X--X counts are the Gram identity. The remaining known
X--Y and Y--Y counts satisfy their caps by the two inequalities. Degrees of
T and X are already 14; Y has known degree six. This converse establishes
a consistent partial specification only. There is no assertion that an
appropriate residual D exists. If such a symmetric binary zero-diagonal D
is provided, the remaining block equations are precisely

    FD = 2J - F - CF,
    D squared + F transpose F = 12I - D + 2J.

In particular no SAT instance omitting D may treat a factor as a solution.

The independent controls check all 216 combinations of two arbitrary
matchings and one permutation on four coordinates, all 12 saved arbitrary
twelve-coordinate cores (including nonsymmetric permutations), all saved
nonempty C0 relabelling records, and all 12 saved rook9 positive controls.
The rook9 residual set is empty; it is not a positive nonempty99 factor.
Fresh random binary incidence fixtures exercise literal mixed/outside
known-common-neighbour formulas only and are not claimed feasible factors.
Corrupted graphs, coordinates, column bijections and transposes are rejected.

Archive Wave149 already contains the general partition and Gram mechanism;
Wave151 contains the incidence-pair mechanism in its fixed-factor context.
The immutable references are authenticated, but this audit does not inherit
historical verification labels or assert novelty. The universal theorem
is necessary coverage, not a target existence or nonexistence result.
