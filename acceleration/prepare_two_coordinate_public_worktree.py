"""Extract only the frozen two-coordinate checker runtime closure from immutable Git."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];SEED='acceleration/results/20260917_independent_review/two_matching_solve_bound.json';PIN='adf254892686dab05f0317b9ecec963b1b98eee8f9f8ccee129b05ebf6145065'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--commit',required=True);ap.add_argument('--destination',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);args=ap.parse_args();destination=args.destination.resolve();report=args.report.resolve();destination.relative_to(ROOT);report.relative_to(ROOT)
    if destination.exists()or report.exists():raise ValueError('Fresh worktree and report required')
    def git(*cmd,input=None):return subprocess.run(['git','-C',str(ROOT),*cmd],input=input,capture_output=True,check=True).stdout
    assert len(args.commit)==40 and git('rev-parse',args.commit).decode().strip()==args.commit
    raw=git('show',args.commit+':'+SEED);assert hashlib.sha256(raw).hexdigest()==PIN;inventory=json.loads(raw)['inputs_sha256'];inventory[SEED]=PIN
    for extra in('.gitattributes','acceleration/replay_two_coordinate_moment_checker.py'):
        inventory[extra]=hashlib.sha256(git('show',args.commit+':'+extra)).hexdigest()
    names=sorted(inventory);query=''.join(args.commit+':'+n+'\n'for n in names).encode();headers=git('cat-file','--batch-check',input=query).decode().splitlines();assert len(headers)==len(names)and all(not s.endswith(' missing')for s in headers),'Missing Git dependency';total=sum(int(s.split()[-1])for s in headers);assert total<200000000
    git('worktree','add','--detach','--no-checkout',str(destination),args.commit)
    subprocess.run(['git','-C',str(destination),'-c','core.autocrlf=false','checkout',args.commit,'--','.gitattributes'],check=True,capture_output=True)
    specs=report.with_suffix('.pathspec');specs.parent.mkdir(parents=True,exist_ok=True)
    with specs.open('xb')as f:f.write(b'\x00'.join(n.encode()for n in names)+b'\x00')
    subprocess.run(['git','-C',str(destination),'-c','core.autocrlf=false','checkout',args.commit,'--pathspec-from-file='+str(specs),'--pathspec-file-nul'],check=True,capture_output=True)
    payload=git('cat-file','--batch',input=query);offset=0;records=[]
    for name in names:
        end=payload.index(b'\n',offset);oid,kind,size=payload[offset:end].decode().split();assert kind=='blob';size=int(size);blob=payload[end+1:end+1+size];offset=end+size+2;assert payload[offset-1:offset]==b'\n';p=(destination/name).resolve();p.relative_to(destination);expected=hashlib.sha256(blob).hexdigest();assert expected==inventory[name]and p.read_bytes()==blob,'Exact Git bytes '+name
        records.append(dict(path=name,sha256=expected,size_bytes=size,git_blob=oid))
    assert offset==len(payload)
    result=dict(status='TWO_COORDINATE_EXACT_GIT_WORKTREE_EXTRACTION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=args.commit,command=[sys.executable,*sys.argv],cwd=str(ROOT),destination=str(destination),records=records,total_bytes=total,files=len(records),inputs_sha256={'acceleration/prepare_two_coordinate_public_worktree.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),specs.relative_to(ROOT).as_posix():hashlib.sha256(specs.read_bytes()).hexdigest()},source_artifact_fallback=False,scope='Git-only runtime input closure plus frozen audit seed, attributes and replay wrapper; real detached worktree preserves exact provenance query.',isolated_checker_executed=False)
    with report.open('x')as f:json.dump(result,f,indent=2)
    print(result['status'],len(records),total,hashlib.sha256(report.read_bytes()).hexdigest())
if __name__=='__main__':main()
