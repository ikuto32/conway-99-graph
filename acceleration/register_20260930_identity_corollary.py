"""Add the separately checked constructive corollary to the eighth milestone."""
from datetime import datetime,timezone
import hashlib,json,copy,sys
from pathlib import Path
import yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old)
    audit=B+'independent_review/triangle_core_identity/summary.json'
    assert h(audit)=='a38394b4438c79e89e19095ff92fdb4c2d21e20284c0c417fb19c8a146913db3'
    r=json.loads((ROOT/audit).read_bytes());assert r['recommendation']=='VERIFIED'
    for p,value in r['inputs_sha256'].items():assert h(p)==value,p
    assert r['claim_id']not in{c['id']for c in data['claims']}
    aid='triangle-identity-construction-audit';now=datetime.now(timezone.utc).isoformat()
    data['artifacts'].append(dict(id=aid,path=audit,sha256=h(audit),availability='LOCAL_ONLY',retrieval='Exact independently checked report and its raw input bindings in this workspace.',unavailable_reason='Eighth milestone publication is pending.'))
    data['claims'].append(dict(id=r['claim_id'],revision=1,statement=r['statement'],kind=r['kind'],basis=r['basis'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description=r['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=['Positive even order and arbitrary three perfect matchings; all cross-fiber matchings are chosen to be identity for this local construction.','No nontrivial target automorphism is assumed.'],
        dependencies=r['dependencies'],evidence=[aid],verification=[dict(claim_revision=1,verifier=r['verifier'],method='independent_derivation',command_or_audit=audit,timestamp=r['timestamp'],outcome='PASS',scope=r['scope'],artifact_hashes={aid:h(audit)},shared_components=r['shared_components'],controls=['Complete3580 representative replay, four size controls, exact SRG(9,4,1,2) positive fixture, extra-edge and nonmatching negatives.'],limitations=r['limitations'])],
        limitations=r['limitations'],created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Internally reviewed direct corollary; no external review or novelty claim.'},reproducibility=dict(manifest=aid)))
    data['updated_at']=now
    result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'identity_corollary_registration');out.mkdir(parents=True,exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before);after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    receipt=dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=[r['claim_id']],previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=result,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'new_verified':1,'claim_population':len(data['claims']),'target_resolution':'UNKNOWN'}))
if __name__=='__main__':main()
