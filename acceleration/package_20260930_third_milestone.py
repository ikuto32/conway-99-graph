"""Preserve exact GPU and ordered-cut recovery records without oversized Git blobs."""
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
from package_20260930_second_milestone import ROOT,B,digest,save
from restore_20260930_rook_cnf import replay

def main():
    out=ROOT/(B+'third_packaging');out.mkdir(exist_ok=False)
    catalog=ROOT/'docs/local-artifacts.json';ignore=ROOT/'.gitignore'
    shutil.copyfile(catalog,out/'local-artifacts.before.json');shutil.copyfile(ignore,out/'gitignore.before.txt')
    data=json.loads(catalog.read_bytes());known={r['path'] for r in data['files']};added=[]
    def append(p,recovery):
        assert p not in known;row=dict(path=p,size_bytes=(ROOT/p).stat().st_size,sha256=digest(ROOT/p),artifact_availability='LOCAL_ONLY',recorded_at=datetime.now(timezone.utc).isoformat(),recovery=recovery)
        data['files'].append(row);known.add(p);added.append(row)
    gpu=B+'eight_moment_pdhg/run02'
    cm=json.loads((ROOT/gpu/'compressed_artifacts.json').read_bytes())
    for r in cm['files']:
        assert digest(ROOT/r['path'])==r['sha256'] and digest(ROOT/r['compressed_path'])==r['compressed_sha256']
        append(r['path'],dict(kind='EXACT_GZIP',manifest=gpu+'/compressed_artifacts.json',companion=r['compressed_path'],restorer='acceleration/restore_compressed_artifacts.py',independent_recovery_audit=B+'independent_review/eight_gpu_support_run02.json'))
        append(r['compressed_path'],dict(kind='EXACT_RAW_BYTE_PARTS',manifest=gpu+'/chunk_manifest.json',restorer='acceleration/restore_chunked_artifacts.py',independent_recovery_audit=B+'independent_review/eight_gpu_support_run02.json'))
    replays=[]
    for folder in sorted((ROOT/(B+'rook_lazy_wave01')).glob('round_*')):
        r=replay(folder);assert digest(ROOT/r['path'])==r['sha256'];replays.append(r)
        append(r['path'],dict(kind='EXACT_BASE_AND_ORDERED_CLAUSES',record=(folder/'instance_record.json').relative_to(ROOT).as_posix(),restorer='acceleration/restore_20260930_rook_cnf.py',command='uv run --locked python acceleration/restore_20260930_rook_cnf.py --round '+folder.relative_to(ROOT).as_posix()+' --out FRESH_OUTPUT_PATH'))
    assert len(replays)==9
    with ignore.open('a',encoding='utf-8') as f:f.write('\n# Third resumed milestone; exact checkpoint parts and ordered CNF reconstruction.\n'+'\n'.join('/'+r['path'] for r in added)+'\n')
    catalog.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    save(out/'summary.json',dict(status='EXACT_THIRD_RECOVERY_CATALOGUED',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),records=added,cnf_reconstruction=replays,source_sha256=digest(Path(__file__)),mathematical_verification=False,originals_preserved=True))
    print(json.dumps(dict(catalogued=len(added),exact_cnf_reconstructions=len(replays))))

if __name__=='__main__':main()
