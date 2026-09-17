"""Inventory exact two-coordinate proof checker inputs in one immutable Git commit."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];COMMIT='2fca344c28bbf0b1be329336c26f24f270ba5746';SEED='acceleration/results/20260917_independent_review/two_matching_solve_bound.json';PIN='adf254892686dab05f0317b9ecec963b1b98eee8f9f8ccee129b05ebf6145065'
def git(*args,input=None):return subprocess.run(['git','-C',str(ROOT),*args],input=input,capture_output=True,check=True).stdout
def main():
    seed=git('show',COMMIT+':'+SEED);assert hashlib.sha256(seed).hexdigest()==PIN
    inventory=dict(json.loads(seed)['inputs_sha256']);inventory[SEED]=PIN;names=sorted(inventory)
    request=''.join(COMMIT+':'+name+'\n'for name in names).encode();headers=git('cat-file','--batch-check',input=request).decode().splitlines();assert len(headers)==len(names)
    absent=[name for name,line in zip(names,headers)if line.endswith(' missing')];sizes=[int(line.split()[-1])for line in headers if not line.endswith(' missing')];assert sum(sizes)<200000000,'preregistered200MB read cap'
    records=[]
    if not absent:
        payload=git('cat-file','--batch',input=request);offset=0
        for name,header in zip(names,headers):
            end=payload.index(b'\n',offset);actual=payload[offset:end].decode();assert actual==header;oid,kind,size=actual.split();assert kind=='blob';size=int(size);start=end+1;data=payload[start:start+size];offset=start+size+1;assert payload[offset-1:offset]==b'\n';digest=hashlib.sha256(data).hexdigest();assert digest==inventory[name],'Git byte mismatch '+name
            records.append(dict(path=name,git_object_id=oid,size_bytes=size,sha256=digest,outcome='PASS'))
        assert offset==len(payload)
    result=dict(status='TWO_COORDINATE_GIT_RUNTIME_CLOSURE_PRESENT'if not absent else 'TWO_COORDINATE_GIT_RUNTIME_CLOSURE_MISSING',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=COMMIT,source_checker_commit=COMMIT,command=[sys.executable,*sys.argv],cwd=str(ROOT),git_version=git('--version').decode().strip(),seed=SEED,seed_sha256=PIN,question='Does the immutable Git commit contain every byte hash-bound by the frozen two-coordinate exact checker?',population='284runtime inputs plus frozen audit seed; unique Git paths, no transitive expansion beyond actual checker inventory',max_bytes=200000000,records=records,missing=absent,unique_paths=len(names),total_bytes=sum(sizes),local_artifact_fallback=False,isolated_execution_performed=False,network_retrieval_tested=False,inputs_sha256={'acceleration/audit_20260917_two_public_closure.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},limitations=['Git object presence and bytes only; this preparation is not a completed isolated replay or independent mathematical review.','Public network retrieval not attempted by this script.'])
    out=ROOT/'acceleration/results/20260917_independent_review/two_public_git_closure_preparation.json'
    with out.open('x')as f:json.dump(result,f,indent=2)
    print(result['status'],len(records),sum(sizes),hashlib.sha256(out.read_bytes()).hexdigest())
if __name__=='__main__':main()
