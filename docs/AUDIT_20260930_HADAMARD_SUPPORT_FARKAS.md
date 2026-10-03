# Independent integer Farkas exclusions of three fixed supports

These exclusions concern exactly the three saved coordinate supports L for
connected01, connected02 and connected03. They do not exclude those cores,
other Hadamard supports, all support orientations, or the unrestricted target.
No target automorphism or residual triangle partition is assumed.

The checker reconstructs each literal identity-cross36-vertex core from its
three matching vectors, and reconstructs its prescribed Gram G using integer
neighbor intersections. For every column's six chosen coordinates it
enumerates all90 balanced fibre assignments using successive two-element
subsets, and removes exactly the assignments containing a row pair whose
G entry is zero. Such removal is necessary: a binary factor's zero Gram
entry is a sum of nonnegative products, so no one column can contribute1.
The full remaining domain and its order are compared with the raw artifact.

Introduce one nonnegative real x for each retained choice. For each of60
columns require that its variables sum to1. For each of666 unordered row
pairs i<=j require that the sum of variables whose choice contains both rows
is G_ij. This reconstructs all726 equalities and every coefficient column
without importing the producer's model builder or scorer. A binary factor
with this fixed coordinate support would give a one-hot nonnegative solution
of this system. No outside-column cap is required for this implication.

For each saved integer vector y the checker evaluates every column product
y^T A_j as a Python integer, checks all are nonnegative, and evaluates the
exact integer y^T b. If x>=0 and Ax=b existed, then

    y^T b = y^T A x = sum_j (y^T A_j) x_j >= 0,

contradicting the recorded negative value. Therefore the exact continuous
system is infeasible, and no binary factor with that fixed support exists.
The initial floating-point outcomes and unsuccessful rational reconstruction
are preserved as provenance; they are not premises of this proof. The
checker does not rerun a numerical solver or approve a SAT encoding.

Controls include an exactly feasible necessary system made from the genuine
known SRG243 factor, all3600 combinations of tiny binary2x2 matrices,
nonnegative integral primal vectors and small integral dual vectors, and an
explicit valid infeasibility certificate. Deliberately corrupted vectors,
models, right-hand sides, raw domains and certificate statistics are rejected.
The SRG243 system is a calibration submodel containing its actual column
choices, not a Conway99 construction or a complete243 domain census.

All proofs bind the complete raw support, reconstructed matrix and integer
certificate. A claimed exclusion does not depend on replaying the producer's
rounding or dual-repair algorithm. The three supports are distinct fixed
configurations; their count is not a count of excluded cores or an overall
search-coverage fraction.
