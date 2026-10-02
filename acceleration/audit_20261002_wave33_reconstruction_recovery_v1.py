"""Independently restore the frozen rooted8 reconstructed operator to fresh path."""
from __future__ import annotations
import argparse,copy,gzip,hashlib,json,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from io import BytesIO
from pathlib import Path
from command_deadline import CommandDeadline
import audit_20261002_batch05_raw_recovery_v1 as core

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='acceleration/results/20261002_wave33_reconstruction_package01/manifest.json'
MANIFEST_SHA='f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989'
EXPECTED={
 'acceleration/results/20261002_independent_review/rooted8_model01/reconstructed_rows.json':'e55bb55fcf1b90d0088d74a2c6a3c600d94674121f828fc40c450b7d58965bbe',
}


def need(ok,why):
    if not ok:raise ValueError(why)


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def controls(deadline):
    payload=b'independent literal package recovery\x00\xff\n'*7;raw_parts=[payload[:70],payload[70:]];compressed={str(i):gzip.compress(raw,mtime=0) for i,raw in enumerate(raw_parts)};parts=[];offset=0
    for i,raw in enumerate(raw_parts):
        parts.append(dict(path=str(i),gzip_sha256=hashlib.sha256(compressed[str(i)]).hexdigest(),gzip_bytes=len(compressed[str(i)]),raw_offset=offset,raw_sha256=hashlib.sha256(raw).hexdigest(),raw_bytes=len(raw)));offset+=len(raw)
    row=dict(path='tiny.bin',sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload),parts=parts)
    core.recover(row,lambda name:compressed[name],BytesIO(payload),deadline)
    rejected=[]
    for label,mutation,message in [('dropped_part',lambda value:value['parts'].pop(),'whole raw length/hash and no omitted tail'),
        ('wrong_raw_hash',lambda value:value.update(sha256='0'*64),'whole raw length/hash and no omitted tail'),
        ('noncontiguous_offset',lambda value:value['parts'][1].update(raw_offset=71),'unique contiguous compressed parts'),
        ('wrong_compressed_hash',lambda value:value['parts'][0].update(gzip_sha256='0'*64),'exact compressed identity')]:
        damaged=copy.deepcopy(row);mutation(damaged)
        try:core.recover(damaged,lambda name:compressed[name],BytesIO(payload),deadline)
        except ValueError as error:need(str(error)==message,'EXACT_NEGATIVE_DIAGNOSTIC');rejected.append(dict(label=label,diagnostic=message))
        else:raise ValueError('CORRUPTED_RECOVERY_ACCEPTED:'+label)
    return dict(multichunk_positive=True,strict_corrupted_controls=rejected)


def run(args):
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Fresh reconstructedroot8 restore plus independent streaming bytecomparison, exactcontrols and rawauditoutputbindings;30sreserve')
    out=args.out.resolve();out.mkdir(exist_ok=False);pins={};restored=[]
    def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>30,'not completed within the allocated budget')
    def pin(name,expected=None):
        tick();value=sha(ROOT/name);need(expected is None or value==expected,'EXACT_INPUT_HASH:'+name);pins[name]=value
    try:
        calibrated=controls(deadline);pin(MANIFEST,MANIFEST_SHA)
        for name in [Path(__file__).relative_to(ROOT).as_posix(),Path(core.__file__).relative_to(ROOT).as_posix(),'acceleration/recover_20261001_twentyninth_raw_artifacts.py','acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock']:pin(name)
        report='acceleration/results/20261002_independent_review/rooted8_model01/summary.json';pin(report,'e3158fe17f4a83e5231c90f72c912e5ef37cd6ddc3ce6300f0c6861f9d0ffc4e')
        audited=json.loads((ROOT/report).read_bytes());manifest=json.loads((ROOT/MANIFEST).read_bytes());rows=manifest['records']
        need(manifest['record_count']==len(rows)==1 and {row['raw_path'] for row in rows}==set(EXPECTED),'EXACT_SINGLE_RECONSTRUCTION_POPULATION')
        need(sum(row['raw_bytes'] for row in rows)==manifest['raw_bytes']==62319858 and sum(len(row['parts']) for row in rows)==manifest['gzip_parts']==8,'EXACT_PACKAGE_DIMENSIONS')
        audit_outputs={str(Path(report).parent/name).replace('\\','/'):digest for name,digest in audited['outputs_sha256'].items()}
        for row in rows:
            need(row['raw_sha256']==EXPECTED[row['raw_path']]==audit_outputs[row['raw_path']],'LITERAL_MATHEMATICAL_OUTPUT_BINDING')
            for part in row['parts']:pin(part['path'],part['gzip_sha256'])
        destination=ROOT/'build/wave33_reconstruction_recovery01';need(not destination.exists(),'FRESH_DESTINATION_NO_OVERWRITE')
        receipt=out/'restoration_receipt.json';argv=[sys.executable,'-B','acceleration/recover_20261001_twentyninth_raw_artifacts.py','--manifest',MANIFEST,'--manifest-sha256',MANIFEST_SHA,'--destination-dir',str(destination),'--receipt',str(receipt)]
        with (out/'restore.stdout.log').open('xb') as stdout,(out/'restore.stderr.log').open('xb') as stderr:
            result=subprocess.run(argv,cwd=ROOT,stdout=stdout,stderr=stderr,timeout=max(1,deadline.status()['remaining_seconds']-30),check=False)
        need(result.returncode==0,'OLD_RESTORER_EXIT_ZERO');raw_receipt=json.loads(receipt.read_bytes())
        need(raw_receipt['status']=='TWENTYNINTH_RAW_ARTIFACT_RECOVERY_PASS' and raw_receipt['action_counts']=={'RESTORED_MISSING':1},'SINGLE_FRESH_RESTORE')
        for row in rows:
            tick();normalized=dict(path=row['raw_path'],sha256=row['raw_sha256'],bytes=row['raw_bytes'],parts=row['parts'])
            with (ROOT/row['raw_path']).open('rb') as original:checked=core.recover(normalized,lambda name:(ROOT/name).read_bytes(),original,deadline)
            target=destination/row['raw_path'];need(sha(target)==row['raw_sha256'] and target.stat().st_size==row['raw_bytes'],'RESTORED_HASH_LENGTH')
            with target.open('rb') as fresh,(ROOT/row['raw_path']).open('rb') as original:
                while True:
                    tick();a=fresh.read(1048576);b=original.read(1048576);need(a==b,'RESTORED_EVERY_ORIGINAL_BYTE');
                    if not a:break
            restored.append(dict(**checked,fresh_destination=str(target),restored_every_byte_matches=True,mathematical_audit_output_hash=audit_outputs[row['raw_path']]))
        summary=dict(status='INDEPENDENT_WAVE33_RECONSTRUCTED_ROOTED8_RAW_RECOVERY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',producer='/root',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,originals=1,raw_bytes=62319858,gzip_parts=8,gzip_bytes=2207588,records=restored,
            fresh_restore_argv=argv,fresh_restore_receipt_sha256=sha(receipt),destination=str(destination),controls=calibrated,
            shared_components=['Unchanged pinned historical restoration CLI, separately implemented prior independent streaming bounded byte checker, Python gzip/SHA-256 and contained supervisor.'],
            scope='Lossless recovery of one hash-bound independently reconstructed rooted8 operator output to a fresh destination; no originals overwritten.',mathematical_verification=False,public_availability_established=False,target_resolution=False,
            limitations=['Existing row derivations are bound by exact raw hashes, not rerun here.','No claim about compressed public retrieval or historical transitive dependency/platform binary availability.'],elapsed_seconds=time.monotonic()-start,deadline=deadline.status())
        save(out/'summary.json',summary);print(json.dumps({key:summary[key] for key in ['status','originals','raw_bytes','elapsed_seconds']}))
    except Exception as error:
        save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),error=repr(error),inputs_sha256=pins,completed=restored,elapsed_seconds=time.monotonic()-start,mathematical_verification=False));raise


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);run(ap.parse_args())
