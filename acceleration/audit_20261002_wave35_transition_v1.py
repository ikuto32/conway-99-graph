"""Read-only frozen329->334 exact claim impact audit; no mathematical replay."""
import argparse,copy,hashlib,json,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline
import audit_20261002_wave34_transition_v1 as previous
ROOT=Path(__file__).resolve().parents[1]
START='24c0caca4b4f2aa55fac8f993ab6c0b95715cd506963480863d217c3726e9a57'
FINAL='5476fe90324fb7a3a8aa275fc1ae1061f7aaeb8e42d9c5123d33a8d1c3f65f5a'
REGS=['acceleration/results/20261002_wave35_registration01','acceleration/results/20261002_wave35_registration02']
CRITERION='C-99-LINEAR-TRIPLE-POINTGRAPH-LAMBDA-ZERO-CRITERION'
CENSUS='C-HYPERGRAPH-WEIGHTED-PILOT02-EXTRA-TRIANGLE-ROOT-CENSUS'
NONEDGE='C-UNRESTRICTED-ROOTED6-NONEDGE-INTEGER-DOMAIN'
EDGE='C-UNRESTRICTED-ROOTED6-EDGE-KERNEL-INTEGER-DOMAIN'
GF3='C-PRISMFREE-ROOTED8-ORIGINAL-LITERAL-GF3-THREE-PRIMALS'
P='acceleration/results/20261002_independent_review/'
BINDINGS={CRITERION:(P+'lambda_phase_structure01/phase_criterion_claim_binding_v2.json','bb787066b63048274729b959821876c294c0d0258b04fadade79df724353dca4'),CENSUS:(P+'lambda_phase_structure01/saved_root_census_claim_binding_v2.json','76543af2df9c7135b46aaee34fc0040c6ea574d32f713045e5fd78ad62e1037d'),NONEDGE:(P+'rooted6_unrestricted_domain01/claim_binding.json','472202b5c6698b797f385a1434246521fae07b10e79c24ed43db402f835323fe'),EDGE:(P+'rooted6_unrestricted_edge_domain01/claim_binding.json','5100f82b408a74866a7276e2929a4e8f723cb4badbd2bb086800e082a808b2e0'),GF3:(P+'gf3_full_artifact01/claim_binding_v2.json','44333458cd07dd160933fce82a6b8bffa6114afe2c20478995751f0e2f34699a')}
need=previous.need;AuditError=previous.AuditError;indexed=previous.indexed
def projection(cid,b,report,original=None):
    fields={k:copy.deepcopy(b[k]) for k in ('id','revision','statement','kind','basis','status','review_state','assumptions','limitations')};scope=b['scope'];paths=dict(b['inputs_sha256'])
    need(b['producer']!=b['verifier'],'INDEPENDENT_ROLES');need(set(scope)=={'description','unrestricted_target','target_resolution'} and scope['target_resolution']=='NONE','EXACT_NARROW_SCOPE')
    if cid==GF3:
        need(b['producer']=='/root/native_driver' and b['verifier']=='/root/structural' and b['method']=='independent_artifact_check','EXACT_GF3_ROLES')
        need(report['status']=='INDEPENDENT_ORIGINAL_LITERAL_GF3_THREE_PRIMALS_V1_PASS' and report['literal_result']=={'complete_vectors':3,'scalar_raw_row_component_checks':257622} and report['rank_claim'] is False and report['target_resolution'] is False and report['profile_domain']['population']==report['profile_domain']['literal_mod3_compatible_profiles']==210 and report['profile_domain']['excluded_profiles']==0,'EXACT_GF3_LITERAL_SCOPE')
        need(b['editorial_correction']['statement_unchanged'] is True and b['editorial_correction']['previous_binding_promoted'] is False and original['statement']==b['statement'] and original['revision']==b['revision']==1 and original['report_sha256']==b['report_sha256'] and {k:original['scope'][k] for k in scope}==scope,'EXACT_GF3_EDITORIAL_SCOPE_PROJECTION')
        need(b['pre_output_calibration']['full_output_inspected'] is False and b['pre_output_calibration']['specific_corrupt_controls']==14,'GF3_PREOUTPUT_DISCLOSURE')
        need(len(report['primal_vectors'])==3 and all(v['trits']==23019 and paths[v['path']]==v['sha256'] for v in report['primal_vectors']),'GF3_COMPLETE_VECTOR_BINDING')
    else:
        need(b['verifier']=='/root/checkpoint_audit' and b['method']=='independent_derivation' if cid!=CENSUS else b['verifier']=='/root/checkpoint_audit' and b['method']=='independent_artifact_check','EXACT_OTHER_METHOD')
        need(b['producer']==('/root' if cid==CRITERION else '/root/native_driver' if cid==CENSUS else '/root/structural'),'EXACT_PRODUCER_ROLE')
        need(report['statement']==b['statement'],'EXACT_REPORT_STATEMENT')
    if cid==CRITERION:need('exactly231given triples' in b['statement'] and 'at every vertex' in b['statement'] and b['dependencies']==[],'SCOPED99_CRITERION')
    if cid==NONEDGE:need(report['accepted_integer_profiles']==651 and report['bounding_integer_triples']==693 and report['rejected_integer_triples']==42 and report['prior_rank_dependency']['fresh_rank_computation'] is False and b['scope']['unrestricted_target'] is True,'EXACT_NONEDGE651_SCOPE')
    if cid==EDGE:need(report['rational_rank']==392 and report['nullity']==2 and report['independent_prime']==1009 and report['integer_profiles']==91 and b['dependencies'][0]['relation']=='verification_dependency' and 'not premises' in b['dependency_reason'],'EXACT_EDGE91_UNCONDITIONAL_PREMISE_SCOPE')
    paths[b['report']]=b['report_sha256'];binding_path,identity=BINDINGS[cid];paths[binding_path]=identity
    for item in b.get('artifacts',[]):
        need(item['path'] not in paths or paths[item['path']]==item['sha256'],'CONSISTENT_DIRECT_ARTIFACT_CLOSURE');paths[item['path']]=item['sha256']
    return dict(fields=fields,scope=scope,paths=paths,shared=b['shared_components'],original_scope=None,controls=b.get('controls',report.get('controls',report.get('corrupted_controls_rejected'))),premises=b.get('premise_state',b.get('mathematical_scope',{})))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Frozen329to334 five exactr1 bindings/directhash closure; prior7.45s metadataaudit,180outer150worker15reserve,no mathematical replay')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(name,wanted=None):
        need(deadline.status()['remaining_seconds']>15,'DEADLINE_RESERVE')
        if name in pins:need(wanted is None or wanted==pins[name],'INPUT_HASH');return pins[name]
        with (ROOT/name).open('rb') as s:actual=hashlib.file_digest(s,'sha256').hexdigest()
        need(wanted is None or wanted==actual,'INPUT_HASH',name);pins[name]=actual;return actual
    def read(name,h=None):pin(name,h);return json.loads((ROOT/name).read_bytes())
    def ledger(name,h):pin(name,h);return yaml.load((ROOT/name).read_text(encoding='utf8'),Loader=previous.UniqueLoader)
    try:
        bindings={cid:read(path,h) for cid,(path,h) in BINDINGS.items()};gold={}
        for cid,b in bindings.items():
            report=read(b['report'],b['report_sha256']);original=read(b['editorial_correction']['preserved_original_binding'],b['editorial_correction']['preserved_original_binding_sha256']) if cid==GF3 else None;gold[cid]=projection(cid,b,report,original)
        snapshots=[];summaries=[];identity=START
        for directory in REGS:
            summary=read(directory+'/summary.json');need(summary['before_ledger_sha256']==identity and summary['mathematical_replays']==0,'CONTIGUOUS_FROZEN_HASH_CHAIN');before=ledger(directory+'/CLAIMS.before.yaml',identity);after=ledger(directory+'/CLAIMS.after.yaml',summary['ledger_sha256'])
            if snapshots:need(snapshots[-1][1]==before,'CONTIGUOUS_FROZEN_SEMANTICS')
            previous.transition(before,after,summary['new_claim_ids'],bindings,gold);snapshots.append((before,after));summaries.append(summary);identity=summary['ledger_sha256']
        need(identity==FINAL,'EXACT_FINAL_HASH');prior,current,artifacts=previous.transition(snapshots[0][0],snapshots[-1][1],BINDINGS,bindings,gold)
        checkpoint=ledger('acceleration/results/20261002_wave35_milestone01/CLAIMS.yaml',FINAL);checkpoint_record=read('acceleration/results/20261002_wave35_milestone01/checkpoint.json');need(checkpoint==snapshots[-1][1] and checkpoint_record['ledger_sha256']==FINAL and checkpoint_record['claim_records']==334,'EXACT_CHECKPOINT_BINDING')
        need(len(prior)==329 and len(current)==334 and Counter(c['status'] for c in current.values())=={'VERIFIED':327,'CANDIDATE':3,'REFUTED':4} and all(c['review_state']=='CLEAR' for c in current.values()),'EXACT_CLAIM_POPULATIONS')
        for cid in BINDINGS:
            for path,h in gold[cid]['paths'].items():pin(path,h)
        controls=[]
        mutations=[('old_claim','ALL_PRIOR_CLAIMS_UNCHANGED',lambda d:d['claims'][0].update(statement='changed')),('criterion_wrong_statement','BOUND_FIELD',lambda d:indexed(d['claims'])[CRITERION].update(statement='allgraphs nonexistent')),('criterion_target_broadening','BOUND_SCOPE',lambda d:indexed(d['claims'])[CRITERION]['scope'].update(target_resolution='NONEXISTENCE')),('census_general_exclusion','BOUND_FIELD',lambda d:indexed(d['claims'])[CENSUS].update(statement='Every root in every graph fails')),('nonedge_wrong_dependency','BOUND_DEPENDENCY_RELATION',lambda d:indexed(d['claims'])[NONEDGE]['dependencies'][0].update(relation='premise')),('edge_prismfree_scope','BOUND_SCOPE',lambda d:indexed(d['claims'])[EDGE]['scope'].update(description='Assumes no inducedprism')),('gf3_rank_promotion','BOUND_FIELD',lambda d:indexed(d['claims'])[GF3].update(statement='Exactrank23019')),('gf3_self_approval','BOUND_VERIFICATION_ROLE_METHOD',lambda d:indexed(d['claims'])[GF3]['verification'][0].update(verifier='/root/native_driver')),('wrong_verification_hash','EXACT_REVISION_HASH_BINDING',lambda d:indexed(d['claims'])[GF3]['verification'][0]['artifact_hashes'].update({indexed(d['claims'])[GF3]['evidence'][0]:'0'*64})),('missing_shared_components','BOUND_SHARED_CHECKER_COMPONENTS',lambda d:indexed(d['claims'])[EDGE]['verification'][0].update(shared_components=[])),('prior_availability_change','ALL_PRIOR_ARTIFACTS_UNCHANGED',lambda d:d['artifacts'][0].update(availability='MISSING'))]
        for name,expected,mutate in mutations:
            damaged=copy.deepcopy(snapshots[-1][1]);mutate(damaged)
            try:previous.transition(snapshots[0][0],damaged,BINDINGS,bindings,gold)
            except AuditError as e:need(e.stage==expected,'CONTROL_WRONG_STAGE',str(e));controls.append(dict(name=name,stage=e.stage,outcome='REJECTED'))
            else:raise AuditError('CORRUPT_TRANSITION_ACCEPTED',name)
        original=read(bindings[GF3]['editorial_correction']['preserved_original_binding']);altered=copy.deepcopy(bindings[GF3]);altered['statement']='changed'
        try:projection(GF3,altered,read(bindings[GF3]['report']),original)
        except AuditError as e:need(e.stage=='EXACT_GF3_EDITORIAL_SCOPE_PROJECTION','CONTROL_WRONG_STAGE');controls.append(dict(name='gf3_editorial_wrongstatement',stage=e.stage,outcome='REJECTED'))
        else:raise AuditError('CORRUPT_EDITORIAL_BINDING_ACCEPTED')
        for name in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261002_wave35_transition_v1_spec.md','acceleration/audit_20261002_wave34_transition_v1.py','acceleration/audit_20261002_wave31_transition_v1.py','acceleration/register_20261002_bound_claims_v9.py','acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock']:pin(name)
        report=dict(status='INDEPENDENT_WAVE35_EXACT329_TO334_TRANSITION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),verifier='/root/checkpoint_audit',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,before_frozen_ledger_sha256=START,after_frozen_ledger_sha256=FINAL,unchanged_prior_claims=329,current_claims=334,new_claim_ids=list(BINDINGS),status_counts=dict(Counter(c['status'] for c in current.values())),review_counts=dict(Counter(c['review_state'] for c in current.values())),successful_registration_directories=REGS,controls=controls,mathematical_replays=0,new_exclusions=0,target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator.',shared_components=['Pinned prior independent transition/UniqueLoader/indexed metadata checking code only,not registrar/discovery code.','Python YAML/SHA256/stdlib/command_deadline scheduling.'],limitations=['Frozen snapshots/checkpoint and direct exact bytes only; no live-ledger equivalence or process-state assertion.','No mathematical replay,independent scientific reapproval,graph realization,target exclusion orresolution.','GF3v2 schema scope projection preserves exactr1statement andreport; v1original/intermediate correction evidence retained.','Newcriterion is narrowly99point231lineartriple degree7; preservedbroaderdraft was notregistered.','Nonedge/edge domains certify necessary integer profiles only; edge verification_dependency reuses rawnecessitygeometry,notconditionaltheorem premise.','All329previous claim/verification/artifact availability records preserved; newartifactavailability remains LOCAL_ONLY before separate publication.'],elapsed_seconds=time.monotonic()-start,deadline=deadline.status())
        with (out/'summary.json').open('x',encoding='utf8',newline='\n') as s:json.dump(report,s,indent=2);s.write('\n')
        print(json.dumps(dict(status=report['status'],report_sha256=pin((out/'summary.json').relative_to(ROOT).as_posix()),elapsed_seconds=report['elapsed_seconds'])),flush=True)
    except BaseException as e:
        with (out/'failure.json').open('x',encoding='utf8') as s:json.dump(dict(error=repr(e),stage=getattr(e,'stage',None),inputs_sha256=pins,elapsed_seconds=time.monotonic()-start,outputs_preserved=True),s,indent=2)
        raise
if __name__=='__main__':main()
