"""Freeze the second milestone from the claim ledger and saved checking records."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    names = dict(ledger='CLAIMS.yaml', validation='acceleration/results/20260917_resume/second_milestone_ledger_validation.json',
        same='acceleration/results/20260917_independent_review/same13_scope.json',
        run='acceleration/results/20260917_same_star_round/star_shortlist/summary.json',
        receipt='acceleration/results/20260917_same_execution/receipt.json',
        filtered='acceleration/results/20260917_independent_review/filtered_star_lp/audit.json',
        matching='acceleration/results/20260917_independent_review/matching_pair.json',
        checkpoint='acceleration/results/20260917_same_star_round/checkpoint.json')
    data = {k:json.loads((ROOT/p).read_bytes()) for k,p in names.items() if k!='ledger'}
    ledger = yaml.safe_load((ROOT/names['ledger']).read_bytes())
    hashes = {k:sha256((ROOT/p).read_bytes()).hexdigest() for k,p in names.items()}
    assert data['validation']['valid']
    assert data['validation']['provenance']['input_hashes']['ledger']['sha256']==hashes['ledger']
    same, run, filtered = data['same'], data['run'], data['filtered']
    previous = yaml.safe_load((ROOT/'acceleration/results/20260917_resume/claims_before_publication.yaml').read_bytes())
    old_ids = {c['id'] for c in previous['claims']}
    changes = [dict(id=c['id'],revision=c['revision'],status=c['status'],scope=c['scope']) for c in ledger['claims'] if c['id'] not in old_ids]
    counts = {k:same[k] for k in ['coarse_candidates','refined_candidates','edge_LP_cases','eligible_cases','selected_distinct_labeled_graphs','independent_raw_passes','unselected_eligible_cases']}
    counts.update(exclusions=run['exact_fixed_K_exclusions'],improvements=run['exact_strict_improvement_count'],pending=len(run['pending_candidates']))
    now = datetime.now(timezone.utc).isoformat()
    report = dict(as_of=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        previous_report='docs/RESEARCH_20260917_FRESH_STAR.md',target=ledger['target'],claim_changes=changes,
        counts=counts,best_same=same['best'],filtered_objective=filtered['objective_id'],
        filtered_exact_interval={k:filtered[k] for k in ['exact_lower','exact_upper']},
        execution=dict(same_wave='COMPLETED',receipt=data['receipt'],other_processes='UNKNOWN; this report performs no live-process inspection'),
        input_paths=names,input_sha256=hashes,script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        draft_pr='https://github.com/ikuto32/conway-99-graph/pull/1')
    with (ROOT/'acceleration/results/20260917_resume/second_milestone.json').open('x',encoding='utf-8') as f:
        json.dump(report,f,indent=2);f.write('\n')
    claim_lines='\n'.join('- `'+c['id']+'` revision'+str(c['revision'])+': '+c['scope']['description'] for c in changes)
    text=f'''# Second resumed milestone, 2026-09-17

Since [the first milestone](RESEARCH_20260917_FRESH_STAR.md), the whole-same-sign
wave and the matching-filter propagation/LP audits have completed. The
triangle-matching claim was separately verified between the two reports.

**As of:** {now}; source `{report['source_commit']}` plus explicitly hashed new
sources; checkpoint `{hashes['checkpoint']}`.

**Verdict:** repository target resolution UNKNOWN. No independently validated
target graph or general nonexistence proof; no target-resolution external review.

**Verified changes since the first publication:**

{claim_lines}

**Work completed:** {counts['coarse_candidates']} legal same-sign family members
coarsely ranked; {counts['refined_candidates']} refined; {counts['edge_LP_cases']}
old-edge LP cases; {counts['eligible_cases']} eligible original-star evaluations;
{counts['independent_raw_passes']} independently checked fixed configurations,
all excluded; {counts['improvements']} improvements and {counts['pending']} pending
selected cases. These overlapping pipeline populations must not be summed.
The separately checked matching-filter propagation leaves 15,335 original-ID
choices after 806 deletion events; this is not a graph count or a coverage measure.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator.
The same-sign family concerns replacement of one of14 coordinates of one seed;
the13 exclusions do not cover its81,000 members or the unrestricted target.

**Best result:** original-star incumbent18481 remains approximately
[5.374367028255648,5.3743670369854]; best selected index79792 is approximately
[{same['best']['exact_lower']['approximate']},{same['best']['exact_upper']['approximate']}].
Lower means less original-domain reciprocity/cap violation. These positive bounds
exclude the respective fixed assignments. The separate filtered-domain objective
`{filtered['objective_id']}` has exact certified endpoints displayed approximately
as [{filtered['exact_lower']['approximate']},{filtered['exact_upper']['approximate']}].
Its domain differs, so this value is not an original-objective ranking comparison.

**Execution:** the same-sign invocation completed with exit0 at
{data['receipt']['finished_at']}. All13 selected exact reviews and the filtered LP
review completed. This report does not assert that another process is live.

**Problems:** no selected-case timeout or pending certificate. An independent
scope check initially mistook an integer row count for a Boolean flag; that failed
attempt is preserved alongside the corrected check. No mathematical refutation
followed from this schema error. Isolated replay also exposed historical absolute
workspace paths; explicit guarded relocation is being audited separately.
New evidence remains LOCAL_ONLY in the ledger until publication is recorded.
Three large raw inputs have lossless gzip companions and a hash-checked recovery
manifest, preserving raw byte identity.

**Next experiment:** deterministically select128 unused, refined-score candidates
from the whole same-sign family, using64 by score and64 by coordinate/cycle
diversity; independently check the new whole-family mapping before ranking their
original-star domains and evaluating a frozen shortlist. No thresholds change
retroactively; see the next-wave preregistration when its preparation completes.

**References:** [authoritative claims](../CLAIMS.yaml),
[same13 scope audit](../{names['same']}), [matching/pair audit](../{names['matching']}),
[filtered LP audit](../{names['filtered']}), [checkpoint](../{names['checkpoint']}),
[machine-readable milestone](../acceleration/results/20260917_resume/second_milestone.json),
[draft PR1]({report['draft_pr']}). Exact fractions and command/hash inventories
are in those records. The source commit is
[3daebfb](https://github.com/ikuto32/conway-99-graph/commit/{report['source_commit']});
publication of new artifacts is recorded separately after push.
'''
    with (ROOT/'docs/RESEARCH_20260917_SECOND_WAVE.md').open('x',encoding='utf-8') as f:f.write(text)
    print(json.dumps(dict(changes=[c['id'] for c in changes],counts=counts)))


if __name__=='__main__':main()
