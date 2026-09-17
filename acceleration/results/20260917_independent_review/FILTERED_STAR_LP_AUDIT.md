# Independent exact audit of the filtered-star LP

Claim: `C-FILTERED-STAR-LP-18481` revision 1. Premise:
`C-STAR-MATCHING-PAIR-18481` revision 1. Objective:
`TRIANGLE_PAIR_FILTERED_STAR_SIMPLEX_V1`.

The raw checking record is `filtered_star_lp/audit.json`; its exact integer
dual witness is `filtered_star_lp/integer_certificate.json`. The reviewer is
the independent verification agent, separate from the filtered-model producer.

## Domain and mathematical scope

Each of the 84 original baseline18481 star domains has been restricted by the
independently checked triangle-matching condition and exact pair propagation.
The resulting 15,335 masks retain their original IDs. The prior reduction
claim establishes that every hypothetical target completion of this fixed
assignment still selects one retained mask at every outer vertex. It does not
establish that these masks are the original complete domains, nor that they
are simultaneously realizable.

The new model explicitly retains `original_complete_domains_used: false` and
the domain label `TRIANGLE_AND_PAIR_FILTERED_ORIGINAL_ID_DOMAINS`. The auditor
checks every mask and original ID against the exact independently audited
reduction. No flag is rewritten to pass an older domain auditor.

The objective is the sum of absolute reciprocal-edge marginal residuals plus
positive parts of the retained outer-pair linear-cap residuals, minimized over
one probability simplex per filtered domain. Its algebra resembles the older
star objective, but its feasible domain is different. This audit makes no
direct objective-performance comparison to the original-domain value.

## Complete integer model check

The auditor imports the previous independent third checker's full99 graph
constructor and matrix-entry cap reconstruction, not the producer's graph or
matrix code. The cap coefficients follow from

    (B+X)² + (B+X) = B²+B + BX+XB+X + X².

For distinct outer vertices, the target sets this entry to 2 and X² has
nonnegative entries. Dropping X² therefore gives necessary linear caps.

Every filtered probability column is reconstructed from its selected edges:
its vertex-normalization coefficient, signed reciprocal coefficients, and
smaller-endpoint projection contributions to every cap. The auditor then
constructs the slack columns separately and compares every coefficient in
all 5,250 rows of the serialized integer CSR model, including row/column
ordering, bounds, objective costs, original-ID offsets, and cap metadata.

The 84 normalization rows are hard equalities. Each of 1,680 reciprocal rows
has two nonnegative slacks with coefficients -1 and +1, both cost 1. For fixed
probabilities, minimizing their cost gives the absolute residual. Each of
3,486 cap rows has one nonnegative slack with coefficient -1 and cost 1, giving
the positive part of its residual. All probability columns have cost zero.
Thus the independently reconstructed augmented LP represents exactly the
stated filtered-domain objective.

## Exact bounds and implication

Stored dual weights are interpreted as exact binary rationals. The auditor
requires beta in [-1,1] and gamma in [0,1], then clears their denominators to
integer scale T. For every retained local star it calculates its exact weighted
cost and checks the support minimum of each filtered simplex. The resulting
integer certificate has lower bound

    [sum_u min_{S in filtered D_u} cost(u,S) - gamma_integer · cap_rhs] / T.

This bounds the objective by the same elementary inequalities used in the
original star certificate: beta times a reciprocal residual is at most its
absolute value, and nonnegative gamma times a cap residual is at most its
positive part. Expected local cost is at least the minimum local cost.

For the upper bound, the stored probabilities are converted to exact binary
rationals, checked nonnegative, normalized by their exact positive simplex
totals, and the objective is evaluated directly over the independently
reconstructed graph constraints. No floating-point tolerance certifies either
endpoint. The exact fractions are retained in the checking record; their
approximate displays are

    11.464794729497703 <= optimum <= 11.464794852600662.

Every target completion would survive the sound domain reductions, reciprocate
its edges and satisfy every cap, giving objective zero. The positive exact
lower bound therefore gives another obstruction to completing this fixed
baseline assignment. That assignment was already excluded; this is not a new
unrestricted exclusion or target resolution.

## Falsification controls and reproduction

The checker accepts the complete independently reconstructed raw matrix,
rejects a flipped slack sign and changed cap RHS, and rejects a changed
filtered original ID. A zero dual gives exactly zero lower bound and supplies
no exclusion; multiplying the integer witness and scale by 10^30 preserves
the exact bound. A negative cap weight and an all-zero probability simplex
are rejected. Corruptions operate on in-memory artifacts after hash checking,
so rejection tests the checking logic rather than only identity guards.

The bound does not depend on HiGHS claiming optimality. The audit does not
promote the solver's raw feasibility residuals, stopping status, or performance
as mathematical facts. No solver is imported or executed by the checker.

From the repository root in the pinned environment:

    uv run --locked python acceleration/audit_20260917_filtered_star_lp.py --input acceleration/results/20260917_theory/filtered_star_lp_baseline18481 --out <fresh-audit-directory>

The report binds the actual command, source commit and hashes, prerequisite
review, full frozen domains, exact model, numeric vectors, controls, and exact
certificate. Its scope remains the named fixed assignment and new filtered
objective.

Overall search coverage: UNKNOWN; no validated denominator.
