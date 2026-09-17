"""Freeze the verified one-coordinate family result and its continuation."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()


def save(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2);f.write('\n')


def main():
    resume=Path('acceleration/results/20260917_resume')
    snapshot=resume/'claims_at_fifth_milestone.yaml';assert not snapshot.exists()
    snapshot.write_bytes(Path('CLAIMS.yaml').read_bytes())
    paths=dict(ledger=snapshot.as_posix(),previous_ledger=(resume/'claims_at_fourth_milestone.yaml').as_posix(),
        validation=(resume/'coordinate_coverage_ledger_validation_v2.json').as_posix(),
        parent='acceleration/results/20260917_whole_star_rerank_v3_checkpoint.json',
        positive='acceleration/results/20260917_independent_review/moment_positive600.json',
        binding='acceleration/results/20260917_independent_review/moment_positive600_claim_binding.json',
        filter='acceleration/results/20260917_independent_review/partial_matching_filter/summary.json',
        universe='acceleration/results/20260917_independent_review/coordinate_universe.json',
        coverage='acceleration/results/20260917_independent_review/coordinate_coverage.json',
        domains='acceleration/results/20260917_independent_review/partial_matching/summary.json',
        model='acceleration/results/20260917_independent_review/partial_moments.json',
        execution='acceleration/results/20260917_partial_matching_moment_replay600/summary.json')
    data={k:(yaml.safe_load(Path(p).read_bytes()) if 'ledger' in k else json.loads(Path(p).read_bytes())) for k,p in paths.items()}
    hashes={k:digest(p) for k,p in paths.items()}
    assert hashes['parent']=='ce0ebb9f245502724979dcc7e90ac988662609786bc0a9f245774b0b08055442'
    assert data['validation']['valid'] and data['validation']['provenance']['input_hashes']['ledger']['sha256']==hashes['ledger']
    ledger=data['ledger'];prior={c['id'] for c in data['previous_ledger']['claims']}
    changes=[{k:c[k] for k in ('id','revision','status','review_state','scope')} for c in ledger['claims'] if c['id'] not in prior]
    assert len(changes)==4 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in changes)
    assert data['positive']['exact_bound']['numerator']==590533056 and data['positive']['checked_original_choices']==54478
    refs={p:hashes[k] for k,p in paths.items()}
    for k in ('positive','binding','filter','universe','coverage','domains','model'):
        for p,h in data[k].get('inputs_sha256',{}).items():
            assert digest(p)==h,p
            if p in refs:assert refs[p]==h,p
            refs[p]=h
    now=datetime.now(timezone.utc).isoformat();commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    checkpoint_path='acceleration/results/20260917_partial_coordinate_checkpoint.json'
    checkpoint=dict(status='VERIFIED_CONDITIONAL_PARTIAL_COORDINATE_CHECKPOINT',created_utc=now,source_commit=commit,
        previous_checkpoint_preserved=dict(path=paths['parent'],sha256=hashes['parent']),
        inherited_reference_policy='Prior checkpoint remains immutable and retains all its own indexed references; this build checks its file hash but does not rerun or rehash the prior entire inventory.',
        target_resolution='UNKNOWN',graph_constructed=False,general_nonexistence_proved=False,
        current_best=data['parent']['current_best'],current_star_marginal_best=data['parent']['current_star_marginal_best'],
        no_new_seed_adoption=True,objectives_not_compared=True,
        verified_partial_family=dict(claim_id='C-PARTIAL-K-ONE-COORDINATE-EXCLUSION',revision=1,fixed_outer_edges=162,
            unknown_outer_edges=1740,original_domain_choices=54478,centers=84,exact_lower_bound='9227079/16384',
            objective='PARTIAL_K_FULL_CENTER_STAR_MOMENT_PHASE1_V1',scope_manifest=data['positive']['scope_manifest'],
            scope_manifest_sha256=data['positive']['scope_manifest_sha256'],prescribed_absences_retained=True),
        separate_matching_filter=data['filter']['counts'],
        matching_assignment_population=dict(count=data['universe']['matching_count'],unit='labeled legal perfect matching of the single freed coordinate',
            independently_counted=True,all_within_excluded_family=True,distinct_LP_instances_solved=1,historical_union_computed=False),
        referenced_files_sha256=refs,directly_hash_checked_reference_count=len(refs),
        next_experiment='Two-sign-coordinate family with156 fixedK and1800 unknown edges; separate complete-domain/model gates and fresh exact certificate needed.',
        process_state='UNKNOWN; checkpoint indexing does not inspect live processes',
        overall_search_coverage='UNKNOWN; no validated denominator',builder_sha256=digest(__file__))
    save(checkpoint_path,checkpoint)
    report=dict(as_of=now,source_commit=commit,previous_report='docs/RESEARCH_20260917_FOURTH_WAVE.md',
        checkpoint=checkpoint_path,checkpoint_sha256=digest(checkpoint_path),target=ledger['target'],claim_changes=changes,
        counts=dict(families_excluded=1,original_domain_choices=54478,independent_column_checks=54478,centers=84,
            moment_equations=3486,hard_reciprocity_equations=1740,legal_coordinate_assignments=data['universe']['matching_count'],
            original_filter_choices=data['filter']['counts']['original_count'],filter_rejections=data['filter']['counts']['rejected_count'],
            filter_survivors=data['filter']['counts']['surviving_count'],filter_empty_domains=data['filter']['empty_domains']),
        exact_lower_bound='9227079/16384',objective=checkpoint['verified_partial_family']['objective'],
        execution=dict(completed600_cap_run=data['execution'],other_processes='UNKNOWN; not inspected by generator'),
        input_paths=paths,input_sha256=hashes,script_sha256=digest(__file__),draft_pr='https://github.com/ikuto32/conway-99-graph/pull/1')
    save(resume/'fifth_milestone.json',report)
    claims='\n'.join('- `'+c['id']+'` revision '+str(c['revision'])+': '+c['scope']['description'] for c in changes)
    text=f'''# Fifth resumed milestone: an exact conditional family exclusion

Since the [fourth milestone](RESEARCH_20260917_FOURTH_WAVE.md), an exact
support-function certificate has excluded an entire one-coordinate family.
Independent raw-neighborhood arithmetic reproduced the certificate. Separate
matching filtering, population counting and scope inclusion were also checked.

**As of:** {now}; source `{commit}` plus hash-bound new sources;
checkpoint `{report['checkpoint_sha256']}`.

**Verdict:** target resolution UNKNOWN. No complete99-vertex target graph or
general nonexistence proof. No target-resolution external review is claimed.
The result fixes162outer edges and the recorded absent edges; only60coordinate
edges and1680disjoint-support edges vary. No automorphism is assumed.

**Verified changes:**

{claims}

**Work completed:** one conditional family excluded using all54,478 unfiltered
local stars over84centers. The independent checker reconstructed every column
directly from full neighborhoods with Python integers and checked all84maxima.
Nine rooted rook9 controls, their RHS/column corruptions, an altered bound,
an out-of-box weight and zero weights calibrated that path.

The separate matching filter removes13,105 of54,478local choices, leaving41,373
with no empty domain. It was not needed for the family certificate. The complete
coordinate list has6,040distinct matchings; all pass partial upper caps. An
independently reviewed inclusion argument places each assignment's completion
problem inside the excluded family. These are6,040coordinate assignments,
not6,040independently solved LP instances or completed graphs. Pipeline units
are separate and must not be added.

**Coverage:** all6,040assignments in this one frozen coordinate population are
covered by the conditional exclusion. No union with earlier fixed-case
exclusions was computed. Overall search coverage: UNKNOWN; no validated denominator.

**Best result:** the exact bound `9227079/16384 > 0` is a lower bound on the
L1full-common-neighbor moment residual over the stated star simplices with
hard reciprocal equalities. Every admitted target completion would have zero
residual, yielding the contradiction. The bound need not be optimal. It is
not comparable with the older original-star or edge objectives; their incumbent
records are retained separately.

**Execution:** the600-second-capped attempt completed after
{data['execution']['solve_seconds']}solver seconds. Earlier60and240second
attempts timed out; their invalid vectors and negative exact extractions are
preserved. The successful certificate depends on exact arithmetic, not the
solver's floating-point optimality report. Other live process states are not
inferred from this saved report.

**Problems:** no unrestricted conclusion follows from the fixed configuration.
Initial registry attempts rejected a wrong dependency key and a missing
explicit null; both failed before changing the ledger and their evidence is
retained. These engineering corrections changed no mathematical result.
Artifact availability is updated separately only after confirmed publication.

**Next experiment:** free both sign coordinates of the same root group, leaving
156fixed outer edges. Require fresh domain and integer-model checks. Recompute
any transferred certificate on every enlarged-domain column; if nonpositive,
use the separately preregistered bounded new LP solve.

**References:** [ledger](../CLAIMS.yaml), [exact arithmetic audit](../{paths['positive']}),
[scope/binding correction](../{paths['binding']}), [matching population](../{paths['universe']}),
[coverage proof](AUDIT_20260917_COORDINATE_FAMILY_COVERAGE.md),
[checkpoint](../{checkpoint_path}),
[saved milestone](../acceleration/results/20260917_resume/fifth_milestone.json),
[draft PR1]({report['draft_pr']}),
[source commit](https://github.com/ikuto32/conway-99-graph/commit/{commit}).
'''
    with Path('docs/RESEARCH_20260917_FIFTH_WAVE.md').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
    print(json.dumps(dict(claims=[c['id'] for c in changes],checkpoint=checkpoint_path,checkpoint_sha256=report['checkpoint_sha256'],indexed_references=len(refs))))


if __name__=='__main__':main()
