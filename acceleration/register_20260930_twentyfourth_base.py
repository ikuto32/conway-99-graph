"""Register three independently checked results and one exact formula refutation."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
COHORTS=[('count_gram_intervals', 'ebace5fc527bded41f3c31fb66455e78b0eb133c8575508d4426eff912e6ae33', 'claim_binding.json', '6dc1fc4dba6df6fffad19335ccb0c37353e54cb4a5f0147165ec05dca38d07cb', 1, '/root'), ('hadamard_seven_profile_cnf', '3d000917a2c0e9fedd2cd5ca8df9a81502f3cb511df3b97a24b679e06c4955d1', 'claim_binding.json', 'bd75613bdda9b52c34b51b9c663328f040993aa740e5011abf7e4fcf014722bd', 1, '/root'), ('hadamard_seven_profile_unsat', 'ff0ce1b606f0fd8c96ba4b4d892943b86abf09c9bb3c32ed3db02702a9e516a2', 'claim_binding.json', '0ca33129dca869a88ad7682cfb4a47c27273d67f491635fd94ae45daa8f88695', 1, '/root/structural_attack'), ('local_frechet_equality', 'f888dae9caee35f174c424169bc4784b5404ef783b0943f04a444bf6b3b558af', 'claim_binding.json', '1d717a88682a7576f47698bdbc3726d8d2879890fb895d2fa6e7d5b168f389e5', 1, '/root/structural_attack')]

def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==229
    bindings={};ids=[]
    for index,(directory,pin,filename,bpin,count,verifier)in enumerate(COHORTS):
        folder=I+directory+'/';sp=folder+'summary.json';bp=folder+filename
        assert h(sp)==pin and h(bp)==bpin
        audit=read(sp);rows=read(bp);rows=rows if isinstance(rows,list)else[rows];assert len(rows)==count and audit['status'].startswith('INDEPENDENT_')and audit['status'].endswith('_PASS')
        paths=[sp,bp]
        for p in paths:
            bindings[p]=h(p)
            obj=read(p)
            for record in(obj if isinstance(obj,list)else[obj]):
                for field in['inputs_sha256','outputs_sha256','evidence_sha256','artifact_hashes']:
                    for ref,sha in record.get(field,{}).items():
                        assert h(ref)==sha,ref;assert ref not in bindings or bindings[ref]==sha;bindings[ref]=sha
        evidence=[];hashes={}
        for j,p in enumerate(paths):
            aid=f'twentyfourth-base-{index}-evidence{j}';assert aid not in{a['id']for a in data['artifacts']};evidence.append(aid);hashes[aid]=h(p)
            data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; independent reports bind raw evidence, source, commands and controls.',unavailable_reason='Twenty-fourth immutable evidence publication not yet confirmed.'))
        for row in rows:
            assert row.get('status',row.get('recommendation')) in ('VERIFIED','REFUTED')and row['verifier']==verifier and row['revision']==1
            assert row['id']not in{c['id']for c in data['claims']}
            shared=row.get('shared_components',row.get('trusted_components',audit.get('shared_components')))
            assert shared
            v=dict(claim_revision=1,verifier=verifier,method='independent_artifact_check',command_or_audit=sp,timestamp=audit['timestamp'],outcome='FAIL' if row['status']=='REFUTED' else 'PASS',scope=row.get('refutation',row['scope']),artifact_hashes=hashes,shared_components=shared,controls=[row.get('method',row.get('checking_method')),'Exact controls and corruption outcomes are preserved in the bound independent report; no solver or proof replay repeated by registrar.'],limitations=row['limitations'])
            claim=dict(id=row['id'],revision=1,statement=row['statement'],kind='mathematical result' if row['kind']=='proposed formula' else row['kind'],basis=row['basis'],status=row['status'],review_state='CLEAR',
                scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row.get('assumptions',['The frozen complete local count classes and135 cells named in this proposed formula.']),
                dependencies=[{k:v for k,v in dep.items()if k in['id','revision','relation']}for dep in row['dependencies']+row.get('verification_dependencies',[])],evidence=list(evidence),verification=[v],limitations=row['limitations'],
                created_at=row['created_at'],updated_at=row['updated_at'],external_source=None,unknowns={'external_source':'Internal independent checking; no external peer review asserted.'},reproducibility=dict(manifest=evidence[0]))
            data['claims'].append(claim);ids.append(claim['id'])
    assert len(ids)==4 and data['claims'][:-4]==old['claims']and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentyfourth_base_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,binding_editorial_adaptations=['Map proposed formula kind to allowed mathematical result without changing statement/status.','Make frozen-class scope explicit as assumption for refuted claim.','Include separately recorded verification_dependencies in dependency list.'],registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=3,new_refuted=1)))
if __name__=='__main__':main()

