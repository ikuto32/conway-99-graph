"""Publish the remaining checker audit after its separate immutable commit."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1]
COMMIT='6b0d3d49f4a68607b84260fc6cdc4d1abfacf6ad'
def main():
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],text=True).split()[0];assert remote==COMMIT
    ledger=ROOT/'CLAIMS.yaml';before=ledger.read_bytes();old=registry.read_ledger(ledger);data=registry.read_ledger(ledger)
    matches=[a for a in data['artifacts'] if a['id']=='editorial-checker-v2-audit'];assert len(matches)==1
    a=matches[0];assert a['availability']=='LOCAL_ONLY'
    blob=subprocess.check_output(['git','show',COMMIT+':'+a['path']]);assert sha256(blob).hexdigest()==a['sha256']==sha256((ROOT/a['path']).read_bytes()).hexdigest()
    a.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{COMMIT}/{a["path"]}',unavailable_reason=None)
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old);assert result['valid'],result['errors']
    folder=ROOT/'acceleration/results/20260930_resume'
    with (folder/'claims_before_sixth_final_audit_publication.yaml').open('xb') as f:f.write(before)
    assert ledger.read_bytes()==before;ledger.write_bytes(yaml.safe_dump(data,sort_keys=False,width=110).encode())
    report=dict(timestamp=now,published_commit=COMMIT,confirmed_remote_ref=remote,artifact_id=a['id'],artifact_sha256=a['sha256'],previous_ledger_sha256=sha256(before).hexdigest(),ledger_sha256=sha256(ledger.read_bytes()).hexdigest(),validation=result,mathematical_claim_changes=[],scope='Availability and retrieval only; source audit, claim statement/revision, dependencies and historical verification unchanged.')
    with (folder/'sixth_final_audit_publication_receipt.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(new_public_artifacts=1,mathematical_claim_changes=[])))
if __name__=='__main__':main()
