"""Derive eight exact saved audit commands; do not rerun completed mathematics."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_independent_review/'
N='acceleration/results/20261001_independent_review/'
PINS={
 B+'exact_eight_next64_cnfs_v3/summary.json':'517ac1c4d51a9eb5da4b6a3579bf5f6b23bfdb670bac5624da22414c3d24da6a',
 B+'exact_eight_next64_object_calibration/summary.json':'95af9e1863fa2d15497cc48235adfed0cc3feff38d906e562440b1ad21cf45a0',
 B+'exact_eight_next64_proofs/summary.json':'7e2cab83b264a30e35a5797137b4948fb59d30e1b1b234ed5ab54e517c13881f',
 N+'exact_eight_prefix64_batch02_cnfs_v3/summary.json':'744996131cec59543519568a2093961edabf4f6dfa0eb9b17c419bb4d6e9b0ca',
 N+'exact_eight_prefix64_batch02_object_calibration/summary.json':'2babe6443b15d9a060504e22943fe9ea4db44dfe6e34cb8565b03e2e08f85e4f',
 B+'sizeclass16_gf3_affine_weights/summary.json':'232a38f1a761915f1c5308a1597f9f7ba121dd9372198a7b5a0b6ff55b125834',
 N+'exact_eight_uniform_gram/summary.json':'c911f7a0d9156c12e91491061f96eb691e1f7d8360f862e5cf45bd7114cff38e',
}

def h(path):
    with (ROOT/path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    import yaml
    ledger=yaml.safe_load((ROOT/'CLAIMS.yaml').read_bytes()); assert len(ledger['claims'])==300
    claim=next(c for c in ledger['claims'] if c['id']=='C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH02-LITERAL-PROFILE-EXCLUSIONS')
    a=next(a for a in ledger['artifacts'] if a['id']==claim['evidence'][0]); pins=dict(PINS); pins[a['path']]=a['sha256']; assert len(pins)==8
    commands=[]
    for p,pin in pins.items():
        assert h(p)==pin; report=json.loads((ROOT/p).read_bytes()); saved=report['command']
        index=next(i for i,v in enumerate(saved) if v.startswith('acceleration/audit_') and v.endswith('.py')); script=saved[index]
        assert report['inputs_sha256'][script]==h(script) and saved.count('--out')==1
        name=Path(p).parent.name; replay=[sys.executable,'-B',*saved[index:]]; replay[replay.index('--out')+1]='build/research-local/wave29-replay/'+name
        commands.append(dict(name=name,original_report=p,original_report_sha256=pin,original_command=saved,replay_command=replay,expected_status=report['status'],source_sha256=h(script)))
    output=ROOT/'acceleration/results/20261001_resume/twentyninth_replay_plan.json'
    result=dict(status='TWENTYNINTH_REPLAY_COMMANDS_AUTHENTICATED_NOT_EXECUTED',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=h(Path(__file__).relative_to(ROOT)),commands=commands,replay_calls=0,native_search_calls=0,skipped_checks=['The eight original independent mathematical/object audits completed successfully. No duplicate mathematical audit is run solely for publication preparation.'],limitations=['Command/source authentication is not mathematical verification.','Use fresh replay output directories; do not overwrite original evidence.','Recover exact raw artifacts and reconstruct the recorded checker/tool environment first.'])
    with output.open('x',encoding='utf8',newline='\n') as f: json.dump(result,f,indent=2); f.write('\n')
    print(json.dumps(dict(commands=len(commands),replay_calls=0,sha256=h(output.relative_to(ROOT)))))

if __name__=='__main__': main()
