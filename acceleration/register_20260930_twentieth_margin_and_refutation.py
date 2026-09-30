"""Register an independent margin lemma and preserve a refuted support guess."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];D='acceleration/results/20260930_independent_review/hadamard_two_group_margin_cancellation/'
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==192
    pins={D+'summary.json':'9c16ea1e303fb9ef5832dd03512e487f8d6c7a285f2ef51f85cedabe1d81749f',D+'claim_binding.json':'822b2b15b8e5724af48e5ed06c42c52bfb2129bf615796a0aaa4d4cd4f794bdf',D+'refuted_intersection_premise.json':'d138abb55f4d37090f64f581d8d17501c5f9710ac8427a5053369ef7f547e349'}
    for p,sha in pins.items():assert h(p)==sha,p
    audit=read(D+'summary.json');row=read(D+'claim_binding.json');refutation=read(D+'refuted_intersection_premise.json')
    assert audit['status']=='INDEPENDENT_HADAMARD_TWO_GROUP_MARGIN_CANCELLATION_PASS'
    assert row['recommendation']=='VERIFIED' and row['verifier']=='/root/eight_domain_audit'
    bindings=dict(pins)
    for field in ['inputs_sha256','outputs_sha256']:
        for p,sha in audit.get(field,{}).items():assert h(p)==sha,p;assert p not in bindings or bindings[p]==sha;bindings[p]=sha
    evidence=[];hashes={}
    for i,p in enumerate(pins):
        aid=f'twentieth-margin-evidence{i}';assert aid not in{a['id'] for a in data['artifacts']};evidence.append(aid);hashes[aid]=h(p)
        data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; includes complete190-pair raw census, controls and counterexample.',unavailable_reason='Twentieth immutable publication not yet confirmed.'))
    dependencies=[{k:v for k,v in dep.items() if k in ['id','revision','relation']} for dep in row['dependencies']]
    v=dict(claim_revision=1,verifier=row['verifier'],method='independent_derivation',command_or_audit=D+'summary.json',timestamp=audit['timestamp'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=audit['shared_components'],controls=[row['method'],'Eight corrupted controls rejected; positive row-margin fixture is explicitly not a full-Gram factor.'],limitations=row['limitations'])
    claim=dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row['assumptions'],dependencies=dependencies,evidence=evidence,verification=[v],limitations=row['limitations'],created_at=row['created_at'],updated_at=row['updated_at'],external_source=None,unknowns={'external_source':'Internal independent derivation only.'},reproducibility=dict(manifest=evidence[0]))
    now=datetime.now(timezone.utc).isoformat()
    wrong=copy.deepcopy(claim);wrong.update(id='C-FIXED-HADAMARD-SUPPORT-INTERSECTIONS-ZERO-OR-THREE',statement='Every pair of distinct six-coordinate support groups in the pinned six-prism support has intersection size zero or three.',basis=['COMPUTED'],status='REFUTED',scope=dict(description='A proposed finite-support intersection restriction; explicitly false on this raw input.',unrestricted_target=False,target_resolution='NONE'),assumptions=['The exact pinned raw support and its first-occurrence group ordering.'],limitations=['The refuted restriction must not be used for normalization, pruning or exception-group coverage.','Refutation does not invalidate the separate general margin-cancellation identity.'],created_at=now,updated_at=now,unknowns={'external_source':'No literature source; this was a tentative root research guess.','original_derivation':'No proof was produced; the exact raw counterexample disproves the proposed restriction.'})
    wrong['verification']=[dict(v,method='independent_artifact_check',outcome='FAIL',scope='Exact statement disproved: groups0and1 intersect in coordinates4and6, size2.',controls=['All190 support-pair intersections independently reconstructed; raw counterexample retained.'],limitations=wrong['limitations'])]
    for c in [claim,wrong]:assert c['id']not in{oldc['id'] for oldc in data['claims']};data['claims'].append(c)
    data['updated_at']=now;assert data['claims'][:-2]==old['claims'] and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentieth_margin_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=[claim['id'],wrong['id']],checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN',new_verified=1,new_refuted=1)
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=1,new_refuted=1)))
if __name__=='__main__':main()
