"""Lossless transport of a raw proof trace; packaging is not proof verification."""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
RAW=B+'hadamard_cyclic_native_pilot/main/proof.drat'
OUT=ROOT/(B+'hadamard_cyclic_proof_packages')


def main():
    data=(ROOT/RAW).read_bytes();digest=hashlib.sha256(data).hexdigest()
    assert digest=='51d67cf0f60365e01a744d2066e0999e944c27a56e3024a73dd5135b000e6ed9'and len(data)==29697087
    OUT.mkdir(parents=True,exist_ok=False);compressed=gzip.compress(data,compresslevel=9,mtime=0)
    assert gzip.decompress(compressed)==data
    parts=[]
    for i,offset in enumerate(range(0,len(compressed),9*1024**2)):
        chunk=compressed[offset:offset+9*1024**2];p=OUT/f'proof.drat.gz.part{i:03d}'
        with p.open('xb')as f:f.write(chunk)
        parts.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(chunk),sha256=hashlib.sha256(chunk).hexdigest()))
    assert gzip.decompress(b''.join((ROOT/p['path']).read_bytes()for p in parts))==data
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        raw_path=RAW,raw_bytes=len(data),raw_sha256=digest,compression='gzip level9,mtime0',parts=parts,
        compressed_bytes=len(compressed),compressed_sha256=hashlib.sha256(compressed).hexdigest(),
        retrieval='Concatenate the ordered parts, gzip-decompress to raw_path, then verify raw_bytes and raw_sha256. Refuse an existing file with different bytes.',
        raw_original_retained=True,recovery_exact_bytes_checked=True,mathematical_verification=False,
        proof_status_at_packaging='Native solver reported UNSAT; complete independent replay is a separate record.',target_resolution='UNKNOWN')
    with(OUT/'artifact_packages.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(raw_bytes=len(data),gzip_bytes=len(compressed),parts=len(parts),exact_recovery=True)))


if __name__=='__main__':main()
