"""Preserve the exact inventoried guide and bind its later recovery instructions."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';GUIDE='docs/REPRODUCING_20260930_TWENTYEIGHTH_WAVE.md';INV=B+'twentyeighth_candidate_inventory/inventory.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    raw=(ROOT/GUIDE).read_bytes();needhash='95b76d5f21e15d90ebc036a36e7f47eabaec91c548015a42ebf0f56d87ecd779';assert sha(raw)==needhash
    start=raw.index(b'Forty-seven oversized raw models');end=raw.index(b'The [authenticated replay plan]',start);addition=raw[start:end];before=raw[:start]+raw[end:]
    invraw=(ROOT/INV).read_bytes();assert sha(invraw)=='0057d4f0101eb1e56516ade234840defb4be5b17d2b0a2b5e35bd85491b48ce1';inv=json.loads(invraw);entries=[r for r in inv['entries']if r['path']==GUIDE];assert len(entries)==1;old=entries[0]
    assert sha(before)==old['sha256']=='db2f23d9830708be66c9012001d5b82862a8dc59c96fc4e6aaed415274e43651'and len(before)==old['bytes']==5669
    out=ROOT/(B+'twentyeighth_guide_update');out.mkdir(exist_ok=False)
    for name,content in[('previous_guide.md',before),('recovery_addition.md',addition),('final_guide.md',raw)]:
        with(out/name).open('xb')as f:f.write(content)
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),recorder_sha256=sha(Path(__file__).read_bytes()),inventory_path=INV,inventory_sha256=sha(invraw),path=GUIDE,old_sha256=sha(before),old_bytes=len(before),new_sha256=sha(raw),new_bytes=len(raw),previous_exact_bytes_recovered=True,recovery_method='Remove the one newly added recovery-instructions paragraph/command block, then require exact original inventory SHA256 and length.',change='Append actual47-file compressed recovery command, manifest hash, byte count and successful fresh/corrupt control references; no scientific scope or claim changes.',outputs_sha256={(out/name).relative_to(ROOT).as_posix():sha((out/name).read_bytes())for name in['previous_guide.md','recovery_addition.md','final_guide.md']},scientific_entry_overrides=0,metadata_entry_overrides=1)
    with(out/'receipt.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(receipt_sha256=sha((out/'receipt.json').read_bytes()),old_sha256=sha(before),new_sha256=sha(raw))))
if __name__=='__main__':main()
