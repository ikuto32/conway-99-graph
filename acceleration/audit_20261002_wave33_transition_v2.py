"""Read-only318-to324 audit v2; allow absent old notes only for no-reason deps."""
from collections import Counter
import copy,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import yaml
from audit_20261002_wave31_transition_v1 import UniqueLoader,indexed,need

ROOT=Path(__file__).resolve().parents[1]
REGS=['acceleration/results/20261002_wave33_registration'+s for s in ['02','03','06','08']]
BINDINGS={
 'C-HYPERGRAPH-ANNEAL-V1-FINITE-ENGINEERING-CONTROLS':('acceleration/results/20261002_independent_review/hypergraph_controls02/claim_binding.json','089f8b8ead68298fbe0f96cbd104b1975427058451269017c30d6ca02db56fcf'),
 'C-PRISMFREE-ROOTED7-MARKED-REROOT-NECESSARY-ENCODING':('acceleration/results/20261002_independent_review/rooted7_model01/claim_binding.json','96d139186fd243a84831abb92d4d611cfe001043309719b998f563979a311b25'),
 'C-ROOTED7-LITERAL-AFFINE-RATIONAL-WITNESS-RECTANGLE':('acceleration/results/20261002_independent_review/rooted7_corner_witnesses01/claim_binding.json','c86c8aaa81b82f24de95d9a1b4d6b1010f05a429d95e7ae6951f21bc17485636'),
 'C-HYPERGRAPH-ANNEAL-PILOT01-SAVED-BEST-OBJECT':('acceleration/results/20261002_independent_review/hypergraph_pilot_review01/claim_binding.json','9b79be7d562255982aa963152795720a45ebed52b6b3e0f9ab8240b52546a779'),
 'C-PRISMFREE-ROOTED8-NONEDGE-LOCAL-CATALOGUE-COVERAGE':('acceleration/results/20261002_independent_review/rooted8_catalogue01/claim_binding.json','6119158229ea692cbcb1e12db86a1ae112f3880ff9a492dcd35c704adb72835d'),
 'C-PRISMFREE-ROOTED8-MARKED-UNIVERSAL5-PRODUCT-NECESSARY-ENCODING':('acceleration/results/20261002_independent_review/rooted8_model01/claim_binding.json','461b9f4f3ad9661a0f921ba8c4e9936fade3d30b7dac071ae1d2b341c3baa097'),
}
FINAL='dbb72994ed9f43c88b3227ec8940d355aca244ac4b05b58dca6ba8b436cb9b96'


def transition(before,after,expected,bindings):
    old,new=indexed(before['claims']),indexed(after['claims']);old_artifacts,artifacts=indexed(before['artifacts']),indexed(after['artifacts'])
    need(set(new)-set(old)==set(expected) and set(old)<=set(new),'EXACT_ADDITIONS')
    need(all(new[cid]==value for cid,value in old.items()),'ALL_PRIOR_CLAIM_RECORDS_UNCHANGED')
    need(all(artifacts[aid]==value for aid,value in old_artifacts.items()),'ALL_PRIOR_ARTIFACT_RECORDS_UNCHANGED')
    for name in set(before)|set(after):
        if name not in ['claims','artifacts','updated_at']:need(before[name]==after[name],'TOPLEVEL_SEMANTICS_UNCHANGED:'+name)
    need(after['target']['status']=='UNKNOWN' and after['target']['overall_search_coverage'] is None,'TARGET_AND_COVERAGE_UNKNOWN')
    new_evidence=set()
    for cid in expected:
        claim,binding=new[cid],bindings[cid]
        for field in ['id','revision','statement','kind','basis','status','review_state','assumptions','limitations','scope']:need(claim[field]==binding[field],'BOUND_FIELD:'+cid+':'+field)
        need(claim['scope']['target_resolution']=='NONE' and claim['revision']==1 and claim['status']=='VERIFIED' and claim['review_state']=='CLEAR','EXACT_NONRESOLUTION_REVISION')
        projected=[{key:dep[key] for key in ['id','revision','relation']} for dep in binding['dependencies']]
        need(claim['dependencies']==projected,'EXACT_DEPENDENCY_RELATION_PROJECTION')
        notes=[{key:dep[key] for key in ['id','revision','reason']} for dep in binding['dependencies'] if 'reason' in dep]
        if 'dependency_notes' in claim['unknowns']:
            need(json.loads(claim['unknowns']['dependency_notes'])==notes,'DEPENDENCY_REASON_PRESERVED')
        else:
            need(not notes,'HISTORICAL_NO_NOTES_ONLY_WHEN_NO_BOUND_REASON')
        for dep in projected:need(dep['id'] in new and dep['revision']==new[dep['id']]['revision'],'PINNED_DEPENDENCY_REVISION')
        need(len(claim['verification'])==1,'ONE_BOUND_INDEPENDENT_RECORD');record=claim['verification'][0]
        method='independent_derivation' if binding['method']=='independent_derivation_and_complete_artifact_checking' else binding['method']
        need(record['method']==method and record['claim_revision']==1 and record['outcome']=='PASS' and record['verifier']==binding['verifier']!=binding['producer'],'EXACT_INDEPENDENT_METHOD_ROLE')
        if cid.startswith('C-PRISMFREE-ROOTED8-'):need(claim['unknowns']['original_binding_method']==binding['method'],'ROOT8_COMBINED_METHOD_RETAINED')
        elif cid=='C-ROOTED7-LITERAL-AFFINE-RATIONAL-WITNESS-RECTANGLE':need(binding['verifier']=='/root/native_driver' and binding['producer']=='/root/structural' and binding['report_sha256']=='382459c568c8e5f9251746f60376e07c82ba981d1bab68ae2c0bc22790f04ca1','EXACT_LITERAL_WITNESS_ROLE')
        else:need(binding['verifier']=='/root/checkpoint_audit','EXACT_OTHER_VERIFIER_ROLE')
        need(record['timestamp']==binding['verification_timestamp'] and record['scope']==binding['scope']['description'] and record['limitations']==binding['limitations'] and record['command_or_audit']==binding['report'],'EXACT_CHECKING_SCOPE')
        need(record['shared_components']==binding['shared_components'],'SHARED_CHECKER_COMPONENTS_DISCLOSED')
        expected_paths=dict(binding['inputs_sha256']);expected_paths[binding['report']]=binding['report_sha256'];expected_paths[BINDINGS[cid][0]]=BINDINGS[cid][1]
        for collection in ['artifacts','evidence']:
            values=binding.get(collection,[])
            if isinstance(values,dict):
                for key,value in values.items():
                    if not key.endswith('_sha256'):need(key+'_sha256' in values,'EXACT_PAIRED_EVIDENCE');expected_paths[value]=values[key+'_sha256']
            else:
                for value in values:
                    if isinstance(value,dict) and 'path' in value:expected_paths[value['path']]=value['sha256']
        actual_paths={artifacts[aid]['path']:artifacts[aid]['sha256'] for aid in claim['evidence']}
        need(actual_paths==expected_paths and len(actual_paths)==len(claim['evidence']),'COMPLETE_BOUND_EVIDENCE_POPULATION')
        need(set(record['artifact_hashes'])==set(claim['evidence']) and all(record['artifact_hashes'][aid]==artifacts[aid]['sha256'] for aid in claim['evidence']),'EXACT_REVISION_ARTIFACT_HASH_BINDING')
        need(json.loads(record['controls'][0])==binding['controls'],'EXACT_CALIBRATION_RECORD')
        need(all(artifacts[aid]['availability']=='LOCAL_ONLY' for aid in claim['evidence']),'NEW_AVAILABILITY_NOT_ASSUMED')
        new_evidence.update(claim['evidence'])
        if cid.startswith('C-PRISMFREE-'):need(binding['premise_state']['no_induced_triangular_prism']=='UNKNOWN' and 'UNKNOWN' in claim['unknowns']['premises'],'PRISM_PREMISE_UNESTABLISHED')
    need(set(artifacts)-set(old_artifacts)==new_evidence,'NO_UNBOUND_NEW_ARTIFACT_RECORDS')
    return old,new,artifacts


def main():
    pins={}
    def pin(name,wanted=None):
        with (ROOT/name).open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
        need(wanted is None or wanted==actual,'PIN:'+name);pins[name]=actual
    def read(name,wanted=None):pin(name,wanted);return json.loads((ROOT/name).read_bytes())
    bindings={cid:read(path,digest) for cid,(path,digest) in BINDINGS.items()};snapshots=[];summaries=[];previous='bf637b857adb9610f67253bd16bd99fe092bfe46cee0f02d95afbc4bf9151bdc'
    for directory in REGS:
        report=read(directory+'/summary.json');need(report['before_ledger_sha256']==previous and report['mathematical_replays']==0,'FROZEN_CHAIN_CONTIGUOUS')
        before_name,after_name=directory+'/CLAIMS.before.yaml',directory+'/CLAIMS.after.yaml';pin(before_name,previous);pin(after_name,report['ledger_sha256'])
        before=yaml.load((ROOT/before_name).read_text(encoding='utf8'),Loader=UniqueLoader);after=yaml.load((ROOT/after_name).read_text(encoding='utf8'),Loader=UniqueLoader)
        if snapshots:need(snapshots[-1][1]==before,'FROZEN_CHAIN_BYTE_SEMANTICS')
        transition(before,after,report['new_claim_ids'],bindings);snapshots.append((before,after));summaries.append(report);previous=report['ledger_sha256']
    need(previous==FINAL,'EXACT_FINAL_LEDGER');old,new,artifacts=transition(snapshots[0][0],snapshots[-1][1],BINDINGS,bindings)
    need(len(old)==318 and len(new)==324 and Counter(c['status'] for c in new.values())=={'VERIFIED':317,'CANDIDATE':3,'REFUTED':4},'EXACT_CLAIM_POPULATIONS')
    for cid,binding in bindings.items():
        report=read(binding['report'],binding['report_sha256'])
        # Some reports cover multiple literal checks; their bound narrow claim
        # record must be identical where an exact statement is supplied.
        if 'statement' in report:need(report['statement']==binding['statement'],'EXACT_SCIENTIFIC_STATEMENT')
        need(report.get('target_resolution',False) in [False,'NONE','UNKNOWN'],'NO_REPORT_TARGET_PROMOTION')
        for aid in new[cid]['evidence']:artifact=artifacts[aid];pin(artifact['path'],artifact['sha256'])
        if cid=='C-HYPERGRAPH-ANNEAL-PILOT01-SAVED-BEST-OBJECT':need('3034' in binding['statement'] and '427' in binding['statement'] and '2607' in binding['statement'] and binding['scope']['unrestricted_target'] is False,'EXACT_ONE_GRAPH_EMPIRICAL_SCOPE')
    rejected=[]
    for label,mutate,message in [('prior_claim',lambda data:data['claims'][0].update(statement='changed'),'ALL_PRIOR_CLAIM_RECORDS_UNCHANGED'),
       ('broadened_target',lambda data:data['claims'][-1]['scope'].update(target_resolution='NONEXISTENCE'),'BOUND_FIELD:'+list(BINDINGS)[-1]+':scope'),
       ('wrong_method_adapter',lambda data:data['claims'][-1]['verification'][0].update(method='external_review'),'EXACT_INDEPENDENT_METHOD_ROLE'),
       ('evidence_hash',lambda data:data['claims'][-1]['verification'][0]['artifact_hashes'].update({data['claims'][-1]['evidence'][0]:'0'*64}),'EXACT_REVISION_ARTIFACT_HASH_BINDING')]:
        damaged=copy.deepcopy(snapshots[-1][1]);mutate(damaged)
        try:transition(snapshots[0][0],damaged,BINDINGS,bindings)
        except ValueError as error:need(str(error)==message,'EXACT_NEGATIVE_DIAGNOSTIC:'+str(error));rejected.append(dict(label=label,diagnostic=message))
        else:raise ValueError('CORRUPTED_TRANSITION_ACCEPTED')
    for name in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261002_wave31_transition_v1.py','acceleration/register_20261002_bound_claims_v7.py','uv.lock','pyproject.toml']:pin(name)
    summary=dict(status='INDEPENDENT_WAVE33_EXACT318_TO324_TRANSITION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,
        previous_claims=318,current_claims=324,unchanged_prior_claims=318,new_claim_ids=list(BINDINGS),clear_status_counts=dict(Counter(c['status'] for c in new.values() if c['review_state']=='CLEAR')),final_frozen_ledger_sha256=FINAL,
        controls=rejected,new_exclusions=0,target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator.',mathematical_replays=0,
        scope='Frozen318-to324 exact ledger/evidence transition; all old claim/artifact records retained and all six added revisions match their precise independent bindings, including evidence/dependency/method-role adapters.',
        limitations=['No mathematical replay or present live-ledger/publication assertion.','Root8 method projection preserves the original combined checking descriptor; literal witness role is limited to the exact native_driver checking of structural producer objects.','Prism absence remains UNKNOWN, rational witnesses realize no graphs, and pilot graph E3034 is not an SRG.'])
    out=ROOT/'acceleration/results/20261002_independent_review/wave33_transition02';out.mkdir(exist_ok=False)
    with (out/'summary.json').open('x',encoding='utf8',newline='\n') as stream:json.dump(summary,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(path=(out/'summary.json').relative_to(ROOT).as_posix(),sha256=hashlib.sha256((out/'summary.json').read_bytes()).hexdigest())))


if __name__=='__main__':main()
