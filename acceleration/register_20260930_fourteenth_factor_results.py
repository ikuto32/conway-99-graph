"""Bind the independently reviewed column-cap encoding and cooling saved states."""
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
def h(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old)
    specs=[('six-prism-complete-column-caps',I+'prism_column_caps/summary.json','5c137eb4b497433d02d99e7b1105c34e06f679b55cd5cbe722b8f265d3f47edf',
            [B+'prism_column_caps_v3/summary.json',B+'prism_column_caps_v3/instance.cnf',B+'prism_column_caps_v3/model.json','docs/AUDIT_20260930_PRISM_COLUMN_CAPS.md']),
           ('factor-permutation-cooling-states',I+'factor_annealer_cooling_v3/claim_binding.json','7422acba6fcf67db021a84ebd0753cc2824fa9fbc77e362df0a55fbd975fb02b',
            [I+'factor_annealer_cooling_v3/summary.json',B+'factor_annealer_cooling_v3/summary.json'])]
    now=datetime.now(timezone.utc).isoformat();added=[];bindings={}
    for label,pin,expected,extras in specs:
        assert h(pin)==expected;r=json.loads((ROOT/pin).read_bytes());assert r['recommendation']=='VERIFIED' and r['review_state']=='CLEAR'
        audit=r if 'inputs_sha256' in r else json.loads((ROOT/extras[0]).read_bytes())
        for p,sha in audit['inputs_sha256'].items():assert h(p)==sha,p;bindings[p]=sha
        bindings[pin]=expected
        evidence=[];hashes={}
        for i,p in enumerate([pin,*extras]):
            aid=label+'-evidence'+str(i);assert aid not in {x['id'] for x in data['artifacts']};hashes[aid]=h(p);evidence.append(aid)
            data['artifacts'].append(dict(id=aid,path=p,sha256=hashes[aid],availability='LOCAL_ONLY',retrieval='Exact workspace path and pinned independent audit; oversized inputs have saved gzip recovery.',unavailable_reason='New cohort is not yet confirmed in immutable public evidence.'))
        cid=r['claim_id'];assert cid not in {x['id'] for x in data['claims']}
        v=r['verification'][0] if 'verification' in r else None
        scope=r['scope'];limitations=r['limitations']
        data['claims'].append(dict(id=cid,revision=r['claim_revision'],statement=r['statement'],kind=r['kind'],basis=r['basis'],status='VERIFIED',review_state='CLEAR',
            scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
            assumptions=r.get('assumptions',['The exact fixed six-prism core and pinned base/normalization premises; no target automorphism or universal core-containment assumption.']),
            dependencies=r['dependencies'],evidence=evidence,
            verification=[dict(claim_revision=r['claim_revision'],verifier=v['verifier'] if v else r['verifier'],method='independent_artifact_check',
                command_or_audit=v['command_or_audit'] if v else pin,timestamp=v['timestamp'] if v else r['timestamp'],outcome='PASS',scope=scope,artifact_hashes=hashes,
                shared_components=v['shared_components'] if v else r['shared_components'],
                controls=['Complete encoded finite domains or all declared saved-state populations, independent integer checks and calibrated corrupted controls are specified by the pinned report.'],limitations=limitations)],
            limitations=limitations,created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Internal independent review only; no external acceptance or novelty claimed.'},reproducibility=dict(manifest=evidence[0])))
        added.append(cid)
    data['updated_at']=now;result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'fourteenth_factor_results_registration');out.mkdir(parents=True,exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    receipt=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=added,
        checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=result,
        registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with (out/'summary.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(dict(new_verified=2,claim_population=len(data['claims']),target_resolution='UNKNOWN')))

if __name__=='__main__':main()
