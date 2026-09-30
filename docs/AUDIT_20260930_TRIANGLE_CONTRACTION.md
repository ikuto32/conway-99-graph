# Independent residual triangle contraction review

Assume an actual SRG(99,14,1,2) in the identity-cross triangle-root family.
The previously checked conditional partition theorem supplies its actual
twenty residual triangles. It does not identify a predetermined partition
of the outside labels with that actual partition. Let R be their60x20
indicator matrix, F the36x60 incidence, C the inner adjacency, and D the
actual residual adjacency. Put T=FR.

Any vertex outside a graph triangle has at most one neighbor in it: two
neighbors would give their adjacent pair two common neighbors. Consequently
every intertriangle block is a partial matching. Each D vertex has degree8,
two neighbors in its own triangle and six outside. Define W=DR-2R. It is
binary, zero on the own-triangle positions, with row6 and column18. Write
B=R^T W. Then B is symmetric, has zero diagonal, entries0 through3, and
row18. This does not require an automorphism of the graph or its partition.

The independent expansion is (2R+W)^T(2R+W)=12I+4B+W^TW,
because R^TR=3I and R^TW=W^TR=B. Also R^TDR=6I+B.
Adding yields R^T(D^2+D)R=18I+5B+W^TW. Inserting the exact residual
equation F^TF+D^2+D=12I+2J gives

    T^T T + 5B + W^T W = 18I + 18J.

Here R^TJR=9J. Thus for distinct triangle indices p,q,
T_p^TT_q+5B_pq+L_pq=18, where L=(W^TW)_pq counts only vertices
outside both triangles that have a neighbor in each. Vertices in either
triangle contribute zero to W in that triangle's column. Nonnegativity
gives B_pq <= min(3, floor((18-T_p^TT_q)/5)).

Independently, multiply FD=2J-(I+C)F on the right by R. Since JR=3J
and DR=2R+W, this gives FW=6J-(C+3I)T exactly.
These are necessary identities, not a converse completion theorem.

Adjacent residual vertices in a triangle already share its third vertex,
so their F columns are disjoint. Hence T is binary, has column18 and row10.
Its diagonal Gram entries are18. Summing an off-diagonal row of T^TT gives
10*18-18=162. Summing the contracted identity then gives sum_{q!=p}L_pq=90.

The checker reconstructs the producer's structural60-vertex control from
neighbor sets, checks all400 contraction entries against raw saved matrices,
and supplies a separate genuine nonempty positive from the independently
validated SRG(243,22,1,2). Its residual180 vertices admit a checked partition
into60 triangles. The latter has residual degree16, W row14/column42 and
factor row18; it is not a Conway99 fixture. The same off-diagonal identity
and mixed identity hold, while the diagonal right side is42I+18J. All3600
entries of both contractions and all3600 mixed entries are checked exactly.
No SRG99 factor or residual graph is invented.

The separately recorded row-capacity observation is a new candidate corollary
for independent parent review, not part of this checker's approval of its own
new work: for a binary36x20 T with row10 and column18, the19 numerators
18-T_p^TT_q sum180. Their residues modulo5 sum at most75, so the sum of
the corresponding floor capacities is at least21. Therefore the isolated
row-capacity test cannot reject such a T. Joint degree feasibility or the
full W/mixed constraints can still add information; neither is solved here.
