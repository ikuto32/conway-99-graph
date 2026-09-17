# Independently verified update

`C-FILTERED-STAR-LP-18481` revision1 is VERIFIED/CLEAR in
[the root ledger](../CLAIMS.yaml). Every integer model row and the rational
primal/dual interval were independently checked: approximately
[11.464794729497703,11.464794852600662] for the explicitly separate filtered-domain
objective. See [written audit](../acceleration/results/20260917_independent_review/FILTERED_STAR_LP_AUDIT.md)
and [second milestone](RESEARCH_20260917_SECOND_WAVE.md). Baseline18481 was already
excluded; this is another fixed-assignment obstruction, not a target result.

## Preserved producer-stage report

# A separate phase-I objective on matching/pair-filtered domains

The numerical pilot completed. Its outputs are **CANDIDATE pending independent
exact verification**. The objective is explicitly named
`TRIANGLE_PAIR_FILTERED_STAR_SIMPLEX_V1`; it uses the 15,335 sound surviving
star choices from the independently checked matching/pair reduction of
baseline18481. No original-complete-domain flag or historical objective
label is reused.

This model's numerical value is not directly compared to the older
original-domain value or used as evidence of target-wide progress. Its
feasible domain is different. Baseline18481 was already excluded; even an
independently certified positive bound here supplies only another obstruction
for that fixed overlap assignment.

## Exact definition

For each outer vertex `u`, let `D(u)` be the saved matching/pair-filtered
original-ID domain. Choose probabilities `p(u,S) >= 0` summing to one over
`S in D(u)`. Write `m(u,v) = sum[p(u,S) : v in S]`. For each disjoint-support
pair `u<v`, define `x_uv=m(u,v)`, using the smaller indexed endpoint. Let
`a_q x <= b_q` be the 3,486 retained linear common-neighbor caps derived from
the fixed full99 partial graph. The new objective is

```text
minimize sum_(disjoint u<v) |m(u,v)-m(v,u)|
       + sum_(outer pairs q) max(0, a_q x-b_q),
```

over the 84 hard simplexes. Direction: minimize. Reciprocal equality is
penalized symmetrically, while cap excess is penalized positively. For a
valid completion every term is zero. Conversely, zero for this continuous
relaxation is not a complete graph or an exact existence certificate.

The equivalent linear program has 15,335 probability variables, 6,846
nonnegative violation slacks, and 5,250 rows: 84 hard normalizations, 1,680
reciprocal equalities, and 3,486 upper caps. Every slack has cost one. The
saved model has 679,939 nonzero integer coefficients. Its exact CSR arrays,
row bounds, variable bounds, costs, row/column conventions, and frozen
original-ID domain map are preserved independently of the solver state.

## Numerical result and limitations

The normalized stored probability point evaluates numerically to
`11.464794852600686`. Clipped box-feasible dual weights yield a numerical
simplex-support lower-bound estimate of `11.464794729497669`. These numbers
are heuristic until checked with exact arithmetic. HiGHS reports an optimal
solution; that status is not a certificate.

The run used HiGHS interior point with crossover disabled, one thread, and
a 30-second solver limit. The observed solve interval was 5.097253 seconds
and no solver time limit was hit. This is one observed run, not a general
performance claim. The pinned dependency versions and exact command are in
the pre-run manifest. Positive and deliberately tightened-cap two-variable
controls check the producer's slack signs against known objective values
zero and one, with numerical tolerance `1e-8`; independent controls remain
the verifier's responsibility.

For exact certification the verifier must reconstruct graph cap terms and
the filtered original-ID columns independently. Interpret the stored finite
binary64 probabilities and dual weights as exact rationals. Normalize each
probability simplex exactly to obtain an upper bound. Clear dual
denominators and evaluate the sum of per-vertex minimum star costs minus
the weighted cap right-hand sides to obtain an exact lower bound. The
independent matching/pair proof is the explicit soundness premise allowing
this reduced domain to represent all possible graph completions.

## Reproduction and evidence

Producer: `acceleration/theory_20260917_filtered_star_lp.py`. The numerical
producer discloses reuse of `audit_phase1.graph_rows` and its graph helpers;
the separate verifier must not rely on those shared helpers to establish
the mathematical model. The historical star LP producer and auditor were
not invoked or modified.

Source commit at execution: `3daebfb05d39aa31afea6fdbb6b80d6b108f1262`.
New source bytes are additionally hash-bound in the manifest. Evidence is in
`acceleration/results/20260917_theory/filtered_star_lp_baseline18481/`:

- `manifest.json`: question, selection, domain scope, prerequisites, command,
  versions, limits, thresholds, and all dependency hashes.
- `frozen_domains.json`: every chosen original ID and mask, bound to the
  independent reduction report.
- `exact_model.json.gz`: complete integer augmented CSR model, with explicit
  reasons for the null values representing infinite bounds.
- `phase1.json`: round-trip binary64 probabilities and clipped dual weights,
  numerical objective components, and exact scope flags.
- `raw_highs_solution.json` and `highs.log`: original solver values, duals,
  status, and progress output.
- `controls.json` and `summary.json`: calibration outcomes and output hashes.

Summary SHA256:
`833387775636e2c65f5f4b9418a059f4befd014bc33c948102546b2d46f44a1c`.
Integer model SHA256:
`e8f180a38e14ad397aae60414e715ca046b93f96e0ae79250e46b0dec7cb220f`.

Replay into a fresh output directory using the existing locked environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_filtered_star_lp.py --out build/filtered_star_lp_replay --seconds 30
```

The saved model and raw solver state allow exact checking after the numerical
process exits; no work remains running. The next action is independent
exact lower/upper certification on this named objective and scope. Overall
search coverage: UNKNOWN; no validated denominator.
