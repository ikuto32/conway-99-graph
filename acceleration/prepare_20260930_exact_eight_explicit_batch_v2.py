"""Create and calibrate a fresh progress-only builder; preserve frozen v1."""
import ast,hashlib,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration'
OLD=A/'build_20260930_exact_eight_explicit_batch.py'
NEW=A/'build_20260930_exact_eight_explicit_batch_v2.py'
OUT=A/'results/20260930_exact_eight_explicit_batch_preparation_v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert sha(OLD)=='507de7427999ed010c0c4fc848c236b2dab4d66a335aaac232f9174e7994de74'
    text=OLD.read_text(encoding='utf8')
    assert text.count('from pathlib import Path\n')==1 and text.count('for i,p in enumerate(plan):')==1
    changed=text.replace('from pathlib import Path\n','from pathlib import Path\nfrom tqdm import tqdm\n').replace('for i,p in enumerate(plan):','for i,p in enumerate(tqdm(plan,desc="Exact-eight builds",unit="case")):')
    with NEW.open('x',encoding='utf8',newline='\n')as f:f.write(changed)
    spec=NEW.with_name(NEW.stem+'_spec.md')
    with spec.open('x',encoding='utf8',newline='\n')as f:
        f.write('# Progress-only builder v2\n\nThe sole execution delta from frozen v1 is importing pinned tqdm and wrapping the ordered build loop with a progress display. The selection, commands, deadlines, checkpoints, hash checks and result semantics are unchanged. v1 remains immutable.\n\n')
        f.write(OLD.with_name(OLD.stem+'_spec.md').read_text(encoding='utf8'))
    check=A/'prepare_20260930_exact_eight_explicit_batch.py'
    source=check.read_text(encoding='utf8')
    source=source.replace("DRIVER=A/'build_20260930_exact_eight_explicit_batch.py'","DRIVER=A/'build_20260930_exact_eight_explicit_batch_v2.py'")
    source=source.replace("OUT=A/'results/20260930_exact_eight_explicit_batch_preparation'","OUT=A/'results/20260930_exact_eight_explicit_batch_preparation_v2'")
    source=source.replace("['datetime','pathlib']","['datetime','pathlib','tqdm']")
    # Isolate the previous preparation's definitions, retaining this new preparer's identity.
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'prepared_controls'}
    exec(compile(source,str(check),'exec'),ns);ns['main']()
    assert NEW.read_text(encoding='utf8').replace('from tqdm import tqdm\n','').replace('enumerate(tqdm(plan,desc="Exact-eight builds",unit="case"))','enumerate(plan)')==text
    delta=dict(status='PROGRESS_ONLY_SOURCE_DELTA_CHECK_PASS',old_sha256=sha(OLD),new_sha256=sha(NEW),spec_sha256=sha(spec),preparer_sha256=sha(Path(__file__)),reused_controls_source_sha256=sha(check),entrypoint_calls=0,native_calls=0,producer_calls=0)
    with(OUT/'delta.json').open('x',encoding='utf8',newline='\n')as f:json.dump(delta,f,indent=2);f.write('\n')
    print(json.dumps(delta))
if __name__=='__main__':main()
