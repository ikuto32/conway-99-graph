# Independent conditional residual-completion review

Reviewer: `/root`, distinct from the producer `/root/state_literature_audit`.
The theorem below is conditional. No factor or completed graph is supplied.

Write T for the triangle, X for its 36 external neighbors and Y for the 60
remaining vertices. Let S=J3-I3, let R record the three 12-vertex cells, and
let C have exactly one neighbor in every cell at every X vertex. In
particular C is symmetric, binary, zero diagonal and cubic; the within-cell
edges and each between-cell bipartite graph are perfect matchings. There is
no assumption of an automorphism. All three matchings and the cross
permutation may vary.

For a binary F of size 36x60, assume R^T F=2J and
FF^T=12I-C-C^2+2J-RR^T. The latter diagonal fixes each row sum at 10,
since (C^2)ii=3 and (RR^T)ii=1. The former fixes every column sum at 6.
Assume D is symmetric, binary, zero diagonal of size 60x60. These are
explicit prerequisites, not consequences of floating-point residuals.

Independent block multiplication gives the following six upper-triangular
blocks of A^2 for A=[[S,R^T,0],[R,C,F],[0,F^T,D]]:

    S^2+R^T R,  S R^T+R^T C,  R^T F,
    RR^T+C^2+FF^T,  CF+FD,  F^T F+D^2.

There are no other summands: each block is the sum over the three possible
intermediate vertex cells. Now R^T R=12I, S^2=I+J,
J3 R^T=J_(3,36), and R^T C=J_(3,36). Thus the first four blocks equal
the corresponding blocks of 12I-A+2J by the prerequisites. The fifth and
sixth agree exactly when

    FD=2J-F-CF,
    D^2+F^T F=12I-D+2J.

The lower blocks are transposes. Therefore these two equations are both
necessary and sufficient, with every matrix shape and graph prerequisite
retained. Since diag(F^TF)=6 and diag(D^2)=deg(D), the last equation gives
deg(D)=8. Imposing degree 8 separately is redundant; it cannot replace the
quadratic equation. This is a universal algebraic argument, not an inference
from the finite controls.

For the optional cheap screen set H=2J-F-CF and T=F^TF. Binary nonnegative
D forces H>=0. For y!=z the last equation says
Tyz+common_D(y,z)=2-Dyz, so Tyz>2 is impossible. If Dyz=1, then Tyz<=1,
F[:,z]<=H[:,y] and F[:,y]<=H[:,z], because these are summands of the two
nonnegative mixed column equations. Any actual D neighborhood at y therefore
is an eight-subset of that symmetric allowed graph, has F-column sum H[:,y],
and has Tzw<=1 for all its distinct members z,w: those two vertices already
share y. Allowed degree or coordinate capacity shortages are consequently
valid rejections. These are necessary tests. Passing them, or having every
individual row domain nonempty, is not a completion certificate.

Summing H gives row sums 120-10-30=80, column sums 72-6-18=48,
and cell column sums 24-2-6=16. These automatic identities supply no new
feasibility evidence.

The separate checker imports no producer code. It reconstructs every saved
coefficient-control adjacency from raw C,R,F,D; computes each full residual
with independent integer common-neighbor bitsets; and checks the expanded
blocks. A directly constructed rook graph on nine vertices is a known-valid
positive control. Deleting an edge, altering a residual coefficient and
altering the saved block assembly are negative controls. All 12 saved small
star choices are checked by literal partial adjacency, and every recorded
cheap-screen array is reconstructed. These calibrate exact calculations;
they do not instantiate a valid target-sized F.

This review establishes claim
`C-TRIANGLE-FACTOR-RESIDUAL60-COMPLETION-EQUIVALENCE` revision 1 within its
recorded scope. It does not certify a SAT encoding, exhaustive star search,
or the producer API on every possible input; such uses need their own
artifact gates. Shared trusted components are Python integer arithmetic,
the raw producer fixtures, and the explicitly written matrix definitions.
