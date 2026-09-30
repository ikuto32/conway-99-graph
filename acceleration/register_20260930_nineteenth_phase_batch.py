"""Register three exact independently checked batch claims and missing traces."""
from datetime import datetime,timezone
from pathlib import Path
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1]
D='acceleration/results/20260930_independent_review/hadamard_parity_phase_batch_outcome/'
def h(p):
    with(ROOT/p).open('rb')as s:return hashlib.file_digest(s,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    ledger=ROOT/'CLAIMS.yaml';before=ledger.read_bytes();old=registry.read_ledger(ledger);data=copy.deepcopy(old);assert len(data['claims'])==184
    pins={D+'summary.json':'b620e76595c8709cb58c4bcd4432c681620d046da905e87aef7fd58ee2479635',D+'claim_bindings.json':'a47db3131e71e44dc70807b7e878c82ba205304aef35eedd2f4d75d5c2b99a2f'}
    for p,sha in pins.items():assert h(p)==sha,p
    audit=read(D+'summary.json');rows=read(D+'claim_bindings.json');assert audit['status']=='INDEPENDENT_HADAMARD_PARITY_PHASE_BATCH_OUTCOME_PASS' and len(rows)==3
    bindings=dict(pins)
    for field in ['inputs_sha256','outputs_sha256']:
        for p,sha in audit[field].items():assert h(p)==sha,p;assert p not in bindings or bindings[p]==sha;bindings[p]=sha
    added={};ids=[]
    def artifact(p):
        if p in added:return added[p]
        aid=f'nineteenth-phase-batch-evidence{len(added)}';assert aid not in{a['id'] for a in data['artifacts']}
        data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; audit transitively binds all native and exact phase artifacts.',unavailable_reason='Nineteenth immutable publication not yet confirmed.'));added[p]=aid;return aid
    for row in rows:
        assert row['recommendation']=='VERIFIED' and row['review_state']=='CLEAR' and row['revision']==1
        assert row['id']not in{c['id'] for c in data['claims']};assert row['verifier']=='/root/eight_domain_audit'
        paths=list(dict.fromkeys([*pins,*row['evidence']]));evidence=[artifact(p) for p in paths];hashes={artifact(p):h(p) for p in paths}
        verification=dict(claim_revision=1,verifier=row['verifier'],method='independent_artifact_check',command_or_audit=D+'summary.json',timestamp=audit['timestamp'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=audit['shared_components'],controls=['Complete three SAT assignment/CNF/raw projection/phase checks; two literal contradiction certificates; reverse-column rank/kernel; exact terminal receipt; nine additional corruptions.'],limitations=row['limitations']+['Learned traces are currently MISSING; no checked mathematical statement depends on their availability.'])
        data['claims'].append(dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row['assumptions'],dependencies=row['dependencies'],evidence=evidence,verification=[verification],limitations=row['limitations'],created_at=row['created_at'],updated_at=row['updated_at'],external_source=None,unknowns={'external_source':'Internal independent review; no external acceptance or novelty claim.'},reproducibility=dict(manifest=evidence[0])));ids.append(row['id'])
    for trace in read(D+'trace_availability.json'):
        assert trace['current_availability']=='MISSING'
        aid=f"nineteenth-phase-batch-missing-trace{trace['index']}";assert aid not in{a['id'] for a in data['artifacts']}
        data['artifacts'].append(dict(id=aid,path=None,sha256=trace['historical_sha256'],availability='MISSING',retrieval=None,unavailable_reason='Original WSL path '+trace['linux_path']+' is unavailable at the saved independent observation. No alternate copy identified; cause UNKNOWN. Historical size/hash receipts remain in '+D+'trace_availability.json. Not used as an UNSAT proof or as a premise of a verified claim.'))
    assert data['claims'][:-3]==old['claims'] and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now;validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_nineteenth_phase_batch_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert ledger.read_bytes()==before;ledger.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN',counts=audit['counts'],coverage_note='Three unique finite samples; two exact branches excluded. Stages overlap. No target-wide denominator.')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as s:json.dump(result,s,indent=2);s.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=3,missing_trace_artifacts=4)))
if __name__=='__main__':main()
