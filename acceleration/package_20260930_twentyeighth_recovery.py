"""Normalize the authenticated oversized wave28 originals without changing them."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gzip,hashlib,json,subprocess,sys
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';OUT=B+'twentyeighth_raw_recovery';LIMIT=10*1024**2;RAW_CHUNK=8*1024**2
FORBIDDEN='acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log'
def safe(p):
    q=(ROOT/p).resolve();assert q.is_relative_to(ROOT)and q.relative_to(ROOT).as_posix()==p
    assert not p.startswith('tools/')and p not in['PROMPT.md',FORBIDDEN];return q
def sha(p):
    with safe(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(safe(p).read_bytes())
def save(p,x):
    with safe(p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def packages():
    m=read(OUT+'/manifest.json');assert m['schema']=='WAVE28_NORMALIZED_RAW_RECOVERY_V1';return m['records']
def stream_identity(r):
    whole=hashlib.sha256();total=0
    with safe(r['path']).open('rb')as original:
        for p in r['parts']:
            assert p['raw_offset']==total and sha(p['path'])==p['gzip_sha256']and safe(p['path']).stat().st_size==p['gzip_bytes']<=LIMIT;hh=hashlib.sha256();n=0
            with gzip.open(safe(p['path']),'rb')as f:
                for block in iter(lambda:f.read(1048576),b''):assert original.read(len(block))==block;whole.update(block);hh.update(block);n+=len(block)
            assert n==p['raw_bytes']and hh.hexdigest()==p['raw_sha256'];total+=n
        assert not original.read(1)
    assert total==r['bytes']and whole.hexdigest()==r['sha256'];return dict(path=r['path'],sha256=whole.hexdigest(),bytes=total,gzip_parts=len(r['parts']),literal_original_comparison=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inventory',required=True);ap.add_argument('--inventory-sha256',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    assert args.out==OUT and sha(args.inventory)==args.inventory_sha256
    inventory=read(args.inventory);assert not inventory['pending']and not inventory['hash_mismatches'];large=inventory['oversized_raw_or_payload_files'];assert large and len({r['path']for r in large})==len(large)
    safe(OUT).mkdir(exist_ok=False);rows=[];bindings={args.inventory:args.inventory_sha256}
    for index,item in enumerate(tqdm(large,desc='Package wave28 raw artifacts',mininterval=1)):
        raw=item['path'];digest=item['sha256'];length=item['bytes'];assert sha(raw)==digest and safe(raw).stat().st_size==length
        matches=[x for x in item.get('package_records',[])if x['raw_sha256']==digest and x['raw_bytes']==length];parts=[];mp=None
        if matches:
            mp=sorted({x['manifest_path']for x in matches})[0];m=read(mp);bindings[mp]=sha(mp)
            assert m['raw_path']==raw and m['raw_sha256']==digest and m['raw_bytes']==length
            if m['gzip_bytes']<=LIMIT:
                assert sha(m['gzip_path'])==m['gzip_sha256']and safe(m['gzip_path']).stat().st_size==m['gzip_bytes']
                parts=[dict(path=m['gzip_path'],gzip_sha256=m['gzip_sha256'],gzip_bytes=m['gzip_bytes'],raw_offset=0,raw_sha256=digest,raw_bytes=length)]
        if not parts:
            offset=0
            with safe(raw).open('rb')as f:
                for j,block in enumerate(iter(lambda:f.read(RAW_CHUNK),b'')):
                    gp=OUT+f'/raw_{index:04d}.part{j:04d}.gz'
                    with safe(gp).open('xb')as compressed:
                        with gzip.GzipFile(filename='',mode='wb',fileobj=compressed,mtime=0,compresslevel=9)as g:g.write(block)
                    n=safe(gp).stat().st_size;assert n<=LIMIT;parts.append(dict(path=gp,gzip_sha256=sha(gp),gzip_bytes=n,raw_offset=offset,raw_sha256=hashlib.sha256(block).hexdigest(),raw_bytes=len(block)));offset+=len(block)
            assert offset==length
        rows.append(dict(path=raw,sha256=digest,bytes=length,manifest=mp,manifest_null_reason='New direct compressed parts; raw identity is pinned by inventory.'if mp is None else None,parts=parts))
    controls=[stream_identity(r)for r in tqdm(rows,desc='Compare every recovered byte',mininterval=1)]
    for p in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md')]:q=p.relative_to(ROOT).as_posix();bindings[q]=sha(q)
    save(OUT+'/manifest.json',dict(schema='WAVE28_NORMALIZED_RAW_RECOVERY_V1',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),records=rows,inputs_sha256=bindings,raw_artifacts=len(rows),raw_bytes=sum(r['bytes']for r in rows),gzip_parts=sum(len(r['parts'])for r in rows),prior_recovery_catalog=dict(path=B+'twentyseventh_artifact_packaging/catalog.json',sha256='fd10bd3872a7699f7ea80e1072c697b300cdb9d0cf7cdb19dd1a0c898e6565a8'),stream_controls=controls,byte_recovery_performed_by_this_normalizer=True,mathematical_verification=False))
    print(json.dumps(dict(manifest_sha256=sha(OUT+'/manifest.json'),raw_artifacts=len(rows),raw_bytes=sum(r['bytes']for r in rows),gzip_parts=sum(len(r['parts'])for r in rows))))
if __name__=='__main__':main()
