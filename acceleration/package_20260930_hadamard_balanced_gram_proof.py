"""Lossless chunked transport of the checked restricted proof; no proof replay."""
from pathlib import Path
from datetime import datetime,timezone
import gzip,hashlib,json,platform,shutil,subprocess,sys,time,zlib
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
RAW=B+'hadamard_balanced_gram_native_pilot/main/proof.drat'
SHA='94d2ab35c76b61f3deb01ebfd9ca0dc70452bddf847383d5838b2b2ca902396b'
SIZE=227098316
OUT=ROOT/(B+'hadamard_balanced_gram_proof_packages')
GATE=B+'independent_review/hadamard_balanced_gram_unsat_v2/summary.json'
GATE_SHA='edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5'
def sha(path):
    with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,obj):
    with Path(path).open('x',encoding='utf8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
class Writer:
    def __init__(self):self.buffer=bytearray();self.parts=[];self.digest=hashlib.sha256();self.count=0
    def write(self,data):
        self.digest.update(data);self.count+=len(data);self.buffer.extend(data)
        while len(self.buffer)>=9*1024**2:self.part(9*1024**2)
        return len(data)
    def flush(self):pass
    def part(self,n):
        p=OUT/f'proof.drat.gz.part{len(self.parts):03d}';blob=bytes(self.buffer[:n]);del self.buffer[:n]
        with p.open('xb')as f:f.write(blob)
        self.parts.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=n,sha256=hashlib.sha256(blob).hexdigest()))
        save(OUT/f'checkpoint_{len(self.parts):03d}.json',dict(completed_parts=self.parts.copy(),complete_stream=False))
def main():
    assert sha(ROOT/RAW)==SHA and(ROOT/RAW).stat().st_size==SIZE
    assert sha(ROOT/GATE)==GATE_SHA
    assert shutil.disk_usage(ROOT).free>=1024**3
    OUT.mkdir(exist_ok=False);started=time.monotonic();w=Writer()
    save(OUT/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256={RAW:SHA,GATE:GATE_SHA,Path(__file__).relative_to(ROOT).as_posix():sha(__file__),'uv.lock':sha(ROOT/'uv.lock'),'pyproject.toml':sha(ROOT/'pyproject.toml')},question='Preserve exact proof bytes as public-size chunks.',limits=dict(cooperative_seconds=180,part_bytes=9*1024**2),compression='gzip level6,mtime0,empty filename',proof_replays=0))
    try:
        with(ROOT/RAW).open('rb')as source,gzip.GzipFile(fileobj=w,filename='',mode='wb',mtime=0,compresslevel=6)as stream,tqdm(total=SIZE,unit='B',unit_scale=True,desc='Proof transport')as progress:
            for block in iter(lambda:source.read(1048576),b''):
                stream.write(block);progress.update(len(block));assert time.monotonic()-started<180,'cooperative packaging limit'
        if w.buffer:w.part(len(w.buffer))
        recovered=hashlib.sha256();count=0;decoder=zlib.decompressobj(31)
        for part in w.parts:
            assert sha(ROOT/part['path'])==part['sha256']
            with(ROOT/part['path']).open('rb')as f:
                for chunk in iter(lambda:f.read(1048576),b''):
                    raw=decoder.decompress(chunk);recovered.update(raw);count+=len(raw)
        tail=decoder.flush();recovered.update(tail);count+=len(tail)
        assert decoder.eof and not decoder.unused_data and count==SIZE and recovered.hexdigest()==SHA
        assert sha(ROOT/RAW)==SHA
        save(OUT/'artifact_packages.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),raw_path=RAW,raw_bytes=SIZE,raw_sha256=SHA,compression='gzip level6,mtime0; concatenate ordered parts before decompression',parts=w.parts,compressed_bytes=w.count,compressed_sha256=w.digest.hexdigest(),raw_original_retained=True,recovery_exact_bytes_checked=True,mathematical_verification=False,proof_status_at_packaging='Separate independent complete proof replay PASS for the exact balanced fixed-support family; no unrestricted target exclusion.',independent_proof_gate=dict(path=GATE,sha256=GATE_SHA),retrieval='Concatenate ordered parts, gzip-decompress to a fresh file, verify raw size and SHA256 before proof replay. Never overwrite different bytes.',elapsed_seconds=time.monotonic()-started,target_resolution='UNKNOWN'))
        print(json.dumps(dict(raw_bytes=SIZE,compressed_bytes=w.count,parts=len(w.parts),exact_recovery=True)))
    except BaseException as error:save(OUT/'failure.json',dict(error=repr(error),completed_parts=w.parts,raw_original_retained=True));raise
if __name__=='__main__':main()
