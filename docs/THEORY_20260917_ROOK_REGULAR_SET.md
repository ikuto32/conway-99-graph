# Candidate exact encoding for a target containing a nine-vertex rook graph

Status: CANDIDATE, pending independent derivation and artifact review. This is
a conditional reduction, not an exclusion. It assumes an induced `3 by 3`
rook graph, not a graph automorphism. It does not establish that every target
contains such a graph.

The pinned archive already derives the two-cell regular-set quotient in
`external_conway99_research/attempts/wave102-prism-incidence-code/derivation.md`
and checks it in `verification/wave102-prism-incidence-code/verification-report.md`,
at commit `85e705cc6c2a14d123120c93a847e30aaab1789e`. Those historical statements
are not being silently promoted. The present candidate derives the finer
eighteen-cell system and its exact adjacency-matrix encoding afresh.

Let B be the 9 by 9 rook adjacency matrix, with vertices `(r,c)` in `{0,1,2}².
Then `B² = 2I - B + 2J`. Every pair in this rook graph already has the target
number of common neighbors. Therefore an external vertex can have at most
one neighbor in it. There are `9(14-4)=90` edges leaving the rook and exactly
90 external vertices. Every external vertex has exactly one rook neighbor.

Partition the external vertices into X_i according to their unique rook
neighbor i. Each X_i has ten vertices. Put `T = I_9 ⊗ 1_10^T`, so after
labeling the target matrix has blocks `A = [[B,T],[T^T,H]]`.
No relationship between the ten labels in different X_i is assumed.

Block multiplication proves that the full target identity is equivalent to:

1. H is a symmetric binary 90 by 90 matrix with zero diagonal;
2. `TH = (2J_9 - B - I_9)T`;
3. `H² = 12I_90 - H + 2J_90 - T^T T`.

The top-left equation holds identically because `TT^T=10I_9`; the top-right
equation is precisely item 2; and the bottom-right equation is item 3.
Conversely, these equations for H give the full target equation for A and
exhibit its induced rook graph. Thus no additional degree assumption is
needed for this equivalence.

Set `Q = 2J_9 - B - I_9`. For x in X_i, its number of neighbors in X_j is
`Q_ij`: one for j=i or for a rook neighbor j of i, and two otherwise.
Each X_i therefore induces five disjoint edges. Between different groups,
the bipartite graph is a perfect matching when i,j are rook neighbors and
is 2-regular otherwise. The total external degree is thirteen.

The equitable quotient for the eighteen cells (nine single rook vertices,
nine external groups) is `[[B,10I],[I,Q]]`. B has eigenvalues 4,1,-2 with
multiplicities 1,4,4. Since J commutes with B, Q has eigenvalues 13,-2,1
with multiplicities 1,4,4. The eighteen-cell quotient consequently has
eigenvalues 14,3,-4 with multiplicities 1,9,8. These are compatible with
the target multiplicities 1,54,44, leaving 45 copies of 3 and 36 of -4 on
the 81-dimensional external subspace whose sum on each X_i is zero.
This calculation supplies no spectral contradiction.

Proposed next use: represent the unknown cross-group graphs by matching and
2-regular blocks and derive local compatibility constraints. A normalization
of labels within X_i would require its own coverage argument. No such
normalization or search is claimed here.

## Literature triage, 2026-09-17

The inspected [arXiv version 2604.23037v2](https://arxiv.org/html/2604.23037v2)
distinguishes a universal Paley(9) pattern from containing one Paley(9).
Section 3.4.2 labels exclusion of a single such subgraph as Conjecture 3.4.4;
Theorem 3.4.3 concerns eleven independent copies and omits its proof. Neither
is a checked premise here. Sections 5.1.3 and 6 report unsuccessful SAT searches,
which are not nonexistence certificates. This focused inspection is not a
comprehensive literature-status audit. The thesis front matter says June 2023,
while this arXiv version is dated April 2026; these dates are kept distinct.
