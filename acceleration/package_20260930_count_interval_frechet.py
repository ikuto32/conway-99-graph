"""Lossless transport only for a preserved failed-formula experiment."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'acceleration/results/20260930_count_interval_frechet_v2/mismatches.json'
RAW_SHA='d16eb34312ad8b6dcb86bf03c02fdb6230cc6d922f44be15ba1befc98ec12bda'
RAW_BYTES=61265344
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:
        assert RAW.stat().st_size==RAW_BYTES and sha(RAW)==RAW_SHA
        packed=out/'mismatches.json.gz'
        with packed.open('xb') as sink:
            with gzip.GzipFile(filename='',mode='wb',fileobj=sink,mtime=0,compresslevel=9) as target:
                with RAW.open('rb') as source:
                    while chunk:=source.read(1024**2):target.write(chunk)
        assert packed.stat().st_size<10*1024**2
        total=0;digest=hashlib.sha256()
        with gzip.open(packed,'rb') as restored,RAW.open('rb') as original:
            while chunk:=restored.read(1024**2):
                assert chunk==original.read(len(chunk));total+=len(chunk);digest.update(chunk)
            assert original.read(1)==b''
        assert total==RAW_BYTES and digest.hexdigest()==RAW_SHA and sha(RAW)==RAW_SHA
        compressed=packed.read_bytes();rejected=[]
        for name,bad in [('truncated',compressed[:-8]),('altered_crc',compressed[:-8]+bytes([compressed[-8]^1])+compressed[-7:])]:
            try:gzip.decompress(bad)
            except (OSError,EOFError):rejected.append(name)
            else:raise ValueError('accepted corrupted gzip '+name)
        report=dict(status='COUNT_INTERVAL_FAILED_FORMULA_BYTE_TRANSPORT_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256={key(RAW):RAW_SHA,key(Path(__file__)):sha(Path(__file__)),'uv.lock':sha(ROOT/'uv.lock'),'pyproject.toml':sha(ROOT/'pyproject.toml')},records=[dict(raw_original_path=key(RAW),raw_bytes=RAW_BYTES,raw_sha256=RAW_SHA,availability='LOCAL_ONLY',availability_reason='Original preserved; exact gzip transport supplied separately.',parts=[dict(index=0,relative_path=packed.name,raw_offset=0,raw_bytes=RAW_BYTES,raw_sha256=RAW_SHA,gzip_bytes=packed.stat().st_size,gzip_sha256=sha(packed))])],literal_full_byte_comparison=True,controls_rejected=rejected,mathematical_verification=False,scope='Exact bytes only; does not verify the producer mismatch count or any formula claim.',new_solver_calls=0)
        save(out/'package_manifest.json',report);print(json.dumps(dict(status=report['status'],raw_bytes=RAW_BYTES,gzip_bytes=packed.stat().st_size,manifest_sha256=sha(out/'package_manifest.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
