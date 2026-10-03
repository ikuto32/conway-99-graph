"""Prepare an exact-inventory stager; no index or filesystem payload mutation."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=ROOT/'acceleration/stage_20260930_twentyeighth_evidence.py';assert h(old)=='f61b1c42dcfa835132f431188254904febe6dc4ce656e2fecca6e2a3e773004b'
    text=old.read_text(encoding='utf8')
    text=text.replace('20260930_twentyeighth','20261001_twentyninth').replace('20260930_TWENTYEIGHTH','20261001_TWENTYNINTH').replace('twentyeighth','twentyninth').replace('TWENTYEIGHTH','TWENTYNINTH').replace('wave28','wave29')
    text=text.replace("B='acceleration/results/20260930_'","B='acceleration/results/20261001_'")
    before="forbidden=('exact_eight_next64','four_serial_build_engineering','four_builds','sizeclass16_affine_gram_gf3','sizeclass16_gf3_affine_weights','explicit_batch_v3','explicit_batch_proofs_v2')"
    assert text.count(before)==1;text=text.replace(before,"forbidden=('batch03','BATCH03','batch04','BATCH04')")
    before="excluded_future_work=['Wave29 next64 campaign, replacement four-build launcher and GF3 affine witness work.']"
    assert text.count(before)==1;text=text.replace(before,"excluded_future_work=['Batch03 and later allocations are outside the wave29 cutoff.']")
    ast.parse(text);new=ROOT/'acceleration/stage_20261001_twentyninth_evidence.py'
    with new.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    out=ROOT/'acceleration/results/20261001_twentyninth_stager_preparation';out.mkdir(exist_ok=False)
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),predecessor_sha256=h(old),source_sha256=h(new),preparer_sha256=h(Path(__file__)),changes=['Wave29 exact paths, status and report labels.','Later batch03/04 paths excluded; stage only exact independent gate/inventory/supplement entries.'],staging_calls=0,native_calls=0,mathematical_verification=False)
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(source_sha256=h(new),staging_calls=0)))
if __name__=='__main__':main()
