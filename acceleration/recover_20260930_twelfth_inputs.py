"""Recover frozen twelfth-wave input packages; never overwrite differing bytes."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
MANIFESTS={
 B+'variable_core_factor_cnf/artifact_packages.json':'46867dcccbb99bd72379b50a7415e6dd1d9d888af8832289d3d054573cad3a1d',
 B+'prism_all_columns/artifact_packages.json':'112a6b94b98ef1f29f0b0691d356018f51697fd39f819b66fa52d8c2e934e55c',
}
def h(data):return hashlib.sha256(data).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination-dir',type=Path);args=ap.parse_args();records=[]
    def write(path,data):
        destination=(args.destination_dir/path if args.destination_dir else ROOT/path).resolve()
        assert destination.is_relative_to(ROOT),'workspace destination required'
        if destination.exists():assert destination.read_bytes()==data,'Refuse to overwrite different bytes: '+str(destination)
        else:
            destination.parent.mkdir(parents=True,exist_ok=True)
            with destination.open('xb')as stream:stream.write(data)
        records.append(dict(path=str(destination),bytes=len(data),sha256=h(data)))
    for name,sha in MANIFESTS.items():
        data=(ROOT/name).read_bytes();assert h(data)==sha
        for package in json.loads(data)['packages']:
            chunks=[]
            for part in package['ordered_parts']:
                chunk=(ROOT/part['path']).read_bytes();assert len(chunk)==part['bytes']and h(chunk)==part['sha256'];chunks.append(chunk)
            stream=b''.join(chunks);assert h(stream)==package['compressed_stream_sha256']
            raw=gzip.decompress(stream);assert len(raw)==package['raw_bytes']and h(raw)==package['raw_sha256']
            write(package['raw_path'],raw)
            if package['raw_path']==B+'prism_all_columns/instance.cnf':
                head,body=raw.split(b'\n',1);assert head==b'p cnf 245880 874800';write(B+'prism_all_columns/clauses.body',body)
    print(json.dumps(dict(status='TWELFTH_RAW_INPUT_RECOVERY_PASS',records=records)))
if __name__=='__main__':main()
