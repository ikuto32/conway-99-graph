"""Register three exact scoped claims approved by separate independent checkers."""
from datetime import datetime, timezone
from pathlib import Path
import copy, hashlib, json, subprocess, sys
import yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'; I=B+'independent_review/'
def h(path):
    with(ROOT/path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())

def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old)
    assert len(data['claims'])==165
    pins={I+'hadamard_six_prism_cyclic_reduction/summary.json':'7b9d988b946284d7a9fbcccccf1c2f32592dbdeb2e30cb6201e1565ea75d4de1',
          I+'hadamard_cyclic_factor_cnf/summary.json':'494add3aecbd2d7d4629c738be73dda3a884c89ecb624fbdb5e867dca2a6ad64',
          I+'hadamard_cyclic_unsat/summary.json':'83029350b25523c015dfe916d8056324c0970021d2b024d68941dd41fb8c2b70',
          I+'hadamard_cyclic_named_dependencies/summary.json':'ff09e34c3d8beec13a98fae12a15bb6fc87ecc7f90d842c93deb776fb46b565d'}
    for p,sha in pins.items():assert h(p)==sha,p
    reduction=read(I+'hadamard_six_prism_cyclic_reduction/summary.json')
    reduction['id'],reduction['revision']=reduction['claim_id'],reduction['claim_revision']
    rows=[reduction]
    gates=[I+'hadamard_six_prism_cyclic_reduction/summary.json',I+'hadamard_cyclic_factor_cnf/summary.json',I+'hadamard_cyclic_unsat/summary.json']
    addendum=read(I+'hadamard_cyclic_named_dependencies/summary.json')
    for update in addendum['claim_updates']:
        row=read(update['source_binding_path']);assert h(update['source_binding_path'])==update['source_binding_sha256']
        for key in ['id','revision','statement','scope','assumptions','recommendation','review_state']:assert row[key]==update[key],key
        row['dependencies']=copy.deepcopy(update['dependencies']);rows.append(row)
    bindings=dict(pins)
    for gate in gates+[I+'hadamard_cyclic_named_dependencies/summary.json']:
        audit=read(gate);assert audit['status'].endswith('_PASS')
        for p,sha in audit['inputs_sha256'].items():assert h(p)==sha,p;bindings[p]=sha
    now=datetime.now(timezone.utc).isoformat();newids=[]
    for index,(row,gate) in enumerate(zip(rows,gates,strict=True)):
        assert row['recommendation']=='VERIFIED' and row['review_state']=='CLEAR' and row['revision']==1
        assert row['id'] not in {c['id']for c in data['claims']}
        audit=read(gate)
        evidence_paths=[gate]
        if index:evidence_paths.append(I+'hadamard_cyclic_named_dependencies/summary.json')
        if index==2:evidence_paths.append(B+'hadamard_cyclic_native_pilot/main/proof.drat')
        evidence=[];hashes={}
        for j,p in enumerate(evidence_paths):
            aid=f'seventeenth-cyclic-{index}-evidence{j}';assert aid not in {a['id']for a in data['artifacts']}
            evidence.append(aid);hashes[aid]=h(p);bindings[p]=h(p)
            reason='Seventeenth-cohort immutable publication is not yet confirmed.'
            retrieval='Exact workspace path and complete pinned independent audit.'
            if p.endswith('proof.drat'):
                reason='Raw proof retained locally; lossless public packaging awaits publication.'
                retrieval='Recover from acceleration/results/20260930_hadamard_cyclic_proof_packages/artifact_packages.json; authenticate the exact raw SHA256 before replay.'
            data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval=retrieval,unavailable_reason=reason))
        timestamp=audit.get('updated_at',audit.get('timestamp'))
        verification=dict(claim_revision=1,verifier=row['verifier'],method='independent_derivation' if index==0 else 'independent_artifact_check',
            command_or_audit=gate,timestamp=timestamp,outcome='PASS',scope=row['scope'],artifact_hashes=hashes,
            shared_components=audit['shared_components'],controls=[
                'Independent semantic reduction, complete gauge/Gram/cap checks and nine corruptions.' if index==0 else
                'Every CNF clause and threshold relation independently reconstructed with local truth controls.' if index==1 else
                'Complete exact proof replay with fresh tiny positive and four corrupt proof/formula controls; six corrupt native receipts rejected.'
            ],limitations=row['limitations'])
        if index:
            verification['shared_components']=verification['shared_components']+['Named-dependency addendum from the same independent verifier binds the exact reduction claim revision.']
        data['claims'].append(dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',
            scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row['assumptions'],dependencies=row['dependencies'],
            evidence=evidence,verification=[verification],limitations=row['limitations'],created_at=now,updated_at=now,external_source=None,
            unknowns={'external_source':'Internal independent checks only; no external acceptance or novelty claim.'},reproducibility=dict(manifest=evidence[0])))
        newids.append(row['id'])
    data['updated_at']=now
    result=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'seventeenth_cyclic_registration');out.mkdir(exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before);after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    receipt=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        new_claim_ids=newids,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),
        validation=result,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf-8',newline='\n')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(new_verified=3,claim_population=len(data['claims']),target_resolution='UNKNOWN')))
if __name__=='__main__':main()
