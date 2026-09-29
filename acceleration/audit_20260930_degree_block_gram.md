# Independent degree-block Gram review

Verifier: `/root/state_literature_audit`. No producer optimizer or checker is
imported. The executable audit binds this written argument and the exact
artifacts it checks; promotion is conditional on that audit completing.

For the pinned 780-variable family, every pair of the forty right vertices is
one Boolean variable. Partition those pairs by their unordered pair of
ten-vertex cells. There are four internal 45-edge blocks and six 100-edge
bipartite blocks. The independently reconstructed 160 degree equations give
degree one in the four internal blocks; four bipartite blocks have degree one
and the two remaining blocks degree two. These blocks partition all variables
and degree equations. Dropping common-neighbor constraints therefore gives a
necessary relaxation, a Cartesian product of the ten degree-feasible sets.

For any exact integer vector `w` and full59 adjacency with these variable
entries, the Gram quadratic is the affine polynomial

```
q(x) = K + Σ_e c_e x_e,
c_(ij) = -18 w_i w_j,
K = 27 Σ_i w_i² + (Σ_i w_i)² - 18 Σ_fixed_edges ij w_i w_j.
```

The audit reconstructs the rook9 core, owner attachments, all fixed entries,
all 780 full59 endpoint pairs, and each polynomial from raw adjacency and `w`.
It checks that the nine parent graphs differ only at declared free entries.
No numerical eigenvalue or solver tolerance is used.

For a fixed-value pattern, remove forced-one edges after subtracting one from
both endpoint quotas and adding their exact weights to the constant term.
Remove forced-zero edges too. For each internal block, an edge-processing
subset dynamic program computes the maximum weight for every covered-vertex
subset. This uses a different recurrence from the producer's least-remaining-
vertex recursion. Every saved table value is checked against the independently
computed optimum; the selected edges separately attain the full value.

For a bipartite block, arbitrary signed integers `alpha_v` and nonnegative
integers `beta_e` give a valid upper bound when
`alpha_u + alpha_v + beta_e >= c_e` for every remaining edge. Indeed each
`0 <= x_e <= 1` satisfies

```
Σ_e c_e x_e <= Σ_v b_v alpha_v + Σ_e beta_e.
```

The vertex terms use exact degree equalities, so alpha need not be nonnegative.
An independently checked feasible binary edge set whose weight equals this
bound certifies the exact block maximum. The audit checks every dual
inequality, capacity term, residual quota, fixed-value condition and equality.

The independent blocks can be combined freely in the degree-only relaxation.
Their attaining edge sets are disjoint and satisfy all 160 degree equations.
Consequently `K + sum(block maxima)` is its exact maximum and an upper bound
for all locally feasible graphs in the frozen family. A strictly negative
value suffices to exclude the fixed-value pattern from any target extension.

For the target, `A1=14·1` follows from its diagonal identity. On `1`-orthogonal
vectors its eigenvalues satisfy `t²+t-12=0`, so they are 3 or -4. Thus
`27I-9A+J` is positive semidefinite, with eigenvalues 0 or 63. The same is true
of each principal full59 submatrix. A negative upper bound for an exact Gram
quadratic contradicts this necessary condition, without assuming an
automorphism or universal containment of this rook scaffold.

The clause for a forbidden pattern has literal `e` when the pattern fixes
`x_e=0`, and literal `-e` when it fixes `x_e=1`. Its falsifying assignment is
exactly that pattern. The audit checks all signs against the saved pattern and
raw parent graph, the initial 21-literal pattern, and all 21 attempted greedy
deletions. Only a strictly negative new bound authorizes a deletion. Each
failed deletion also supplies a degree-feasible attaining assignment with
nonnegative quadratic value. That assignment still satisfies the weaker final
pattern after deleting the same retained literal. Thus the final clause is
irredundant for this one fixed-vector degree-bound test. This is not a claim
of globally shortest clauses, or of graph feasibility for failed deletions.

Positive unfixed maxima mean only that these nine weight vectors do not
exclude the whole degree relaxation. They establish neither graph existence
nor feasibility of the full constrained target family. The final negative
pattern is a conditional exclusion within one fixed central-factor scaffold;
it is not a general rook exclusion or a resolution of Conway-99.
