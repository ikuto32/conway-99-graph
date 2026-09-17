"""Generic gzip companion audit using the frozen independent zlib decoder."""
import argparse
from datetime import datetime,timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import zlib
from audit_compressed_artifacts import decode,sha,safe_relative


def controls(root):
    raw=b'generic independent artifact recovery\n'*3
    good=gzip.compress(raw,mtime=0);h=hashlib.sha256(raw).hexdigest()
    assert decode([good[:7],good[7:]],lambda _:None,len(raw),h)==(len(raw),h)
    results=[dict(name='positive_split_stream',outcome='PASS')]
    damaged=bytearray(good);damaged[-8]^=1
    for name,blob,size,digest in [('crc',bytes(damaged),len(raw),h),('truncation',good[:-1],len(raw),h),
        ('size',good,len(raw)+1,h),('hash',good,len(raw),'0'*64),('trailing',good+b'x',len(raw),h),
        ('second_member',good+good,len(raw)*2,hashlib.sha256(raw+raw).hexdigest())]:
        try:decode([blob],lambda _:None,size,digest)
        except (ValueError,zlib.error):results.append(dict(name=name,outcome='REJECT'))
        else:raise ValueError('Corrupt control accepted: '+name)
    for name in ('../escape','C:/escape','x:y'):
        try:safe_relative(root,name)
        except ValueError:results.append(dict(name='path:'+name,outcome='REJECT'))
        else:raise ValueError('Unsafe path accepted')
    return results


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest',type=Path);ap.add_argument('--destination',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    manifest=args.manifest.resolve();manifest.relative_to(root)
    destination=args.destination.resolve();destination.relative_to(root)
    report_path=args.out.resolve();report_path.relative_to(root)
    if destination.exists() or report_path.exists():raise ValueError('Fresh destination/report required')
    original_hash=sha(manifest);data=json.loads(manifest.read_bytes())
    if data['schema_version']!=1 or not data['files']:raise ValueError('Expected nonempty schema1 companionmanifest')
    seen=set();validated=[]
    for row in data['files']:
        source=safe_relative(root,row['compressed_path']);target=safe_relative(destination,row['path'])
        identity=str(target).casefold()
        if identity in seen:raise ValueError('Duplicate destination')
        seen.add(identity)
        if source.stat().st_size!=row['compressed_size_bytes'] or sha(source)!=row['compressed_sha256']:
            raise ValueError('Compressed source size/hash mismatch')
        validated.append((row,source,target))
    checks=controls(root);destination.mkdir(parents=True)
    records=[]
    for row,source,target in validated:
        target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='wb',prefix='.replay-',dir=target.parent,delete=False) as output:
            staging=Path(output.name)
            with source.open('rb') as stream:
                size,h=decode(iter(lambda:stream.read(65536),b''),output.write,row['size_bytes'],row['sha256'])
        if sha(staging)!=h or sha(source)!=row['compressed_sha256']:raise ValueError('Recovery/input changed')
        os.link(staging,target)  # Atomic exclusive publication; refuses an existing target.
        staging.unlink()
        records.append(dict(path=row['path'],compressed_path=row['compressed_path'],compressed_sha256=row['compressed_sha256'],
                            recovered_path=target.relative_to(root).as_posix(),recovered_sha256=h,recovered_size_bytes=size,outcome='PASS'))
    if sha(manifest)!=original_hash:raise ValueError('Manifest changed')
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='INDEPENDENT_GENERIC_GZIP_MANIFEST_RECOVERY_PASS',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),python=platform.python_version(),zlib_runtime=zlib.ZLIB_RUNTIME_VERSION,
        files=len(records),total_recovered_bytes=sum(x['recovered_size_bytes'] for x in records),records=records,controls=checks,
        inputs_sha256={manifest.relative_to(root).as_posix():original_hash,
                       'acceleration/audit_compressed_artifact_manifest.py':sha(Path(__file__)),
                       'acceleration/audit_compressed_artifacts.py':sha(root/'acceleration/audit_compressed_artifacts.py'),
                       'uv.lock':sha(root/'uv.lock')},
        shared_components=['Frozen independent streaming zlib decoder and path helper','Python zlib and hashlib'],
        producer_restore_imported=False,original_raw_files_consulted=False,originals_overwritten=False,
        limitations=['Engineering byte-recovery check only','Local companion bytes checked; networkpublication not tested',
                     'Uses the same frozen decoder as historical independentaudit, so not a new independent decoder'],
        mathematical_claim_promotion=False,target_resolution=False)
    report_path.parent.mkdir(parents=True,exist_ok=True)
    with report_path.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=report['status'],files=len(records),bytes=report['total_recovered_bytes'],report=str(args.out))))


if __name__=='__main__':main()
