"""Freeze ledger-derived whole-family and structural-cut milestone."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml

ROOT=Path(__file__).resolve().parents[1]


def main():
    snapshot=ROOT/'acceleration/results/20260917_resume/claims_at_third_milestone.yaml'
    assert not snapshot.exists()
    snapshot.write_bytes((ROOT/'CLAIMS.yaml').read_bytes())
    names=dict(ledger=snapshot.relative_to(ROOT).as_posix(),
        previous_ledger='acceleration/results/20260917_resume/claims_before_second_publication.yaml',
        validation='acceleration/results/20260917_resume/root_scaffold_ledger_validation.json',
        whole='acceleration/results/20260917_independent_review/whole16_scope.json',
        ranking='acceleration/results/20260917_whole_fresh_v2_balanced/ranking/summary.json',
        evaluation='acceleration/results/20260917_whole_fresh_v2_balanced/shortlist/summary.json',
        execution='acceleration/results/20260917_whole_shortlist_execution/receipt.json',
        cuts='acceleration/results/20260917_independent_review/matching_cut_application.json',
        cyclic='acceleration/results/20260917_independent_review/matching_cut_cyclic.json',
        normalization='acceleration/results/20260917_independent_review/root_scaffold.json',
        checkpoint='acceleration/results/20260917_whole_fresh_v2_checkpoint.json')
    data={k:(yaml.safe_load((ROOT/p).read_bytes()) if k.endswith('ledger') else json.loads((ROOT/p).read_bytes())) for k,p in names.items()}
    hashes={k:sha256((ROOT/p).read_bytes()).hexdigest() for k,p in names.items()}
    assert data['validation']['valid'] and data['validation']['provenance']['input_hashes']['ledger']['sha256']==hashes['ledger']
    ledger=data['ledger'];old={c['id'] for c in data['previous_ledger']['claims']}
    changes=[dict(id=c['id'],revision=c['revision'],status=c['status'],scope=c['scope']) for c in ledger['claims'] if c['id'] not in old]
    rank,ev,whole=data['ranking'],data['evaluation'],data['whole']
    counts=dict(requested_original_star_rankings=rank['requested_count'],scored_original_star_rankings=rank['scored_count'],
        unavailable_rankings=rank['unavailable_count'],selected_exact_evaluations=len(ev['records']),
        independently_checked_configurations=whole['independent_raw_passes'],original_choices_checked=whole['domain_choices_checked'],
        exact_exclusions=ev['exact_fixed_K_exclusions'],strict_improvements=ev['exact_strict_improvement_count'],
        pending_selected_cases=len(ev['pending_candidates']),edge_warm_runs=ev['edge_LP_runs'])
    now=datetime.now(timezone.utc).isoformat();commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    report=dict(as_of=now,source_commit=commit,previous_report='docs/RESEARCH_20260917_SECOND_WAVE.md',
        checkpoint=names['checkpoint'],checkpoint_sha256=hashes['checkpoint'],target=ledger['target'],claim_changes=changes,
        current_verified_claim_count=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),
        whole_counts=counts,identity_cut_counts=data['cuts']['totals'],cyclic_cut_counts=data['cyclic']['totals'],
        best_selected=whole['best'],execution=dict(completed_wave_receipt=data['execution'],other_processes='UNKNOWN; no live inspection performed by this report generator'),
        input_paths=names,input_sha256=hashes,script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        next_protocol='docs/NEXT_20260917_WHOLE_STAR_RERANK_V3.md',draft_pr='https://github.com/ikuto32/conway-99-graph/pull/1')
    with (ROOT/'acceleration/results/20260917_resume/third_milestone.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    claims='\n'.join('- `'+c['id']+'` revision '+str(c['revision'])+': '+c['scope']['description'] for c in changes)
    text=f'''# Third resumed milestone: whole-family shortlist and reusable cuts

Since [the second milestone](RESEARCH_20260917_SECOND_WAVE.md), another frozen
shortlist has completed independent exact checking. Reusable positive-edge
clauses and their finite applications have also been checked. A fresh written
audit establishes the every-root normalization; no novelty is claimed.

**As of:** {now}; computational source `{commit}` plus hash-bound new sources;
checkpoint `{hashes['checkpoint']}`. Its 7,357 referenced hashes are indexed;
that inventory count is not a mathematical progress measure.

**Verdict:** repository target resolution UNKNOWN. No complete target graph or
general nonexistence proof; no target-resolution external review.

**Verified changes:**

{claims}

**Work completed:** {counts['requested_original_star_rankings']} existing family
members selected for original-star ranking; {counts['scored_original_star_rankings']}
scored, {counts['unavailable_rankings']} unavailable. Of those, a frozen
{counts['selected_exact_evaluations']}-case union shortlist completed exact
pipelines and separate raw checking of {counts['original_choices_checked']}
original local choices. All {counts['exact_exclusions']} configurations are
excluded within their fixed-edge scope, with {counts['strict_improvements']}
strict improvements, {counts['pending_selected_cases']} pending selected cases,
and {counts['edge_warm_runs']} edge warm-start runs. Pipeline counts overlap.

The structural corpus is separately the previous 29 records, containing 747,064
original `(candidate, outer vertex, domain ID)` choices. Sixteen identity clauses
remove 324 distinct choices. The 896-map cyclic/sign bank has 14,336 distinct
clause images and removes exactly that same set: zero additional removals and
no empty domain. These clause/choice counts are not added to configuration counts.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator.
The exact shortlist is 16 of this 128-member ranking cohort. Neither that cohort
nor the chosen 896 relabelings exhausts the unrestricted target.

**Best result:** incumbent18481 remains approximately
[5.374367028255648,5.3743670369854]. Best selected index77958 is approximately
[{whole['best']['exact_lower']['approximate']},{whole['best']['exact_upper']['approximate']}].
Both are exact rational bounds displayed approximately for the original-domain
reciprocity/cap violation objective; lower is better. Each new exact lower bound
exceeds the incumbent upper bound. No seed was adopted. These positive bounds
are fixed-configuration obstructions, not distance-to-solution measurements.

**Execution:** the 16-case invocation completed at
{data['execution']['finished_at']} with exit0; its final independent reviews and
checkpoint indexing completed. Other process liveness is not inferred here.

**Problems and limits:** no selected-case failures or pending certificates. The
first cut audit's documentation hash became stale after a clarification; that
report was preserved and a fresh recheck binds the final unchanged theorem and
raw clauses. The frozen raw star checker retains an historical source-commit
field; a separate execution receipt records the actual observed source and
discloses uncaptured start provenance. Five large numerical-ranking inputs
remain LOCAL_ONLY (3,303,775,159 bytes); see their availability catalog. Exact
selected-case proofs use separately retained domains and certificates. New
artifacts remain LOCAL_ONLY until their publication commit is recorded.

**Next experiment:** cold 5,000-iteration reranking of the same 128 unchanged
models, with all 16 exact controls reported and a frozen shortlist policy among
the remaining 112 untested members. This generates no new candidates. Its
[protocol](NEXT_20260917_WHOLE_STAR_RERANK_V3.md) and
[calibration criteria](NEXT_20260917_WHOLE_STAR_RERANK_V3_CALIBRATION.md) precede
the numerical outputs. A separate bounded partial-coordinate pilot asks whether
one necessary LP can cover every completion of a freed matching coordinate.

**References:** [claim ledger](../CLAIMS.yaml), [whole16 audit](../{names['whole']}),
[cut application](../{names['cuts']}), [finite no-gain audit](../{names['cyclic']}),
[every-root derivation](../acceleration/results/20260917_independent_review/ROOT_SCAFFOLD_DERIVATION.md),
[checkpoint](../{names['checkpoint']}),
[machine-readable milestone](../acceleration/results/20260917_resume/third_milestone.json),
[large-input availability](../acceleration/results/20260917_whole_fresh_v2_balanced/ranking/local_artifacts.json),
[draft PR1]({report['draft_pr']}),
[immutable source commit](https://github.com/ikuto32/conway-99-graph/commit/{commit}).
New publication identity is recorded separately after push.
'''
    with (ROOT/'docs/RESEARCH_20260917_THIRD_WAVE.md').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
    print(json.dumps(dict(claim_changes=[c['id'] for c in changes],counts=counts)))


if __name__=='__main__':main()
