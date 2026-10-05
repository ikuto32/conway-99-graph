"""Register exact 25-row results and two independently checked design exclusions."""
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
    specs=[
        ('triangle-one-c2-encoding',I+'triangle_one_c2_row_cnf/summary.json',
         '661062b1fbdf0d9e076082867b44353509fb892d9946dc142d1c70b91f59558d',False,
         [B+'triangle_one_c2_row_cnf/manifest.json',B+'triangle_one_c2_row_cnf/scope.json',B+'triangle_one_c2_row_cnf/instance.cnf',B+'triangle_one_c2_row_cnf/model.json']),
        ('triangle-one-c2-construction',I+'triangle_one_c2_row_sat_binding/summary.json',
         'ee7af7ec95d70c19068e2d3b3fb756e28db3ba97c7a8c16c0f79c09516a3950e',False,
         [B+'triangle_one_c2_row_native_pilot/manifest.json',B+'triangle_one_c2_row_native_pilot/summary.json',
          I+'triangle_one_c2_row_sat_object/summary.json',I+'triangle_one_c2_row_sat_object/independent_factor.json']),
        ('six-prism-complement-design',I+'prism_complement_design/summary.json',
         '7fe88ffdfb13708f48a730f326d632362331e7c2434ff6e67e21159e53a9c978',True,
         [B+'prism_factor_design_pilot/manifest.json',B+'prism_factor_design_pilot/instance.cnf',
          B+'prism_factor_design_pilot/proof.drat',I+'prism_complement_design/complete_main_proof.receipt.json',
          'docs/AUDIT_20260930_PRISM_COMPLEMENT_DESIGN.md']),
    ]
    now=datetime.now(timezone.utc).isoformat();added=[];bindings={}
    for label,pin,expected,multiple,extras in specs:
        assert h(pin)==expected,pin
        report=json.loads((ROOT/pin).read_bytes())
        assert report['status'].startswith('INDEPENDENT_') and report['status'].endswith('_PASS')
        for p,value in report['inputs_sha256'].items():assert h(p)==value,p;bindings[p]=value
        evidence=[];hashes={}
        for index,p in enumerate([pin,*extras]):
            aid=label+('-audit' if index==0 else '-evidence'+str(index))
            assert aid not in {a['id'] for a in data['artifacts']}
            hashes[aid]=h(p);evidence.append(aid)
            data['artifacts'].append(dict(id=aid,path=p,sha256=hashes[aid],availability='LOCAL_ONLY',
                retrieval='Exact workspace path, with source, commands and complete checking artifacts pinned by the independent report.',
                unavailable_reason='This new milestone has not yet been confirmed in an immutable public commit.'))
        for record in report['claims'] if multiple else [report]:
            r={**report,**record}
            assert r['recommendation']=='VERIFIED'
            cid=r['claim_id'];revision=r['claim_revision'];assert cid not in {c['id'] for c in data['claims']}
            method='independent_derivation' if cid=='C-SIX-PRISM-GLOBAL-COMPLEMENT-PAIRING-EXCLUSION' else 'independent_artifact_check'
            data['claims'].append(dict(id=cid,revision=revision,statement=r['statement'],kind=r['kind'],basis=r['basis'],
                status='VERIFIED',review_state='CLEAR',scope=dict(description=r['scope'],unrestricted_target=False,target_resolution='NONE'),
                assumptions=r.get('assumptions') or ['Only the exact fixed core, incidence conditions and construction restrictions explicitly stated in the pinned audit.','No nontrivial target automorphism or universal core-containment premise is assumed.'],
                dependencies=r['dependencies'],evidence=evidence,
                verification=[dict(claim_revision=revision,verifier=r['verifier'],method=method,command_or_audit=pin,
                    timestamp=r['timestamp'],outcome='PASS',scope=r['scope'],artifact_hashes=hashes,
                    shared_components=r['shared_components'],controls=['The pinned independent report preserves exact raw checks, positive and corrupted controls, and distinguishes universal derivation from finite calibration.'],limitations=r['limitations'])],
                limitations=r['limitations'],created_at=now,updated_at=now,external_source=None,
                unknowns={'external_source':'Internal independent verification only; no novelty or external acceptance asserted.'},
                reproducibility=dict(manifest=evidence[0])))
            added.append(cid)
    assert len(added)==4
    data['updated_at']=now
    result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old)
    assert result['valid'],result['errors']
    out=ROOT/(B+'eleventh_preparation_registration');out.mkdir(parents=True,exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before);after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    receipt=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=added,checked_input_bindings=bindings,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=result,
        registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(new_verified=4,claim_population=len(data['claims']),target_resolution='UNKNOWN')))


if __name__=='__main__':main()
