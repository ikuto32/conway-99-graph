"""Register independent seven-profile screen and complete coordinate marginal domains."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
COHORTS=[('hadamard_seven_profile_arc','eeb0a947e6dde99c65578c6de323951f6c6654fdafeb31b22d053e117e84467d','claim_binding.json','29e3003a0251a5f9ae7c9f095c41f1e2a90e102b066675a40f65a78817a1f7c0',1,'/root'),('coordinate_marginal_domains','9d08476ace166438321273b13161d759dbc858c782b16d8a2f0e9801d424cf39','claim_binding.json','b3f9e4e0b5541e900d3a26c04c1be77f40ea543a8658e6f6ef6f942323bc0b81',1,'/root')]
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==223
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
            aid=f'twentythird-seven-and-coordinates-{index}-evidence{j}';assert aid not in{a['id']for a in data['artifacts']};evidence.append(aid);hashes[aid]=h(p)
            data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; independent reports bind raw evidence, source, commands and controls.',unavailable_reason='Twenty-third immutable evidence publication not yet confirmed.'))
        for row in rows:
            assert row.get('status',row.get('recommendation'))=='VERIFIED'and row['verifier']==verifier and row['revision']==1
            assert row['id']not in{c['id']for c in data['claims']}
            shared=row.get('shared_components',row.get('trusted_components',audit.get('shared_components')))
            assert shared
            v=dict(claim_revision=1,verifier=verifier,method='independent_artifact_check',command_or_audit=sp,timestamp=audit['timestamp'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=shared,controls=[row.get('method',row.get('checking_method')),'Exact controls and corruption outcomes are preserved in the bound independent report; no solver or proof replay repeated by registrar.'],limitations=row['limitations'])
            claim=dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',
                scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row['assumptions'],
                dependencies=[{k:v for k,v in dep.items()if k in['id','revision','relation']}for dep in row['dependencies']],evidence=list(evidence),verification=[v],limitations=row['limitations'],
                created_at=row['created_at'],updated_at=row['updated_at'],external_source=None,unknowns={'external_source':'Internal independent checking; no external peer review asserted.'},reproducibility=dict(manifest=evidence[0]))
            data['claims'].append(claim);ids.append(claim['id'])
    assert len(ids)==2 and data['claims'][:-2]==old['claims']and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentythird_seven_and_coordinates_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=2)))
if __name__=='__main__':main()

