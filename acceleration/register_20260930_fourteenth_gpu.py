"""Register four exact independently approved GPU engineering records only."""
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
BINDING=B+'independent_review/factor_gpu_claim_bindings/summary.json'
PIN='6bf6e04ee313bb577acf5f48edccc8c9afd310493017ebc6de8efcd8643755dd'

def h(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old)
    assert h(BINDING)==PIN
    report=json.loads((ROOT/BINDING).read_bytes());assert len(report['records'])==4
    bindings={BINDING:PIN}
    for p,sha in report['inputs_sha256'].items():assert h(p)==sha,p;bindings[p]=sha
    labels=['factor-permutation-calibration','factor-permutation-pilot-states','factor-public-json-resume','factor-v2-resume-failure']
    added=[];now=datetime.now(timezone.utc).isoformat()
    for label,c in zip(labels,report['records'],strict=True):
        assert c['recommendation']=='VERIFIED' and c['review_state']=='CLEAR'
        assert c['id'] not in {x['id'] for x in data['claims']}
        evidence=[];path_ids={};hashes={}
        for index,item in enumerate([*c['evidence'],dict(path=BINDING,sha256=PIN,retrieval='Pinned independent exact claim-binding record.')]):
            p=item['path'];assert h(p)==item['sha256'];aid=label+'-evidence'+str(index)
            assert aid not in {x['id'] for x in data['artifacts']}
            data['artifacts'].append(dict(id=aid,path=p,sha256=item['sha256'],availability='LOCAL_ONLY',retrieval=item['retrieval'],
                unavailable_reason='New cohort is not yet confirmed in immutable public evidence; the original pilot PUBLIC metadata was explicitly corrected.'))
            evidence.append(aid);path_ids[p]=aid;hashes[aid]=item['sha256']
        verification=[]
        for source in c['verification']:
            v={k:copy.deepcopy(source[k]) for k in ['claim_revision','verifier','method','command_or_audit','timestamp','outcome','scope','shared_components']}
            v['artifact_hashes']={path_ids[p]:sha for p,sha in source['artifact_hashes'].items()}
            v['artifact_hashes'][path_ids[BINDING]]=PIN
            v['controls']=[json.dumps(c['controls'],sort_keys=True)]
            v['limitations']=c['limitations'];verification.append(v)
        claim={k:copy.deepcopy(c[k]) for k in ['id','revision','statement','kind','basis','assumptions','dependencies','limitations']}
        claim.update(status='VERIFIED',review_state='CLEAR',scope=dict(description=c['scope']['description'],unrestricted_target=False,target_resolution='NONE'),
            evidence=evidence,verification=verification,created_at=now,updated_at=now,external_source=None,
            unknowns={'external_source':'Internal artifact review only; no external acceptance or novelty claimed.'},reproducibility=dict(manifest=evidence[-1]))
        data['claims'].append(claim);added.append(c['id'])
    data['updated_at']=now
    result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old)
    assert result['valid'],result['errors']
    out=ROOT/(B+'fourteenth_gpu_registration');out.mkdir(parents=True,exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before);after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    receipt=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        new_claim_ids=added,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),
        validation=result,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN',
        mappings='Exact approved record statements/dependencies retained; evidence paths mapped to stable artifact IDs. Scope has no unrestricted-target applicability. All new artifacts remain LOCAL_ONLY.')
    with (out/'summary.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(dict(new_verified=len(added),claim_population=len(data['claims']),target_resolution='UNKNOWN')))

if __name__=='__main__':main()
