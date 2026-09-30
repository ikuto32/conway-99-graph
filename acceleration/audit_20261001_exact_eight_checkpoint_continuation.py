"""Independent continuation prebuild review; no producer imports/process launch.

Draft until producer source/spec and explicit authorization are frozen.
"""
import argparse, ast, copy, json, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
import audit_20261001_exact_eight_checkpoint_records as ck

old=ck.old;prior=old.prior;ROOT=ck.ROOT
need=ck.need;read=ck.read;sha=ck.sha;key=ck.key;save=old.save
SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
STATUS='INDEPENDENT_EXACT_EIGHT_BATCH04_CONTINUATION_PREFLIGHT_PASS'


def shape_controls(launch,snapshot,children):
    rejected=[]
    for name,mutate in [
        ('wrong_workers',lambda x:x.update(workers=3)),
        ('wrong_budget',lambda x:x.update(seconds_per_chunk=121)),
        ('wrong_old_calls',lambda x:x.update(original_producer_calls=56)),
        ('wrong_new_calls',lambda x:x.update(additional_allocated_producer_calls=4)),
        ('drop_repeat',lambda x:x['repeated_uncheckpointed_case_ids'].pop()),
        ('drop_partition',lambda x:x['build_selections'].pop()),
        ('reverse_partitions',lambda x:x['build_selections'].reverse()),
        ('reuse_output',lambda x:x['build_selections'][1].update(out=x['build_selections'][0]['out'])),
        ('reuse_attempt',lambda x:x['build_selections'][1].update(attempt_id=x['build_selections'][0]['attempt_id']))]:
        bad=copy.deepcopy(launch);mutate(bad)
        need(not ck.same(bad,launch),'complete launch comparison rejects '+name);rejected.append(name)
    for j,(_,child)in enumerate(children):
        for name,mutate in [
            ('drop_pending',lambda x:x['ordered_case_ids'].pop()),
            ('reverse_pending',lambda x:x['ordered_case_ids'].reverse()),
            ('promote_old_case',lambda x:x['ordered_case_ids'].__setitem__(0,snapshot['partitions'][j]['part']['ordered_case_ids'][0])),
            ('wrong_checkpoint',lambda x:x['retained_checkpoint'].update(sha256='0'*64)),
            ('wrong_authority',lambda x:x.update(authorization_record_sha256='0'*64)),
            ('wrong_prefix_count',lambda x:x.update(retained_prefix_count=15))]:
            bad=copy.deepcopy(child);mutate(bad)
            need(not ck.same(bad,child),'complete child comparison rejects '+name);rejected.append(f'part{j}_{name}')
    return dict(finite_checkpoint_and_process=ck.controls(),actual_shape_corruptions_rejected=rejected)


def main():
    ap=argparse.ArgumentParser()
    for name in ['launch-plan','preparation','authorization','adoption','source-controls','producer','producer-spec']:
        ap.add_argument('--'+name,type=Path,required=True);ap.add_argument('--'+name+'-sha256',required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    out=a.out.resolve();need(out.is_relative_to(ROOT/'acceleration/results'),'new review output boundary')
    out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(path,expected=None):
        path=path.resolve();name=key(path);need(ck.canonical(name)==path,'safe canonical input')
        if name not in pins:pins[name]=sha(path)
        need(expected is None or pins[name]==expected,'hash '+name)
    try:
        for p,h in old.PINS.items():pin(p,h)
        closure=prior.static_closure(Path(__file__))
        for p in closure:pin(p)
        for p in [Path(__file__),SPEC,ROOT/'docs/REVIEW_PLAN_20261001_EXACT_EIGHT_CHECKPOINT_CONTINUATION.md']:pin(p)
        need(all(not p.name.startswith(('theory_','native_','continue_','run_','select_'))for p in closure),
             'independent helper imports only')
        for field in ['launch_plan','preparation','authorization','adoption','source_controls','producer','producer_spec']:
            pin(getattr(a,field),getattr(a,field+'_sha256'))
        # Parse for audit provenance only; never import or execute producer code.
        ast.parse(a.producer.read_text(encoding='utf8'))
        launch=read(a.launch_plan);prepared=read(a.preparation)
        adoption=read(a.adoption);source_controls=read(a.source_controls)
        need(adoption['authorizer']=='/root'
             and adoption['decision']=='AUTHORIZED_CONDITIONAL_ON_INDEPENDENT_PREFLIGHT'
             and adoption['adopted_plan']==dict(path=key(a.authorization),sha256=a.authorization_sha256)
             and adoption['producer_attempt_accounting']==dict(old=60,additional_allocated=8,
                 accepted_formula_population_if_complete=64,retained_checkpoint_population=56,
                 explicit_repeated_uncheckpointed_cases=4)
             and adoption['ledger_mutations']==0 and adoption['mathematical_verification']is False,
             'exact root adoption of bounded continuation plan')
        need(source_controls['status']=='CANDIDATE_BATCH04_CONTINUATION_SOURCE_PREPARATION_CONTROLS_PASS'
             and source_controls['adapter_imported']is False
             and source_controls['adapter_modes_executed']==source_controls['actual_old_artifact_replays']
             ==source_controls['process_creation_calls']==source_controls['producer_calls']
             ==source_controls['native_calls']==0 and source_controls['positive_assertions']==6
             and source_controls['corruptions_rejected']==12,'disclosed source-only producer controls')
        for name,h in source_controls['inputs_sha256'].items():pin(ck.canonical(name),h)
        prep_source=ROOT/'acceleration/check_20261001_exact_eight_batch04_continuation_preparation.py'
        pin(prep_source,source_controls['source_sha256'])
        for name,h in {**prepared['inputs_sha256'],**prepared['outputs_sha256']}.items():pin(ck.canonical(name),h)
        for p,h in [(a.producer,a.producer_sha256),(a.producer_spec,a.producer_spec_sha256),
                    (a.authorization,a.authorization_sha256)]:
            need(prepared['inputs_sha256'].get(key(p))==h,'preparation directly binds reviewed source/spec/authority')
        need(prepared['outputs_sha256'].get(key(a.launch_plan))==a.launch_plan_sha256,
             'preparation directly binds candidate launch plan')
        need(launch['authorization']==dict(path=key(a.authorization),sha256=a.authorization_sha256),
             'explicit caller-authenticated continuation authorization')
        parent_path,parent=ck.ref_read(launch['original_selection'],pin)
        pop=prior.population(pin);approved,byid,_,_,_,proof_review=old.selection_review(parent_path,pop,pin)
        need(ck.same(parent,approved),'unchanged independently reconstructed original selection')
        snapshot=ck.interrupted_review(parent_path,parent,launch['original_launch_plan'],
                                       launch['interrupted_launcher'],launch['retained_checkpoints'],pin,byid)
        children=ck.continuation_plan_review(launch,parent_path,parent,snapshot,launch['original_launch_plan'],
                                            launch['interrupted_launcher'],pin,True)
        need(prepared['status']=='CANDIDATE_BATCH04_CHECKPOINT_CONTINUATION_PREPARED'
             and prepared['selected_case_ids']==parent['ordered_case_ids']and prepared['retained_count']==56
             and prepared['pending_case_ids']==snapshot['pending_case_ids']
             and prepared['original_producer_calls']==60 and prepared['additional_allocated_producer_calls']==8
             and prepared['native_calls']==prepared['build_invocations']==0,'honest preparation boundary')
        controls=shape_controls(launch,snapshot,children)
        save(out/'controls.json',controls)
        save(out/'prior_proof_identity_review.json',proof_review)
        save(out/'interrupted_prefix_review.json',snapshot)
        need(time.perf_counter()-start<600,'bounded complete provenance review')
        save(out/'summary.json',dict(status=STATUS,timestamp=datetime.now(timezone.utc).isoformat(),
             command=[sys.executable,*sys.argv],inputs_sha256=pins,
             outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},
             original_selection=launch['original_selection'],launch_plan_path=key(a.launch_plan),
             launch_plan_sha256=a.launch_plan_sha256,selected_case_ids=parent['ordered_case_ids'],
             authorization_adoption=dict(path=key(a.adoption),sha256=a.adoption_sha256),
             retained_checkpoint_records=56,pending_case_ids=snapshot['pending_case_ids'],
             evidenced_original_producer_calls=60,additional_allocated_producer_calls=8,
             repeated_uncheckpointed_case_ids=snapshot['uncheckpointed_repeated_case_ids'],
             old_process_receipts_checked=4,new_build_partition_sizes=[2]*4,
             seconds_per_partition=120,total_new_allocated_build_seconds=480,
             formula_validity_approved=False,new_builds=0,new_solver_calls=0,git_commands=0,
             producer_imports=0,scope='Continuation selection/provenance and static adapter review only. Full64 independent raw encoding review and fresh object calibration remain mandatory.',
             elapsed_seconds=time.perf_counter()-start))
        print(json.dumps(dict(status=STATUS,summary_sha256=sha(out/'summary.json'))))
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),inputs_sha256=pins,
                                    source_sha256=sha(Path(__file__)),new_builds=0,new_solver_calls=0));raise


if __name__=='__main__':main()
