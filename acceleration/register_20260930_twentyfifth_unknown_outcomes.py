"""Register two checked UNKNOWN executions; neither is an exclusion."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
COHORTS=[('direct_cell_standalone_unknown_v2', '7a97722db1ede1df9f01004af8e00f6ff3503dcdf16618e893bf5d6a70f0b1fd', 'claim_binding.json', '037059a3a5b556690700b7c488b1855318afab7790b26a4ff6253a42bccc5afe', 1, '/root/structural_attack'), ('direct_cell_count_coupled_unknown_v2', '677cd12aa5096097311538a894ed0cf885007daa13242a21cf9b7be57215bb95', 'claim_binding.json', 'f8f3ab1ff3df6a35563b83047317b982673b44d3211aedaa8504f7958ebf769f', 1, '/root/structural_attack')]

def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==254
    bindings={};ids=[]
    for index,(directory,pin,filename,bpin,count,verifier)in enumerate(COHORTS):
        folder=I+directory+'/';sp=folder+'summary.json';bp=folder+filename
        assert h(sp)==pin and h(bp)==bpin
        audit=read(sp);rows=read(bp);rows=rows if isinstance(rows,list)else[rows];assert len(rows)==count and audit['status'].startswith('INDEPENDENT_')and audit['status'].endswith('_PASS')
        clarification=I+'direct_cell_unknown_availability_clarification.json';assert h(clarification)=='322f0166525f982f33ad1443cb449a3f84e202834f2ec661a15810ee5c2c9a19';paths=[sp,bp,clarification]
        for p in paths:
            bindings[p]=h(p)
            obj=read(p)
            for record in(obj if isinstance(obj,list)else[obj]):
                for field in['inputs_sha256','outputs_sha256','evidence_sha256','artifact_hashes']:
                    for ref,sha in record.get(field,{}).items():
                        assert h(ref)==sha,ref;assert ref not in bindings or bindings[ref]==sha;bindings[ref]=sha
        evidence=[];hashes={}
        for j,p in enumerate(paths):
            aid=f'twentyfifth-unknown-{index}-evidence{j}';assert aid not in{a['id']for a in data['artifacts']};evidence.append(aid);hashes[aid]=h(p)
            data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; independent reports bind raw evidence, source, commands and controls.',unavailable_reason='Twenty-fifth immutable evidence publication not yet confirmed.'))
        for row in rows:
            assert row.get('status',row.get('recommendation')) in ('VERIFIED','REFUTED')and row['verifier']==verifier and row['revision']==1
            assert row['id']not in{c['id']for c in data['claims']}
            for dep in row['dependencies']:assert dep['relation']=='verification_dependency' and h(dep['artifact'])==dep['sha256']
            shared=row.get('shared_components',row.get('trusted_components',audit.get('shared_components',audit.get('source_sharing'))))
            assert shared
            v=dict(claim_revision=1,verifier=verifier,method='independent_artifact_check',command_or_audit=sp,timestamp=audit['timestamp'],outcome='FAIL' if row['status']=='REFUTED' else 'PASS',scope=row.get('refutation',row['scope']),artifact_hashes=hashes,shared_components=shared,controls=[row.get('method',row.get('checking_method')),'Exact controls and corruption outcomes are preserved in the bound independent report; no solver or proof replay repeated by registrar.'],limitations=row['limitations'])
            claim=dict(id=row['id'],revision=1,statement=row['statement'],kind='mathematical result' if row['kind']=='proposed formula' else row['kind'],basis=row['basis'],status=row['status'],review_state='CLEAR',
                scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=['The exact saved native run and guard configuration bound by this report; one attempt only.', 'Independent encoding, semantic and object-calibration gate artifacts named in the original binding are immutable verification premises.', 'Current ext4 originals were missing; the saved host partial traces, historical transfer checks and append-only clarification supply the recorded availability scope.'],
                dependencies=[dict(id=('C-FIXED-HADAMARD-DIRECT-CELL-ALL-CAPS-ENCODING' if index==0 else 'C-FIXED-HADAMARD-DIRECT-CELL-COUNT-COUPLED-ALL-CAPS-ENCODING'),revision=1,relation='verification_dependency')],evidence=list(evidence),verification=[v],limitations=row['limitations'],
                created_at=row.get('created_at',row.get('created')),updated_at=row.get('updated_at',row.get('updated')),external_source=None,unknowns={'external_source':'Internal independent checking; no external peer review asserted.'},reproducibility=dict(manifest=evidence[0]))
            data['claims'].append(claim);ids.append(claim['id'])
    assert len(ids)==2 and data['claims'][:-2]==old['claims']and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentyfifth_unknown_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(registrar_sha256=h(Path(__file__).relative_to(ROOT)),timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,binding_editorial_adaptations=['Map the original encoding/semantic artifact dependencies to the applicable now-registered exact encoding claim revision; preserve original artifact bindings as evidence.', 'Keep object calibration as an explicitly pinned checking assumption, not an invented claim ID.', 'Bind the append-only host/ext4 availability wording clarification; execution statement and UNKNOWN conclusion unchanged.'],registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=2,new_refuted=0)))
if __name__=='__main__':main()

