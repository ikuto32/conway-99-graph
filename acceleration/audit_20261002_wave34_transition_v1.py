"""Read-only exact324->329 audit; independent of registration adapters.

This checks binding/registry metadata and direct evidence identity, not mathematics.
"""
import argparse,copy,hashlib,json,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline
from audit_20261002_wave31_transition_v1 import UniqueLoader,indexed

ROOT=Path(__file__).resolve().parents[1]
START='b550318e7d3d85a2d2f8d853478905887da599813f3b2f9a0939240b277e58a4'
FINAL='05b129e28181c17ff5d6a18fd22d33033ed264418597848ccafc1ad731abd88f'
REGS=['acceleration/results/20261002_wave34_registration'+x for x in ('01','03','05')]
ENGINE='C-HYPERGRAPH-WEIGHTED-ANNEAL-V1-FINITE-ENGINEERING-CONTROLS'
PILOT='C-HYPERGRAPH-WEIGHTED-ANNEAL-PILOT02-SAVED-BEST-OBJECT'
NORM='C-PRISMFREE-ROOTED8-NORMALIZED-LITERAL-GF2-THREE-PRIMALS'
MEANS='C-UNRESTRICTED-ROOTED6-PER-VERTEX-GLOBAL-PRISM-MEAN-IDENTITIES'
ROWS='C-PRISMFREE-ROOTED7-PER-VERTEX-MEAN-NECESSARY-ROWS'
BINDINGS={
 ENGINE:('acceleration/results/20261002_independent_review/hypergraph_weighted_controls01/claim_binding.json','c97801c3ad60a9c362d8441a26e50e16eaa2b1b319f4d83b6399602555b0a74d'),
 PILOT:('acceleration/results/20261002_independent_review/hypergraph_weighted_pilot02/claim_binding.json','d639a1dd113a62ef531c6c0621567c7c06e3ffe21b560acdc0addcdb332a4b40'),
 NORM:('acceleration/results/20261002_independent_review/normalized_gf2_full_artifact01/claim_binding.json','9fb71449199b211ac1cad462df2714384b3e0096022b4adc3799d153ceeb7642'),
 MEANS:('acceleration/results/20261002_independent_review/rooted6_means02/universal_claim_binding.json','f39634de8e150908b4846c0c1959ca7d7c7e73df4b3877399de3875c2a0fecf7'),
 ROWS:('acceleration/results/20261002_independent_review/rooted6_means02/conditional_rows_claim_binding.json','15b6edc63b1849b2b2c1302fd91549adc6392a084638d2b3ed534cb5ef9cf7af')}

class AuditError(ValueError):
    def __init__(self,stage,detail=''):
        self.stage=stage;super().__init__(stage+(': '+detail if detail else ''))
def need(test,stage,detail=''):
    if not test:raise AuditError(stage,detail)

def exact_projection(cid,binding,report,calibration=None):
    """Construct expected schema fields from authenticated independent records."""
    fields={key:copy.deepcopy(binding[key]) for key in ('id','revision','statement','kind','basis','status','review_state','assumptions','limitations')}
    scope=copy.deepcopy(binding['scope']);inputs=dict(binding.get('inputs_sha256',{}))
    shared=binding.get('shared_components');original_scope=None
    need(binding['producer']!=binding['verifier'],'INDEPENDENT_ROLES')
    if cid==NORM:
        need(binding['producer']=='/root/native_driver' and binding['verifier']=='/root/structural','EXACT_NORMALIZED_ROLES')
        need(report['status']=='INDEPENDENT_NORMALIZED_GF2_THREE_FULL_PRIMALS_PASS' and
             report['rows_normalization_checked']==85874 and report['full_scalar_row_component_checks']==257622
             and report['rank_claim'] is False and report['target_resolution'] is False and
             report['profile_parity_population']['all210_integer_profiles_mod2_consistent'] is True,'EXACT_NORMALIZED_CHECK_SCOPE')
        need(binding['pre_output_calibration']['full_output_inspected'] is False and
             binding['pre_output_calibration']['sha256']=='63ae57b00a0cdc87ec2209dceb8e185ef70cd1ac350bf3a51ab0b7c13dfe5611' and
             calibration['status']=='INDEPENDENT_NORMALIZED_GF2_FULL_CHECKER_CALIBRATION_V1_PASS','EXACT_PREOUTPUT_CALIBRATION')
        inputs=dict(report['inputs_sha256'])
        for name,identity in {binding['pre_output_calibration']['path']:binding['pre_output_calibration']['sha256'],**calibration['inputs_sha256']}.items():
            need(name not in inputs or inputs[name]==identity,'CONSISTENT_PREOUTPUT_CHECKING_CLOSURE');inputs[name]=identity
        shared=binding['verification']['shared_components']
        original_scope=copy.deepcopy(scope);scope={key:scope[key] for key in ('description','unrestricted_target','target_resolution')}
        need('UNKNOWN' in json.dumps(original_scope) and original_scope['profile_population']['count']==210 and
             original_scope['profile_population']['excluded']==0,'NO_NORMALIZED_GRAPH_OR_RANK_PROMOTION')
        for vector in binding['certificate_artifacts']:
            need(inputs[vector['path']]==vector['sha256'] and vector['binary_coordinates']==23019,'EXACT_COMPLETE_PRIMAL_PINS')
    else:
        need(binding['verifier']=='/root/checkpoint_audit','EXACT_OTHER_VERIFIER')
        if cid in (ENGINE,PILOT):need(binding['producer']=='/root/native_driver','EXACT_ENGINE_DISCOVERY_ROLE')
        else:need(binding['producer']=='/root/structural','EXACT_MEANS_DISCOVERY_ROLE')
    if cid==MEANS:
        need(report['statement']==binding['statement'] and binding['kind']=='mathematical_result' and
             report['written_proof']=='acceleration/audit_20261002_rooted6_means_v1_proof.md','EXACT_UNIVERSAL_THEOREM_ADAPTER')
        need(binding['inputs_sha256'][report['written_proof']]=='570216537a80c0766737afa52a3a447d8392065d59c1bda95675701e3782625d' and
             binding['premise_state']['no_induced_triangular_prism']=='NOT_ASSUMED','UNIVERSAL_NO_PRISMFREE_PREMISE')
        fields['kind']='mathematical result'
    if cid==ROWS:
        need(report['status']=='INDEPENDENT_ROOTED6_PER_VERTEX_GLOBAL_MEANS_V2_PASS' and
             report['derived_conditional_root7_rows']==report['all_saved_corners_checked']==report['saved_corners_passing_derived_rows']==4 and
             report['profiles_excluded']==0 and report['prism_absence_status']=='UNKNOWN' and report['root_swap_same_free_orbit'] is True,
             'EXACT_FOUR_CONDITIONAL_ROWS_ADAPTER')
        need(binding['premise_state']['no_induced_triangular_prism']=='UNKNOWN','CONDITIONAL_PREMISE_UNKNOWN')
    elif 'statement' in report:need(report['statement']==binding['statement'],'EXACT_REPORT_STATEMENT')
    need(scope['target_resolution']=='NONE','NO_TARGET_PROMOTION')
    paths=dict(inputs);paths[binding['report']]=binding['report_sha256'];path,identity=BINDINGS[cid];paths[path]=identity
    for collection in ('artifacts','evidence'):
        values=binding.get(collection,[])
        if isinstance(values,dict):
            for key,value in values.items():
                if not key.endswith('_sha256'):
                    need(key+'_sha256' in values,'PAIRED_EVIDENCE_MAPPING')
                    need(value not in paths or paths[value]==values[key+'_sha256'],'CONSISTENT_EVIDENCE');paths[value]=values[key+'_sha256']
        else:
            for item in values:
                if isinstance(item,dict) and 'path' in item:
                    need(item['path'] not in paths or paths[item['path']]==item['sha256'],'CONSISTENT_EVIDENCE');paths[item['path']]=item['sha256']
    return {'fields':fields,'scope':scope,'paths':paths,'shared':shared,'original_scope':original_scope,
            'controls':binding.get('controls',report.get('controls',report.get('corrupted_controls_rejected'))),
            'premises':binding.get('premise_state',binding.get('mathematical_scope',{}))}

def transition(before,after,expected,bindings,gold):
    old,new=indexed(before['claims']),indexed(after['claims']);old_artifacts,artifacts=indexed(before['artifacts']),indexed(after['artifacts'])
    need(set(new)-set(old)==set(expected) and set(old)<=set(new),'EXACT_NEW_IDS')
    need(all(new[cid]==record for cid,record in old.items()),'ALL_PRIOR_CLAIMS_UNCHANGED')
    need([new[c['id']] for c in before['claims']]==after['claims'][:len(before['claims'])],'PRIOR_CLAIM_ORDER_UNCHANGED')
    need(set(old_artifacts)<=set(artifacts) and all(artifacts[aid]==record for aid,record in old_artifacts.items()),'ALL_PRIOR_ARTIFACTS_UNCHANGED')
    for field in set(before)|set(after):
        if field not in ('claims','artifacts','updated_at'):need(before[field]==after[field],'TOPLEVEL_SEMANTICS_UNCHANGED',field)
    need(after['target']['status']=='UNKNOWN' and after['target']['overall_search_coverage'] is None,'TARGET_AND_COVERAGE_UNKNOWN')
    all_evidence=set()
    for cid in expected:
        claim,binding,projected=new[cid],bindings[cid],gold[cid]
        for key,value in projected['fields'].items():need(claim[key]==value,'BOUND_FIELD',cid+':'+key)
        need(claim['scope']==projected['scope'],'BOUND_SCOPE',cid)
        need(claim['revision']==1 and claim['status']=='VERIFIED' and claim['review_state']=='CLEAR','EXACT_CURRENT_REVISION')
        deps=[{k:d[k] for k in ('id','revision','relation')} for d in binding['dependencies']]
        need(claim['dependencies']==deps,'BOUND_DEPENDENCY_RELATION',cid)
        for dep in deps:need(dep['id'] in new and new[dep['id']]['revision']==dep['revision'],'PINNED_DEPENDENCY_REVISION')
        notes=[{k:d[k] for k in ('id','revision','reason')} for d in binding['dependencies'] if 'reason' in d]
        need(json.loads(claim['unknowns']['dependency_notes'])==notes,'BOUND_DEPENDENCY_REASON')
        need(json.loads(claim['unknowns']['premises'])==projected['premises'],'BOUND_PREMISE_STATE')
        need(claim['unknowns']['original_binding_method']==binding['method'],'BOUND_METHOD_NOTE')
        if projected['original_scope'] is not None:
            need(json.loads(claim['unknowns']['original_binding_scope'])==projected['original_scope'],'RICH_NORMALIZED_SCOPE_RETAINED')
        if cid in (MEANS,ROWS):need(claim['unknowns']['original_binding_kind']==binding['kind'],'ORIGINAL_KIND_RETAINED')
        need(len(claim['verification'])==1,'ONE_BOUND_INDEPENDENT_RECORD');record=claim['verification'][0]
        need(record['method']==binding['method'] and record['claim_revision']==1 and record['verifier']==binding['verifier'] and record['outcome']=='PASS','BOUND_VERIFICATION_ROLE_METHOD')
        need(record['timestamp']==binding['verification_timestamp'] and record['scope']==projected['scope']['description'] and
             record['command_or_audit']==binding['report'] and record['limitations']==binding['limitations'],'BOUND_VERIFICATION_SCOPE')
        need(record['shared_components']==projected['shared'],'BOUND_SHARED_CHECKER_COMPONENTS')
        need(json.loads(record['controls'][0])==projected['controls'],'BOUND_CONTROLS')
        actual={artifacts[aid]['path']:artifacts[aid]['sha256'] for aid in claim['evidence']}
        need(actual==projected['paths'] and len(actual)==len(claim['evidence']),'COMPLETE_EXACT_BOUND_EVIDENCE')
        need(set(record['artifact_hashes'])==set(claim['evidence']) and
             all(record['artifact_hashes'][aid]==artifacts[aid]['sha256'] for aid in claim['evidence']),'EXACT_REVISION_HASH_BINDING')
        need(all(artifacts[aid]['availability']=='LOCAL_ONLY' for aid in claim['evidence']),'NO_UNCONFIRMED_PUBLIC_PROMOTION')
        need(claim['reproducibility']['manifest'] in claim['evidence'] and
             artifacts[claim['reproducibility']['manifest']]['path']==binding['report'],'EXACT_REPRODUCIBILITY_ENTRY')
        need(all(datetime.fromisoformat(claim[key]).tzinfo is not None for key in ('created_at','updated_at')),'TIMESTAMPS_WITH_TIMEZONES')
        all_evidence.update(claim['evidence'])
    need(set(artifacts)-set(old_artifacts)==all_evidence,'NO_UNBOUND_NEW_ARTIFACTS')
    return old,new,artifacts

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Read-only fiveexactr1 binding/registry transitions and directhash closure about0.5GiB; no mathematical replay')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(name,identity=None):
        need(deadline.status()['remaining_seconds']>15,'DEADLINE','save/shutdown reserve')
        if name in pins:
            need(identity is None or identity==pins[name],'PIN_CONSISTENCY');return pins[name]
        with (ROOT/name).open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
        need(identity is None or identity==actual,'INPUT_HASH',name);pins[name]=actual;return actual
    def read(name,identity=None):pin(name,identity);return json.loads((ROOT/name).read_bytes())
    def ledger(name,identity):pin(name,identity);return yaml.load((ROOT/name).read_text(encoding='utf8'),Loader=UniqueLoader)
    bindings={cid:read(path,h) for cid,(path,h) in BINDINGS.items()};gold={};reports={}
    for cid,binding in bindings.items():
        report=read(binding['report'],binding['report_sha256']);reports[cid]=report
        calibration=read(binding['pre_output_calibration']['path'],binding['pre_output_calibration']['sha256']) if cid==NORM else None
        gold[cid]=exact_projection(cid,binding,report,calibration)
    snapshots=[];summaries=[];previous=START
    for directory in REGS:
        summary=read(directory+'/summary.json');need(summary['before_ledger_sha256']==previous and summary['mathematical_replays']==0,'CONTIGUOUS_FROZEN_HASH_CHAIN')
        before=ledger(directory+'/CLAIMS.before.yaml',previous);after=ledger(directory+'/CLAIMS.after.yaml',summary['ledger_sha256'])
        if snapshots:need(snapshots[-1][1]==before,'CONTIGUOUS_FROZEN_SEMANTICS')
        transition(before,after,summary['new_claim_ids'],bindings,gold);snapshots.append((before,after));summaries.append(summary);previous=summary['ledger_sha256']
    need(previous==FINAL,'EXACT_FINAL_HASH');old,new,artifacts=transition(snapshots[0][0],snapshots[-1][1],BINDINGS,bindings,gold)
    need(len(old)==324 and len(new)==329 and Counter(c['status'] for c in new.values())=={'VERIFIED':322,'CANDIDATE':3,'REFUTED':4}
         and all(c['review_state']=='CLEAR' for c in new.values()),'EXACT_CLAIM_POPULATIONS')
    for cid in BINDINGS:
        for name,identity in gold[cid]['paths'].items():pin(name,identity)
    controls=[]
    mutations=[
      ('old_claim', 'ALL_PRIOR_CLAIMS_UNCHANGED',lambda d:d['claims'][0].update(statement='changed')),
      ('universal_wrong_statement','BOUND_FIELD',lambda d:indexed(d['claims'])[MEANS].update(statement='all graphs do not exist')),
      ('universal_kind_adapter_wrong','BOUND_FIELD',lambda d:indexed(d['claims'])[MEANS].update(kind='mathematical_result')),
      ('conditional_target_broadening','BOUND_SCOPE',lambda d:indexed(d['claims'])[ROWS]['scope'].update(target_resolution='NONEXISTENCE')),
      ('normalization_scope_broadening','BOUND_SCOPE',lambda d:indexed(d['claims'])[NORM]['scope'].update(unrestricted_target=True)),
      ('normalization_richscope_erasure','RICH_NORMALIZED_SCOPE_RETAINED',lambda d:indexed(d['claims'])[NORM]['unknowns'].update(original_binding_scope='{}')),
      ('wrong_dependency_relation','BOUND_DEPENDENCY_RELATION',lambda d:indexed(d['claims'])[MEANS]['dependencies'][0].update(relation='premise')),
      ('prism_absence_promotion','BOUND_PREMISE_STATE',lambda d:indexed(d['claims'])[ROWS]['unknowns'].update(premises='{"no_induced_triangular_prism":"VERIFIED"}')),
      ('wrong_evidence_hash','EXACT_REVISION_HASH_BINDING',lambda d:indexed(d['claims'])[PILOT]['verification'][0]['artifact_hashes'].update({indexed(d['claims'])[PILOT]['evidence'][0]:'0'*64})),
      ('self_verifier_promotion','BOUND_VERIFICATION_ROLE_METHOD',lambda d:indexed(d['claims'])[NORM]['verification'][0].update(verifier='/root/native_driver')),
      ('missing_shared_disclosure','BOUND_SHARED_CHECKER_COMPONENTS',lambda d:indexed(d['claims'])[NORM]['verification'][0].update(shared_components=[]))]
    for label,expected,mutate in mutations:
        damaged=copy.deepcopy(snapshots[-1][1]);mutate(damaged)
        try:transition(snapshots[0][0],damaged,BINDINGS,bindings,gold)
        except AuditError as error:
            need(error.stage==expected,'NEGATIVE_EXACT_STAGE',str(error));controls.append({'label':label,'stage':error.stage,'diagnostic':str(error)})
        else:raise AuditError('CORRUPT_TRANSITION_ACCEPTED',label)
    for name in (Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261002_wave34_transition_v1_spec.md',
                 'acceleration/audit_20261002_wave31_transition_v1.py','acceleration/register_20261002_bound_claims_v7.py',
                 'acceleration/register_20261002_bound_claims_v8.py','acceleration/register_20261002_bound_claims_v9.py',
                 'acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml'):
        pin(name)
    report={'status':'INDEPENDENT_WAVE34_EXACT324_TO329_TRANSITION_PASS','timestamp':datetime.now(timezone.utc).isoformat(),
            'verifier':'/root/checkpoint_audit','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,
            'before_frozen_ledger_sha256':START,'after_frozen_ledger_sha256':FINAL,'previous_claims':324,'current_claims':329,
            'unchanged_prior_claims':324,'new_claim_ids':list(BINDINGS),'clear_status_counts':dict(Counter(c['status'] for c in new.values())),
            'successful_registration_directories':REGS,'controls':controls,'mathematical_replays':0,'new_exclusions':0,
            'target_resolution':'UNKNOWN','overall_search_coverage':'UNKNOWN; no validated denominator.',
            'elapsed_seconds':time.monotonic()-start,'deadline':deadline.status(),
            'exact_adapters':['Normalized GF2: exact9fb71449...binding projects only schema3 scope fields, preserves complete original scope, expands exact full report+preoutput calibration input pins, retains nested shared components;257622 scalar checks,all210 parity profiles,no rank/exclusion.',
              'Universal means: exactf39634de...binding kind mathematical_result mapped only to schema mathematical result, original kind retained; no prism absence assumed; independent written proof pinned.',
              'Conditional mean rows: exact15b6edc6...binding has narrower four-row statement than combined report headline, justified by exact saved row/corner artifacts and complete written proof; premiseUNKNOWN,all4corners pass,0exclusions.'],
            'shared_components':['Prior independent UniqueLoader/indexed helpers for duplicate YAML keys/IDs only','Python yaml/exact hashes/stdlib','command_deadline scheduling'],
            'limitations':['Metadata/direct byte identity checking only; no new mathematical replay or live-ledger/current process assertion.',
              'Failed registrations02/v7 and04/v8 are preserved; successful frozen01/03/05 form exact contiguous chain.',
              'GF2 witnesses do not prove integer/nonnegative solutions, rank, realized profiles or graphs.',
              'Weighted pilot F3801 ordinaryE3486 graph is not SRG; native20m counter is not full trajectory checking.',
              'Universal means include exact prism terms; target row specialization remains conditional on UNKNOWN prism absence.',
              'Prior published availability records preserved; new evidence LOCAL_ONLY until a separate publisher establishes retrieval.']}
    with (out/'summary.json').open('x',encoding='utf8',newline='\n') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'path':str(out/'summary.json'),'sha256':hashlib.sha256((out/'summary.json').read_bytes()).hexdigest(),'status':report['status']}))

if __name__=='__main__':main()
