# One freed matching coordinate: new domains and a near-zero relaxation diagnostic

Status: **CANDIDATE prototype; independent domain/model review pending**.
No exact family exclusion, exact LP feasibility certificate, or target result
was obtained. Frozen producer: `acceleration/theory_20260917_partial_matching.py`.

The deterministic coordinate is baseline18481's `root_group=0, same_0`.
Exactly its six existing matching edges are removed. All other **162** baseline
K edges remain fixed, including the other thirteen same-sign matchings and all
seven cross-class matchings. Same-fibre and unlisted other-coordinate edges
remain absent. The unknown universe is the sixty support-legal edges among the
twelve vertices of this matching coordinate, plus the existing 1,680
disjoint-support edges, totaling 1,740 unknown edges. This is a conditional
one-coordinate family, not the positive-only scaffold/core domain.

The twelve affected outer vertices now have partial degree five, so their
local domains choose nine new outer neighbors. The other seventy-two vertices
retain partial degree six and choose eight. Frozen historical builders require
degree six/eight choices and 1,680 variables; they were inspected but not used
as if they already supported this different domain. No historical domain file
or builder was changed.

## Frozen experiment and result

`manifest.json` preregistered this coordinate, exact unknown/absent-edge scope,
restricted-subset controls, limits, and the independent-review gate for proof
claims before enumeration or solving. Limits were 160 seconds for enumeration,
3,000,000 global search nodes, 20,000 domains per center, 200,000 total domains,
and 240 seconds overall. The LP received a 60-second diagnostic limit only
after all 84 nonempty domains completed.

All 84 new domain tables completed without a cap: **54,478 choices**, with a
maximum of 3,057 at one center. Their search visited 469,834 nodes, with another
36 nodes in the two restricted-universe calibration searches. Those restricted
universes were checked against direct enumeration of every subset and actual
full-99 graph mutation; deleting a chosen edge from a valid local completion
was rejected. Every one of the 26,250 historical baseline stars embeds in the
new tables by appending its removed matching partner for an affected center.
This is a positive regression check, not independent completeness verification.

The overall pilot took 36.672 seconds of measured wall time. HiGHS 1.15.1,
single-thread IPM without crossover, reported `Optimal` for the new LP with
floating objective **5.048235921933426e-12**, spending approximately 31.906 seconds
in the solve. This is only a numerical near-zero diagnostic. It is neither an
exact zero nor a feasibility/exclusion certificate.

The LP has 54,478 domain-probability variables, 1,740 reciprocity rows, 3,486
linear-cap rows, and 84 hard simplex normalizations. Its augmented matrix has
5,310 rows, 61,444 columns, and 2,892,298 nonzeros. Saved probabilities and row
duals remain floating-point guidance. No exact certificate was produced.

## Exact local-domain definition being prototyped

Let `B` denote the fixed partial adjacency after the six matching edges are
removed, and `U` the declared 1,740-edge unknown universe. A local star at outer
vertex `u` chooses `14-degree_B(u)` incident edges from `U`. Adding them to `B`
must preserve all degree and off-diagonal common-neighbor caps, and must make
every `u`/root-neighbor common-neighbor count exactly `2-B_us`. Root-neighbor
degrees remain saturated by the scaffold, so these latter quotas are necessary.

For each pair `u,w`, the chosen neighbor set `S` obeys

```text
sum_{v in S} (B_vw + [v=w]) <= 2-B_uw-(B²)_uw.
```

The prototype enforces these integer resource capacities, the fourteen root
label quotas, and conflicts between two selected vertices whose previous pair
cap was already saturated. It first tests each prospective edge individually
by full graph mutation. Binary include/exclude branching on a candidate from
an unsatisfied quota partitions the finite subset universe. Resource/label
capacity pruning and saturated-pair conflicts need separate independent
equivalence/completeness review before any claim about the full family.

Every generated affected-center star has exactly one freed matching edge;
every unaffected-center star has zero. This is checked and recorded rather
than silently assuming the old eight-disjoint-neighbor convention.

## A distinct relaxation, not a comparable historical merit score

The objective identifier is
`PARTIAL_K_STAR_RECIPROCITY_CAP_PHASE1_V1`. Put a probability simplex on each
new local domain. For each unknown edge `u<v`, its projected variable is the
selection marginal at the smaller endpoint. Minimize the sum of absolute
endpoint-marginal disagreements plus the sum of positive linear-cap residuals.
The linear caps use this new partial `B`:

```text
(B²+B)_ab + (BE+EB+E)_ab <= 2,   for outer a<b.
```

They drop the nonnegative off-diagonal term `(E²)_ab` from the full target
equation. `linear_caps.json` saves their integer coefficients and the complete
unknown-edge indexing. The probability tables and cap coefficients determine
the relaxation, but its correctness and domain completeness are not yet
independently checked. Its feasible domain differs from the historical fixed-K
star objective, so the two values must not be presented as seed improvement.

The new numeric near-zero cannot establish that any matching coordinate member
extends to an SRG. In particular, reciprocal degree-one marginals on the twelve
freed vertices need not belong to the convex hull of perfect matchings: odd-set
inequalities may still be violated. None were added to this frozen primary run.

## Concrete next obligation

First reconstruct the saved fractional matching marginals and test all odd
subsets of the twelve freed vertices in a separately preregistered diagnostic.
For an odd set `T`, a true perfect-matching marginal satisfies
`sum_{ab subset T} y_ab <= (|T|-1)/2`. If these inequalities produce a useful
strengthening, record a distinct objective/model revision before rerunning the
LP. Before a family exclusion could be claimed, independently enumerate the
new domains, check the generalized matrix construction and fixed-absence scope,
then preserve and independently replay an exact rational dual certificate.
The current numeric result alone supplies none of those proof obligations.

Artifacts are the manifest, restricted controls, 84 separately labeled new
domain JSON files, integer linear caps, numeric LP output, and hash-bound
summary in this directory. Replay with a fresh output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_partial_matching.py --out build/partial-matching-new --seconds 240
```

The scope remains this named coordinate family with all declared fixed
presences and absences. No automorphism assumption or unrestricted coverage
claim is used. Overall search coverage: UNKNOWN; no validated denominator.
