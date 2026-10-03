"""Recover four exact oversized sixteenth-wave artifacts; no proof checking."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
MANIFESTS={B+'sixteenth_raw_packages/artifact_packages.json':'6b79058f45b416dbc8d33896470824e6511ad0dd937e17ab5f402d048169aeeb',
           B+'fixed_support_connected01_cnf/artifact_packages.json':'38e713b4ce8eafd6ac428ba38cdf1bbdda0a8e9348b8b8409dfecf98d538ff52'}

def h(data):return hashlib.sha256(data).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination-dir',type=Path);ap.add_argument('--receipt',type=Path);args=ap.parse_args();records=[]
    for name,pin in MANIFESTS.items():
        data=(ROOT/name).read_bytes();assert h(data)==pin
        for package in json.loads(data)['packages']:
            parts=[]
            for item in package['ordered_parts']:
                chunk=(ROOT/item['path']).read_bytes();assert h(chunk)==item['sha256'] and len(chunk)==item['bytes'];parts.append(chunk)
            compressed=b''.join(parts);assert h(compressed)==package['compressed_stream_sha256']
            raw=gzip.decompress(compressed);assert h(raw)==package['raw_sha256'] and len(raw)==package['raw_bytes']
            relative=Path(package['raw_path']);assert not relative.is_absolute() and '..' not in relative.parts
            destination=((args.destination_dir or ROOT)/relative).resolve();assert destination.is_relative_to(ROOT)
            if destination.exists():assert destination.read_bytes()==raw,'Refuse overwriting different artifact bytes'
            else:
                destination.parent.mkdir(parents=True,exist_ok=True)
                with destination.open('xb') as f:f.write(raw)
            records.append(dict(path=str(destination),bytes=len(raw),sha256=h(raw)))
    result=dict(status='SIXTEENTH_RAW_INPUT_RECOVERY_PASS',records=records,files=len(records),bytes=sum(r['bytes'] for r in records),mathematical_verification=False)
    if args.receipt:
        with args.receipt.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:result[k] for k in ['status','files','bytes','mathematical_verification']}))

if __name__=='__main__':main()
