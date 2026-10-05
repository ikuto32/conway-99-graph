"""Deterministic, reversible packaging of15 frozen raw proof streams."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,copy,gzip,hashlib,json,platform,subprocess,sys,time,zlib
import recover_20260930_four_profile_proofs as recovery
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';CAMPAIGN=B/'20260930_hadamard_four_profile_native_campaign/summary.json';CAMPAIGN_SHA='1b735246ecd4ca2e5d3512d356b3c8130c67db74bfb0911dd6fa54e4f87a8b1f';CHUNK=8*1024**2;MAX_GZIP=10*1024**2
need=recovery.need;sha=recovery.sha
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def gzip_part(path,raw):
    with path.open('xb') as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,compresslevel=9,mtime=0) as g:g.write(raw)
def calibration(out):
    out.mkdir();raw=b'1 -2 0\nd 3 0\n0\n'*17;path=out/'tiny.gz';gzip_part(path,raw);part=dict(index=0,relative_path='tiny.gz',raw_offset=0,raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest(),gzip_bytes=path.stat().st_size,gzip_sha256=sha(path));record=dict(case=-1,raw_bytes=len(raw),raw_sha256=part['raw_sha256'],parts=[part]);recovery.recover_record(record,out);rejected=[]
    for name in ('wrong_whole_hash','wrong_chunk_length','wrong_offset','wrong_compressed_hash'):
        bad=copy.deepcopy(record)
        if name=='wrong_whole_hash':bad['raw_sha256']='0'*64
        elif name=='wrong_chunk_length':bad['parts'][0]['raw_bytes']+=1
        elif name=='wrong_offset':bad['parts'][0]['raw_offset']=1
        else:bad['parts'][0]['gzip_sha256']='0'*64
        try:recovery.recover_record(bad,out)
        except ValueError:rejected.append(name)
        else:raise ValueError('corrupt package metadata accepted')
    corrupt=bytearray(path.read_bytes());corrupt[-8]^=1;badpath=out/'corrupt.gz';badpath.write_bytes(corrupt);bad=copy.deepcopy(record);bad['parts'][0]['relative_path']='corrupt.gz';bad['parts'][0]['gzip_sha256']=sha(badpath)
    try:recovery.recover_record(bad,out)
    except (ValueError,OSError,EOFError,zlib.error):rejected.append('corrupt_gzip_payload')
    else:raise ValueError('corrupt gzip accepted')
    save(out/'summary.json',dict(status='PACKAGING_RECOVERY_CALIBRATION_PASS',tiny_positive_bytes=len(raw),rejected_controls=rejected,proof_validity_checked=False,inputs_sha256={key(Path(recovery.__file__)):sha(Path(recovery.__file__))}))
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        need(sha(CAMPAIGN)==CAMPAIGN_SHA,'campaign identity');campaign=read(CAMPAIGN);need(campaign['completed_attempts']==15 and not campaign['unattempted_cases'],'completed ordered fifteen-case population');calibration(out/'controls');records=[];inputs={key(CAMPAIGN):CAMPAIGN_SHA}
        for item in campaign['case_records']:
            summarypath=ROOT/item['summary_path'];need(sha(summarypath)==item['summary_sha256'],'case summary identity');case=read(summarypath);proof=case['proof_copy'];path=summarypath.parent/'main/proof.drat';need(case['native_receipt']['actual_exit_code']==20 and not case['native_receipt']['outer_windows_guard_expired'],'saved native UNSAT outcome; not proof approval');need(sha(path)==proof['sha256'] and path.stat().st_size==proof['bytes'],'raw native transfer identity');inputs[key(summarypath)]=item['summary_sha256'];inputs[key(path)]=proof['sha256'];folder=out/f'case_{item["case"]:03d}';folder.mkdir();parts=[];offset=0;total=hashlib.sha256()
            with path.open('rb') as stream:
                for index,data in enumerate(iter(lambda:stream.read(CHUNK),b'')):
                    target=folder/f'proof.part{index:04d}.drat.gz';gzip_part(target,data);need(target.stat().st_size<MAX_GZIP,'strict sub10MiB payload');parts.append(dict(index=index,relative_path=target.relative_to(out).as_posix(),raw_offset=offset,raw_bytes=len(data),raw_sha256=hashlib.sha256(data).hexdigest(),gzip_bytes=target.stat().st_size,gzip_sha256=sha(target)));offset+=len(data);total.update(data)
            need(offset==proof['bytes'] and total.hexdigest()==proof['sha256'],'unchanged raw during packaging');record=dict(case=item['case'],raw_original_path=key(path),raw_sha256=proof['sha256'],raw_bytes=proof['bytes'],preserved_ext4_original=proof['linux_source'],case_summary_path=item['summary_path'],case_summary_sha256=item['summary_sha256'],cnf_sha256=case['cnf_sha256'],parts=parts,proof_validity_checked_by_packager=False);recovered=recovery.recover_record(record,out);need(sha(path)==proof['sha256'],'original retained unchanged');records.append(record);save(folder/'recovery_identity.json',recovered);print(json.dumps(dict(case=item['case'],raw_bytes=offset,gzip_bytes=sum(p['gzip_bytes'] for p in parts),parts=len(parts))),flush=True)
        totalraw=sum(r['raw_bytes'] for r in records);need(totalraw==149571922,'frozen total raw size')
        for path in (Path(__file__),Path(__file__).with_name('package_20260930_four_profile_proofs_spec.md'),Path(recovery.__file__),ROOT/'uv.lock',ROOT/'pyproject.toml'):inputs[key(path)]=sha(path)
        manifest=dict(schema='FOUR_PROFILE_RAW_DRAT_GZIP_PARTS_V1',created=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),zlib_compile_version=zlib.ZLIB_VERSION,zlib_runtime_version=zlib.ZLIB_RUNTIME_VERSION,inputs_sha256=inputs,raw_chunk_bytes=CHUNK,gzip_parameters=dict(compresslevel=9,mtime=0,filename=''),strict_maximum_part_bytes=MAX_GZIP,records=records,proofs=len(records),total_raw_bytes=totalraw,total_gzip_bytes=sum(p['gzip_bytes'] for r in records for p in r['parts']),parts=sum(len(r['parts']) for r in records),proof_validity_checked=False,originals_preserved=True,artifact_availability='LOCAL_ONLY',availability_reason='Prepared public payload; publication not yet confirmed.',recovery_command='uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_four_profile_proofs.py --manifest PATH --manifest-sha256 SHA --verify-only')
        save(out/'package_manifest.json',manifest);save(out/'summary.json',dict(status='FIFTEEN_RAW_PROOFS_LOSSLESSLY_PACKAGED',package_manifest_path=key(out/'package_manifest.json'),package_manifest_sha256=sha(out/'package_manifest.json'),proofs=len(records),total_raw_bytes=totalraw,total_gzip_bytes=manifest['total_gzip_bytes'],gzip_parts=manifest['parts'],largest_gzip_part_bytes=max(p['gzip_bytes'] for r in records for p in r['parts']),all_raw_streams_recovered_and_rehashed=True,originals_preserved=True,proof_validity_checked=False,elapsed_seconds=time.monotonic()-start,artifact_availability='LOCAL_ONLY',inputs_sha256=inputs));print(json.dumps(read(out/'summary.json')))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__)),originals_not_deleted=True));raise
if __name__=='__main__':main()
