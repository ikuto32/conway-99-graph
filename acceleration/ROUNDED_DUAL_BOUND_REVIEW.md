# Rounded dual bounds: arithmetic is feasible, one frozen dual does not transfer

The bounded CPU study in `results/20260916_atomic_cycle_qa/rounded_dual_cpu_study.json`
found no useful pruning from the initial state's dual weights. It checked 319
distinct candidates: the baseline, 64 uniformly sampled native atomic proposals,
and the previously optimized atomic3/atomic4 candidates, with overlap deduplicated.
257 candidates had saved numerical LP optima for an additional weak-duality check.
The study took 10.99 seconds. No CUDA scorer or search policy was implemented.

At scale D = 1,000,000, the baseline's exact lower bound is 7.331873, compared
with the independently evaluated exact feasible upper bound approximately
7.332122013712176. Every one of the 318 other tested candidates has a negative
bound, ranging from -23.713504 to -2.045954. Since the objective is nonnegative,
these can be strengthened to zero for free, but still prune no candidates for
either improvement or the incumbent-plus-0.5 escape band.

## Exact bound

For a fixed overlap assignment K, write the existing necessary phase-I objective as

    F_K(x) = sum over 840 quota rows |A_r(K)x - b_r(K)|
             + sum over 3486 pair rows max(0, A_r(K)x - b_r(K)),  0 <= x <= 1.

The pair rows retain known-known and known-unknown products, dropping only the
nonnegative unknown-unknown products. No fixed disjoint block totals are assumed.

Choose any dual weights y with -1 <= y_r <= 1 for quota rows and 0 <= y_r <= 1
for pair rows. These intervals imply

    F_K(x) >= y . (A(K)x - b(K)).

Minimizing the right side over the box gives

    min_x F_K(x) >= L_K(y) = -b(K).y + sum_j min(0, (A(K)^T y)_j).

Clip each stored binary floating-point dual weight to its exact interval, then
round D times that exact rational value to an integer n_r. The study uses nearest
integer with ties to even. The vector n/D remains exactly dual-feasible, regardless
of whether the original floating-point solver returned an optimum.

The entire score numerator is integer:

    N_K = -sum_r b_r(K) n_r + sum_j min(0, sum_r A_rj(K) n_r),
    L_K(n/D) = N_K / D.

Rows omitted as tautologies by the LP producer receive weight zero in the full
coordinate table. Row-coordinate matching is checked against the independent
full99 graph-derived model.

## A direct GPU formula and integer range

Let q[u,s] be the quota numerator, with zero at the 336 absent quota coordinates.
Let p[u,v] be the symmetric pair numerator, with a zero diagonal. For an unknown
disjoint edge {a,b}, the combined column numerator is

    c_ab = sum over the two labels s of b: q[a,s]
           + sum over the two labels s of a: q[b,s]
           + p[a,b]
           + sum over w in K(b): p[a,w]
           + sum over w in K(a): p[b,w].

Each K vertex has degree four. Thus every unknown column has exactly four quota
and nine pair incidences. The CPU study independently checked these counts for
every column of every sampled candidate. There are 1,680 unknown columns.

All valid-row targets satisfy 0 <= b_r <= 2. Consequently

    -4D <= c_ab <= 13D,
    -15372D <= N_K <= 1680D.

At D = 1,000,000, the worst negative score numerator is -15,372,000,000, well
within signed 64-bit range. The existing degree-four neighbor geometry supplies
the target terms and the nine pair incidences. A prospective CUDA implementation
could evaluate the 4,326 RHS terms and 1,680 column terms per candidate using
integer reductions. This is an arithmetic design, not a measured GPU benchmark.

## Pruning comparison and rounding sensitivity

For any independently verified feasible incumbent x, its exact value U is an
upper bound on the incumbent's optimal merit. If N_K >= ceil(D U), the candidate
cannot have a strictly better optimal merit. The comparison must use the exact
rational U, not an unchecked floating-point objective. Deliberate uphill search
requires a separate policy; eliminating all non-improving moves would remove
the escape behavior used by the existing driver.

The function min(0,t) is 1-Lipschitz. There are at most 8,652 target units and
21,840 total matrix incidences. Nearest rounding therefore changes this frozen
dual's score by at most

    (8652 + 21840) / (2D) = 0.015246  at D = 1,000,000.

The largest noninitial score is below -2, so increasing grid precision cannot
make this same frozen dual useful on the tested candidates. The weakness comes
from transferring the dual to a changed K, rather than from rounding. A bank of
different duals could provide the maximum of several valid lower bounds, but
its effectiveness has not been tested here. The present evidence does not
justify implementing a single-frozen-dual GPU pruning stage.

This is a bounded sample, not screening of all 16,299 initial atomic proposals.
