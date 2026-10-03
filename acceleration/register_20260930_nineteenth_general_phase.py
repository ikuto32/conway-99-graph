"""Integrate two already independently approved phase results; no self-approval."""
from datetime import datetime,timezone
from pathlib import Path
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
def h(p):
    with(ROOT/p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==180
    dirs=[I+'hadamard_general_f3_phase_necessity/',I+'hadamard_phase_premise_subset/']
    pins={dirs[0]+'summary.json':'30dd4e571140a139f7e36baf47f62a4428b752c79bbddd164ec6e54f3b232d67',
        dirs[0]+'claim_binding.json':'c8e35f77dc16d84dd56ed725e695ea0ddf9c3a30a1b04194972dd88a7566f91e',
        dirs[0]+'registry_dependency_addendum.json':'edbc06bef2014276044471ebe7fd62a033869a557a96f3c42c5e2532175ff9a4',
        dirs[1]+'summary.json':'0a475da571e5766594f3b675b4348af76814c17b4f0fd2f0484de98428429c20',
        dirs[1]+'claim_binding.json':'8ae421c6e9de6b88a7aaefdcc031d7d0d6d955d1038e6753dbf268d1a59b45eb',
        dirs[1]+'verified_nogood.json':'f25f3c876a7285be983061852259060d8ea2d07cecafef9dfb43d6928230c287'}
    for p,sha in pins.items():assert h(p)==sha,p
    rows=[read(d+'claim_binding.json')for d in dirs];audits=[read(d+'summary.json')for d in dirs]
    assert audits[0]['status']=='INDEPENDENT_GENERAL_BALANCED_GF3_PHASE_NECESSITY_PASS'
    assert audits[1]['status'].endswith('_PASS')
    mapping=read(dirs[0]+'registry_dependency_addendum.json')
    assert mapping['status']=='APPROVED_EDITORIAL_REGISTRY_MAPPING'and mapping['claim_id']==rows[0]['id']and mapping['claim_revision']==1
    assert mapping['claim_binding_sha256']==pins[dirs[0]+'claim_binding.json']and mapping['original_dependencies']==rows[0]['dependencies']and mapping['verifier']==rows[0]['verifier']
    rows[0]['dependencies']=mapping['ledger_dependencies'];bindings=dict(pins)
    for audit in audits:
        for field in ['inputs_sha256','outputs_sha256']:
            for p,sha in audit[field].items():assert h(p)==sha,p;assert p not in bindings or bindings[p]==sha;bindings[p]=sha
    extras=[[dirs[0]+'registry_dependency_addendum.json',dirs[0]+'dependency_controls.json'],[dirs[1]+'verified_nogood.json',dirs[1]+'certificate_replay.json']]
    now=datetime.now(timezone.utc).isoformat();ids=[]
    for index,(row,audit,directory)in enumerate(zip(rows,audits,dirs,strict=True)):
        assert row['status']=='VERIFIED'and row['review_state']=='CLEAR'and row['revision']==1
        assert row['id']not in {c['id']for c in data['claims']}
        evidence=[];hashes={}
        for j,p in enumerate([directory+'summary.json',directory+'claim_binding.json',*extras[index]]):
            aid=f'nineteenth-general-phase-{index}-evidence{j}';assert aid not in {a['id']for a in data['artifacts']}
            assert bindings[p]==h(p);evidence.append(aid);hashes[aid]=h(p)
            data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; independent audit binds raw inputs and certificates.',unavailable_reason='Nineteenth immutable evidence publication is not yet confirmed.'))
        shared=mapping['shared_components']if index==0 else row['shared_components']
        controls=['All900 local and150 pair configurations,150 gauge types, explicit omitted-dependency counterexample and eleven corruptions.'if index==0 else
            'All20 deletion membership checks by a separate rank implementation,729 tiny span controls,ten corruptions,and literal14selector mapping.']
        v=dict(claim_revision=1,verifier=row['verifier'],method='independent_artifact_check',command_or_audit=directory+'summary.json',timestamp=audit['timestamp'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=shared,controls=controls,limitations=row['limitations'])
        data['claims'].append(dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',
            scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row['assumptions'],dependencies=row['dependencies'],evidence=evidence,verification=[v],limitations=row['limitations'],created_at=row['created_at'],updated_at=row['updated_at'],external_source=None,
            unknowns={'external_source':'Independent internal checking only; no external acceptance or novelty claim.'},reproducibility=dict(manifest=evidence[0])))
        ids.append(row['id'])
    assert data['claims'][:len(old['claims'])]==old['claims']and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    data['updated_at']=now;validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/(B+'nineteenth_general_phase_registration');out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    record=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=bindings,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,approved_dependency_translation=mapping,
        existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(new_verified=2,claim_population=len(data['claims']),verified_clear=sum(c['status']=='VERIFIED'and c['review_state']=='CLEAR'for c in data['claims']),target_resolution='UNKNOWN')))
if __name__=='__main__':main()
