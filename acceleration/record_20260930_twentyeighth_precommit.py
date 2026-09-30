"""Record the actual registry and source-syntax checks before wave28 staging."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=B+'resume/twentyeighth_precommit_validation.json';validation=json.loads((ROOT/p).read_bytes());assert validation['valid']and not validation['errors']
    command=[sys.executable,'-B','check_python_syntax.py'];r=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60)
    files={}
    for name,data in [('stdout',r.stdout),('stderr',r.stderr)]:
        q=B+'resume/twentyeighth_syntax.'+name+'.log'
        with(ROOT/q).open('xb')as f:f.write(data)
        files[q]=h(q)
    assert r.returncode==0;rj=json.loads(r.stdout)
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=h(Path(__file__).relative_to(ROOT)),registry_validation=dict(path=p,sha256=h(p),valid=True,skipped=validation['skipped']),syntax=dict(command=command,actual_exit_code=r.returncode,result=rj,outputs_sha256=files,scope='Timestamped root/acceleration source census includes later untracked preparation sources. Actual publication remains bounded by the independent stage inventory.'),skipped_checks=['No duplicate complete mathematical audit replay during publication; original independent reports remain authoritative.','Registry unit controls and the remaining unchanged CI checks are left to the actual pushed-commit workflow; no unobserved pass asserted.'],mathematical_verification=False)
    q=ROOT/(B+'resume/twentyeighth_precommit_checks.json')
    with q.open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(registry_valid=True,syntax=rj,receipt_sha256=h(q.relative_to(ROOT)))))
if __name__=='__main__':main()
