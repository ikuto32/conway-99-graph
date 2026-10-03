"""Confirm immutable publication; record candidate-output selection correction."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import yaml
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
COMMIT='32a012be994de5d40568023a460b3a9938da2fcd'
B='acceleration/results/20260930_'
def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True).split()[0]
    assert remote==COMMIT
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=registry.read_ledger(path)
    changed=[];local=[]
    for artifact in data['artifacts']:
        if artifact['availability']!='LOCAL_ONLY' or not artifact['path'] or '20260930' not in artifact['path']:continue
        blob=subprocess.run(['git','show',COMMIT+':'+artifact['path']],cwd=ROOT,capture_output=True)
        if blob.returncode:local.append(artifact['id']);continue
        assert sha(blob.stdout)==artifact['sha256']==sha((ROOT/artifact['path']).read_bytes())
        artifact.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{COMMIT}/{artifact["path"]}',unavailable_reason=None)
        changed.append(artifact['id'])
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old)
    assert validation['valid'],validation['errors']
    out=ROOT/(B+'resume')
    with(out/'claims_before_seventh_publication.yaml').open('xb')as f:f.write(before)
    assert path.read_bytes()==before
    path.write_bytes(yaml.safe_dump(data,sort_keys=False,width=110).encode())
    report=dict(timestamp=now,published_commit=COMMIT,confirmed_remote_ref=remote,new_public_artifact_ids=changed,
        remaining_local_originals=local,previous_ledger_sha256=sha(before),ledger_sha256=sha(path.read_bytes()),validation=validation,
        mathematical_claim_changes=[],target_resolution='UNKNOWN',scope='Availability metadata only. Exact statements, revisions, dependencies, verification records and artifact hashes unchanged.')
    with(out/'seventh_publication_pointer_receipt.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(report,f,indent=2);f.write('\n')
    # The inventory's substring row_obstruction did not match row29_obstruction.
    # Preserve this packaging deviation and immediately publish its two missing producer files.
    prefix=B+'triangle_wave154_row29_obstruction/'
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',COMMIT,'--',prefix],cwd=ROOT,text=True).splitlines()
    assert len(names)==5
    manifest=json.loads((ROOT/(prefix+'manifest.json')).read_bytes())
    companions=['acceleration/theory_20260930_triangle_row_obstruction.py','acceleration/theory_20260930_triangle_row_obstruction_spec.md']
    for name in companions:assert sha((ROOT/name).read_bytes())==manifest['input_hashes'][name]
    deviation=dict(timestamp=now,status='PUBLICATION_SELECTION_DEVIATION_RECORDED',commit=COMMIT,
        actual_candidate_output_paths=names,original_exclusion_substring='row_obstruction',actual_path_substring='row29_obstruction',
        reason='Literal substring selection did not match the more specific row29 name; five frozen producer artifacts were included before the planned eighth-wave publication.',
        mathematical_claim_effect='None. The raw producer summary remains CANDIDATE and no row29 claim appears in seventh ledger totals. Its separate independent audit is reserved for the next milestone.',
        corrective_publication_companions={name:sha((ROOT/name).read_bytes()) for name in companions},
        action='Publish the exact two missing producer source/spec companions in this follow-up commit; preserve the original catalog and commit unchanged.',
        full_original_artifact_input_hashes=manifest['input_hashes'])
    with(out/'seventh_candidate_publication_selection_correction.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(deviation,f,indent=2);f.write('\n')
    print(json.dumps({'new_public_artifacts':len(changed),'remaining_local_originals':len(local),'candidate_publication_companions':companions,'mathematical_claim_changes':[]}))

if __name__=='__main__':main()
