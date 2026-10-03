"""Register independently reviewed tenth-wave preparations and one partial factor."""
from datetime import datetime, timezone
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys
import yaml
import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'


def digest(p):
    with (ROOT/p).open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();previous=registry.read_ledger(path);data=copy.deepcopy(previous)
    assert (ROOT/(B+'resume/ninth_publication_pointer_receipt.json')).is_file(), 'finish ninth publication first'
    now=datetime.now(timezone.utc).isoformat();added=[];bindings={}
    specs=[
        ('triangle-q1-capacity',B+'independent_review/triangle_q1_capacity_cnf/summary.json',
         '78db3e5afd4a1a3a0cedc451ac3e36f14ccd3615e15babcd060a1bc1f7a81a22',
         [B+'triangle_q1_capacity_cnf/manifest.json',B+'triangle_q1_capacity_cnf/scope.json',B+'triangle_q1_capacity_cnf/instance.cnf',B+'triangle_q1_capacity_cnf/model.json']),
        ('triangle-residual60',B+'independent_review/triangle_residual60/summary.json',
         '16120b7fe6a2645b9de8cb81e4eb4c9a6852bad0c513e4978fb116effdab7a73',
         [B+'triangle_residual60/manifest.json','docs/AUDIT_20260930_TRIANGLE_RESIDUAL60.md']),
        ('triangle-capacity-q1-construction',B+'independent_review/triangle_q1_capacity_sat_binding/summary.json',
         '8f9a8465c7ecdbb0a37b1a37333625682158e548bb00b7f9a6d136af1e4cae65',
         [B+'triangle_q1_capacity_native_pilot/manifest.json',B+'triangle_q1_capacity_native_pilot/summary.json',
          B+'independent_review/triangle_q1_capacity_sat_object/independent_factor.json',
          B+'independent_review/triangle_q1_capacity_sat_object/summary.json']),
    ]
    for label,pin,expected,extras in specs:
        assert digest(pin)==expected
        r=json.loads((ROOT/pin).read_bytes())
        assert r['recommendation']=='VERIFIED' and r['status'].endswith('_PASS')
        assert r['claim_id'] not in {c['id'] for c in data['claims']}
        for name,value in r['inputs_sha256'].items():
            assert digest(name)==value,name
            bindings[name]=value
        evidence=[];hashes={}
        for i,p in enumerate([pin,*extras]):
            aid=label+('-audit' if i==0 else '-evidence'+str(i))
            assert aid not in {a['id'] for a in data['artifacts']}
            hashes[aid]=digest(p);evidence.append(aid)
            data['artifacts'].append(dict(id=aid,path=p,sha256=hashes[aid],availability='LOCAL_ONLY',
                retrieval='Exact workspace path; reproducibility and control records pinned by independent audit.',
                unavailable_reason='No immutable public commit for this new preparation has yet been confirmed.'))
        scope=r['scope'];limits=r['limitations'];revision=r['claim_revision']
        data['claims'].append(dict(id=r['claim_id'],revision=revision,statement=r['statement'],kind=r['kind'],basis=r['basis'],
            status='VERIFIED',review_state='CLEAR',scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
            assumptions=r.get('assumptions') or ['The exact fixed core, canonical C0, Gram equations, margins and capacity inequalities recorded by the independent audit.','No nontrivial target automorphism or universal containment of this core is assumed.'],
            dependencies=r['dependencies'],evidence=evidence,
            verification=[dict(claim_revision=revision,verifier=r['verifier'],method='independent_derivation' if label=='triangle-residual60' else 'independent_artifact_check',
                command_or_audit=pin,timestamp=r['timestamp'],outcome='PASS',scope=scope,artifact_hashes=hashes,
                shared_components=r['shared_components'],controls=['Exact controls and their limitations are recorded in the bound independent audit.'],limitations=limits)],
            limitations=limits,created_at=now,updated_at=now,external_source=None,
            unknowns={'external_source':'Internal independent review only; no external review claimed.'},reproducibility=dict(manifest=evidence[0])))
        added.append(r['claim_id'])
    data['updated_at']=now
    result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',previous)
    assert result['valid'],result['errors']
    out=ROOT/(B+'tenth_preparation_registration');out.mkdir(parents=True,exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after)
    (out/'CLAIMS.after.yaml').write_bytes(after)
    record=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        new_claim_ids=added,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),
        validation=result,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(new_verified_claims=len(added),claim_population=len(data['claims']),target_resolution='UNKNOWN')))


if __name__=='__main__':main()
