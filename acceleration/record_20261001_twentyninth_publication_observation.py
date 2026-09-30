"""Save a current read-only remote/PR/workflow observation, with no success inference."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'acceleration/results/20261001_twentyninth_publication_observation';out.mkdir(exist_ok=False)
    records=[]
    commands=[('remote',['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930']),
        ('pr',['gh','pr','view','3','--json','number,url,state,isDraft,headRefOid,mergedAt']),
        ('workflows',['gh','run','list','--branch','codex/eight-coordinate-continuation-20260930','--limit','8','--json','databaseId,workflowName,status,conclusion,headSha,event'])]
    for label,command in commands:
        stamp=datetime.now(timezone.utc).isoformat();start=time.monotonic()
        run=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=30)
        outputs={}
        for channel,data in [('stdout',run.stdout),('stderr',run.stderr)]:
            p=out/(label+'.'+channel+'.log')
            with p.open('xb')as f:f.write(data)
            outputs[p.relative_to(ROOT).as_posix()]=hashlib.sha256(data).hexdigest()
        records.append(dict(timestamp=stamp,command=command,actual_exit_code=run.returncode,elapsed_seconds=time.monotonic()-start,
            outputs_sha256=outputs,result=json.loads(run.stdout)if label!='remote' and run.returncode==0 else run.stdout.decode('utf8',errors='replace')))
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),observations=records,
        evidence_commit='d43ab1ca6638b565d555b0765044668761de6a64',pointer_commit='cc55ad8bd7ad3ef35d33cae35232f9cc8eb264e5',
        mathematical_claim_changes=[],scope='Dated execution/publication metadata only. A workflow success is not mathematical verification; incomplete states remain as observed.')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(summary_sha256=hashlib.sha256((out/'summary.json').read_bytes()).hexdigest(),observations=[dict(label=name,exit=r['actual_exit_code'],result=r['result'])for(name,_),r in zip(commands,records)])))
if __name__=='__main__':main()
