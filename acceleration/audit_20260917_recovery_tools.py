"""Independent byte reconstruction checks and adversarial recovery-tool controls."""
from datetime import datetime,timezone
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import zlib
import restore_chunked_artifacts as subject
import audit_compressed_artifact_manifest as gzsubject

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'build/independent-recovery-tools-20260917'
OUT=ROOT/'acceleration/results/20260917_independent_review/recovery_tools.json'
def require(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
    with p.open('x')as f:json.dump(d,f,indent=2)
def main():
    require(not WORK.exists()and not OUT.exists(),'Fresh audit paths');WORK.mkdir();bindings={};controls=[]
    manifest=ROOT/'acceleration/results/20260917_four_matching_filtered_moments/chunk_manifest.json';bindings[manifest.relative_to(ROOT).as_posix()]=sha(manifest);data=json.loads(manifest.read_bytes());require(len(data['artifacts'])==1,'one selected matrix');artifact=data['artifacts'][0]
    # Invoke the restoration tool, then independently read chunks and target
    # with different buffer boundaries. No producer hash helper is used here.
    destination=WORK/'filtered';observed=subject.restore(manifest,ROOT,destination);target=destination/artifact['source'];total=0;acc=hashlib.sha256()
    with target.open('rb')as recovered:
        for part in artifact['parts']:
            p=manifest.parent/part['path'];bindings[p.relative_to(ROOT).as_posix()]=sha(p);require(p.stat().st_size==part['bytes']and sha(p)==part['sha256'],'part independently checked')
            with p.open('rb')as f:
                while True:
                    block=f.read(100003)
                    if not block:break
                    require(recovered.read(len(block))==block,'ordered bytes differ');total+=len(block);acc.update(block)
        require(recovered.read(1)==b'','trailing output')
    require(total==artifact['source_bytes']==27081591 and acc.hexdigest()==artifact['source_sha256']==sha(target),'whole independent identity')
    original=manifest.parent/artifact['source'];require(sha(original)==sha(target),'original raw cross-check');bindings[original.relative_to(ROOT).as_posix()]=sha(original)
    before=sha(target)
    try:subject.restore(manifest,ROOT,destination)
    except FileExistsError:controls.append(dict(name='existing_target',outcome='REJECT'))
    else:raise ValueError('overwrite accepted')
    require(sha(target)==before,'existing artifact mutated')
    for helper in(subject.safe,lambda root,base,name:gzsubject.safe_relative(base,name)):
        require(helper(ROOT,WORK,'safe.bin')==WORK/'safe.bin','positive confinement')
        for name in('../escape','..\\escape','C:/escape','x:y','/escape'):
            try:helper(ROOT,WORK,name)
            except ValueError:controls.append(dict(name='unsafe_path',value=name,outcome='REJECT'))
            else:raise ValueError('path accepted '+name)
    fixture=WORK/'fixture';fixture.mkdir();p=fixture/'part.bin';p.write_bytes(b'calibrated raw bytes');h=sha(p)
    good=dict(schema_version=1,artifacts=[dict(source='restored.bin',source_bytes=p.stat().st_size,source_sha256=h,parts=[dict(path='part.bin',bytes=p.stat().st_size,sha256=h)])])
    for name,edit in [('wrong_part_hash',lambda a:a['parts'][0].update(sha256='0'*64)),('duplicate_part',lambda a:a['parts'].append(a['parts'][0].copy())),('wrong_whole_hash',lambda a:a.update(source_sha256='0'*64)),('target_traversal',lambda a:a.update(source='../escape'))]:
        corrupted=json.loads(json.dumps(good));edit(corrupted['artifacts'][0]);m=fixture/(name+'.json');save(m,corrupted);dest=WORK/name
        try:subject.restore(m,ROOT,dest)
        except(ValueError,FileExistsError):controls.append(dict(name=name,outcome='REJECT',final_target_created=(dest/'restored.bin').exists()))
        else:raise ValueError('corrupt chunk accepted '+name)
        require(not(dest/'restored.bin').exists(),'corrupt final artifact published')
    # The generic gzip wrapper uses frozen streaming zlib. Independently recover
    # its toy output with gzip.GzipFile and compare the calibrated bytes.
    raw=b'Independent wrapper byte fixture\x00\xff\n'*127;compressed=fixture/'toy.gz';compressed.write_bytes(gzip.compress(raw,mtime=0));gzmanifest=fixture/'gzip_manifest.json'
    save(gzmanifest,dict(schema_version=1,files=[dict(path='nested/toy.bin',compressed_path=compressed.relative_to(ROOT).as_posix(),compressed_size_bytes=compressed.stat().st_size,compressed_sha256=sha(compressed),size_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())]))
    command=[sys.executable,str(ROOT/'acceleration/audit_compressed_artifact_manifest.py'),str(gzmanifest),'--destination',str(WORK/'gzip_output'),'--out',str(WORK/'gzip_receipt.json')]
    runs=[]
    for expected in(0,1):
        run=subprocess.run(command,capture_output=True,text=True,cwd=ROOT);runs.append(dict(command=command,exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr));require((run.returncode==0)==(expected==0),'gzip wrapper expected result')
    with gzip.GzipFile(fileobj=compressed.open('rb'))as stream:decoded=stream.read()
    require(decoded==raw==(WORK/'gzip_output/nested/toy.bin').read_bytes(),'independent gzip bytes')
    for p in(Path(__file__),Path(subject.__file__),Path(gzsubject.__file__),ROOT/'acceleration/audit_compressed_artifacts.py',ROOT/'uv.lock'):bindings[p.relative_to(ROOT).as_posix()]=sha(p)
    report=dict(status='INDEPENDENT_RECOVERY_TOOLS_BYTE_AND_GUARD_REVIEW_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),zlib=zlib.ZLIB_RUNTIME_VERSION,inputs_sha256=bindings,matrix_recovered_bytes=total,matrix_sha256=acc.hexdigest(),parts=len(artifact['parts']),restore_tool_result=observed,controls=controls,gzip_wrapper_runs=runs,independent_method='Compared all recovered matrix bytes with ordered parts using100003-byte reads and separate hashlib implementation; original raw read only afterward as cross-check. Calibrated gzip bytes independently read via GzipFile. Adversarial path, duplicate, hash, and no-overwrite cases challenged actual tools.',source_review='Both tools resolve targets beneath allowed roots, stage verified bytes, and publish with exclusive hard links. Chunk restore rechecks part/source/manifest identities; gzip wrapper checks compressed identity and uses complete-single-member frozen zlib decoder. Failed staging files may remain as evidence. No general concurrent hostile-filesystem race claim is made.',shared_components=['Python hashlib/filesystem runtime','Actual subject tools invoked for behavior controls only','GzipFile and frozen decoder share underlying zlib; no independent compression algorithm claimed'],original_raw_consulted_by_independent_audit=True,originals_overwritten=False,mathematical_verification=False,limitations=['Engineering byte identity and tested guard behavior only; no mathematical claim promotion.','Local bytes checked, not public network retrieval.','Same-tool execution alone was not treated as independent checking.'])
    save(OUT,report);print(report['status'],sha(OUT))
if __name__=='__main__':main()
