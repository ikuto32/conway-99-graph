"""Independent exact334-to337 claim/evidence impact check; no math replay."""
import argparse,copy,hashlib,json,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline
import audit_20261002_wave34_transition_v1 as previous
ROOT=Path(__file__).resolve().parents[1]
START='4b7470f6e2bd183d355a2247e28a354159681f0b12c10fcb90181bff94e91ea5'
FINAL='8f8d39f5e4fcaf8cb8ec2681e0a9ec795439c80e2c8bd1d8a5903ef1087d342d'
REG='acceleration/results/20261003_wave36_registration02'
MODEL='C-UNRESTRICTED-ROOTED7-MARKED-REROOT-MEAN-NECESSARY-ENCODING'
LP='C-UNRESTRICTED-ROOTED7-PRIMARY-DOMAIN-RATIONAL-FEASIBILITY'
ENGINE='C-HYPERGRAPH-WEIGHT60-EXCLUSIVE-SWAP-V2-FINITE-ENGINEERING-CONTROLS'
BINDINGS={MODEL:('acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/claim_binding.json','107ac82be6212129f8d98056a4c640ee64e2557238b11465edb91535076cb727'),LP:('acceleration/results/20261003_independent_review/rooted7_unrestricted_lp01/claim_binding.json','e8d9f598e3d9dad746ec890cabf0ad5ce07a6a048fd1929c5bdeecad1ed438f6'),ENGINE:('acceleration/results/20261002_independent_review/weight60_controls01/claim_binding_schema2.json','7a935bcd901844a4341b18a62ab24e31fbc2984861f0b8b2086fa9d1fd387985')}
need=previous.need;AuditError=previous.AuditError;indexed=previous.indexed
def projection(cid,b,report,original=None):
    fields={k:copy.deepcopy(b[k]) for k in ('id','revision','statement','kind','basis','status','review_state','assumptions','limitations')};scope=b['scope'];paths=dict(b['inputs_sha256'])
    need(set(scope)=={'description','unrestricted_target','target_resolution'} and scope['target_resolution']=='NONE','EXACT_NARROW_SCOPE')
    need(b['producer']!=b['verifier'],'INDEPENDENT_ROLES')
    if cid==MODEL:
        need(b['producer']=='/root/structural' and b['verifier']=='/root/checkpoint_audit' and b['method']=='independent_derivation','EXACT_MODEL_ROLES')
        need(report['status']=='INDEPENDENT_UNRESTRICTED_ROOTED7_NECESSARY_OPERATOR_V1_PASS' and report['statement']==b['statement'] and report['variables']==2810 and report['rows']==11769 and report['terms']==89350 and report['new_exclusions']==0 and report['target_resolution']=='NONE','EXACT_NECESSARY_MODEL_SCOPE')
        need(b['scope']['unrestricted_target'] is True and [d['id'] for d in b['dependencies']]==['C-UNRESTRICTED-ROOTED7-NONEDGE-LOCAL-CATALOGUE-COVERAGE','C-UNRESTRICTED-ROOTED6-NONEDGE-INTEGER-DOMAIN','C-UNRESTRICTED-ROOTED6-EDGE-KERNEL-INTEGER-DOMAIN','C-UNRESTRICTED-ROOTED6-PER-VERTEX-GLOBAL-PRISM-MEAN-IDENTITIES'] and all(d['revision']==1 and d['relation']=='uses_result' for d in b['dependencies']),'UNRESTRICTED_MODEL_PREMISES')
    elif cid==LP:
        need(b['producer']=='/root/structural' and b['verifier']=='/root/checkpoint_audit' and b['method']=='independent_artifact_check','EXACT_LP_ROLES')
        need(report['status']=='INDEPENDENT_UNRESTRICTED_ROOTED7_LP_TEN_PRIMALS_651_WITNESSES_V2_PASS' and report['statement']==b['statement'] and report['complete_exact_primal_cases']==10 and report['complete_saved_profile_vectors']==651 and report['integer_count_vectors']==21 and report['complete_exact_farkas_cases']==0 and report['exclusions']==0 and report['target_resolution']=='NONE','EXACT_RATIONAL_WITNESS_SCOPE')
        need(b['dependencies']==[{'id':MODEL,'revision':1,'relation':'uses_result'}] and b['scope']['unrestricted_target'] is True,'EXACT_LP_ENCODING_DEPENDENCY')
    else:
        need(b['producer']=='/root/native_driver' and b['verifier']=='/root/structural' and b['method']=='independent_artifact_check','EXACT_ENGINE_ROLES')
        need(report['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_ANNEAL_V2_CONTROLS_PASS' and report['native_calls_observed']==57 and report['successful_calls_completely_replayed']==29 and report['strict_negative_calls_checked']==28 and report['full_proposals']==20992 and report['all_saved_intermediate_checkpoints']==328 and report['pair_table_records']==2494 and report['overlap_valid']==1303 and report['overlap_accepted']==592 and report['overlap_rejected']==711 and report['target_resolution'] is False,'EXACT_FINITE_ENGINE_SCOPE')
        need(b['scope']['unrestricted_target'] is False and b['revision']==b['claim_revision']==1,'FINITE_ENGINE_NOT_TARGET_RESULT')
        correction=b['editorial_schema_correction'];need(correction['statement_changed'] is False and correction['claim_revision_changed'] is False and correction['scope_changed'] is False,'EXACT_EDITORIAL_FLAGS')
        for field in ('id','revision','claim_revision','statement','scope','report','report_sha256','assumptions','dependencies','limitations','status','review_state','basis','kind','producer','verifier','method','verification_timestamp'):
            need(b[field]==original[field],'EXACT_ENGINE_EDITORIAL_MATERIAL_FIELDS',field)
        old_shared=original['shared_components'];need(type(old_shared) is dict and len(old_shared)==2 and b['shared_component_hashes']==old_shared and report['shared_components']==old_shared,'ORIGINAL_SHARED_HASHES_PRESERVED')
        expected=[f'Pinned prior independently authored helper {name}; SHA256 {digest}; code reuse disclosed, no old execution approval transfer.' for name,digest in sorted(old_shared.items())]
        need(b['shared_components']==expected,'EXACT_SHARED_SCHEMA_REPRESENTATION')
        need(all(b['inputs_sha256'].get(p)==h for p,h in original['inputs_sha256'].items()),'ALL_ORIGINAL_ENGINE_INPUT_PINS_PRESERVED')
    need(b['revision']==1 and b['status']=='VERIFIED' and b['review_state']=='CLEAR','EXACT_BOUND_R1_STATUS')
    paths[b['report']]=b['report_sha256'];name,h=BINDINGS[cid];paths[name]=h
    for record in b.get('artifacts',[]):
        need(record['path'] not in paths or paths[record['path']]==record['sha256'],'CONSISTENT_BINDING_CLOSURE');paths[record['path']]=record['sha256']
    return {'fields':fields,'scope':scope,'paths':paths,'shared':b['shared_components'],'original_scope':None,'controls':b.get('controls',report.get('controls',report.get('corrupted_controls_rejected'))),'premises':b.get('premise_state',b.get('mathematical_scope',{}))}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();start=time.monotonic();d=CommandDeadline(args.seconds,allocation_reason='Frozen334to337 metadata/directhash impactcheck;3bindings and~100MiB finiteengineering/localoperator evidence;180outer150worker15reserve,no mathematics replay or stager import')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        need(d.status()['remaining_seconds']>15,'DEADLINE_RESERVE')
        if p in pins:need(h is None or pins[p]==h,'INPUT_HASH');return pins[p]
        with (ROOT/p).open('rb') as s:actual=hashlib.file_digest(s,'sha256').hexdigest()
        need(h is None or actual==h,'INPUT_HASH',p);pins[p]=actual;return actual
    def read(p,h=None):pin(p,h);return json.loads((ROOT/p).read_bytes())
    def ledger(p,h):pin(p,h);return yaml.load((ROOT/p).read_text(encoding='utf8'),Loader=previous.UniqueLoader)
    try:
        bindings={cid:read(p,h) for cid,(p,h) in BINDINGS.items()};gold={};reports={}
        original=read('acceleration/results/20261002_independent_review/weight60_controls01/claim_binding.json','3218c24c1ec41da1495b33585ad87ccbf658f4ce923c57d744b26473a84574be')
        for cid,b in bindings.items():report=read(b['report'],b['report_sha256']);reports[cid]=report;gold[cid]=projection(cid,b,report,original if cid==ENGINE else None)
        summary=read(REG+'/summary.json','0beacc9cf870fd4e3acc19c123ed5a766fa8770d1080b229d00de0fa43cc69ff')
        need(summary['before_ledger_sha256']==START and summary['ledger_sha256']==FINAL and summary['mathematical_replays']==0 and summary['new_claim_ids']==list(BINDINGS),'EXACT_REGISTRATION_CHAIN')
        before=ledger(REG+'/CLAIMS.before.yaml',START);after=ledger(REG+'/CLAIMS.after.yaml',FINAL);old,new,artifacts=previous.transition(before,after,BINDINGS,bindings,gold)
        need(len(old)==334 and len(new)==337 and Counter(c['status'] for c in new.values())=={'VERIFIED':330,'CANDIDATE':3,'REFUTED':4} and all(c['review_state']=='CLEAR' for c in new.values()),'EXACT_CLAIM_COUNTS')
        for cid in BINDINGS:
            for p,h in gold[cid]['paths'].items():pin(p,h)
        supervisor=read('acceleration/results/20261003_wave36_registration_supervision02/summary.json');need(supervisor['command_exit_code']==0 and supervisor['cleanup']['reaped'] and supervisor['cleanup']['job_active_zero_observed'],'ACTUAL_REGISTRATION_TERMINAL')
        failed=read('acceleration/results/20261003_wave36_registration_supervision01/summary.json');need(failed['command_exit_code']==1 and failed['cleanup']['reaped'] and failed['cleanup']['job_active_zero_observed'],'PRESERVED_FAILED_REGISTRATION_TERMINAL')
        failed_manifest=read('acceleration/results/20261003_wave36_registration_supervision01/manifest.json');need(START in failed_manifest['command'],'FAILED_REGISTRATION_START_PIN')
        stderr='acceleration/results/20261003_wave36_registration_supervision01/stderr.log';pin(stderr);need('shared_components' in (ROOT/stderr).read_text(encoding='utf8') and 'not of type' in (ROOT/stderr).read_text(encoding='utf8'),'EXACT_FAILED_SCHEMA_REASON')
        # Registrar failed before snapshot/ledger publication; its old start bytes are
        # the successful invocation's exact before state, not a retroactive refutation.
        controls=[]
        tests=[('prior_claim_change','ALL_PRIOR_CLAIMS_UNCHANGED',lambda x:x['claims'][0].update(statement='changed')),
               ('model_uniform_secondary_profile','BOUND_FIELD',lambda x:indexed(x['claims'])[MODEL].update(statement='All secondary pairs share one profile')),
               ('model_prismfree_scope','BOUND_SCOPE',lambda x:indexed(x['claims'])[MODEL]['scope'].update(description='Assume prism absence')),
               ('lp_graph_realization','BOUND_FIELD',lambda x:indexed(x['claims'])[LP].update(statement='651 graphs constructed')),
               ('lp_target_resolution','BOUND_SCOPE',lambda x:indexed(x['claims'])[LP]['scope'].update(target_resolution='EXISTENCE')),
               ('lp_dependency_scope_change','BOUND_DEPENDENCY_RELATION',lambda x:indexed(x['claims'])[LP]['dependencies'][0].update(relation='premise')),
               ('engine_performance_claim','BOUND_FIELD',lambda x:indexed(x['claims'])[ENGINE].update(statement='General speed and search guarantees')),
               ('engine_self_approval','BOUND_VERIFICATION_ROLE_METHOD',lambda x:indexed(x['claims'])[ENGINE]['verification'][0].update(verifier='/root/native_driver')),
               ('engine_lost_shared_disclosure','BOUND_SHARED_CHECKER_COMPONENTS',lambda x:indexed(x['claims'])[ENGINE]['verification'][0].update(shared_components=[])),
               ('changed_artifact_identity','EXACT_REVISION_HASH_BINDING',lambda x:indexed(x['claims'])[LP]['verification'][0]['artifact_hashes'].update({indexed(x['claims'])[LP]['evidence'][0]:'0'*64})),
               ('baseline_availability_change','ALL_PRIOR_ARTIFACTS_UNCHANGED',lambda x:x['artifacts'][0].update(availability='MISSING'))]
        for name,expected,change in tests:
            bad=copy.deepcopy(after);change(bad)
            try:previous.transition(before,bad,BINDINGS,bindings,gold)
            except AuditError as e:need(e.stage==expected,'CONTROL_WRONG_STAGE',str(e));controls.append({'name':name,'stage':e.stage,'outcome':'REJECTED'})
            else:raise AuditError('CONTROL_FALSE_ACCEPT',name)
        for name,expected,change in [('editorial_changed_statement','EXACT_ENGINE_EDITORIAL_MATERIAL_FIELDS',lambda x:x.update(statement='broadened')),('editorial_wrong_shared_hash','ORIGINAL_SHARED_HASHES_PRESERVED',lambda x:x['shared_component_hashes'].update({next(iter(x['shared_component_hashes'])):'0'*64})),('editorial_mutated_original_input','ALL_ORIGINAL_ENGINE_INPUT_PINS_PRESERVED',lambda x:x['inputs_sha256'].update({next(iter(original['inputs_sha256'])):'0'*64}))]:
            bad=copy.deepcopy(bindings[ENGINE]);change(bad)
            try:projection(ENGINE,bad,reports[ENGINE],original)
            except AuditError as e:need(e.stage==expected,'CONTROL_WRONG_STAGE',str(e));controls.append({'name':name,'stage':e.stage,'outcome':'REJECTED'})
            else:raise AuditError('EDITORIAL_CONTROL_FALSE_ACCEPT',name)
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261003_wave36_transition_v1_spec.md','acceleration/audit_20261002_wave34_transition_v1.py','acceleration/audit_20261002_wave31_transition_v1.py','acceleration/register_20261002_bound_claims_v9.py','acceleration/record_20261003_weight60_binding_schema2_v2.py','acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock']:pin(p)
        report={'status':'INDEPENDENT_WAVE36_EXACT334_TO337_TRANSITION_PASS','timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'verifier':'/root/checkpoint_audit','command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,'before_frozen_ledger_sha256':START,'after_frozen_ledger_sha256':FINAL,'unchanged_prior_claims':334,'current_claims':337,'new_claim_ids':list(BINDINGS),'status_counts':dict(Counter(c['status'] for c in new.values())),'review_counts':dict(Counter(c['review_state'] for c in new.values())),'controls':controls,'preserved_failed_registration':'acceleration/results/20261003_wave36_registration_supervision01','successful_registration':REG,'mathematical_replays':0,'new_exclusions':0,'target_resolution':'UNKNOWN','overall_search_coverage':'UNKNOWN; no validated denominator.','shared_components':['Pinned prior independent transition/UniqueLoader metadata checking only; no registrar, stager or discovery source imported.','Python YAML/SHA256/stdlib/command_deadline.'],'limitations':['Frozen snapshots and direct evidence hashes only; this is not independent mathematical reapproval or live process observation.','All334 prior claims/verification/artifact records and their previous availability retained.','Unrestricted2810-variable rooted7 model is necessary; exact rational witnesses cover count relaxation only, not realized graphs or integer exclusion.','Weight60 engineering claim covers57 finite calls only, including generic non99 fixtures; no trajectory/performance/ergodicity/search coverage assertion.','Shared-component dictionary correction retains exactr1 statement/scope/report/revision and original hashes; failure01 is a schema rejection, not mathematical refutation.','No prospective weight60 scientific pilot is approved by this impact audit.'],'elapsed_seconds':time.monotonic()-start,'deadline':d.status()}
        with (out/'summary.json').open('x',encoding='utf8',newline='\n') as s:json.dump(report,s,indent=2,sort_keys=True);s.write('\n')
        print(json.dumps({'status':report['status'],'report_sha256':pin((out/'summary.json').relative_to(ROOT).as_posix()),'elapsed_seconds':report['elapsed_seconds']}),flush=True)
    except BaseException as e:
        with (out/'failure.json').open('x',encoding='utf8',newline='\n') as s:json.dump({'error':repr(e),'stage':getattr(e,'stage',None),'inputs_sha256':pins,'elapsed_seconds':time.monotonic()-start,'outputs_preserved':True},s,indent=2);s.write('\n')
        raise
if __name__=='__main__':main()
