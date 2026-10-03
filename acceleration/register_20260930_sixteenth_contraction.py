"""Register separately reviewed contraction identities and row-capacity redundancy."""
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
    assert len(data['claims'])==154
    pins={I+'triangle_contraction/summary.json':'5b190d159e2fc2b681dc52be1083d2f74f402c86f1305b7acdaf58435fcdc96a',
        I+'triangle_contraction/claim_binding.json':'5095a7f66d3f706252f70161c03f997cbf07bc72d32dca8ce36aa5f36fcb6047',
        I+'triangle_capacity_floor/summary.json':'6df422517939dfd7ce2691148d75e67c6fe966b0879924ad860988fd3d58d9ad'}
    for p,v in list(pins.items()):
        assert h(p)==v,p
        for q,w in read(p).get('inputs_sha256',{}).items():
            assert h(q)==w,q
            assert q not in pins or pins[q]==w
            pins[q]=w
    floor=read(I+'triangle_capacity_floor/summary.json');floor['id']=floor['claim_id'];floor['revision']=floor['claim_revision']
    rows=[('triangle-contraction',read(I+'triangle_contraction/claim_binding.json'),I+'triangle_contraction/summary.json',
            [I+'triangle_contraction/claim_binding.json',B+'triangle_contraction/summary.json']),
        ('triangle-capacity-floor',floor,I+'triangle_capacity_floor/summary.json',[I+'triangle_contraction/capacity_floor_candidate.json'])]
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
            verification=[dict(claim_revision=1,verifier=row['verifier'],method='independent_derivation',command_or_audit=auditpath,
                timestamp=row['updated_at'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=audit['shared_components'],
                controls=['Universal written derivation plus the exact nonempty or margin-positive controls and rejected corruptions listed in the audit.'],
                limitations=row['limitations'])],limitations=row['limitations'],created_at=now,updated_at=now,external_source=None,
            unknowns={'external_source':'Independent internal verification only; no novelty, external review or target resolution asserted.'},
            reproducibility=dict(manifest=evidence[0])))
        ids.append(row['id'])
    data['updated_at']=now;result=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old)
    assert result['valid'],result['errors']
    out=ROOT/(B+'sixteenth_contraction_registration');out.mkdir(parents=True,exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before);after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    receipt=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=pins,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=result,
        registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(new_verified=2,claim_population=len(data['claims']),target_resolution='UNKNOWN')))


if __name__=='__main__':main()
