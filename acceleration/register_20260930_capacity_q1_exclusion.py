"""Register the separately verified single-Q1 exclusion without overlap inflation."""
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


def h(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old)
    binding=B+'independent_review/triangle_capacity_q1_rows/claim_binding.json'
    assert h(binding)=='6e28b4fd426355b58eca471e60f5c2bf25f7eb0eeb3331e933fef1d0a220498c'
    r=json.loads((ROOT/binding).read_bytes());assert r['recommendation']=='VERIFIED'
    for p,value in r['inputs_sha256'].items():assert h(p)==value,p
    assert r['claim_id'] not in {c['id'] for c in data['claims']}
    now=datetime.now(timezone.utc).isoformat();evidence=[];hashes={}
    for index,p in enumerate([binding,r['verification']['audit_path'],B+'capacity_q1_rows/manifest.json',B+'capacity_q1_rows/raw99.json']):
        aid='triangle-capacity-q1-row-exclusion-'+str(index)
        assert aid not in {a['id'] for a in data['artifacts']}
        hashes[aid]=h(p);evidence.append(aid)
        data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',
            retrieval='Exact workspace artifact with all row-tree hashes and checking sources in the independent audit.',
            unavailable_reason='Tenth milestone publication has not yet been confirmed.'))
    data['claims'].append(dict(id=r['claim_id'],revision=1,statement=r['statement'],kind=r['kind'],basis=r['basis'],
        status='VERIFIED',review_state='CLEAR',scope=dict(description=r['scope'],unrestricted_target=False,target_resolution='NONE'),
        assumptions=r['assumptions'],dependencies=r['dependencies'],evidence=evidence,
        verification=[dict(claim_revision=1,verifier=r['verification']['verifier'],method='independent_artifact_check',
            command_or_audit=binding,timestamp=r['verification']['timestamp'],outcome='PASS',scope=r['verification']['scope'],
            artifact_hashes=hashes,shared_components=r['shared_components'],
            controls=['Pinned positive fixtures rerun; 50 fresh tree, constraint, raw graph and factor corruptions rejected.'],limitations=r['limitations'])],
        limitations=r['limitations'],created_at=now,updated_at=now,external_source=None,
        unknowns={'external_source':'Internal independent review only; no novelty or external acceptance asserted.'},
        reproducibility=dict(manifest=evidence[0])))
    data['updated_at']=now
    result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old)
    assert result['valid'],result['errors']
    out=ROOT/(B+'capacity_q1_exclusion_registration');out.mkdir(parents=True,exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after)
    (out/'CLAIMS.after.yaml').write_bytes(after)
    report=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=[r['claim_id']],
        checked_input_bindings=r['inputs_sha256'],previous_ledger_sha256=hashlib.sha256(before).hexdigest(),
        ledger_sha256=hashlib.sha256(after).hexdigest(),validation=result,
        registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(new_verified=1,claim_population=len(data['claims']),distinct_fixed_configurations_excluded=1,target_resolution='UNKNOWN')))


if __name__=='__main__':main()
