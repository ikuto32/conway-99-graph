"""Update availability only after exact artifact bytes exist in a published commit."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--commit',required=True);p.add_argument('--pr',required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise ValueError('Preserve previous publication record')
    ledger_path=Path('CLAIMS.yaml');before=ledger_path.read_bytes();ledger=yaml.safe_load(before)
    records=[]
    for artifact in ledger['artifacts']:
        result=subprocess.run(['git','show',f"{a.commit}:{artifact['path']}"],capture_output=True)
        if result.returncode:
            continue
        actual=sha256(result.stdout).hexdigest()
        if actual!=artifact['sha256']:
            raise ValueError('Published bytes differ: '+artifact['id'])
        old=artifact['availability']
        artifact.update(availability='PUBLIC',retrieval=f"https://github.com/ikuto32/conway-99-graph/blob/{a.commit}/{artifact['path']}",unavailable_reason=None)
        records.append(dict(id=artifact['id'],path=artifact['path'],sha256=actual,previous_availability=old))
    now=datetime.now(timezone.utc).isoformat();ledger['updated_at']=now
    ledger_path.write_text(yaml.safe_dump(ledger,sort_keys=False,width=110),encoding='utf-8')
    with a.out.open('x',encoding='utf-8') as f:
        json.dump(dict(timestamp=now,source_commit=a.commit,draft_pr=a.pr,
            remote_observation='Root separately checked gh pr view and git ls-remote; OPEN draft, head equals this commit.',
            records=records,ledger_before_sha256=sha256(before).hexdigest(),ledger_after_sha256=sha256(ledger_path.read_bytes()).hexdigest(),
            claim_statements_revisions_verification_unchanged=True,scope='Artifact availability metadata only; no new mathematical claim.',
            script_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),f,indent=2);f.write('\n')
    print(json.dumps(dict(published_artifacts=len(records),commit=a.commit,draft_pr=a.pr)))


if __name__=='__main__':main()
