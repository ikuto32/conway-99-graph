"""Record actual registry and syntax checks for the wave29 publication cutoff."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20261001_'
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    path=B+'resume/twentyninth_precommit_validation.json'
    assert h('CLAIMS.yaml')=='297d6d915c244ccc6dd82c39939eef917a2b0ffa8a76126185b386774a097baf'
    registry_command=[sys.executable,'-B','acceleration/validate_claims.py','--hashes','available','--previous','acceleration/results/20260930_twentyninth_initial_registration/CLAIMS.before.yaml','--out',path]
    check=subprocess.run(registry_command,cwd=ROOT,capture_output=True,timeout=60)
    for label,data in [('stdout',check.stdout),('stderr',check.stderr)]:
        with(ROOT/(B+'resume/twentyninth_registry.'+label+'.log')).open('xb')as f:f.write(data)
    assert check.returncode==0;validation=json.loads((ROOT/path).read_bytes());assert validation['valid']and not validation['errors']
    command=[sys.executable,'-B','check_python_syntax.py'];result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60);files={}
    for label,data in [('stdout',result.stdout),('stderr',result.stderr)]:
        p=B+'resume/twentyninth_syntax.'+label+'.log'
        with(ROOT/p).open('xb')as f:f.write(data)
        files[p]=h(p)
    assert result.returncode==0;syntax=json.loads(result.stdout)
    receipt=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=h(Path(__file__).relative_to(ROOT)),registry_validation=dict(path=path,sha256=h(path),command=registry_command,actual_exit_code=check.returncode,valid=True,skipped=validation['skipped']),syntax=dict(command=command,actual_exit_code=result.returncode,result=syntax,outputs_sha256=files,scope='Timestamped source census includes later untracked preparation. Publication is restricted separately by exact inventory.'),skipped_checks=['No duplicate mathematical replay solely for publication. Original independent reports remain authoritative.','Registry unit controls and other unchanged CI checks are not repeated locally; inspect actual pushed-commit workflow results separately.'],mathematical_verification=False)
    output=ROOT/(B+'resume/twentyninth_precommit_checks.json')
    with output.open('x',encoding='utf8',newline='\n')as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(dict(registry_valid=True,syntax=syntax,receipt_sha256=h(output.relative_to(ROOT)))))
if __name__=='__main__':main()
