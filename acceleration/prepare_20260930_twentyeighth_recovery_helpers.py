"""Make fresh wave28-labelled copies of previously exercised recovery tooling."""
from datetime import datetime,timezone
from pathlib import Path
import ast,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'acceleration/results/20260930_twentyeighth_recovery_preparation';out.mkdir(exist_ok=False);rows=[]
    for stem in['recover_20260930_twentyseventh_raw_artifacts','check_20260930_twentyseventh_recovery_controls']:
        old=ROOT/'acceleration'/(stem+'.py');new=old.with_name(stem.replace('twentyseventh','twentyeighth')+'.py');source=old.read_text(encoding='utf8')
        if stem.startswith('recover_'):assert h(old)=='6d0721e1c25411e0d661e782fff19719a9a887bea8e019f5ec55536f373c4183'
        changed=source.replace('twentyseventh','twentyeighth').replace('TWENTYSEVENTH','TWENTYEIGHTH').replace('wave27','wave28')
        if stem.startswith('check_'):
            changed=changed.replace('complete fresh fourteen-artifact restoration','complete fresh restoration of every manifest original')
            marker="original=json.loads(M.read_bytes());rows=[]"
            replacement="original=json.loads(M.read_bytes());fresh=json.loads((B/'fresh_recovery.json').read_bytes());assert fresh['status']=='TWENTYEIGHTH_RAW_ARTIFACT_RECOVERY_PASS' and fresh['originals']==len(original['records']) and fresh['action_counts']=={'RESTORED_MISSING':len(original['records'])};rows=[]"
            assert changed.count(marker)==1;changed=changed.replace(marker,replacement)
        ast.parse(changed)
        with new.open('x',encoding='utf8',newline='\n')as f:f.write(changed)
        rows.append(dict(predecessor=old.relative_to(ROOT).as_posix(),predecessor_sha256=h(old),source=new.relative_to(ROOT).as_posix(),source_sha256=h(new)))
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),preparer_sha256=h(Path(__file__)),records=rows,changes=['Wave28 path/status/progress labels.','Corrupted-control wrapper explicitly authenticates complete fresh recovery population and all RESTORED_MISSING actions.'],ast_checks=2,recovery_calls=0,native_calls=0,mathematical_verification=False)
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(rows))
if __name__=='__main__':main()
