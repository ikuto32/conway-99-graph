"""Generate the first resumed milestone from ledger and immutable run records."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml

ROOT=Path(__file__).resolve().parents[1]


def main():
    names=dict(ledger='CLAIMS.yaml',run='acceleration/results/20260917_fresh_star_shortlist/summary.json',
        independent='acceleration/results/20260917_independent_review/claim_bindings.json',
        checkpoint='acceleration/results/20260917_fresh_star_checkpoint.json',
        observation='acceleration/results/20260917_resume/execution_observation.json',
        validation='acceleration/results/20260917_resume/verified_ledger_validation_corrected.json')
    hashes={k:sha256((ROOT/p).read_bytes()).hexdigest() for k,p in names.items()}
    ledger=yaml.safe_load((ROOT/names['ledger']).read_text(encoding='utf-8'))
    docs={k:json.loads((ROOT/p).read_bytes()) for k,p in names.items() if k!='ledger'}
    assert docs['validation']['valid']
    assert docs['validation']['provenance']['input_hashes']['ledger']['sha256']==hashes['ledger']
    claims=[c['id'] for c in ledger['claims'] if c['status']=='VERIFIED' and c['review_state']=='CLEAR']
    run,independent,checkpoint=docs['run'],docs['independent'],docs['checkpoint']
    counts=dict(ranked_candidates=checkpoint['ranking_attempted_candidates'],selected_candidates=len(run['records']),
        attempted_star_evaluations=sum('result_path' in r for r in run['records']),
        completed_exact_pipeline_evaluations=sum(r['audited'] for r in run['records']),
        independently_checked_distinct_K=independent['independent_raw_passes'],
        fixed_K_exclusions=run['exact_fixed_K_exclusions'],strict_merit_improvements=run['exact_strict_improvement_count'],
        pending_cases=len(run['pending_candidates']),edge_warm_runs=run['edge_LP_runs'])
    report=dict(as_of=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        previous_report='docs/STOP_20260916_FRESH_STAR.md',checkpoint=names['checkpoint'],checkpoint_sha256=hashes['checkpoint'],
        target=ledger['target'],current_verified_claims=claims,counts=counts,
        best_incumbent=checkpoint['current_star_marginal_best']['exact_interval'],best_selected=independent['best'],
        execution_observation=docs['observation'],input_paths=names,input_sha256=hashes,
        counting_scope='Each stage has its own population; pipeline counts overlap and are never summed.',
        source_script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    with (ROOT/'acceleration/results/20260917_resume/milestone.json').open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2);stream.write('\n')
    text=f'''# Resumed fresh-star milestone, 2026-09-17

Changes since [the saved stop](STOP_20260916_FRESH_STAR.md): the selected fresh-star
evaluation and separate raw-artifact review are complete. The current claim ledger
is now [root CLAIMS.yaml](../CLAIMS.yaml); the pinned historical ledger is unchanged.

**As of:** {report['as_of']}; computational source `{report['source_commit']}` plus
the explicitly hashed new tooling; checkpoint `{hashes['checkpoint']}`.

**Verdict:** repository target resolution UNKNOWN. No complete target graph or
general nonexistence proof; no target-resolution external review.

**Verified changes:** `C-STAR-BASELINE-18481` revision1 freshly checks the exact
incumbent interval and fixed-K exclusion. `C-FRESH-STAR-16-EXCLUSIONS` revision2
excludes precisely the 16 selected fixed configurations.
`C-FRESH-STAR-16-NO-IMPROVEMENT` revision1 proves that each of their exact lower
bounds exceeds the incumbent upper bound. Same-fiber edges and all unlisted
overlapping-support edges are fixed absent. No nontrivial automorphism is assumed.

**Work completed:** {counts['ranked_candidates']} previously ranked candidates;
{counts['selected_candidates']} selected configurations; {counts['attempted_star_evaluations']} attempted star evaluations;
{counts['completed_exact_pipeline_evaluations']} completed exact pipelines;
{counts['independently_checked_distinct_K']} separately checked distinct configurations;
{counts['strict_merit_improvements']} improvements; {counts['pending_cases']} pending cases.
These pipeline populations overlap and must not be summed. The remaining112
ranked configurations were not evaluated by this wave.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator.
This wave evaluates16 of the128 previously ranked configurations only.

**Best result:** incumbent18481 retains its exact interval, approximately
[5.374367028255648,5.3743670369854]. Selected index67 is best in this batch,
approximately[7.00134161058368,7.0013416347365816]. Both use the same original-star
simplex reciprocity/cap violation objective; lower is better. Exact fractions are
in the linked audit. The positive bounds exclude the respective fixed K and do
not measure distance to an SRG.

**Execution:** the 16-case invocation exited0 at its saved receipt time. The next
same-sign whole-matching driver and GPU search were observed live at
{docs['observation']['observed_at']}; this is a dated observation, not a promise of
continued execution. The separate new triangle-matching filter remains CANDIDATE
pending independent review and is not included in verified totals here.

**Problems:** no candidate errors, timeouts or pending certificates in this wave.
Initial sandbox restrictions required native-library/read-access retries.
The first ledger impact check falsely rejected a new downstream claim; that failed
report is preserved, the checker was corrected with regression controls, and
the subsequent impact check passes. This bookkeeping correction does not alter
the mathematical artifacts. Some inherited checkpoint dependencies remain
local-only; hash identity alone does not provide public replay. New artifacts
are initially LOCAL_ONLY until their publication commit is available.

**Next experiment:** execute the preregistered [whole same-sign matching wave](NEXT_20260917_SAME_MATCHING.md)
from this checkpoint, to seek a strictly improved exact star interval. In parallel,
independently audit the stronger local triangle-matching filter.

**References:** [run summary](../{names['run']}),
[independent claim binding](../{names['independent']}),
[written derivation](../acceleration/results/20260917_independent_review/MATHEMATICAL_AUDIT.md),
[checkpoint](../{names['checkpoint']}),
[machine-readable milestone](../acceleration/results/20260917_resume/milestone.json),
[claim schema and migration](CLAIMS_SCHEMA.md).
The immutable publication commit and draft PR are recorded separately after push.
'''
    with (ROOT/'docs/RESEARCH_20260917_FRESH_STAR.md').open('x',encoding='utf-8') as stream:
        stream.write(text)
    print(json.dumps(dict(counts=counts,verified_claims=claims)))


if __name__=='__main__':main()
