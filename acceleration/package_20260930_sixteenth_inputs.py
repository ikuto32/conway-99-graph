"""Lossless packaging of oversized coefficient-simplification trial evidence."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse
import gzip
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
RAW='acceleration/results/20260930_farkas_compress/trials.json'

def h(data):return sha256(data).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();assert out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    raw=(ROOT/RAW).read_bytes();compressed=gzip.compress(raw,mtime=0);parts=[]
    for offset in range(0,len(compressed),9*1024**2):
        p=out/f'trials.json.gz.part{len(parts):03d}';chunk=compressed[offset:offset+9*1024**2];p.write_bytes(chunk)
        parts.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=h(chunk),bytes=len(chunk)))
    assert gzip.decompress(compressed)==raw
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),inputs_sha256={RAW:h(raw),Path(__file__).resolve().relative_to(ROOT).as_posix():h(Path(__file__).read_bytes())},
        packages=[dict(raw_path=RAW,raw_sha256=h(raw),raw_bytes=len(raw),compressed_stream_sha256=h(compressed),ordered_parts=parts)],
        raw_original_retained=True,mathematical_verification=False)
    with (out/'artifact_packages.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(raw_bytes=len(raw),gzip_bytes=len(compressed),manifest_sha256=h((out/'artifact_packages.json').read_bytes()))))

if __name__=='__main__':main()
