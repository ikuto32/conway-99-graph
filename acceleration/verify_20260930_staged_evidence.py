"""Check hash-bound staged evidence bytes before publication; no mathematical review."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml

ROOT=Path(__file__).resolve().parents[1]
def main():
    ledger=yaml.safe_load((ROOT/'CLAIMS.yaml').read_bytes());ok=[];absent=[];bad=[]
    for a in ledger['artifacts']:
        if '20260930' not in a['path']:continue
        r=subprocess.run(['git','show',':'+a['path']],cwd=ROOT,capture_output=True)
        if r.returncode:absent.append(a['path'])
        elif sha256(r.stdout).hexdigest()!=a['sha256']:bad.append(a['path'])
        else:ok.append(a['id'])
    out=dict(timestamp=datetime.now(timezone.utc).isoformat(),matched_artifacts=ok,local_originals_not_staged=absent,mismatched_staged_bytes=bad,mathematical_verification=False)
    p=ROOT/'acceleration/results/20260930_resume/third_staged_evidence.json'
    with p.open('x',encoding='utf-8')as f:json.dump(out,f,indent=2)
    print(json.dumps(dict(staged_bound_artifacts=len(ok),local_originals_not_staged=absent,mismatched_staged_bytes=bad)))
    assert not bad

if __name__=='__main__':main()
