# Whole-family fresh v2: downstream shortlist protocol

This is a downstream implementation addendum to `NEXT_20260917_WHOLE_FRESH.md`, not a change to its frozen cohort or ranking protocol. The numerical ranking has completed; the original-star LP evaluations described here had not been launched when this addendum was prepared. Source commit: `938b32242532723a094b0fcf8729907d423a9951`, plus the source hashes in the preflight receipt.

The question is whether independently evaluated original-star phase-I intervals on the preregistered union shortlist improve the original-domain baseline18481 interval. This is a heuristic selection of fixed configurations. Neither the numerical ranking nor an exclusion of every selected configuration settles the unrestricted target. Overall search coverage: UNKNOWN; no validated denominator.

## Frozen selection and scope

`acceleration/evaluate_fresh_whole_v2.py` accepts only the honest whole-family ranking status and `whole_fresh_v2_balanced` producer. It checks the independent ranking audit, all declared input hashes, direct whole-family row identity, original candidate graph identity, and all alternating-cycle sizes. No cross-family label, index remapping, or conversion of original-domain audit flags is used.

The selection is the frozen union of eight lowest numerical upper scores and eight lowest numerical lower scores, with score ties broken by original index; duplicate selections retain both roles, and lowest upper-score unused rows fill the union to16. Selection is independently reproduced by the ranking checker. On the actual128 ranked/available rows the16 IDs are:

`51030,49629,71703,74803,50028,65848,1736,55055,77958,25999,10260,80479,46130,47816,41448,50849`.

The objective ID remains `ORIGINAL_STAR_SIMPLEX_PDHG_V1`: original84 star simplexes, reciprocity and linear common-neighbor cap violations. It does not use the triangle/pair-filtered objective. GPU values are floating-point ranking scores, not certificates. The exact LP is compared only with the baseline using this same original-domain objective.

## Independent checks and bounded execution

The adapter reuses the frozen evaluator's helper functions and its evaluation chain; this is disclosed shared producer code, not independent verification. Each selected graph gets fresh native original-star enumeration and pair propagation, followed by the separate pair checker, complete original-domain set identity check, original-star LP, separate exact rational audit and independent integer certificate replay. Native pair-pruned domains are never substituted for original domains in the LP. Only independently audited positive bounds exclude the particular fixed K. Failures/caps/nonpositive bounds remain pending.

Limits: original-star native enumeration30seconds,2,000,000nodes,20,000domains per row; native pair propagation30seconds,500,000,000checks; independent pair audit60seconds; LP30seconds per candidate; subprocess wall allowance240seconds. The numerical LP uses the pinned workspace solver configuration. Only the best independently positive strict original-star improver is eligible for the existing audited edge warm-start chain,30seconds; a warm-start failure remains pending. No SAT/DRAT invocation is part of this wave. Stop artifacts preserve every completed record and the active index.

The29 synthetic adapter controls cover positive/multicycle cases and malformed selection, scope, identity, scores, availability, metadata, and artifact association. These are producer engineering controls, not mathematical verification. The separate real preflight validates the genuine independent ranking PASS without launching a solver or creating the requested execution directory. Records:

- `acceleration/results/20260917_whole_fresh_v2_balanced/shortlist_adapter_controls.json`
- `acceleration/results/20260917_whole_fresh_v2_balanced/shortlist_preflight.log`
- `acceleration/results/20260917_whole_fresh_v2_balanced/shortlist_preflight_receipt.json`
- `acceleration/results/20260917_independent_review/whole_fresh_ranking.json`

## Exact restart/launch command

Run from the repository root in the existing locked environment. Use `--validate-only` instead of `--execute` for read-only preflight. The output directory must not already exist; an interrupted attempt is preserved and any retry requires a fresh output directory and explicit deviation record rather than overwriting evidence.

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/evaluate_fresh_whole_v2.py --ranking acceleration/results/20260917_whole_fresh_v2_balanced/ranking/summary.json --ranking-audit acceleration/results/20260917_independent_review/whole_fresh_ranking.json --ranking-auditor acceleration/audit_20260917_whole_fresh_ranking.py --ranking-auditor-sha256 580e2c4eeba8d50b18c8f207e6985f0ba318914d5d6cd69edc8e439c5569efd2 --baseline-star-audit acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/audit.json --out acceleration/results/20260917_whole_fresh_v2_balanced/shortlist --seconds 30 --audit-seconds 60 --execute
```

Actual source and artifact hashes, timestamps, command, and read-only outcome are bound in the receipt. Subsequent execution status belongs to its saved manifest/run record and live process observations; this document does not assert that a process is running.
