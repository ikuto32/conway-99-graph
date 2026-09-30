"""Exact recovery of new formula and lossless GPU trace packages."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
MANIFESTS={B+'fourteenth_gpu_trace_packages/artifact_packages.json':'7ce95bd15128833fff0f4fc1526fcf43f81625fbcba2c4a36276434a6e9e438f',
           B+'prism_column_caps_v3/artifact_packages.json':'ccee4b2cde1d36df8c58d0b609f0ca330f9b5e814a6958ec4e8b2b6e27fe9042',
           B+'variable_core_pair_orbits/artifact_packages.json':'dd165beb09538e6ab4021c3304bdd5a8358a24dee7e5a13261057eb01ce9fdc4'}
def h(b):return hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination-dir',type=Path);ap.add_argument('--receipt',type=Path);args=ap.parse_args();records=[]
    for name,pin in MANIFESTS.items():
        data=(ROOT/name).read_bytes();assert h(data)==pin
        for package in json.loads(data)['packages']:
            if 'ordered_parts' in package:
                parts=[]
                for item in package['ordered_parts']:
                    chunk=(ROOT/item['path']).read_bytes();assert h(chunk)==item['sha256'] and len(chunk)==item['bytes'];parts.append(chunk)
                compressed=b''.join(parts);assert h(compressed)==package['compressed_stream_sha256']
            else:
                compressed=(ROOT/package['gzip_path']).read_bytes();assert h(compressed)==package['gzip_sha256'] and len(compressed)==package['gzip_bytes']
            raw=gzip.decompress(compressed);assert h(raw)==package['raw_sha256'] and len(raw)==package['raw_bytes']
            relative=Path(package['raw_path']);assert not relative.is_absolute() and '..' not in relative.parts
            destination=((args.destination_dir or ROOT)/relative).resolve();assert destination.is_relative_to(ROOT),'Workspace destination required'
            if destination.exists():assert destination.read_bytes()==raw,'Refuse differing existing bytes: '+str(destination)
            else:
                destination.parent.mkdir(parents=True,exist_ok=True)
                with destination.open('xb') as f:f.write(raw)
            records.append(dict(path=str(destination),bytes=len(raw),sha256=h(raw)))
    report=dict(status='FOURTEENTH_RAW_INPUT_RECOVERY_PASS',records=records,files=len(records),bytes=sum(r['bytes'] for r in records),mathematical_verification=False)
    if args.receipt:
        with args.receipt.open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({k:report[k] for k in ('status','files','bytes','mathematical_verification')}))

if __name__=='__main__':main()
