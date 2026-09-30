"""Register separately checked broader encoding and two exact projection claims."""
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
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==168
    encoding=I+'hadamard_prism_ordered_cnf/summary.json';projection=I+'hadamard_triplicate_counts_v2/summary.json'
    pins={encoding:'377e985056a4f6daae704d342c63d4a06d7086ee43b3b5e9636d9a1135d18132',projection:'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88'}
    for p,sha in pins.items():assert h(p)==sha
    rows=[read(I+'hadamard_prism_ordered_cnf/claim_binding.json'),*read(projection)['claims']];gates=[encoding,projection,projection]
    for gate in set(gates):
        audit=read(gate);assert audit['status'].endswith('_PASS')
        for p,sha in audit['inputs_sha256'].items():assert h(p)==sha,p;pins[p]=sha
    now=datetime.now(timezone.utc).isoformat();new=[]
    for index,(row,gate) in enumerate(zip(rows,gates,strict=True)):
        assert row['recommendation']=='VERIFIED'and row['review_state']=='CLEAR'and row['revision']==1
        assert row['id']not in {c['id']for c in data['claims']}
        aid=f'seventeenth-model-projection-evidence{index}';assert aid not in {a['id']for a in data['artifacts']}
        data['artifacts'].append(dict(id=aid,path=gate,sha256=h(gate),availability='LOCAL_ONLY',retrieval='Exact repository-relative path; independent review binds raw artifacts and source versions.',unavailable_reason='Seventeenth-cohort immutable publication not yet confirmed.'))
        audit=read(gate)
        controls=['Complete clause reconstruction and threshold truth controls.'if index==0 else 'Independent exact integer elimination, all117480local triples,120separate local witnesses, and nine corrupted controls.']
        verification=dict(claim_revision=1,verifier=row['verifier'],method='independent_derivation'if index==1 else'independent_artifact_check',
            command_or_audit=gate,timestamp=audit['timestamp'],outcome='PASS',scope=row['scope'],artifact_hashes={aid:h(gate)},
            shared_components=audit['shared_components'],controls=controls,limitations=row['limitations'])
        data['claims'].append(dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',
            scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row['assumptions'],dependencies=row['dependencies'],evidence=[aid],verification=[verification],
            limitations=row['limitations'],created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Internal independent checks only; no external acceptance or novelty claim.'},reproducibility=dict(manifest=aid)))
        new.append(row['id'])
    data['updated_at']=now;result=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'seventeenth_model_projection_registration');out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    record=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=new,
        checked_input_bindings=pins,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=result,
        registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf-8',newline='\n')as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(new_verified=3,claim_population=len(data['claims']),target_resolution='UNKNOWN')))
if __name__=='__main__':main()
