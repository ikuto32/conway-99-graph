"""Freeze verified four-coordinate exclusion and subsequent checked prerequisites."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import yaml


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2);f.write('\n')


def main():
    base='acceleration/results/20260917_';resume=base+'resume/';rev=base+'independent_review/'
    snapshot=resume+'claims_at_eighth_milestone.yaml';assert not Path(snapshot).exists()
    current=yaml.safe_load(Path('CLAIMS.yaml').read_bytes());previous=yaml.safe_load(Path(resume+'claims_at_seventh_milestone.yaml').read_bytes())
    old={c['id']:c for c in previous['claims']}
    changes=[{k:c[k] for k in ('id','revision','status','review_state','statement','scope')}for c in current['claims'] if c['id']not in old or c['revision']!=old[c['id']]['revision']]
    assert len(changes)==7 and all(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in changes)
    paths=dict(parent=base+'four_coordinate_foundations_checkpoint.json',four_bound=rev+'four_matching_filtered_run01_bound.json',
        four_binding=rev+'four_matching_exclusion_claim_binding.json',six_domains=rev+'six_matchings/summary.json',
        six_filter=rev+'six_coordinate_matching_filter/summary.json',six_model=rev+'six_filtered_moments.json',
        failed_four_transfer=rev+'filtered_four_weight_transfer/summary.json',failed_six_transfer=rev+'six_filtered_transfer.json',
        rook=rev+'rook_regular_set_recheck.json',gpu_parity=rev+'moment_pdhg_gpu_cpu_parity_v2/summary.json',
        public_replay=base+'two_coordinate_public_replay/replay_receipt.json',
        process_observation=resume+'eighth_solver_process_observation.json')
    reports={k:read(p)for k,p in paths.items()};refs={p:digest(p)for p in paths.values()}
    for key in ('four_bound','four_binding','six_domains','six_filter','six_model','failed_four_transfer','failed_six_transfer','rook','gpu_parity'):
        for p,h in reports[key]['inputs_sha256'].items():
            assert digest(p)==h,p
            assert p not in refs or refs[p]==h,p
            refs[p]=h
    assert reports['four_bound']['exact_bound']['numerator']==275944444 and reports['four_bound']['conditional_family_exclusion']
    assert reports['six_filter']['counts']['original_count']==879449 and reports['six_filter']['counts']['surviving_count']==712721
    assert reports['six_model']['shape']==[5610,719693]
    Path(snapshot).write_bytes(Path('CLAIMS.yaml').read_bytes());refs[snapshot]=digest(snapshot)
    now=datetime.now(timezone.utc).isoformat();commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    checkpoint=base+'four_coordinate_exclusion_checkpoint.json'
    counts=dict(claim_records=len(current['claims']),verified_clear=sum(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in current['claims']),four_original_choices=290460,four_rejected_by_necessary_filter=59581,four_retained_choices_exactly_scored=230879,six_original_choices=879449,six_rejected_by_necessary_filter=166728,six_surviving_choices=712721,gpu_parity_inputs=4,gpu_checkpoints_per_input=4)
    data=dict(created_utc=now,source_commit=commit,status='VERIFIED_FOUR_COORDINATE_CONDITIONAL_EXCLUSION_CHECKPOINT',target_resolution='UNKNOWN',
        previous_checkpoint_preserved=dict(path=paths['parent'],sha256=refs[paths['parent']]),current_best=reports['parent']['current_best'],current_star_marginal_best=reports['parent']['current_star_marginal_best'],no_seed_adoption=True,
        claim_changes=changes,counts=counts,verified_family=dict(claim_id='C-PARTIAL-K-FOUR-COORDINATE-EXCLUSION',revision=1,fixed_outer_edges=144,unknown_outer_edges=1920,prescribed_absences_retained=True,exact_lower_bound='68986111/262144'),
        six_coordinate_exclusion_established=False,rook_encoding_conditional=True,rook_historical_checker_source_missing=True,rook_current_check_independent_of_missing_source=True,
        numerical_gpu_parity_is_not_a_certificate=True,referenced_files_sha256=refs,directly_hash_checked_reference_count=len(refs),
        execution_observation=reports['process_observation'],execution_observation_is_historical_not_current_liveness=True,
        next_experiment='Continue separately capped six-coordinate CPU solve and independently gated GPU weight search; check all resulting certificates directly from raw neighborhoods.',
        overall_search_coverage='UNKNOWN; no validated denominator',draft_pr='https://github.com/ikuto32/conway-99-graph/pull/2',builder_sha256=digest(__file__))
    save(checkpoint,data)
    save(resume+'eighth_milestone.json',dict(as_of=now,source_commit=commit,previous_report='docs/RESEARCH_20260917_SEVENTH_WAVE.md',checkpoint=checkpoint,checkpoint_sha256=digest(checkpoint),claim_changes=changes,counts=counts,target=current['target'],input_paths=paths,referenced_files_sha256=refs,draft_pr=data['draft_pr']))
    print(json.dumps(dict(checkpoint=checkpoint,sha256=digest(checkpoint),counts=counts,changes=len(changes),references=len(refs))))


if __name__=='__main__':main()
