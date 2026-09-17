# Independent fixed-overlap certificate audit, 2026-09-17

Reviewer: `independent_verifier` agent, separate from the discovery/evaluation
agent. Source baseline: `7518ebcec78589fe7f8b068ee7a1dd87e8bf8d42`.
This is a written derivation and source review, supplemented by the raw
checking records in this directory. It is not external or peer review.

## Exact statement and restricted scope

Fix the complete overlap assignment serialized in a candidate artifact.
Let B be its known symmetric 99-by-99 adjacency matrix. The 15 vertices
consisting of the root and its neighbors have degree 14 already. Every outer
vertex has known degree 6. Only the 1,680 outer pairs with disjoint root-group
supports may receive an additional edge; all other omitted edges stay absent.

For every outer vertex u, D_u is the complete set of locally admissible
8-element subsets of its permitted additional neighbors, satisfying exact
root-neighbor quotas and all partial common-neighbor caps. The certificate
claims a bound on a relaxation over independent simplex probabilities on these
84 sets. Neither this statement nor its proof assumes a nontrivial
automorphism. This audit does not assert that every possible overlap assignment
has been generated, or independently establish all global normalization
arguments used elsewhere in the repository.

## Independent derivation

For any symmetric binary completion X supported on the permitted unknown
edges, A=B+X. The target identity implies, for distinct outer vertices a,b,

    (B²+B)[a,b] + (BX+XB+X)[a,b] + (X²)[a,b] = 2.

The last summand is nonnegative. Thus the retained linear cap
L_ab(X) <= b_ab holds, with b_ab=2-(B²+B)[a,b]. This is a necessary condition,
not a sufficient one. The third checker reconstructs each coefficient from
the matrix entries in BE+EB+E for a single symmetric unit edge E. For an
off-diagonal cap, (E²)[a,b]=0. This reconstruction imports neither the producer's
matrix nor either preexisting exact verifier.

Write m_uv for the probability that u's chosen local star contains v, and
define x_uv=m_uv at the smaller endpoint u<v. Let r_uv=m_uv-m_vu. The checked
objective is

    F = sum_{u<v unknown} |r_uv| + sum_{a<b outer} max(0,L_ab(x)-b_ab).

The feasible domain is the product of the 84 complete original-domain
simplices. This objective is exactly `STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS`;
it is not the older edge LP objective and is not target-wide progress.

For integer weights beta, gamma and a positive integer scale T, the checked
boxes |beta|<=T and 0<=gamma<=T imply

    F >= [beta·r + gamma·(L(x)-b)] / T.

The weighted variable cost is separable over star choices. Its expectation
at vertex u is at least its minimum over every S in D_u. Therefore

    F >= [sum_u min_{S in D_u} cost(u,S) - gamma·b] / T.

The right side is the exact recorded integer gap divided by T. A full target
completion yields one star from each D_u, reciprocal marginals, and all
retained caps; hence F=0. A strictly positive checked gap consequently excludes
only this fixed overlap assignment. A nonpositive gap cannot establish
existence or nonexistence. Positive gap is sufficient regardless of numerical
LP termination status, provided the raw weights and complete domains check.

For an upper bound on the relaxed optimum, each stored nonnegative probability
vector is interpreted as exact binary rationals and normalized by its exact
positive total. Direct rational evaluation of F gives a feasible simplex
objective value. The third checker compares this value exactly to the saved
audit, without an acceptance tolerance. A strict comparison between an upper
bound and another assignment's positive lower bound compares this objective
only; a smaller value does not mean a graph exists.

## Domain completeness source review

Reviewed `audit_goal_theory_domains.py`, `audit_goal_theory_stars.py`,
`audit_goal_theory_pairs.py`, and `audit_certificate.py` at the hashes recorded
by the computational reports. The existing independent domain enumerator uses
increasing-index neighbor subsets and checks real adjacency changes. This is a
different path from the native quota-oriented domain producer. It is not
reimplemented by the third arithmetic checker; that dependency is explicit.

For addition of edge uv, only the pair uv and pairs joining u to an old
neighbor of v or v to an old neighbor of u can change common-neighbor counts.
The checked affected-pair list is therefore complete. The uv check accounts
for its allowed cap falling from 2 to 1. Other counts cannot decrease after
additional edges; adjacency can only reduce a cap. An invalid singleton or
prefix cannot become valid later, so rejecting it is sound. The DFS uses a
strictly increasing order, ensuring uniqueness and coverage of subsets.
Pruning for too few remaining neighbors, insufficient suffix quota supply,
or already exhausted required labels cannot remove a quota-satisfying
completion. Exact quota saturation plus eight added edges fixes all required
root-neighbor common counts.

The nonempty pair-audit branch reenumerates all 84 original domains and
compares their exact masks. Its capped branches are explicitly incomplete.
Pair arc consistency itself does not imply a simultaneous choice of stars.
The star certificate uses the original domains, not the pair-pruned domains,
so no pair-deletion exclusion is needed in its proof beyond the hash-bound
completeness evidence.

## Independent computation and falsification

`audit_20260917_fresh_review.py` uses only the standard library. It independently
builds B by nested root-group/sign loops, checks every partial cap, reconstructs
all retained coefficients, checks every local domain cost and minimizer, and
recomputes the exact dual and rational primal bounds. Project modules imported:
none. Shared trusted components are Python and the raw artifact format; full
domain completeness additionally depends on the separately reviewed auditor.

`controls.json` preserves the historical positive index521 check and six
corrupted-artifact rejections. Corruptions bypass hash guards: changed gap,
negative cap weight, omitted domain, repeated domain, incorrect projection,
and incorrect exclusion flag. These tests attempt to falsify the arithmetic
checker rather than simply rerun the producer.

`baseline_and_matrix.json` binds the incumbent's raw exact interval check to
claim `C-STAR-BASELINE-18481`, revision 1. It also checks direct integer matrix
multiplication identities for all 3,486 outer pairs in each of four assignments:
all-zero unknown edges, all-one, seeded binary, and seeded sparse. The
machine-readable report records the population of four assignments and
3,486 pair identities each.
The universal validity comes from the algebraic derivation above; these four
controls are not an exhaustive proof over unknown-edge assignments.

Fresh baseline completeness replay and shortlist raw checking, if complete,
are recorded in separate immutable JSON reports rather than inferred from
this written note. No result is promoted solely because agents agree.

## Reproduction

Run from the repository root using the pinned `uv.lock` environment. The
actual interpreter path in this session is `build/research-venv/Scripts/python.exe`
(Python 3.12); use the exact commands in each JSON report. The scripts accept
a fresh `--out` path and refuse to overwrite existing evidence.

    uv sync --locked
    uv run --locked python acceleration/audit_20260917_fresh_review.py --out <fresh-controls.json>
    uv run --locked python acceleration/audit_20260917_matrix_controls.py --out <fresh-baseline.json>
    uv run --locked python acceleration/audit_20260917_fresh_review.py --run acceleration/results/20260917_fresh_star_shortlist --out <fresh-batch.json>

No native DLL, numerical solver, GPU, or SAT invocation is made by these new
checkers. The report hashes bind the actual inputs and checking source.
