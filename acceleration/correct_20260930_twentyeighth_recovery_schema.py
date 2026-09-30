"""Preserve the failed field-name assumption and make a fresh narrow correction."""
from datetime import datetime,timezone
from pathlib import Path
import ast,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=ROOT/'acceleration/package_20260930_twentyeighth_recovery.py';spec=old.with_name(old.stem+'_spec.md');new=old.with_name(old.stem+'_v2.py');newsp=new.with_name(new.stem+'_spec.md');out=ROOT/'acceleration/results/20260930_twentyeighth_recovery_schema_failure';out.mkdir(exist_ok=False)
    evidence=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),failed_source_sha256=sha(old),failed_spec_sha256=sha(spec),observed_tool_chunk='c6af55',actual_exit_code=1,error="KeyError: 'hash_mismatches'",cause='Fresh inventory names the conflict list recorded_hash_conflicts; predecessor inventory used hash_mismatches.',stage='Before output-directory creation and before any compression/decompression.',outputs_created=False,original_source_preserved=True)
    with(out/'failure.json').open('x',encoding='utf8',newline='\n')as f:json.dump(evidence,f,indent=2);f.write('\n')
    text=old.read_text(encoding='utf8');token="inventory['hash_mismatches']";assert text.count(token)==1;text=text.replace(token,"inventory['recorded_hash_conflicts']");ast.parse(text)
    with new.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    with newsp.open('x',encoding='utf8',newline='\n')as f:f.write('# V2 inventory field-name correction\n\nThe preserved v1 failed before producing outputs because it expected the prior\ninventory conflict-field name. V2 checks recorded_hash_conflicts, the exact\nfield in the frozen wave28 inventory. All recovery semantics remain unchanged.\n\n'+spec.read_text(encoding='utf8'))
    with(out/'correction.json').open('x',encoding='utf8',newline='\n')as f:json.dump(dict(source_sha256=sha(new),spec_sha256=sha(newsp),preparer_sha256=sha(Path(__file__)),failure_sha256=sha(out/'failure.json'),executed_recovery_calls=0),f,indent=2);f.write('\n')
    print(json.dumps(dict(source_sha256=sha(new),spec_sha256=sha(newsp))))
if __name__=='__main__':main()
