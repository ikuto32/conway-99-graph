"""Catalog large originals and verify their exact existing recovery companions."""
from datetime import datetime,timezone
from hashlib import sha256
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
def digest(p):
    h=sha256()
    with p.open('rb') as f:
        while block:=f.read(1<<20):h.update(block)
    return h.hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2);f.write('\n')
def main():
    out=ROOT/(B+'second_packaging');out.mkdir(exist_ok=False)
    catalog=ROOT/'docs/local-artifacts.json';ignore=ROOT/'.gitignore'
    shutil.copyfile(catalog,out/'local-artifacts.before.json');shutil.copyfile(ignore,out/'gitignore.before.txt')
    data=json.loads(catalog.read_bytes());known={r['path']:r for r in data['files']};records=[];gzipfiles=[]
    def append(p,recovery):
        row=dict(path=p,size_bytes=(ROOT/p).stat().st_size,sha256=digest(ROOT/p),artifact_availability='LOCAL_ONLY',recorded_at=datetime.now(timezone.utc).isoformat(),recovery=recovery)
        assert p not in known;data['files'].append(row);known[p]=row;records.append(row)
    for p in [B+'rook_window_sat/instance.cnf',B+'rook_free_internal_sat/instance.cnf',B+'rook_sat_pilot/main/proof.drat']:
        source=ROOT/p;z=ROOT/(p+'.gz');h=sha256();n=0
        with gzip.open(z,'rb') as f:
            while block:=f.read(1<<20):h.update(block);n+=len(block)
        assert n==source.stat().st_size and h.hexdigest()==digest(source)
        gzipfiles.append(dict(path=p,size_bytes=n,sha256=h.hexdigest(),compressed_path=p+'.gz',compressed_size_bytes=z.stat().st_size,compressed_sha256=digest(z)))
        append(p,dict(kind='EXACT_GZIP',manifest=B+'second_packaging/compressed_artifacts.json',companion=p+'.gz',restorer='acceleration/restore_compressed_artifacts.py'))
    save(out/'compressed_artifacts.json',dict(schema_version=1,encoding='gzip; exact byte recovery',files=gzipfiles))
    chunkpath=B+'eight_filtered_moments/run01/chunk_manifest.json';chunks=json.loads((ROOT/chunkpath).read_bytes())
    for r in chunks['artifacts']:
        base=(ROOT/chunkpath).parent;h=sha256();n=0
        for part in r['parts']:
            p=base/part['path'];assert digest(p)==part['sha256'] and p.stat().st_size==part['bytes']
            with p.open('rb') as f:
                while block:=f.read(1<<20):h.update(block);n+=len(block)
        source=base/r['source'];assert n==r['source_bytes']==source.stat().st_size and h.hexdigest()==r['source_sha256']==digest(source)
        append(source.relative_to(ROOT).as_posix(),dict(kind='EXACT_RAW_BYTE_PARTS',manifest=chunkpath,restorer='acceleration/restore_chunked_artifacts.py'))
    manifest=B+'eight_moment_pdhg/export/manifest.json';m=json.loads((ROOT/manifest).read_bytes())
    assert digest(ROOT/m['binary_path'])==m['binary_sha256']
    append(m['binary_path'],dict(kind='DETERMINISTIC_REGENERATION',manifest=manifest,source='acceleration/export_20260930_eight_moment_pdhg.py',
        command='uv run --locked python acceleration/export_20260930_eight_moment_pdhg.py --out FRESH_EXPORT_DIRECTORY --binary FRESH_BINARY_PATH',
        caveat='Restore exact model chunks and raw filter gzip first. Compare binary SHA256. Export performs no numerical search. Native binaries require separate documented compilation.'))
    with ignore.open('a',encoding='utf-8') as f:f.write('\n# Second resumed milestone; originals recover from exact companions.\n'+'\n'.join('/'+r['path'] for r in records)+'\n')
    catalog.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    save(out/'summary.json',dict(status='EXACT_RECOVERY_COMPANIONS_CATALOGUED',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),records=records,source_sha256=digest(Path(__file__)),mathematical_verification=False,originals_preserved=True))
    print(json.dumps(dict(records=len(records),gzip_roundtrips=len(gzipfiles),chunk_roundtrips=len(chunks['artifacts']))))

if __name__=='__main__':main()
