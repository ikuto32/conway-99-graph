"""Restore hash-bound ordered raw-byte chunks without overwriting any file."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(65536),b''):h.update(block)
    return h.hexdigest()


def safe(root,base,name):
    p=Path(name)
    if p.is_absolute() or '..' in p.parts or ':' in str(name):raise ValueError('Unsafe relative path')
    result=(base/p).resolve();result.relative_to(root)
    return result


def restore(manifest_path,root,destination=None):
    manifest_path=Path(manifest_path).resolve();manifest_path.relative_to(root)
    before=digest(manifest_path);data=json.loads(manifest_path.read_bytes())
    if data['schema_version']!=1 or not data['artifacts']:raise ValueError('Expected nonempty schema1 chunks')
    base=manifest_path.parent
    if destination is not None:
        destination=Path(destination).resolve();destination.relative_to(root)
    planned=[];seen=set()
    for artifact in data['artifacts']:
        target=safe(root,destination if destination is not None else base,artifact['source'])
        if target.exists() or str(target).casefold() in seen:raise FileExistsError('Refusing destination overwrite/duplicate: '+str(target))
        seen.add(str(target).casefold())
        if not artifact['parts']:raise ValueError('No parts')
        parts=[];part_seen=set();size=0
        for part in artifact['parts']:
            path=safe(root,base,part['path'])
            if str(path).casefold() in part_seen:raise ValueError('Duplicate source part')
            part_seen.add(str(path).casefold())
            if path.stat().st_size!=part['bytes'] or digest(path)!=part['sha256']:raise ValueError('Part size/hash mismatch')
            size+=part['bytes'];parts.append((path,part))
        if size!=artifact['source_bytes']:raise ValueError('Part sizes do not total source size')
        planned.append((artifact,target,parts))
    records=[]
    for artifact,target,parts in planned:
        target.parent.mkdir(parents=True,exist_ok=True)
        h=hashlib.sha256();size=0
        with tempfile.NamedTemporaryFile(mode='wb',prefix='.chunk-replay-',dir=target.parent,delete=False) as output:
            staging=Path(output.name)
            for path,part in parts:
                ph=hashlib.sha256();pn=0
                with path.open('rb') as source:
                    for block in iter(lambda:source.read(65536),b''):
                        ph.update(block);h.update(block);pn+=len(block);size+=len(block);output.write(block)
                if pn!=part['bytes'] or ph.hexdigest()!=part['sha256']:raise ValueError('Part changed while restoring')
        if size!=artifact['source_bytes'] or h.hexdigest()!=artifact['source_sha256'] or digest(staging)!=artifact['source_sha256']:
            raise ValueError('Whole artifact size/hash mismatch; staging retained, final target not published')
        if digest(manifest_path)!=before:raise ValueError('Manifest changed')
        os.link(staging,target)  # Fails if target was created meanwhile; no rename overwrite.
        staging.unlink()
        records.append(dict(source=artifact['source'],restored_path=target.relative_to(root).as_posix(),
            size_bytes=size,sha256=h.hexdigest(),parts=len(parts),outcome='PASS'))
    return dict(manifest_sha256=before,records=records)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest',type=Path);ap.add_argument('--destination',type=Path)
    ap.add_argument('--report',type=Path,required=True);args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    report=args.report.resolve();report.relative_to(root)
    if report.exists():raise FileExistsError('Fresh report required')
    result=restore(args.manifest,root,args.destination)
    result.update(status='CHUNKED_ARTIFACT_RESTORE_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),python=platform.python_version(),
        inputs_sha256={str(args.manifest):result['manifest_sha256'],
                       'acceleration/restore_chunked_artifacts.py':digest(Path(__file__)),'uv.lock':digest(root/'uv.lock')},
        original_raw_files_consulted=False,originals_overwritten=False,mathematical_verification=False,
        scope='Byte identity of ordered rawpart concatenation only; source_availability metadata is not changed')
    report.parent.mkdir(parents=True,exist_ok=True)
    with report.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=result['status'],records=result['records'])))


if __name__=='__main__':main()
