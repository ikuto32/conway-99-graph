"""Register exact independently reviewed core counts and local obstructions."""
from datetime import datetime,timezone
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import yaml
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
A=B+'independent_review/'
def digest(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())

def main():
    ledger=ROOT/'CLAIMS.yaml';before=ledger.read_bytes();previous=registry.read_ledger(ledger);data=copy.deepcopy(previous)
    specs=[
        ('triangle-matching-pairs',A+'triangle_matching_pair_census/summary.json','085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79',
         [B+'triangle_matching_pair_census_v2/manifest.json',B+'triangle_matching_pair_census_v2/summary.json']),
        ('triangle-paircap-reduction',A+'triangle_core_paircap_theorem/summary.json','5fa165b4d17673be87097804f0ca64d10f8ed3d4ea199841007e4c7df118cc4f',[]),
        ('triangle-labelled-p-counts',A+'triangle_core_permutation_census_v2/summary.json','ce3e6379a5e5b49f5a98b2416e4964dc81fdf083652972f2050a2f306b8ce9b7',
         [B+'triangle_core_permutation/manifest.json',B+'triangle_core_permutation/cases.jsonl']),
        ('triangle-row29-obstruction',A+'triangle_wave154_row29_obstruction/summary.json','43b81ed2aef9cde8b600cb6981455cdec69a84bb1961aa08ecb68a1248ba5fb9',
         [B+'triangle_wave154_row29_obstruction/manifest.json',B+'triangle_wave154_row29_obstruction/proof_tree.json']),
        ('triangle39-gram-sos',A+'triangle39_gram_sos/summary.json','e52b7d4826ab5d7d9d6078006d47d722123cbf6ccaa7386bd933975c06ae8359',
         [B+'triangle39_gram_sos/manifest.json',B+'triangle39_gram_sos/archive_overlap.json']),
    ]
    now=datetime.now(timezone.utc).isoformat();added=[];bound_inputs={}
    for label,path,expected,extras in specs:
        assert digest(path)==expected,path
        report=read(path)
        assert report['status'].startswith('INDEPENDENT_')and report['status'].endswith('_PASS'),path
        assert report.get('recommendation')=='VERIFIED',path
        assert report['claim_id']not in{c['id']for c in data['claims']},report['claim_id']
        for name,value in report['inputs_sha256'].items():
            assert digest(name)==value,name
            bound_inputs[name]=value
        evidence=[];hashes={}
        for index,name in enumerate([path,*extras]):
            aid=label+('-audit'if index==0 else '-evidence'+str(index))
            assert aid not in{a['id']for a in data['artifacts']}
            value=digest(name);evidence.append(aid);hashes[aid]=value
            data['artifacts'].append(dict(id=aid,path=name,sha256=value,availability='LOCAL_ONLY',
                retrieval='Exact workspace-relative completed report or raw artifact; source, commands and companion controls are pinned by the independent audit.',
                unavailable_reason='This new milestone has not yet been confirmed in a public immutable commit.'))
        scope=report['scope'];limits=report['limitations'];revision=report['claim_revision']
        shared=report.get('shared_components',[])
        if not isinstance(shared,list):shared=[json.dumps(shared,sort_keys=True)]
        if not shared:shared=['Exact raw inputs and standard-library runtime are shared; independently authored checking paths and other trusted components are disclosed in the pinned report.']
        data['claims'].append(dict(id=report['claim_id'],revision=revision,statement=report['statement'],kind=report['kind'],basis=report['basis'],
            status='VERIFIED',review_state='CLEAR',scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
            assumptions=report.get('assumptions',['Only the explicit graph/matching population or fixed configuration stated in the bound audit.','No nontrivial target automorphism is assumed.']),
            dependencies=report['dependencies'],evidence=evidence,
            verification=[dict(claim_revision=revision,verifier=report['verifier'],
                method='independent_derivation'if label in('triangle39-gram-sos','triangle-paircap-reduction')else'independent_artifact_check',
                command_or_audit=path,timestamp=report['timestamp'],outcome='PASS',scope=scope,artifact_hashes=hashes,
                shared_components=shared,controls=['The pinned independent report distinguishes universal derivation, complete finite enumeration, representative witnesses and calibrated positive/corrupted controls.'],limitations=limits)],
            limitations=limits,created_at=now,updated_at=now,external_source=None,
            unknowns={'external_source':'Internal checking only; cited archive overlap does not import historical verification or establish novelty.'},
            reproducibility=dict(manifest=evidence[0])))
        added.append(report['claim_id'])
    data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',previous)
    assert validation['valid'],validation['errors']
    out=ROOT/(B+'eighth_registration');out.mkdir(parents=True,exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    assert ledger.read_bytes()==before
    ledger.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=added,checked_input_bindings=bound_inputs,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),
        validation=validation,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'new_verified_claims':len(added),'claim_population':len(data['claims']),'target_resolution':'UNKNOWN'}))

if __name__=='__main__':main()
