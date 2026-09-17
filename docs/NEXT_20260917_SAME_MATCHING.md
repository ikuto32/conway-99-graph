# Preregistered follow-up: whole same-sign matching neighborhood

Created 2026-09-17, during the frozen fresh-star shortlist evaluation.
This document specifies a next experiment; it is not an execution receipt.

Question: can a whole same-sign matching change improve the current
`STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS` objective, or produce
a fixed configuration surviving its exact positive-bound exclusion?

Selection of seed: use `current_star_marginal_best` from the next hash-checked
checkpoint after all 16 current shortlisted cases and any pending restart
work are resolved. If none improves, retain index18481. Do not rerun this
fixed seed as an unresolved completion case: its positive exact star bound
already excludes it.

Family: all replacements of one of the 14 same-sign matching coordinates,
with the other 20 coordinates fixed, followed by the existing partial-graph
caps. This is a finite neighborhood of labeled overlap configurations with
same-fiber edges absent. No hypothetical completed-graph automorphism is
assumed. It covers neither all overlap configurations nor the unrestricted
target.

Use the frozen `continue_star_cp_round.py` pipeline through
`continue_star_cp_uv.py`, which only redirects child Python commands to the
locked uv interpreter. Complete native generation is checked by the existing
independent Python family enumerator. Old-edge GPU scores select 64 LP probes;
only the frozen near-zero rule feeds at most 32 star evaluations. Prior CP
probe exclusions remain active. Do not change selection after seeing results.

Success: exact rational upper bound strictly below the incumbent's exact
lower bound. A nonpositive lower bound is pending further completion tests,
not a feasibility certificate. A fixed-K exclusion requires complete local
domains and an independently checked positive integer certificate. A target
resolution requires the full separately checked graph or unrestricted proof.

Limits and thresholds: preserve the original pipeline's GPU iteration counts,
native node/domain caps, per-LP time limits, and unchanged `1e-7` edge audit
threshold. Its outer limits are 1800 seconds per ordinary stage and 3600 seconds
for star evaluation. A failure ends that invocation and preserves its files;
follow-up recovery requires new paths and an explicit deviation record.

Before execution record the actual parent checkpoint/hash, source commit,
command, uv.lock hash and hardware in a separate run manifest. The pipeline
records its exact selection and child commands. Checkpoint byte identity is
distinct from independent mathematical verification. No comparison to the
different old-edge objective is intended.
