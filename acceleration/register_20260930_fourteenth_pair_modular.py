"""Register the independently bound pair normalization and finite modular route."""
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
BINDING=B+'independent_review/pair_and_modular_claim_bindings/summary.json'
PIN='650f2fadf94aa9d8bd3cbf16baaa2c6773932e2a21ee17ed9b04d7079e35f270'
def h(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old)
    assert h(BINDING)==PIN;report=json.loads((ROOT/BINDING).read_bytes());assert len(report['claims'])==2
    for p,sha in report['inputs_sha256'].items():assert h(p)==sha,p
    now=datetime.now(timezone.utc).isoformat();added=[]
    for index,c in enumerate(report['claims']):
        assert c['recommended_status']=='VERIFIED' and c['recommended_review_state']=='CLEAR'
        assert c['id'] not in {x['id'] for x in data['claims']}
        label=['ordered-matching-pair-normalization','modular-kernel-finite-route'][index]
        extras=[B+'variable_core_pair_orbits/instance.cnf',B+'variable_core_pair_orbits/coverage.json'] if index==0 else [B+'independent_review/triangle_modular_kernel_finite/reconstructed_perturbations.json']
        evidence=[];hashes={}
        assert h(c['evidence_report'])==c['evidence_sha256']
        for i,p in enumerate([c['evidence_report'],BINDING,*extras]):
            aid=label+'-evidence'+str(i);assert aid not in {x['id'] for x in data['artifacts']}
            hashes[aid]=h(p);evidence.append(aid)
            data['artifacts'].append(dict(id=aid,path=p,sha256=hashes[aid],availability='LOCAL_ONLY',retrieval='Exact workspace path and pinned audit; public immutable publication pending.',unavailable_reason='This new cohort has not yet been confirmed in public evidence.'))
        claim={k:copy.deepcopy(c[k]) for k in ['id','revision','statement','kind','basis','assumptions','dependencies','limitations']}
        claim.update(status='VERIFIED',review_state='CLEAR',scope=dict(description=c['scope'],unrestricted_target=index==0,target_resolution='NONE'),evidence=evidence,
            verification=[dict(claim_revision=c['revision'],verifier=c['verifier'],method='independent_artifact_check',command_or_audit=c['evidence_report'],timestamp=c['verification_timestamp'],
                outcome='PASS',scope=c['scope'],artifact_hashes=hashes,shared_components=[c['trusted_components']],
                controls=['Exact complete finite populations, raw-byte checks, reconstruction limits and positive/corrupted controls are recorded in the pinned independent audit.'],limitations=c['limitations'])],
            created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Internal independent review only; no external acceptance or novelty claimed.'},reproducibility=dict(manifest=evidence[0]))
        data['claims'].append(claim);added.append(c['id'])
    data['updated_at']=now;result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'fourteenth_pair_modular_registration');out.mkdir(parents=True,exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before);after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before
    path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    record=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=added,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),checked_input_bindings={BINDING:PIN,**report['inputs_sha256']},
        validation=result,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with (out/'summary.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(dict(new_verified=2,claim_population=len(data['claims']),target_resolution='UNKNOWN')))

if __name__=='__main__':main()
