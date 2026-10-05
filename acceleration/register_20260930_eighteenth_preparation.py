"""Register the independently approved direct MIP and scoped parity results."""
from datetime import datetime,timezone
from pathlib import Path
import copy,hashlib,json,subprocess,sys
import yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
def h(p):
    with(ROOT/p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==171
    pins={I+'hadamard_prism_binary_mip_claim_binding/summary.json':'91d6d1cbef4d091dba9187b53a7cfdddb2a1d309a079cf3f658aa81546bc89bf',
        I+'hadamard_prism_binary_mip_claim_binding/claim_binding.json':'4ef7bd314b7d3023effca264e64643a3c7b3d1ee24f140444c0056b28a85026e',
        I+'hadamard_prism_binary_mip_calibration/summary.json':'4c27ffee59dbfae792e6776cb5d6175750e31c7f65c9f5e14337d07b3acab6ca',
        I+'hadamard_balanced_parity/summary.json':'8134ed25d5dc06704e6f7f668fa03deec56874eca6d5fad9e6a4138787c7dd76',
        I+'hadamard_balanced_parity_sat_v2/summary.json':'d2536119ac3fa0d45c190a6562de2ccc67c3f9c9765fbfc03257e37b15097f9c',
        I+'hadamard_parity_object_v2_delta/summary.json':'599b7b2f713124e658ce0a7c3b06be0d0a79f170a5fb9fed45531eb5aec914b5',
        I+'hadamard_parity_object_v2_delta/claim_binding.json':'d992d0c8a7c3cfb626a05bf7500e9df9b948b842d218c2761b21739def0de122',
        I+'hadamard_balanced_parity_object_calibration_v2/summary.json':'101b4af16c1356cad1951f04626d3fcc4a244f3afac220ed94b717b9ee1e8dec'}
    for p,sha in pins.items():assert h(p)==sha,p
    mip=read(I+'hadamard_prism_binary_mip_claim_binding/claim_binding.json');assert mip['status_recommendation']=='VERIFIED';mip['recommendation']='VERIFIED'
    parity_audit=read(I+'hadamard_balanced_parity/summary.json');parity=copy.deepcopy(parity_audit['claim'])
    parity['assumptions']=['Coordinatewise balanced triples are an additional construction restriction on the exact fixed support.','All outside-column overlap caps are premises; excluding all-cyclic factors uses the pinned cyclic-exclusion claim.','No target automorphism is assumed.']
    parity['limitations']=parity_audit['limitations']
    witness=read(I+'hadamard_parity_object_v2_delta/claim_binding.json')
    rows=[mip,parity,witness];gates=[I+'hadamard_prism_binary_mip_calibration/summary.json',I+'hadamard_balanced_parity/summary.json',I+'hadamard_balanced_parity_sat_v2/summary.json']
    extra=[[I+'hadamard_prism_binary_mip_claim_binding/summary.json'],[],[I+'hadamard_parity_object_v2_delta/summary.json',I+'hadamard_balanced_parity_object_calibration_v2/summary.json']]
    bindings=dict(pins)
    for gate in set(gates+[p for group in extra for p in group]):
        audit=read(gate);assert audit['status'].endswith('_PASS')
        for p,sha in audit.get('inputs_sha256',{}).items():assert h(p)==sha,p;bindings[p]=sha
    now=datetime.now(timezone.utc).isoformat();new=[]
    for index,(row,gate)in enumerate(zip(rows,gates,strict=True)):
        assert row['recommendation']=='VERIFIED'and row['review_state']=='CLEAR'and row['revision']==1
        assert row['id']not in {c['id']for c in data['claims']};audit=read(gate);evidence=[];hashes={}
        for j,p in enumerate([gate,*extra[index]]):
            aid=f'eighteenth-preparation-{index}-evidence{j}';assert aid not in {a['id']for a in data['artifacts']}
            evidence.append(aid);hashes[aid]=h(p);bindings[p]=h(p)
            data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; independent audit pins all source and raw artifacts.',unavailable_reason='Eighteenth immutable evidence publication is not yet confirmed.'))
        verifier=mip['verification_records'][0]['verifier']if index==0 else parity_audit['verifier']if index==1 else witness['verification']['verifier']
        shared=audit.get('shared_components',parity_audit['shared_components'])
        controls=[mip['verification_records'][0]['controls']]if index==0 else[
            'All 4481 clauses reconstructed, ordered S3 tuple enumeration, complete relation truth tables and eleven corruptions.'if index==1 else
            'All 520 assignment entries and 4481 clauses, raw twenty-pattern/sixty-count reconstruction; six actual-artifact corruptions plus corrected positive calibration and both hexadecimal representations.']
        verification=dict(claim_revision=1,verifier=verifier,method='independent_artifact_check',command_or_audit=gate,timestamp=audit['timestamp'],outcome='PASS',
            scope=row['scope'],artifact_hashes=hashes,shared_components=shared,controls=controls,limitations=row['limitations'])
        data['claims'].append(dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',
            scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row['assumptions'],dependencies=row['dependencies'],evidence=evidence,
            verification=[verification],limitations=row['limitations'],created_at=now,updated_at=now,external_source=None,
            unknowns={'external_source':'Independent internal checks only; no external acceptance or novelty claim.'},reproducibility=dict(manifest=evidence[0])))
        new.append(row['id'])
    data['updated_at']=now;result=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'eighteenth_preparation_registration');out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    record=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        new_claim_ids=new,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=result,
        registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf-8',newline='\n')as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(new_verified=3,claim_population=len(data['claims']),target_resolution='UNKNOWN')))
if __name__=='__main__':main()
