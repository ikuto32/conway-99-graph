"""Rebound semantic controls for recovery indexing; no scientific processes."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import build_recovered_star_checkpoint as b


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();b.require(not args.out.exists(),'Fresh QA output required')
    directory=b.resolve(args.round);book=b.Index();controls=[]
    original,view,audit,repairs=b.inspect_recovery(book,directory,directory/'recovery')
    manifest=book.read(directory/'manifest.json');failure=book.read(directory/'failure.json')
    b.check_stopped_round(manifest,failure)
    selected=b.select_from_cp(view,audit)
    b.require(selected and 19706 in [r['proposal_index'] for r in selected],'Actual strict-repaired near-zero candidate absent')
    repair_id=repairs['records'][0]['proposal_index']
    repair_pos=next(i for i,r in enumerate(view['records']) if r['proposal_index']==repair_id)
    other_pos=next(i for i,r in enumerate(view['records']) if r['proposal_index']!=repair_id)
    def reject(name,call):
        try:call()
        except (ValueError,KeyError,TypeError) as error:
            controls.append(dict(name=name,rejected=True,error=str(error)))
        else:raise ValueError('Accepted invalid control: '+name)
    mutations=[
        ('wrong_view_status',lambda o,v,a,r:v.update(status='BOUNDED_CP_MATCHING_SEARCH_FINISHED')),
        ('wrong_recovery_status',lambda o,v,a,r:a.update(status='INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS')),
        ('history_overwritten',lambda o,v,a,r:r.update(original_files_overwritten=True)),
        ('failure_hidden',lambda o,v,a,r:v.update(original_audit_failure_preserved=False)),
        ('relaxed_tolerance',lambda o,v,a,r:a.update(independent_LP_audit_tolerance=1e-6)),
        ('view_relaxed_tolerance',lambda o,v,a,r:v.update(audit_tolerance_changed=True)),
        ('wrong_family_scope',lambda o,v,a,r:v.update(coarse_candidate_count=v['coarse_candidate_count']+1)),
        ('invented_view_field',lambda o,v,a,r:v.update(invented_claim=True)),
        ('missing_original_field',lambda o,v,a,r:v.pop('producer_version')),
        ('lost_original_output',lambda o,v,a,r:v['outputs_sha256'].pop(next(iter(o['outputs_sha256'])))),
        ('changed_original_input_hash',lambda o,v,a,r:v['inputs_sha256'].__setitem__(next(iter(o['inputs_sha256'])),'0'*64)),
        ('reordered_selection',lambda o,v,a,r:v['records'].reverse()),
        ('duplicate_selection',lambda o,v,a,r:v['records'].__setitem__(0,deepcopy(v['records'][1]))),
        ('missing_independent_audit',lambda o,v,a,r:a['probe_reports'].pop()),
        ('extra_repair_index',lambda o,v,a,r:v['repaired_proposal_indices'].append(-1)),
        ('duplicate_repair',lambda o,v,a,r:r['records'].append(deepcopy(r['records'][0]))),
        ('extra_solver_run',lambda o,v,a,r:r.update(solver_runs=r['solver_runs']+1)),
        ('repair_candidate_changed',lambda o,v,a,r:v['records'][repair_pos].update(candidate_sha256='0'*64)),
        ('repair_selection_role_changed',lambda o,v,a,r:v['records'][repair_pos].update(selection_roles=['invented'])),
        ('unlisted_LP_changed',lambda o,v,a,r:v['records'][other_pos].update(numeric_objective=1234)),
        ('repair_map_candidate_changed',lambda o,v,a,r:r['records'][0].update(candidate_sha256='0'*64)),
        ('repair_map_old_hash_changed',lambda o,v,a,r:r['records'][0].update(original_result_sha256='0'*64)),
        ('repair_map_new_hash_changed',lambda o,v,a,r:r['records'][0].update(replacement_result_sha256='0'*64)),
        ('repair_not_optimal',lambda o,v,a,r:v['records'][repair_pos].update(optimal=False)),
        ('repair_wrong_original_failure',lambda o,v,a,r:r['records'][0].update(original_strict_audit_error='Other failure')),
        ('wrong_numeric_best',lambda o,v,a,r:v.update(best=v['records'][other_pos])),
        ('wrong_improvement_count',lambda o,v,a,r:v.update(numerical_improvement_count=999)),
        ('audit_reran_science',lambda o,v,a,r:a.update(LP_solver_or_family_enumeration_reruns=1)),
        ('CP_selection_not_replayed',lambda o,v,a,r:a.update(both_selection_stages_indices_roles_and_upper_only_ties_replayed=False)),
        ('CP_vectors_not_checked',lambda o,v,a,r:a.update(selected_saved_vectors_finite_and_exact_box_feasible=False)),
        ('one_LP_relaxed',lambda o,v,a,r:a['probe_reports'][other_pos]['phase1_audit'].update(numerical_tolerance=1e-6)),
    ]
    for name,change in mutations:
        data=deepcopy([original,view,audit,repairs]);change(*data)
        reject(name,lambda d=data:b.check_recovery_semantics(*d))
    for name,change in (
        ('original_round_finished',lambda m,f:f.update(status='STAR_GUIDED_CP_NEIGHBORHOOD_FINISHED')),
        ('wrong_failed_stage',lambda m,f:f.update(stage='search')),
        ('hidden_retry',lambda m,f:f.update(retries=1)),
        ('false_goal_completion',lambda m,f:f.update(goal_marked_complete=True)),
        ('missing_original_receipt',lambda m,f:f['completed_steps'].pop()),
        ('wrong_original_result',lambda m,f:f['completed_steps'][0].update(result_path='wrong.json')),
        ('wrong_original_result_status',lambda m,f:f['completed_steps'][0].update(status='PASS')),
    ):
        data=deepcopy([manifest,failure]);change(*data)
        reject(name,lambda d=data:b.check_stopped_round(*d))
    # Reuse loaded, hash-checked objects but mutate their semantic copies after
    # the cryptographic guard, ensuring errors are not mere changed-byte checks.
    class SemanticBook(b.Index):
        def __init__(self,path,change):
            super().__init__();self.verified=dict(book.verified);self.documents=book.documents
            self.path=b.key(path);self.change=change
        def read(self,path,status=None):
            value=deepcopy(super().read(path,status))
            if b.key(path)==self.path:self.change(value)
            return value
    fixed=repairs['records'][0]
    for name,path,change in (
        ('replacement_other_candidate',fixed['replacement_result_path'],lambda d:d.update(candidate_sha256='0'*64)),
        ('replacement_wrong_solver_tolerance',fixed['replacement_result_path'],lambda d:d['requested_solver_tolerances'].update(ipm_optimality_tolerance=1e-8)),
        ('replacement_wrong_producer',fixed['replacement_result_path'],lambda d:d['source_sha256'].__setitem__('phase1_probe_precise.py','0'*64)),
        ('replacement_metadata_objective_changed',fixed['replacement_result_path'],lambda d:d.update(numeric_objective=999)),
        ('stored_strict_audit_relaxed',fixed['strict_audit_path'],lambda d:d.update(numerical_tolerance=1e-6)),
        ('stored_strict_interval_changed',fixed['strict_audit_path'],lambda d:d['exact_primal_upper_bound'].update(numerator='999')),
        ('wrong_original_summary_binding',directory/'recovery/summary.json',lambda d:d.update(original_summary_path='wrong.json')),
        ('wrong_effective_summary_binding',directory/'recovery/audit.json',lambda d:d.update(effective_summary_path='wrong.json')),
    ):
        reject(name,lambda p=path,c=change:b.inspect_recovery(SemanticBook(p,c),directory,directory/'recovery'))
    inputs=dict(book.verified)
    for name,digest in b.PINS.items():
        inputs[b.key(b.ROOT/'acceleration'/name)]=book.bind(b.ROOT/'acceleration'/name,digest)
    for path in (Path(__file__),Path(b.__file__)):
        inputs[b.key(path)]=sha256(path.read_bytes()).hexdigest()
    report=dict(status='RECOVERED_STAR_CHECKPOINT_SEMANTIC_CONTROLS_PASS',inputs_sha256=inputs,
        original_CP_records=len(original['records']),effective_CP_records=len(view['records']),
        repaired_proposal_indices=view['repaired_proposal_indices'],near_zero_eligible_indices=[r['proposal_index'] for r in selected],
        positive_controls=['actual_stopped_receipt','actual_bound_strict_recovery','all64_unchanged_selection_associations','exact_nearzero_reconstruction'],
        negative_controls=len(controls),controls=controls,semantic_controls_bypass_hash_guards=True,
        scientific_reruns=0,subprocess_invocations=0,checkpoint_created=False)
    with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=report['status'],negative_controls=len(controls),eligible=len(selected))))


if __name__=='__main__':main()
