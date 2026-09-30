"""Recover only the frozen eleventh-wave column-cap clause recipe; never overwrite."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'acceleration/results/20260930_triangle_factor_column_caps'
PACKAGE_SHA = '9b738c22deedbb0d3d752d9f7804555d1b6923ea74a5f94fd78344ee4b3d40cd'
RAW_SHA = '5586d926d48c897d6a7163c93aa0ded2d7a9a5d60e7018056106f0f14805e416'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--destination',type=Path,default=BASE/'clause_recipe.json')
    args=ap.parse_args()
    manifest=(BASE/'artifact_packages.json').read_bytes()
    assert hashlib.sha256(manifest).hexdigest()==PACKAGE_SHA
    packages=json.loads(manifest)['packages']
    package=next(p for p in packages if p['raw_path']==str((BASE/'clause_recipe.json').relative_to(ROOT)).replace('\\','/'))
    assert package['raw_sha256']==RAW_SHA and package['raw_bytes']==12025031
    compressed=[]
    for part in package['ordered_parts']:
        data=(ROOT/part['path']).read_bytes()
        assert len(data)==part['bytes'] and hashlib.sha256(data).hexdigest()==part['sha256']
        compressed.append(data)
    stream=b''.join(compressed)
    assert hashlib.sha256(stream).hexdigest()==package['compressed_stream_sha256']
    raw=gzip.decompress(stream)
    assert len(raw)==package['raw_bytes'] and hashlib.sha256(raw).hexdigest()==RAW_SHA
    destination=args.destination.resolve()
    assert destination.is_relative_to(ROOT)
    if destination.exists():
        assert destination.read_bytes()==raw,'Existing destination differs; refusing overwrite'
        action='EXISTING_EXACT_BYTES_CHECKED'
    else:
        destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open('xb') as handle:handle.write(raw)
        action='RESTORED_FROM_PUBLIC_GZIP'
    print(json.dumps(dict(status='ELEVENTH_RECIPE_RECOVERY_PASS',action=action,path=str(destination),bytes=len(raw),sha256=RAW_SHA)))

if __name__=='__main__':main()
