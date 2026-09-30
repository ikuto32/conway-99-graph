"""Register independently reviewed sizeclass16 encodings and complete792 kernel redundancy."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
COHORTS=[('exact_eight_sizeclass16_cnfs_v2','b5e5a90ecc9a52996200e3e8cc4988fd04a85122be22b7355de73678ddcb2b0a','claim_binding.json','8285bd8da4b8ec10d786ca5b85f2b6616bf307a801d34124f61dd2c030c6778a',1,'/root/structural_attack'),('exact_eight_kernel_redundancy','6e12ed8b6147d2db20691fe93ec9f45be3f08ef68d541c617e1ffcae505a2a55','claim_binding.json','1ce8659935147855c369ed0637c7b0437a46a46bda6268431048f77bd0d65092',1,'/root/state_literature_audit')]

def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==289 and hashlib.sha256(before).hexdigest()=='2513562d899050d3c2ed0f12e14c275ff8d2b2dbaa667ec5800408296be72dc1';now=datetime.now(timezone.utc).isoformat()
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
            aid=f'twentyeighth-kernel-sizeclass-{index}-evidence{j}';assert aid not in{a['id']for a in data['artifacts']};evidence.append(aid);hashes[aid]=h(p)
            data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; independent reports bind raw evidence, source, commands and controls.',unavailable_reason='Twenty-eighth immutable evidence publication not yet confirmed.'))
        for row in rows:
            assert row.get('status',row.get('recommendation')) in ('VERIFIED','REFUTED')and row['verifier']==verifier and row['revision']==1
            assert row['id']not in{c['id']for c in data['claims']}
            shared=row.get('shared_components',row.get('trusted_components',audit.get('shared_components',audit.get('source_sharing'))))
            assert shared
            v=dict(claim_revision=1,verifier=verifier,method='independent_artifact_check',command_or_audit=sp,timestamp=audit.get('timestamp',audit.get('created_at')),outcome='FAIL' if row['status']=='REFUTED' else 'PASS',scope=row.get('refutation',row['scope']),artifact_hashes=hashes,shared_components=shared,controls=[row.get('method',row.get('checking_method')),'Exact controls and corruption outcomes are preserved in the bound independent report; no solver or proof replay repeated by registrar.'],limitations=row.get('limitations',[row['scope']]))
            claim=dict(id=row['id'],revision=1,statement=row['statement'],kind='mathematical result' if row['kind']=='finite_check' else row['kind'],basis=row['basis'],status=row['status'],review_state='CLEAR',
                scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row.get('assumptions',['The pinned fixed support, exact literal count profiles and within-triplicate column caps specified in the statement.']),
                dependencies=[dict(id=dep.get('id',dep.get('claim_id')),revision=dep['revision'],relation=dep['relation'])for dep in row['dependencies']+row.get('verification_dependencies',[])],evidence=list(evidence),verification=[v],limitations=row.get('limitations',[row['scope']]),
                created_at=row.get('created_at',row.get('created')),updated_at=row.get('updated_at',row.get('updated')),external_source=None,unknowns={'external_source':'Internal independent checking; no external peer review asserted.'},reproducibility=dict(manifest=evidence[0]))
            data['claims'].append(claim);ids.append(claim['id'])
    assert len(ids)==2 and data['claims'][:-2]==old['claims']and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentyeighth_kernel_sizeclass_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(registrar_sha256=h(Path(__file__).relative_to(ROOT)),timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,binding_editorial_adaptations=['Use summary created_at as actual verification timestamp. Copy exact statements, assumptions, scopes and dependencies; copy scope verbatim as limitations when no redundant limitations list exists. No mathematical change.'],registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=2,new_refuted=0)))
if __name__=='__main__':main()

