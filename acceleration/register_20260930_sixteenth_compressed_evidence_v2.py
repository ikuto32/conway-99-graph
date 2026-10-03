"""Add a separately checked smaller certificate to the unchanged fixed-support statement at independently approved revision2."""
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
I=B+'independent_review/hadamard_farkas_compressed/'


def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())


def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old)
    assert len(data['claims'])==165
    pins={I+'summary.json':'81c9989d4721c4298e6a87525dcdd5fe2592e708c2683bfb55b5015315f6ef8c',
        I+'claim_evidence_addendum.json':'bf6d0599fb43206db68827a056d693c89ad5015c4924fde1e761ca68eda3a506',B+'independent_review/farkas_revision2_impact/summary.json':'59bde4c9988d41fc88153949909b93bff6518fed5b8002285b610ed4d0532fd5'}
    for p,v in list(pins.items()):
        assert h(p)==v
        for q,w in read(p).get('inputs_sha256',{}).items():assert h(q)==w;pins[q]=w
    impact_path=B+'independent_review/farkas_revision2_impact/summary.json'
    audit=read(impact_path);assert audit['status']=='INDEPENDENT_FIXED_SUPPORT_FARKAS_REVISION2_IMPACT_PASS' and audit['claim_revision']==2
    now=datetime.now(timezone.utc).isoformat();evidence=[];hashes={}
    for i,p in enumerate([I+'summary.json',I+'claim_evidence_addendum.json',impact_path]):
        aid='sixteenth-compressed-farkas-evidence-'+str(i);assert aid not in {a['id']for a in data['artifacts']}
        value=h(p);evidence.append(aid);hashes[aid]=value
        data['artifacts'].append(dict(id=aid,path=p,sha256=value,availability='LOCAL_ONLY',
            retrieval='Exact workspace path; raw alternate integer certificate and unchanged model are pinned in this audit.',
            unavailable_reason='Sixteenth-cohort immutable publication has not been confirmed.'))
    ci=next(i for i,c in enumerate(data['claims'])if c['id']=='C-FIXED-HADAMARD-CONNECTED01-SUPPORT-EXCLUSION')
    claim=copy.deepcopy(data['claims'][ci]);data['claims'][ci]=claim
    assert claim==read(B+'independent_review/farkas_revision2_impact/revision1_claim_snapshot.json')
    assert claim['revision']==1 and claim['status']=='VERIFIED' and claim['review_state']=='CLEAR'
    claim['revision']=2
    claim['evidence']=[*claim['evidence'],*evidence]
    claim['verification'].append(dict(claim_revision=2,verifier='/root/state_literature_audit',method='independent_artifact_check',
        command_or_audit=impact_path,timestamp=audit['timestamp'],outcome='PASS',
        scope='Revision2 impact review freshly checks both original and compressed integer certificates for the identical support/system; statement, assumptions, dependencies and other claims remain unchanged.',
        artifact_hashes=hashes,shared_components=audit['shared_components'],
        controls=['Fresh original and compressed726-weight/4067-product checks, exact revision1 and unaffected02/03 snapshots; prior calibrated controls explicitly bound.'],
        limitations=['The original certificate remains unchanged evidence.','No optimality or exhaustive compression search claim.','Only one fixed support, not its core, is excluded.']))
    claim['updated_at']=now;data['updated_at']=now
    assert all(new==prior for i,(new,prior)in enumerate(zip(data['claims'],old['claims'],strict=True))if i!=ci)
    assert all(claim[k]==old['claims'][ci][k] for k in old['claims'][ci] if k not in ['revision','evidence','verification','updated_at'])
    result=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'sixteenth_compressed_registration');out.mkdir(parents=True,exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before);after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    receipt=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=[],updated_evidence_claim_ids=[claim['id']],
        statement_changes=[],revision_changes=[dict(id=claim['id'],from_revision=1,to_revision=2)],checked_input_bindings=pins,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=result,
        registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(new_claims=0,additional_independent_certificate=claim['id'],claim_population=165)))


if __name__=='__main__':main()
