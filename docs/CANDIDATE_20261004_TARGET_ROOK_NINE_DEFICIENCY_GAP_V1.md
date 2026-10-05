# Candidate: the induced-rook count cannot be 230

This is a written, source-only necessary condition. No graph enumeration,
matrix calculation, code import or scientific command was executed. The
statement remains CANDIDATE pending a different-author written audit. It
does not exclude the count231 or a Conway99 graph.

## Exact statement and counting convention

For every complete finite simple SRG(99,14,1,2), let R count its actual
nine-vertex subsets whose induced graph is the3-by-3 rook graph. Count each
subset once, without counting embeddings, automorphisms or disjoint packings.
Then

    0 <= R <=231,   R !=230.

More precisely, write T for the full family of231 actual triangles. For a
triangle T, let r_T be the number of induced rook-nine subsets containing T
and d_T=6-r_T. At each graph point v there is a simple graph D_v on its seven
incident actual triangles: two triangle nodes are joined exactly when they
are not together contained in an induced rook-nine. These graphs necessarily
satisfy

    deg_(D_v)(T)=d_T for every v in T,
    0 <= d_T <=6,
    sum_T d_T=6*(231-R).

Thus the same triangle deficiency occurs at all three of its points; this is
an exact counting identity, not a uniformity or equitable-partition assumption.
The set of triangles with odd deficiency has even incidence at every point.
These local degree constraints are available as necessary screens on any
future explicitly defined rook/triangle incidence candidate. No such candidate
or screen has been computed here.

## Actual triangles and unique reconstruction

Every neighbor of a vertex has exactly one neighbor within that vertex's
neighborhood: the common neighbor completing their edge. The neighborhood
therefore consists of seven disjoint edges. Every vertex lies in exactly seven
actual triangles, each edge belongs to exactly one, and the triangle count is
99*7/3=231. Distinct triangles share at most one point.

Three actual triangles cannot meet pairwise at three different points. Those
points form a triangle, and any one of its edges also lies in its original
triangle with a different third point, contradicting lambda1. We will use
this prohibition directly rather than inherit a binary-code approval.

Two distinct triangles T={v,a,b} and U={v,c,d} through v belong to at most
one induced rook-nine. In any such rook, T and U are its row and column
through v. Each of the four cross pairs ac,ad,bc,bd is nonadjacent and has
v as one common neighbor. Its other common neighbor is uniquely fixed by
mu2, and gives its corresponding opposite grid point. Consequently T and U
determine the same entire nine-subset in every proposed rook. This argument
only asserts uniqueness when a rook exists; it does not assert existence or
that arbitrary cross pairs form a grid.

An induced C4 is also contained in at most one induced rook-nine. In any
rook containing that C4, it is a grid rectangle. The unique completions of
its four edges determine four more grid points. The two completions of
opposite parallel edges are adjacent, and their unique edge completion
determines the ninth point. Hence two proposed rook subsets coincide.
The target has4158 nonedges. Each nonedge and its two common neighbors gives
an induced C4, counted twice by its two opposite pairs, so there are2079
induced C4s. A rook-nine contains nine, giving9R<=2079 and R<=231.

## Local defect graphs and their total

Fix an actual triangle T and v in T. Each rook containing T contains exactly
one other actual triangle U through v. Conversely a pair T,U belongs to at
most one rook by the preceding reconstruction. Thus the six other incident
triangles contain exactly r_T nondefective partners of T. The remaining
6-r_T partners are precisely its neighbors in D_v. This proves the claimed
degree identity and bounds without assuming rook subsets disjoint.

Each rook-nine contains exactly six actual triangles. Its triangle edges
cannot have alternate external completions because lambda1 fixes their third
point. Double counting triangle-rook incidences gives

    sum_T r_T=6R,   sum_T d_T=6*231-6R.

At any point v the sum of the seven degrees d_T is even, being twice the
number of edges of D_v. Hence the triangles with odd d_T give an even
binary incidence selection. This is a consequence of the local defect graph,
not a presumed nonzero codeword of a target.

## A total deficiency of six forces an even six-triangle selection

Suppose R=230, so the total nonnegative deficiency is six. If d_T>=2 for
some triangle T, at each of its three points D_v has d_T other neighbors
of its node. Every such neighboring triangle has positive deficiency.
The lists at different points of T are disjoint: a different triangle cannot
meet T twice. There are therefore at least3*d_T other positive triangles,
and the total deficiency is at least

    d_T+3*d_T=4*d_T>=8,

contrary to six. It follows that exactly six triangles have deficiency one
and all other triangles have deficiency zero.

At any point v, the positive nodes of D_v all have degree one and the other
nodes have degree zero. Therefore those positive nodes are paired by a
matching, and their number is even. The six deficiency-one triangles have
even point incidence. The next paragraph classifies this particular selection
from the graph hypotheses alone.

## Self-contained even-six classification

Take six distinct actual triangles having even incidence at every used point.
A point in all six would leave each of their twelve other points private by
linearity, which is impossible. A point in four gives eight distinct outer
points, each needing incidence from one of the remaining two triangles.
Those two triangles have only six point incidences, which cannot cover eight.
Thus every used point has multiplicity two. There are18 incidences and nine
used points.

Form a dual graph with the six selected triangles as nodes and the nine
points as edges. It is simple by linearity and cubic because each selected
triangle has three points. A dual triangle would be three actual triangles
meeting at three distinct points, already ruled out by lambda1. A triangle-free
cubic graph on six nodes must be K3,3: its complement is2-regular, hence C6
or two C3s; the complement of C6 contains a triangle, leaving two C3s and
therefore K3,3.

Identify the nine used points with the edges of this K3,3. Its six star
triples give the three rows and three columns of a rook-nine. Any additional
edge between two points nonadjacent in this rook would already have two
common neighbors within the rook, contradicting lambda1 for that extra edge.
The nine-subset is consequently an induced rook-nine, containing all six
selected actual triangles.

In particular, at every used point v its two selected triangles are together
contained in this rook. They are not adjacent in D_v. But in the R=230
situation they are the only positive nodes at v, and both must have degree
one; zero-degree nodes cannot provide any edge. Their required defect edge
is absent. This contradiction proves R!=230.

## Hand boundaries, overlap and scope

The small rook9 graph has one rook, six actual triangles, and two triangles
at each point. Its analogous local graphs on two nodes are empty, with zero
deficiency. The even-six classification correctly returns that same rook;
it never forbids an even six-triangle incidence dependency in general. The
contradiction uses the additional assertion that those same six triangles
are the entire positive deficiency support.

At R=231 every d_T is zero, and this argument has no contradiction. A claim
that R<=229 would need a separately justified exclusion of R=231. The
historical N3-free literature/reduction has additional premises; it is not
silently used here. There is no Hamming-cover, target-nonexistence, zero-rook,
nonconstant-kernel or code-rank conclusion.

The known nine-C4 packing bound, rook reconstruction and even-six K3,3
classification overlap the preserved October3 double-fiber and weight-seven
papers. The separately audited September17 rook regular-set encoding is also
compatible with the target spectrum and supplies no rook exclusion. The new
candidate combines self-contained reconstruction with the global deficiency-six
case, rather than presenting those older ingredients as discoveries.

A bounded comparison read those named papers, the N3 scope note and
wave112-c4-short-vector-incidence/derivation.md. A targeted docs Markdown
search for rook230/rook deficiency/defect graph did not find this precise
argument. This is not a whole-archive or worldwide novelty claim. Root read
and reconstructed the even-six step before this freeze; agreement is shared
discovery context and is not independent approval. A different author must
challenge the unique-pair map,6R counting, all local degree steps and the
six-column conclusion before any mathematical promotion.

## Failed shortcuts retained

An uncovered C4 has not been proved here to force the forbidden N3 pattern;
the other edge-completion pair may be adjacent with a different center.
Neither a universal grid cover nor a hypothetical target automorphism is
assumed. Counting embeddings instead of nine-subsets would invalidate the
6R and9R coefficients. A graph with only the local lambda1 condition but
without the target's regular triangle incidence and mu2 is outside the
R=230 statement. No computational controls or proposed exact enumeration
are needed for this written proof; no execution authority is requested.
