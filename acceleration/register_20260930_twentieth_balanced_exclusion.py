"""Register independent approval; this registrar does not verify mathematics."""
from datetime import datetime,timezone
from pathlib import Path
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1]
D='acceleration/results/20260930_independent_review/hadamard_balanced_gram_unsat_v2/'
def h(p):
    with(ROOT/p).open('rb')as s:return hashlib.file_digest(s,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    ledger=ROOT/'CLAIMS.yaml';before=ledger.read_bytes();old=registry.read_ledger(ledger);data=copy.deepcopy(old)
    assert len(data['claims'])==191
    pins={D+'summary.json':'edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5',D+'claim_binding.json':'da711189190afebf5efbb005ae8b6cccc8ada41c995f7dc7f47694110682868b'}
    pins['acceleration/results/20260930_hadamard_balanced_gram_cnf/instance.cnf']='c2d780f94dac4dda955743df03f8db2e8ec0f51217c671eb19fc5e42ed69ba37'
    pins['acceleration/results/20260930_hadamard_balanced_gram_native_pilot/main/proof.drat']='94d2ab35c76b61f3deb01ebfd9ca0dc70452bddf847383d5838b2b2ca902396b'
    for p,sha in pins.items():assert h(p)==sha,p
    row=read(D+'claim_binding.json');audit=read(D+'summary.json')
    assert row['verifier']=='/root/structural_attack' and row['producer']=='/root'
    assert row['status']=='VERIFIED' and row['review_state']=='CLEAR' and row['revision']==1
    assert row['id']not in{c['id'] for c in data['claims']}
    bindings=dict(pins)
    for field in ['inputs_sha256','outputs_sha256']:
        for p,sha in audit[field].items():assert h(p)==sha,p;assert p not in bindings or bindings[p]==sha;bindings[p]=sha
    evidence=[];hashes={}
    for i,p in enumerate(pins):
        aid=f'twentieth-balanced-exclusion-evidence{i}';assert aid not in{a['id'] for a in data['artifacts']}
        evidence.append(aid);hashes[aid]=h(p)
        data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; independent audit binds original CNF, complete proof, checker provenance, commands and controls. Raw proof transport packages are separate evidence.',unavailable_reason='Twentieth immutable publication not yet confirmed; original raw proof retained locally.'))
    verification=dict(claim_revision=1,verifier=row['verifier'],method='independent_artifact_check',command_or_audit=D+'summary.json',timestamp=audit['timestamp'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=row['shared_components'],controls=['Complete exact227098316-byte DRAT replay with authenticated checker, positive proof and four corrupted proof/input controls plus six corrupted native receipts. Initial source-authentication wrapper failure preserved.'],limitations=row['limitations'])
    data['claims'].append(dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row['assumptions'],dependencies=row['dependencies'],evidence=evidence,verification=[verification],limitations=row['limitations'],created_at=row['created_at'],updated_at=row['updated_at'],external_source=None,unknowns={'external_source':'Internal independent review; no external acceptance or novelty claim.'},reproducibility=dict(manifest=evidence[0])))
    assert data['claims'][:-1]==old['claims'] and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentieth_balanced_exclusion_registration';out.mkdir(exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before);after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    assert ledger.read_bytes()==before;ledger.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=[row['id']],checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN',coverage_note='Complete balanced construction class excluded on one literal support; no arbitrary-support, whole-core or unrestricted-target coverage.')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as s:json.dump(result,s,indent=2);s.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=1)))
if __name__=='__main__':main()
