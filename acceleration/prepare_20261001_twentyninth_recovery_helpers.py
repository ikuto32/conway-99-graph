"""Create fresh wave29-labelled copies of exercised exact-byte recovery tools."""
from datetime import datetime,timezone
from pathlib import Path
import ast,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
SOURCES=[
 ('package_20260930_twentyeighth_recovery_v2.py','25c553eddd2b4e3ecbe08bcc10d8dbd26564139a9fb3006cd115737bdd849b98','package_20261001_twentyninth_recovery.py'),
 ('recover_20260930_twentyeighth_raw_artifacts.py','f503fa64f21771619c6756c64710e0a06185f5a8b433b0a9653954e33b014256','recover_20261001_twentyninth_raw_artifacts.py'),
 ('check_20260930_twentyeighth_recovery_controls.py','81c3c7115ad91444f2f0b975f840d20fd3e39810cddc51fc9a58f59eb264038a','check_20261001_twentyninth_recovery_controls.py')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'acceleration/results/20261001_twentyninth_recovery_preparation';out.mkdir(exist_ok=False);records=[]
    for oldname,pin,newname in SOURCES:
        old=ROOT/'acceleration'/oldname;new=ROOT/'acceleration'/newname;assert sha(old)==pin
        text=old.read_text(encoding='utf8')
        if oldname.startswith('package_'):
            text=text.replace("OUT=B+'twentyeighth_raw_recovery'","OUT='acceleration/results/20261001_twentyninth_raw_recovery'")
            text=text.replace("B+'twentyseventh_artifact_packaging/catalog.json'","B+'twentyeighth_artifact_packaging/catalog.json'").replace('fd10bd3872a7699f7ea80e1072c697b300cdb9d0cf7cdb19dd1a0c898e6565a8','1dc941ddb899393f5d7d570f266cad6bc6205e64f3db13b4affe870f31de3586')
        text=text.replace('20260930_twentyeighth','20261001_twentyninth').replace('twentyeighth-recovery','twentyninth-recovery').replace('TWENTYEIGHTH','TWENTYNINTH').replace('WAVE28','WAVE29').replace('wave28','wave29')
        ast.parse(text)
        with new.open('x',encoding='utf8',newline='\n')as f:f.write(text)
        records.append(dict(predecessor=old.relative_to(ROOT).as_posix(),predecessor_sha256=pin,source=new.relative_to(ROOT).as_posix(),source_sha256=sha(new)))
    spec=ROOT/'acceleration/package_20261001_twentyninth_recovery_spec.md'
    with spec.open('x',encoding='utf8',newline='\n')as f:f.write('# Wave29 exact-byte public recovery\n\nConsume only the root-frozen candidate inventory and its explicit hash. Preserve all raw originals. Reuse an authenticated existing gzip stream when it is at most10MiB; otherwise create deterministic compressed parts with8MiB raw chunks. Compare every decompressed byte with its original, verify all sizes/hashes/offsets, and preserve a normalized manifest. No mathematical approval or solver call.\n\nThe restorer refuses conflicting existing destinations and unsafe paths, preserves original evidence, checks every compressed/raw identity and records the actual command/tool source. Perform one full restoration to a fresh directory and seven corrupted-manifest/part/path/existing-file controls before publication. Final independent metadata review must check the recovery results and replay command interfaces.\n')
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),preparer_sha256=sha(Path(__file__)),records=records,spec_sha256=sha(spec),changes=['Wave29 path/schema/status/progress labels.','Normalized recovery points to the immutable prior wave28 catalog; original protected-path guard is unchanged.'],ast_checks=3,recovery_calls=0,native_calls=0,mathematical_verification=False)
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(sources=3,recovery_calls=0,summary_sha256=sha(out/'summary.json'))))
if __name__=='__main__':main()
