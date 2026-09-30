"""Lossless public-size transport for a frozen candidate model; no math check."""
from pathlib import Path
from datetime import datetime,timezone
import gzip,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
RAW=B+'hadamard_case0_profile_cnf/model.json';SHA='6705e33a26c332d093e3a2bff6dcd5dca276c6b50da2b24c61c7cbf891e0629c'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def main():
    start=time.monotonic();raw=(ROOT/RAW).read_bytes();assert len(raw)==13208093 and hashlib.sha256(raw).hexdigest()==SHA
    out=ROOT/(B+'hadamard_case0_model_package');out.mkdir(exist_ok=False)
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256={RAW:SHA,Path(__file__).relative_to(ROOT).as_posix():h(__file__),'uv.lock':h(ROOT/'uv.lock'),'pyproject.toml':h(ROOT/'pyproject.toml')},question='Recover exact frozen candidate model bytes from public-size parts.',limits=dict(cooperative_seconds=60,part_bytes=9*1024**2),mathematical_verification=False))
    try:
        compressed=gzip.compress(raw,compresslevel=6,mtime=0);assert time.monotonic()-start<60
        parts=[]
        for i,offset in enumerate(range(0,len(compressed),9*1024**2)):
            p=out/f'model.json.gz.part{i:03d}';blob=compressed[offset:offset+9*1024**2]
            with p.open('xb')as f:f.write(blob)
            parts.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(blob),sha256=h(p)))
        restored=gzip.decompress(b''.join((ROOT/p['path']).read_bytes()for p in parts))
        assert restored==raw and h(ROOT/RAW)==SHA
        save(out/'artifact_packages.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),raw_path=RAW,raw_sha256=SHA,raw_bytes=len(raw),compressed_bytes=len(compressed),compressed_sha256=hashlib.sha256(compressed).hexdigest(),parts=parts,compression='gzip level6 mtime0; concatenate ordered parts before decompression',raw_original_retained=True,producer_recovery_identity_checked=True,independent_verification=False,mathematical_verification=False,scope='Artifact identity only. No encoding or satisfiability approval.',retrieval='Concatenate ordered parts, gzip-decompress to a fresh file, verify raw size/hash; never overwrite different bytes.',elapsed_seconds=time.monotonic()-start))
        print(json.dumps(dict(raw_bytes=len(raw),compressed_bytes=len(compressed),parts=len(parts))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error)));raise
if __name__=='__main__':main()

