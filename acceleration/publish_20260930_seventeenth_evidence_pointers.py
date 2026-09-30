"""Bind unchanged seventeenth claims to confirmed immutable public evidence."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,subprocess
import yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];COMMIT='97a3b8415f2dbb83b27b6b6608f11cf155812999'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True).split()[0];assert remote==COMMIT
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();previous=registry.read_ledger(path);data=registry.read_ledger(path);changed=[];remaining=[]
    for a in data['artifacts']:
        if a['availability']!='LOCAL_ONLY'or not a['path']or'20260930'not in a['path']:continue
        blob=subprocess.run(['git','show',COMMIT+':'+a['path']],cwd=ROOT,capture_output=True)
        if blob.returncode:remaining.append(a['id']);continue
        assert sha(blob.stdout)==a['sha256']==sha((ROOT/a['path']).read_bytes())
        a.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{COMMIT}/{a["path"]}',unavailable_reason=None);changed.append(a['id'])
    # The raw cyclic proof is retained locally and is publicly recoverable.
    proof=next(a for a in data['artifacts']if a['id']=='seventeenth-cyclic-2-evidence2')
    manifest='acceleration/results/20260930_hadamard_cyclic_proof_packages/artifact_packages.json'
    public=subprocess.check_output(['git','show',COMMIT+':'+manifest],cwd=ROOT);package=json.loads(public)
    assert public==(ROOT/manifest).read_bytes()and package['raw_sha256']==proof['sha256']
    proof['retrieval']=f'Recover exact raw proof from https://github.com/ikuto32/conway-99-graph/blob/{COMMIT}/{manifest}; verify SHA256 before replay.'
    proof['unavailable_reason']='Original raw file is LOCAL_ONLY; complete lossless package and replay instructions are public at the pinned commit.'
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now;assert data['claims']==previous['claims']
    result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',previous);assert result['valid'],result['errors']
    folder=ROOT/'acceleration/results/20260930_resume'
    with(folder/'claims_before_seventeenth_publication.yaml').open('xb')as stream:stream.write(before)
    assert path.read_bytes()==before;path.write_bytes(yaml.safe_dump(data,sort_keys=False,width=110).encode())
    receipt=dict(timestamp=now,published_commit=COMMIT,confirmed_remote_ref=remote,new_public_artifact_ids=changed,remaining_local_originals=remaining,
        recoverable_raw_proof=dict(artifact_id=proof['id'],package_path=manifest,package_sha256=sha(public),raw_sha256=proof['sha256']),
        previous_ledger_sha256=sha(before),ledger_sha256=sha(path.read_bytes()),validation=result,mathematical_claim_changes=[],target_resolution='UNKNOWN',
        scope='Artifact availability and retrieval only; all claim statements/revisions/dependencies/verification records unchanged.')
    with(folder/'seventeenth_publication_pointer_receipt.json').open('x',encoding='utf-8',newline='\n')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(new_public_artifacts=len(changed),remaining_local_originals=len(remaining),mathematical_claim_changes=[])))
if __name__=='__main__':main()
