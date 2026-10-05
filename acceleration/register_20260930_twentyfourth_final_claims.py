"""Register seven independently checked proof, union and auxiliary results."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
COHORTS=[('hadamard_twohundredfifteen_profile_proofs', '14d5064f7d09f491899f25113844df53b0b49658abc549ed784ed0b92ad55210', 'claim_binding.json', 'd001bb58caf5c62d6a0eab63a69368407a03b04626b3d7ec48a7f5ff437bfcf7', 1, '/root/state_literature_audit'), ('hadamard_seven_profile_union', 'fe1108f78c2b925ee6a79a55cff53ee9abe6d292965fd2550a1e6a9d34881df4', 'claim_bindings.json', '80424dd0fa7ffb9f4fe3889fbf51a13585cfc0e1f86a46ebb15aeee550499e75', 2, '/root/eight_domain_audit'), ('count_master_eight_orbit_cuts', '4c919b9b48d4c9d6bf085480f9ae166172f33b457e85713c50c109c29bc57493', 'claim_bindings.json', 'c22d1b40f45bbec1739ba8221a4fa2ce30f149a3c876b708a4ea0c44ead1fe25', 2, '/root'), ('hadamard_gram_affine_gf2', 'd581cc37dc751f6aa96be2b016ac33084d466d7497982002506bf7091178dcfa', 'claim_binding.json', 'a4b7482673e61d74c2422540106caa0257029f2dbf828a67e92086d81a4461af', 1, '/root/structural_attack'), ('hadamard_twohundredfifteen_proof_transport', '4a893e6636a102e6ab0ba32e69674bae96288e320e24d0242cd974017db645f6', 'claim_binding.json', 'be5b0f9af8b623095f9dd1b4e68f9d208ced918e2e820ebea3882f12999ed695', 1, '/root')]

def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==241
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
            aid=f'twentyfourth-final-{index}-evidence{j}';assert aid not in{a['id']for a in data['artifacts']};evidence.append(aid);hashes[aid]=h(p)
            data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; independent reports bind raw evidence, source, commands and controls.',unavailable_reason='Twenty-fourth immutable evidence publication not yet confirmed.'))
        for row in rows:
            assert row.get('status',row.get('recommendation')) in ('VERIFIED','REFUTED')and row['verifier']==verifier and row['revision']==1
            assert row['id']not in{c['id']for c in data['claims']}
            shared=row.get('shared_components',row.get('trusted_components',audit.get('shared_components',audit.get('source_sharing'))))
            assert shared
            v=dict(claim_revision=1,verifier=verifier,method='independent_artifact_check',command_or_audit=sp,timestamp=audit['timestamp'],outcome='FAIL' if row['status']=='REFUTED' else 'PASS',scope=row.get('refutation',row['scope']),artifact_hashes=hashes,shared_components=shared,controls=[row.get('method',row.get('checking_method')),'Exact controls and corruption outcomes are preserved in the bound independent report; no solver or proof replay repeated by registrar.'],limitations=row['limitations'])
            claim=dict(id=row['id'],revision=1,statement=row['statement'],kind='mathematical result' if row['kind']=='proposed formula' else row['kind'],basis=row['basis'],status=row['status'],review_state='CLEAR',
                scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row.get('assumptions',['The precise domains and fixed-support matrices named in the statement and bound independent report.']),
                dependencies=[dict(id=dep.get('id',dep.get('claim_id')),revision=dep['revision'],relation=dep['relation'])for dep in row['dependencies']+row.get('verification_dependencies',[])],evidence=list(evidence),verification=[v],limitations=row['limitations'],
                created_at=row.get('created_at',row.get('created')),updated_at=row.get('updated_at',row.get('updated')),external_source=None,unknowns={'external_source':'Internal independent checking; no external peer review asserted.'},reproducibility=dict(manifest=evidence[0]))
            data['claims'].append(claim);ids.append(claim['id'])
    assert len(ids)==7 and data['claims'][:-7]==old['claims']and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentyfourth_final_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,binding_editorial_adaptations=['Map claim_id dependency key to ledger id without changing referenced claim.','Copy existing created/updated timestamps into ledger created_at/updated_at.','Make explicit the pinned fixed-support/literal-profile/within-triplicate-cap premises already present in the exact statement.'],registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=7,new_refuted=0)))
if __name__=='__main__':main()

