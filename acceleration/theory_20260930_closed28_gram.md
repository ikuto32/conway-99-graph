# Candidate necessity argument for a closed-neighborhood Gram screen

Status: **CANDIDATE**, awaiting separate independent review. This note states
the precise prerequisite and scope for the saved experiment.

If the target adjacency matrix exists, its diagonal identity gives degree 14
at every vertex, so `A1=14·1`. On the orthogonal complement of `1`, the exact
identity gives `(A-3I)(A+4I)=0`. Since `A` is real symmetric, its eigenvalues
there are 3 or -4. Therefore

```
G = 27I - 9A + J
```

has eigenvalues 0 on the span of `1` and on the 3-eigenspace, and 63 on the
-4-eigenspace. It is positive semidefinite. Every principal submatrix is
positive semidefinite. Consequently, for any complete induced adjacency
matrix `H`, an integer vector `z` satisfying `zᵀ(27I-9H+J)z < 0` is an exact
obstruction to this particular induced graph occurring in the target.

Let the normalized root be `v=0` and the selected outer center be `u`. They
are nonadjacent, so their two common neighbors are exactly the two recorded
inner vertices incident to `u`. The union `N[v] ∪ N[u]` thus has `15+15-2=28`
vertices: the root, all fourteen inner vertices, `u`, and its twelve outer
neighbors. The stored star fixes that entire vertex set.

After choosing a full perfect matching in `N(u)`, every adjacency within this
28-vertex set is determined:

- Root-to-inner edges and inner matching edges are fixed; root-to-outer
  nonedges and all other inner-to-inner nonedges are fixed.
- Every inner-to-outer incidence is fixed by each outer vertex's two labels.
- `u` is adjacent to precisely its fourteen listed neighbors and no other
  vertex of this set.
- The other twelve outer vertices lie in `N(u)`. The known edges together
  with the chosen residual matching cover all fourteen vertices of `N(u)`
  exactly once. Since the neighborhood of a target vertex induces a perfect
  matching when lambda is one, all additional pairs within `N(u)` are
  necessarily nonedges.

Thus no undecided entry is silently set to zero. Different residual matchings
may produce different complete induced matrices. A negative Gram witness for
one of them rejects only that chosen matching. It does not reject the center
star without exhaustive coverage of all matching choices, and it says nothing
about the unrestricted target by itself.

The experiment selects the first 32 retained original star IDs at each of 84
centers and uses exactly the already saved witness for each, for 2,688 cases.
It uses float64 eigendecomposition only to propose an integer vector, with
fixed guidance threshold -1e-8 and rounding scales 2^10, 2^20, 2^30. A rejection
requires strictly negative exact Python-integer quadratic value. No numerical
near-zero value or failure to find such a vector establishes PSD. The first
negative case retains its complete matrix, full99 vertex correspondence, star,
matching, integer vector and input identities for independent falsification.

Controls use the exact rational PSD test on the valid rook-9 graph's displayed
Gram matrix, a five-clique with integer all-ones vector and quadratic value -20,
and corrupted zero-vector and incorrect-quadratic checks. These controls
calibrate the implementation; the general necessity argument above still
requires a separate written review.
