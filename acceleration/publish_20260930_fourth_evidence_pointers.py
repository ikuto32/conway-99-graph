"""Publish availability metadata only after exact pushed Git blob checks."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml
import validate_claims as validator

ROOT=Path(__file__).resolve().parents[1]
def main():
    commit=subprocess.check_output(['git','rev-parse','6ee4a57aaf166b5bb7619d341ed0b4f1dcf50000'],text=True).strip()
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],text=True).split()[0]
    assert remote==commit
    path=ROOT/'CLAIMS.yaml';raw=path.read_bytes();old=validator.read_ledger(path);data=validator.read_ledger(path)
    changed=[];local=[]
    for a in data['artifacts']:
        if a['availability']!='LOCAL_ONLY' or '20260930' not in a['path']:continue
        r=subprocess.run(['git','show',commit+':'+a['path']],capture_output=True)
        if r.returncode:
            local.append(a['id']);continue
        assert sha256(r.stdout).hexdigest()==a['sha256']==sha256((ROOT/a['path']).read_bytes()).hexdigest()
        a.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{commit}/{a["path"]}',unavailable_reason=None)
        changed.append(a['id'])
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    result=validator.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old);assert result['valid'],result['errors']
    with (ROOT/'acceleration/results/20260930_resume/claims_before_fourth_publication.yaml').open('xb') as f:f.write(raw)
    assert path.read_bytes()==raw;path.write_text(yaml.safe_dump(data,sort_keys=False,width=110),encoding='utf-8')
    receipt=dict(timestamp=now,published_commit=commit,confirmed_remote_ref=remote,artifact_ids=changed,remaining_local_originals=local,
        impact_review='Availability/retrieval metadata only. All statements, revisions, dependency pins, verification records and artifact bytes/hashes are unchanged. Oversized originals remain LOCAL_ONLY with exact public recovery companions; local compiled binaries are not declared public.',
        previous_ledger_sha256=sha256(raw).hexdigest(),ledger_sha256=sha256(path.read_bytes()).hexdigest(),validation=result,mathematical_claim_changes=[],target_resolution='UNKNOWN')
    with(ROOT/'acceleration/results/20260930_resume/fourth_publication_pointer_receipt.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,indent=2)
    print(json.dumps(dict(new_public_artifacts=len(changed),remaining_local_originals=len(local),mathematical_claim_changes=[])))

if __name__=='__main__':main()
