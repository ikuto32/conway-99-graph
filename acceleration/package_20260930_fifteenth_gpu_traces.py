"""Losslessly package exact completed connected-portfolio trace and checkpoint JSONs."""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import json
import platform
import re
import subprocess
import sys
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
INPUTS={B+'connected_core_portfolio_pilot/summary.json':'7ad597591aa3f52120d2d1c4cb2646378007a2e11875296666f832f4b6c303a6'}

def sha(b):return hashlib.sha256(b).hexdigest()
def relative(p):return p.relative_to(ROOT).as_posix()

def main():
    selected=[]
    for name,pin in INPUTS.items():
        p=ROOT/name;assert sha(p.read_bytes())==pin
        selected.extend(q for q in p.parent.rglob('*.json') if re.fullmatch(r'(?:chunk|checkpoint)_\d{5}\.json',q.name))
    selected=sorted(selected);assert len(selected)==192
    out=ROOT/(B+'fifteenth_gpu_trace_packages');out.mkdir(parents=True,exist_ok=False);packages=[]
    for index,p in enumerate(tqdm(selected,desc='Packaging frozen GPU traces')):
        raw=p.read_bytes();compressed=gzip.compress(raw,mtime=0);assert gzip.decompress(compressed)==raw
        part=out/f'raw_{index:03d}.json.gz';assert len(compressed)<10*1024**2
        with part.open('xb') as f:f.write(compressed)
        packages.append(dict(raw_path=relative(p),raw_sha256=sha(raw),raw_bytes=len(raw),compression='gzip, mtime=0',
            compressed_stream_sha256=sha(compressed),ordered_parts=[dict(path=relative(part),bytes=len(compressed),sha256=sha(compressed))],
            availability='LOCAL_ONLY_RAW_WITH_PUBLIC_RECOVERY_PENDING',producer_decompression_identity_passed=True))
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256={**INPUTS,relative(Path(__file__).resolve()):sha(Path(__file__).read_bytes())},
        selection_rule='Exactly chunk_NNNNN.json and checkpoint_NNNNN.json under the pinned completed four-core portfolio directory; receipts and raw best matrices excluded.',
        packages=packages,raw_files=len(packages),raw_bytes=sum(x['raw_bytes'] for x in packages),compressed_bytes=sum(x['ordered_parts'][0]['bytes'] for x in packages),
        mathematical_reverification_performed=False,original_files_unchanged=True,public_publication_confirmed=False)
    with (out/'artifact_packages.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({k:report[k] for k in ['raw_files','raw_bytes','compressed_bytes']}|{'manifest_sha256':sha((out/'artifact_packages.json').read_bytes())}))

if __name__=='__main__':main()
