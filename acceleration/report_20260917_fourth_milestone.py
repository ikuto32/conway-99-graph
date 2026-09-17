"""Freeze the next ledger-derived milestone; no mathematical checking here."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml


def main():
    root=Path(__file__).resolve().parents[1]
    resume=root/'acceleration/results/20260917_resume'
    snapshot=resume/'claims_at_fourth_milestone.yaml'
    assert not snapshot.exists()
    snapshot.write_bytes((root/'CLAIMS.yaml').read_bytes())
    paths=dict(ledger=snapshot.relative_to(root).as_posix(),
        previous_ledger='acceleration/results/20260917_resume/claims_at_third_milestone.yaml',
        ranking='acceleration/results/20260917_independent_review/rerank_v3_results.json',
        scope='acceleration/results/20260917_independent_review/rerank_v3_16_scope.json',
        execution='acceleration/results/20260917_rerank_v3_shortlist_execution/receipt.json',
        checkpoint='acceleration/results/20260917_whole_star_rerank_v3_checkpoint.json',
        partial='acceleration/results/20260917_independent_review/partial_matching/summary.json',
        oddsets='acceleration/results/20260917_independent_review/partial_oddsets.json',
        moments='acceleration/results/20260917_independent_review/partial_moments.json',
        validation='acceleration/results/20260917_partial_matching_moments/claims_validation.json')
    data={k:(yaml.safe_load((root/p).read_bytes()) if 'ledger' in k else json.loads((root/p).read_bytes())) for k,p in paths.items()}
    hashes={k:sha256((root/p).read_bytes()).hexdigest() for k,p in paths.items()}
    assert data['validation']['valid'] and data['validation']['provenance']['input_hashes']['ledger']['sha256']==hashes['ledger']
    ledger=data['ledger']; prior={c['id'] for c in data['previous_ledger']['claims']}
    changes=[{k:c[k] for k in ('id','revision','status','review_state','scope')} for c in ledger['claims'] if c['id'] not in prior]
    assert len(changes)>=6 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in changes)
    rank,scope,partial,odd,moment=(data[k] for k in ('ranking','scope','partial','oddsets','moments'))
    counts=dict(reranked_existing_candidates=len(rank['records']),new_candidates=0,
        eligible_untested_candidates=scope['eligible_ranked_population'],selected_evaluations=len(scope['selected_indices']),
        independently_checked_configurations=scope['independent_raw_passes'],original_star_choices_checked=scope['domain_choices_checked'],
        worse_than_incumbent=len(scope['strictly_worse_indices']),better_than_incumbent=len(scope['strictly_better_indices']),
        unseparated_intervals=len(scope['unseparated_intervals']),partial_centers=partial['centers'],partial_domain_choices=partial['domain_choices'],
        odd_subsets=odd['odd_subsets'],violated_saved_point_masks=odd['strictly_violated_masks'])
    now=datetime.now(timezone.utc).isoformat();commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    best=scope['best']; best_display={k:v for k,v in best.items() if k not in ('exact_lower','exact_upper')}
    best_display.update(lower_approximate=best['exact_lower']['approximate'],upper_approximate=best['exact_upper']['approximate'])
    report=dict(as_of=now,source_commit=commit,previous_report='docs/RESEARCH_20260917_THIRD_WAVE.md',
        checkpoint=paths['checkpoint'],checkpoint_sha256=hashes['checkpoint'],target=ledger['target'],claim_changes=changes,
        counts=counts,best_selected=best_display,
        calibration={k:v for k,v in rank['calibration_metrics'].items() if k not in ('pair_records','ambiguous_pair_ids')},
        moment_model={k:moment[k] for k in ('shape','nonzeros','probability_columns','hard_simplex_rows','hard_reciprocity_rows','soft_moment_equalities','solver_outcome')},
        execution=dict(completed_shortlist_receipt=data['execution'],other_processes='UNKNOWN; this report generator does not observe live processes'),
        input_paths=paths,input_sha256=hashes,script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        next_experiment='Exact support-function extraction and a separately preregistered longer same-model solve if the first extraction is nonpositive.',
        draft_pr='https://github.com/ikuto32/conway-99-graph/pull/1')
    with (resume/'fourth_milestone.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    claims='\n'.join('- `'+c['id']+'` revision '+str(c['revision'])+': '+c['scope']['description'] for c in changes)
    text=f'''# Fourth resumed milestone: reranked shortlist and partial-coordinate model

Since the [third milestone](RESEARCH_20260917_THIRD_WAVE.md), another frozen
16-configuration shortlist has passed independent exact checks. A larger
partial-coordinate domain and a full common-neighbor moment relaxation have
also been independently checked. These are scoped results, not a resolution.

**As of:** {now}; source `{commit}` plus separately hash-bound new sources;
checkpoint `{hashes['checkpoint']}`.

**Verdict:** repository target resolution UNKNOWN. No validated target graph or
general nonexistence proof; no target-resolution external review.

**Verified changes:**

{claims}

**Work completed:** {counts['reranked_existing_candidates']} existing candidates
reranked at 5,000 cold iterations, zero new candidates. The frozen union policy
selected {counts['selected_evaluations']} of {counts['eligible_untested_candidates']}
previously untested candidates. Independent checking covered
{counts['original_star_choices_checked']:,} original star choices across those
{counts['independently_checked_configurations']} configurations. Every selected
configuration has a positive exact lower bound in its fixed-edge scope;
{counts['better_than_incumbent']} improves the incumbent and
{counts['unseparated_intervals']} has an unseparated comparison interval.
Ranking and evaluation stages overlap and are not summed.

The separate partial-coordinate model has {counts['partial_domain_choices']:,}
complete local choices over {counts['partial_centers']} centers. It holds 162
outer edges fixed, frees 60 possible matching-coordinate edges, and retains
1,680 disjoint-support unknown edges with the documented prescribed absences.
The saved numerical point violates one of {counts['odd_subsets']:,} tested odd
subsets by approximately 3.92e-15, while its degree/reciprocity equalities are
not exact. This is a point diagnostic, not a family obstruction.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator.
The selection fraction describes this finite batch only. No automorphism of a
hypothetical target graph is assumed.

**Best result:** original-domain incumbent18481 remains approximately
[5.374367028255648, 5.3743670369854]. Best new selected index66083 has exact
rational bounds displayed approximately as
[{best_display['lower_approximate']}, {best_display['upper_approximate']}].
Lower is better for this defined reciprocity/cap violation objective; these
positive values are conditional obstructions, not distances to a solution.
The partial-coordinate and full moment objectives have different feasible
domains/definitions and are not compared numerically with this objective.

**Execution:** the shortlist invocation completed at
{data['execution']['finished_at']} with exit0 and final independent review.
Other process states are not inferred by this saved report.

**Problems:** the strengthened odd-set LP and initial full moment LP reached
their separate 60-second solver caps without valid primal or dual solutions.
Their raw objective fields of zero are unusable. The moment model's complete
integer matrix was independently checked, but that does not establish
feasibility or exclusion. The saved original failure records are preserved.
Four V3 numerical input copies totaling 3,212,989,588 bytes remain LOCAL_ONLY;
selected-case exact artifacts are separate. Public availability is recorded
only after the corresponding commit is confirmed remote.

**Next experiment:** extract exact support-function bounds from arbitrary saved
finite weights, which need not be solver-certified dual solutions, then run
the same frozen model with a separately declared longer limit if necessary.
A matching-filter pilot is separately awaiting independent checking.

**References:** [ledger](../CLAIMS.yaml), [exact shortlist audit](../{paths['scope']}),
[full moment audit](../{paths['moments']}), [checkpoint](../{paths['checkpoint']}),
[machine-readable milestone](../acceleration/results/20260917_resume/fourth_milestone.json),
[large-input catalog](../acceleration/results/20260917_whole_star_rerank_v3/local_artifacts.json),
[draft PR1]({report['draft_pr']}),
[source commit](https://github.com/ikuto32/conway-99-graph/commit/{commit}).
'''
    with (root/'docs/RESEARCH_20260917_FOURTH_WAVE.md').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
    print(json.dumps(dict(claims=[c['id'] for c in changes],counts=counts)))


if __name__=='__main__':main()
