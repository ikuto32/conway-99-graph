"""Register the independently checked finite collection without adding coverage."""
from datetime import datetime,timezone
from pathlib import Path
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';D=B+'independent_review/hadamard_phase_premise_orders/'
def h(p):
    with(ROOT/p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==182
    pins={D+'summary.json':'5bc72f2b3154d3e927c7b690e70d5c4b3dc0c362fffb739b6bf5ccab13ed3910',D+'claim_binding.json':'5d9bd877838c295e974f06fbdb813b3b4f6b8425f3518be8fb7a23f56f3721dd',D+'unique_clauses.json':'65f3b412e1836edb61182de9c2d8ca0668bb72ae574483a1c5e8027fccc8b4fb'}
    for p,sha in pins.items():assert h(p)==sha,p
    row=read(D+'claim_binding.json');audit=read(D+'summary.json');assert audit['status']=='INDEPENDENT_TWELVE_ORDER_PHASE_PREMISE_COLLECTION_PASS'
    assert row['status']=='VERIFIED'and row['review_state']=='CLEAR'and row['revision']==1
    assert row['id']not in{c['id']for c in data['claims']};bindings=dict(pins)
    for field in ['inputs_sha256','outputs_sha256']:
        for p,sha in audit[field].items():assert h(p)==sha,p;assert p not in bindings or bindings[p]==sha;bindings[p]=sha
    evidence=[];hashes={}
    for index,p in enumerate(pins):
        aid=f'nineteenth-premise-collection-evidence{index}';assert aid not in{a['id']for a in data['artifacts']}
        evidence.append(aid);hashes[aid]=h(p);data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; audit binds every raw certificate and trial.',unavailable_reason='Nineteenth immutable evidence publication is not yet confirmed.'))
    v=dict(claim_revision=1,verifier=row['verifier'],method='independent_artifact_check',command_or_audit=D+'summary.json',timestamp=audit['timestamp'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,
        shared_components=row['shared_components'],controls=['Every12 certificate and240 membership decision, exact seed/order and checkpoint identities, literal clause maps and all pairwise subsumption checks.'],limitations=row['limitations'])
    data['claims'].append(dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row['assumptions'],dependencies=row['dependencies'],evidence=evidence,verification=[v],limitations=row['limitations'],created_at=row['created_at'],updated_at=row['updated_at'],external_source=None,unknowns={'external_source':'Independent internal checking only; no external acceptance or novelty claim.'},reproducibility=dict(manifest=evidence[0])))
    assert data['claims'][:-1]==old['claims']and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now;validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/(B+'nineteenth_premise_collection_registration');out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    record=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=[row['id']],checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN',coverage_note='The11distinct excluded pattern families overlap; no union size or target-wide denominator claimed.')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(new_verified=1,claim_population=183,verified_clear=181,target_resolution='UNKNOWN')))
if __name__=='__main__':main()
