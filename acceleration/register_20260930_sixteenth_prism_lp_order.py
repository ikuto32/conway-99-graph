"""Register exact fractional feasibility and integral column-order normalization separately."""
from datetime import datetime, timezone
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys
import yaml
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
I=B+'independent_review/'


def h(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads((ROOT/path).read_bytes())


def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old)
    assert len(data['claims'])==163
    pins={I+'hadamard_six_prism_uniform_lp/summary.json':'6f6e5d601205f1789a3ed1f3128d3305043fc9e7504d63949427df6383cade26',
        I+'hadamard_six_prism_column_order/summary.json':'0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2'}
    for p,v in list(pins.items()):
        assert h(p)==v,p
        for q,w in read(p).get('inputs_sha256',{}).items():
            assert h(q)==w,q
            assert q not in pins or pins[q]==w
            pins[q]=w
    rows=[]
    for name in ['hadamard_six_prism_uniform_lp','hadamard_six_prism_column_order']:
        p=I+name+'/summary.json';rows.append((name,read(p)['claim'],p,[]))
    now=datetime.now(timezone.utc).isoformat();ids=[]
    for label,row,auditpath,extra in rows:
        audit=read(auditpath);assert audit['status'].endswith('_PASS')
        assert row['recommendation']=='VERIFIED' and row['revision']==1 and row['review_state']=='CLEAR'
        evidence=[];hashes={}
        for i,p in enumerate([auditpath,*extra]):
            aid='sixteenth-'+label+'-evidence-'+str(i)
            assert aid not in {a['id'] for a in data['artifacts']}
            value=h(p);pins[p]=value;evidence.append(aid);hashes[aid]=value
            data['artifacts'].append(dict(id=aid,path=p,sha256=value,availability='LOCAL_ONLY',
                retrieval='Exact workspace path; independently reviewed proof and raw control records are pinned in the audit.',
                unavailable_reason='Sixteenth-cohort immutable publication has not been confirmed.'))
        assert row['id'] not in {c['id'] for c in data['claims']}
        data['claims'].append(dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],
            status='VERIFIED',review_state='CLEAR',scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),
            assumptions=row['assumptions'],dependencies=row['dependencies'],evidence=evidence,
            verification=[dict(claim_revision=1,verifier=row['verifier'],method='independent_derivation' if row['kind']=='mathematical result' else 'independent_artifact_check',command_or_audit=auditpath,
                timestamp=row['updated_at'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=audit['shared_components'],
                controls=['Independent raw matrix/rational or integral relabelling proof, complete finite controls and rejected corruptions listed in the audit.'],
                limitations=row['limitations'])],limitations=row['limitations'],created_at=now,updated_at=now,external_source=None,
            unknowns={'external_source':'Independent internal verification only; no novelty, external review or target resolution asserted.'},
            reproducibility=dict(manifest=evidence[0])))
        ids.append(row['id'])
    data['updated_at']=now;result=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old)
    assert result['valid'],result['errors']
    out=ROOT/(B+'sixteenth_prism_lp_order_registration');out.mkdir(parents=True,exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before);after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    receipt=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=pins,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=result,
        registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(new_verified=2,claim_population=len(data['claims']),target_resolution='UNKNOWN')))


if __name__=='__main__':main()
