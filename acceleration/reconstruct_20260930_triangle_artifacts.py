"""Restore only the two prescribed triangle packages, without overwriting conflicts."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import gzip
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
PREFIX='acceleration/results/'
SPECS={
 '20260930_triangle_full99_cnf':dict(package_sha256='53ac60da634afa446c3fe3fc8f51f0c02699ef562aa6639b10250040bd56380c',header=b'p cnf 429476 1486729\n',body_sha256='a8316f7a82ef744de40065eedcf403e9e900969993dcc147df49e34282d3ac38',body_bytes=28948861),
 '20260930_triangle_wave151_full99_cnf':dict(package_sha256='fbd805f357fac21e6e6e77548915d61a69d990d86786f3df0d40e86752b4ec48',header=b'p cnf 429779 1487778\n',body_sha256='5b28fa5240a96cea714bfb4fcf942174f5bac9ed8a803409a5bc7ccd0c0ec7f0',body_bytes=28968469),
}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def digest(p):
    h=sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def save(p,obj):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def safe_target(root,name,allowed):
    need(name in allowed,'raw path is not one of the exact prescribed paths')
    need(not PurePosixPath(name).is_absolute()and'..'not in PurePosixPath(name).parts and'\\'not in name,'strict repository-relative path')
    root=Path(root).resolve();p=root/name
    need(p.resolve().is_relative_to(root),'resolved output leaves requested root')
    return p
def packages(name):
    p=ROOT/PREFIX/name/'artifact_packages.json';need(digest(p)==SPECS[name]['package_sha256'],'exact package metadata hash')
    obj=json.loads(p.read_bytes());records=obj['packages']
    need({r['raw_path']for r in records}=={PREFIX+name+'/instance.cnf',PREFIX+name+'/model.json'}and len(records)==2,'exact two raw package paths')
    return records
class Parts(io.RawIOBase):
    def __init__(self,paths):self.paths=iter(paths);self.current=None
    def readable(self):return True
    def readinto(self,buf):
        while True:
            if self.current is None:
                try:self.current=next(self.paths).open('rb')
                except StopIteration:return 0
            n=self.current.readinto(buf)
            if n:return n
            self.current.close();self.current=None
    def close(self):
        if self.current is not None:self.current.close()
        super().close()
def validate_existing(p,sha,size):
    need(p.is_file()and p.stat().st_size==size and digest(p)==sha,'existing output differs; overwrite refused '+str(p))
def publish_stream(target,reader,sha,size):
    if target.exists():
        validate_existing(target,sha,size);return 'EXISTING_IDENTICAL'
    target.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.triangle-recovery-',dir=target.parent);tmp=Path(tmp)
    try:
        h=sha256();count=0
        with os.fdopen(fd,'wb')as f:
            for block in iter(lambda:reader.read(1<<20),b''):f.write(block);h.update(block);count+=len(block)
        need(h.hexdigest()==sha and count==size,'decoded raw hash/size mismatch')
        try:os.link(tmp,target)
        except FileExistsError:validate_existing(target,sha,size)
        validate_existing(target,sha,size)
    finally:
        # Only the exact temporary file created above is removed; never a user output.
        if tmp.exists():tmp.unlink()
    return 'RESTORED_VERIFIED'
def restore(name,record,out_root,source_root=ROOT):
    allowed={PREFIX+name+'/instance.cnf',PREFIX+name+'/model.json'}
    target=safe_target(out_root,record['raw_path'],allowed);paths=[];compressed=sha256()
    for i,part in enumerate(record['ordered_parts']):
        expected=record['raw_path']+'.gz.part'+str(i).zfill(3)
        need(part['path']==expected,'exact ordered part path')
        p=safe_target(source_root,part['path'],{expected});need(p.stat().st_size==part['bytes']and digest(p)==part['sha256'],'part byte/hash mismatch')
        paths.append(p)
        with p.open('rb')as f:
            for b in iter(lambda:f.read(1<<20),b''):compressed.update(b)
    need(paths and compressed.hexdigest()==record['compressed_stream_sha256'],'complete compressed stream hash')
    with io.BufferedReader(Parts(paths))as joined:
        with gzip.GzipFile(fileobj=joined,mode='rb')as raw:
            status=publish_stream(target,raw,record['raw_sha256'],record['raw_bytes'])
    return dict(path=record['raw_path'],output=str(target.resolve()),sha256=digest(target),bytes=target.stat().st_size,status=status)
def body(name,cnf_record,out_root):
    source=safe_target(out_root,cnf_record['raw_path'],{PREFIX+name+'/instance.cnf'})
    validate_existing(source,cnf_record['raw_sha256'],cnf_record['raw_bytes'])
    target=safe_target(out_root,PREFIX+name+'/clauses.body',{PREFIX+name+'/clauses.body'})
    with source.open('rb')as f:
        need(f.readline()==SPECS[name]['header'],'exact LF header for body recovery')
        status=publish_stream(target,f,SPECS[name]['body_sha256'],SPECS[name]['body_bytes'])
    return dict(path=PREFIX+name+'/clauses.body',output=str(target.resolve()),sha256=digest(target),bytes=target.stat().st_size,status=status,recipe='Remove exactly the first LF header line from the authenticated recovered CNF.')
def recover(names,out_root,include_bodies):
    records=[]
    for name in names:
        pkg=packages(name)
        for row in pkg:records.append(restore(name,row,out_root))
        if include_bodies:records.append(body(name,next(r for r in pkg if r['raw_path'].endswith('/instance.cnf')),out_root))
    return records
def calibrate(out):
    out.mkdir(parents=True,exist_ok=False);scratch=ROOT/'build/seventh-triangle-recovery-controls'
    need(not scratch.exists(),'fresh-path control destination already exists')
    records=recover(list(SPECS),scratch/'fresh',True)
    need(len(records)==6 and all(r['status']=='RESTORED_VERIFIED'for r in records),'six fresh raw recoveries')
    repeated=recover(list(SPECS),scratch/'fresh',True)
    need(all(r['status']=='EXISTING_IDENTICAL'for r in repeated),'idempotent matching outputs')
    name=next(iter(SPECS));record=packages(name)[0];rejected=[]
    def reject(label,fn):
        try:fn()
        except(ValueError,OSError)as exc:rejected.append(dict(case=label,error=str(exc)))
        else:raise AssertionError(label+' was accepted')
    changed=deepcopy(record);changed['raw_sha256']='0'*64
    reject('changed_raw_hash',lambda:restore(name,changed,scratch/'changed_hash'))
    changed=deepcopy(record);changed['ordered_parts'][0]['sha256']='0'*64
    reject('changed_part_hash',lambda:restore(name,changed,scratch/'changed_part_hash'))
    changed=deepcopy(record);changed['raw_path']='../escape.cnf'
    reject('escape_path',lambda:restore(name,changed,scratch/'escape'))
    changed=deepcopy(record);changed['raw_path']=PREFIX+name+'/unexpected.cnf'
    reject('unexpected_raw_name',lambda:restore(name,changed,scratch/'wrong_name'))
    conflict=safe_target(scratch/'conflict',record['raw_path'],{record['raw_path']});conflict.parent.mkdir(parents=True,exist_ok=True);conflict.write_bytes(b'USER-EXISTING-CONTROL\n');before=digest(conflict)
    reject('existing_conflicting_output',lambda:restore(name,record,scratch/'conflict'))
    need(digest(conflict)==before,'conflicting existing file unchanged')
    part=record['ordered_parts'][0];changed_part=safe_target(scratch/'part_source',part['path'],{part['path']});changed_part.parent.mkdir(parents=True,exist_ok=True)
    data=(ROOT/part['path']).read_bytes();changed_part.write_bytes(bytes([data[0]^1])+data[1:])
    reject('changed_part_bytes',lambda:restore(name,record,scratch/'changed_part_bytes',scratch/'part_source'))
    report=dict(status='EXACT_TRIANGLE_RECONSTRUCTION_CONTROLS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=digest(Path(__file__)),uv_lock_sha256=digest(ROOT/'uv.lock'),fresh_recoveries=records,identical_existing_outputs_accepted=len(repeated),corruptions_rejected=rejected,conflicting_existing_file_preserved=True,source_inputs_modified=False,shared_gitignore_modified=False,ledger_modified=False,mathematical_verification=False,limitations=['Engineering byte recovery only; no mathematical or solver claim.','Fresh raw control copies are LOCAL_ONLY beneath build/; the public inputs remain the original small gzip parts.'])
    save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True)
    c=sub.add_parser('calibrate');c.add_argument('--out',type=Path,required=True)
    r=sub.add_parser('recover');r.add_argument('--packages',type=Path,action='append');r.add_argument('--out-root',type=Path,default=ROOT);r.add_argument('--include-bodies',action='store_true');r.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='calibrate':calibrate(args.out);return
    names=list(SPECS)
    if args.packages:
        names=[]
        for p in args.packages:
            full=p.resolve();matches=[name for name in SPECS if full==(ROOT/PREFIX/name/'artifact_packages.json').resolve()]
            need(len(matches)==1,'only the two prescribed repository package manifests are accepted');names+=matches
        need(len(set(names))==len(names),'duplicate package manifest')
    need(not args.report.exists(),'report already exists');args.report.parent.mkdir(parents=True,exist_ok=True)
    records=recover(names,args.out_root,args.include_bodies)
    report=dict(status='EXACT_TRIANGLE_ARTIFACT_RECOVERY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=digest(Path(__file__)),package_manifests={PREFIX+n+'/artifact_packages.json':SPECS[n]['package_sha256']for n in names},records=records,mathematical_verification=False)
    save(args.report,report);print(json.dumps(dict(status=report['status'],restored=len(records),report=str(args.report),sha256=digest(args.report))))
if __name__=='__main__':main()
